"""Discrete variational affective state tracking per partner."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np


class VariationalAffectiveState:
    """Track per-partner beta as a categorical posterior over discrete levels."""

    def __init__(
        self,
        num_partners: int,
        num_levels: int = 5,
        persistence: float = 0.8,
        sigma_sq_max: float = 0.25,
        floor_val: float = 0.01,
        initial_beta: float = 0.5,
    ):
        self.num_partners = int(num_partners)
        self.num_levels = int(num_levels)
        self.persistence = float(persistence)
        self.sigma_sq_max = float(sigma_sq_max)
        self.floor_val = float(floor_val)
        self.initial_beta = float(initial_beta)
        self.levels = self._build_levels(self.num_levels)
        self.transition = self._build_transition(self.num_levels, self.persistence)
        self.reset()

    def update(
        self,
        partner_idx: int,
        predicted_action_probs,
        observed_action: int,
    ) -> tuple[float, float]:
        """Apply a categorical predict-then-correct update from squared surprise."""

        partner_idx = int(partner_idx)
        probs = jnp.asarray(predicted_action_probs, dtype=jnp.float32)
        surprise = 1.0 - probs[int(observed_action)]
        epsilon_sq = surprise**2

        sigma_sq = self.sigma_sq_max * (1.0 - self.levels) + self.floor_val
        log_lik = -epsilon_sq / (2.0 * sigma_sq) - 0.5 * jnp.log(sigma_sq)
        likelihood = jnp.exp(log_lik - jnp.max(log_lik))

        q_prev = self.posteriors[partner_idx]
        predicted = self.transition.T @ q_prev
        unnormalized = likelihood * predicted
        q_new = unnormalized / jnp.sum(unnormalized)
        expected_beta = jnp.sum(self.levels * q_new)

        self.posteriors = self.posteriors.at[partner_idx].set(q_new)
        self.prediction_errors = self.prediction_errors.at[partner_idx].set(surprise)
        self.beta_history.append(np.asarray(self.get_all_betas(), dtype=float))
        self.prediction_error_history.append(np.asarray(self.prediction_errors, dtype=float))
        return float(expected_beta), float(surprise)

    def get_beta(self, partner_idx: int) -> float:
        return float(jnp.sum(self.levels * self.posteriors[int(partner_idx)]))

    def get_all_betas(self) -> np.ndarray:
        return np.asarray(jnp.sum(self.posteriors * self.levels[None, :], axis=1), dtype=float)

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

    def get_posterior(self, partner_idx: int) -> np.ndarray:
        return np.asarray(self.posteriors[int(partner_idx)], dtype=float)

    def reset(self):
        init_idx = int(np.argmin(np.abs(np.asarray(self.levels, dtype=float) - self.initial_beta)))
        init_posterior = jnp.zeros((self.num_levels,), dtype=jnp.float32).at[init_idx].set(1.0)
        self.posteriors = jnp.tile(init_posterior[None, :], (self.num_partners, 1))
        self.prediction_errors = jnp.full((self.num_partners,), jnp.nan, dtype=jnp.float32)
        self.beta_history: list[np.ndarray] = [np.asarray(self.get_all_betas(), dtype=float)]
        self.prediction_error_history: list[np.ndarray] = [np.asarray(self.prediction_errors, dtype=float)]

    @staticmethod
    def _build_levels(num_levels: int) -> jnp.ndarray:
        if num_levels == 5:
            return jnp.asarray([0.1, 0.3, 0.5, 0.7, 0.9], dtype=jnp.float32)
        return jnp.linspace(0.1, 0.9, num_levels, dtype=jnp.float32)

    @staticmethod
    def _build_transition(num_levels: int, persistence: float) -> jnp.ndarray:
        transition = np.zeros((num_levels, num_levels), dtype=np.float32)
        off_diag = (1.0 - persistence) / 2.0

        for idx in range(num_levels):
            transition[idx, idx] = persistence
            if idx > 0:
                transition[idx, idx - 1] = off_diag
            if idx < num_levels - 1:
                transition[idx, idx + 1] = off_diag

        transition[0, 0] += off_diag
        transition[-1, -1] += off_diag
        return jnp.asarray(transition, dtype=jnp.float32)
