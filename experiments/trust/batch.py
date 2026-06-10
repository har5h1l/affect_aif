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
from experiments.trust.runner import checkpoint_group_complete, checkpoint_rows_for_completed_keys
from experiments.trust.spec import ExpandedRunSpec, ExperimentSpec, load_experiment_specs
from experiments.trust.tasks import run_variant_replication_task


def default_batch_id(now: datetime | None = None) -> str:
    timestamp = now or datetime.now()
    return timestamp.strftime("batch_%Y%m%d_%H%M%S")


@dataclass
class ConfigBatchState:
    config_path: str
    config_name: str
    output_dir: Path
    spec: ExperimentSpec
    spec_payload: dict[str, Any]
    expanded_runs: list[ExpandedRunSpec] = field(default_factory=list)
    primary_rows: list[dict] = field(default_factory=list)
    submitted_primary: int = 0
    completed_primary: int = 0
    resumed_primary: int = 0

    def all_rows(self) -> pd.DataFrame:
        return pd.DataFrame(self.primary_rows)


def _run_key_from_values(variant_id: Any, seed: Any, replication: Any) -> tuple[str, int, int]:
    return (str(variant_id), int(seed), int(replication))


def _run_key(run: ExpandedRunSpec) -> tuple[str, int, int]:
    return _run_key_from_values(run.variant_id, run.seed, run.replication)


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

    def _load_states(self) -> list[ConfigBatchState]:
        states: list[ConfigBatchState] = []
        for config_path in self.config_paths:
            path = Path(config_path)
            for spec in load_experiment_specs(path):
                states.append(
                    ConfigBatchState(
                        config_path=config_path,
                        config_name=spec.experiment.id,
                        output_dir=self.batch_dir / spec.hypothesis.id / spec.experiment.id,
                        spec=spec,
                        spec_payload=spec.to_payload(),
                        expanded_runs=spec.expand_runs(),
                    )
                )
        return states

    def _load_checkpoint(self, state: ConfigBatchState) -> set[tuple[str, int, int]]:
        partial_path = state.output_dir / "results_partial.csv"
        if not partial_path.exists():
            return set()
        partial = pd.read_csv(partial_path, low_memory=False)
        required = {"variant_id", "seed", "replication", "round"}
        if partial.empty or not required <= set(partial.columns):
            return set()

        expected_rounds = {_run_key(run): int(run.rounds) for run in state.expanded_runs}
        completed_keys: set[tuple[str, int, int]] = set()
        for values, group in partial.groupby(["variant_id", "seed", "replication"], dropna=False):
            key = _run_key_from_values(*values)
            expected = expected_rounds.get(key)
            if expected is None:
                continue
            if checkpoint_group_complete(group, expected):
                completed_keys.add(key)

        if not completed_keys:
            return set()
        resumed = checkpoint_rows_for_completed_keys(partial, completed_keys)
        state.primary_rows.extend(resumed.to_dict(orient="records"))
        state.completed_primary += len(completed_keys)
        state.resumed_primary += len(completed_keys)
        self._write_checkpoint_manifest(state, completed_keys)
        self._emit(
            f"[batch={self.batch_id}] resumed config={state.config_name} "
            f"{len(completed_keys)}/{len(state.expanded_runs)} primary"
        )
        return completed_keys

    def _schedule_config_work(
        self,
        executor: ProcessPoolExecutor,
        state: ConfigBatchState,
        future_map: dict[Any, tuple[str, ConfigBatchState, dict[str, Any]]],
    ):
        completed_keys = self._load_checkpoint(state)
        for run in state.expanded_runs:
            if _run_key(run) in completed_keys:
                continue
            future = executor.submit(
                run_variant_replication_task,
                state.spec_payload,
                run.to_payload(),
                config_path=state.config_path,
                config_name=state.config_name,
                batch_id=self.batch_id,
            )
            state.submitted_primary += 1
            future_map[future] = (
                "variant",
                state,
                {"variant_id": run.variant_id, "replication": run.replication, "seed": run.seed},
            )

    def _write_checkpoint_manifest(
        self,
        state: ConfigBatchState,
        completed_keys: set[tuple[str, int, int]] | None = None,
    ):
        completed = sorted(
            completed_keys
            or {
                _run_key_from_values(row["variant_id"], row["seed"], row["replication"])
                for row in state.primary_rows
            }
        )
        manifest = {
            "batch_id": self.batch_id,
            "config_name": state.config_name,
            "hypothesis_id": state.spec.hypothesis.id,
            "experiment_id": state.spec.experiment.id,
            "completed_tasks": [
                {"variant_id": variant_id, "seed": seed, "replication": replication}
                for variant_id, seed, replication in completed
            ],
        }
        state.output_dir.mkdir(parents=True, exist_ok=True)
        (state.output_dir / "checkpoint_manifest.json").write_text(json.dumps(manifest, indent=2))

    def _write_checkpoint(self, state: ConfigBatchState):
        """Save partial results for a config so progress survives crashes."""
        state.output_dir.mkdir(parents=True, exist_ok=True)
        partial = state.all_rows()
        if not partial.empty:
            partial.to_csv(state.output_dir / "results_partial.csv", index=False)
            self._write_checkpoint_manifest(state)
            self._emit(
                f"[batch={self.batch_id}] checkpoint config={state.config_name} "
                f"{state.completed_primary}/{state.submitted_primary} primary"
            )

    def _write_config_outputs(self, state: ConfigBatchState):
        state.output_dir.mkdir(parents=True, exist_ok=True)
        results = state.all_rows()
        results_path = state.output_dir / "results.csv"
        config_copy_path = state.output_dir / "config.toml"
        metadata_path = state.output_dir / "batch_metadata.json"
        results.to_csv(results_path, index=False)
        config_copy_path.write_text(Path(state.config_path).read_text(encoding="utf-8"), encoding="utf-8")
        metadata = {
            "batch_id": self.batch_id,
            "config_path": state.config_path,
            "config_name": state.config_name,
            "results_path": str(results_path),
            "workers": self.workers,
            "primary_tasks": state.submitted_primary,
            "sensitivity_tasks": 0,
            "hypothesis_id": state.spec.hypothesis.id,
            "experiment_id": state.spec.experiment.id,
            "expanded_runs": len(state.expanded_runs),
            "resumed_tasks": state.resumed_primary,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2))
        if self.make_gifs and not results.empty:
            build_run_gifs(results, str(state.output_dir / "gifs"))
        if state.spec.analysis.auto:
            from analysis.configured import run_configured_analysis

            run_configured_analysis(state.spec, results_path, state.output_dir)

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
                    if task_kind == "variant":
                        state.completed_primary += 1
                        state.primary_rows.extend(payload["records"])
                        self.completion_log.append(
                            {
                                "task_kind": "variant",
                                "config_name": state.config_name,
                                "variant_id": payload["variant_id"],
                                "replication": int(payload["replication"]),
                            }
                        )
                        self._emit(
                            f"[batch={self.batch_id}] variant complete config={state.config_name} "
                            f"variant={payload['variant_id']} replication={int(payload['replication']) + 1}/"
                            f"{state.spec.experiment.replications}"
                        )
                        if state.completed_primary % self.checkpoint_interval == 0:
                            self._write_checkpoint(state)

        for state in states:
            self._write_config_outputs(state)

        return BatchRunResult(
            batch_id=self.batch_id,
            batch_dir=self.batch_dir,
            config_states=states,
            completion_log=self.completion_log,
        )


__all__ = ["BatchExperimentRunner", "BatchRunResult", "default_batch_id"]
