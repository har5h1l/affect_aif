import jax.numpy as jnp
import numpy as np

from affect_aif.core.control import (
    compute_efe_with_terminal_value,
    compute_expected_free_energy,
    _rollout_policy_trust_game_mean_field,
    _rollout_policy_trust_game_sophisticated,
    construct_policies,
    generate_observation_sequences,
)
from affect_aif.core.maths import entropy, normalize, softmax


def test_softmax_sums_to_one():
    values = softmax(np.array([1.0, 2.0, 3.0]), backend="numpy")
    assert np.isclose(values.sum(), 1.0)


def test_softmax_temperature():
    cold = softmax(np.array([0.0, 1.0]), tau=0.1, backend="numpy")
    hot = softmax(np.array([0.0, 1.0]), tau=2.0, backend="numpy")
    assert cold[1] > hot[1]


def test_entropy_uniform_is_log_n():
    value = entropy(np.array([0.25, 0.25, 0.25, 0.25]), backend="numpy")
    assert np.isclose(value, np.log(4.0))


def test_normalize():
    values = normalize(np.array([2.0, 3.0]), axis=0, backend="numpy")
    assert np.allclose(values, np.array([0.4, 0.6]))


def test_construct_policies_binary_horizon_two():
    policies = construct_policies([2], planning_horizon=2)
    assert policies.shape == (4, 2)
    assert {tuple(row) for row in policies.tolist()} == {(0, 0), (0, 1), (1, 0), (1, 1)}


def test_generate_observation_sequences_binary_horizon_three():
    sequences = generate_observation_sequences(3)
    assert sequences.shape == (4, 2)
    assert {tuple(row) for row in sequences.tolist()} == {(0, 0), (0, 1), (1, 0), (1, 1)}


def _toy_efe_inputs():
    A = np.empty(2, dtype=object)
    A[0] = np.eye(2, dtype=float)
    A[1] = np.eye(2, dtype=float)

    B = np.empty(1, dtype=object)
    B[0] = np.zeros((2, 2, 1), dtype=float)
    B[0][:, :, 0] = np.eye(2, dtype=float)

    qs = np.array([np.array([1.0, 0.0], dtype=float)], dtype=object)
    policy = np.array([0], dtype=np.int32)
    policies = np.array([[0], [0]], dtype=np.int32)
    terminal_values = np.array([0.25, -0.5], dtype=float)
    return A, B, qs, policy, policies, terminal_values


def _rollout_inputs():
    beliefs = jnp.asarray([[[0.25, 0.25], [0.25, 0.25]]], dtype=jnp.float32)
    one_hot_beliefs = jnp.asarray([[[1.0, 0.0], [0.0, 0.0]]], dtype=jnp.float32)
    common = dict(
        active_partner=jnp.int32(0),
        assignment_mode_code=jnp.int32(0),
        B_type=jnp.asarray(np.eye(2), dtype=jnp.float32),
        B_stance_by_action=jnp.asarray(
            [
                np.eye(2, dtype=float),
                np.eye(2, dtype=float),
            ],
            dtype=jnp.float32,
        ),
        partner_action_prob_table=jnp.asarray(
            [
                [0.999, 0.999],
                [0.001, 0.001],
            ],
            dtype=jnp.float32,
        ),
        payoff_index_table=jnp.asarray([[0, 1], [1, 0]], dtype=jnp.int32),
        agent_payoff_table=jnp.zeros((2, 2), dtype=jnp.float32),
        payoff_preferences=jnp.asarray([0.0, 0.0], dtype=jnp.float32),
        partner_action_preferences=jnp.asarray([0.0, 0.0], dtype=jnp.float32),
        terminal_signal=jnp.zeros((1,), dtype=jnp.float32),
        mu=jnp.float32(0.0),
        max_abs_payoff=jnp.float32(1.0),
    )
    return {
        "policy": jnp.asarray([0, 0, 0], dtype=jnp.int32),
        "observation_sequences": jnp.asarray(generate_observation_sequences(3), dtype=jnp.int32),
        "beliefs": beliefs,
        "one_hot_beliefs": one_hot_beliefs,
        "common": common,
    }


def test_expected_free_energy_is_negative_for_preferred_outcome():
    A, B, qs, policy, _, _ = _toy_efe_inputs()
    C = np.empty(2, dtype=object)
    C[0] = np.zeros(2, dtype=float)
    C[1] = np.array([1.0, 0.0], dtype=float)

    efe = compute_expected_free_energy(A, B, C, qs, policy, use_utility=True, use_information_gain=False)

    assert efe < 0.0


