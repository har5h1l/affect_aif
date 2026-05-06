"""Windowed analysis helpers shared by configured analyses."""

from __future__ import annotations

import pandas as pd

from analysis.metrics import post_switch_window_summary


def post_switch_windows(results: pd.DataFrame, windows: tuple[int, ...] = (5, 10)) -> dict[int, pd.DataFrame]:
    """Return post-switch summaries keyed by inclusive encounter window."""

    return {window: post_switch_window_summary(results, window=window) for window in windows}
