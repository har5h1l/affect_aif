"""JAX rollout helpers for trust-game planning."""

from __future__ import annotations

from functools import partial

import jax
import jax.numpy as jnp
import numpy as np


def _decode_action_jax(action, active_partner, assignment_mode_code, num_social_actions=2):
    partner_idx = jnp.where(assignment_mode_code == 1, action // num_social_actions, active_partner)
    social_action = jnp.where(assignment_mode_code == 1, action % num_social_actions, action)
    return partner_idx.astype(jnp.int32), social_action.astype(jnp.int32)


def _to_binary_action_jax(social_action, num_social_actions):
    """Map graded investment level to binary cooperate/defect for partner prediction."""

    return jnp.where(num_social_actions <= 2, social_action, jnp.where(social_action > 0, 0, 1))


def _contextual_partner_prediction(
    belief,
    last_action,
    interaction_count,
    partner_action_prob_table,
    switch_round,
):
    phase = jnp.where(interaction_count >= switch_round, 1, 0).astype(jnp.int32)
    p_coop_by_type = partner_action_prob_table[:, last_action, phase]
    p_coop = jnp.dot(belief, p_coop_by_type)
    action_probs = jnp.asarray([p_coop, 1.0 - p_coop], dtype=jnp.float32)
    ambiguity_per_type = -(
        p_coop_by_type * jnp.log(p_coop_by_type + 1e-16)
        + (1.0 - p_coop_by_type) * jnp.log(1.0 - p_coop_by_type + 1e-16)
    )
    expected_ambiguity = jnp.dot(belief, ambiguity_per_type)
    return action_probs, expected_ambiguity


def _payoff_distribution_jax(social_action, partner_action_probs, payoff_index_table, num_payoffs):
    coop_idx = payoff_index_table[social_action, 0]
    defect_idx = payoff_index_table[social_action, 1]
    dist = jnp.zeros((num_payoffs,), dtype=jnp.float32)
    dist = dist.at[coop_idx].add(partner_action_probs[0])
    dist = dist.at[defect_idx].add(partner_action_probs[1])
    return dist


def generate_observation_sequences(planning_horizon: int) -> np.ndarray:
    """Enumerate all binary observation sequences needed for sophisticated rollout."""

    if planning_horizon <= 1:
        return np.zeros((1, 0), dtype=int)

    obs_steps = planning_horizon - 1
    total = 2**obs_steps
    encoded = np.arange(total, dtype=np.int32)[:, None]
    shifts = np.arange(obs_steps - 1, -1, -1, dtype=np.int32)[None, :]
    return ((encoded >> shifts) & 1).astype(int)


def _normalize_jax(values):
    total = jnp.sum(values)
    return values / (total + 1e-16)


def _entropy_jax(probs):
    return -jnp.sum(probs * jnp.log(probs + 1e-16))


def _predictive_belief_update(
    belief,
    observed_action,
    last_action,
    interaction_count,
    B_type,
    partner_action_prob_table,
    switch_round,
):
    phase = jnp.where(interaction_count >= switch_round, 1, 0).astype(jnp.int32)
    p_coop_by_type = partner_action_prob_table[:, last_action, phase]
    likelihood = jnp.where(observed_action == 0, p_coop_by_type, 1.0 - p_coop_by_type)
    posterior = _normalize_jax(likelihood * belief)
    predictive_next = _normalize_jax(B_type @ posterior)
    return posterior, predictive_next


def _rollout_policy_trust_game_mean_field(
    policy,
    beliefs,
    last_actions,
    counts,
    active_partner,
    assignment_mode_code,
    B_type,
    partner_action_prob_table,
    payoff_index_table,
    agent_payoff_table,
    payoff_preferences,
    partner_action_preferences,
    terminal_signal,
    switch_round,
    mu,
    max_abs_payoff,
    use_utility_flag,
    use_information_gain_flag,
    num_social_actions=2,
):
    horizon = policy.shape[0]

    def scan_step(carry, raw_action):
        beliefs_t, last_actions_t, counts_t, t = carry
        partner_idx, social_action = _decode_action_jax(
            raw_action, active_partner, assignment_mode_code, num_social_actions
        )
        belief = beliefs_t[partner_idx]
        last_action = last_actions_t[partner_idx]
        count = counts_t[partner_idx]
        partner_action_probs, expected_ambiguity = _contextual_partner_prediction(
            belief=belief,
            last_action=last_action,
            interaction_count=count,
            partner_action_prob_table=partner_action_prob_table,
            switch_round=switch_round,
        )
        payoff_dist = _payoff_distribution_jax(
            social_action=social_action,
            partner_action_probs=partner_action_probs,
            payoff_index_table=payoff_index_table,
            num_payoffs=payoff_preferences.shape[0],
        )
        pragmatic = -jnp.sum(partner_action_probs * partner_action_preferences) - jnp.sum(
            payoff_dist * payoff_preferences
        )
        has_observation = t < (horizon - 1)
        epistemic = jnp.where(
            has_observation,
            expected_ambiguity - _entropy_jax(partner_action_probs),
            0.0,
        )
        step_cost = use_utility_flag * pragmatic + use_information_gain_flag * epistemic

        beliefs_tp1 = beliefs_t.at[partner_idx].set(B_type @ belief)
        binary_action = _to_binary_action_jax(social_action, num_social_actions)
        last_actions_tp1 = last_actions_t.at[partner_idx].set(binary_action)
        counts_tp1 = counts_t.at[partner_idx].set(count + 1)
        aux = (step_cost, partner_idx, social_action)
        return (beliefs_tp1, last_actions_tp1, counts_tp1, t + 1), aux

    (beliefs_f, last_actions_f, counts_f, _), (step_costs, partner_indices, social_actions) = jax.lax.scan(
        scan_step,
        (beliefs, last_actions, counts, jnp.int32(0)),
        policy,
    )

    first_partner, _ = _decode_action_jax(policy[0], active_partner, assignment_mode_code, num_social_actions)
    total_step_cost = jnp.sum(step_costs)
    precision_weight = 1.0 + mu * terminal_signal[first_partner]
    total = total_step_cost * precision_weight
    terminal_value = total - total_step_cost
    del beliefs_f, last_actions_f, counts_f, agent_payoff_table, max_abs_payoff, partner_indices, social_actions
    return total, step_costs, terminal_value, first_partner


def _eval_single_path(
    policy,
    obs_sequence,
    beliefs,
    last_actions,
    counts,
    active_partner,
    assignment_mode_code,
    B_type,
    partner_action_prob_table,
    payoff_index_table,
    agent_payoff_table,
    payoff_preferences,
    partner_action_preferences,
    terminal_signal,
    switch_round,
    mu,
    max_abs_payoff,
    use_utility_flag,
    use_information_gain_flag,
    num_social_actions=2,
):
    del agent_payoff_table, max_abs_payoff

    horizon = policy.shape[0]

    def scan_step(carry, step_inputs):
        beliefs_t, last_actions_t, counts_t, path_log_prob = carry
        t, raw_action = step_inputs
        partner_idx, social_action = _decode_action_jax(
            raw_action, active_partner, assignment_mode_code, num_social_actions
        )
        belief = beliefs_t[partner_idx]
        last_action = last_actions_t[partner_idx]
        count = counts_t[partner_idx]
        partner_action_probs, expected_ambiguity = _contextual_partner_prediction(
            belief=belief,
            last_action=last_action,
            interaction_count=count,
            partner_action_prob_table=partner_action_prob_table,
            switch_round=switch_round,
        )
        payoff_dist = _payoff_distribution_jax(
            social_action=social_action,
            partner_action_probs=partner_action_probs,
            payoff_index_table=payoff_index_table,
            num_payoffs=payoff_preferences.shape[0],
        )
        pragmatic = -jnp.sum(partner_action_probs * partner_action_preferences) - jnp.sum(
            payoff_dist * payoff_preferences
        )

        has_observation = t < (horizon - 1)
        observed_action = jnp.where(has_observation, obs_sequence[t], 0).astype(jnp.int32)
        obs_prob = jnp.where(has_observation, partner_action_probs[observed_action], 1.0)
        posterior, predictive_next = _predictive_belief_update(
            belief=belief,
            observed_action=observed_action,
            last_action=last_action,
            interaction_count=count,
            B_type=B_type,
            partner_action_prob_table=partner_action_prob_table,
            switch_round=switch_round,
        )
        prior_entropy = _entropy_jax(belief)
        posterior_entropy = _entropy_jax(posterior)
        epistemic = jnp.where(has_observation, posterior_entropy - prior_entropy, 0.0)
        step_cost = use_utility_flag * pragmatic + use_information_gain_flag * epistemic
        next_belief = jnp.where(has_observation, predictive_next, _normalize_jax(B_type @ belief))

        beliefs_tp1 = beliefs_t.at[partner_idx].set(next_belief)
        binary_action = _to_binary_action_jax(social_action, num_social_actions)
        last_actions_tp1 = last_actions_t.at[partner_idx].set(binary_action)
        counts_tp1 = counts_t.at[partner_idx].set(count + 1)
        path_log_prob_tp1 = path_log_prob + jnp.where(has_observation, jnp.log(obs_prob + 1e-16), 0.0)
        return (beliefs_tp1, last_actions_tp1, counts_tp1, path_log_prob_tp1), step_cost

    init = (beliefs, last_actions, counts, jnp.float32(0.0))
    (_, _, _, path_log_prob), step_costs = jax.lax.scan(
        scan_step,
        init,
        (jnp.arange(horizon, dtype=jnp.int32), policy),
    )
    first_partner, _ = _decode_action_jax(policy[0], active_partner, assignment_mode_code, num_social_actions)
    total_step_cost = jnp.sum(step_costs)
    precision_weight = 1.0 + mu * terminal_signal[first_partner]
    total = total_step_cost * precision_weight
    path_weight = jnp.exp(path_log_prob)
    return total * path_weight, step_costs * path_weight, (total - total_step_cost) * path_weight, first_partner


def _rollout_policy_trust_game_sophisticated(
    policy,
    observation_sequences,
    beliefs,
    last_actions,
    counts,
    active_partner,
    assignment_mode_code,
    B_type,
    partner_action_prob_table,
    payoff_index_table,
    agent_payoff_table,
    payoff_preferences,
    partner_action_preferences,
    terminal_signal,
    switch_round,
    mu,
    max_abs_payoff,
    use_utility_flag,
    use_information_gain_flag,
    num_social_actions=2,
):
    path_rollout = jax.vmap(
        _eval_single_path,
        in_axes=(
            None,
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
    )
    weighted_totals, weighted_step_costs, weighted_terminal_values, first_partners = path_rollout(
        policy,
        observation_sequences,
        beliefs,
        last_actions,
        counts,
        active_partner,
        assignment_mode_code,
        B_type,
        partner_action_prob_table,
        payoff_index_table,
        agent_payoff_table,
        payoff_preferences,
        partner_action_preferences,
        terminal_signal,
        switch_round,
        mu,
        max_abs_payoff,
        use_utility_flag,
        use_information_gain_flag,
        num_social_actions,
    )
    return (
        jnp.sum(weighted_totals, axis=0),
        jnp.sum(weighted_step_costs, axis=0),
        jnp.sum(weighted_terminal_values, axis=0),
        first_partners[0],
    )


@partial(jax.jit, static_argnames=("num_actions", "num_social_actions"))
def decision_step_trust_game(
    beliefs,
    last_actions,
    counts,
    active_partner,
    policies,
    observation_sequences,
    key,
    B_type,
    partner_action_prob_table,
    payoff_index_table,
    agent_payoff_table,
    payoff_preferences,
    partner_action_preferences,
    terminal_signal,
    precision_signal,
    assignment_mode_code,
    switch_round,
    gamma,
    mu,
    num_actions,
    sampling_mode_code,
    use_utility_flag,
    use_information_gain_flag,
    modulate_precision_flag,
    max_abs_payoff,
    num_social_actions=2,
):
    rollout = jax.vmap(
        _rollout_policy_trust_game_sophisticated,
        in_axes=(
            0,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
    )
    G, step_costs, terminal_values, first_partners = rollout(
        policies,
        observation_sequences,
        beliefs,
        last_actions,
        counts,
        active_partner,
        assignment_mode_code,
        B_type,
        partner_action_prob_table,
        payoff_index_table,
        agent_payoff_table,
        payoff_preferences,
        partner_action_preferences,
        terminal_signal,
        switch_round,
        mu,
        max_abs_payoff,
        use_utility_flag,
        use_information_gain_flag,
        num_social_actions,
    )
    precision_scale = jnp.where(modulate_precision_flag > 0, 1.0 + precision_signal[first_partners], 1.0)
    logits = -gamma * precision_scale * G
    q_pi = jax.nn.softmax(logits)

    def sample_marginal(args):
        q_pi_t, key_t = args
        action_probs = jnp.sum(jax.nn.one_hot(policies[:, 0], num_actions) * q_pi_t[:, None], axis=0)
        key_t, subkey = jax.random.split(key_t)
        action = jax.random.categorical(subkey, jnp.log(action_probs + 1e-16))
        return action.astype(jnp.int32), key_t

    def sample_full(args):
        q_pi_t, key_t = args
        key_t, subkey = jax.random.split(key_t)
        policy_idx = jax.random.categorical(subkey, jnp.log(q_pi_t + 1e-16))
        action = policies[policy_idx, 0]
        return action.astype(jnp.int32), key_t

    action, key = jax.lax.cond(
        sampling_mode_code == 0,
        sample_marginal,
        sample_full,
        (q_pi, key),
    )
    selected_partner, selected_social_action = _decode_action_jax(
        action, active_partner, assignment_mode_code, num_social_actions
    )
    predicted_partner_action_probs, _ = _contextual_partner_prediction(
        belief=beliefs[selected_partner],
        last_action=last_actions[selected_partner],
        interaction_count=counts[selected_partner],
        partner_action_prob_table=partner_action_prob_table,
        switch_round=switch_round,
    )
    best_policy_idx = jnp.argmin(G)
    best_policy_step_costs = step_costs[best_policy_idx]
    mean_abs_step_efe = jnp.mean(jnp.abs(best_policy_step_costs))
    return {
        "action": action,
        "key": key,
        "q_pi": q_pi,
        "G": G,
        "terminal_values": terminal_values,
        "predicted_partner_action_probs": predicted_partner_action_probs,
        "selected_partner": selected_partner,
        "selected_social_action": selected_social_action,
        "best_policy_idx": best_policy_idx,
        "best_policy_step_costs": best_policy_step_costs,
        "mean_abs_step_efe": mean_abs_step_efe,
    }
