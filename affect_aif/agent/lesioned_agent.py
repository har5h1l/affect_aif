"""Affective agent with a lesioned affect-to-action pathway."""

from __future__ import annotations

import jax.numpy as jnp

from affect_aif.agent.affective_agent import AffectiveAgent


class LesionedAgent(AffectiveAgent):
    """Affective architecture with decoupled or frozen affective influence on action."""

    def __init__(self, *args, lesion_mode: str = "decouple", **kwargs):
        initial_beta = float(kwargs.get("initial_beta", 0.5))
        super().__init__(*args, **kwargs)
        self.lesion_mode = lesion_mode
        self._frozen_beta = initial_beta

    def current_mu(self) -> float:
        if self.lesion_mode == "decouple":
            return 0.0
        return super().current_mu()

    def terminal_signal(self):
        if self.lesion_mode == "freeze":
            return jnp.full((self.num_partners,), self._frozen_beta, dtype=jnp.float32)
        return super().terminal_signal()

    def precision_signal(self):
        if self.lesion_mode == "freeze":
            return jnp.full((self.num_partners,), self._frozen_beta, dtype=jnp.float32)
        return super().precision_signal()

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float):
        if self.lesion_mode == "freeze":
            del partner_idx, partner_action, payoff
            return
        super()._update_auxiliary_states(partner_idx=partner_idx, partner_action=partner_action, payoff=payoff)
