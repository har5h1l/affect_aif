"""Per-partner discrete Bayesian affective state tracking.

Phase 4 implementation: beta as a categorical hidden state with explicit
likelihood P(ε|β) and transition dynamics P(β_t|β_{t-1}), subject to
standard Bayesian inference rather than the continuous EMA update.
"""

from __future__ import annotations

import numpy as np


def _build_transition_matrix(num_levels: int, persistence: float) -> np.ndarray:
    """Build a tridiagonal persistent transition matrix with reflecting boundaries.

    B[:, j] = P(β_t | β_{t-1} = j). Diagonal = persistence; remaining
    probability splits equally between neighbors. At boundaries, the
    probability that would go out-of-bounds folds back to self-transition,
    making boundary states stickier (reflecting boundary).
    """
    L = num_levels
    B = np.zeros((L, L), dtype=np.float64)
    half_leak = (1.0 - persistence) / 2.0
    for j in range(L):
        B[j, j] = persistence
        if j > 0:
            B[j - 1, j] += half_leak
        else:
            B[j, j] += half_leak  # reflect
        if j < L - 1:
            B[j + 1, j] += half_leak
        else:
            B[j, j] += half_leak  # reflect
    return B


def _build_likelihood_matrix(
    num_surprise_bins: int,
    beta_levels: np.ndarray,
    alpha_charge: float = 3.0,
    sigma_0_sq: float = 0.25,
) -> np.ndarray:
    """Build a discretized likelihood matrix P(surprise_bin | beta_level).

    Shape: (num_surprise_bins, num_beta_levels). Each column sums to 1.
    Higher beta levels assign more probability to low surprise bins.

    This is the discretized form of the continuous likelihood used at runtime.
    Useful for theoretical analysis and visualization.
    """
    # Surprise bin centers in [0, 1]
    bin_centers = np.linspace(0.0, 1.0, num_surprise_bins, dtype=np.float64)
    L = len(beta_levels)
    A = np.zeros((num_surprise_bins, L), dtype=np.float64)
    for l_idx in range(L):
        bl = beta_levels[l_idx]
        for s_idx in range(num_surprise_bins):
            eps = bin_centers[s_idx]
            charge = alpha_charge * (sigma_0_sq - eps**2)
            A[s_idx, l_idx] = np.exp(charge * bl)
    # Normalize columns
    col_sums = A.sum(axis=0, keepdims=True)
    A /= col_sums + 1e-16
    return A


class DiscreteBetaState:
    """Manage per-partner affective precision via discrete Bayesian inference.

    Each partner's precision state β_k is a categorical distribution over L
    levels. On each observation, the posterior updates as:

        q(β_k^t) ∝ P(ε_k^t | β_k^t) · Σ_{β'} P(β_k^t | β') q(β_k^{t-1} = β')

    This is the same predict-then-correct scheme used for partner-type
    inference, extended to the precision state.
    """

    def __init__(
        self,
        num_partners: int,
        num_levels: int = 5,
        persistence: float = 0.8,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 0.5,
        beta_min: float | None = None,
        beta_max: float | None = None,
    ):
        self.num_partners = int(num_partners)
        self.num_levels = int(num_levels)
        self.persistence = float(persistence)
        self.alpha_charge = float(alpha_charge)
        self.sigma_0_sq = float(sigma_0_sq)
        self.initial_beta = float(initial_beta)

        # Beta levels: evenly spaced. Use beta_min/beta_max if provided.
        lo = float(beta_min) if beta_min is not None else 1.0 / (num_levels + 1)
        hi = float(beta_max) if beta_max is not None else num_levels / (num_levels + 1)
        self.beta_levels = np.linspace(lo, hi, num_levels, dtype=np.float64)

        # Transition matrix: B_beta[:, j] = P(β_t | β_{t-1} = j)
        self.B_beta = _build_transition_matrix(num_levels, persistence)

        # Initial posterior concentrated at the level nearest initial_beta
        self._initial_posterior = self._build_initial_posterior()

        self.reset()

    def _build_initial_posterior(self) -> np.ndarray:
        """Soft assignment concentrated at the level nearest initial_beta."""
        dists = np.abs(self.beta_levels - self.initial_beta)
        # Sharpness of 5 gives a moderately concentrated initial distribution
        # that can be sharpened or shifted by evidence
        log_posterior = -5.0 * dists
        log_posterior -= log_posterior.max()
        posterior = np.exp(log_posterior)
        posterior /= posterior.sum()
        return posterior

    def _likelihood(self, surprise: float) -> np.ndarray:
        """P(ε|β_l) for each level l (unnormalized).

        Uses charge = α(σ₀² - ε²) and likelihood ∝ exp(charge × β_l).
        This directly mirrors the continuous EMA's signed charge mechanism:
        low surprise (charge > 0) favors higher β, high surprise (charge < 0)
        favors lower β.
        """
        charge = self.alpha_charge * (self.sigma_0_sq - surprise**2)
        log_lik = charge * self.beta_levels
        log_lik -= log_lik.max()
        return np.exp(log_lik)

    def update(
        self,
        partner_idx: int,
        predicted_action_probs,
        observed_action: int,
    ) -> tuple[float, float]:
        """Bayesian predict-then-correct update of the precision posterior."""
        probs = np.asarray(predicted_action_probs, dtype=np.float64)
        surprise = 1.0 - probs[int(observed_action)]

        # Predict: prior = B @ previous posterior
        prior = self.B_beta @ self.posteriors[int(partner_idx)]
        prior /= prior.sum() + 1e-16

        # Update: posterior ∝ likelihood × prior
        lik = self._likelihood(float(surprise))
        posterior = lik * prior
        posterior /= posterior.sum() + 1e-16

        self.posteriors[int(partner_idx)] = posterior

        # Point estimate: posterior expectation
        beta = float(np.dot(posterior, self.beta_levels))
        self.betas[int(partner_idx)] = beta
        self.prediction_errors[int(partner_idx)] = float(surprise)

        self.beta_history.append(self.betas.copy())
        self.prediction_error_history.append(self.prediction_errors.copy())

        return beta, float(surprise)

    def get_beta(self, partner_idx: int) -> float:
        return float(self.betas[int(partner_idx)])

    def get_all_betas(self) -> np.ndarray:
        return self.betas.copy()

    def get_prediction_errors(self) -> np.ndarray:
        return self.prediction_errors.copy()

    def get_belief(self, partner_idx: int) -> np.ndarray:
        """Return the full discrete posterior q(β_k) for a partner."""
        return self.posteriors[int(partner_idx)].copy()

    def get_all_beliefs(self) -> np.ndarray:
        """Return posteriors for all partners. Shape: (num_partners, num_levels)."""
        return self.posteriors.copy()

    def get_belief_entropy(self, partner_idx: int) -> float:
        """Entropy of q(β_k) — measures uncertainty about the precision level."""
        p = self.posteriors[int(partner_idx)]
        return float(-np.sum(p * np.log(p + 1e-16)))

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
        self.posteriors = np.tile(self._initial_posterior, (self.num_partners, 1))
        initial_expected_beta = float(np.dot(self._initial_posterior, self.beta_levels))
        self.betas = np.full(self.num_partners, initial_expected_beta, dtype=np.float64)
        self.prediction_errors = np.full(self.num_partners, np.nan, dtype=np.float64)
        self.beta_history: list[np.ndarray] = [self.betas.copy()]
        self.prediction_error_history: list[np.ndarray] = [self.prediction_errors.copy()]
