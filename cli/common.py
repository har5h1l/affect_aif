"""Shared utilities for supported CLI entry points."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def slugify_name(text: str) -> str:
    """Convert user-facing names to stable path-friendly slugs."""

    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "run"


def _normalize_condition_value(value):
    """Canonicalize mixed numeric/string condition identifiers from CSV loads."""

    if pd.isna(value):
        return value
    text = str(value).strip()
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def normalize_results_table(results: pd.DataFrame) -> pd.DataFrame:
    """Normalize loaded results so mixed condition ids do not fragment analysis groups."""

    frame = results.copy()
    if "condition" in frame.columns:
        frame["condition"] = frame["condition"].map(_normalize_condition_value)
    if "condition_name" in frame.columns:
        frame["condition_name"] = frame["condition_name"].astype(str)
    return frame


def load_results_table(path: str | Path) -> pd.DataFrame:
    """Load a results table from CSV or parquet."""

    source = Path(path)
    if source.suffix == ".parquet":
        return normalize_results_table(pd.read_parquet(source))
    return normalize_results_table(pd.read_csv(source, low_memory=False))


def filter_primary_runs(results: pd.DataFrame) -> pd.DataFrame:
    """Restrict a results table to primary runs when the run-mode column exists."""

    if "run_mode" not in results.columns:
        return results
    primary = results[results["run_mode"] == "primary"].copy()
    return primary if not primary.empty else results
