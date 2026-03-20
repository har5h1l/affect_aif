"""Predefined MettaGrid/CoGames cooperation scenarios for benchmarking.

Each scenario defines a gridworld configuration designed to test
cooperation dynamics comparable to the trust game.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BenchmarkScenario:
    """A benchmark scenario configuration."""

    name: str
    description: str
    grid_width: int = 16
    grid_height: int = 16
    num_partners: int = 4
    num_rounds: int = 100
    ticks_per_round: int = 10
    partner_types: list[str] = field(default_factory=lambda: [
        "cooperator", "reciprocator", "exploiter", "random"
    ])
    resource_spawn_rate: float = 0.1
    episode_length: int = 1000


# Pre-defined scenarios

RESOURCE_SHARING = BenchmarkScenario(
    name="resource_sharing",
    description=(
        "Small arena with 1 focal agent + 4 partners. Resources spawn "
        "periodically. Partners follow scripted cooperation/defection policies. "
        "Tests whether per-partner precision tracking helps identify partner types "
        "in a spatially-embedded setting."
    ),
    grid_width=16,
    grid_height=16,
    num_partners=4,
    num_rounds=100,
    ticks_per_round=10,
    partner_types=["cooperator", "reciprocator", "exploiter", "random"],
)

BETRAYAL_ARENA = BenchmarkScenario(
    name="betrayal_arena",
    description=(
        "Cooperation scenario with a scheduled betrayal: one partner switches "
        "from cooperator to exploiter mid-episode. Tests adaptation speed "
        "in gridworld context."
    ),
    grid_width=16,
    grid_height=16,
    num_partners=2,
    num_rounds=100,
    ticks_per_round=10,
    partner_types=["cooperator", "random"],
)

LARGE_GROUP = BenchmarkScenario(
    name="large_group",
    description=(
        "Larger arena with 8 partners and more complex spatial dynamics. "
        "Tests scaling of per-partner tracking."
    ),
    grid_width=32,
    grid_height=32,
    num_partners=8,
    num_rounds=200,
    ticks_per_round=15,
    partner_types=[
        "cooperator", "cooperator",
        "reciprocator", "reciprocator",
        "exploiter", "exploiter",
        "random", "random",
    ],
)


SCENARIOS = {
    "resource_sharing": RESOURCE_SHARING,
    "betrayal_arena": BETRAYAL_ARENA,
    "large_group": LARGE_GROUP,
}


def get_scenario(name: str) -> BenchmarkScenario:
    """Look up a predefined scenario by name."""
    if name not in SCENARIOS:
        available = ", ".join(sorted(SCENARIOS.keys()))
        raise ValueError(f"Unknown scenario '{name}'. Available: {available}")
    return SCENARIOS[name]


def list_scenarios() -> list[str]:
    """Return names of all available scenarios."""
    return sorted(SCENARIOS.keys())
