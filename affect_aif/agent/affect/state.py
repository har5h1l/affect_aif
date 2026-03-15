"""Per-partner affective state tracking."""

from __future__ import annotations

import math

import jax.numpy as jnp
import numpy as np


class AffectiveState:
    """Manage slow-timescale affective precision estimates for each partner."""

    def __init__(
        self,
        num_partners: int,
        lambda_smooth: float = 0.6,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 0.5,
    ):
        self.num_partners = int(num_partners)
        self.lambda_smooth = float(lambda_smooth)
        self.alpha_charge = float(alpha_charge)
        # (1 - 0.5)^2: expected squared surprise under a maximally uninformative binary partner.
        self.sigma_0_sq = float(sigma_0_sq)
        self.initial_beta = float(initial_beta)
        self.reset()

    def update(
        self,
        partner_idx: int,
        predicted_action_probs,
        observed_action: int,
    ) -> tuple[float, float]:
        """Apply a slow but responsive precision update from squared surprise."""

        probs = jnp.asarray(predicted_action_probs, dtype=jnp.float32)
        surprise = 1.0 - probs[int(observed_action)]
        charge = self.alpha_charge * (self.sigma_0_sq - surprise**2)
        current_beta = self.betas[int(partner_idx)]
        squashed = jax_sigmoid(charge)
        updated = self.lambda_smooth * current_beta + (1.0 - self.lambda_smooth) * squashed

        self.betas = self.betas.at[int(partner_idx)].set(updated)
        self.prediction_errors = self.prediction_errors.at[int(partner_idx)].set(surprise)
        self.beta_history.append(np.asarray(self.betas, dtype=float))
        self.prediction_error_history.append(np.asarray(self.prediction_errors, dtype=float))
        return float(updated), float(surprise)

    def get_beta(self, partner_idx: int) -> float:
        return float(self.betas[int(partner_idx)])

    def get_all_betas(self) -> np.ndarray:
        return np.asarray(self.betas, dtype=float)

    def get_prediction_errors(self) -> np.ndarray:
        return np.asarray(self.prediction_errors, dtype=float)

    def get_history(self, partner_idx: int | None = None) -> np.ndarray:
        history = np.asarray(self.beta_history, dtype=float)
        if partner_idx is None:
            return history
        return history[:, int(partner_idx)]

    def get_prediction_error_history(self, partner_idx: int | None = None) -> np.ndarray:
        history = np.asarray(self.prediction_error_history, dtype=float)
        if partner_idx is None:
            return history
        return history[:, int(partner_idx)]

    def reset(self):
        self.betas = jnp.full((self.num_partners,), self.initial_beta, dtype=jnp.float32)
        self.prediction_errors = jnp.full((self.num_partners,), jnp.nan, dtype=jnp.float32)
        self.beta_history: list[np.ndarray] = [np.asarray(self.betas, dtype=float)]
        self.prediction_error_history: list[np.ndarray] = [np.asarray(self.prediction_errors, dtype=float)]


def jax_sigmoid(x):
    """Small local sigmoid helper to avoid importing the full JAX NN stack here."""

    return 1.0 / (1.0 + jnp.exp(-x))
