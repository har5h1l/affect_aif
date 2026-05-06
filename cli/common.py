"""Shared utilities for supported CLI entry points."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


def slugify_name(text: str) -> str:
    """Convert user-facing names to stable path-friendly slugs."""

    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "run"


def normalize_results_table(results: pd.DataFrame) -> pd.DataFrame:
    """Normalize loaded variant-shaped results."""

    frame = results.copy()
    if "variant_id" in frame.columns:
        frame["variant_id"] = frame["variant_id"].astype(str)
    return frame


def load_results_table(path: str | Path) -> pd.DataFrame:
    """Load a results table from CSV or parquet."""

    source = Path(path)
    if source.suffix == ".parquet":
        return normalize_results_table(pd.read_parquet(source))
    return normalize_results_table(pd.read_csv(source, low_memory=False))


def filter_primary_runs(results: pd.DataFrame) -> pd.DataFrame:
    """Return results unchanged; TOML specs emit only primary variant runs."""

    return results
