"""Per-entity HESP-aligned discrete Bayesian beta tracking."""

from __future__ import annotations

import numpy as np


DEFAULT_BETA_LEVELS = np.asarray([0.5, 0.67, 1.0, 1.5, 2.0], dtype=np.float64)


def affective_charge(prediction_error: float, *, alpha: float = 3.0, sigma_0_sq: float = 0.25) -> float:
    """Convert surprise magnitude into a signed HESP-style charge."""

    error = float(prediction_error)
    return float(alpha) * (float(sigma_0_sq) - error**2)


def _build_transition_matrix(num_levels: int, persistence: float) -> np.ndarray:
    """Build a tridiagonal persistent transition matrix with reflecting boundaries."""

    level_count = int(num_levels)
    transition = np.zeros((level_count, level_count), dtype=np.float64)
    half_leak = (1.0 - persistence) / 2.0
    for column in range(level_count):
        transition[column, column] = persistence
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
    """Per-entity affective precision tracking outside the POMDP state space."""

    def __init__(
        self,
        num_entities: int,
        num_levels: int = 5,
        persistence: float = 0.8,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 1.0,
        beta_min: float | None = None,
        beta_max: float | None = None,
    ):
        self.num_entities = int(num_entities)
        self.num_levels = int(num_levels)
        self.persistence = float(persistence)
        self.alpha_charge = float(alpha_charge)
        self.sigma_0_sq = float(sigma_0_sq)
        self.initial_beta = float(initial_beta)

        if beta_min is None and beta_max is None and num_levels == len(DEFAULT_BETA_LEVELS):
            self.beta_levels = DEFAULT_BETA_LEVELS.copy()
        else:
            lower = float(beta_min) if beta_min is not None else 0.5
            upper = float(beta_max) if beta_max is not None else 2.0
            self.beta_levels = np.linspace(lower, upper, num_levels, dtype=np.float64)

        self._transition = _build_transition_matrix(num_levels, persistence)
        self._initial_posterior = self._build_initial_posterior()
        self.reset()

    def _build_initial_posterior(self) -> np.ndarray:
        distances = np.abs(self.beta_levels - self.initial_beta)
        posterior = np.zeros((self.num_levels,), dtype=np.float64)
        posterior[int(np.argmin(distances))] = 1.0
        return posterior

    def update(
        self,
        entity_idx: int,
        predicted_action_probs,
        observed_action: int,
    ) -> tuple[float, float]:
        """Update precision belief for an entity from social prediction error."""

        probs = np.asarray(predicted_action_probs, dtype=np.float64)
        surprise = 1.0 - probs[int(observed_action)]
        charge = affective_charge(surprise, alpha=self.alpha_charge, sigma_0_sq=self.sigma_0_sq)

        prior = self._transition @ self.posteriors[int(entity_idx)]
        prior /= prior.sum() + 1e-16

        effective_precision = 1.0 / np.maximum(self.beta_levels, 1e-12)
        log_likelihood = charge * effective_precision
        log_likelihood -= log_likelihood.max()
        likelihood = np.exp(log_likelihood)
        likelihood /= likelihood.sum() + 1e-16

        posterior = likelihood * prior
        posterior /= posterior.sum() + 1e-16

        self.posteriors[int(entity_idx)] = posterior
        beta = float(np.dot(posterior, self.beta_levels))
        self.betas[int(entity_idx)] = beta
        self.prediction_errors[int(entity_idx)] = float(surprise)

        self.beta_history.append(self.betas.copy())
        self.prediction_error_history.append(self.prediction_errors.copy())

        return beta, float(surprise)

    def get_beta(self, entity_idx: int) -> float:
        return float(self.betas[int(entity_idx)])

    def get_all_betas(self) -> np.ndarray:
        return self.betas.copy()

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
