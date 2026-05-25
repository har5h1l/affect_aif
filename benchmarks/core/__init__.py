"""Shared benchmark runner, config, metrics, and reporting helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from benchmarks.core.common_metrics import (
        adaptation_speed,
        cooperation_rate,
        cumulative_payoff,
        mean_payoff,
        partner_discrimination,
        type_identification_accuracy,
    )
__all__ = [
    "cooperation_rate",
    "cumulative_payoff",
    "mean_payoff",
    "type_identification_accuracy",
    "adaptation_speed",
    "partner_discrimination",
]


def __getattr__(name: str) -> Any:
    if name in {
        "cooperation_rate",
        "cumulative_payoff",
        "mean_payoff",
        "type_identification_accuracy",
        "adaptation_speed",
        "partner_discrimination",
    }:
        from benchmarks.core import common_metrics

        return getattr(common_metrics, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
