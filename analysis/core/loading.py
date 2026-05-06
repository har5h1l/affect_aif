"""Loading helpers for configured analyses."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_configured_results(results_path: str | Path) -> pd.DataFrame:
    """Load CSV/parquet results."""

    path = Path(results_path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)
