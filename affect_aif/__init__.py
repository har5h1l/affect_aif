"""Affect as computational infrastructure for social active inference."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["ExperimentConfig", "ExperimentRunner"]

if TYPE_CHECKING:
    from affect_aif.experiment.config import ExperimentConfig
    from affect_aif.experiment.runner import ExperimentRunner


def __getattr__(name: str) -> Any:
    if name == "ExperimentConfig":
        from affect_aif.experiment.config import ExperimentConfig

        return ExperimentConfig
    if name == "ExperimentRunner":
        from affect_aif.experiment.runner import ExperimentRunner

        return ExperimentRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
