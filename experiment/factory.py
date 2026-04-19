"""Factories for models, environments, and agents."""

from __future__ import annotations

from env.graded_trust_game import GradedTrustGameEnv
from env.trust_game import TrustGameEnv
from experiment.conditions import resolve_condition_spec
from experiment.config import ExperimentConfig
from experiment.multi_focal_config import MultiFocalConfig
from trust import AffectiveAgent, LesionedAgent, TrustGameAgent, TrustGameModel


def create_model(config: ExperimentConfig) -> TrustGameModel:
    return TrustGameModel(config)


def create_env(config: ExperimentConfig, seed: int) -> TrustGameEnv:
    if config.payoff_mode == "graded":
        return GradedTrustGameEnv(config, seed=seed)
    return TrustGameEnv(config, seed=seed)


def _planning_horizon_for_condition(config: ExperimentConfig, condition: int | str, default_horizon: int) -> int:
    candidates: list[int | str] = [condition]
    if isinstance(condition, str) and condition.strip().isdigit():
        candidates.append(int(condition))
    elif not isinstance(condition, str):
        candidates.append(str(condition))
        candidates.append(resolve_condition_spec(condition).name)
    else:
        candidates.append(resolve_condition_spec(condition).name)

    for key in candidates:
        if key in config.horizon_overrides:
            return int(config.horizon_overrides[key])
    return int(default_horizon)


def create_agent(config: ExperimentConfig, condition: int | str, model: TrustGameModel, seed: int) -> TrustGameAgent:
    spec = resolve_condition_spec(condition)
    planning_horizon = _planning_horizon_for_condition(config, condition, spec.planning_horizon)
    common = dict(
        model=model,
        gamma=config.gamma,
        lr=config.lr,
        action_sampling=config.action_sampling,
        max_policies=config.max_policies,
        reference_horizon=config.deep_horizon,
        seed=seed,
        use_parameter_learning=config.use_parameter_learning,
        use_information_gain=spec.use_information_gain,
        learn_A=config.learn_A,
        learn_B=config.learn_B,
        learn_E=config.learn_E,
        pA_scale=config.pA_scale,
        pB_scale=config.pB_scale,
        lr_E=config.lr_E,
    )
    params = {
        "alpha_charge": config.alpha_charge,
        "sigma_0_sq": config.sigma_0_sq,
        "initial_beta": config.initial_beta,
    }
    params.update(spec.parameter_overrides)

    if spec.agent_kind == "base":
        return TrustGameAgent(planning_horizon=planning_horizon, **common)
    if spec.agent_kind == "lesioned":
        return LesionedAgent(
            planning_horizon=planning_horizon,
            alpha_charge=params["alpha_charge"],
            sigma_0_sq=params["sigma_0_sq"],
            initial_beta=params["initial_beta"],
            num_levels=config.beta_num_levels,
            persistence=config.beta_persistence,
            lesion_mode=spec.lesion_mode or config.lesion_mode,
            **common,
        )
    if spec.agent_kind == "affective":
        return AffectiveAgent(
            planning_horizon=planning_horizon,
            alpha_charge=params["alpha_charge"],
            sigma_0_sq=params["sigma_0_sq"],
            initial_beta=params["initial_beta"],
            num_levels=config.beta_num_levels,
            persistence=config.beta_persistence,
            **common,
        )
    raise ValueError(f"Unknown agent kind '{spec.agent_kind}'.")


def create_agents_from_multi_focal_config(
    config: MultiFocalConfig,
    seed: int,
) -> list[TrustGameAgent]:
    """Build M agents from a multi-focal config (spec Section 2 + 4).

    Each agent gets its own TrustGameModel built from population payoff_mode +
    per-agent model_overrides. num_partners is forced to M-1 (no self-modeling, F5).
    """
    M = config.num_agents()
    agents: list[TrustGameAgent] = []
    for i, spec in enumerate(config.agents):
        overrides = dict(spec.get("model_overrides", {}))
        overrides.pop("num_partners", None)
        overrides.pop("assignment_mode", None)
        overrides.pop("payoff_mode", None)
        model_cfg: dict = {
            "payoff_mode": config.payoff_mode,
            "num_partners": M - 1,
            "assignment_mode": config.assignment_mode,
        }
        model_cfg.update(overrides)
        model_cfg["payoff_mode"] = config.payoff_mode
        model_cfg["num_partners"] = M - 1
        model_cfg["assignment_mode"] = config.assignment_mode
        model = TrustGameModel(model_cfg)

        kind = spec["kind"]
        agent_kwargs = {k: v for k, v in spec.items() if k not in {"kind", "model_overrides", "_label"}}
        if kind == "base":
            agent = TrustGameAgent(model, seed=seed + i, **agent_kwargs)
        elif kind == "affective":
            agent = AffectiveAgent(model, seed=seed + i, **agent_kwargs)
        elif kind == "lesioned":
            agent = LesionedAgent(model, seed=seed + i, **agent_kwargs)
        else:
            raise ValueError(f"unknown agent kind={kind!r}")
        agent._kind_label = spec.get("_label", kind)
        agents.append(agent)
    return agents
