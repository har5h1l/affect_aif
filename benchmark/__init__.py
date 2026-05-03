"""Backend-aware benchmarking for external and cross-task evaluation.

The trust-task evaluation arena lives under ``tasks.trust.evaluation``.

The local CvC backend exists as an experimental proof-of-concept path. It is
kept separate so the main project can remain on Python 3.10 while that work
matures on Python 3.12.

The legacy scripted gridworld adapter remains available only as a backward-
compatibility shim; it is not treated as a real CoGames integration or a peer
of the trust-task evaluation arena.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from benchmark.common_metrics import (
        adaptation_speed,
        cooperation_rate,
        cumulative_payoff,
        partner_discrimination,
        type_identification_accuracy,
    )
    from benchmark.compat import cogames_available, mettagrid_available

__all__ = [
    "cogames_available",
    "mettagrid_available",
    "cooperation_rate",
    "cumulative_payoff",
    "type_identification_accuracy",
    "adaptation_speed",
    "partner_discrimination",
]


def __getattr__(name: str) -> Any:
    if name in {"cogames_available", "mettagrid_available"}:
        from benchmark import compat

        return getattr(compat, name)
    if name in {
        "cooperation_rate",
        "cumulative_payoff",
        "type_identification_accuracy",
        "adaptation_speed",
        "partner_discrimination",
    }:
        from benchmark import common_metrics

        return getattr(common_metrics, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
