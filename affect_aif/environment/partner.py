"""Partner process for the trust game."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from affect_aif.generative_model.partner_types import PartnerType
from affect_aif.generative_model.payoffs import COOPERATE, DEFECT


@dataclass
class Partner:
    """A scripted partner exposing the same action/outcome lifecycle as an agent."""

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

    def plan_and_act(self, correlation_action: int | None = None, correlation_strength: float = 0.9) -> int:
        """Choose an action using the current scripted type policy."""

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

    def sample_action(self, correlation_action: int | None = None, correlation_strength: float = 0.9) -> int:
        """Backward-compatible alias for the scripted action sampler."""

        return self.plan_and_act(
            correlation_action=correlation_action,
            correlation_strength=correlation_strength,
        )

    def observe_outcome(
        self,
        agent_action: int,
        partner_action: int | None = None,
        partner_payoff: float | None = None,
        agent_payoff: float | None = None,
    ):
        """Update partner-local context after an interaction completes."""

        del partner_action, partner_payoff, agent_payoff

        self.last_agent_action = int(agent_action)
        self.interaction_count += 1

    def update_after_interaction(self, agent_action: int):
        """Backward-compatible alias for the scripted outcome update."""

        self.observe_outcome(agent_action=agent_action)

    def force_type_switch(self, new_type: str):
        """Apply a configured type change and reset local context."""

        self.type_name = str(new_type)
        self.interaction_count = 0
        self.last_agent_action = COOPERATE
        self.last_partner_action = COOPERATE

    def maybe_switch_type(self, available_types: list[str], p_switch: float) -> bool:
        """Stochastically switch to a different latent type."""

        if self.rng.random() >= p_switch:
            return False

        candidates = [name for name in available_types if name != self.type_name]
        self.force_type_switch(str(self.rng.choice(candidates)))
        return True
