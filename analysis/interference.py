"""Cross-partner interference summaries for locality ablations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.metrics import (
    _ensure_array,
    _safe_entropy,
    _safe_nanmean,
    _safe_range,
    _scheduled_switch_targets,
    _stack_beta_rows,
)


def cross_partner_interference_summary(results: pd.DataFrame, *, post_window: int = 10) -> pd.DataFrame:
    """Summarize switched-vs-untouched partner behavior after a scheduled switch."""

    required = {"variant_id", "seed", "round", "selected_partner", "payoff", "q_pi_entropy"}
    if not required.issubset(results.columns) or "scheduled_stance_switch_partner_ids" not in results.columns:
        return pd.DataFrame()

    frame = results.copy()
    frame["_scheduled_stance_targets"] = frame["scheduled_stance_switch_partner_ids"].apply(_scheduled_switch_targets)
    switch_rows = frame.loc[frame["_scheduled_stance_targets"].apply(bool)]
    rows: list[dict] = []
    for (variant_id, seed), group in frame.groupby(["variant_id", "seed"], sort=False):
        group = group.sort_values("round")
        scheduled = switch_rows.loc[
            (switch_rows["variant_id"] == variant_id) & (switch_rows["seed"] == seed)
        ]
        if scheduled.empty:
            continue
        switch_round = int(scheduled.iloc[0]["round"])
        switched_partner = int(scheduled.iloc[0]["_scheduled_stance_targets"][0])
        pre = group.loc[group["round"] < switch_round]
        post = group.loc[(group["round"] >= switch_round) & (group["round"] < switch_round + int(post_window))]
        switched_post = post.loc[post["selected_partner"].astype(int) == switched_partner]
        untouched_post = post.loc[post["selected_partner"].astype(int) != switched_partner]
        rows.append(
            {
                "variant_id": variant_id,
                "seed": int(seed),
                "switch_round": switch_round,
                "switched_partner": switched_partner,
                "post_window": int(post_window),
                "pre_selection_entropy": _safe_entropy(pre["selected_partner"].value_counts().to_numpy()),
                "post_selection_entropy": _safe_entropy(post["selected_partner"].value_counts().to_numpy()),
                "switched_post_encounters": int(len(switched_post)),
                "untouched_post_encounters": int(len(untouched_post)),
                "switched_post_mean_payoff": float(switched_post["payoff"].mean()) if len(switched_post) else np.nan,
                "untouched_post_mean_payoff": float(untouched_post["payoff"].mean()) if len(untouched_post) else np.nan,
                "switched_post_mean_entropy": (
                    float(switched_post["q_pi_entropy"].mean()) if len(switched_post) else np.nan
                ),
                "untouched_post_mean_entropy": (
                    float(untouched_post["q_pi_entropy"].mean()) if len(untouched_post) else np.nan
                ),
                "untouched_selection_rate": float(len(untouched_post) / len(post)) if len(post) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def global_vs_local_beta_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize global beta and vector beta ranges by variant and seed."""

    if "variant_id" not in results.columns or "seed" not in results.columns:
        return pd.DataFrame()
    rows: list[dict] = []
    for (variant_id, seed), group in results.groupby(["variant_id", "seed"], sort=False):
        row = {"variant_id": variant_id, "seed": int(seed)}
        if "global_beta" in group.columns:
            values = pd.to_numeric(group["global_beta"], errors="coerce")
            finite = values[np.isfinite(values)]
            row["global_beta_mean"] = float(finite.mean()) if len(finite) else np.nan
            row["global_beta_range"] = float(finite.max() - finite.min()) if len(finite) else np.nan
        vector_column = (
            "local_betas"
            if "local_betas" in group.columns
            else "betas"
            if "betas" in group.columns
            else None
        )
        if vector_column is not None:
            beta_stack = _stack_beta_rows(group[vector_column].apply(_ensure_array))
            if beta_stack.size:
                temporal_ranges = np.asarray(
                    [_safe_range(beta_stack[:, idx]) for idx in range(beta_stack.shape[1])],
                    dtype=float,
                )
                finite_ranges = temporal_ranges[np.isfinite(temporal_ranges)]
                row["vector_beta_mean"] = _safe_nanmean(beta_stack.ravel())
                row["vector_beta_mean_range"] = _safe_nanmean(temporal_ranges)
                row["vector_beta_max_range"] = float(finite_ranges.max()) if finite_ranges.size else np.nan
        rows.append(row)
    return pd.DataFrame(rows)
