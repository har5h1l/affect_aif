"""Dirichlet-parameter learning helpers."""

from __future__ import annotations

import numpy as np

from aif.agent import Agent
from aif.maths import dirichlet_expected_value
from aif.utils import obj_array


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


def update_pA(agent: Agent, obs: list[int], learning_rate: float = 1.0) -> None:
    """Update the agent's likelihood Dirichlet and refresh ``A`` in place."""

    if agent.pA is None:
        raise ValueError("update_pA called on Agent with pA=None")
    if agent.qs is None:
        raise ValueError("update_pA called before any inference")

    agent.pA = update_likelihood_dirichlet(agent.pA, obs, agent.qs, learning_rate=learning_rate)
    for modality in range(len(agent.pA)):
        agent.A[modality] = np.asarray(
            dirichlet_expected_value(np.asarray(agent.pA[modality], dtype=float), backend="numpy"),
            dtype=float,
        )


def update_pB(agent: Agent, qs_previous: np.ndarray, action: list[int]) -> None:
    """Update the agent's transition Dirichlet and refresh ``B`` in place."""

    if agent.pB is None:
        raise ValueError("update_pB called on Agent with pB=None")
    if agent.qs is None:
        raise ValueError("update_pB called before any inference")

    agent.pB = update_transition_dirichlet(agent.pB, action, agent.qs, qs_previous)
    for factor in range(len(agent.pB)):
        agent.B[factor] = np.asarray(
            dirichlet_expected_value(np.asarray(agent.pB[factor], dtype=float), backend="numpy"),
            dtype=float,
        )


def update_pD(agent: Agent, learning_rate: float = 1.0) -> None:
    """Accumulate the current posterior into the agent's initial-state prior."""

    if agent.pD is None:
        raise ValueError("update_pD called on Agent with pD=None")
    if agent.qs is None:
        raise ValueError("update_pD called before any inference")

    if isinstance(agent.pD, np.ndarray) and agent.pD.dtype == object:
        updated = np.empty(len(agent.pD), dtype=object)
        for factor in range(len(agent.pD)):
            updated[factor] = np.asarray(agent.pD[factor], dtype=float) + learning_rate * np.asarray(
                agent.qs[factor], dtype=float
            )
            agent.D[factor] = np.asarray(
                dirichlet_expected_value(np.asarray(updated[factor], dtype=float), backend="numpy"),
                dtype=float,
            )
        agent.pD = updated
        return

    agent.pD = np.asarray(agent.pD, dtype=float) + learning_rate * np.asarray(agent.qs, dtype=float)
    agent.D = np.asarray(dirichlet_expected_value(np.asarray(agent.pD, dtype=float), backend="numpy"), dtype=float)


def update_pE(agent: Agent, q_pi: np.ndarray, learning_rate: float = 0.5) -> None:
    """Accumulate the policy posterior into the agent's policy prior."""

    if agent.pE is None:
        raise ValueError("update_pE called on Agent with pE=None")

    agent.pE = np.asarray(agent.pE, dtype=float) + learning_rate * np.asarray(q_pi, dtype=float)
    expected = np.asarray(dirichlet_expected_value(np.asarray(agent.pE, dtype=float), backend="numpy"), dtype=float)
    agent.E = np.log(expected + 1e-16)
