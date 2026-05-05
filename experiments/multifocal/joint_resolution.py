"""Joint action resolution for multi-focal trust-game pairs."""

from __future__ import annotations

import numpy as np

from tasks.trust.pomdp import TrustPomdpTemplate


def joint_resolve(my_action: int, partner_action: int, template: TrustPomdpTemplate) -> tuple[int, float]:
    """Resolve a pair's actions into (payoff_obs_idx, payoff_value) for the agent
    whose action is `my_action`. Symmetric: payoff for the other side is computed
    by a second call with the arguments swapped against the partner's template.

    Returns:
        payoff_obs_idx: index into template.payoff_levels (used as the second
                        observation modality in observe_outcome).
        payoff_value:   raw payoff (used for logging / metrics).
    """
    payoff_value = float(template.payoff_matrix[int(my_action), int(partner_action), 0])
    levels = np.asarray(template.payoff_levels, dtype=float)
    diffs = np.abs(levels - payoff_value)
    obs_idx = int(np.argmin(diffs))
    if diffs[obs_idx] > 1e-9:
        raise ValueError(
            f"payoff_value={payoff_value} not found in template.payoff_levels={levels.tolist()}; "
            "template construction is inconsistent with the actions taken."
        )
    return obs_idx, payoff_value
