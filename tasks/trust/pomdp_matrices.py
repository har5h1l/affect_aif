"""Matrix and policy builders for the native trust-task POMDP template."""

from __future__ import annotations

from itertools import product

import numpy as np

from tasks.trust.payoffs import payoff_to_index
from tasks.trust.stance import cooperation_evidence_strength, interpolate_stance_transition


def build_payoff_index_table(
    *,
    payoff_matrix: np.ndarray,
    payoff_values: tuple[float, ...],
    num_social_actions: int,
) -> np.ndarray:
    indices = np.zeros((num_social_actions, 2), dtype=int)
    for agent_action in range(num_social_actions):
        for partner_action in range(2):
            payoff = payoff_matrix[agent_action, partner_action, 0]
            indices[agent_action, partner_action] = payoff_to_index(payoff, payoff_values)
    return indices


def build_task_likelihoods(
    *,
    num_types: int,
    num_stances: int,
    num_social_actions: int,
    payoff_values: tuple[float, ...],
    partner_action_prob_table: np.ndarray,
    payoff_index_table: np.ndarray,
    observation_noise: float,
) -> tuple[np.ndarray, np.ndarray]:
    partner_action = np.zeros((2, num_types, num_stances), dtype=float)
    for type_idx in range(num_types):
        for stance_idx in range(num_stances):
            p_coop = partner_action_prob_table[type_idx, stance_idx]
            clean = np.asarray([p_coop, 1.0 - p_coop], dtype=float)
            partner_action[:, type_idx, stance_idx] = (1.0 - observation_noise) * clean + observation_noise * 0.5

    payoff_obs = np.zeros((len(payoff_values), num_social_actions, num_types, num_stances), dtype=float)
    for agent_action in range(num_social_actions):
        for type_idx in range(num_types):
            for stance_idx in range(num_stances):
                p_coop = partner_action_prob_table[type_idx, stance_idx]
                coop_idx = int(payoff_index_table[agent_action, 0])
                defect_idx = int(payoff_index_table[agent_action, 1])
                payoff_obs[coop_idx, agent_action, type_idx, stance_idx] += p_coop
                payoff_obs[defect_idx, agent_action, type_idx, stance_idx] += 1.0 - p_coop
    return partner_action, payoff_obs


def build_transition_matrices(
    *,
    num_types: int,
    num_stances: int,
    num_social_actions: int,
    num_controls: tuple[int, ...],
    p_switch: float,
) -> list[np.ndarray]:
    type_base = np.full((num_types, num_types), p_switch / max(num_types - 1, 1), dtype=float)
    np.fill_diagonal(type_base, 1.0 - p_switch)

    if len(num_controls) > 1:
        type_transition_array = type_base[:, :, None]
        stance_transition = np.zeros((num_stances, num_stances, int(num_controls[1])), dtype=float)
        own_transition = np.zeros((num_social_actions, num_social_actions, int(num_controls[2])), dtype=float)
        for stance_action in range(int(num_controls[1])):
            evidence = cooperation_evidence_strength(stance_action, num_social_actions=num_social_actions)
            stance_transition[:, :, stance_action] = interpolate_stance_transition(evidence)
        for own_action in range(int(num_controls[2])):
            own_transition[own_action, :, own_action] = 1.0
        return [type_transition_array, stance_transition, own_transition]

    num_flat_controls = int(num_controls[0])
    type_transition_array = np.repeat(type_base[:, :, None], num_flat_controls, axis=2)
    stance_transition = np.zeros((num_stances, num_stances, num_flat_controls), dtype=float)
    own_transition = np.zeros((num_social_actions, num_social_actions, num_flat_controls), dtype=float)
    for action in range(num_flat_controls):
        evidence = cooperation_evidence_strength(action, num_social_actions=num_social_actions)
        stance_transition[:, :, action] = interpolate_stance_transition(evidence)
        own_transition[action, :, action] = 1.0
    return [type_transition_array, stance_transition, own_transition]


def build_preference_vectors(
    *,
    payoff_values: tuple[float, ...],
    preference_temperature: float,
) -> list[np.ndarray]:
    payoff_array = np.asarray(payoff_values, dtype=float)
    return [
        np.zeros(2, dtype=float),
        _log_stable(_softmax(payoff_array / max(float(preference_temperature), 1e-12))),
    ]


def build_initial_beliefs(*, num_types: int, num_stances: int, num_social_actions: int) -> list[np.ndarray]:
    return [
        np.full(num_types, 1.0 / num_types, dtype=float),
        np.asarray([0.2, 0.6, 0.2], dtype=float),
        np.full(num_social_actions, 1.0 / num_social_actions, dtype=float),
    ]


def build_policies(
    num_controls: tuple[int, ...],
    *,
    planning_horizon: int,
    max_policies: int | None,
    rng: np.random.Generator | None,
) -> np.ndarray:
    horizon = int(planning_horizon)
    if horizon < 1:
        raise ValueError("planning_horizon must be >= 1.")
    if max_policies is not None and int(max_policies) < 1:
        raise ValueError("max_policies must be >= 1 when provided.")

    instantaneous_controls = np.asarray(list(product(*(range(int(size)) for size in num_controls))), dtype=int)
    num_step_controls = int(instantaneous_controls.shape[0])
    total_policies = num_step_controls**horizon
    requested = total_policies if max_policies is None else min(int(max_policies), total_policies)
    if requested == total_policies:
        policy_indices = range(total_policies)
    elif rng is None:
        policy_indices = range(requested)
    else:
        policy_indices = rng.choice(total_policies, size=requested, replace=False)

    policies = np.zeros((requested, horizon, len(num_controls)), dtype=int)
    for policy_row, policy_idx in enumerate(policy_indices):
        idx = int(policy_idx)
        for timestep in range(horizon - 1, -1, -1):
            policies[policy_row, timestep] = instantaneous_controls[idx % num_step_controls]
            idx //= num_step_controls
    return policies


def _softmax(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    shifted = array - float(np.max(array))
    exp_values = np.exp(shifted)
    return exp_values / max(float(exp_values.sum()), 1e-16)


def _log_stable(values: np.ndarray) -> np.ndarray:
    return np.log(np.maximum(np.asarray(values, dtype=float), 1e-16))
