"""Condition metadata and simple lookup helpers."""

from __future__ import annotations


CONDITIONS = {
    1: {"name": "deep_no_affect", "description": "Deep planner baseline"},
    2: {"name": "affective_shallow", "description": "Shallow planner with affective terminal values"},
    3: {"name": "lesioned_shallow", "description": "Shallow planner with decoupled affect"},
    4: {"name": "shallow_no_affect", "description": "Shallow planner baseline"},
    5: {"name": "reward_avg_shallow", "description": "Shallow planner with reward-average terminal values"},
    6: {"name": "intermediate_3_no_affect", "description": "Intermediate planner baseline at horizon 3"},
    7: {"name": "intermediate_4_no_affect", "description": "Intermediate planner baseline at horizon 4"},
    8: {"name": "deep_affective", "description": "Deep planner with affective terminal values"},
}


def get_condition_name(condition: int) -> str:
    return CONDITIONS[condition]["name"]
