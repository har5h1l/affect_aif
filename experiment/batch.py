"""Batch orchestration for multi-config experiment execution."""

from __future__ import annotations

import json
import os
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from analysis.visualization import build_run_gifs
from cli.common import slugify_name
from experiment.calibration import (
    build_sensitivity_specs,
    serialize_config,
)
from experiment.config import ExperimentConfig
from experiment.constants import SENSITIVITY_CONDITIONS
from experiment.tasks import (
    run_primary_replication_task,
    run_sensitivity_replication_task,
)


def default_batch_id(now: datetime | None = None) -> str:
    timestamp = now or datetime.now()
    return timestamp.strftime("batch_%Y%m%d_%H%M%S")


@dataclass
class ConfigBatchState:
    config_path: str
    config_name: str
    output_dir: Path
    config: ExperimentConfig
    config_payload: dict[str, Any]
    primary_rows: list[dict] = field(default_factory=list)
    sensitivity_rows: list[dict] = field(default_factory=list)
    submitted_primary: int = 0
    completed_primary: int = 0
    submitted_sensitivity: int = 0
    completed_sensitivity: int = 0

    def all_rows(self) -> pd.DataFrame:
        return pd.DataFrame(self.primary_rows + self.sensitivity_rows)


@dataclass
class BatchRunResult:
    batch_id: str
    batch_dir: Path
    config_states: list[ConfigBatchState]
    completion_log: list[dict[str, Any]]


