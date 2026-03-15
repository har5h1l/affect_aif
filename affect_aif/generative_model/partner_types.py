"""Partner type definitions and behavioral policies."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from affect_aif.generative_model.payoffs import COOPERATE, DEFECT


PARTNER_TYPE_ORDER = ("cooperator", "reciprocator", "exploiter", "random")


@dataclass
class PartnerType:
    """Defines a partner's behavioral policy as a function of game history."""

    type_name: str
    params: dict = field(default_factory=dict)

    def get_action_probability(self, agent_last_action: int, round_number: int) -> float:
        """Return P(cooperate) given the observed interaction history."""

        if self.type_name == "cooperator":
            return float(self.params.get("p_coop", 0.9))

        if self.type_name == "reciprocator":
            mirror = float(self.params.get("p_mirror", 0.85))
            return mirror if agent_last_action == COOPERATE else 1.0 - mirror

        if self.type_name == "exploiter":
            switch_round = int(self.params.get("switch_round", 4))
            if round_number < switch_round:
                return float(self.params.get("p_coop_early", 0.85))
            return float(self.params.get("p_coop_late", 0.15))

        if self.type_name == "random":
            return float(self.params.get("p_coop", 0.5))

        raise ValueError(f"Unknown partner type '{self.type_name}'.")

    def get_action_distribution(self, agent_last_action: int, round_number: int) -> np.ndarray:
        """Return the full categorical distribution over partner actions."""

        p_coop = self.get_action_probability(agent_last_action=agent_last_action, round_number=round_number)
        return np.asarray([p_coop, 1.0 - p_coop], dtype=float)


def default_partner_type_params() -> dict[str, dict]:
    """Default parameterization for the canonical partner types."""

    return {
        "cooperator": {"p_coop": 0.9},
        "reciprocator": {"p_mirror": 0.85},
        "exploiter": {"p_coop_early": 0.85, "p_coop_late": 0.15, "switch_round": 4},
        "random": {"p_coop": 0.5},
    }
