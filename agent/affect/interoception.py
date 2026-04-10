"""Helpers for HESP-style affective charge and interoceptive observations."""

from __future__ import annotations

import math

import numpy as np


def affective_charge(prediction_error: float, *, alpha: float = 3.0, sigma_0_sq: float = 0.25) -> float:
    """Convert surprise magnitude into a signed HESP-style charge."""

    error = float(prediction_error)
    return float(alpha) * (float(sigma_0_sq) - error**2)


def discretize_intero(charge: float, *, num_levels: int = 5) -> int:
    """Map signed charge onto a discrete interoceptive observation bin."""

    levels = max(int(num_levels), 1)
    probability = 1.0 / (1.0 + math.exp(-float(charge)))
    raw_bin = int(math.floor(probability * levels))
    return int(np.clip(raw_bin, 0, levels - 1))

