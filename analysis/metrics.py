"""Derived metrics for experiment results."""

from __future__ import annotations

import ast
import re

import numpy as np
import pandas as pd


def _condition_sort_key(value) -> tuple[int, str]:
    if isinstance(value, (int, np.integer)):
        return (0, f"{int(value):04d}")
    return (1, str(value))


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


def _safe_range(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.nan
    return float(finite.max() - finite.min())


def _scheduled_switch_targets(value) -> list[int]:
    array = _ensure_array(value)
    if array.size == 0:
        return []
    return [int(item) for item in array.tolist()]


def final_round_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate final cumulative payoff and identification accuracy per seed and condition."""

    frame = results.copy()
    frame["_condition_sort"] = frame["condition"].apply(_condition_sort_key)
    frame = frame.sort_values(["_condition_sort", "seed", "round"]).drop(columns="_condition_sort")
    agg_dict = {
        "total_payoff": ("payoff", "sum"),
        "mean_accuracy": ("inferred_type_correct", "mean"),
        "mean_stance_accuracy": ("inferred_stance_correct", "mean"),
        "mean_joint_accuracy": ("inferred_joint_correct", "mean"),
        "mean_q_pi_entropy": ("q_pi_entropy", "mean"),
        "mean_abs_step_efe": ("mean_abs_step_efe", "mean"),
        "planning_cost": ("planning_cost", "first"),
        "planning_cost_ratio": ("planning_cost_ratio", "first"),
        "mu": ("mu", "first"),
    }
    if "cumulative_log_evidence" in frame.columns:
        agg_dict["total_log_evidence"] = ("cumulative_log_evidence", "last")
    if "round_log_evidence" in frame.columns:
        agg_dict["mean_round_log_evidence"] = ("round_log_evidence", "mean")
    grouped = frame.groupby(["condition", "condition_name", "seed"], as_index=False).agg(**agg_dict)
    return grouped


def payoff_by_partner_type(results: pd.DataFrame) -> pd.DataFrame:
    """Mean payoff and accuracy sliced by ground-truth partner type."""

    return results.groupby(["condition", "condition_name", "true_partner_type"], as_index=False).agg(
        mean_payoff=("payoff", "mean"),
        mean_accuracy=("inferred_type_correct", "mean"),
        n=("payoff", "size"),
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
    betas["beta_value"] = betas["betas"].apply(
        lambda arr: float(arr[partner_idx]) if len(arr) > partner_idx else np.nan
    )
    rewards["reward_value"] = rewards["reward_avgs"].apply(
        lambda arr: float(arr[partner_idx]) if len(arr) > partner_idx else np.nan
    )
    merged = betas.merge(
        rewards[["condition", "seed", "round", "partner_idx", "reward_value"]],
        on=["condition", "seed", "round", "partner_idx"],
    )
    merged["divergence"] = merged["beta_value"] - merged["reward_value"]
    return merged


def has_switch_events(results: pd.DataFrame) -> bool:
    """Return True when the results include at least one partner switch event."""

    if "type_switched" in results.columns and bool(results["type_switched"].fillna(False).astype(bool).any()):
        return True
    if "stance_switched" in results.columns and bool(results["stance_switched"].fillna(False).astype(bool).any()):
        return True
    if "current_partner_scheduled_switch" in results.columns and bool(
        results["current_partner_scheduled_switch"].fillna(False).astype(bool).any()
    ):
        return True
    if "current_partner_scheduled_stance_switch" in results.columns and bool(
        results["current_partner_scheduled_stance_switch"].fillna(False).astype(bool).any()
    ):
        return True
    if "scheduled_switch_partner_ids" not in results.columns:
        scheduled_type = pd.Series([[] for _ in range(len(results))], index=results.index)
    else:
        scheduled_type = results["scheduled_switch_partner_ids"].apply(_scheduled_switch_targets)
    if "scheduled_stance_switch_partner_ids" not in results.columns:
        scheduled_stance = pd.Series([[] for _ in range(len(results))], index=results.index)
    else:
        scheduled_stance = results["scheduled_stance_switch_partner_ids"].apply(_scheduled_switch_targets)
    return bool(scheduled_type.apply(len).gt(0).any() or scheduled_stance.apply(len).gt(0).any())


def post_switch_window_summary(results: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    """Summarize payoff and inference quality in the rounds immediately after a switch."""

    frame = results.copy()
    frame["_condition_sort"] = frame["condition"].apply(_condition_sort_key)
    frame = frame.sort_values(["_condition_sort", "seed", "partner_idx", "round"]).drop(columns="_condition_sort")
    if frame.empty:
        return pd.DataFrame()
    if "scheduled_switch_partner_ids" in frame.columns:
        frame["scheduled_switch_partner_ids"] = frame["scheduled_switch_partner_ids"].apply(_scheduled_switch_targets)
    else:
        frame["scheduled_switch_partner_ids"] = [[] for _ in range(len(frame))]
    if "scheduled_stance_switch_partner_ids" in frame.columns:
        frame["scheduled_stance_switch_partner_ids"] = frame["scheduled_stance_switch_partner_ids"].apply(
            _scheduled_switch_targets
        )
    else:
        frame["scheduled_stance_switch_partner_ids"] = [[] for _ in range(len(frame))]
    summaries: list[dict] = []
    for (condition, condition_name, seed, partner_idx), group in frame.groupby(
        ["condition", "condition_name", "seed", "partner_idx"],
    ):
        seed_rows = frame[(frame["condition"] == condition) & (frame["seed"] == seed)]
        switch_rounds: set[tuple[int, str]] = set()
        for _, switch_row in seed_rows.iterrows():
            if int(partner_idx) in switch_row["scheduled_switch_partner_ids"]:
                switch_rounds.add((int(switch_row["round"]), "scheduled_type"))
            if int(partner_idx) in switch_row["scheduled_stance_switch_partner_ids"]:
                switch_rounds.add((int(switch_row["round"]), "scheduled_stance"))
        if "type_switched" in group.columns:
            switched_types = group["type_switched"].fillna(False).astype(bool)
        else:
            switched_types = pd.Series(False, index=group.index)
        if "stance_switched" in group.columns:
            switched_stances = group["stance_switched"].fillna(False).astype(bool)
        else:
            switched_stances = pd.Series(False, index=group.index)
        for _, switch_row in group[switched_types | switched_stances].iterrows():
            switch_rounds.add((int(switch_row["round"]), str(switch_row.get("switch_kind", "unknown"))))

        for switch_round, switch_kind in sorted(switch_rounds):
            window_frame = group[group["round"] >= switch_round].head(int(window)).copy()
            if window_frame.empty:
                continue
            window_frame["encounters_since_switch"] = np.arange(len(window_frame), dtype=int)
            summaries.append(
                {
                    "condition": condition,
                    "condition_name": str(condition_name),
                    "seed": int(seed),
                    "partner_idx": int(partner_idx),
                    "switch_round": switch_round,
                    "switch_kind": str(switch_kind),
                    "window": int(window),
                    "window_label": f"1-{int(window)}",
                    "mean_payoff": float(window_frame["payoff"].mean()),
                    "mean_accuracy": float(window_frame["inferred_type_correct"].mean()),
                    "mean_stance_accuracy": (
                        float(window_frame["inferred_stance_correct"].mean())
                        if "inferred_stance_correct" in window_frame.columns
                        else np.nan
                    ),
                    "mean_joint_accuracy": (
                        float(window_frame["inferred_joint_correct"].mean())
                        if "inferred_joint_correct" in window_frame.columns
                        else np.nan
                    ),
                    "mean_terminal_signal": _safe_nanmean(
                        np.asarray(
                            [
                                _ensure_array(value)[int(partner_idx)]
                                for value in window_frame["terminal_signal"].tolist()
                            ],
                            dtype=float,
                        )
                    )
                    if "terminal_signal" in window_frame
                    else np.nan,
                    "encounters": int(len(window_frame)),
                }
            )
    return pd.DataFrame(summaries)


def betrayal_trajectory(results: pd.DataFrame, max_encounters: int = 10) -> pd.DataFrame:
    """Return per-encounter trajectories following partner switches."""

    frame = results.copy()
    frame["_condition_sort"] = frame["condition"].apply(_condition_sort_key)
    frame = frame.sort_values(["_condition_sort", "seed", "partner_idx", "round"]).drop(columns="_condition_sort")
    if frame.empty:
        return pd.DataFrame()
    if "scheduled_switch_partner_ids" in frame.columns:
        frame["scheduled_switch_partner_ids"] = frame["scheduled_switch_partner_ids"].apply(_scheduled_switch_targets)
    else:
        frame["scheduled_switch_partner_ids"] = [[] for _ in range(len(frame))]
    if "scheduled_stance_switch_partner_ids" in frame.columns:
        frame["scheduled_stance_switch_partner_ids"] = frame["scheduled_stance_switch_partner_ids"].apply(
            _scheduled_switch_targets
        )
    else:
        frame["scheduled_stance_switch_partner_ids"] = [[] for _ in range(len(frame))]

    records: list[dict] = []
    for (condition, condition_name, seed, partner_idx), group in frame.groupby(
        ["condition", "condition_name", "seed", "partner_idx"],
    ):
        group = group.reset_index(drop=True)
        group["betas"] = group["betas"].apply(_ensure_array)
        group["reward_avgs"] = group["reward_avgs"].apply(_ensure_array)
        group["terminal_signal"] = group["terminal_signal"].apply(_ensure_array)
        seed_rows = frame[(frame["condition"] == condition) & (frame["seed"] == seed)]
        switch_rounds: set[tuple[int, str]] = set()
        for _, switch_row in seed_rows.iterrows():
            if int(partner_idx) in switch_row["scheduled_switch_partner_ids"]:
                switch_rounds.add((int(switch_row["round"]), "scheduled_type"))
            if int(partner_idx) in switch_row["scheduled_stance_switch_partner_ids"]:
                switch_rounds.add((int(switch_row["round"]), "scheduled_stance"))
        type_switched = (
            group["type_switched"].fillna(False).astype(bool)
            if "type_switched" in group.columns
            else pd.Series(False, index=group.index)
        )
        stance_switched = (
            group["stance_switched"].fillna(False).astype(bool)
            if "stance_switched" in group.columns
            else pd.Series(False, index=group.index)
        )
        for _, switch_row in group[type_switched | stance_switched].iterrows():
            switch_rounds.add((int(switch_row["round"]), str(switch_row.get("switch_kind", "unknown"))))

        for event_idx, (switch_round, switch_kind) in enumerate(sorted(switch_rounds)):
            window = group[group["round"] >= switch_round].head(int(max_encounters)).copy()
            for encounter_offset, (_, row) in enumerate(window.iterrows()):
                beta_arr = row["betas"]
                reward_arr = row["reward_avgs"]
                terminal_arr = row["terminal_signal"]
                records.append(
                    {
                        "condition": condition,
                        "condition_name": str(condition_name),
                        "seed": int(seed),
                        "partner_idx": int(partner_idx),
                        "switch_event_idx": int(event_idx),
                        "switch_round": int(switch_round),
                        "switch_kind": str(switch_kind),
                        "encounters_since_switch": int(encounter_offset),
                        "round": int(row["round"]),
                        "payoff": float(row["payoff"]),
                        "inferred_type_correct": float(row["inferred_type_correct"]),
                        "beta": float(beta_arr[int(partner_idx)]) if len(beta_arr) > partner_idx else np.nan,
                        "reward_signal": float(reward_arr[int(partner_idx)])
                        if len(reward_arr) > partner_idx
                        else np.nan,
                        "terminal_signal": float(terminal_arr[int(partner_idx)])
                        if len(terminal_arr) > partner_idx
                        else np.nan,
                        "divergence_beta_minus_reward": (
                            float(beta_arr[int(partner_idx)] - reward_arr[int(partner_idx)])
                            if len(beta_arr) > partner_idx and len(reward_arr) > partner_idx
                            else np.nan
                        ),
                    }
                )
    return pd.DataFrame(records)


def affective_movement_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize whether β and terminal signals move enough to matter."""

    frame = results[["condition", "condition_name", "seed", "betas", "terminal_signal"]].copy()
    if frame.empty:
        return pd.DataFrame()

    frame["betas"] = frame["betas"].apply(_ensure_array)
    frame["terminal_signal"] = frame["terminal_signal"].apply(_ensure_array)
    per_seed = frame.groupby(["condition", "condition_name", "seed"], as_index=False).agg(
        beta_range=(
            "betas",
            lambda series: _safe_nanmean(np.asarray([_safe_range(arr) for arr in series], dtype=float)),
        ),
        terminal_signal_range=(
            "terminal_signal",
            lambda series: _safe_nanmean(np.asarray([_safe_range(arr) for arr in series], dtype=float)),
        ),
        beta_mean=(
            "betas",
            lambda series: _safe_nanmean(np.asarray([_safe_nanmean(arr) for arr in series], dtype=float)),
        ),
        terminal_signal_mean=(
            "terminal_signal",
            lambda series: _safe_nanmean(np.asarray([_safe_nanmean(arr) for arr in series], dtype=float)),
        ),
    )
    if per_seed.empty:
        return per_seed
    thresholds = per_seed.copy()
    thresholds["beta_moved_materially"] = thresholds["beta_range"] >= 0.05
    thresholds["terminal_signal_moved_materially"] = thresholds["terminal_signal_range"] >= 0.05
    return thresholds


def post_switch_condition_comparison(results: pd.DataFrame, windows: tuple[int, ...] = (5, 10)) -> pd.DataFrame:
    """Compare paired conditions in post-switch windows.

    Uses the canonical tau-4 affective agent (`tau4_affect`) and the reward
    average preset when both are present in the results.
    """

    rows: list[pd.DataFrame] = []
    for window in windows:
        summary = post_switch_window_summary(results, window=window)
        if summary.empty:
            continue
        pivot = summary.pivot_table(
            index=["seed", "partner_idx", "switch_round"],
            columns="condition",
            values=["mean_payoff", "mean_accuracy", "mean_terminal_signal"],
        )
        if pivot.empty:
            continue
        pivot.columns = [f"{metric}_c{condition}" for metric, condition in pivot.columns]
        pivot = pivot.reset_index()
        pivot["window"] = int(window)
        pivot["window_label"] = f"1-{int(window)}"
        pivot["payoff_difference_tau4_affect_minus_reward_average"] = pivot.get(
            "mean_payoff_ctau4_affect", np.nan
        ) - pivot.get(
            "mean_payoff_creward_average", np.nan
        )
        pivot["accuracy_difference_tau4_affect_minus_reward_average"] = pivot.get(
            "mean_accuracy_ctau4_affect", np.nan
        ) - pivot.get(
            "mean_accuracy_creward_average",
            np.nan,
        )
        pivot["stance_accuracy_difference_tau4_affect_minus_reward_average"] = pivot.get(
            "mean_stance_accuracy_ctau4_affect",
            np.nan,
        ) - pivot.get("mean_stance_accuracy_creward_average", np.nan)
        pivot["terminal_signal_difference_tau4_affect_minus_reward_average"] = pivot.get(
            "mean_terminal_signal_ctau4_affect", np.nan
        ) - pivot.get("mean_terminal_signal_creward_average", np.nan)
        rows.append(pivot)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def betrayal_latency_summary(
    results: pd.DataFrame,
    max_encounters: int = 10,
    safe_payoff_threshold: float = 1.0,
) -> pd.DataFrame:
    """Estimate detection and payoff-recovery latencies after betrayal events."""

    trajectory = betrayal_trajectory(results, max_encounters=max_encounters)
    if trajectory.empty:
        return pd.DataFrame()

    rows: list[dict] = []
    for (condition, condition_name, seed, partner_idx, switch_event_idx), group in trajectory.groupby(
        ["condition", "condition_name", "seed", "partner_idx", "switch_event_idx"],
    ):
        group = group.sort_values("encounters_since_switch")
        detection = group.loc[group["inferred_type_correct"] >= 1.0, "encounters_since_switch"]
        recovery = group.loc[group["payoff"] >= float(safe_payoff_threshold), "encounters_since_switch"]
        rows.append(
            {
                "condition": condition,
                "condition_name": str(condition_name),
                "seed": int(seed),
                "partner_idx": int(partner_idx),
                "switch_event_idx": int(switch_event_idx),
                "switch_round": int(group["switch_round"].iloc[0]),
                "max_encounters": int(max_encounters),
                "safe_payoff_threshold": float(safe_payoff_threshold),
                "detection_latency": float(detection.iloc[0]) if not detection.empty else np.nan,
                "payoff_recovery_latency": float(recovery.iloc[0]) if not recovery.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)
