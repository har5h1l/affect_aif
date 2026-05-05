"""Affective agent with a lesioned affect-to-action pathway."""

from __future__ import annotations

import numpy as np

from tasks.trust.agents.affective import AffectiveAgent


class LesionedAgent(AffectiveAgent):
    """Affective architecture with decoupled or frozen affective influence on action."""

    def __init__(self, *args, lesion_mode: str = "decouple", **kwargs):
        normalized_mode = "fixed" if lesion_mode == "freeze" else str(lesion_mode)
        if normalized_mode not in {"decouple", "fixed"}:
            raise ValueError("lesion_mode must be 'decouple' or 'fixed'.")
        kwargs["affect_modulates_precision"] = False
        super().__init__(*args, **kwargs)
        self.lesion_mode = normalized_mode

    def precision_signal(self):
        if self.lesion_mode in {"decouple", "fixed"}:
            return np.ones((self.num_partners,), dtype=float)
        return super().precision_signal()

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float):
        if self.lesion_mode == "fixed":
            del partner_idx, partner_action, payoff
            return
        super()._update_auxiliary_states(partner_idx=partner_idx, partner_action=partner_action, payoff=payoff)
