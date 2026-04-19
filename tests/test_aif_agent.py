from __future__ import annotations

import numpy as np

import aif


def _build_agent():
    A = np.empty(1, dtype=object)
    A[0] = np.asarray([[0.8, 0.2], [0.2, 0.8]], dtype=float)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0], dtype=float)
    D = np.empty(1, dtype=object)
    D[0] = np.asarray([0.6, 0.4], dtype=float)
    policies = np.asarray([[[0]], [[1]]], dtype=int)
    return aif.Agent(A=A, B=B, C=C, D=D, policies=policies)


def test_agent_constructs_with_expected_defaults():
    agent = _build_agent()

    assert np.array_equal(agent.A[0], np.asarray([[0.8, 0.2], [0.2, 0.8]], dtype=float))
    assert np.array_equal(agent.B[0], np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1))
    assert np.array_equal(agent.C[0], np.asarray([1.0, 0.0], dtype=float))
    assert np.array_equal(agent.D[0], np.asarray([0.6, 0.4], dtype=float))
    assert np.array_equal(agent.policies, np.asarray([[[0]], [[1]]], dtype=int))
    assert agent.qs is None
    assert agent.E is None
    assert agent.pA is None
    assert agent.pB is None
    assert agent.pD is None
    assert agent.pE is None
    assert agent.gamma == 1.0
    assert agent.use_utility is True
    assert agent.use_information_gain is True
    assert agent.action_sampling == "marginal"
    assert isinstance(agent.rng, np.random.Generator)


def test_agent_reset_copies_d_into_qs():
    agent = _build_agent()

    agent.reset()

    assert agent.qs is not None
    np.testing.assert_allclose(agent.qs[0], agent.D[0])
    assert agent.qs[0] is not agent.D[0]


def test_agent_reset_leaves_optional_fields_alone():
    agent = _build_agent()
    agent.pA = np.empty(1, dtype=object)
    agent.pA[0] = np.ones((2, 2), dtype=float)
    agent.pB = np.empty(1, dtype=object)
    agent.pB[0] = np.ones((2, 2, 2), dtype=float)

    agent.reset()

    assert agent.pA is not None
    assert agent.pB is not None
    np.testing.assert_array_equal(agent.pA[0], np.ones((2, 2), dtype=float))
    np.testing.assert_array_equal(agent.pB[0], np.ones((2, 2, 2), dtype=float))


def test_agent_default_rng_is_reproducible():
    a1 = _build_agent()
    a2 = _build_agent()

    seq1 = a1.rng.integers(0, 100, size=8)
    seq2 = a2.rng.integers(0, 100, size=8)

    np.testing.assert_array_equal(seq1, seq2)
