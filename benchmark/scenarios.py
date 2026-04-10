"""Predefined MettaGrid/CoGames cooperation scenarios for benchmarking.

Each scenario defines a gridworld configuration designed to test
cooperation dynamics comparable to the trust game.
"""

from __future__ import annotations

from typing import Any
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
    assignment_mode: str = "random"
    p_switch: float = 0.05
    initial_partner_types: list[str] | None = None
    scheduled_type_switches: list[dict[str, Any]] = field(default_factory=list)
    resource_spawn_rate: float = 0.1
    episode_length: int = 1000

    def trust_game_defaults(self) -> dict[str, Any]:
        """Return trust-game-compatible defaults for this scenario."""

        defaults: dict[str, Any] = {
            "num_partners": int(self.num_partners),
            "assignment_mode": str(self.assignment_mode),
            "p_switch": float(self.p_switch),
            "partner_types": [str(name) for name in self.partner_types],
        }
        if self.initial_partner_types is not None:
            defaults["initial_partner_types"] = [str(name) for name in self.initial_partner_types]
        if self.scheduled_type_switches:
            defaults["scheduled_type_switches"] = [dict(event) for event in self.scheduled_type_switches]
        return defaults


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
    assignment_mode="agent_choice",
    p_switch=0.0,
    initial_partner_types=["cooperator", "random"],
    scheduled_type_switches=[{"partner_idx": 0, "round": 50, "to_type": "exploiter"}],
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
