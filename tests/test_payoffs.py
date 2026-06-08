"""Unit tests for trust payoff and action-encoding helpers."""

from __future__ import annotations

import numpy as np
import pytest

from tasks.trust.payoffs import (
    build_payoff_matrix,
    decode_action,
    decode_env_agent_action,
    decode_instantaneous_index,
    encode_action,
    encode_env_action_factorized,
    encode_instantaneous_index,
    expected_agent_payoff,
    factorized_num_controls,
    infer_payoff_levels,
    num_actions,
    payoff_distribution,
    payoff_to_index,
)


def test_build_payoff_matrix_maps_pd_game_cells():
    matrix = build_payoff_matrix()

    assert matrix[0, 0, 0] == 3.0
    assert matrix[0, 1, 0] == -1.0
    assert matrix[1, 0, 0] == 5.0
    assert matrix[1, 1, 0] == 1.0


def test_infer_payoff_levels_extracts_sorted_unique_agent_payoffs():
    matrix = build_payoff_matrix()

    assert infer_payoff_levels(matrix) == (-1.0, 1.0, 3.0, 5.0)


def test_payoff_to_index_raises_for_unknown_level():
    with pytest.raises(KeyError, match="Payoff 9.0"):
        payoff_to_index(9.0)


def test_payoff_distribution_sums_to_one():
    matrix = build_payoff_matrix()
    levels = infer_payoff_levels(matrix)
    dist = payoff_distribution(
        agent_action=0,
        partner_action_probs=np.asarray([0.7, 0.3], dtype=float),
        payoff_matrix=matrix,
        payoff_levels=levels,
    )

    np.testing.assert_allclose(dist.sum(), 1.0)
    assert dist[payoff_to_index(3.0, levels)] == pytest.approx(0.7)
    assert dist[payoff_to_index(-1.0, levels)] == pytest.approx(0.3)


def test_expected_agent_payoff_is_probability_weighted():
    matrix = build_payoff_matrix()
    probs = np.asarray([0.25, 0.75], dtype=float)

    assert expected_agent_payoff(agent_action=0, partner_action_probs=probs, payoff_matrix=matrix) == pytest.approx(
        0.25 * 3.0 + 0.75 * (-1.0)
    )


def test_num_actions_depends_on_assignment_mode():
    assert num_actions(num_partners=4, assignment_mode="random") == 2
    assert num_actions(num_partners=4, assignment_mode="agent_choice", num_social_actions=6) == 24


def test_random_assignment_decode_requires_active_partner():
    with pytest.raises(ValueError, match="active_partner"):
        decode_action(0, num_partners=4, assignment_mode="random")


def test_agent_choice_encode_decode_roundtrip():
    encoded = encode_action(2, 1, num_partners=4, assignment_mode="agent_choice")
    partner_idx, social_action = decode_action(encoded, num_partners=4, assignment_mode="agent_choice")

    assert partner_idx == 2
    assert social_action == 1


def test_factorized_num_controls_matches_assignment_mode():
    assert factorized_num_controls(4, "agent_choice", 2) == [4, 2, 2]
    assert factorized_num_controls(4, "random", 2) == [1, 2, 2]


def test_instantaneous_index_roundtrip():
    num_controls = [4, 2, 2]
    controls = (2, 1, 0)

    flat = encode_instantaneous_index(controls, num_controls)
    assert decode_instantaneous_index(flat, num_controls) == controls


def test_encode_env_action_factorized_agent_choice_binary():
    num_controls = factorized_num_controls(4, "agent_choice", 2)
    encoded = encode_env_action_factorized(
        partner_idx=2,
        stance_action=1,
        own_action=0,
        assignment_mode="agent_choice",
        num_partners=4,
        num_controls=num_controls,
    )

    partner_idx, own_action = decode_env_agent_action(
        encoded,
        num_partners=4,
        assignment_mode="agent_choice",
        active_partner=None,
        num_social_actions=2,
        factorized=True,
    )

    assert partner_idx == 2
    assert own_action == 0
