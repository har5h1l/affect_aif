from __future__ import annotations

import numpy as np

import aif
from aif.learning import update_pA, update_pB, update_pD, update_pE
from aif.maths import dirichlet_expected_value


def _build_agent() -> aif.Agent:
    A = np.empty(1, dtype=object)
    A[0] = np.asarray([[0.8, 0.2], [0.2, 0.8]], dtype=float)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0], dtype=float)
    D = np.empty(1, dtype=object)
    D[0] = np.asarray([0.6, 0.4], dtype=float)
    policies = np.asarray([[0], [1]], dtype=int)

    agent = aif.Agent(
        A=A,
        B=B,
        C=C,
        D=D,
        policies=policies,
        pA=np.empty(1, dtype=object),
        pB=np.empty(1, dtype=object),
        pD=np.empty(1, dtype=object),
        pE=np.asarray([1.0, 1.0], dtype=float),
    )
    agent.pA[0] = np.ones((2, 2), dtype=float)
    agent.pB[0] = np.ones((2, 2, 2), dtype=float)
    agent.pD[0] = np.asarray([1.0, 1.0], dtype=float)
    agent.reset()
    agent.qs[0] = np.asarray([0.75, 0.25], dtype=float)
    return agent


def test_update_pA_uses_current_posterior_and_leaves_other_priors_alone():
    agent = _build_agent()
    pB_before = agent.pB[0].copy()
    pD_before = agent.pD[0].copy()
    pE_before = agent.pE.copy()
    A_before = agent.A[0].copy()

    update_pA(agent, obs=[0], learning_rate=1.0)

    assert agent.pA[0][0, 0] > 1.0
    assert not np.array_equal(agent.A[0], A_before)
    np.testing.assert_allclose(
        agent.A[0],
        dirichlet_expected_value(np.asarray(agent.pA[0], dtype=float), backend="numpy"),
    )
    np.testing.assert_array_equal(agent.pB[0], pB_before)
    np.testing.assert_array_equal(agent.pD[0], pD_before)
    np.testing.assert_array_equal(agent.pE, pE_before)


def test_update_pB_uses_qs_previous_and_action():
    agent = _build_agent()
    pA_before = agent.pA[0].copy()
    pD_before = agent.pD[0].copy()
    pE_before = agent.pE.copy()
    B_before = agent.B[0].copy()
    qs_previous = np.asarray([0.4, 0.6], dtype=float)

    update_pB(agent, qs_previous=qs_previous, action=[1])

    assert agent.pB[0][0, 0, 1] > 1.0
    assert not np.array_equal(agent.B[0], B_before)
    np.testing.assert_allclose(
        agent.B[0],
        dirichlet_expected_value(np.asarray(agent.pB[0], dtype=float), backend="numpy"),
    )
    np.testing.assert_array_equal(agent.pA[0], pA_before)
    np.testing.assert_array_equal(agent.pD[0], pD_before)
    np.testing.assert_array_equal(agent.pE, pE_before)


def test_update_pD_accumulates_current_posterior():
    agent = _build_agent()
    pA_before = agent.pA[0].copy()
    pB_before = agent.pB[0].copy()
    pE_before = agent.pE.copy()
    D_before = agent.D[0].copy()

    update_pD(agent, learning_rate=0.5)

    np.testing.assert_allclose(agent.pD[0], np.asarray([1.375, 1.125], dtype=float))
    assert not np.array_equal(agent.D[0], D_before)
    np.testing.assert_allclose(
        agent.D[0],
        dirichlet_expected_value(np.asarray(agent.pD[0], dtype=float), backend="numpy"),
    )
    np.testing.assert_array_equal(agent.pA[0], pA_before)
    np.testing.assert_array_equal(agent.pB[0], pB_before)
    np.testing.assert_array_equal(agent.pE, pE_before)


def test_update_pE_accumulates_policy_posterior():
    agent = _build_agent()
    pA_before = agent.pA[0].copy()
    pB_before = agent.pB[0].copy()
    pD_before = agent.pD[0].copy()
    E_before = agent.E.copy() if agent.E is not None else None

    update_pE(agent, q_pi=np.asarray([0.25, 0.75], dtype=float), learning_rate=0.5)

    np.testing.assert_allclose(agent.pE, np.asarray([1.125, 1.375], dtype=float))
    assert E_before is None or not np.array_equal(agent.E, E_before)
    np.testing.assert_allclose(
        agent.E,
        np.log(dirichlet_expected_value(np.asarray(agent.pE, dtype=float), backend="numpy") + 1e-16),
    )
    np.testing.assert_array_equal(agent.pA[0], pA_before)
    np.testing.assert_array_equal(agent.pB[0], pB_before)
    np.testing.assert_array_equal(agent.pD[0], pD_before)


def test_package_reexports_match_learning_module_wrappers():
    agent = _build_agent()

    aif.update_pA(agent, obs=[0], learning_rate=1.0)

    assert agent.pA[0][0, 0] > 1.0


def test_update_wrappers_raise_for_missing_priors_or_posterior():
    agent = _build_agent()
    agent.qs = None
    with np.testing.assert_raises_regex(ValueError, "before any inference"):
        update_pA(agent, obs=[0])
    with np.testing.assert_raises_regex(ValueError, "before any inference"):
        update_pB(agent, qs_previous=np.asarray([0.4, 0.6], dtype=float), action=[1])
    with np.testing.assert_raises_regex(ValueError, "before any inference"):
        update_pD(agent)

    agent.reset()
    agent.pA = None
    with np.testing.assert_raises_regex(ValueError, "pA=None"):
        update_pA(agent, obs=[0])
    agent.pA = np.empty(1, dtype=object)
    agent.pA[0] = np.ones((2, 2), dtype=float)
    agent.pB = None
    with np.testing.assert_raises_regex(ValueError, "pB=None"):
        update_pB(agent, qs_previous=np.asarray([0.4, 0.6], dtype=float), action=[1])
    agent.pB = np.empty(1, dtype=object)
    agent.pB[0] = np.ones((2, 2, 2), dtype=float)
    agent.pD = None
    with np.testing.assert_raises_regex(ValueError, "pD=None"):
        update_pD(agent)
    agent.pD = np.empty(1, dtype=object)
    agent.pD[0] = np.asarray([1.0, 1.0], dtype=float)
    agent.pE = None
    with np.testing.assert_raises_regex(ValueError, "pE=None"):
        update_pE(agent, q_pi=np.asarray([0.5, 0.5], dtype=float))
