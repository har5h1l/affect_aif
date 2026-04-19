from __future__ import annotations

import numpy as np

import aif
from aif.policies import gamma_per_policy, sample_action as sample_action_from_module


def _build_agent(action_sampling: str = "marginal", seed: int = 7) -> aif.Agent:
    A = np.empty(1, dtype=object)
    A[0] = np.eye(2, dtype=float)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0], dtype=float)
    D = np.empty(1, dtype=object)
    D[0] = np.asarray([0.5, 0.5], dtype=float)
    policies = np.asarray([[0], [1]], dtype=int)
    return aif.Agent(
        A=A,
        B=B,
        C=C,
        D=D,
        policies=policies,
        action_sampling=action_sampling,
        rng=np.random.default_rng(seed),
    )


def test_sample_action_marginal_uses_agent_state():
    agent = _build_agent("marginal", seed=11)
    q_pi = np.asarray([0.05, 0.95], dtype=float)

    action = sample_action_from_module(agent, q_pi)

    assert action == 1


def test_sample_action_reproducible_with_agent_rng():
    q_pi = np.asarray([0.45, 0.55], dtype=float)
    a1 = _build_agent("marginal", seed=123)
    a2 = _build_agent("marginal", seed=123)

    seq1 = [sample_action_from_module(a1, q_pi) for _ in range(20)]
    seq2 = [sample_action_from_module(a2, q_pi) for _ in range(20)]

    assert seq1 == seq2


def test_sample_action_full_returns_factorized_action():
    agent = _build_agent("full", seed=5)
    agent.policies = np.asarray([[[0, 1]], [[1, 0]]], dtype=int)
    q_pi = np.asarray([0.0, 1.0], dtype=float)

    action = sample_action_from_module(agent, q_pi)

    np.testing.assert_array_equal(action, np.asarray([1, 0], dtype=int))


def test_package_reexport_matches_module_wrapper():
    agent = _build_agent("marginal", seed=17)
    q_pi = np.asarray([0.3, 0.7], dtype=float)

    action = aif.sample_action(agent, q_pi)
    agent = _build_agent("marginal", seed=17)
    module_action = sample_action_from_module(agent, q_pi)

    assert action == module_action


def test_gamma_per_policy_uses_inverse_beta_expectation():
    first_partners = np.asarray([0, 1, 0, 1], dtype=int)
    precision_signal = np.asarray([0.5, 2.0], dtype=float)

    gamma_values = gamma_per_policy(
        gamma_base=1.0,
        first_partners=first_partners,
        precision_signal=precision_signal,
    )

    np.testing.assert_allclose(gamma_values, np.asarray([2.0, 0.5, 2.0, 0.5]))
