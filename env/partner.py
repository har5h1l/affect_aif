"""Partner process for the trust game."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from agent.model.types import PartnerType
from agent.model.payoffs import COOPERATE, DEFECT
from agent.model.stance import (
    AGENT_CHARACTER_ORDER,
    cooperation_evidence_strength,
    posterior_to_stance,
    update_agent_character_posterior,
)

_REPRESENTATIVE_POSTERIORS = {
    "trusting": np.asarray([0.75, 0.10, 0.15], dtype=float),
    "neutral": np.asarray([0.45, 0.15, 0.40], dtype=float),
    "hostile": np.asarray([0.15, 0.70, 0.15], dtype=float),
}


@dataclass
class Partner:
    """A scripted partner exposing the same action/outcome lifecycle as an agent."""

    partner_idx: int
    type_name: str
    stance_name: str
    type_lookup: dict[str, PartnerType]
    rng: np.random.Generator
    num_social_actions: int = 2
    last_partner_action: int = COOPERATE
    agent_character_posterior: np.ndarray = field(
        default_factory=lambda: np.full(len(AGENT_CHARACTER_ORDER), 1.0 / len(AGENT_CHARACTER_ORDER), dtype=float)
    )

    @property
    def type_impl(self) -> PartnerType:
        return self.type_lookup[self.type_name]

    def plan_and_act(self, correlation_action: int | None = None, correlation_strength: float = 0.9) -> int:
        """Choose an action using the current scripted type policy."""

        if correlation_action is not None and self.rng.random() < correlation_strength:
            action = int(correlation_action)
        else:
            p_coop = self.type_impl.get_action_probability(self.stance_name)
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
        evidence = cooperation_evidence_strength(agent_action, self.num_social_actions)
        self.agent_character_posterior = update_agent_character_posterior(
            self.agent_character_posterior,
            cooperation_evidence_strength=evidence,
        )
        self.stance_name = posterior_to_stance(self.agent_character_posterior)

    def update_after_interaction(self, agent_action: int):
        """Backward-compatible alias for the scripted outcome update."""

        self.observe_outcome(agent_action=agent_action)

    def force_type_switch(self, new_type: str):
        """Apply a configured type change while preserving stance history."""

        self.type_name = str(new_type)

    def force_stance_switch(self, new_stance: str):
        """Apply a configured stance change and align the latent posterior."""

        self.stance_name = str(new_stance)
        self.agent_character_posterior = np.asarray(_REPRESENTATIVE_POSTERIORS[self.stance_name], dtype=float).copy()

    def maybe_switch_type(self, available_types: list[str], p_switch: float) -> bool:
        """Stochastically switch to a different latent type."""

        if self.rng.random() >= p_switch:
            return False

        candidates = [name for name in available_types if name != self.type_name]
        self.force_type_switch(str(self.rng.choice(candidates)))
        return True
