"""Compatibility facade for control and rollout helpers."""

from agent.inference.efe import (
    compute_efe_all_policies,
    compute_expected_free_energy,
)
from agent.inference.policies import compute_policy_posterior, construct_policies, sample_action
from agent.inference.rollout import (
    _rollout_policy_trust_game_mean_field,
    _rollout_policy_trust_game_sophisticated,
    decision_step_trust_game,
    generate_observation_sequences,
)

__all__ = [
    "compute_efe_all_policies",
    "compute_expected_free_energy",
    "compute_policy_posterior",
    "construct_policies",
    "decision_step_trust_game",
    "generate_observation_sequences",
    "sample_action",
    "_rollout_policy_trust_game_mean_field",
    "_rollout_policy_trust_game_sophisticated",
]
