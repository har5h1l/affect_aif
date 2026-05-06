"""Hypothesis-specific checks for current Hesp-extension experiment outputs."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from analysis.metrics import (
    betrayal_latency_summary,
    final_round_summary,
    has_switch_events,
    post_switch_window_summary,
)

DEPTH_CONDITION_NAMES = {
    1: ("tau1_no_affect", "tau1_affect"),
    2: ("tau2_no_affect", "tau2_affect"),
    4: ("tau4_no_affect", "tau4_affect"),
    8: ("tau8_no_affect", "tau8_affect"),
}

HYPOTHESES = {
    "H0": "Openness Gate",
    "H1": "Model Fitness",
    "H2": "Deployment",
    "H3": "Stress Response",
    "H4": "Social Choice",
    "H5": "Perturbation Phenotypes",
}

REQUIRED_SUMMARY_COLUMNS = {
    "condition",
    "condition_name",
    "seed",
    "round",
    "payoff",
    "inferred_type_correct",
    "inferred_stance_correct",
    "inferred_joint_correct",
    "q_pi_entropy",
    "mean_abs_step_efe",
    "planning_cost",
    "planning_cost_ratio",
}


def _clean(values: Any) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    return array[np.isfinite(array)]


def _mean(values: Any) -> float | None:
    clean = _clean(values)
    if clean.size == 0:
        return None
    return float(clean.mean())


def _std(values: Any) -> float | None:
    clean = _clean(values)
    if clean.size < 2:
        return None
    return float(clean.std(ddof=1))


def _welch_ttest(values_a: Any, values_b: Any) -> dict[str, float | None]:
    sample_a = _clean(values_a)
    sample_b = _clean(values_b)
    if sample_a.size < 2 or sample_b.size < 2:
        return {"t_stat": None, "p_value": None}
    t_stat, p_value = stats.ttest_ind(sample_a, sample_b, equal_var=False)
    return {"t_stat": float(t_stat), "p_value": float(p_value)}


def _cohen_d(values_a: Any, values_b: Any) -> float | None:
    sample_a = _clean(values_a)
    sample_b = _clean(values_b)
    if sample_a.size < 2 or sample_b.size < 2:
        return None
    var_a = sample_a.var(ddof=1)
    var_b = sample_b.var(ddof=1)
    pooled_num = (sample_a.size - 1) * var_a + (sample_b.size - 1) * var_b
    pooled_den = sample_a.size + sample_b.size - 2
    if pooled_den <= 0:
        return None
    pooled_sd = math.sqrt(max(pooled_num / pooled_den, 0.0))
    if pooled_sd == 0.0:
        return 0.0
    return float((sample_a.mean() - sample_b.mean()) / pooled_sd)


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, np.ndarray):
        return [_json_safe(item) for item in value.tolist()]
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [_json_safe(item) for item in value]
    return value


def _payload(
    label: str,
    *,
    available: bool,
    summary: Mapping[str, Any],
    evidence: Mapping[str, Any] | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "available": bool(available),
        "hypothesis": label,
        "label": label.lower().replace(" ", "_").replace(",", ""),
        "summary": dict(summary),
        "evidence": dict(evidence or {}),
    }
    if reason:
        payload["reason"] = reason
        payload["summary"].setdefault("reason", reason)
    return _json_safe(payload)


def _summary_by_condition(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    if REQUIRED_SUMMARY_COLUMNS <= set(results.columns):
        return final_round_summary(results)

    frame = results.copy()
    if "condition_name" not in frame.columns:
        return pd.DataFrame()
    if "condition" not in frame.columns:
        frame["condition"] = frame["condition_name"]
    if "seed" not in frame.columns:
        frame["seed"] = 0
    if "payoff" not in frame.columns:
        frame["payoff"] = np.nan

    agg = {"total_payoff": ("payoff", "sum")}
    optional_columns = {
        "inferred_type_correct": "mean_accuracy",
        "inferred_stance_correct": "mean_stance_accuracy",
        "inferred_joint_correct": "mean_joint_accuracy",
        "q_pi_entropy": "mean_q_pi_entropy",
        "mean_abs_step_efe": "mean_abs_step_efe",
        "planning_cost": "planning_cost",
        "planning_cost_ratio": "planning_cost_ratio",
    }
    for column, output in optional_columns.items():
        if column in frame.columns:
            agg[output] = (column, "mean")
    return frame.groupby(["condition", "condition_name", "seed"], as_index=False).agg(**agg)


def _condition_values(summary: pd.DataFrame, condition_name: str, column: str) -> np.ndarray:
    if summary.empty or column not in summary.columns:
        return np.asarray([], dtype=float)
    return summary.loc[summary["condition_name"] == condition_name, column].to_numpy(dtype=float)


def _paired_seed_differences(
    summary: pd.DataFrame,
    left_condition_name: str,
    right_condition_name: str,
    column: str,
) -> np.ndarray:
    if summary.empty or column not in summary.columns:
        return np.asarray([], dtype=float)
    left = summary.loc[summary["condition_name"] == left_condition_name, ["seed", column]].rename(
        columns={column: "left_value"}
    )
    right = summary.loc[summary["condition_name"] == right_condition_name, ["seed", column]].rename(
        columns={column: "right_value"}
    )
    merged = left.merge(right, on="seed", how="inner")
    if merged.empty:
        return np.asarray([], dtype=float)
    deltas = merged["right_value"].to_numpy(dtype=float) - merged["left_value"].to_numpy(dtype=float)
    return _clean(deltas)


def _depth_gain_payload(summary: pd.DataFrame, column: str) -> tuple[dict[int, float], np.ndarray]:
    mean_by_depth: dict[int, float] = {}
    deltas: list[np.ndarray] = []
    for depth, (no_affect_name, affect_name) in DEPTH_CONDITION_NAMES.items():
        delta = _paired_seed_differences(summary, no_affect_name, affect_name, column)
        if delta.size == 0:
            continue
        mean_by_depth[int(depth)] = float(delta.mean())
        deltas.append(delta)
    if not deltas:
        return {}, np.asarray([], dtype=float)
    return mean_by_depth, np.concatenate(deltas)


def _switch_window_metric(
    results: pd.DataFrame,
    condition_name: str,
    column: str,
    *,
    window: int = 5,
) -> np.ndarray:
    if not has_switch_events(results):
        return np.asarray([], dtype=float)
    windows = post_switch_window_summary(results, window=window)
    if windows.empty or column not in windows.columns or condition_name not in set(windows["condition_name"]):
        return np.asarray([], dtype=float)
    return windows.loc[windows["condition_name"] == condition_name, column].to_numpy(dtype=float)


def _latency_metric(results: pd.DataFrame, condition_name: str, column: str) -> np.ndarray:
    if not has_switch_events(results):
        return np.asarray([], dtype=float)
    latency = betrayal_latency_summary(results, max_encounters=10)
    if latency.empty or column not in latency.columns or condition_name not in set(latency["condition_name"]):
        return np.asarray([], dtype=float)
    return latency.loc[latency["condition_name"] == condition_name, column].to_numpy(dtype=float)


def _conditions(results: pd.DataFrame) -> set[str]:
    if "condition_name" not in results.columns:
        return set()
    return set(results["condition_name"].dropna().astype(str))


def test_h0_openness_gate(results: pd.DataFrame) -> dict[str, Any]:
    """Affect matters when the policy posterior has room to move."""

    summary = _summary_by_condition(results)
    payoff_gains_by_depth, payoff_deltas = _depth_gain_payload(summary, "total_payoff")
    entropy_by_condition = {}
    if "mean_q_pi_entropy" in summary.columns:
        entropy_by_condition = {
            str(condition): _mean(group["mean_q_pi_entropy"])
            for condition, group in summary.groupby("condition_name", sort=True)
        }
    available = bool(payoff_gains_by_depth) or bool(entropy_by_condition) or "payoff_mode" in results.columns
    return _payload(
        HYPOTHESES["H0"],
        available=available,
        summary={"claim": "policy-space openness gates affective precision effects"},
        evidence={
            "depths_evaluated": sorted(payoff_gains_by_depth),
            "mean_affect_payoff_gain": _mean(payoff_deltas),
            "payoff_gain_by_depth": payoff_gains_by_depth,
            "mean_q_pi_entropy_by_condition": entropy_by_condition,
            "payoff_modes": sorted(results["payoff_mode"].dropna().astype(str).unique())
            if "payoff_mode" in results.columns
            else [],
        },
        reason=None if available else "Requires depth-pair, policy entropy, or payoff-mode evidence.",
    )


def test_h1_model_fitness(results: pd.DataFrame) -> dict[str, Any]:
    """Per-partner affect tracks model fitness rather than cached reward."""

    summary = _summary_by_condition(results)
    reward_control_names = {"reward_average", "reward_control", "tau2_reward_average"}
    condition_names = _conditions(results)
    beta_columns = [column for column in ("betas", "terminal_values", "beta_mean") if column in results.columns]
    available = bool(beta_columns) or bool(condition_names & reward_control_names)
    evidence = {
        "beta_signal_columns": beta_columns,
        "reward_control_conditions": sorted(condition_names & reward_control_names),
    }
    if "total_payoff" in summary.columns:
        evidence["mean_total_payoff_by_condition"] = {
            str(condition): _mean(group["total_payoff"])
            for condition, group in summary.groupby("condition_name", sort=True)
        }
    reason = None if available else "Requires beta or reward-control columns to test model fitness versus reward."
    return _payload(
        HYPOTHESES["H1"],
        available=available,
        summary={"claim": "precision tracks model reliability rather than partner reward"},
        evidence=evidence,
        reason=reason,
    )


def test_h2_deployment(results: pd.DataFrame, accuracy_margin: float = 0.05) -> dict[str, Any]:
    """Lesioned agents should preserve inference while impairing action deployment."""

    summary = _summary_by_condition(results)
    lesion_name = "lesioned"
    intact_name = "tau4_affect"
    if lesion_name not in set(summary.get("condition_name", [])) or intact_name not in set(
        summary.get("condition_name", [])
    ):
        return _payload(
            HYPOTHESES["H2"],
            available=False,
            summary={"claim": "knowledge can remain intact while action deployment worsens"},
            reason="Requires lesioned and tau4_affect conditions.",
        )

    accuracy_column = "mean_joint_accuracy" if "mean_joint_accuracy" in summary.columns else "mean_accuracy"
    lesion_accuracy = _condition_values(summary, lesion_name, accuracy_column)
    intact_accuracy = _condition_values(summary, intact_name, accuracy_column)
    lesion_payoff = _condition_values(summary, lesion_name, "total_payoff")
    intact_payoff = _condition_values(summary, intact_name, "total_payoff")
    accuracy_diff = (_mean(lesion_accuracy) or 0.0) - (_mean(intact_accuracy) or 0.0)
    payoff_diff = (_mean(lesion_payoff) or 0.0) - (_mean(intact_payoff) or 0.0)
    return _payload(
        HYPOTHESES["H2"],
        available=True,
        summary={
            "accuracy_preserved": abs(accuracy_diff) <= float(accuracy_margin),
            "deployment_impaired": payoff_diff < 0.0,
        },
        evidence={
            "accuracy_column": accuracy_column,
            "accuracy_difference_lesioned_minus_tau4_affect": accuracy_diff,
            "payoff_difference_lesioned_minus_tau4_affect": payoff_diff,
            "accuracy_margin": float(accuracy_margin),
            "payoff_welch": _welch_ttest(lesion_payoff, intact_payoff),
            "payoff_cohens_d": _cohen_d(lesion_payoff, intact_payoff),
        },
    )


def test_h3_stress_response(results: pd.DataFrame) -> dict[str, Any]:
    """Affect should matter most under betrayal, stance shifts, or partner volatility."""

    if not has_switch_events(results):
        return _payload(
            HYPOTHESES["H3"],
            available=False,
            summary={"claim": "affect should be most visible after social volatility"},
            reason="Requires scheduled or observed switch events.",
        )

    affect_name = "tau4_affect"
    control_name = "tau4_no_affect"
    affect_payoff = _switch_window_metric(results, affect_name, "mean_payoff", window=5)
    control_payoff = _switch_window_metric(results, control_name, "mean_payoff", window=5)
    affect_detection = _latency_metric(results, affect_name, "detection_latency")
    control_detection = _latency_metric(results, control_name, "detection_latency")
    available = affect_payoff.size > 0 and control_payoff.size > 0
    evidence = {
        "mean_post_switch_payoff_tau4_affect": _mean(affect_payoff),
        "mean_post_switch_payoff_tau4_no_affect": _mean(control_payoff),
        "payoff_difference_tau4_affect_minus_tau4_no_affect": (
            (_mean(affect_payoff) or 0.0) - (_mean(control_payoff) or 0.0) if available else None
        ),
        "detection_latency_difference_tau4_no_affect_minus_tau4_affect": (
            (_mean(control_detection) or 0.0) - (_mean(affect_detection) or 0.0)
            if affect_detection.size > 0 and control_detection.size > 0
            else None
        ),
        "payoff_welch": _welch_ttest(affect_payoff, control_payoff),
    }
    reason = None if available else "Requires tau4_affect and tau4_no_affect post-switch windows."
    return _payload(
        HYPOTHESES["H3"],
        available=available,
        summary={"claim": "post-switch behavior is the primary volatility readout"},
        evidence=evidence,
        reason=reason,
    )


def test_h4_social_choice(results: pd.DataFrame) -> dict[str, Any]:
    """Per-partner affect should shape who the agent selects, avoids, or revisits."""

    partner_column = "selected_partner_idx" if "selected_partner_idx" in results.columns else "partner_idx"
    available = partner_column in results.columns and ("condition_name" in results.columns)
    counts: dict[str, dict[str, int]] = {}
    if available:
        grouped = results.groupby(["condition_name", partner_column]).size()
        for (condition_name, partner_idx), count in grouped.items():
            counts.setdefault(str(condition_name), {})[str(partner_idx)] = int(count)
    return _payload(
        HYPOTHESES["H4"],
        available=available,
        summary={"claim": "agent-choice settings expose partner approach and avoidance"},
        evidence={"partner_selection_counts": counts, "partner_column": partner_column if available else None},
        reason=None if available else "Requires partner-choice or partner-index columns.",
    )


def test_h5_perturbation_phenotypes(results: pd.DataFrame) -> dict[str, Any]:
    """Clinical-like regimes should separate by task regime."""

    clinical_names = {"alexithymia", "borderline", "depression"}
    condition_names = _conditions(results)
    present = sorted(condition_names & clinical_names)
    summary = _summary_by_condition(results)
    evidence: dict[str, Any] = {"clinical_conditions": present}
    if present and "total_payoff" in summary.columns:
        evidence["mean_total_payoff_by_clinical_condition"] = {
            condition: _mean(_condition_values(summary, condition, "total_payoff")) for condition in present
        }
    return _payload(
        HYPOTHESES["H5"],
        available=bool(present),
        summary={"claim": "perturbation phenotypes are task-regime dependent, not global traits"},
        evidence=evidence,
        reason=None if present else "Requires alexithymia, borderline, or depression conditions.",
    )


def run_all_hypothesis_tests(results: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Run the current H0-H5 behavior-card suite and return a JSON-safe dictionary."""

    return {
        "h0": test_h0_openness_gate(results),
        "h1": test_h1_model_fitness(results),
        "h2": test_h2_deployment(results),
        "h3": test_h3_stress_response(results),
        "h4": test_h4_social_choice(results),
        "h5": test_h5_perturbation_phenotypes(results),
    }
