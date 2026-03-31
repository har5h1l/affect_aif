"""Backend-aware benchmarking for trust-game and CvC evaluation.

The trust backend is the canonical supported benchmark surface for
affect_aif's current active-inference agents.

The local CvC backend exists as an experimental proof-of-concept path. It is
kept separate so the main project can remain on Python 3.10 while that work
matures on Python 3.12.

The legacy scripted gridworld adapter remains available only as a backward-
compatibility shim; it is not treated as a real CoGames integration or a peer
of the trust benchmark.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from affect_aif.benchmark.baselines import (
        GrimTriggerAgent,
        PavlovAgent,
        QLearningAgent,
        RandomAgent,
        TitForTatAgent,
        WinStayLoseShiftAgent,
    )
    from affect_aif.benchmark.compat import cogames_available, mettagrid_available
    from affect_aif.benchmark.common_metrics import (
        adaptation_speed,
        cooperation_rate,
        cumulative_payoff,
        partner_discrimination,
        type_identification_accuracy,
    )

__all__ = [
    "cogames_available",
    "mettagrid_available",
    "RandomAgent",
    "TitForTatAgent",
    "WinStayLoseShiftAgent",
    "PavlovAgent",
    "GrimTriggerAgent",
    "QLearningAgent",
    "cooperation_rate",
    "cumulative_payoff",
    "type_identification_accuracy",
    "adaptation_speed",
    "partner_discrimination",
]


def __getattr__(name: str) -> Any:
    if name in {"cogames_available", "mettagrid_available"}:
        from affect_aif.benchmark import compat

        return getattr(compat, name)
    if name in {
        "RandomAgent",
        "TitForTatAgent",
        "WinStayLoseShiftAgent",
        "PavlovAgent",
        "GrimTriggerAgent",
        "QLearningAgent",
    }:
        from affect_aif.benchmark import baselines

        return getattr(baselines, name)
    if name in {
        "cooperation_rate",
        "cumulative_payoff",
        "type_identification_accuracy",
        "adaptation_speed",
        "partner_discrimination",
    }:
        from affect_aif.benchmark import common_metrics

        return getattr(common_metrics, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
