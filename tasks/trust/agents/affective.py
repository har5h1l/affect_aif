"""Affective trust-game agent."""

from __future__ import annotations

import numpy as np

from aif.affect.beta import DiscreteBetaState
from tasks.trust.agents.base import TrustGameAgent
from tasks.trust.models import TrustGameModel


class AffectiveAgent(TrustGameAgent):
    """Trust-game agent with per-entity affective precision summaries."""

    def __init__(
        self,
        model: TrustGameModel,
        *,
        num_partners: int | None = None,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 1.0,
        num_levels: int = 5,
        persistence: float = 0.8,
        **kwargs,
    ):
        del num_partners
        super().__init__(model, **kwargs)
        self.affect = DiscreteBetaState(
            num_entities=self.num_partners,
            num_levels=num_levels,
            persistence=persistence,
            alpha_charge=alpha_charge,
            sigma_0_sq=sigma_0_sq,
            initial_beta=initial_beta,
        )

    def reset(self):
        super().reset()
        if hasattr(self, "affect"):
            self.affect.reset()

    def precision_signal(self):
        return np.asarray(self.affect.get_all_betas(), dtype=float)

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float) -> None:
        del payoff
        if self.pending_prediction_partner != partner_idx:
            return
        self.affect.update(
            entity_idx=partner_idx,
            predicted_action_probs=self.pending_prediction_probs,
            observed_action=partner_action,
        )

    def get_betas(self) -> np.ndarray:
        return self.affect.get_all_betas()

    def get_prediction_errors(self) -> np.ndarray:
        return self.affect.get_prediction_errors()
