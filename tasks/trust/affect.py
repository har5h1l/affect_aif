"""Task-local affective precision tracking for trust agents.

The trust task represents per-partner affect as an expected beta rate. Callers
that modulate policy precision should keep the HESP inverse-beta convention:

    gamma_k = gamma_base / expected_beta_k
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

DEFAULT_BETA_LEVELS = np.asarray([0.5, 0.67, 1.0, 1.5, 2.0], dtype=np.float64)
LOG_SURPRISE_BASELINE_SQ = float(np.log(2.0) ** 2)


def surprise_from_probability(probability: float) -> float:
    """Convert an observed-outcome probability into Hesp-style surprisal."""

    probability_value = float(probability)
    if not np.isfinite(probability_value):
        raise ValueError("probability must be finite")
    clipped = float(np.clip(probability_value, 1e-16, 1.0))
    return float(-np.log(clipped))


def _affective_charge(surprise: float, *, alpha: float, sigma_0_sq: float) -> float:
    """Convert surprise magnitude into a signed HESP-style charge."""

    error = float(surprise)
    return float(alpha) * (float(sigma_0_sq) - error**2)


def _build_transition_matrix(num_levels: int, persistence: float) -> np.ndarray:
    """Build a tridiagonal persistent transition matrix with reflecting boundaries."""

    level_count = int(num_levels)
    transition = np.zeros((level_count, level_count), dtype=np.float64)
    half_leak = (1.0 - float(persistence)) / 2.0
    for column in range(level_count):
        transition[column, column] = float(persistence)
        if column > 0:
            transition[column - 1, column] += half_leak
        else:
            transition[column, column] += half_leak
        if column < level_count - 1:
            transition[column + 1, column] += half_leak
        else:
            transition[column, column] += half_leak
    return transition


class DiscreteBetaState:
    """Per-entity Bayesian beta tracking outside the POMDP state space."""

    def __init__(
        self,
        num_entities: int,
        initial_beta: float = 1.0,
        beta_levels: Sequence[float] | None = None,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = LOG_SURPRISE_BASELINE_SQ,
        persistence: float = 0.8,
        initial_prior: Sequence[float] | None = None,
    ) -> None:
        self.num_entities = int(num_entities)
        self.alpha_charge = float(alpha_charge)
        self.sigma_0_sq = float(sigma_0_sq)
        self.persistence = float(persistence)
        self.initial_beta = float(initial_beta)

        if self.num_entities <= 0:
            raise ValueError("num_entities must be positive")
        if not np.isfinite(self.alpha_charge) or self.alpha_charge <= 0.0:
            raise ValueError("alpha_charge must be finite and positive")
        if not np.isfinite(self.sigma_0_sq) or self.sigma_0_sq <= 0.0:
            raise ValueError("sigma_0_sq must be finite and positive")
        if not np.isfinite(self.initial_beta) or self.initial_beta <= 0.0:
            raise ValueError("initial_beta must be finite and positive")
        if not np.isfinite(self.persistence) or not 0.0 <= self.persistence <= 1.0:
            raise ValueError("persistence must be between 0 and 1")

        if beta_levels is None:
            self.beta_levels = DEFAULT_BETA_LEVELS.copy()
        else:
            self.beta_levels = np.asarray(list(beta_levels), dtype=np.float64)
        self.num_levels = int(self.beta_levels.shape[0])
        if self.num_levels == 0:
            raise ValueError("beta_levels must be non-empty")
        if not np.all(np.isfinite(self.beta_levels)):
            raise ValueError("beta_levels must be finite")
        if not np.all(self.beta_levels > 0.0):
            raise ValueError("beta_levels must be strictly positive")
        self._specified_initial_prior = None if initial_prior is None else np.asarray(list(initial_prior), dtype=float)
        if self._specified_initial_prior is not None:
            if self._specified_initial_prior.shape != (self.num_levels,):
                raise ValueError("initial_prior must match beta_levels length")
            if not np.all(np.isfinite(self._specified_initial_prior)):
                raise ValueError("initial_prior must be finite")
            if np.any(self._specified_initial_prior < 0.0):
                raise ValueError("initial_prior must be non-negative")
            if float(self._specified_initial_prior.sum()) <= 0.0:
                raise ValueError("initial_prior must have positive mass")

        self._transition = _build_transition_matrix(self.num_levels, self.persistence)
        self._initial_posterior = self._build_initial_posterior()
        self.reset()

    def _build_initial_posterior(self) -> np.ndarray:
        if self._specified_initial_prior is not None:
            posterior = self._specified_initial_prior.astype(np.float64, copy=True)
            posterior /= posterior.sum()
            return posterior
        distances = np.abs(self.beta_levels - self.initial_beta)
        posterior = np.zeros((self.num_levels,), dtype=np.float64)
        posterior[int(np.argmin(distances))] = 1.0
        return posterior

    def expected_beta(self) -> np.ndarray:
        """Return expected beta for each entity."""

        return self.betas.copy()

    def update(self, entity: int, surprise: float) -> None:
        """Update an entity's beta belief from an observed surprise value."""

        entity_idx = int(entity)
        surprise_value = float(surprise)
        if not np.isfinite(surprise_value):
            raise ValueError("surprise must be finite")
        charge = _affective_charge(
            surprise_value,
            alpha=self.alpha_charge,
            sigma_0_sq=self.sigma_0_sq,
        )

        prior = self._transition @ self.posteriors[entity_idx]
        prior /= prior.sum() + 1e-16

        inverse_beta = 1.0 / np.maximum(self.beta_levels, 1e-12)
        log_likelihood = charge * inverse_beta
        log_likelihood -= log_likelihood.max()
        likelihood = np.exp(log_likelihood)
        likelihood /= likelihood.sum() + 1e-16

        posterior = likelihood * prior
        posterior /= posterior.sum() + 1e-16

        self.posteriors[entity_idx] = posterior
        self.betas[entity_idx] = float(np.dot(posterior, self.beta_levels))
        self.prediction_errors[entity_idx] = surprise_value

        self.beta_history.append(self.betas.copy())
        self.prediction_error_history.append(self.prediction_errors.copy())

    def get_beta(self, entity_idx: int) -> float:
        return float(self.betas[int(entity_idx)])

    def get_all_betas(self) -> np.ndarray:
        return self.expected_beta()

    def get_prediction_error(self, entity_idx: int) -> float:
        return float(self.prediction_errors[int(entity_idx)])

    def get_prediction_errors(self) -> np.ndarray:
        return self.prediction_errors.copy()

    def get_belief(self, entity_idx: int) -> np.ndarray:
        """Return the full discrete posterior ``q(beta_entity)`` for one entity."""

        return self.posteriors[int(entity_idx)].copy()

    def get_all_beliefs(self) -> np.ndarray:
        """Return posteriors for all entities. Shape: ``(num_entities, num_levels)``."""

        return self.posteriors.copy()

    def get_belief_entropy(self, entity_idx: int) -> float:
        posterior = self.posteriors[int(entity_idx)]
        return float(-np.sum(posterior * np.log(posterior + 1e-16)))

    def get_history(self, entity_idx: int | None = None) -> np.ndarray:
        history = np.asarray(self.beta_history, dtype=float)
        if entity_idx is None:
            return history
        return history[:, int(entity_idx)]

    def get_prediction_error_history(self, entity_idx: int | None = None) -> np.ndarray:
        history = np.asarray(self.prediction_error_history, dtype=float)
        if entity_idx is None:
            return history
        return history[:, int(entity_idx)]

    def reset(self) -> None:
        self.posteriors = np.tile(self._initial_posterior, (self.num_entities, 1))
        initial_expected_beta = float(np.dot(self._initial_posterior, self.beta_levels))
        self.betas = np.full(self.num_entities, initial_expected_beta, dtype=np.float64)
        self.prediction_errors = np.full(self.num_entities, np.nan, dtype=np.float64)
        self.beta_history: list[np.ndarray] = [self.betas.copy()]
        self.prediction_error_history: list[np.ndarray] = [self.prediction_errors.copy()]
