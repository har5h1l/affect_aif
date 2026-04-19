"""Affective active inference agent."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from aif.affect.beta import DiscreteBetaState
from agent.base import BaseAgent


class AffectiveAgent(BaseAgent):
    """Shallow planner with per-partner affective precision summaries."""

    def __init__(
        self,
        A,
        B,
        C,
        D,
        model,
        planning_horizon: int = 2,
        gamma: float = 1.0,
        lr: float = 0.1,
        num_partners: int = 4,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 1.0,
        num_levels: int = 5,
        persistence: float = 0.8,
        **kwargs,
    ):
        super().__init__(
            A=A,
            B=B,
            C=C,
            D=D,
            model=model,
            planning_horizon=planning_horizon,
            gamma=gamma,
            lr=lr,
            **kwargs,
        )
        self.affect = DiscreteBetaState(
            num_entities=num_partners,
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
        return jnp.asarray(self.affect.get_all_betas(), dtype=jnp.float32)

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float):
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
