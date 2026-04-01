"""Process-safe worker tasks for experiment execution."""

from __future__ import annotations

from typing import Any

from affect_aif.experiment.calibration import deserialize_config
from affect_aif.experiment.runner import ExperimentRunner


def run_calibration_episode_task(config_payload: dict[str, Any], episode_idx: int, seed: int) -> dict[str, float | int]:
    config = deserialize_config(config_payload)
    config.verbose = False
    runner = ExperimentRunner(config)
    return runner.run_calibration_episode(episode_idx=episode_idx, seed=seed)


def run_primary_replication_task(
    config_payload: dict[str, Any],
    *,
    condition: int | str,
    replication: int,
    seed: int,
    calibration_summary: dict[str, Any] | None,
    config_path: str,
    config_name: str,
    batch_id: str,
) -> dict[str, Any]:
    config = deserialize_config(config_payload)
    config.verbose = False
    if calibration_summary is not None:
        config.mu = float(calibration_summary["derived_mu"])
    runner = ExperimentRunner(config)
    runner.calibration_summary = calibration_summary
    rows = runner.run_replication(
        condition=condition,
        replication=replication,
        seed=seed,
        config_path=config_path,
        config_name=config_name,
        batch_id=batch_id,
    )
    return {
        "task_kind": "primary",
        "condition": condition,
        "replication": int(replication),
        "seed": int(seed),
        "records": rows,
        "cumulative_payoff": float(sum(float(row["payoff"]) for row in rows)),
    }


def run_sensitivity_replication_task(
    config_payload: dict[str, Any],
    *,
    parameter_name: str,
    parameter_value: float,
    condition: int | str,
    replication: int,
    seed: int,
    calibration_summary: dict[str, Any],
    config_path: str,
    config_name: str,
    batch_id: str,
) -> dict[str, Any]:
    config = deserialize_config(config_payload)
    config.verbose = False
    config.mu = float(calibration_summary["derived_mu"])
    runner = ExperimentRunner(config)
    runner.calibration_summary = calibration_summary
    rows = runner.run_sensitivity_replication(
        parameter_name=parameter_name,
        parameter_value=parameter_value,
        condition=condition,
        replication=replication,
        seed=seed,
        config_path=config_path,
        config_name=config_name,
        batch_id=batch_id,
    )
    return {
        "task_kind": "sensitivity",
        "condition": condition,
        "replication": int(replication),
        "seed": int(seed),
        "parameter_name": parameter_name,
        "parameter_value": float(parameter_value),
        "records": rows,
    }
