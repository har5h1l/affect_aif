from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents, create_pymdp_agent
from tasks.trust.pomdp_matrices import (
    build_initial_beliefs,
    build_policies,
    build_preference_vectors,
    build_task_likelihoods,
    build_transition_matrices,
)


def test_template_exports_jax_arrays_and_expected_shapes() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=4),
        planning_horizon=2,
    )

    assert len(template.A) == 2
    assert len(template.B) == 3
    assert template.A[0].shape == (2, 4, 3, 2)
    assert template.A[1].shape == (4, 4, 3, 2)
    assert template.B[0].shape == (4, 4, 1)
    assert template.B[1].shape == (3, 3, 2)
    assert template.B[2].shape == (2, 2, 2)
    assert template.control_fac_idx == (1, 2)
    assert all(isinstance(array, jnp.ndarray) for array in template.A)
    assert all(isinstance(array, jnp.ndarray) for array in template.B)
    assert all(isinstance(array, jnp.ndarray) for array in template.C)
    assert all(isinstance(array, jnp.ndarray) for array in template.D)
    assert isinstance(template.E, jnp.ndarray)
    assert isinstance(template.policies, jnp.ndarray)


def test_template_preserves_probability_normalization() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=4),
        planning_horizon=2,
    )

    for A_m in template.A:
        np.testing.assert_allclose(np.asarray(A_m).sum(axis=0), 1.0)
    for B_f in template.B:
        np.testing.assert_allclose(np.asarray(B_f).sum(axis=0), 1.0)
    np.testing.assert_allclose(np.asarray(template.E).sum(), 1.0)


def test_template_can_create_official_pymdp_agents() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=3),
        planning_horizon=1,
    )

    agent = create_pymdp_agent(template, gamma=1.0)
    partner_agents = create_partner_agents(template, num_partners=3, gamma=1.0)

    assert agent.__class__.__module__.startswith("pymdp.")
    assert len(partner_agents) == 3
    assert all(partner.__class__.__module__.startswith("pymdp.") for partner in partner_agents)


def test_pomdp_matrix_helpers_match_template_contract() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="graded", num_partners=4, assignment_mode="agent_choice"),
        planning_horizon=2,
        max_policies=128,
    )

    task_A = build_task_likelihoods(
        num_types=template.num_types,
        num_stances=template.num_stances,
        num_social_actions=template.num_social_actions,
        payoff_values=template.payoff_values,
        partner_action_prob_table=template.partner_action_prob_table,
        payoff_index_table=template.payoff_index_table,
        observation_noise=template.observation_noise,
    )
    B = build_transition_matrices(
        num_types=template.num_types,
        num_stances=template.num_stances,
        num_social_actions=template.num_social_actions,
        num_controls=template.num_controls,
        p_switch=template.p_switch,
    )
    C = build_preference_vectors(
        payoff_values=template.payoff_values,
        preference_temperature=template.preference_temperature,
    )
    D = build_initial_beliefs(
        num_types=template.num_types,
        num_stances=template.num_stances,
        num_social_actions=template.num_social_actions,
    )
    policies = build_policies(
        template.num_controls,
        planning_horizon=2,
        max_policies=128,
        rng=None,
    )

    np.testing.assert_allclose(task_A[0], np.asarray(template.A[0])[..., 0])
    np.testing.assert_allclose(np.transpose(task_A[1], (0, 2, 3, 1)), np.asarray(template.A[1]))
    for actual, expected in zip(B, template.B, strict=True):
        np.testing.assert_allclose(actual, np.asarray(expected))
    for actual, expected in zip(C, template.C, strict=True):
        np.testing.assert_allclose(actual, np.asarray(expected))
    for actual, expected in zip(D, template.D, strict=True):
        np.testing.assert_allclose(actual, np.asarray(expected))
    np.testing.assert_array_equal(policies, np.asarray(template.policies))
