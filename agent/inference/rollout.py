"""Rollout helpers for trust-game planning."""

from __future__ import annotations

import numpy as np


def _decode_action(action, active_partner, assignment_mode_code, num_social_actions=2):
    if int(assignment_mode_code) == 1:
        return int(action) // int(num_social_actions), int(action) % int(num_social_actions)
    return int(active_partner), int(action)


def _decode_policy_timestep(
    policy_row,
    active_partner,
    assignment_mode_code,
    num_social_actions=2,
):
    """Return (partner_idx, stance_action, own_action). Legacy flat rows use stance=own=social."""

    row = np.asarray(policy_row, dtype=int).ravel()
    if row.size == 1:
        partner_idx, social_action = _decode_action(
            int(row[0]),
            active_partner=active_partner,
            assignment_mode_code=assignment_mode_code,
            num_social_actions=num_social_actions,
        )
        return partner_idx, int(social_action), int(social_action)
    if int(assignment_mode_code) == 1:
        return int(row[0]), int(row[1]), int(row[2])
    return int(active_partner), int(row[1]), int(row[2])


def generate_observation_sequences(planning_horizon: int) -> np.ndarray:
    """Enumerate all binary observation sequences needed for sophisticated rollout."""

    if planning_horizon <= 1:
        return np.zeros((1, 0), dtype=int)

    obs_steps = planning_horizon - 1
    total = 2**obs_steps
    encoded = np.arange(total, dtype=np.int32)[:, None]
    shifts = np.arange(obs_steps - 1, -1, -1, dtype=np.int32)[None, :]
    return ((encoded >> shifts) & 1).astype(int)


