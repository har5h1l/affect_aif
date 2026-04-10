"""Result annotation and persistence helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from experiment.conditions import resolve_condition_spec
from experiment.config import ExperimentConfig


def annotate_primary_records(
    rows: list[dict],
    *,
    condition: int | str,
    config: ExperimentConfig,
    config_path: str | None = None,
    config_name: str | None = None,
    batch_id: str | None = None,
) -> list[dict]:
    for row in rows:
        row["condition_name"] = resolve_condition_spec(condition).name
        row["run_mode"] = "primary"
        row["config_path"] = config_path or np.nan
        row["config_name"] = config_name or config.experiment_name
        row["batch_id"] = batch_id or np.nan
    return rows


def save_results(results: pd.DataFrame, path: str | Path):
    """Persist results to CSV or parquet."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix == ".parquet":
        results.to_parquet(target, index=False)
        return
    results.to_csv(target, index=False)
