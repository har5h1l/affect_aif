"""Shared utilities for supported CLI entry points."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def slugify_name(text: str) -> str:
    """Convert user-facing names to stable path-friendly slugs."""

    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "run"


def load_results_table(path: str | Path) -> pd.DataFrame:
    """Load a results table from CSV or parquet."""

    source = Path(path)
    if source.suffix == ".parquet":
        return pd.read_parquet(source)
    return pd.read_csv(source)


def filter_primary_runs(results: pd.DataFrame) -> pd.DataFrame:
    """Restrict a results table to primary runs when the run-mode column exists."""

    if "run_mode" not in results.columns:
        return results
    primary = results[results["run_mode"] == "primary"].copy()
    return primary if not primary.empty else results
