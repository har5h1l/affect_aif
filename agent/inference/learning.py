"""Dirichlet-parameter learning helpers."""

from __future__ import annotations

import numpy as np

from agent.inference.utils import obj_array


def _ensure_obj(x):
    if isinstance(x, np.ndarray) and x.dtype == object:
        return x
    arr = obj_array(1)
    arr[0] = np.asarray(x, dtype=float)
    return arr


def update_likelihood_dirichlet(
    qA: np.ndarray,
    obs: list[int],
    qs: np.ndarray,
    learning_rate: float = 1.0,
) -> np.ndarray:
    """Conjugate likelihood update for categorical observations."""

    qA = qA.copy()
    qs = _ensure_obj(qs)
    for modality, observation in enumerate(obs):
        if len(qs) == 1:
            qA[modality][observation, ...] += learning_rate * qs[0]
            continue

        increment = qs[0]
        for factor in range(1, len(qs)):
            increment = np.multiply.outer(increment, qs[factor])
        qA[modality][observation, ...] += learning_rate * increment
    return qA


def update_transition_dirichlet(
    qB: np.ndarray,
    actions: list[int],
    qs_current: np.ndarray,
    qs_previous: np.ndarray,
) -> np.ndarray:
    """Conjugate transition update for categorical latent dynamics."""

    qB = qB.copy()
    qs_current = _ensure_obj(qs_current)
    qs_previous = _ensure_obj(qs_previous)
    for factor in range(len(qs_current)):
        action = actions[min(factor, len(actions) - 1)]
        qB[factor][:, :, action] += np.outer(qs_current[factor], qs_previous[factor])
    return qB
