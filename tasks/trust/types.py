"""Partner type definitions and stance-conditioned behavior tables."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from tasks.trust.stance import STANCE_ORDER, get_type_stance_cooperation_probability

PARTNER_TYPE_ORDER = ("cooperator", "reciprocator", "exploiter", "random")


@dataclass
class PartnerType:
    """Defines a partner's stance-conditioned action policy."""

    type_name: str
    params: dict = field(default_factory=dict)

    def get_action_probability(self, stance_name: str) -> float:
        """Return P(cooperate) under the partner's current stance."""

        stance = str(stance_name)
        if "cooperation_probabilities" in self.params:
            try:
                return float(self.params["cooperation_probabilities"][stance])
            except KeyError as exc:
                raise ValueError(f"Unknown stance '{stance}' for type '{self.type_name}'.") from exc
        return get_type_stance_cooperation_probability(self.type_name, stance)

    def get_action_distribution(self, stance_name: str) -> np.ndarray:
        """Return the full categorical distribution over partner actions."""

        p_coop = self.get_action_probability(stance_name=stance_name)
        return np.asarray([p_coop, 1.0 - p_coop], dtype=float)


def default_partner_type_params() -> dict[str, dict]:
    """Default parameterization for the canonical partner types."""

    return {
        type_name: {
            "cooperation_probabilities": {
                stance_name: get_type_stance_cooperation_probability(type_name, stance_name)
                for stance_name in STANCE_ORDER
            }
        }
        for type_name in PARTNER_TYPE_ORDER
    }
