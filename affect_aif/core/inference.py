"""Variational state inference."""

from __future__ import annotations

import numpy as np

from affect_aif.core.maths import kl_divergence, log_stable, normalize, softmax, spm_dot
from affect_aif.core.utils import obj_array


def _ensure_obj_prior(prior) -> np.ndarray:
    if isinstance(prior, np.ndarray) and prior.dtype == object:
        return prior
    wrapped = obj_array(1)
    wrapped[0] = np.asarray(prior, dtype=float)
    return wrapped


def _factor_message(log_likelihood: np.ndarray, qs: np.ndarray, factor: int) -> np.ndarray:
    message = log_likelihood
    axes = [axis for axis in range(log_likelihood.ndim) if axis != factor]
    for axis in reversed(axes):
        q_idx = axis if axis < factor else axis - 1
        message = np.tensordot(message, qs[q_idx], axes=([axis], [0]))
    return message


def update_posterior_states(
    A: np.ndarray,
    obs: list[int],
    prior,
    num_iter: int = 16,
    method: str = "fpi",
) -> np.ndarray:
    """Posterior state inference via fixed-point updates."""

    del method
    prior = _ensure_obj_prior(prior)
    num_factors = len(prior)
    qs = obj_array(num_factors)
    for factor in range(num_factors):
        qs[factor] = np.asarray(prior[factor], dtype=float).copy()

    if num_factors == 1:
        likelihood = np.ones_like(qs[0], dtype=float)
        for modality, observation in enumerate(obs):
            likelihood *= np.asarray(A[modality][observation], dtype=float)
        qs[0] = normalize(likelihood * prior[0], axis=0, backend="numpy").squeeze()
        return qs

    for _ in range(num_iter):
        for factor in range(num_factors):
            log_q = log_stable(prior[factor], backend="numpy")
            for modality, observation in enumerate(obs):
                log_likelihood = log_stable(A[modality][observation], backend="numpy")
                message = _factor_message(log_likelihood, qs, factor)
                log_q = log_q + message
            qs[factor] = softmax(log_q, backend="numpy")

    return qs


def compute_vfe(
    qs: np.ndarray,
    A: np.ndarray,
    B: np.ndarray,
    obs: list[int],
    prior,
) -> float:
    """Compute variational free energy for the current posterior."""

    del B
    prior = _ensure_obj_prior(prior)
    complexity = 0.0
    accuracy = 0.0

    for factor in range(len(qs)):
        complexity += float(kl_divergence(qs[factor], prior[factor], backend="numpy"))

    if len(qs) == 1:
        predicted_obs = []
        for modality, observation in enumerate(obs):
            likelihood = np.asarray(A[modality][observation], dtype=float)
            predicted_obs.append(float(np.sum(qs[0] * log_stable(likelihood, backend="numpy"))))
        accuracy = float(np.sum(predicted_obs))
    else:
        for modality, observation in enumerate(obs):
            likelihood_tensor = np.asarray(A[modality][observation], dtype=float)
            expected_log_likelihood = spm_dot(log_stable(likelihood_tensor, backend="numpy"), qs, backend="numpy")
            accuracy += float(expected_log_likelihood)

    return complexity - accuracy
