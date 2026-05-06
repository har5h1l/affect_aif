"""Process-safe worker tasks for experiment execution."""

from __future__ import annotations

from typing import Any

from experiments.trust.runner import ExperimentRunner
from experiments.trust.spec import ExpandedRunSpec, ExperimentSpec


def run_variant_replication_task(
    spec_payload: dict[str, Any],
    run_payload: dict[str, Any],
    *,
    config_path: str,
    config_name: str,
    batch_id: str,
) -> dict[str, Any]:
    spec = ExperimentSpec.from_payload(spec_payload)
    run = ExpandedRunSpec.from_payload(run_payload)
    rows = ExperimentRunner.from_spec(spec).run_replication(
        run=run,
        config_path=config_path,
        config_name=config_name,
        batch_id=batch_id,
    )
    return {
        "task_kind": "variant",
        "hypothesis_id": run.hypothesis_id,
        "experiment_id": run.experiment_id,
        "variant_id": run.variant_id,
        "replication": int(run.replication),
        "seed": int(run.seed),
        "records": rows,
        "cumulative_payoff": float(sum(float(row["payoff"]) for row in rows)),
    }
