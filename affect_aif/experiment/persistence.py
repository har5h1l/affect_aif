"""Result annotation and persistence helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from affect_aif.experiment.conditions import resolve_condition_spec
from affect_aif.experiment.config import ExperimentConfig


def annotate_primary_records(
    rows: list[dict],
    *,
    condition: int | str,
    config: ExperimentConfig,
    calibration_summary: dict | None,
    config_path: str | None = None,
    config_name: str | None = None,
    batch_id: str | None = None,
) -> list[dict]:
    for row in rows:
        row["condition_name"] = resolve_condition_spec(condition).name
        if calibration_summary is not None:
            row["mu_source"] = "derived"
            row["calibration_mean_abs_efe_per_step"] = calibration_summary["mean_abs_efe_per_step"]
            row["derived_mu"] = calibration_summary["derived_mu"]
        else:
            row["mu_source"] = "not_required"
            row["calibration_mean_abs_efe_per_step"] = np.nan
            row["derived_mu"] = np.nan
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
