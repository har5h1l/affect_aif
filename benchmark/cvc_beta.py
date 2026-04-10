"""Pure-Python beta (precision) update helpers for CvC policies.

Separated from cvc_affect_policy.py so they can be tested without mettagrid.
"""

from __future__ import annotations

import math

# Beta EMA hyper-parameters (match trust-game defaults in affect/state.py)
ALPHA_CHARGE: float = 3.0
SIGMA_0_SQ: float = 0.25
LAMBDA_SMOOTH: float = 0.6
INITIAL_BETA: float = 0.5

# Team-beta thresholds for policy modulation
COOPERATE_THRESHOLD: float = 0.6
INDEPENDENT_THRESHOLD: float = 0.4

# Team-beta EMA smoothing
TEAM_BETA_SMOOTH: float = 0.8


def sigmoid(x: float) -> float:
    """Numerically stable sigmoid."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    ex = math.exp(x)
    return ex / (1.0 + ex)


def update_beta(
    predicted: tuple[int, int],
    actual: tuple[int, int],
    prev_beta: float,
    max_distance: float,
) -> float:
    """EMA beta update from positional prediction error.

    Args:
        predicted: Expected teammate position (global coords).
        actual: Observed teammate position (global coords).
        prev_beta: Previous beta value for this teammate.
        max_distance: Normalisation constant (obs_height + obs_width).

    Returns:
        Updated beta in (0, 1).
    """
    dist = abs(predicted[0] - actual[0]) + abs(predicted[1] - actual[1])
    surprise = dist / max(max_distance, 1.0)
    charge = ALPHA_CHARGE * (SIGMA_0_SQ - surprise * surprise)
    squashed = sigmoid(charge)
    return LAMBDA_SMOOTH * prev_beta + (1.0 - LAMBDA_SMOOTH) * squashed
