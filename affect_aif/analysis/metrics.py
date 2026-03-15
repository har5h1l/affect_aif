"""Derived metrics for experiment results."""

from __future__ import annotations

import ast
import re

import numpy as np
import pandas as pd


def _ensure_array(value) -> np.ndarray:
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


def _safe_nanmean(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    if np.isnan(values).all():
        return np.nan
    return float(np.nanmean(values))


def final_round_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate final cumulative payoff and identification accuracy per seed and condition."""

    frame = results.sort_values(["condition", "seed", "round"]).copy()
    grouped = frame.groupby(["condition", "condition_name", "seed"], as_index=False).agg(
        total_payoff=("payoff", "sum"),
        mean_accuracy=("inferred_type_correct", "mean"),
        mean_q_pi_entropy=("q_pi_entropy", "mean"),
        mean_abs_step_efe=("mean_abs_step_efe", "mean"),
        planning_cost=("planning_cost", "first"),
        planning_cost_ratio=("planning_cost_ratio", "first"),
        mu=("mu", "first"),
    )
    return grouped


def payoff_by_partner_type(results: pd.DataFrame) -> pd.DataFrame:
    """Mean payoff and accuracy sliced by ground-truth partner type."""

    return (
        results.groupby(["condition", "condition_name", "true_partner_type"], as_index=False)
        .agg(
            mean_payoff=("payoff", "mean"),
            mean_accuracy=("inferred_type_correct", "mean"),
            n=("payoff", "size"),
        )
    )


def extract_partner_signal(results: pd.DataFrame, column: str, partner_idx: int) -> pd.DataFrame:
    """Extract one per-partner array-valued metric into a tidy long frame."""

    frame = results[["condition", "condition_name", "seed", "round", column]].copy()
    frame[column] = frame[column].apply(_ensure_array)
    frame["partner_idx"] = int(partner_idx)
    frame["value"] = frame[column].apply(lambda arr: float(arr[partner_idx]) if len(arr) > partner_idx else np.nan)
    return frame.drop(columns=[column])


def beta_reward_divergence(results: pd.DataFrame, partner_idx: int | None = None) -> pd.DataFrame:
    """Compare affective β and reward averages over time."""

    betas = results[["condition", "condition_name", "seed", "round", "betas"]].copy()
    rewards = results[["condition", "seed", "round", "reward_avgs"]].copy()
    betas["betas"] = betas["betas"].apply(_ensure_array)
    rewards["reward_avgs"] = rewards["reward_avgs"].apply(_ensure_array)

    if partner_idx is None:
        betas["beta_mean"] = betas["betas"].apply(_safe_nanmean)
        rewards["reward_mean"] = rewards["reward_avgs"].apply(_safe_nanmean)
        merged = betas.merge(rewards[["condition", "seed", "round", "reward_mean"]], on=["condition", "seed", "round"])
        merged["divergence"] = merged["beta_mean"] - merged["reward_mean"]
        return merged

    betas["partner_idx"] = int(partner_idx)
    rewards["partner_idx"] = int(partner_idx)
    betas["beta_value"] = betas["betas"].apply(lambda arr: float(arr[partner_idx]) if len(arr) > partner_idx else np.nan)
    rewards["reward_value"] = rewards["reward_avgs"].apply(
        lambda arr: float(arr[partner_idx]) if len(arr) > partner_idx else np.nan
    )
    merged = betas.merge(
        rewards[["condition", "seed", "round", "partner_idx", "reward_value"]],
        on=["condition", "seed", "round", "partner_idx"],
    )
    merged["divergence"] = merged["beta_value"] - merged["reward_value"]
    return merged


def post_switch_window_summary(results: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    """Summarize payoff and inference quality in the rounds immediately after a switch."""

    frame = results.sort_values(["condition", "seed", "partner_idx", "round"]).copy()
    summaries: list[dict] = []
    for (condition, condition_name, seed, partner_idx), group in frame.groupby(
        ["condition", "condition_name", "seed", "partner_idx"],
    ):
        switch_rounds = group.loc[group["type_switched"].astype(bool), "round"].tolist()
        for switch_round in switch_rounds:
            window_frame = group[(group["round"] >= switch_round) & (group["round"] < switch_round + int(window))]
            if window_frame.empty:
                continue
            summaries.append(
                {
                    "condition": int(condition),
                    "condition_name": str(condition_name),
                    "seed": int(seed),
                    "partner_idx": int(partner_idx),
                    "switch_round": int(switch_round),
                    "window": int(window),
                    "mean_payoff": float(window_frame["payoff"].mean()),
                    "mean_accuracy": float(window_frame["inferred_type_correct"].mean()),
                    "encounters": int(len(window_frame)),
                }
            )
    return pd.DataFrame(summaries)
