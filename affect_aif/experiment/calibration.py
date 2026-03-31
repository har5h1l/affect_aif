"""Serialization and calibration helpers for experiment execution."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import numpy as np

from affect_aif.experiment.config import ExperimentConfig

MIN_FULL_RUN_CALIBRATION_EPISODES = 10


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


def build_zero_calibration_summary(config: ExperimentConfig) -> dict[str, float | int]:
    return {
        "requested_calibration_episodes": int(config.calibration_episodes),
        "calibration_episodes": 0,
        "mean_abs_efe_per_step": 0.0,
        "derived_mu": 0.0,
    }


def resolve_calibration_episodes(config: ExperimentConfig, *, enforce_minimum: bool) -> int:
    requested = int(config.calibration_episodes)
    if enforce_minimum:
        return max(requested, MIN_FULL_RUN_CALIBRATION_EPISODES)
    return requested


def build_sensitivity_specs(config: ExperimentConfig) -> list[tuple[str, float]]:
    sweep_specs: list[tuple[str, float]] = []
    for factor in config.sensitivity_factors["mu"]:
        sweep_specs.append(("mu", float(factor)))
    for value in config.sensitivity_factors["lambda_smooth"]:
        sweep_specs.append(("lambda_smooth", float(value)))
    for value in config.sensitivity_factors["alpha_charge"]:
        sweep_specs.append(("alpha_charge", float(value)))
    for value in config.sensitivity_factors["sigma_0_sq"]:
        sweep_specs.append(("sigma_0_sq", float(value)))
    return sweep_specs


def serialize_config(config: ExperimentConfig) -> dict[str, Any]:
    return asdict(config)


def deserialize_config(payload: dict[str, Any]) -> ExperimentConfig:
    return ExperimentConfig.from_dict(payload)


__all__ = [
    "MIN_FULL_RUN_CALIBRATION_EPISODES",
    "build_calibration_summary",
    "build_sensitivity_specs",
    "build_zero_calibration_summary",
    "deserialize_config",
    "resolve_calibration_episodes",
    "serialize_config",
]
