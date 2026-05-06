"""Factories for environments and native trust runtimes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from experiments.trust.config import ExperimentConfig
from experiments.trust.spec import ExpandedRunSpec, VariantSpec
from tasks.trust.affect import DiscreteBetaState
from tasks.trust.envs import GradedTrustGameEnv, TrustGameEnv
from tasks.trust.pomdp import TrustPomdpTemplate, build_trust_pomdp_template, create_partner_agents
from tasks.trust.runtime import PartnerBank


@dataclass
class NativeTrustRuntime:
    template: TrustPomdpTemplate
    partner_bank: PartnerBank
    affect_mode: str
    base_gamma: float
    action_selection: str
    rng: np.random.Generator
    planning_horizon: int
    variant_id: str
    agent_kind: str

    @property
    def num_partners(self) -> int:
        return len(self.partner_bank.agents)

    @property
    def _kind_label(self) -> str:
        return self.variant_id


def create_model(config: ExperimentConfig) -> TrustPomdpTemplate:
    """Build a native template for task-side consumers that need static matrices."""

    return build_trust_pomdp_template(
        config,
        planning_horizon=1,
        max_policies=config.max_policies,
        rng=np.random.default_rng(config.random_seed),
    )


def create_env(config: ExperimentConfig, seed: int) -> TrustGameEnv:
    if config.payoff_mode == "graded":
        return GradedTrustGameEnv(config, seed=seed)
    return TrustGameEnv(config, seed=seed)


def create_native_runtime_from_run(run: ExpandedRunSpec) -> NativeTrustRuntime:
    """Build a native trust runtime from an expanded TOML variant run."""

    return create_native_runtime_from_variant(
        run.to_runtime_config(),
        variant=run.variant,
        variant_id=run.variant_id,
        seed=run.seed,
    )


def create_native_runtime_from_variant(
    config: ExperimentConfig,
    *,
    variant: VariantSpec,
    variant_id: str | None = None,
    seed: int,
) -> NativeTrustRuntime:
    """Build a native trust runtime from explicit runtime config and variant metadata."""

    return _create_runtime_from_config_and_variant(
        config,
        variant=variant,
        variant_id=variant.id if variant_id is None else str(variant_id),
        seed=seed,
    )


def create_agents_from_multi_focal_config(
    config,
    seed: int,
) -> list[NativeTrustRuntime]:
    """Build one native runtime per multi-focal participant."""

    participant_count = config.num_agents()
    runtimes: list[NativeTrustRuntime] = []
    supported_agent_keys = {
        "planning_horizon",
        "gamma",
        "action_sampling",
        "use_information_gain",
        "max_policies",
        "alpha_charge",
        "sigma_0_sq",
        "initial_beta",
        "num_levels",
        "persistence",
        "lesion_mode",
    }
    for i, spec in enumerate(config.agents):
        overrides = dict(spec.get("model_overrides", {}))
        if "num_partners" in overrides:
            raise ValueError(
                "multi-focal model_overrides must not set 'num_partners'; "
                "each agent model is forced to M - 1 partners."
            )
        if "num_partners" in spec:
            raise ValueError(
                "multi-focal agent specs must not set 'num_partners'; "
                "each agent model is forced to M - 1 partners."
            )
        unknown_agent_keys = {
            key for key in spec if key not in {"kind", "model_overrides", "_label"} and key not in supported_agent_keys
        }
        if unknown_agent_keys:
            raise ValueError(f"unsupported multi-focal agent keys: {sorted(unknown_agent_keys)}")

        kind = str(spec["kind"])
        affect = "precision" if kind == "affective" else "tracked_only" if kind == "lesioned" else "none"
        planning_horizon = int(spec.get("planning_horizon", 8))
        runtime_config = ExperimentConfig(
            payoff_mode=config.payoff_mode,
            num_partners=participant_count - 1,
            assignment_mode=config.assignment_mode,
            num_rounds=config.num_rounds,
            random_seed=seed + i,
            max_policies=int(spec.get("max_policies", 4096)),
            gamma=float(spec.get("gamma", 1.0)),
            action_sampling=str(spec.get("action_sampling", "marginal")),
            alpha_charge=float(spec.get("alpha_charge", 3.0)),
            sigma_0_sq=float(spec.get("sigma_0_sq", 0.25)),
            initial_beta=float(spec.get("initial_beta", 1.0)),
            beta_num_levels=int(spec.get("num_levels", 5)),
            beta_persistence=float(spec.get("persistence", 0.8)),
        )
        for key, value in overrides.items():
            setattr(runtime_config, key, value)
        runtime_config.payoff_mode = config.payoff_mode
        runtime_config.num_partners = participant_count - 1
        runtime_config.assignment_mode = config.assignment_mode
        variant = VariantSpec(
            id=str(spec.get("_label", kind)),
            affect=affect,
            planning_horizon=planning_horizon,
            gamma=runtime_config.gamma,
            epistemic_value=bool(spec.get("use_information_gain", True)),
            alpha_charge=runtime_config.alpha_charge,
            sigma_0_sq=runtime_config.sigma_0_sq,
            initial_beta=runtime_config.initial_beta,
            beta_persistence=runtime_config.beta_persistence,
            beta_levels=tuple(
                runtime_config.beta_levels
                if runtime_config.beta_levels is not None
                else np.linspace(0.5, 2.0, int(runtime_config.beta_num_levels), dtype=np.float64).tolist()
            ),
            action_selection=runtime_config.action_sampling,
        )
        runtime = create_native_runtime_from_variant(
            runtime_config,
            variant=variant,
            variant_id=variant.id,
            seed=seed + i,
        )
        runtime.variant_id = str(spec.get("_label", kind))
        runtime.agent_kind = kind
        runtimes.append(runtime)
    return runtimes


def _create_runtime_from_config_and_variant(
    config: ExperimentConfig,
    *,
    variant: VariantSpec,
    variant_id: str,
    seed: int,
) -> NativeTrustRuntime:
    rng = np.random.default_rng(int(seed))
    planning_horizon = int(variant.planning_horizon)
    template = build_trust_pomdp_template(
        config,
        planning_horizon=planning_horizon,
        max_policies=config.max_policies,
        rng=rng,
    )
    agents = create_partner_agents(template, num_partners=config.num_partners, gamma=config.gamma)
    for agent in agents:
        _set_information_gain(agent, variant.epistemic_value)

    beta = None
    affect_mode = "none"
    agent_kind = "base"
    if variant.affect in {"precision", "tracked_only"}:
        agent_kind = "affective" if variant.affect == "precision" else "lesioned"
        affect_mode = "normal" if variant.affect == "precision" else "decouple"
        beta = DiscreteBetaState(
            num_entities=config.num_partners,
            beta_levels=np.asarray(variant.beta_levels, dtype=np.float64),
            persistence=config.beta_persistence,
            alpha_charge=config.alpha_charge,
            sigma_0_sq=config.sigma_0_sq,
            initial_beta=config.initial_beta,
        )

    return NativeTrustRuntime(
        template=template,
        partner_bank=PartnerBank(agents=agents, beta=beta),
        affect_mode=affect_mode,
        base_gamma=config.gamma,
        action_selection=config.action_sampling,
        rng=rng,
        planning_horizon=planning_horizon,
        variant_id=variant_id,
        agent_kind=agent_kind,
    )


def _set_information_gain(agent, enabled: bool) -> None:
    if hasattr(agent, "use_states_info_gain"):
        object.__setattr__(agent, "use_states_info_gain", bool(enabled))
    if hasattr(agent, "use_param_info_gain") and not enabled:
        object.__setattr__(agent, "use_param_info_gain", False)


__all__ = [
    "NativeTrustRuntime",
    "create_agents_from_multi_focal_config",
    "create_env",
    "create_model",
    "create_native_runtime_from_run",
    "create_native_runtime_from_variant",
]
