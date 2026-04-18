"""Generic active-inference primitives."""

from __future__ import annotations

import numpy as np

from aif.agent import Agent
from aif.inference import infer_policies, infer_states
from aif.learning import update_likelihood_dirichlet, update_transition_dirichlet
from aif.maths import dirichlet_expected_value, log_stable, softmax
from aif.policies import construct_policies, sample_action as _sample_action_impl
from aif.utils import obj_array


def sample_action(agent, q_pi: np.ndarray):
    """Sample an action using the agent's policies, mode, and RNG."""

    return _sample_action_impl(
        q_pi=q_pi,
        policies=agent.policies,
        timestep=0,
        sampling_mode=agent.action_sampling,
        rng=agent.rng,
    )


def update_pA(agent, obs, learning_rate: float = 1.0) -> None:
    """Update the agent's likelihood Dirichlet and refresh A."""

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


def update_pB(agent, qs_previous, action) -> None:
    """Update the agent's transition Dirichlet and refresh B."""

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


def update_pD(agent, learning_rate: float = 1.0) -> None:
    """Update the agent's initial-state Dirichlet and refresh D."""

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


def update_pE(agent, q_pi, learning_rate: float = 0.5) -> None:
    """Update the agent's policy-prior Dirichlet and refresh E."""

    if agent.pE is None:
        raise ValueError("update_pE called on Agent with pE=None")

    agent.pE = np.asarray(agent.pE, dtype=float) + learning_rate * np.asarray(q_pi, dtype=float)
    expected = np.asarray(dirichlet_expected_value(np.asarray(agent.pE, dtype=float), backend="numpy"), dtype=float)
    agent.E = np.log(expected + 1e-16)


import aif.learning as _learning_module
import aif.policies as _policies_module

_policies_module.sample_action = sample_action
_learning_module.update_pA = update_pA
_learning_module.update_pB = update_pB
_learning_module.update_pD = update_pD
_learning_module.update_pE = update_pE

__all__ = ["softmax", "log_stable", "obj_array", "construct_policies"]
