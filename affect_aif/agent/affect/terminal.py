"""Terminal value helpers for affective and reward-average agents."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from affect_aif.generative_model.payoffs import decode_action


def _roll_policy_terminal_state(model, beliefs, last_actions, counts, policy, active_partner: int | None):
    sim_beliefs = jnp.asarray(beliefs, dtype=jnp.float32)
    sim_last_actions = jnp.asarray(last_actions, dtype=jnp.int32)
    sim_counts = jnp.asarray(counts, dtype=jnp.int32)
    terminal_partner = active_partner if active_partner is not None else 0
    terminal_action = 0

    for raw_action in np.asarray(policy, dtype=int):
        terminal_partner, terminal_action = decode_action(
            int(raw_action),
            num_partners=model.num_partners,
            assignment_mode=model.assignment_mode,
            active_partner=active_partner,
        )
        partner_probs = jnp.asarray(
            model.contextual_partner_action_distribution(
                sim_beliefs[terminal_partner],
                int(sim_last_actions[terminal_partner]),
                int(sim_counts[terminal_partner]),
            ),
            dtype=jnp.float32,
        )
        sim_last_actions = sim_last_actions.at[terminal_partner].set(int(terminal_action))
        sim_counts = sim_counts.at[terminal_partner].set(sim_counts[terminal_partner] + 1)
        sim_beliefs = sim_beliefs.at[terminal_partner].set(
            jnp.asarray(model.transition_for_action(0), dtype=jnp.float32) @ sim_beliefs[terminal_partner]
        )

    continuation_probs = jnp.asarray(
        model.contextual_partner_action_distribution(
            sim_beliefs[terminal_partner],
            int(sim_last_actions[terminal_partner]),
            int(sim_counts[terminal_partner]),
        ),
        dtype=jnp.float32,
    )
    continuation = model.expected_agent_payoff(int(terminal_action), np.asarray(continuation_probs, dtype=float))
    return terminal_partner, continuation


def compute_terminal_values(
    model,
    beliefs,
    last_actions,
    counts,
    policies,
    betas,
    active_partner: int | None,
    mu: float = 2.0,
) -> np.ndarray:
    """Compute precision-weighted continuation values for each policy."""

    max_abs_payoff = max(abs(level) for level in model.payoff_levels)
    terminal_values = np.zeros(len(policies), dtype=float)
    betas = np.asarray(betas, dtype=float)
    for idx, policy in enumerate(np.asarray(policies, dtype=int)):
        partner_idx, continuation = _roll_policy_terminal_state(model, beliefs, last_actions, counts, policy, active_partner)
        terminal_values[idx] = -float(mu) * betas[int(partner_idx)] * (continuation / max_abs_payoff)
    return terminal_values


def compute_terminal_values_reward_avg(
    model,
    beliefs,
    last_actions,
    counts,
    policies,
    reward_avgs,
    active_partner: int | None,
    mu: float = 2.0,
) -> np.ndarray:
    """Reward-average version of terminal continuation values."""

    max_abs_payoff = max(abs(level) for level in model.payoff_levels)
    terminal_values = np.zeros(len(policies), dtype=float)
    reward_signal = np.tanh(np.asarray(reward_avgs, dtype=float) / max_abs_payoff)
    for idx, policy in enumerate(np.asarray(policies, dtype=int)):
        partner_idx, continuation = _roll_policy_terminal_state(model, beliefs, last_actions, counts, policy, active_partner)
        terminal_values[idx] = -float(mu) * reward_signal[int(partner_idx)] * (continuation / max_abs_payoff)
    return terminal_values
