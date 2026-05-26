"""Derived metrics for experiment results."""

from __future__ import annotations

import ast
import re
from collections import defaultdict

import numpy as np
import pandas as pd


def _variant_sort_key(value) -> tuple[int, str]:
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


def _safe_entropy(values: pd.Series | np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return np.nan
    total = float(values.sum())
    if total <= 0:
        return np.nan
    probs = values / total
    probs = probs[probs > 0]
    return float(-(probs * np.log(probs)).sum())


def _safe_lag1_autocorr(values: pd.Series | np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 3:
        return np.nan
    previous = values[:-1]
    current = values[1:]
    if np.isclose(previous.std(), 0.0) or np.isclose(current.std(), 0.0):
        return np.nan
    return float(np.corrcoef(previous, current)[0, 1])


def _selected_partner_beta(row: pd.Series) -> float:
    if "betas" not in row or "selected_partner" not in row:
        return np.nan
    partner_idx = int(row["selected_partner"])
    if partner_idx < 0:
        return np.nan
    betas = _ensure_array(row["betas"])
    if len(betas) <= partner_idx:
        return np.nan
    return float(betas[partner_idx])


def _mean_beta(row: pd.Series) -> float:
    if "betas" not in row:
        return np.nan
    return _safe_nanmean(_ensure_array(row["betas"]))


def _stack_beta_rows(series: pd.Series) -> np.ndarray:
    arrays = [_ensure_array(value) for value in series]
    arrays = [array for array in arrays if array.size > 0]
    if not arrays:
        return np.asarray([], dtype=float)
    width = max(len(array) for array in arrays)
    stacked = np.full((len(arrays), width), np.nan, dtype=float)
    for row_idx, array in enumerate(arrays):
        stacked[row_idx, : len(array)] = array
    return stacked


def _scheduled_switch_targets(value) -> list[int]:
    if value is None:
        return []
    if isinstance(value, float) and np.isnan(value):
        return []
    if isinstance(value, str) and value.strip() in {"", "[]", "nan", "None"}:
        return []
    array = _ensure_array(value)
    if array.size == 0:
        return []
    if array.ndim == 0:
        return [int(array.item())] if np.isfinite(array.item()) else []
    return [int(item) for item in array.tolist() if np.isfinite(item)]


def _build_scheduled_switch_map(
    frame: pd.DataFrame,
    column: str,
    switch_kind: str,
) -> dict[tuple[object, int, int], set[tuple[int, str]]]:
    """Index scheduled switch rows by variant/seed/partner for fast lookup."""

    schedule_map: dict[tuple[object, int, int], set[tuple[int, str]]] = defaultdict(set)
    if column not in frame.columns:
        return schedule_map
    scheduled_rows = frame.loc[frame[column].apply(len).gt(0), ["variant_id", "seed", "round", column]]
    for _, row in scheduled_rows.iterrows():
        for partner_idx in row[column]:
            schedule_map[(row["variant_id"], int(row["seed"]), int(partner_idx))].add((int(row["round"]), switch_kind))
    return schedule_map


def _build_observed_switch_map(frame: pd.DataFrame) -> dict[tuple[object, int, int], set[tuple[int, str]]]:
    """Index observed switch rows by variant/seed/partner for fast lookup."""

    observed_map: dict[tuple[object, int, int], set[tuple[int, str]]] = defaultdict(set)
    type_switched = (
        frame["type_switched"].fillna(False).astype(bool)
        if "type_switched" in frame.columns
        else pd.Series(False, index=frame.index)
    )
    stance_switched = (
        frame["stance_switched"].fillna(False).astype(bool)
        if "stance_switched" in frame.columns
        else pd.Series(False, index=frame.index)
    )
    switch_rows = frame.loc[
        type_switched | stance_switched, ["variant_id", "seed", "partner_idx", "round", "switch_kind"]
    ]
    for _, row in switch_rows.iterrows():
        observed_map[(row["variant_id"], int(row["seed"]), int(row["partner_idx"]))].add(
            (int(row["round"]), str(row.get("switch_kind", "unknown")))
        )
    return observed_map


def _switch_rounds_for_partner(
    key: tuple[object, int, int],
    scheduled_type_map: dict[tuple[object, int, int], set[tuple[int, str]]],
    scheduled_stance_map: dict[tuple[object, int, int], set[tuple[int, str]]],
    observed_map: dict[tuple[object, int, int], set[tuple[int, str]]],
) -> list[tuple[int, str]]:
    switch_rounds = set()
    switch_rounds.update(scheduled_type_map.get(key, set()))
    switch_rounds.update(scheduled_stance_map.get(key, set()))
    switch_rounds.update(observed_map.get(key, set()))
    return sorted(switch_rounds)


def final_round_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate final cumulative payoff and identification accuracy per seed and variant."""

    frame = results.copy()
    frame["_variant_sort"] = frame["variant_id"].apply(_variant_sort_key)
    frame = frame.sort_values(["_variant_sort", "seed", "round"]).drop(columns="_variant_sort")
    agg_dict = {
        "total_payoff": ("payoff", "sum"),
        "mean_accuracy": ("inferred_type_correct", "mean"),
        "mean_stance_accuracy": ("inferred_stance_correct", "mean"),
        "mean_joint_accuracy": ("inferred_joint_correct", "mean"),
        "mean_q_pi_entropy": ("q_pi_entropy", "mean"),
        "mean_abs_step_efe": ("mean_abs_step_efe", "mean"),
        "planning_cost": ("planning_cost", "first"),
        "planning_cost_ratio": ("planning_cost_ratio", "first"),
    }
    if "cumulative_log_evidence" in frame.columns:
        agg_dict["total_log_evidence"] = ("cumulative_log_evidence", "last")
    if "round_log_evidence" in frame.columns:
        agg_dict["mean_round_log_evidence"] = ("round_log_evidence", "mean")
    grouped = frame.groupby(["variant_id", "seed"], as_index=False).agg(**agg_dict)
    return grouped


def payoff_by_partner_type(results: pd.DataFrame) -> pd.DataFrame:
    """Mean payoff and accuracy sliced by ground-truth partner type."""

    return results.groupby(["variant_id", "true_partner_type"], as_index=False).agg(
        mean_payoff=("payoff", "mean"),
        mean_accuracy=("inferred_type_correct", "mean"),
        n=("payoff", "size"),
    )


def extract_partner_signal(results: pd.DataFrame, column: str, partner_idx: int) -> pd.DataFrame:
    """Extract one per-partner array-valued metric into a tidy long frame."""

    frame = results[["variant_id", "seed", "round", column]].copy()
    frame[column] = frame[column].apply(_ensure_array)
    frame["partner_idx"] = int(partner_idx)
    frame["value"] = frame[column].apply(lambda arr: float(arr[partner_idx]) if len(arr) > partner_idx else np.nan)
    return frame.drop(columns=[column])


def beta_reward_divergence(results: pd.DataFrame, partner_idx: int | None = None) -> pd.DataFrame:
    """Compare affective β and reward averages over time."""

    betas = results[["variant_id", "seed", "round", "betas"]].copy()
    rewards = results[["variant_id", "seed", "round", "reward_avgs"]].copy()
    betas["betas"] = betas["betas"].apply(_ensure_array)
    rewards["reward_avgs"] = rewards["reward_avgs"].apply(_ensure_array)

    if partner_idx is None:
        betas["beta_mean"] = betas["betas"].apply(_safe_nanmean)
        rewards["reward_mean"] = rewards["reward_avgs"].apply(_safe_nanmean)
        merged = betas.merge(
            rewards[["variant_id", "seed", "round", "reward_mean"]],
            on=["variant_id", "seed", "round"],
        )
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
        rewards[["variant_id", "seed", "round", "partner_idx", "reward_value"]],
        on=["variant_id", "seed", "round", "partner_idx"],
    )
    merged["divergence"] = merged["beta_value"] - merged["reward_value"]
    return merged


def has_switch_events(results: pd.DataFrame) -> bool:
    """Return True when the results include scheduled betrayal-style switch events."""

    if "current_partner_scheduled_switch" in results.columns and bool(
        results["current_partner_scheduled_switch"].fillna(False).astype(bool).any()
    ):
        return True
    if "current_partner_scheduled_stance_switch" in results.columns and bool(
        results["current_partner_scheduled_stance_switch"].fillna(False).astype(bool).any()
    ):
        return True

    def _has_nonempty_schedule(column: str) -> bool:
        if column not in results.columns:
            return False
        raw = results[column].astype(str).str.strip()
        candidates = raw[~raw.isin({"", "[]", "nan", "None"})]
        if candidates.empty:
            return False
        return bool(candidates.apply(lambda value: len(_scheduled_switch_targets(value)) > 0).any())

    if _has_nonempty_schedule("scheduled_switch_partner_ids") or _has_nonempty_schedule(
        "scheduled_stance_switch_partner_ids"
    ):
        return True
    if "switch_kind" in results.columns:
        switch_kind = results["switch_kind"].fillna("").astype(str)
        return bool(switch_kind.str.startswith("scheduled_").any())
    return False


def post_switch_window_summary(results: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    """Summarize payoff and inference quality in the rounds immediately after a switch."""

    frame = results.copy()
    frame["_variant_sort"] = frame["variant_id"].apply(_variant_sort_key)
    frame = frame.sort_values(["_variant_sort", "seed", "partner_idx", "round"]).drop(columns="_variant_sort")
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
    scheduled_type_map = _build_scheduled_switch_map(frame, "scheduled_switch_partner_ids", "scheduled_type")
    scheduled_stance_map = _build_scheduled_switch_map(frame, "scheduled_stance_switch_partner_ids", "scheduled_stance")
    observed_map = _build_observed_switch_map(frame)
    summaries: list[dict] = []
    for (variant_id, seed, partner_idx), group in frame.groupby(
        ["variant_id", "seed", "partner_idx"],
    ):
        key = (variant_id, int(seed), int(partner_idx))
        switch_rounds = _switch_rounds_for_partner(key, scheduled_type_map, scheduled_stance_map, observed_map)
        for switch_round, switch_kind in sorted(switch_rounds):
            window_frame = group[group["round"] >= switch_round].head(int(window)).copy()
            if window_frame.empty:
                summaries.append(
                    {
                        "variant_id": str(variant_id),
                        "seed": int(seed),
                        "partner_idx": int(partner_idx),
                        "switch_round": switch_round,
                        "switch_kind": str(switch_kind),
                        "window": int(window),
                        "window_label": f"1-{int(window)}",
                        "mean_payoff": np.nan,
                        "mean_accuracy": np.nan,
                        "mean_stance_accuracy": np.nan,
                        "mean_joint_accuracy": np.nan,
                        "encounters": 0,
                    }
                )
                continue
            window_frame["encounters_since_switch"] = np.arange(len(window_frame), dtype=int)
            summaries.append(
                {
                    "variant_id": str(variant_id),
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
                    "encounters": int(len(window_frame)),
                }
            )
    return pd.DataFrame(summaries)


def betrayal_phase_summary(
    results: pd.DataFrame,
    pre_window: int = 20,
    acute_window: int = 10,
) -> pd.DataFrame:
    """Split betrayal events into pre-switch, acute post-switch, and post-acute tail windows."""

    frame = results.copy()
    frame["_variant_sort"] = frame["variant_id"].apply(_variant_sort_key)
    frame = frame.sort_values(["_variant_sort", "seed", "partner_idx", "round"]).drop(columns="_variant_sort")
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
    scheduled_type_map = _build_scheduled_switch_map(frame, "scheduled_switch_partner_ids", "scheduled_type")
    scheduled_stance_map = _build_scheduled_switch_map(frame, "scheduled_stance_switch_partner_ids", "scheduled_stance")
    observed_map = _build_observed_switch_map(frame)

    rows: list[dict] = []
    for (variant_id, seed, partner_idx), group in frame.groupby(["variant_id", "seed", "partner_idx"]):
        key = (variant_id, int(seed), int(partner_idx))
        switch_rounds = _switch_rounds_for_partner(key, scheduled_type_map, scheduled_stance_map, observed_map)
        for switch_round, switch_kind in switch_rounds:
            phases = {
                "pre_switch": group[group["round"] < switch_round].tail(int(pre_window)),
                "acute_post_switch": group[group["round"] >= switch_round].head(int(acute_window)),
                "post_acute_tail": group[group["round"] >= switch_round].iloc[int(acute_window) :],
            }
            for phase, phase_frame in phases.items():
                selected_partner_rate = (
                    float((phase_frame["selected_partner"] == int(partner_idx)).mean())
                    if "selected_partner" in phase_frame.columns and not phase_frame.empty
                    else np.nan
                )
                selected_action_mean = (
                    float(phase_frame["selected_action"].mean())
                    if "selected_action" in phase_frame.columns and not phase_frame.empty
                    else np.nan
                )
                rows.append(
                    {
                        "variant_id": str(variant_id),
                        "seed": int(seed),
                        "partner_idx": int(partner_idx),
                        "switch_round": int(switch_round),
                        "switch_kind": str(switch_kind),
                        "phase": phase,
                        "encounters": int(len(phase_frame)),
                        "mean_payoff": float(phase_frame["payoff"].mean()) if not phase_frame.empty else np.nan,
                        "mean_q_pi_entropy": (
                            float(phase_frame["q_pi_entropy"].mean())
                            if "q_pi_entropy" in phase_frame.columns and not phase_frame.empty
                            else np.nan
                        ),
                        "selected_partner_rate": selected_partner_rate,
                        "mean_selected_action": selected_action_mean,
                    }
                )
    return pd.DataFrame(rows)


def betrayal_trajectory(results: pd.DataFrame, max_encounters: int = 10) -> pd.DataFrame:
    """Return per-encounter trajectories following partner switches."""

    frame = results.copy()
    frame["_variant_sort"] = frame["variant_id"].apply(_variant_sort_key)
    frame = frame.sort_values(["_variant_sort", "seed", "partner_idx", "round"]).drop(columns="_variant_sort")
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
    scheduled_type_map = _build_scheduled_switch_map(frame, "scheduled_switch_partner_ids", "scheduled_type")
    scheduled_stance_map = _build_scheduled_switch_map(frame, "scheduled_stance_switch_partner_ids", "scheduled_stance")
    observed_map = _build_observed_switch_map(frame)

    records: list[dict] = []
    for (variant_id, seed, partner_idx), group in frame.groupby(
        ["variant_id", "seed", "partner_idx"],
    ):
        group = group.reset_index(drop=True)
        key = (variant_id, int(seed), int(partner_idx))
        switch_rounds = _switch_rounds_for_partner(key, scheduled_type_map, scheduled_stance_map, observed_map)
        for event_idx, (switch_round, switch_kind) in enumerate(switch_rounds):
            window = group[group["round"] >= switch_round].head(int(max_encounters)).copy()
            if window.empty:
                continue
            window["betas"] = window["betas"].apply(_ensure_array)
            window["reward_avgs"] = window["reward_avgs"].apply(_ensure_array)
            for encounter_offset, (_, row) in enumerate(window.iterrows()):
                beta_arr = row["betas"]
                reward_arr = row["reward_avgs"]
                records.append(
                    {
                        "variant_id": str(variant_id),
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
                        "divergence_beta_minus_reward": (
                            float(beta_arr[int(partner_idx)] - reward_arr[int(partner_idx)])
                            if len(beta_arr) > partner_idx and len(reward_arr) > partner_idx
                            else np.nan
                        ),
                    }
                )
    return pd.DataFrame(records)


def affective_movement_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize whether β values move enough to matter."""

    frame = results[["variant_id", "seed", "betas"]].copy()
    if frame.empty:
        return pd.DataFrame()

    frame["betas"] = frame["betas"].apply(_ensure_array)
    rows: list[dict] = []
    for (variant_id, seed), group in frame.groupby(["variant_id", "seed"], sort=False):
        beta_stack = _stack_beta_rows(group["betas"])
        if beta_stack.size:
            temporal_ranges = np.asarray(
                [_safe_range(beta_stack[:, idx]) for idx in range(beta_stack.shape[1])],
                dtype=float,
            )
            beta_range = _safe_nanmean(temporal_ranges)
            beta_mean = _safe_nanmean(beta_stack.ravel())
        else:
            beta_range = np.nan
            beta_mean = np.nan
        rows.append(
            {
                "variant_id": variant_id,
                "seed": int(seed),
                "beta_range": beta_range,
                "beta_mean": beta_mean,
            }
        )
    per_seed = pd.DataFrame(rows)
    if per_seed.empty:
        return per_seed
    thresholds = per_seed.copy()
    thresholds["beta_moved_materially"] = thresholds["beta_range"] >= 0.05
    return thresholds


def deployment_dissociation_summary(results: pd.DataFrame, reference_variant: str = "affect") -> pd.DataFrame:
    """Summarize H2 belief-vs-policy deployment deltas against an affective reference."""

    summary = final_round_summary(results)
    if summary.empty:
        return pd.DataFrame()
    if "round_log_evidence" in results.columns:
        log_score = (
            results.groupby(["variant_id", "seed"], as_index=False)
            .agg(mean_round_log_evidence=("round_log_evidence", "mean"))
            .rename(columns={"mean_round_log_evidence": "predictive_log_score"})
        )
        summary = summary.merge(log_score, on=["variant_id", "seed"], how="left")

    value_columns = [
        "total_payoff",
        "mean_accuracy",
        "mean_stance_accuracy",
        "mean_joint_accuracy",
        "mean_q_pi_entropy",
        "predictive_log_score",
    ]
    available = [column for column in value_columns if column in summary.columns]
    per_variant = summary.groupby("variant_id", as_index=False).agg({column: "mean" for column in available})
    reference = per_variant.loc[per_variant["variant_id"] == reference_variant]
    if reference.empty:
        return per_variant
    reference_row = reference.iloc[0]
    for column in available:
        per_variant[f"delta_{column}_vs_{reference_variant}"] = per_variant[column] - float(reference_row[column])
    return per_variant


def partner_choice_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize partner-selection allocation for agent-choice runs."""

    if "selected_partner" not in results.columns:
        return pd.DataFrame()
    frame = results.copy()
    frame = frame[frame["selected_partner"].notna()]
    if frame.empty:
        return pd.DataFrame()
    frame["selected_partner"] = frame["selected_partner"].astype(int)
    if "betas" in frame.columns:
        frame["selected_partner_beta"] = frame.apply(_selected_partner_beta, axis=1)
    else:
        frame["selected_partner_beta"] = np.nan
    totals = frame.groupby(["variant_id", "seed"], as_index=False).size().rename(columns={"size": "total_choices"})
    grouped = (
        frame.groupby(["variant_id", "seed", "selected_partner"], as_index=False)
        .agg(
            selection_count=("selected_partner", "size"),
            mean_payoff=("payoff", "mean"),
            mean_q_pi_entropy=("q_pi_entropy", "mean"),
            mean_selected_partner_beta=("selected_partner_beta", "mean"),
        )
        .merge(totals, on=["variant_id", "seed"], how="left")
    )
    grouped["selection_rate"] = grouped["selection_count"] / grouped["total_choices"]
    return grouped


def phenotype_validation_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize beta dynamics and visible behavior for H5 perturbation variants."""

    if results.empty:
        return pd.DataFrame()
    frame = results.copy()
    if "betas" in frame.columns:
        frame["mean_beta"] = frame.apply(_mean_beta, axis=1)
    else:
        frame["mean_beta"] = np.nan

    rows: list[dict] = []
    for (variant_id, seed), group in frame.groupby(["variant_id", "seed"]):
        group = group.sort_values("round")
        beta_stack = _stack_beta_rows(group["betas"]) if "betas" in group.columns else np.asarray([], dtype=float)
        partner_ranges = (
            np.asarray([_safe_range(beta_stack[:, idx]) for idx in range(beta_stack.shape[1])], dtype=float)
            if beta_stack.size
            else np.asarray([], dtype=float)
        )
        selected_counts = (
            group["selected_partner"].value_counts().to_numpy(dtype=float)
            if "selected_partner" in group.columns
            else np.asarray([], dtype=float)
        )
        actions = group["selected_action"].dropna().to_numpy(dtype=float) if "selected_action" in group.columns else []
        action_flip_rate = (
            float(np.mean(np.diff(actions) != 0)) if len(actions) > 1 else np.nan
        )
        finite_partner_ranges = partner_ranges[np.isfinite(partner_ranges)]
        rows.append(
            {
                "variant_id": str(variant_id),
                "seed": int(seed),
                "beta_mean": float(group["mean_beta"].mean()),
                "beta_std": float(group["mean_beta"].std(ddof=0)),
                "beta_range": float(finite_partner_ranges.max()) if finite_partner_ranges.size else np.nan,
                "beta_lag1_autocorr": _safe_lag1_autocorr(group["mean_beta"]),
                "mean_q_pi_entropy": (
                    float(group["q_pi_entropy"].mean()) if "q_pi_entropy" in group.columns else np.nan
                ),
                "partner_selection_entropy": _safe_entropy(selected_counts),
                "action_flip_rate": action_flip_rate,
                "total_payoff": float(group["payoff"].sum()) if "payoff" in group.columns else np.nan,
            }
        )
    return pd.DataFrame(rows)


def partner_model_fitness_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize partner-local precision, surprise, reward, and accuracy.

    Beta is the HESP rate parameter, so lower beta means higher policy precision.
    This table makes the H1 distinction explicit: precision should follow
    predictive reliability/surprise more closely than payoff or reward signal.
    """

    required = {"variant_id", "seed", "round", "betas"}
    if results.empty or not required <= set(results.columns):
        return pd.DataFrame()

    rows: list[dict] = []
    for _, row in results.iterrows():
        betas = _ensure_array(row["betas"])
        prediction_errors = (
            _ensure_array(row["prediction_errors"]) if "prediction_errors" in row.index else np.asarray([])
        )
        reward_avgs = _ensure_array(row["reward_avgs"]) if "reward_avgs" in row.index else np.asarray([])
        active_partner = (
            int(row["partner_idx"]) if "partner_idx" in row.index and pd.notna(row["partner_idx"]) else None
        )
        for partner_idx, beta in enumerate(betas):
            if not np.isfinite(beta):
                continue
            is_active = active_partner == partner_idx
            rows.append(
                {
                    "variant_id": str(row["variant_id"]),
                    "seed": int(row["seed"]),
                    "round": int(row["round"]),
                    "partner_idx": int(partner_idx),
                    "beta": float(beta),
                    "precision": float(1.0 / beta) if beta > 0 else np.nan,
                    "surprise": (
                        float(prediction_errors[partner_idx])
                        if len(prediction_errors) > partner_idx
                        else np.nan
                    ),
                    "reward_signal": (
                        float(reward_avgs[partner_idx]) if len(reward_avgs) > partner_idx else np.nan
                    ),
                    "active_payoff": float(row["payoff"]) if is_active and "payoff" in row.index else np.nan,
                    "active_accuracy": (
                        float(row["inferred_type_correct"])
                        if is_active and "inferred_type_correct" in row.index
                        else np.nan
                    ),
                    "active_encounter": bool(is_active),
                }
            )
    tidy = pd.DataFrame(rows)
    if tidy.empty:
        return tidy
    summary = tidy.groupby(["variant_id", "seed", "partner_idx"], as_index=False).agg(
        beta_mean=("beta", "mean"),
        precision_mean=("precision", "mean"),
        surprise_mean=("surprise", "mean"),
        reward_signal_mean=("reward_signal", "mean"),
        active_mean_payoff=("active_payoff", "mean"),
        active_accuracy=("active_accuracy", "mean"),
        active_encounters=("active_encounter", "sum"),
    )
    return summary


def _safe_corr(left: pd.Series, right: pd.Series) -> float:
    pair = pd.DataFrame({"left": left, "right": right}).replace([np.inf, -np.inf], np.nan).dropna()
    if len(pair) < 3:
        return np.nan
    if np.isclose(pair["left"].std(ddof=0), 0.0) or np.isclose(pair["right"].std(ddof=0), 0.0):
        return np.nan
    return float(pair["left"].corr(pair["right"]))


def _cohen_d(left: pd.Series, right: pd.Series) -> float:
    left_values = pd.Series(left, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    right_values = pd.Series(right, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    if len(left_values) < 2 or len(right_values) < 2:
        return np.nan
    pooled_var = (
        ((len(left_values) - 1) * left_values.var(ddof=1))
        + ((len(right_values) - 1) * right_values.var(ddof=1))
    ) / (len(left_values) + len(right_values) - 2)
    if not np.isfinite(pooled_var) or np.isclose(pooled_var, 0.0):
        return np.nan
    return float((left_values.mean() - right_values.mean()) / np.sqrt(pooled_var))


def _bootstrap_mean_ci(
    values: pd.Series,
    iterations: int = 1000,
    random_seed: int = 0,
) -> tuple[float, float]:
    clean = pd.Series(values, dtype=float).replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    if clean.size == 0 or iterations <= 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(int(random_seed))
    samples = rng.choice(clean, size=(int(iterations), clean.size), replace=True)
    means = samples.mean(axis=1)
    return (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)))


def _bootstrap_difference_ci(
    left: pd.Series,
    right: pd.Series,
    iterations: int = 1000,
    random_seed: int = 0,
) -> tuple[float, float]:
    left_values = pd.Series(left, dtype=float).replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    right_values = pd.Series(right, dtype=float).replace([np.inf, -np.inf], np.nan).dropna().to_numpy(dtype=float)
    if left_values.size == 0 or right_values.size == 0 or iterations <= 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(int(random_seed))
    left_samples = rng.choice(left_values, size=(int(iterations), left_values.size), replace=True)
    right_samples = rng.choice(right_values, size=(int(iterations), right_values.size), replace=True)
    diffs = left_samples.mean(axis=1) - right_samples.mean(axis=1)
    return (float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975)))


def _effect_row(
    *,
    readout: str,
    metric: str,
    treatment_variant: str,
    treatment_values: pd.Series,
    reference_variant: str | None = None,
    reference_values: pd.Series | None = None,
    bootstrap_iterations: int = 1000,
    random_seed: int = 0,
) -> dict:
    treatment_clean = pd.Series(treatment_values, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    reference_clean = (
        pd.Series(reference_values, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
        if reference_values is not None
        else pd.Series(dtype=float)
    )
    treatment_mean = float(treatment_clean.mean()) if not treatment_clean.empty else np.nan
    reference_mean = float(reference_clean.mean()) if not reference_clean.empty else np.nan
    if reference_values is None:
        difference = treatment_mean
        ci_low, ci_high = _bootstrap_mean_ci(treatment_clean, bootstrap_iterations, random_seed)
        cohen_d = np.nan
        n_reference = 0
    else:
        difference = treatment_mean - reference_mean
        ci_low, ci_high = _bootstrap_difference_ci(
            treatment_clean,
            reference_clean,
            bootstrap_iterations,
            random_seed,
        )
        cohen_d = _cohen_d(treatment_clean, reference_clean)
        n_reference = int(len(reference_clean))
    return {
        "readout": readout,
        "metric": metric,
        "treatment_variant": treatment_variant,
        "reference_variant": reference_variant or "",
        "treatment_mean": treatment_mean,
        "reference_mean": reference_mean,
        "difference": difference,
        "cohen_d": cohen_d,
        "bootstrap_ci_low": ci_low,
        "bootstrap_ci_high": ci_high,
        "n_treatment": int(len(treatment_clean)),
        "n_reference": n_reference,
    }


def evidence_effect_summary(
    results: pd.DataFrame,
    treatment_variant: str = "affect",
    reference_variant: str = "no_affect",
    bootstrap_iterations: int = 1000,
    random_seed: int = 0,
) -> pd.DataFrame:
    """Summarize key write-up effect sizes and bootstrap intervals."""

    if results.empty:
        return pd.DataFrame()
    rows: list[dict] = []
    final = final_round_summary(results)
    final_metrics = [
        "total_payoff",
        "mean_q_pi_entropy",
        "mean_joint_accuracy",
        "mean_stance_accuracy",
    ]
    for metric in final_metrics:
        if metric not in final.columns:
            continue
        treatment = final.loc[final["variant_id"] == treatment_variant, metric]
        reference = final.loc[final["variant_id"] == reference_variant, metric]
        if treatment.empty or reference.empty:
            continue
        rows.append(
            _effect_row(
                readout="final",
                metric=metric,
                treatment_variant=treatment_variant,
                reference_variant=reference_variant,
                treatment_values=treatment,
                reference_values=reference,
                bootstrap_iterations=bootstrap_iterations,
                random_seed=random_seed,
            )
        )

    partner_fitness = partner_model_fitness_summary(results)
    if not partner_fitness.empty:
        for variant_id, group in partner_fitness.groupby("variant_id"):
            reward_proxy = group["reward_signal_mean"]
            if reward_proxy.notna().sum() < 3:
                reward_proxy = group["active_mean_payoff"]
            seed_rows = []
            for seed, seed_group in group.groupby("seed"):
                corr_surprise = _safe_corr(seed_group["precision_mean"], seed_group["surprise_mean"])
                corr_reward = _safe_corr(seed_group["precision_mean"], reward_proxy.loc[seed_group.index])
                if np.isfinite(corr_surprise) and np.isfinite(corr_reward):
                    seed_rows.append(
                        {
                            "seed": int(seed),
                            "dominance": abs(corr_surprise) - abs(corr_reward),
                        }
                    )
            seed_frame = pd.DataFrame(seed_rows)
            if seed_frame.empty:
                corr_surprise = _safe_corr(group["precision_mean"], group["surprise_mean"])
                corr_reward = _safe_corr(group["precision_mean"], reward_proxy)
                if np.isfinite(corr_surprise) and np.isfinite(corr_reward):
                    seed_frame = pd.DataFrame(
                        [{"seed": -1, "dominance": abs(corr_surprise) - abs(corr_reward)}]
                    )
            if not seed_frame.empty:
                rows.append(
                    _effect_row(
                        readout="model_fitness",
                        metric="abs_corr_precision_surprise_minus_reward",
                        treatment_variant=str(variant_id),
                        treatment_values=seed_frame["dominance"],
                        bootstrap_iterations=bootstrap_iterations,
                        random_seed=random_seed,
                    )
                )

    if has_switch_events(results):
        reallocation = betrayal_reallocation_summary(results)
        for metric in [
            "reencounters",
            "decisions_to_first_reencounter",
            "reencounter_selection_rate",
            "mean_payoff_on_reencounter",
            "mean_q_pi_entropy_on_reencounter",
        ]:
            if reallocation.empty or metric not in reallocation.columns:
                continue
            treatment = reallocation.loc[reallocation["variant_id"] == treatment_variant, metric]
            reference = reallocation.loc[reallocation["variant_id"] == reference_variant, metric]
            if treatment.empty or reference.empty:
                continue
            rows.append(
                _effect_row(
                    readout="betrayal_reallocation",
                    metric=metric,
                    treatment_variant=treatment_variant,
                    reference_variant=reference_variant,
                    treatment_values=treatment,
                    reference_values=reference,
                    bootstrap_iterations=bootstrap_iterations,
                    random_seed=random_seed,
                )
            )

        misdeployment = betrayal_misdeployment_summary(results)
        for metric in [
            "wrong_type_rate",
            "bad_payoff_rate",
            "low_entropy_rate",
            "overconfident_wrong_type_rate",
            "overconfident_bad_payoff_rate",
        ]:
            if misdeployment.empty or metric not in misdeployment.columns:
                continue
            treatment = misdeployment.loc[misdeployment["variant_id"] == treatment_variant, metric]
            reference = misdeployment.loc[misdeployment["variant_id"] == reference_variant, metric]
            if treatment.empty or reference.empty:
                continue
            rows.append(
                _effect_row(
                    readout="betrayal_misdeployment",
                    metric=metric,
                    treatment_variant=treatment_variant,
                    reference_variant=reference_variant,
                    treatment_values=treatment,
                    reference_values=reference,
                    bootstrap_iterations=bootstrap_iterations,
                    random_seed=random_seed,
                )
            )
    return pd.DataFrame(rows)


def model_fitness_correlation_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Correlate partner precision with surprise and reward for H1."""

    partner_summary = partner_model_fitness_summary(results)
    if partner_summary.empty:
        return pd.DataFrame()
    rows: list[dict] = []
    for variant_id, group in partner_summary.groupby("variant_id"):
        reward_proxy = group["reward_signal_mean"]
        reward_source = "reward_signal"
        if reward_proxy.notna().sum() < 3:
            reward_proxy = group["active_mean_payoff"]
            reward_source = "active_mean_payoff"
        corr_surprise = _safe_corr(group["precision_mean"], group["surprise_mean"])
        corr_reward = _safe_corr(group["precision_mean"], reward_proxy)
        rows.append(
            {
                "variant_id": str(variant_id),
                "n_partner_seed_units": int(len(group)),
                "reward_proxy": reward_source,
                "corr_precision_surprise": corr_surprise,
                "corr_precision_reward": corr_reward,
                "abs_corr_precision_surprise": abs(corr_surprise) if np.isfinite(corr_surprise) else np.nan,
                "abs_corr_precision_reward": abs(corr_reward) if np.isfinite(corr_reward) else np.nan,
                "surprise_dominates_reward": (
                    bool(abs(corr_surprise) > abs(corr_reward))
                    if np.isfinite(corr_surprise) and np.isfinite(corr_reward)
                    else False
                ),
            }
        )
    return pd.DataFrame(rows)


def betrayal_misdeployment_summary(
    results: pd.DataFrame,
    window: int = 10,
    entropy_quantile: float = 0.25,
    bad_payoff_threshold: float = 1.0,
) -> pd.DataFrame:
    """Summarize low-entropy bad outcomes after betrayal-style switches."""

    frame = results.copy()
    if frame.empty or not has_switch_events(frame):
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
    scheduled_type_map = _build_scheduled_switch_map(frame, "scheduled_switch_partner_ids", "scheduled_type")
    scheduled_stance_map = _build_scheduled_switch_map(frame, "scheduled_stance_switch_partner_ids", "scheduled_stance")
    observed_map = _build_observed_switch_map(frame)

    entropy_cutoffs = (
        frame.groupby("variant_id")["q_pi_entropy"].quantile(float(entropy_quantile)).to_dict()
        if "q_pi_entropy" in frame.columns
        else {}
    )
    rows: list[dict] = []
    for (variant_id, seed, partner_idx), group in frame.groupby(["variant_id", "seed", "partner_idx"]):
        group = group.sort_values("round")
        key = (variant_id, int(seed), int(partner_idx))
        switch_rounds = _switch_rounds_for_partner(key, scheduled_type_map, scheduled_stance_map, observed_map)
        for event_idx, (switch_round, switch_kind) in enumerate(switch_rounds):
            window_frame = group[group["round"] >= switch_round].head(int(window)).copy()
            cutoff = float(entropy_cutoffs.get(variant_id, np.nan))
            if window_frame.empty:
                rows.append(
                    {
                        "variant_id": str(variant_id),
                        "seed": int(seed),
                        "partner_idx": int(partner_idx),
                        "switch_event_idx": int(event_idx),
                        "switch_round": int(switch_round),
                        "switch_kind": str(switch_kind),
                        "window": int(window),
                        "encounters": 0,
                        "mean_payoff": np.nan,
                        "mean_q_pi_entropy": np.nan,
                        "wrong_type_rate": np.nan,
                        "bad_payoff_rate": np.nan,
                        "low_entropy_rate": np.nan,
                        "overconfident_wrong_type_rate": np.nan,
                        "overconfident_bad_payoff_rate": np.nan,
                        "selected_partner_rate": np.nan,
                        "entropy_cutoff": cutoff,
                    }
                )
                continue
            bad_payoff = window_frame["payoff"] <= float(bad_payoff_threshold)
            wrong_type = (
                window_frame["inferred_type_correct"] < 1.0
                if "inferred_type_correct" in window_frame.columns
                else pd.Series(False, index=window_frame.index)
            )
            low_entropy = (
                window_frame["q_pi_entropy"] <= cutoff
                if np.isfinite(cutoff) and "q_pi_entropy" in window_frame.columns
                else pd.Series(False, index=window_frame.index)
            )
            selected_partner_rate = (
                float((window_frame["selected_partner"] == int(partner_idx)).mean())
                if "selected_partner" in window_frame.columns
                else np.nan
            )
            rows.append(
                {
                    "variant_id": str(variant_id),
                    "seed": int(seed),
                    "partner_idx": int(partner_idx),
                    "switch_event_idx": int(event_idx),
                    "switch_round": int(switch_round),
                    "switch_kind": str(switch_kind),
                    "window": int(window),
                    "encounters": int(len(window_frame)),
                    "mean_payoff": float(window_frame["payoff"].mean()),
                    "mean_q_pi_entropy": (
                        float(window_frame["q_pi_entropy"].mean())
                        if "q_pi_entropy" in window_frame.columns
                        else np.nan
                    ),
                    "wrong_type_rate": float(wrong_type.mean()),
                    "bad_payoff_rate": float(bad_payoff.mean()),
                    "low_entropy_rate": float(low_entropy.mean()),
                    "overconfident_wrong_type_rate": float((low_entropy & wrong_type).mean()),
                    "overconfident_bad_payoff_rate": float((low_entropy & bad_payoff & wrong_type).mean()),
                    "selected_partner_rate": selected_partner_rate,
                    "entropy_cutoff": cutoff,
                }
            )
    return pd.DataFrame(rows)


def betrayal_reallocation_summary(
    results: pd.DataFrame,
    max_decisions: int | None = None,
) -> pd.DataFrame:
    """Summarize avoidance, return latency, and payoff conditional on re-encounter."""

    frame = results.copy()
    if frame.empty or not has_switch_events(frame):
        return pd.DataFrame()
    frame["_variant_sort"] = frame["variant_id"].apply(_variant_sort_key)
    frame = frame.sort_values(["_variant_sort", "seed", "round"]).drop(columns="_variant_sort")
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

    scheduled_type_map = _build_scheduled_switch_map(frame, "scheduled_switch_partner_ids", "scheduled_type")
    scheduled_stance_map = _build_scheduled_switch_map(frame, "scheduled_stance_switch_partner_ids", "scheduled_stance")
    observed_map = _build_observed_switch_map(frame)
    event_keys = sorted(
        set(scheduled_type_map) | set(scheduled_stance_map) | set(observed_map),
        key=lambda key: (_variant_sort_key(key[0]), key[1], key[2]),
    )
    if not event_keys:
        return pd.DataFrame()

    selector_column = "selected_partner" if "selected_partner" in frame.columns else "partner_idx"
    rows: list[dict] = []
    for key in event_keys:
        variant_id, seed, partner_idx = key
        run_frame = frame[(frame["variant_id"] == variant_id) & (frame["seed"].astype(int) == int(seed))]
        run_frame = run_frame.sort_values("round")
        switch_rounds = _switch_rounds_for_partner(key, scheduled_type_map, scheduled_stance_map, observed_map)
        for event_idx, (switch_round, switch_kind) in enumerate(switch_rounds):
            post_switch = run_frame[run_frame["round"] >= int(switch_round)].copy()
            if max_decisions is not None:
                post_switch = post_switch.head(int(max_decisions))
            selected = (
                post_switch[selector_column].astype(float) == float(partner_idx)
                if selector_column in post_switch.columns and not post_switch.empty
                else pd.Series(False, index=post_switch.index)
            )
            reencounters = post_switch[selected].copy()
            first_positions = np.flatnonzero(selected.to_numpy(dtype=bool))
            first_position = int(first_positions[0]) if first_positions.size else None
            first_round = int(reencounters["round"].iloc[0]) if not reencounters.empty else None
            post_switch_decisions = int(len(post_switch))
            rows.append(
                {
                    "variant_id": str(variant_id),
                    "seed": int(seed),
                    "partner_idx": int(partner_idx),
                    "switch_event_idx": int(event_idx),
                    "switch_round": int(switch_round),
                    "switch_kind": str(switch_kind),
                    "post_switch_decisions": post_switch_decisions,
                    "reencounters": int(len(reencounters)),
                    "returned_to_partner": bool(not reencounters.empty),
                    "decisions_to_first_reencounter": float(first_position) if first_position is not None else np.nan,
                    "rounds_to_first_reencounter": (
                        float(first_round - int(switch_round)) if first_round is not None else np.nan
                    ),
                    "reencounter_selection_rate": (
                        float(len(reencounters) / post_switch_decisions) if post_switch_decisions else np.nan
                    ),
                    "mean_payoff_on_reencounter": (
                        float(reencounters["payoff"].mean()) if not reencounters.empty else np.nan
                    ),
                    "mean_q_pi_entropy_on_reencounter": (
                        float(reencounters["q_pi_entropy"].mean())
                        if "q_pi_entropy" in reencounters.columns and not reencounters.empty
                        else np.nan
                    ),
                }
            )
    return pd.DataFrame(rows)


def post_switch_variant_comparison(results: pd.DataFrame, windows: tuple[int, ...] = (5, 10)) -> pd.DataFrame:
    """Compare paired variants in post-switch windows.

    Emits one row per switch window with pivoted metrics for each observed variant.
    """

    rows: list[pd.DataFrame] = []
    for window in windows:
        summary = post_switch_window_summary(results, window=window)
        if summary.empty:
            continue
        pivot = summary.pivot_table(
            index=["seed", "partner_idx", "switch_round"],
            columns="variant_id",
            values=["mean_payoff", "mean_accuracy"],
        )
        if pivot.empty:
            continue
        pivot.columns = [f"{metric}__variant_{variant}" for metric, variant in pivot.columns]
        pivot = pivot.reset_index()
        pivot["window"] = int(window)
        pivot["window_label"] = f"1-{int(window)}"
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
    for (variant_id, seed, partner_idx, switch_event_idx), group in trajectory.groupby(
        ["variant_id", "seed", "partner_idx", "switch_event_idx"],
    ):
        group = group.sort_values("encounters_since_switch")
        detection = group.loc[group["inferred_type_correct"] >= 1.0, "encounters_since_switch"]
        recovery = group.loc[group["payoff"] >= float(safe_payoff_threshold), "encounters_since_switch"]
        rows.append(
            {
                "variant_id": str(variant_id),
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
