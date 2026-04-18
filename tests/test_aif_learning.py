from __future__ import annotations

import numpy as np

import aif


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

    aif.update_pA(agent, obs=[0], learning_rate=1.0)

    assert agent.pA[0][0, 0] > 1.0
    np.testing.assert_array_equal(agent.pB[0], pB_before)
    np.testing.assert_array_equal(agent.pD[0], pD_before)
    np.testing.assert_array_equal(agent.pE, pE_before)


def test_update_pB_uses_qs_previous_and_action():
    agent = _build_agent()
    pA_before = agent.pA[0].copy()
    pD_before = agent.pD[0].copy()
    pE_before = agent.pE.copy()
    qs_previous = np.asarray([0.4, 0.6], dtype=float)

    aif.update_pB(agent, qs_previous=qs_previous, action=[1])

    assert agent.pB[0][0, 0, 1] > 1.0
    np.testing.assert_array_equal(agent.pA[0], pA_before)
    np.testing.assert_array_equal(agent.pD[0], pD_before)
    np.testing.assert_array_equal(agent.pE, pE_before)


def test_update_pD_accumulates_current_posterior():
    agent = _build_agent()
    pA_before = agent.pA[0].copy()
    pB_before = agent.pB[0].copy()
    pE_before = agent.pE.copy()

    aif.update_pD(agent, learning_rate=0.5)

    np.testing.assert_allclose(agent.pD[0], np.asarray([1.375, 1.125], dtype=float))
    np.testing.assert_array_equal(agent.pA[0], pA_before)
    np.testing.assert_array_equal(agent.pB[0], pB_before)
    np.testing.assert_array_equal(agent.pE, pE_before)


def test_update_pE_accumulates_policy_posterior():
    agent = _build_agent()
    pA_before = agent.pA[0].copy()
    pB_before = agent.pB[0].copy()
    pD_before = agent.pD[0].copy()

    aif.update_pE(agent, q_pi=np.asarray([0.25, 0.75], dtype=float), learning_rate=0.5)

    np.testing.assert_allclose(agent.pE, np.asarray([1.125, 1.375], dtype=float))
    np.testing.assert_array_equal(agent.pA[0], pA_before)
    np.testing.assert_array_equal(agent.pB[0], pB_before)
    np.testing.assert_array_equal(agent.pD[0], pD_before)
