"""Condition metadata and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConditionMetadata:
    """Stable metadata for a supported experiment condition."""

    name: str
    description: str
    aliases: tuple[str, ...] = ()


CONDITIONS: dict[int, ConditionMetadata] = {
    1: ConditionMetadata("deep_no_affect", "Deep planner baseline"),
    2: ConditionMetadata("affective_shallow", "Shallow planner with affective terminal values"),
    3: ConditionMetadata("lesioned_shallow", "Shallow planner with decoupled affect"),
    4: ConditionMetadata("shallow_no_affect", "Shallow planner baseline"),
    5: ConditionMetadata("reward_avg_shallow", "Shallow planner with reward-average terminal values"),
    6: ConditionMetadata("intermediate_3_no_affect", "Intermediate planner baseline at horizon 3"),
    7: ConditionMetadata("intermediate_4_no_affect", "Intermediate planner baseline at horizon 4"),
    8: ConditionMetadata("deep_affective", "Deep planner with affective terminal values"),
    9: ConditionMetadata("alexithymia", "Blunted affective charging (alpha_charge=0.1)"),
    10: ConditionMetadata("borderline", "Volatile affect (alpha_charge=12.0, lambda_smooth=0.5)"),
    11: ConditionMetadata("depression", "Persistently low baseline precision (initial_beta=0.2)"),
    12: ConditionMetadata(
        "variational_affective",
        "Shallow planner with variational discrete beta",
        aliases=("discrete_affective_shallow",),
    ),
}


def get_condition_name(condition: int) -> str:
    return CONDITIONS[condition].name


def get_condition_metadata(condition: int) -> ConditionMetadata:
    return CONDITIONS[condition]


def normalize_condition_name(name: str) -> str:
    normalized = str(name).strip().lower()
    for metadata in CONDITIONS.values():
        if normalized == metadata.name or normalized in metadata.aliases:
            return metadata.name
    raise KeyError(f"Unknown condition name '{name}'.")


__all__ = [
    "CONDITIONS",
    "ConditionMetadata",
    "get_condition_metadata",
    "get_condition_name",
    "normalize_condition_name",
]
