"""Parsing helpers for result tables with array-valued CSV cells."""

from __future__ import annotations

import ast
import re
from typing import Any

import numpy as np


def variant_sort_key(value: Any) -> tuple[int, str]:
    if isinstance(value, (int, np.integer)):
        return (0, f"{int(value):04d}")
    return (1, str(value))


def ensure_array(value: Any) -> np.ndarray:
    if isinstance(value, np.ndarray):
        return value.astype(float)
    if isinstance(value, list):
        return np.asarray(value, dtype=float)
    if isinstance(value, str):
        cleaned = re.sub(r"np\.(?:float64|int64)\(([^)]+)\)", r"\1", value)
        cleaned = cleaned.replace("nan", "None")
        parsed = ast.literal_eval(cleaned)
        if isinstance(parsed, (list, tuple)):
            parsed = [np.nan if item is None else item for item in parsed]
        return np.asarray(parsed, dtype=float)
    return np.asarray(value, dtype=float)


def scheduled_switch_targets(value: Any) -> list[int]:
    if value is None:
        return []
    if isinstance(value, float) and np.isnan(value):
        return []
    if isinstance(value, str) and value.strip() in {"", "[]", "nan", "None"}:
        return []
    array = ensure_array(value)
    if array.size == 0:
        return []
    if array.ndim == 0:
        return [int(array.item())] if np.isfinite(array.item()) else []
    return [int(item) for item in array.tolist() if np.isfinite(item)]
