"""Serialization and sensitivity helpers for experiment execution."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from experiments.trust.config import ExperimentConfig


def build_sensitivity_specs(config: ExperimentConfig) -> list[tuple[str, float]]:
    sweep_specs: list[tuple[str, float]] = []
    factors = config.sensitivity_factors
    if not isinstance(factors, dict):
        factors = {"alpha_charge": factors}
    for value in factors.get("alpha_charge", []):
        sweep_specs.append(("alpha_charge", float(value)))
    for value in factors.get("sigma_0_sq", []):
        sweep_specs.append(("sigma_0_sq", float(value)))
    for value in factors.get("beta_persistence", []):
        sweep_specs.append(("beta_persistence", float(value)))
    for value in factors.get("initial_beta", []):
        sweep_specs.append(("initial_beta", float(value)))
    return sweep_specs


def serialize_config(config: ExperimentConfig) -> dict[str, Any]:
    return asdict(config)


def deserialize_config(payload: dict[str, Any]) -> ExperimentConfig:
    return ExperimentConfig.from_dict(payload)


__all__ = [
    "build_sensitivity_specs",
    "deserialize_config",
    "serialize_config",
]
