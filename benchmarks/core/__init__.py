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
    from benchmarks.core.compat import cogames_available, mettagrid_available

__all__ = [
    "cogames_available",
    "mettagrid_available",
    "cooperation_rate",
    "cumulative_payoff",
    "mean_payoff",
    "type_identification_accuracy",
    "adaptation_speed",
    "partner_discrimination",
]


def __getattr__(name: str) -> Any:
    if name in {"cogames_available", "mettagrid_available"}:
        from benchmarks.core import compat

        return getattr(compat, name)
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
