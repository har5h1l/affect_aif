"""Condition metadata and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConditionSpec:
    """Stable metadata and construction settings for an experiment condition."""

    name: str
    description: str
    planning_horizon: int
    agent_kind: str
    use_information_gain: bool = True
    lesion_mode: str | None = None
    parameter_overrides: dict[str, float] = field(default_factory=dict)


CONDITIONS: dict[int, ConditionSpec] = {
    1: ConditionSpec("tau1_no_affect", "No affect at horizon 1", planning_horizon=1, agent_kind="base"),
    2: ConditionSpec("tau1_affect", "Affective agent at horizon 1", planning_horizon=1, agent_kind="affective"),
    3: ConditionSpec("tau2_no_affect", "No affect at horizon 2", planning_horizon=2, agent_kind="base"),
    4: ConditionSpec("tau2_affect", "Affective agent at horizon 2", planning_horizon=2, agent_kind="affective"),
    5: ConditionSpec("tau4_no_affect", "No affect at horizon 4", planning_horizon=4, agent_kind="base"),
    6: ConditionSpec("tau4_affect", "Affective agent at horizon 4", planning_horizon=4, agent_kind="affective"),
    7: ConditionSpec("tau8_no_affect", "No affect at horizon 8", planning_horizon=8, agent_kind="base"),
    8: ConditionSpec("tau8_affect", "Affective agent at horizon 8", planning_horizon=8, agent_kind="affective"),
    9: ConditionSpec("tau3_no_affect", "No affect at horizon 3", planning_horizon=3, agent_kind="base"),
    10: ConditionSpec("tau3_affect", "Affective agent at horizon 3", planning_horizon=3, agent_kind="affective"),
}

PRESET_CONDITIONS: dict[str, ConditionSpec] = {
    "lesioned": ConditionSpec(
        "lesioned",
        "Tau-4 affective lesion with decoupled affect-to-action pathway",
        planning_horizon=4,
        agent_kind="lesioned",
        lesion_mode="decouple",
    ),
    "no_epistemic": ConditionSpec(
        "no_epistemic",
        "Tau-4 affective agent without epistemic value",
        planning_horizon=4,
        agent_kind="affective",
        use_information_gain=False,
    ),
    "alexithymia": ConditionSpec(
        "alexithymia",
        "Tau-4 affective agent with blunted beta charging",
        planning_horizon=4,
        agent_kind="affective",
        parameter_overrides={"alpha_charge": 0.1},
    ),
    "borderline": ConditionSpec(
        "borderline",
        "Tau-4 affective agent with volatile beta dynamics",
        planning_horizon=4,
        agent_kind="affective",
        parameter_overrides={"alpha_charge": 12.0},
    ),
    "depression": ConditionSpec(
        "depression",
        "Tau-4 affective agent with pessimistic initial beta prior",
        planning_horizon=4,
        agent_kind="affective",
        parameter_overrides={"initial_beta": 2.0},
    ),
}


def get_condition_name(condition: int) -> str:
    return CONDITIONS[int(condition)].name


def get_condition_metadata(condition: int) -> ConditionSpec:
    return CONDITIONS[int(condition)]


def get_preset_condition(name: str) -> ConditionSpec:
    normalized = str(name).strip().lower()
    if normalized in PRESET_CONDITIONS:
        return PRESET_CONDITIONS[normalized]
    raise KeyError(f"Unknown preset condition '{name}'.")


def normalize_condition_name(name: str) -> str:
    normalized = str(name).strip().lower()
    for metadata in list(CONDITIONS.values()) + list(PRESET_CONDITIONS.values()):
        if normalized == metadata.name:
            return metadata.name
    raise KeyError(f"Unknown condition name '{name}'.")


def resolve_condition_spec(condition: int | str) -> ConditionSpec:
    if isinstance(condition, str):
        normalized = str(condition).strip().lower()
        if normalized.isdigit():
            return get_condition_metadata(int(normalized))
        if normalized in PRESET_CONDITIONS:
            return get_preset_condition(normalized)
        for condition_id, metadata in CONDITIONS.items():
            if normalized == metadata.name:
                return get_condition_metadata(condition_id)
        return get_preset_condition(normalized)
    return get_condition_metadata(condition)


__all__ = [
    "CONDITIONS",
    "ConditionSpec",
    "PRESET_CONDITIONS",
    "get_condition_metadata",
    "get_condition_name",
    "get_preset_condition",
    "normalize_condition_name",
    "resolve_condition_spec",
]
