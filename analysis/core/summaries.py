"""Summary helpers for configured analyses."""

from __future__ import annotations

import pandas as pd

from analysis.metrics import affective_movement_summary, final_round_summary


def final_round(results: pd.DataFrame) -> pd.DataFrame:
    return final_round_summary(results)


def affective_movement(results: pd.DataFrame) -> pd.DataFrame:
    return affective_movement_summary(results)
