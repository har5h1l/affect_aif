"""Plot helpers for configured analyses."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from analysis.plots import save_all_figures


def save_figures(results: pd.DataFrame, output_dir: str | Path) -> None:
    save_all_figures(results, str(output_dir))