def _normalize(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    total = float(array.sum())
    return array / max(total, 1e-16)


def _entropy(values: np.ndarray) -> float:
    probs = _normalize(values)
    return float(-(probs * np.log(probs + 1e-16)).sum())


def _partner_action_distribution(joint_belief: np.ndarray, partner_action_prob_table: np.ndarray) -> np.ndarray:
    p_coop = float(np.sum(np.asarray(joint_belief, dtype=float) * np.asarray(partner_action_prob_table, dtype=float)))
    return np.asarray([p_coop, 1.0 - p_coop], dtype=float)


def _joint_likelihood(observed_action: int, partner_action_prob_table: np.ndarray) -> np.ndarray:
    p_coop = np.asarray(partner_action_prob_table, dtype=float)
    if int(observed_action) == 0:
        return p_coop
    return 1.0 - p_coop


def _predict_next_joint(joint_belief: np.ndarray, B_type: np.ndarray, B_stance: np.ndarray) -> np.ndarray:
    predictive = np.asarray(B_type, dtype=float) @ np.asarray(joint_belief, dtype=float) @ np.asarray(B_stance, dtype=float).T
    return _normalize(predictive)


def _joint_belief_update(
    joint_belief: np.ndarray,
    observed_action: int,
    B_type: np.ndarray,
    B_stance: np.ndarray,
    partner_action_prob_table: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    likelihood = _joint_likelihood(observed_action, partner_action_prob_table)
    posterior = _normalize(np.asarray(joint_belief, dtype=float) * likelihood)
    predictive_next = _predict_next_joint(posterior, B_type=B_type, B_stance=B_stance)
    return posterior, predictive_next


def _payoff_distribution(social_action, partner_action_probs, payoff_index_table, num_payoffs):
    coop_idx = int(payoff_index_table[int(social_action), 0])
    defect_idx = int(payoff_index_table[int(social_action), 1])
    dist = np.zeros((num_payoffs,), dtype=float)
    dist[coop_idx] += float(partner_action_probs[0])
    dist[defect_idx] += float(partner_action_probs[1])
    return dist


def gamma_per_policy(gamma_base, first_partners, precision_signal):
    """Map per-partner beta expectations onto per-policy policy precision."""

    partners = np.asarray(first_partners, dtype=int)
    beta_expectations = np.asarray(precision_signal, dtype=float)[partners]
    safe_beta = np.maximum(beta_expectations, 1e-12)
    return float(gamma_base) / safe_beta


def _rollout_policy_trust_game_mean_field(
    policy,
    beliefs,
    active_partner,
    assignment_mode_code,
    B_type,
    B_stance_by_action,
    partner_action_prob_table,
    payoff_index_table,
    agent_payoff_table,
    payoff_preferences,
    partner_action_preferences,
    max_abs_payoff,
    use_utility_flag,
    use_information_gain_flag,
    num_social_actions=2,
):
    del agent_payoff_table, max_abs_payoff, use_information_gain_flag

    beliefs_t = np.asarray(beliefs, dtype=float).copy()
    step_costs: list[float] = []
    first_partner = None

    for policy_row in np.asarray(policy, dtype=int):
        partner_idx, stance_action, own_action = _decode_policy_timestep(
            policy_row,
            active_partner=active_partner,
            assignment_mode_code=assignment_mode_code,
            num_social_actions=num_social_actions,
        )
        if first_partner is None:
            first_partner = partner_idx
        joint = beliefs_t[partner_idx]
        partner_probs = _partner_action_distribution(joint, partner_action_prob_table)
        payoff_dist = _payoff_distribution(
            social_action=own_action,
            partner_action_probs=partner_probs,
            payoff_index_table=payoff_index_table,
            num_payoffs=len(payoff_preferences),
        )
        pragmatic = -float(np.dot(partner_probs, partner_action_preferences)) - float(np.dot(payoff_dist, payoff_preferences))
        step_cost = float(use_utility_flag) * pragmatic
        step_costs.append(step_cost)
        beliefs_t[partner_idx] = _predict_next_joint(
            joint,
            B_type=np.asarray(B_type, dtype=float),
            B_stance=np.asarray(B_stance_by_action[int(stance_action)], dtype=float),
        )

    total = float(sum(step_costs))
    return total, np.asarray(step_costs, dtype=float), int(first_partner)


def _rollout_policy_trust_game_sophisticated(
    policy,
    observation_sequences,
    beliefs,
    active_partner,
    assignment_mode_code,
    B_type,
    B_stance_by_action,
    partner_action_prob_table,
    payoff_index_table,
    agent_payoff_table,
    payoff_preferences,
    partner_action_preferences,
    max_abs_payoff,
    use_utility_flag,
    use_information_gain_flag,
    num_social_actions=2,
):
    del agent_payoff_table, max_abs_payoff

    policy = np.asarray(policy, dtype=int)
    observation_sequences = np.asarray(observation_sequences, dtype=int)
    beliefs = np.asarray(beliefs, dtype=float)
    B_type = np.asarray(B_type, dtype=float)
    B_stance_by_action = np.asarray(B_stance_by_action, dtype=float)
    partner_action_prob_table = np.asarray(partner_action_prob_table, dtype=float)

    weighted_total = 0.0
    weighted_steps = np.zeros((len(policy),), dtype=float)
    first_partner = None

    for obs_sequence in observation_sequences:
        beliefs_t = beliefs.copy()
        path_log_prob = 0.0
        step_costs = np.zeros((len(policy),), dtype=float)

        for t, policy_row in enumerate(policy):
            partner_idx, stance_action, own_action = _decode_policy_timestep(
                policy_row,
                active_partner=active_partner,
                assignment_mode_code=assignment_mode_code,
                num_social_actions=num_social_actions,
            )
            if first_partner is None:
                first_partner = partner_idx
            joint = beliefs_t[partner_idx]
            partner_probs = _partner_action_distribution(joint, partner_action_prob_table)
            payoff_dist = _payoff_distribution(
                social_action=own_action,
                partner_action_probs=partner_probs,
                payoff_index_table=payoff_index_table,
                num_payoffs=len(payoff_preferences),
            )
            pragmatic = -float(np.dot(partner_probs, partner_action_preferences)) - float(np.dot(payoff_dist, payoff_preferences))

            if t < len(policy) - 1:
                observed_action = int(obs_sequence[t])
                obs_prob = float(partner_probs[observed_action])
                posterior, predictive_next = _joint_belief_update(
                    joint,
                    observed_action=observed_action,
                    B_type=B_type,
                    B_stance=B_stance_by_action[int(stance_action)],
                    partner_action_prob_table=partner_action_prob_table,
                )
                prior_entropy = _entropy(joint.reshape(-1))
                posterior_entropy = _entropy(posterior.reshape(-1))
                epistemic = posterior_entropy - prior_entropy
                beliefs_t[partner_idx] = predictive_next
                path_log_prob += np.log(obs_prob + 1e-16)
            else:
                epistemic = 0.0
                beliefs_t[partner_idx] = _predict_next_joint(
                    joint,
                    B_type=B_type,
                    B_stance=B_stance_by_action[int(stance_action)],
                )

            step_costs[t] = float(use_utility_flag) * pragmatic + float(use_information_gain_flag) * epistemic

        path_weight = float(np.exp(path_log_prob))
        weighted_total += float(step_costs.sum()) * path_weight
        weighted_steps += step_costs * path_weight

    return weighted_total, weighted_steps, int(first_partner if first_partner is not None else 0)


def decision_step_trust_game(
    beliefs,
    active_partner,
    policies,
    observation_sequences,
    B_type,
    B_stance_by_action,
    partner_action_prob_table,
    payoff_index_table,
    agent_payoff_table,
    payoff_preferences,
    partner_action_preferences,
    precision_signal,
    assignment_mode_code,
    gamma,
    use_utility_flag,
    use_information_gain_flag,
    num_social_actions=2,
    log_policy_prior=None,
):
    """Evaluate all policies and return rollout diagnostics."""

    totals = []
    step_costs = []
    first_partners = []
    for policy in np.asarray(policies, dtype=int):
        total, steps, first_partner = _rollout_policy_trust_game_sophisticated(
            policy=policy,
            observation_sequences=observation_sequences,
            beliefs=beliefs,
            active_partner=active_partner,
            assignment_mode_code=assignment_mode_code,
            B_type=B_type,
            B_stance_by_action=B_stance_by_action,
            partner_action_prob_table=partner_action_prob_table,
            payoff_index_table=payoff_index_table,
            agent_payoff_table=agent_payoff_table,
            payoff_preferences=payoff_preferences,
            partner_action_preferences=partner_action_preferences,
            max_abs_payoff=1.0,
            use_utility_flag=use_utility_flag,
            use_information_gain_flag=use_information_gain_flag,
            num_social_actions=num_social_actions,
        )
        totals.append(total)
        step_costs.append(steps)
        first_partners.append(first_partner)

    G = np.asarray(totals, dtype=float)
    step_costs = np.asarray(step_costs, dtype=float)
    first_partners = np.asarray(first_partners, dtype=int)
    gamma_values = gamma_per_policy(gamma_base=gamma, first_partners=first_partners, precision_signal=precision_signal)
    logits = -gamma_values * G
    if log_policy_prior is not None:
        logits = logits + np.asarray(log_policy_prior, dtype=float)
    logits -= logits.max(initial=0.0)
    exp_logits = np.exp(logits)
    q_pi = exp_logits / max(float(exp_logits.sum()), 1e-16)
    mean_abs_step_efe = float(np.mean(np.abs(step_costs))) if step_costs.size else float("nan")
    return {
        "G": G,
        "q_pi": q_pi,
        "step_costs": step_costs,
        "first_partners": first_partners,
        "mean_abs_step_efe": mean_abs_step_efe,
    }
