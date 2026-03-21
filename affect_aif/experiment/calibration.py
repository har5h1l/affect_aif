"""Serialization and calibration helpers for experiment execution."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import numpy as np

from affect_aif.experiment.config import ExperimentConfig


def build_calibration_summary(
    config: ExperimentConfig,
    efe_values: list[float],
    calibration_episodes: int,
) -> dict[str, float | int]:
    mean_abs_efe = float(np.nanmean(np.asarray(efe_values, dtype=float))) if efe_values else 0.0
    horizon_gap = max(1, config.deep_horizon - config.shallow_horizon)
    derived_mu = float(mean_abs_efe * horizon_gap)
    return {
        "requested_calibration_episodes": int(config.calibration_episodes),
        "calibration_episodes": int(calibration_episodes),
        "mean_abs_efe_per_step": mean_abs_efe,
        "derived_mu": derived_mu,
    }


def serialize_config(config: ExperimentConfig) -> dict[str, Any]:
    return asdict(config)


def deserialize_config(payload: dict[str, Any]) -> ExperimentConfig:
    return ExperimentConfig.from_dict(payload)
