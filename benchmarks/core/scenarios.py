"""Predefined trust-task evaluation scenarios."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BenchmarkScenario:
    """A benchmark scenario configuration."""

    name: str
    description: str
    num_partners: int = 4
    num_rounds: int = 100
    partner_types: list[str] = field(default_factory=lambda: ["cooperator", "reciprocator", "exploiter", "random"])
    assignment_mode: str = "random"
    p_switch: float = 0.05
    initial_partner_types: list[str] | None = None
    scheduled_type_switches: list[dict[str, Any]] = field(default_factory=list)

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


RESOURCE_SHARING = BenchmarkScenario(
    name="resource_sharing",
    description=(
        "Trust-task arena with 1 focal agent and 4 partners. Tests whether "
        "per-partner precision tracking helps identify partner types."
    ),
    num_partners=4,
    num_rounds=100,
    partner_types=["cooperator", "reciprocator", "exploiter", "random"],
)

BETRAYAL_ARENA = BenchmarkScenario(
    name="betrayal_arena",
    description=(
        "Cooperation scenario with a scheduled betrayal: one partner switches "
        "from cooperator to exploiter mid-episode. Tests adaptation speed."
    ),
    num_partners=2,
    num_rounds=100,
    assignment_mode="agent_choice",
    p_switch=0.0,
    initial_partner_types=["cooperator", "random"],
    scheduled_type_switches=[{"partner_idx": 0, "round": 50, "to_type": "exploiter"}],
)

LARGE_GROUP = BenchmarkScenario(
    name="large_group",
    description="Larger trust-task arena with 8 partners. Tests scaling of per-partner tracking.",
    num_partners=8,
    num_rounds=200,
    partner_types=[
        "cooperator",
        "cooperator",
        "reciprocator",
        "reciprocator",
        "exploiter",
        "exploiter",
        "random",
        "random",
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
