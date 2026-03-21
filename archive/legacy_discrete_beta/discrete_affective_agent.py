"""Affective active inference agent with discrete Bayesian beta inference.

Phase 4: replaces the continuous EMA beta update with a categorical hidden
state subject to standard Bayesian inference (predict-then-correct with
explicit likelihood and transition dynamics).
"""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from affect_aif.agent.affect.discrete_state import DiscreteBetaState
from affect_aif.agent.base_agent import BaseAgent


class DiscreteAffectiveAgent(BaseAgent):
    """Shallow planner with per-partner discrete Bayesian precision tracking."""

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
        num_beta_levels: int = 5,
        beta_persistence: float = 0.8,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 0.5,
        mu: float = 0.0,
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
        self.mu = float(mu)
        self.affect = DiscreteBetaState(
            num_partners=num_partners,
            num_levels=num_beta_levels,
            persistence=beta_persistence,
            alpha_charge=alpha_charge,
            sigma_0_sq=sigma_0_sq,
            initial_beta=initial_beta,
        )

    def reset(self):
        super().reset()
        if hasattr(self, "affect"):
            self.affect.reset()

    def current_mu(self) -> float:
        return float(self.mu)

    def terminal_signal(self):
        return jnp.asarray(self.affect.get_all_betas(), dtype=jnp.float32)

    def precision_signal(self):
        return jnp.asarray(self.affect.get_all_betas(), dtype=jnp.float32)

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float):
        del payoff
        if self.pending_prediction_partner != partner_idx:
            return
        self.affect.update(
            partner_idx=partner_idx,
            predicted_action_probs=self.pending_prediction_probs,
            observed_action=partner_action,
        )

    def get_betas(self) -> np.ndarray:
        return self.affect.get_all_betas()

    def get_prediction_errors(self) -> np.ndarray:
        return self.affect.get_prediction_errors()

    def get_beta_beliefs(self) -> np.ndarray:
        """Return discrete posteriors over beta levels for all partners.

        Shape: (num_partners, num_beta_levels). Each row sums to 1.
        """
        return self.affect.get_all_beliefs()