def test_expected_free_energy_is_positive_for_dispreferred_outcome():
    A, B, qs, policy, _, _ = _toy_efe_inputs()
    C = np.empty(2, dtype=object)
    C[0] = np.zeros(2, dtype=float)
    C[1] = np.array([-1.0, 0.0], dtype=float)

    efe = compute_expected_free_energy(A, B, C, qs, policy, use_utility=True, use_information_gain=False)

    assert efe > 0.0


def test_expected_free_energy_with_terminal_value_is_additive():
    A, B, qs, _, policies, terminal_values = _toy_efe_inputs()
    C = np.empty(2, dtype=object)
    C[0] = np.zeros(2, dtype=float)
    C[1] = np.array([1.0, 0.0], dtype=float)

    base = np.array(
        [
            compute_expected_free_energy(A, B, C, qs, policy, use_utility=True, use_information_gain=False)
            for policy in policies
        ],
        dtype=float,
    )
    adjusted = compute_efe_with_terminal_value(
        A,
        B,
        C,
        qs,
        policies,
        terminal_values,
        planning_horizon=1,
        use_utility=True,
        use_information_gain=False,
    )

    assert np.allclose(adjusted, base + terminal_values)


def test_rollout_epistemic_value_is_positive_for_uncertain_beliefs():
    inputs = _rollout_inputs()
    sophisticated = _rollout_policy_trust_game_sophisticated(
        inputs["policy"],
        inputs["observation_sequences"],
        inputs["beliefs"],
        use_utility_flag=jnp.float32(0.0),
        use_information_gain_flag=jnp.float32(1.0),
        **inputs["common"],
    )

    assert float(sophisticated[0]) < 0.0
    assert -float(sophisticated[0]) > 0.0


def test_rollout_epistemic_value_approaches_zero_for_sharp_beliefs():
    inputs = _rollout_inputs()
    sophisticated = _rollout_policy_trust_game_sophisticated(
        inputs["policy"],
        inputs["observation_sequences"],
        inputs["one_hot_beliefs"],
        use_utility_flag=jnp.float32(0.0),
        use_information_gain_flag=jnp.float32(1.0),
        **inputs["common"],
    )

    assert abs(float(sophisticated[0])) < 1e-6


def test_rollout_terminal_value_adjustment_works_correctly():
    inputs = _rollout_inputs()
    weighted_common = {
        **inputs["common"],
        "terminal_signal": jnp.asarray([0.25], dtype=jnp.float32),
        "mu": jnp.float32(2.0),
    }
    base_total, base_step_costs, _, _ = _rollout_policy_trust_game_mean_field(
        inputs["policy"],
        inputs["beliefs"],
        use_utility_flag=jnp.float32(0.0),
        use_information_gain_flag=jnp.float32(1.0),
        **inputs["common"],
    )
    weighted_total, _, terminal_value, _ = _rollout_policy_trust_game_mean_field(
        inputs["policy"],
        inputs["beliefs"],
        use_utility_flag=jnp.float32(0.0),
        use_information_gain_flag=jnp.float32(1.0),
        **weighted_common,
    )

    expected_step_sum = float(jnp.sum(base_step_costs))
    expected_weight = 1.0 + float(jnp.float32(2.0) * jnp.float32(0.25))
    assert np.isclose(float(base_total), expected_step_sum, atol=1e-6)
    assert np.isclose(float(weighted_total), expected_step_sum * expected_weight, atol=1e-6)
    assert np.isclose(float(terminal_value), expected_step_sum * (expected_weight - 1.0), atol=1e-6)


def test_sophisticated_and_mean_field_rollouts_agree_for_sharp_beliefs():
    inputs = _rollout_inputs()
    mean_field = _rollout_policy_trust_game_mean_field(
        inputs["policy"],
        inputs["one_hot_beliefs"],
        use_utility_flag=jnp.float32(0.0),
        use_information_gain_flag=jnp.float32(1.0),
        **inputs["common"],
    )
    sophisticated = _rollout_policy_trust_game_sophisticated(
        inputs["policy"],
        inputs["observation_sequences"],
        inputs["one_hot_beliefs"],
        use_utility_flag=jnp.float32(0.0),
        use_information_gain_flag=jnp.float32(1.0),
        **inputs["common"],
    )

    assert np.isclose(float(mean_field[0]), float(sophisticated[0]), atol=1e-6)


def test_graded_construct_policies():
    policies = construct_policies([24], planning_horizon=2)
    assert policies.shape == (576, 2)  # 24^2 = 576


def test_graded_construct_policies_with_sampling():
    policies = construct_policies([24], planning_horizon=2, max_policies=100, rng=np.random.default_rng(0))
    assert policies.shape == (100, 2)
    assert policies.max() < 24
