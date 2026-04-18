from __future__ import annotations

import numpy as np

import aif
from agent.model.trust_game import TrustGameModel
from experiment.config import ExperimentConfig


def _build_toy_agent():
    A = np.empty(1, dtype=object)
    A[0] = np.asarray([[0.8, 0.2], [0.2, 0.8]], dtype=float)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0], dtype=float)
    D = np.empty(1, dtype=object)
    D[0] = np.asarray([0.5, 0.5], dtype=float)
    policies = np.asarray([[[0]], [[1]]], dtype=int)
    return aif.Agent(A=A, B=B, C=C, D=D, policies=policies)


def test_infer_states_uses_d_when_qs_and_action_are_absent():
    agent = _build_toy_agent()

    qs = aif.infer_states(agent, obs=[0])

    np.testing.assert_allclose(qs[0], [0.8, 0.2], atol=1e-12)
    np.testing.assert_allclose(agent.qs[0], [0.8, 0.2], atol=1e-12)


def test_infer_states_uses_existing_qs_when_no_action_is_provided():
    agent = _build_toy_agent()
    agent.qs = np.empty(1, dtype=object)
    agent.qs[0] = np.asarray([0.9, 0.1], dtype=float)

    qs = aif.infer_states(agent, obs=[0])

    np.testing.assert_allclose(qs[0], [0.72 / 0.74, 0.02 / 0.74], atol=1e-12)


def test_infer_states_predicts_through_b_when_action_is_provided():
    agent = _build_toy_agent()
    agent.qs = np.empty(1, dtype=object)
    agent.qs[0] = np.asarray([0.9, 0.1], dtype=float)

    qs = aif.infer_states(agent, obs=[0], action=[1])

    np.testing.assert_allclose(qs[0], [0.08 / 0.26, 0.18 / 0.26], atol=1e-12)


def test_infer_policies_returns_q_pi_and_g_with_sane_shapes():
    agent = _build_toy_agent()
    agent.reset()

    q_pi, G = aif.infer_policies(agent)

    assert q_pi.shape == (2,)
    assert G.shape == (2,)
    np.testing.assert_allclose(q_pi.sum(), 1.0, atol=1e-12)
    assert np.all(np.isfinite(G))


def test_infer_states_matches_trust_game_joint_posterior_buggy_path():
    model = TrustGameModel(ExperimentConfig(num_partners=2, observation_noise=0.0))
    num_types = model.num_types
    num_stances = model.num_stances
    num_states = num_types * num_stances

    A = np.empty(1, dtype=object)
    A[0] = model.A[0].reshape(2, num_states)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(num_states), np.eye(num_states)], axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0], dtype=float)
    D = np.empty(1, dtype=object)
    D[0] = np.full(num_states, 1.0 / num_states, dtype=float)

    agent = aif.Agent(A=A, B=B, C=C, D=D, policies=np.asarray([[[0]]], dtype=int))

    qs = aif.infer_states(agent, obs=[0])
    posterior = model.infer_joint_posterior(
        D[0].reshape(num_types, num_stances),
        observation=[0, 2],
        own_action=0,
    )

    np.testing.assert_allclose(qs[0].reshape(num_types, num_stances), posterior, atol=1e-10)
