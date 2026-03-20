"""Benchmark configuration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run across environments."""

    # Scenario
    scenario: str = "resource_sharing"
    agents: list[str] = field(default_factory=lambda: [
        "affective_shallow", "shallow_no_affect", "random", "tit_for_tat"
    ])

    # Scale
    num_replications: int = 10
    num_rounds: int = 100
    ticks_per_round: int = 10

    # Comparison
    run_trust_game: bool = True
    run_gridworld: bool = True

    # Trust game config overrides
    trust_game_overrides: dict = field(default_factory=dict)

    # Output
    output_dir: str = "results/benchmark"
    random_seed: int = 42

    @classmethod
    def from_json(cls, path: str) -> BenchmarkConfig:
        data = json.loads(Path(path).read_text())
        return cls(**data)

    def to_json(self, path: str):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2))


# Agent type registry: maps agent names to the info needed to create them.
# AIF agents are identified by condition number; baselines by class name.
AGENT_REGISTRY = {
    # Active inference agents (by condition ID)
    "deep_no_affect": {"type": "aif", "condition": 1},
    "affective_shallow": {"type": "aif", "condition": 2},
    "lesioned_shallow": {"type": "aif", "condition": 3},
    "shallow_no_affect": {"type": "aif", "condition": 4},
    "reward_avg_shallow": {"type": "aif", "condition": 5},
    "intermediate_3": {"type": "aif", "condition": 6},
    "intermediate_4": {"type": "aif", "condition": 7},
    "deep_affective": {"type": "aif", "condition": 8},
    "alexithymia": {"type": "aif", "condition": 9},
    "borderline": {"type": "aif", "condition": 10},
    "depression": {"type": "aif", "condition": 11},
    "variational_affective": {"type": "aif", "condition": 12},

    # Baseline agents
    "random": {"type": "baseline", "class": "RandomAgent"},
    "tit_for_tat": {"type": "baseline", "class": "TitForTatAgent"},
    "win_stay_lose_shift": {"type": "baseline", "class": "WinStayLoseShiftAgent"},
    "q_learning": {"type": "baseline", "class": "QLearningAgent"},
}
