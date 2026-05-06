"""Basic statistical summaries for experiment outputs."""

from __future__ import annotations

from itertools import combinations

import pandas as pd
from scipy import stats

from analysis.metrics import final_round_summary


def _variant_value(value):
    return value.item() if hasattr(value, "item") else value


def cumulative_payoff_anova(results: pd.DataFrame) -> dict:
    """One-way ANOVA over total payoff by variant."""

    summary = final_round_summary(results)
    grouped = [group["total_payoff"].to_numpy() for _, group in summary.groupby("variant_id")]
    if len(grouped) < 2 or any(len(group) < 2 for group in grouped):
        return {"f_stat": float("nan"), "p_value": float("nan")}
    f_stat, p_value = stats.f_oneway(*grouped)
    return {"f_stat": float(f_stat), "p_value": float(p_value)}


def pairwise_payoff_tests(results: pd.DataFrame) -> pd.DataFrame:
    """Pairwise Welch t-tests over total payoff."""

    summary = final_round_summary(results)
    records = []
    for (variant_a, frame_a), (variant_b, frame_b) in combinations(summary.groupby("variant_id"), 2):
        if len(frame_a) < 2 or len(frame_b) < 2:
            t_stat, p_value = float("nan"), float("nan")
        else:
            t_stat, p_value = stats.ttest_ind(frame_a["total_payoff"], frame_b["total_payoff"], equal_var=False)
        records.append(
            {
                "variant_a": _variant_value(variant_a),
                "variant_b": _variant_value(variant_b),
                "t_stat": float(t_stat),
                "p_value": float(p_value),
            }
        )
    return pd.DataFrame(records)
