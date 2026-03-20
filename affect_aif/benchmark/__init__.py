"""Benchmark module for cross-environment evaluation of active inference agents.

Provides tools to run affect_aif agents in both the native trust game and
external environments (CoGames/MettaGrid), with common metrics for comparison.

CoGames and MettaGrid are optional dependencies. Core components (baselines,
metrics) work without them.
"""

from __future__ import annotations

from affect_aif.benchmark.compat import cogames_available, mettagrid_available
from affect_aif.benchmark.baselines import (
    RandomAgent,
    TitForTatAgent,
    WinStayLoseShiftAgent,
    QLearningAgent,
)
from affect_aif.benchmark.common_metrics import (
    cooperation_rate,
    cumulative_payoff,
    type_identification_accuracy,
    adaptation_speed,
    partner_discrimination,
)

__all__ = [
    "cogames_available",
    "mettagrid_available",
    "RandomAgent",
    "TitForTatAgent",
    "WinStayLoseShiftAgent",
    "QLearningAgent",
    "cooperation_rate",
    "cumulative_payoff",
    "type_identification_accuracy",
    "adaptation_speed",
    "partner_discrimination",
]
