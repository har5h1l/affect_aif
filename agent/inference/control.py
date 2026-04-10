"""Compatibility facade for control and rollout helpers."""

from affect_aif.core.efe import (
    compute_efe_all_policies,
    compute_efe_with_terminal_value,
    compute_expected_free_energy,
)
from affect_aif.core.policies import compute_policy_posterior, construct_policies, sample_action
from affect_aif.core.rollout import (
    _rollout_policy_trust_game_mean_field,
    _rollout_policy_trust_game_sophisticated,
    decision_step_trust_game,
    generate_observation_sequences,
)

__all__ = [
    "compute_efe_all_policies",
    "compute_efe_with_terminal_value",
    "compute_expected_free_energy",
    "compute_policy_posterior",
    "construct_policies",
    "decision_step_trust_game",
    "generate_observation_sequences",
    "sample_action",
    "_rollout_policy_trust_game_mean_field",
    "_rollout_policy_trust_game_sophisticated",
]
