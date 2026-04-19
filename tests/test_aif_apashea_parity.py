"""Acceptance test for the standalone ``aif.Agent`` notebook setup."""

from __future__ import annotations

import numpy as np
import pytest


pytest.importorskip("pymdp.pymdp_external_custom", reason="requires Andrew Pescia's notebook pymdp fork")
pymdp = pytest.importorskip("pymdp")


def _norm_dist(arr: np.ndarray) -> np.ndarray:
    totals = arr.sum(axis=0, keepdims=True)
    return arr / np.where(totals == 0.0, 1.0, totals)


def _build_apashea_setup():
    num_obs = [2, 4]
    num_states = [4, 3, 2]
    num_controls = [1, 2, 2]
    payoff_numeric_values = [-1, 1, 3, 5]

    A = np.empty(len(num_obs), dtype=object)
    cooperation_probs = np.array(
        [
            [0.95, 0.80, 0.55],
            [0.90, 0.70, 0.30],
            [0.70, 0.35, 0.10],
            [0.60, 0.50, 0.35],
        ],
        dtype=float,
    )
    A[0] = np.zeros((num_obs[0], num_states[0], num_states[1], num_states[2]), dtype=float)
    for state_type in range(num_states[0]):
        for stance in range(num_states[1]):
            for own_action in range(num_states[2]):
                coop_prob = cooperation_probs[state_type, stance]
                A[0][0, state_type, stance, own_action] = coop_prob
                A[0][1, state_type, stance, own_action] = 1.0 - coop_prob
    A[0] = _norm_dist(A[0])

    payoff_table = {
        (0, 0): 3,
        (0, 1): -1,
        (1, 0): 5,
        (1, 1): 1,
    }
    A[1] = np.zeros((num_obs[1], num_states[0], num_states[1], num_states[2]), dtype=float)
    for state_type in range(num_states[0]):
        for stance in range(num_states[1]):
            for own_action in range(num_states[2]):
                coop_prob = cooperation_probs[state_type, stance]
                for payoff_idx, payoff_value in enumerate(payoff_numeric_values):
                    prob = 0.0
                    for partner_action in range(2):
                        partner_prob = coop_prob if partner_action == 0 else (1.0 - coop_prob)
                        if payoff_table[(own_action, partner_action)] == payoff_value:
                            prob += partner_prob
                    A[1][payoff_idx, state_type, stance, own_action] = prob
    A[1] = _norm_dist(A[1])

    B = np.empty(len(num_states), dtype=object)
    B[0] = np.zeros((num_states[0], num_states[0], num_controls[0]), dtype=float)
    for next_type in range(num_states[0]):
        for prev_type in range(num_states[0]):
            B[0][next_type, prev_type, 0] = 0.95 if next_type == prev_type else 0.017
    B[0] = _norm_dist(B[0])

    B[1] = np.zeros((num_states[1], num_states[1], num_controls[1]), dtype=float)
    B[1][:, :, 0] = np.array(
        [
            [0.90, 0.10, 0.00],
            [0.30, 0.60, 0.10],
            [0.05, 0.35, 0.60],
        ],
        dtype=float,
    )
    B[1][:, :, 1] = np.array(
        [
            [0.10, 0.50, 0.40],
            [0.05, 0.35, 0.60],
            [0.02, 0.18, 0.80],
        ],
        dtype=float,
    )
    B[1] = _norm_dist(B[1])

    B[2] = np.zeros((num_states[2], num_states[2], num_controls[2]), dtype=float)
    for action in range(num_controls[2]):
        B[2][action, :, action] = 1.0
    B[2] = _norm_dist(B[2])

    C = np.empty(len(num_obs), dtype=object)
    C[0] = np.array([0.0, 0.0], dtype=float)
    payoff_preferences = np.exp(np.array(payoff_numeric_values, dtype=float))
    C[1] = payoff_preferences / payoff_preferences.sum()

    D = np.empty(len(num_states), dtype=object)
    D[0] = np.array([0.25, 0.25, 0.25, 0.25], dtype=float)
    D[1] = np.array([0.2, 0.6, 0.2], dtype=float)
    D[2] = np.array([0.5, 0.5], dtype=float)

    policies = [
        np.array([[0, 0, 0]], dtype=int),
        np.array([[0, 0, 1]], dtype=int),
        np.array([[0, 1, 0]], dtype=int),
        np.array([[0, 1, 1]], dtype=int),
    ]
    return A, B, C, D, policies


def test_aif_matches_pymdp_first_5_steps():
    import aif
    from pymdp.agent import Agent as PymdpAgent

    A, B, C, D, policies = _build_apashea_setup()
    obs_sequence = [[0, 1]] * 5

    pymdp_agent = PymdpAgent(
        A=A,
        B=B,
        C=C,
        D=D,
        policies=policies,
        inference_algo="VANILLA",
        inference_horizon=1,
        control_fac_idx=[1, 2],
    )
    aif_agent = aif.Agent(
        A=np.asarray(A, dtype=object),
        B=np.asarray(B, dtype=object),
        C=np.asarray(C, dtype=object),
        D=np.asarray(D, dtype=object),
        policies=np.asarray(policies, dtype=int),
    )
    aif_agent.reset()

    for timestep, obs in enumerate(obs_sequence):
        pymdp_agent.infer_states(obs)
        aif.infer_states(aif_agent, obs)
        for factor in range(len(D)):
            np.testing.assert_allclose(
                np.asarray(aif_agent.qs[factor], dtype=float),
                np.asarray(pymdp_agent.qs[factor], dtype=float),
                atol=1e-3,
                err_msg=f"mismatch at step {timestep}, factor {factor}",
            )
