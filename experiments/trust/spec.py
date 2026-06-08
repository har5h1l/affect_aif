"""Hierarchical TOML experiment specifications for trust experiments."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, cast

from tasks.trust.affect import LOG_SURPRISE_BASELINE_SQ
from tasks.trust.types import PARTNER_TYPE_ORDER

try:  # pragma: no cover - exercised only on Python < 3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


LEGACY_PUBLIC_KEYS = {
    "conditions",
    "presets",
    "deep_horizon",
    "shallow_horizon",
    "horizon_overrides",
    "lr",
    "use_parameter_learning",
    "learn_A",
    "learn_B",
    "learn_E",
    "pA_scale",
    "pB_scale",
    "lr_E",
    "lesion_mode",
    "run_sensitivity",
    "sensitivity_factors",
    "experiment_name",
    "verbose",
    "verbosity_mode",
    "gif_after_run",
    "gif_output_dir",
}

PAYOFF_VALUES = {"binary", "graded"}
ASSIGNMENT_VALUES = {"random", "agent_choice"}
AFFECT_VALUES = {"none", "precision", "tracked_only", "global_beta"}
FAMILY_VALUES = {"trust", "multifocal"}


@dataclass(frozen=True)
class HypothesisSpec:
    id: str
    name: str


@dataclass(frozen=True)
class ExperimentMeta:
    id: str
    rounds: int
    replications: int
    seed: int
    family: str = "trust"


@dataclass(frozen=True)
class StanceSwitchSpec:
    round: int
    partner: int
    to: str

    def to_runtime_dict(self) -> dict[str, Any]:
        return {"round": int(self.round), "partner_idx": int(self.partner), "to_stance": str(self.to)}


@dataclass(frozen=True)
class TypeSwitchSpec:
    round: int
    partner: int
    to: str

    def to_runtime_dict(self) -> dict[str, Any]:
        return {"round": int(self.round), "partner_idx": int(self.partner), "to_type": str(self.to)}


@dataclass(frozen=True)
class ScenarioSpec:
    payoff: str
    assignment: str
    partners: int = 4
    type_volatility: float = 0.05
    observation_noise: float = 0.0
    correlation_pairs: tuple[tuple[int, int], ...] = ()
    correlation_strength: float = 0.9
    partner_types: tuple[str, ...] = tuple(PARTNER_TYPE_ORDER)
    partner_type_params: dict[str, dict[str, Any]] = field(default_factory=dict)
    initial_types: tuple[str, ...] | None = None
    initial_stances: tuple[str, ...] | None = None
    type_switches: tuple[TypeSwitchSpec, ...] = ()
    stance_switches: tuple[StanceSwitchSpec, ...] = ()
    investment_levels: int = 6
    endowment: float = 10.0
    multiplier: float = 3.0
    mutual_coop: tuple[float, float] = (3.0, 3.0)
    sucker: tuple[float, float] = (-1.0, 5.0)
    temptation: tuple[float, float] = (5.0, -1.0)
    mutual_defect: tuple[float, float] = (1.0, 1.0)


@dataclass(frozen=True)
class VariantSpec:
    id: str
    affect: str
    planning_horizon: int
    gamma: float = 1.0
    epistemic_value: bool = True
    alpha_charge: float = 3.0
    sigma_0_sq: float = LOG_SURPRISE_BASELINE_SQ
    initial_beta: float = 1.0
    beta_prior: tuple[float, ...] | None = None
    beta_persistence: float = 0.8
    beta_levels: tuple[float, ...] = (0.5, 0.67, 1.0, 1.5, 2.0)
    action_selection: str = "marginal"


@dataclass(frozen=True)
class SweepSpec:
    parameter: str
    values: tuple[float | int | str | bool, ...]
    applies_to: tuple[str, ...]


@dataclass(frozen=True)
class RuntimeSpec:
    max_policies: int = 4096
    debug_mode: bool = False
    log_policy_traces: bool = False


@dataclass(frozen=True)
class AnalysisSpec:
    auto: bool = False
    target: str = "experiment"
    primary: str = ""
    compare: tuple[str, ...] = ()
    switch_window: tuple[int, ...] = ()
    metrics: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExpandedRunSpec:
    hypothesis_id: str
    experiment_id: str
    variant_id: str
    replication: int
    seed: int
    rounds: int
    scenario: ScenarioSpec
    variant: VariantSpec
    analysis: AnalysisSpec
    runtime: RuntimeSpec

    def to_runtime_config(self):
        from experiments.trust.config import ExperimentConfig

        return ExperimentConfig(
            payoff_mode=self.scenario.payoff,
            assignment_mode=self.scenario.assignment,
            num_partners=self.scenario.partners,
            num_rounds=self.rounds,
            p_switch=self.scenario.type_volatility,
            observation_noise=self.scenario.observation_noise,
            correlation_pairs=[list(pair) for pair in self.scenario.correlation_pairs],
            correlation_strength=self.scenario.correlation_strength,
            partner_types=list(self.scenario.partner_types),
            partner_type_params=dict(self.scenario.partner_type_params),
            initial_partner_types=None if self.scenario.initial_types is None else list(self.scenario.initial_types),
            initial_partner_stances=(
                None if self.scenario.initial_stances is None else list(self.scenario.initial_stances)
            ),
            scheduled_type_switches=[switch.to_runtime_dict() for switch in self.scenario.type_switches],
            scheduled_stance_switches=[switch.to_runtime_dict() for switch in self.scenario.stance_switches],
            num_investment_levels=self.scenario.investment_levels,
            endowment=self.scenario.endowment,
            multiplier=self.scenario.multiplier,
            mutual_coop=self.scenario.mutual_coop,
            sucker=self.scenario.sucker,
            temptation=self.scenario.temptation,
            mutual_defect=self.scenario.mutual_defect,
            gamma=self.variant.gamma,
            action_sampling=self.variant.action_selection,
            alpha_charge=self.variant.alpha_charge,
            sigma_0_sq=self.variant.sigma_0_sq,
            initial_beta=self.variant.initial_beta,
            initial_beta_prior=None if self.variant.beta_prior is None else list(self.variant.beta_prior),
            beta_persistence=self.variant.beta_persistence,
            beta_levels=list(self.variant.beta_levels),
            max_policies=self.runtime.max_policies,
            debug_mode=self.runtime.debug_mode,
            log_policy_traces=self.runtime.log_policy_traces,
            num_replications=1,
            random_seed=self.seed,
        )

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ExpandedRunSpec:
        scenario_data = dict(payload["scenario"])
        scenario_data["partner_types"] = tuple(scenario_data.get("partner_types", PARTNER_TYPE_ORDER))
        scenario_data["partner_type_params"] = dict(scenario_data.get("partner_type_params", {}))
        scenario_data["correlation_pairs"] = tuple(tuple(pair) for pair in scenario_data.get("correlation_pairs", ()))
        if scenario_data.get("initial_types") is not None:
            scenario_data["initial_types"] = tuple(scenario_data["initial_types"])
        if scenario_data.get("initial_stances") is not None:
            scenario_data["initial_stances"] = tuple(scenario_data["initial_stances"])
        for key in ("mutual_coop", "sucker", "temptation", "mutual_defect"):
            scenario_data[key] = tuple(scenario_data.get(key, getattr(ScenarioSpec, key)))
        scenario_data["stance_switches"] = tuple(
            StanceSwitchSpec(**item) for item in scenario_data.get("stance_switches", ())
        )
        scenario_data["type_switches"] = tuple(
            TypeSwitchSpec(**item) for item in scenario_data.get("type_switches", ())
        )
        variant_data = dict(payload["variant"])
        variant_data["beta_levels"] = tuple(variant_data.get("beta_levels", (0.5, 0.67, 1.0, 1.5, 2.0)))
        if variant_data.get("beta_prior") is not None:
            variant_data["beta_prior"] = tuple(variant_data["beta_prior"])
        return cls(
            hypothesis_id=str(payload["hypothesis_id"]),
            experiment_id=str(payload["experiment_id"]),
            variant_id=str(payload["variant_id"]),
            replication=int(payload["replication"]),
            seed=int(payload["seed"]),
            rounds=int(payload["rounds"]),
            scenario=ScenarioSpec(**scenario_data),
            variant=VariantSpec(**variant_data),
            analysis=AnalysisSpec(**payload.get("analysis", {})),
            runtime=RuntimeSpec(**payload.get("runtime", {})),
        )


@dataclass(frozen=True)
class ExperimentSpec:
    hypothesis: HypothesisSpec
    experiment: ExperimentMeta
    scenario: ScenarioSpec
    variants: tuple[VariantSpec, ...]
    sweeps: tuple[SweepSpec, ...] = ()
    runtime: RuntimeSpec = RuntimeSpec()
    analysis: AnalysisSpec = AnalysisSpec()
    path: str | None = None

    @classmethod
    def from_toml(cls, path: str | Path) -> ExperimentSpec:
        target = Path(path)
        data = tomllib.loads(target.read_text(encoding="utf-8"))
        _reject_legacy_keys(data)

        hypothesis = HypothesisSpec(**_require_table(data, "hypothesis"))
        experiment = ExperimentMeta(**_require_table(data, "experiment"))
        _validate_family_sections(experiment, data.get("benchmark"))
        scenario = _parse_scenario(_require_table(data, "scenario"))
        variants = tuple(_parse_variant(item) for item in data.get("variants", ()))
        if not variants:
            raise ValueError("experiment spec requires at least one [[variants]] entry")
        sweeps = tuple(_parse_sweep(item) for item in data.get("sweeps", ()))
        runtime = RuntimeSpec(**data.get("runtime", {}))
        analysis = _parse_analysis(data.get("analysis", {}), hypothesis)
        return cls(
            hypothesis=hypothesis,
            experiment=experiment,
            scenario=scenario,
            variants=variants,
            sweeps=sweeps,
            runtime=runtime,
            analysis=analysis,
            path=str(target),
        )

    def expand_runs(self) -> list[ExpandedRunSpec]:
        expanded_variants: list[tuple[str, VariantSpec]] = []
        for variant in self.variants:
            matching = [sweep for sweep in self.sweeps if variant.id in sweep.applies_to]
            if not matching:
                expanded_variants.append((variant.id, variant))
                continue
            variants_for_base: list[tuple[str, VariantSpec]] = [(variant.id, variant)]
            for sweep in matching:
                next_variants: list[tuple[str, VariantSpec]] = []
                for _, current in variants_for_base:
                    for value in sweep.values:
                        updated = replace(current, **cast(dict[str, Any], {sweep.parameter: value}))
                        next_variants.append((f"{variant.id}__{sweep.parameter}_{_value_slug(value)}", updated))
                variants_for_base = next_variants
            expanded_variants.extend(variants_for_base)

        runs: list[ExpandedRunSpec] = []
        for variant_id, variant in expanded_variants:
            for replication in range(self.experiment.replications):
                runs.append(
                    ExpandedRunSpec(
                        hypothesis_id=self.hypothesis.id,
                        experiment_id=self.experiment.id,
                        variant_id=variant_id,
                        replication=replication,
                        seed=self.experiment.seed + replication,
                        rounds=self.experiment.rounds,
                        scenario=self.scenario,
                        variant=variant,
                        analysis=self.analysis,
                        runtime=self.runtime,
                    )
                )
        return runs

    def with_overrides(self, *, rounds: int | None = None, replications: int | None = None) -> ExperimentSpec:
        return replace(
            self,
            experiment=replace(
                self.experiment,
                rounds=self.experiment.rounds if rounds is None else int(rounds),
                replications=self.experiment.replications if replications is None else int(replications),
            ),
        )

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> ExperimentSpec:
        data = dict(payload)
        data["hypothesis"] = HypothesisSpec(**data["hypothesis"])
        data["experiment"] = ExperimentMeta(**data["experiment"])
        scenario = dict(data["scenario"])
        scenario["partner_types"] = tuple(scenario.get("partner_types", PARTNER_TYPE_ORDER))
        scenario["partner_type_params"] = dict(scenario.get("partner_type_params", {}))
        scenario["correlation_pairs"] = tuple(tuple(pair) for pair in scenario.get("correlation_pairs", ()))
        if scenario.get("initial_types") is not None:
            scenario["initial_types"] = tuple(scenario["initial_types"])
        if scenario.get("initial_stances") is not None:
            scenario["initial_stances"] = tuple(scenario["initial_stances"])
        for key in ("mutual_coop", "sucker", "temptation", "mutual_defect"):
            scenario[key] = tuple(scenario.get(key, getattr(ScenarioSpec, key)))
        scenario["stance_switches"] = tuple(
            StanceSwitchSpec(**item) for item in scenario.get("stance_switches", ())
        )
        scenario["type_switches"] = tuple(TypeSwitchSpec(**item) for item in scenario.get("type_switches", ()))
        data["scenario"] = ScenarioSpec(**scenario)
        data["variants"] = tuple(
            VariantSpec(
                **{
                    **item,
                    "beta_levels": tuple(item.get("beta_levels", ())),
                    "beta_prior": None if item.get("beta_prior") is None else tuple(item["beta_prior"]),
                }
            )
            for item in data["variants"]
        )
        data["sweeps"] = tuple(
            SweepSpec(**{**item, "values": tuple(item["values"]), "applies_to": tuple(item["applies_to"])})
            for item in data.get("sweeps", ())
        )
        data["runtime"] = RuntimeSpec(**data.get("runtime", {}))
        analysis = dict(data.get("analysis", {}))
        for key in ("compare", "switch_window", "metrics"):
            analysis[key] = tuple(analysis.get(key, ()))
        data["analysis"] = AnalysisSpec(**analysis)
        return cls(**data)


def load_experiment_specs(path: str | Path) -> list[ExperimentSpec]:
    """Load one TOML file as either a single experiment or an experiment suite."""
    target = Path(path)
    data = tomllib.loads(target.read_text(encoding="utf-8"))
    _reject_legacy_keys(data)
    if "suite" not in data:
        return [ExperimentSpec.from_toml(target)]
    return _parse_suite(data, target)


def _merge_table(*tables: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for table in tables:
        if table:
            merged.update(dict(table))
    return merged


def _parse_suite(data: dict[str, Any], path: Path) -> list[ExperimentSpec]:
    defaults = dict(data.get("defaults", {}))
    default_hypothesis = defaults.get("hypothesis", {})
    default_experiment = defaults.get("experiment", {})
    default_scenario = defaults.get("scenario", {})
    default_runtime = defaults.get("runtime", {})
    default_analysis = defaults.get("analysis", {})
    shared_variants = tuple(_parse_variant(item) for item in data.get("variants", ()))
    if not shared_variants:
        raise ValueError("suite config requires at least one shared [[variants]] entry")

    specs: list[ExperimentSpec] = []
    experiments = data.get("experiments", ())
    if not experiments:
        raise ValueError("suite config requires at least one [[experiments]] entry")

    for entry in experiments:
        experiment_entry = dict(entry)
        scenario_entry = experiment_entry.pop("scenario", {})
        hypothesis_entry = experiment_entry.pop("hypothesis", {})
        runtime_entry = experiment_entry.pop("runtime", {})
        analysis_entry = experiment_entry.pop("analysis", {})
        variant_entries = experiment_entry.pop("variants", None)
        seed_offset = int(experiment_entry.pop("seed_offset", 0))

        hypothesis = HypothesisSpec(**_merge_table(default_hypothesis, hypothesis_entry))
        experiment_data = _merge_table(default_experiment, experiment_entry)
        if "id" not in experiment_data:
            raise ValueError("suite experiment entry requires id")
        if "seed" in experiment_data:
            experiment_data["seed"] = int(experiment_data["seed"]) + seed_offset
        experiment = ExperimentMeta(**experiment_data)
        scenario = _parse_scenario(_merge_table(default_scenario, scenario_entry))
        variants = (
            tuple(_parse_variant(item) for item in variant_entries)
            if variant_entries is not None
            else shared_variants
        )
        runtime = RuntimeSpec(**_merge_table(default_runtime, runtime_entry))
        analysis = _parse_analysis(_merge_table(default_analysis, analysis_entry), hypothesis)
        specs.append(
            ExperimentSpec(
                hypothesis=hypothesis,
                experiment=experiment,
                scenario=scenario,
                variants=variants,
                runtime=runtime,
                analysis=analysis,
                path=str(path),
            )
        )
    return specs


def _require_table(data: dict[str, Any], name: str) -> dict[str, Any]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"experiment spec requires [{name}] table")
    return value


def _reject_legacy_keys(value: Any, path: str = "") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in LEGACY_PUBLIC_KEYS:
                location = f"{path}.{key}" if path else key
                raise ValueError(f"legacy public config key is not supported in TOML specs: {location}")
            _reject_legacy_keys(nested, f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            _reject_legacy_keys(item, f"{path}[{idx}]")


def _parse_scenario(data: dict[str, Any]) -> ScenarioSpec:
    scenario = dict(data)
    if scenario.get("payoff") not in PAYOFF_VALUES:
        raise ValueError(f"scenario.payoff must be one of {sorted(PAYOFF_VALUES)}")
    if scenario.get("assignment") not in ASSIGNMENT_VALUES:
        raise ValueError(f"scenario.assignment must be one of {sorted(ASSIGNMENT_VALUES)}")
    scenario["partner_types"] = tuple(scenario.get("partner_types", PARTNER_TYPE_ORDER))
    scenario["partner_type_params"] = dict(scenario.get("partner_type_params", {}))
    scenario["correlation_pairs"] = tuple(tuple(pair) for pair in scenario.get("correlation_pairs", ()))
    if "initial_types" in scenario:
        scenario["initial_types"] = tuple(scenario["initial_types"])
    if "initial_stances" in scenario:
        scenario["initial_stances"] = tuple(scenario["initial_stances"])
    for key in ("mutual_coop", "sucker", "temptation", "mutual_defect"):
        scenario[key] = tuple(scenario.get(key, getattr(ScenarioSpec, key)))
    scenario["stance_switches"] = tuple(StanceSwitchSpec(**item) for item in scenario.get("stance_switches", ()))
    scenario["type_switches"] = tuple(TypeSwitchSpec(**item) for item in scenario.get("type_switches", ()))
    return ScenarioSpec(**scenario)


def _validate_family_sections(experiment: ExperimentMeta, benchmark: object | None) -> None:
    if experiment.family not in FAMILY_VALUES:
        raise ValueError(f"experiment.family must be one of {sorted(FAMILY_VALUES)}")
    if benchmark is not None:
        raise ValueError("benchmark settings are not part of the active experiment surface")


def _parse_variant(data: dict[str, Any]) -> VariantSpec:
    variant = dict(data)
    if variant.get("affect") not in AFFECT_VALUES:
        raise ValueError(f"variant.affect must be one of {sorted(AFFECT_VALUES)}")
    variant["beta_levels"] = tuple(float(value) for value in variant.get("beta_levels", (0.5, 0.67, 1.0, 1.5, 2.0)))
    if variant.get("beta_prior") is not None:
        variant["beta_prior"] = tuple(float(value) for value in variant["beta_prior"])
        if len(variant["beta_prior"]) != len(variant["beta_levels"]):
            raise ValueError("variant.beta_prior must match variant.beta_levels length")
        if any(value < 0.0 for value in variant["beta_prior"]):
            raise ValueError("variant.beta_prior must be non-negative")
        if sum(variant["beta_prior"]) <= 0.0:
            raise ValueError("variant.beta_prior must have positive mass")
    return VariantSpec(**variant)


def _parse_sweep(data: dict[str, Any]) -> SweepSpec:
    return SweepSpec(
        parameter=str(data["parameter"]),
        values=tuple(data["values"]),
        applies_to=tuple(str(item) for item in data["applies_to"]),
    )


def _parse_analysis(data: dict[str, Any], hypothesis: HypothesisSpec) -> AnalysisSpec:
    normalized = dict(data)
    normalized.setdefault("primary", f"{_slugify(hypothesis.id)}_{_slugify(hypothesis.name)}")
    normalized["compare"] = tuple(normalized.get("compare", ()))
    normalized["switch_window"] = tuple(int(item) for item in normalized.get("switch_window", ()))
    normalized["metrics"] = tuple(normalized.get("metrics", ()))
    return AnalysisSpec(**normalized)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower())
    return slug.strip("_")


def _value_slug(value: float | int | str | bool) -> str:
    return str(value).replace(".", "p").replace("-", "neg")


__all__ = [
    "AnalysisSpec",
    "ExpandedRunSpec",
    "ExperimentMeta",
    "ExperimentSpec",
    "HypothesisSpec",
    "RuntimeSpec",
    "ScenarioSpec",
    "StanceSwitchSpec",
    "SweepSpec",
    "TypeSwitchSpec",
    "VariantSpec",
    "load_experiment_specs",
]
