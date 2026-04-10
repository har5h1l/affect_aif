"""Helpers for HESP-style affective charge computation."""

from __future__ import annotations


def affective_charge(prediction_error: float, *, alpha: float = 3.0, sigma_0_sq: float = 0.25) -> float:
    """Convert surprise magnitude into a signed HESP-style charge."""

    error = float(prediction_error)
    return float(alpha) * (float(sigma_0_sq) - error**2)