class BatchExperimentRunner:
    """Run multiple configs through a shared worker pool."""

    def __init__(
        self,
        *,
        config_paths: list[str],
        output_root: str,
        batch_id: str | None = None,
        workers: int | None = None,
        make_gifs: bool = False,
        verbose: bool = False,
        checkpoint_interval: int = 1,
    ):
        self.config_paths = [str(Path(path)) for path in config_paths]
        self.output_root = Path(output_root)
        self.batch_id = batch_id or default_batch_id()
        self.batch_dir = self.output_root / self.batch_id
        self.workers = max(1, int(workers or os.cpu_count() or 1))
        self.make_gifs = bool(make_gifs)
        self.verbose = bool(verbose)
        self.checkpoint_interval = max(1, int(checkpoint_interval))
        self.completion_log: list[dict[str, Any]] = []

    def _emit(self, message: str):
        if self.verbose:
            print(message, flush=True)

    def _unique_config_dirs(self) -> list[tuple[str, Path]]:
        seen: dict[str, int] = {}
        resolved: list[tuple[str, Path]] = []
        for config_path in self.config_paths:
            stem = slugify_name(Path(config_path).stem)
            count = seen.get(stem, 0)
            seen[stem] = count + 1
            name = stem if count == 0 else f"{stem}_{count + 1}"
            resolved.append((name, self.batch_dir / name))
        return resolved

    def _load_states(self) -> list[ConfigBatchState]:
        states: list[ConfigBatchState] = []
        for config_path, (config_name, output_dir) in zip(
            self.config_paths,
            self._unique_config_dirs(),
            strict=True,
        ):
            config = ExperimentConfig.from_json(config_path)
            config.verbose = False
            config.gif_after_run = False
            config.gif_output_dir = None
            states.append(
                ConfigBatchState(
                    config_path=config_path,
                    config_name=config_name,
                    output_dir=output_dir,
                    config=config,
                    config_payload=serialize_config(config),
                )
            )
        return states

    def _schedule_config_work(
        self,
        executor: ProcessPoolExecutor,
        state: ConfigBatchState,
        future_map: dict[Any, tuple[str, ConfigBatchState, dict[str, Any]]],
    ):
        configured_conditions = list(state.config.conditions) + list(state.config.presets)
        sensitivity_conditions = [
            condition
            for condition in configured_conditions
            if isinstance(condition, int) and condition in SENSITIVITY_CONDITIONS
        ]
        for condition in configured_conditions:
            for replication in range(state.config.num_replications):
                seed = state.config.random_seed + replication
                future = executor.submit(
                    run_primary_replication_task,
                    state.config_payload,
                    condition=condition,
                    replication=replication,
                    seed=seed,
                    config_path=state.config_path,
                    config_name=state.config_name,
                    batch_id=self.batch_id,
                )
                state.submitted_primary += 1
                future_map[future] = (
                    "primary",
                    state,
                    {"condition": condition, "replication": replication, "seed": seed},
                )
        if state.config.run_sensitivity:
            for parameter_name, parameter_value in build_sensitivity_specs(state.config):
                for condition in sensitivity_conditions:
                    for replication in range(state.config.num_replications):
                        seed = state.config.random_seed + replication
                        future = executor.submit(
                            run_sensitivity_replication_task,
                            state.config_payload,
                            parameter_name=parameter_name,
                            parameter_value=parameter_value,
                            condition=condition,
                            replication=replication,
                            seed=seed,
                            config_path=state.config_path,
                            config_name=state.config_name,
                            batch_id=self.batch_id,
                        )
                        state.submitted_sensitivity += 1
                        future_map[future] = (
                            "sensitivity",
                            state,
                            {
                                "condition": condition,
                                "replication": replication,
                                "seed": seed,
                                "parameter_name": parameter_name,
                                "parameter_value": parameter_value,
                            },
                        )

    def _write_checkpoint(self, state: ConfigBatchState):
        """Save partial results for a config so progress survives crashes."""
        state.output_dir.mkdir(parents=True, exist_ok=True)
        partial = state.all_rows()
        if not partial.empty:
            partial.to_csv(state.output_dir / "results_partial.csv", index=False)
            self._emit(
                f"[batch={self.batch_id}] checkpoint config={state.config_name} "
                f"{state.completed_primary}/{state.submitted_primary} primary"
            )

    def _write_config_outputs(self, state: ConfigBatchState):
        state.output_dir.mkdir(parents=True, exist_ok=True)
        results = state.all_rows()
        results_path = state.output_dir / "results.csv"
        config_copy_path = state.output_dir / "config.json"
        metadata_path = state.output_dir / "batch_metadata.json"
        results.to_csv(results_path, index=False)
        state.config.to_json(str(config_copy_path))
        metadata = {
            "batch_id": self.batch_id,
            "config_path": state.config_path,
            "config_name": state.config_name,
            "results_path": str(results_path),
            "workers": self.workers,
            "primary_tasks": state.submitted_primary,
            "sensitivity_tasks": state.submitted_sensitivity,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2))
        if self.make_gifs and not results.empty:
            build_run_gifs(results, str(state.output_dir / "gifs"))

    def run_all(self) -> BatchRunResult:
        states = self._load_states()
        self.batch_dir.mkdir(parents=True, exist_ok=True)
        future_map: dict[Any, tuple[str, ConfigBatchState, dict[str, Any]]] = {}

        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            for state in states:
                self._schedule_config_work(executor, state, future_map)

            while future_map:
                done, _ = wait(list(future_map.keys()), return_when=FIRST_COMPLETED)
                for future in done:
                    task_kind, state, metadata = future_map.pop(future)
                    payload = future.result()
                    if task_kind == "primary":
                        state.completed_primary += 1
                        state.primary_rows.extend(payload["records"])
                        self.completion_log.append(
                            {
                                "task_kind": "primary",
                                "config_name": state.config_name,
                                "condition": payload["condition"],
                                "replication": int(payload["replication"]),
                            }
                        )
                        self._emit(
                            f"[batch={self.batch_id}] primary complete config={state.config_name} "
                            f"condition={payload['condition']} replication={int(payload['replication']) + 1}/"
                            f"{state.config.num_replications}"
                        )
                        if state.completed_primary % self.checkpoint_interval == 0:
                            self._write_checkpoint(state)
                    elif task_kind == "sensitivity":
                        state.completed_sensitivity += 1
                        state.sensitivity_rows.extend(payload["records"])
                        self.completion_log.append(
                            {
                                "task_kind": "sensitivity",
                                "config_name": state.config_name,
                                "condition": payload["condition"],
                                "replication": int(payload["replication"]),
                                "parameter_name": str(payload["parameter_name"]),
                            }
                        )

        for state in states:
            self._write_config_outputs(state)

        return BatchRunResult(
            batch_id=self.batch_id,
            batch_dir=self.batch_dir,
            config_states=states,
            completion_log=self.completion_log,
        )


__all__ = ["BatchExperimentRunner", "BatchRunResult", "default_batch_id"]
