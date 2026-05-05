"""Affective trust-game agent."""

from __future__ import annotations

import numpy as np

from tasks.trust.affect import DiscreteBetaState
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
        affect_modulates_precision: bool = True,
        **kwargs,
    ):
        del num_partners
        super().__init__(model, **kwargs)
        self.affect_modulates_precision = bool(affect_modulates_precision)
        beta_levels = None
        if num_levels != 5:
            beta_levels = np.linspace(0.5, 2.0, int(num_levels), dtype=np.float64)
        self.affect = DiscreteBetaState(
            num_entities=self.num_partners,
            beta_levels=beta_levels,
            persistence=persistence,
            alpha_charge=alpha_charge,
            sigma_0_sq=sigma_0_sq,
            initial_beta=initial_beta,
        )
        self.latest_surprise_by_partner = np.full((self.num_partners,), np.nan, dtype=float)
        self.latest_prediction_probability_by_partner = np.full((self.num_partners,), np.nan, dtype=float)

    def reset(self):
        super().reset()
        if hasattr(self, "affect"):
            self.affect.reset()
        if hasattr(self, "num_partners"):
            self.latest_surprise_by_partner = np.full((self.num_partners,), np.nan, dtype=float)
            self.latest_prediction_probability_by_partner = np.full((self.num_partners,), np.nan, dtype=float)

    def precision_signal(self):
        if not getattr(self, "affect_modulates_precision", True):
            return np.ones((self.num_partners,), dtype=float)
        return np.asarray(self.affect.expected_beta(), dtype=float)

    def _predicted_partner_action_probability(self, partner_idx: int, partner_action: int) -> float:
        partner_idx = int(partner_idx)
        partner_action = int(partner_action)
        if self.pending_prediction_partner == partner_idx:
            predicted_action_probs = np.asarray(self.pending_prediction_probs, dtype=np.float64)
            if 0 <= partner_action < predicted_action_probs.size:
                probability = float(predicted_action_probs[partner_action])
                if np.isfinite(probability):
                    return float(np.clip(probability, 0.0, 1.0))
        return self._predicted_partner_action_probability_from_A(partner_idx, partner_action)

    def _predicted_partner_action_probability_from_A(self, partner_idx: int, partner_action: int) -> float:
        joint_belief = self.model.as_joint_belief(self.partner_beliefs[int(partner_idx)])
        action_likelihood = np.asarray(self.bundle.A[0], dtype=float)[int(partner_action)]
        while action_likelihood.ndim > joint_belief.ndim:
            action_idx = 0
            if self.pending_social_action is not None and 0 <= int(self.pending_social_action) < action_likelihood.shape[-1]:
                action_idx = int(self.pending_social_action)
            action_likelihood = action_likelihood[..., action_idx]
        if action_likelihood.shape != joint_belief.shape:
            fallback_probs = self.model.partner_action_distribution(joint_belief)
            return float(fallback_probs[int(partner_action)])
        probability = float(np.sum(joint_belief * action_likelihood))
        return float(np.clip(probability, 0.0, 1.0))

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float) -> None:
        del payoff
        probability = self._predicted_partner_action_probability(partner_idx, partner_action)
        surprise = 1.0 - probability
        self.affect.update(
            entity=partner_idx,
            surprise=surprise,
        )
        self.latest_surprise_by_partner[int(partner_idx)] = float(surprise)
        self.latest_prediction_probability_by_partner[int(partner_idx)] = float(probability)

    def get_betas(self) -> np.ndarray:
        return self.affect.expected_beta()

    def get_prediction_errors(self) -> np.ndarray:
        return self.affect.get_prediction_errors()
