"""Partner process for the trust game."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from affect_aif.generative_model.partner_types import PartnerType
from affect_aif.generative_model.payoffs import COOPERATE, DEFECT


@dataclass
class Partner:
    """A simulated partner with a hidden behavioral type."""

    partner_idx: int
    type_name: str
    type_lookup: dict[str, PartnerType]
    rng: np.random.Generator
    last_agent_action: int = COOPERATE
    interaction_count: int = 0
    last_partner_action: int = COOPERATE

    @property
    def type_impl(self) -> PartnerType:
        return self.type_lookup[self.type_name]

    def sample_action(self, correlation_action: int | None = None, correlation_strength: float = 0.9) -> int:
        """Sample the partner's action from its current type policy."""

        if correlation_action is not None and self.rng.random() < correlation_strength:
            action = int(correlation_action)
        else:
            p_coop = self.type_impl.get_action_probability(
                agent_last_action=self.last_agent_action,
                round_number=self.interaction_count,
            )
            action = COOPERATE if self.rng.random() < p_coop else DEFECT
        self.last_partner_action = action
        return action

    def update_after_interaction(self, agent_action: int):
        """Update partner-local context after an interaction completes."""

        self.last_agent_action = int(agent_action)
        self.interaction_count += 1

    def maybe_switch_type(self, available_types: list[str], p_switch: float) -> bool:
        """Stochastically switch to a different latent type."""

        if self.rng.random() >= p_switch:
            return False

        candidates = [name for name in available_types if name != self.type_name]
        self.type_name = str(self.rng.choice(candidates))
        self.interaction_count = 0
        self.last_agent_action = COOPERATE
        return True
