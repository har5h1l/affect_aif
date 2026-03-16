import numpy as np
import jax.numpy as jnp

from affect_aif.core.control import (
    _rollout_policy_trust_game_mean_field,
    _rollout_policy_trust_game_sophisticated,
    construct_policies,
    generate_observation_sequences,
)
from affect_aif.core.maths import entropy, normalize, softmax
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.generative_model.model import TrustGameModel


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


def _rollout_inputs():
    cfg = ExperimentConfig(num_rounds=2, num_replications=1, calibration_episodes=1, random_seed=0)
    model = TrustGameModel(cfg)
    A, B, C, D = model.get_matrices()
    beliefs = jnp.tile(jnp.asarray(D[0], dtype=jnp.float32)[None, :], (cfg.num_partners, 1))
    sharp_beliefs = beliefs.at[0].set(jnp.asarray([0.999, 0.0005, 0.00025, 0.00025], dtype=jnp.float32))
    common = dict(
        active_partner=jnp.int32(0),
        assignment_mode_code=jnp.int32(0),
        B_type=jnp.asarray(B[0][:, :, 0], dtype=jnp.float32),
        partner_action_prob_table=jnp.asarray(A[0][0], dtype=jnp.float32),
        payoff_index_table=jnp.asarray(model.payoff_index_table, dtype=jnp.int32),
        agent_payoff_table=jnp.asarray(model.agent_payoff_table, dtype=jnp.float32),
        payoff_preferences=jnp.asarray(C[1], dtype=jnp.float32),
        partner_action_preferences=jnp.asarray(C[0], dtype=jnp.float32),
        terminal_signal=jnp.zeros((cfg.num_partners,), dtype=jnp.float32),
        switch_round=jnp.int32(model.switch_round),
        mu=jnp.float32(0.0),
        max_abs_payoff=jnp.float32(max(abs(level) for level in model.payoff_levels)),
        use_utility_flag=jnp.float32(1.0),
        use_information_gain_flag=jnp.float32(1.0),
    )
    return {
        "policy": jnp.asarray([0, 0, 0], dtype=jnp.int32),
        "observation_sequences": jnp.asarray(generate_observation_sequences(3), dtype=jnp.int32),
        "beliefs": beliefs,
        "sharp_beliefs": sharp_beliefs,
        "last_actions": jnp.zeros((cfg.num_partners,), dtype=jnp.int32),
        "counts": jnp.zeros((cfg.num_partners,), dtype=jnp.int32),
        "common": common,
    }


def test_sophisticated_rollout_differs_from_mean_field_for_uniform_belief():
    inputs = _rollout_inputs()
    mean_field = _rollout_policy_trust_game_mean_field(
        inputs["policy"],
        inputs["beliefs"],
        inputs["last_actions"],
        inputs["counts"],
        **inputs["common"],
    )
    sophisticated = _rollout_policy_trust_game_sophisticated(
        inputs["policy"],
        inputs["observation_sequences"],
        inputs["beliefs"],
        inputs["last_actions"],
        inputs["counts"],
        **inputs["common"],
    )
    assert not np.isclose(float(mean_field[0]), float(sophisticated[0]))


def test_rollout_gap_shrinks_when_belief_is_sharp():
    inputs = _rollout_inputs()
    mean_uniform = _rollout_policy_trust_game_mean_field(
        inputs["policy"],
        inputs["beliefs"],
        inputs["last_actions"],
        inputs["counts"],
        **inputs["common"],
    )
    sophisticated_uniform = _rollout_policy_trust_game_sophisticated(
        inputs["policy"],
        inputs["observation_sequences"],
        inputs["beliefs"],
        inputs["last_actions"],
        inputs["counts"],
        **inputs["common"],
    )
    mean_sharp = _rollout_policy_trust_game_mean_field(
        inputs["policy"],
        inputs["sharp_beliefs"],
        inputs["last_actions"],
        inputs["counts"],
        **inputs["common"],
    )
    sophisticated_sharp = _rollout_policy_trust_game_sophisticated(
        inputs["policy"],
        inputs["observation_sequences"],
        inputs["sharp_beliefs"],
        inputs["last_actions"],
        inputs["counts"],
        **inputs["common"],
    )
    uniform_gap = abs(float(sophisticated_uniform[0]) - float(mean_uniform[0]))
    sharp_gap = abs(float(sophisticated_sharp[0]) - float(mean_sharp[0]))
    assert sharp_gap < uniform_gap
