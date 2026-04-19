"""Policy construction and posterior/action selection helpers."""

from __future__ import annotations

import itertools

import numpy as np

from aif.agent import Agent
from aif.maths import normalize, softmax
from aif.utils import enumerate_factorized_actions


def construct_policies(
    num_controls: list[int],
    planning_horizon: int,
    max_policies: int | None = None,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Enumerate or sample policy sequences."""

    rng = rng or np.random.default_rng()
    instantaneous_actions = enumerate_factorized_actions(num_controls)
    action_count = len(instantaneous_actions)
    total = action_count**planning_horizon

    if max_policies is None or total <= max_policies:
        all_sequences = itertools.product(range(action_count), repeat=planning_horizon)
        encoded = np.asarray(list(all_sequences), dtype=int)
    else:
        encoded = rng.integers(0, action_count, size=(max_policies, planning_horizon), dtype=int)

    if len(num_controls) == 1:
        return encoded

    decoded = np.zeros((encoded.shape[0], planning_horizon, len(num_controls)), dtype=int)
    action_lookup = np.asarray(instantaneous_actions, dtype=int)
    for idx in range(encoded.shape[0]):
        decoded[idx] = action_lookup[encoded[idx]]
    return decoded


def compute_policy_posterior(
    G: np.ndarray,
    gamma: float = 1.0,
    E: np.ndarray | None = None,
) -> np.ndarray:
    """Posterior over policies via softmax of negative EFE."""

    log_prior = np.zeros_like(G) if E is None else np.asarray(E, dtype=float)
    logits = -gamma * np.asarray(G, dtype=float) + log_prior
    return softmax(logits, backend="numpy")


def gamma_per_policy(gamma_base, first_partners, precision_signal):
    """Map per-partner beta expectations onto per-policy precision."""

    partners = np.asarray(first_partners, dtype=int)
    beta_expectations = np.asarray(precision_signal, dtype=float)[partners]
    safe_beta = np.maximum(beta_expectations, 1e-12)
    return float(gamma_base) / safe_beta


def _sample_action_impl(
    q_pi: np.ndarray,
    policies: np.ndarray,
    timestep: int = 0,
    sampling_mode: str = "marginal",
    rng: np.random.Generator | None = None,
):
    """Sample or select an action from the policy posterior."""

    rng = rng or np.random.default_rng()
    q_pi = np.asarray(q_pi, dtype=float)
    policies = np.asarray(policies, dtype=int)

    if sampling_mode == "full":
        policy_idx = int(rng.choice(len(q_pi), p=q_pi))
        step = policies[policy_idx, timestep]
        if policies.ndim == 3:
            return np.asarray(step, dtype=int)
        return int(step)

    if policies.ndim == 2:
        actions = policies[:, timestep]
        marginal = np.zeros(actions.max() + 1, dtype=float)
        for idx, action in enumerate(actions):
            marginal[action] += q_pi[idx]
        marginal = normalize(marginal, axis=0, backend="numpy").squeeze()
        return int(rng.choice(len(marginal), p=marginal))

    actions = policies[:, timestep, :]
    unique_actions, inverse = np.unique(actions, axis=0, return_inverse=True)
    marginal = np.zeros(len(unique_actions), dtype=float)
    for idx, action_idx in enumerate(inverse):
        marginal[action_idx] += q_pi[idx]
    marginal = normalize(marginal, axis=0, backend="numpy").squeeze()
    chosen = int(rng.choice(len(unique_actions), p=marginal))
    return unique_actions[chosen]


def sample_action(agent: Agent, q_pi: np.ndarray, timestep: int = 0):
    """Sample an action using the agent's policies, mode, and RNG."""

    return _sample_action_impl(
        q_pi=q_pi,
        policies=agent.policies,
        timestep=timestep,
        sampling_mode=agent.action_sampling,
        rng=agent.rng,
    )
