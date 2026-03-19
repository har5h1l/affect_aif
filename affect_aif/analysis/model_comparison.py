"""Bayesian model comparison via predictive log-likelihoods and Bayes factors."""

from __future__ import annotations

import math
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats


def cumulative_log_likelihood(results: pd.DataFrame) -> pd.DataFrame:
    """Compute cumulative predictive log-likelihood per condition per seed.

    Each round's ``predictive_log_lik`` is the log probability the agent's model
    assigned to the actually observed partner action *before* seeing it.  Summing
    across rounds gives the total log model evidence for that episode.
    """
    if "predictive_log_lik" not in results.columns:
        raise ValueError("Results must contain 'predictive_log_lik' column. Re-run experiments with updated runner.")

    frame = results.sort_values(["condition", "seed", "round"]).copy()
    frame["predictive_log_lik"] = pd.to_numeric(frame["predictive_log_lik"], errors="coerce")

    grouped = frame.groupby(["condition", "condition_name", "seed"], as_index=False).agg(
        cumulative_log_lik=("predictive_log_lik", "sum"),
        num_rounds=("predictive_log_lik", "count"),
        mean_log_lik_per_round=("predictive_log_lik", "mean"),
    )
    return grouped


def pairwise_bayes_factors(log_lik_summary: pd.DataFrame) -> pd.DataFrame:
    """Compute pairwise log Bayes factors between all condition pairs.

    For each seed, log BF(A vs B) = cumulative_log_lik_A - cumulative_log_lik_B.
    We report the mean and SE across seeds, plus a one-sample t-test against zero.

    Interpretation (Kass & Raftery 1995):
      |log10 BF| < 0.5  : not worth more than a bare mention
      0.5 - 1.0         : substantial
      1.0 - 2.0         : strong
      > 2.0             : decisive
    """
    records = []
    conditions = sorted(log_lik_summary["condition"].unique())

    for cond_a, cond_b in combinations(conditions, 2):
        seeds_a = log_lik_summary[log_lik_summary["condition"] == cond_a].set_index("seed")
        seeds_b = log_lik_summary[log_lik_summary["condition"] == cond_b].set_index("seed")
        common_seeds = seeds_a.index.intersection(seeds_b.index)
        if len(common_seeds) < 2:
            continue

        log_bf = (
            seeds_a.loc[common_seeds, "cumulative_log_lik"].values
            - seeds_b.loc[common_seeds, "cumulative_log_lik"].values
        )
        mean_log_bf = float(np.mean(log_bf))
        se_log_bf = float(np.std(log_bf, ddof=1) / np.sqrt(len(log_bf)))
        # Convert to log10 for Kass-Raftery scale
        mean_log10_bf = mean_log_bf / np.log(10)

        t_stat, p_value = stats.ttest_1samp(log_bf, 0.0)

        name_a = seeds_a["condition_name"].iloc[0] if "condition_name" in seeds_a.columns else str(cond_a)
        name_b = seeds_b["condition_name"].iloc[0] if "condition_name" in seeds_b.columns else str(cond_b)

        strength = _kass_raftery_strength(abs(mean_log10_bf))

        records.append({
            "condition_a": int(cond_a),
            "condition_b": int(cond_b),
            "name_a": str(name_a),
            "name_b": str(name_b),
            "n_seeds": int(len(common_seeds)),
            "mean_log_bf_nats": mean_log_bf,
            "se_log_bf_nats": se_log_bf,
            "mean_log10_bf": mean_log10_bf,
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "strength": strength,
            "favors": str(name_a) if mean_log_bf > 0 else str(name_b),
        })

    return pd.DataFrame(records)


def model_ranking(log_lik_summary: pd.DataFrame) -> pd.DataFrame:
    """Rank models by mean cumulative log-likelihood across seeds."""
    ranking = (
        log_lik_summary
        .groupby(["condition", "condition_name"], as_index=False)
        .agg(
            mean_cumulative_log_lik=("cumulative_log_lik", "mean"),
            se_cumulative_log_lik=("cumulative_log_lik", lambda x: float(np.std(x, ddof=1) / np.sqrt(len(x)))),
            mean_log_lik_per_round=("mean_log_lik_per_round", "mean"),
            n_seeds=("seed", "count"),
        )
        .sort_values("mean_cumulative_log_lik", ascending=False)
        .reset_index(drop=True)
    )
    ranking["rank"] = range(1, len(ranking) + 1)
    # Relative to best model
    best = ranking["mean_cumulative_log_lik"].iloc[0]
    ranking["delta_from_best_nats"] = ranking["mean_cumulative_log_lik"] - best
    ranking["delta_from_best_log10"] = ranking["delta_from_best_nats"] / np.log(10)
    return ranking


def _kass_raftery_strength(abs_log10_bf: float) -> str:
    """Classify Bayes factor strength on the Kass & Raftery (1995) scale."""
    if abs_log10_bf < 0.5:
        return "negligible"
    if abs_log10_bf < 1.0:
        return "substantial"
    if abs_log10_bf < 2.0:
        return "strong"
    return "decisive"


def format_comparison_report(
    ranking: pd.DataFrame,
    bayes_factors: pd.DataFrame,
) -> str:
    """Format a human-readable model comparison report."""
    lines = ["# Bayesian Model Comparison Report", ""]
    lines.append("## Model Ranking (by predictive log-likelihood)")
    lines.append("")
    for _, row in ranking.iterrows():
        lines.append(
            f"  {row['rank']}. **{row['condition_name']}** (C{row['condition']}): "
            f"mean LL = {row['mean_cumulative_log_lik']:.1f} ± {row['se_cumulative_log_lik']:.1f} "
            f"(Δ = {row['delta_from_best_log10']:.2f} log₁₀)"
        )
    lines.append("")

    lines.append("## Pairwise Bayes Factors")
    lines.append("")
    for _, row in bayes_factors.iterrows():
        direction = ">" if row["mean_log_bf_nats"] > 0 else "<"
        lines.append(
            f"  {row['name_a']} vs {row['name_b']}: "
            f"log₁₀ BF = {row['mean_log10_bf']:+.2f} ({row['strength']}), "
            f"favors **{row['favors']}**, "
            f"t({row['n_seeds']-1}) = {row['t_stat']:.2f}, p = {row['p_value']:.4f}"
        )
    lines.append("")
    return "\n".join(lines)
