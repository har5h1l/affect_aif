"""Environment-agnostic metrics for cross-environment comparison.

All functions operate on pandas DataFrames with the standard result schema
(columns: agent_action, partner_action, payoff, true_partner_type, partner_idx,
inferred_type_correct, round, condition, seed).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def cooperation_rate(results: pd.DataFrame, group_by: str | list[str] | None = None) -> pd.DataFrame | float:
    """Fraction of rounds where agent cooperated (action=0).

    If group_by is provided, returns a DataFrame with cooperation rate per group.
    Otherwise returns a single float.
    """
    if group_by is not None:
        return (
            results.groupby(group_by)["agent_action"]
            .apply(lambda s: float((s == 0).mean()))
            .rename("cooperation_rate")
            .reset_index()
        )
    return float((results["agent_action"] == 0).mean())


def cumulative_payoff(results: pd.DataFrame, group_by: str | list[str] | None = None) -> pd.DataFrame | float:
    """Total payoff accumulated over the episode.

    If group_by is provided, returns a DataFrame with cumulative payoff per group.
    """
    if group_by is not None:
        return results.groupby(group_by)["payoff"].sum().rename("cumulative_payoff").reset_index()
    return float(results["payoff"].sum())


def type_identification_accuracy(
    results: pd.DataFrame, group_by: str | list[str] | None = None
) -> pd.DataFrame | float:
    """Fraction of rounds where agent correctly identified partner type.

    Requires 'inferred_type_correct' column in results.
    """
    if "inferred_type_correct" not in results.columns:
        return np.nan
    if group_by is not None:
        return results.groupby(group_by)["inferred_type_correct"].mean().rename("type_id_accuracy").reset_index()
    return float(results["inferred_type_correct"].mean())


def adaptation_speed(
    results: pd.DataFrame,
    switch_round: int,
    accuracy_threshold: float = 0.8,
    window: int = 5,
) -> float:
    """Rounds after a type switch to recover identification accuracy.

    Measures how quickly the agent adapts after a partner type switch at
    `switch_round`. Returns the number of rounds until a rolling window
    of `window` rounds achieves `accuracy_threshold` accuracy.
    Returns np.nan if the threshold is never reached.
    """
    if "inferred_type_correct" not in results.columns:
        return np.nan

    post_switch = results[results["round"] >= switch_round].copy()
    if len(post_switch) < window:
        return np.nan

    rolling_acc = post_switch["inferred_type_correct"].rolling(window).mean()
    recovered = rolling_acc[rolling_acc >= accuracy_threshold]
    if recovered.empty:
        return np.nan

    first_recovery_idx = recovered.index[0]
    recovery_round = int(post_switch.loc[first_recovery_idx, "round"])
    return float(recovery_round - switch_round)


def partner_discrimination(results: pd.DataFrame) -> float:
    """Difference in cooperation rate toward cooperators vs exploiters.

    Measures whether the agent treats different partner types differently.
    Higher values indicate better discrimination. Returns np.nan if both
    types are not present.
    """
    if "true_partner_type" not in results.columns:
        return np.nan

    by_type = results.groupby("true_partner_type")["agent_action"].apply(lambda s: float((s == 0).mean()))

    coop_types = [t for t in by_type.index if "cooperat" in t.lower()]
    exploit_types = [t for t in by_type.index if "exploit" in t.lower()]

    if not coop_types or not exploit_types:
        return np.nan

    coop_rate_with_cooperators = float(np.mean([by_type[t] for t in coop_types]))
    coop_rate_with_exploiters = float(np.mean([by_type[t] for t in exploit_types]))

    return coop_rate_with_cooperators - coop_rate_with_exploiters


def mean_payoff(results: pd.DataFrame, group_by: str | list[str] | None = None) -> pd.DataFrame | float:
    """Average payoff per round."""
    if group_by is not None:
        return results.groupby(group_by)["payoff"].mean().rename("mean_payoff").reset_index()
    return float(results["payoff"].mean())


def social_welfare(results: pd.DataFrame) -> float:
    """Sum of agent + partner payoffs (joint welfare)."""
    if "partner_payoff" not in results.columns:
        return np.nan
    return float((results["payoff"] + results["partner_payoff"]).sum())


def environment_transfer_gap(
    trust_results: pd.DataFrame,
    grid_results: pd.DataFrame,
    metric_fn=None,
) -> pd.DataFrame:
    """Compare a metric across trust game and gridworld results by condition.

    Returns a DataFrame with columns: condition, trust_game, gridworld, gap.
    """
    if metric_fn is None:
        metric_fn = mean_payoff

    trust_metrics = metric_fn(trust_results, group_by="condition")
    grid_metrics = metric_fn(grid_results, group_by="condition")

    metric_col = [c for c in trust_metrics.columns if c != "condition"][0]

    merged = trust_metrics.merge(grid_metrics, on="condition", suffixes=("_trust", "_grid"))
    trust_col = f"{metric_col}_trust"
    grid_col = f"{metric_col}_grid"
    merged["gap"] = merged[trust_col] - merged[grid_col]
    return merged


def relative_ranking_preservation(
    trust_results: pd.DataFrame,
    grid_results: pd.DataFrame,
    metric_fn=None,
) -> float:
    """Spearman rank correlation of condition performance across environments.

    Returns 1.0 if agents rank identically in both environments, -1.0 if reversed.
    """
    from scipy import stats

    if metric_fn is None:
        metric_fn = mean_payoff

    trust_metrics = metric_fn(trust_results, group_by="condition")
    grid_metrics = metric_fn(grid_results, group_by="condition")

    metric_col = [c for c in trust_metrics.columns if c != "condition"][0]

    merged = trust_metrics.merge(grid_metrics, on="condition", suffixes=("_trust", "_grid"))
    if len(merged) < 3:
        return np.nan

    corr, _ = stats.spearmanr(
        merged[f"{metric_col}_trust"],
        merged[f"{metric_col}_grid"],
    )
    return float(corr)
