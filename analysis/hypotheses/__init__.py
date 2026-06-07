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

HYPOTHESES = {
    "H0": "Policy Openness",
    "H1": "Model Fitness",
    "H2": "Deployment",
    "H3": "Locality Global Precision",
    "H4": "Social Allocation",
    "H5": "Timescale Volatility",
    "H6": "Perturbation Phenotypes",
    "H7": "Signal Source",
    "H8": "Observation Noise Robustness",
}

REQUIRED_SUMMARY_COLUMNS = {
    "variant_id",
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


def _summary_by_variant(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    if REQUIRED_SUMMARY_COLUMNS <= set(results.columns):
        return final_round_summary(results)

    frame = results.copy()
    if "variant_id" not in frame.columns:
        return pd.DataFrame()
    if "variant" not in frame.columns:
        frame["variant_id"] = frame["variant_id"]
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
    return frame.groupby(["variant_id", "seed"], as_index=False).agg(**agg)


def _variant_values(summary: pd.DataFrame, variant_id: str, column: str) -> np.ndarray:
    if summary.empty or column not in summary.columns:
        return np.asarray([], dtype=float)
    return summary.loc[summary["variant_id"] == variant_id, column].to_numpy(dtype=float)


def _paired_seed_differences(
    summary: pd.DataFrame,
    left_variant_id: str,
    right_variant_id: str,
    column: str,
) -> np.ndarray:
    if summary.empty or column not in summary.columns:
        return np.asarray([], dtype=float)
    left = summary.loc[summary["variant_id"] == left_variant_id, ["seed", column]].rename(
        columns={column: "left_value"}
    )
    right = summary.loc[summary["variant_id"] == right_variant_id, ["seed", column]].rename(
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
    variants = set(summary["variant_id"].dropna().astype(str)) if "variant_id" in summary.columns else set()
    for no_affect_name in sorted(variant for variant in variants if variant.startswith("no_affect")):
        suffix = no_affect_name.removeprefix("no_affect")
        affect_name = f"affect{suffix}"
        if affect_name not in variants:
            continue
        delta = _paired_seed_differences(summary, no_affect_name, affect_name, column)
        if delta.size == 0:
            continue
        mean_by_depth[len(mean_by_depth) + 1] = float(delta.mean())
        deltas.append(delta)
    if not deltas:
        return {}, np.asarray([], dtype=float)
    return mean_by_depth, np.concatenate(deltas)


def _switch_window_metric(
    results: pd.DataFrame,
    variant_id: str,
    column: str,
    *,
    window: int = 5,
) -> np.ndarray:
    if not has_switch_events(results):
        return np.asarray([], dtype=float)
    windows = post_switch_window_summary(results, window=window)
    if windows.empty or column not in windows.columns or variant_id not in set(windows["variant_id"]):
        return np.asarray([], dtype=float)
    return windows.loc[windows["variant_id"] == variant_id, column].to_numpy(dtype=float)


def _latency_metric(results: pd.DataFrame, variant_id: str, column: str) -> np.ndarray:
    if not has_switch_events(results):
        return np.asarray([], dtype=float)
    latency = betrayal_latency_summary(results, max_encounters=10)
    if latency.empty or column not in latency.columns or variant_id not in set(latency["variant_id"]):
        return np.asarray([], dtype=float)
    return latency.loc[latency["variant_id"] == variant_id, column].to_numpy(dtype=float)


def _variants(results: pd.DataFrame) -> set[str]:
    if "variant_id" not in results.columns:
        return set()
    return set(results["variant_id"].dropna().astype(str))


def test_h0_openness_gate(results: pd.DataFrame) -> dict[str, Any]:
    """Affect matters when the policy posterior has room to move."""

    summary = _summary_by_variant(results)
    payoff_gains_by_depth, payoff_deltas = _depth_gain_payload(summary, "total_payoff")
    entropy_by_variant = {}
    if "mean_q_pi_entropy" in summary.columns:
        entropy_by_variant = {
            str(variant): _mean(group["mean_q_pi_entropy"])
            for variant, group in summary.groupby("variant_id", sort=True)
        }
    available = bool(payoff_gains_by_depth) or bool(entropy_by_variant) or "payoff_mode" in results.columns
    return _payload(
        HYPOTHESES["H0"],
        available=available,
        summary={"claim": "policy-space openness gates affective precision effects"},
        evidence={
            "depths_evaluated": sorted(payoff_gains_by_depth),
            "mean_affect_payoff_gain": _mean(payoff_deltas),
            "payoff_gain_by_depth": payoff_gains_by_depth,
            "mean_q_pi_entropy_by_variant": entropy_by_variant,
            "payoff_modes": sorted(results["payoff_mode"].dropna().astype(str).unique())
            if "payoff_mode" in results.columns
            else [],
        },
        reason=None if available else "Requires depth-pair, policy entropy, or payoff-mode evidence.",
    )


def test_h1_model_fitness(results: pd.DataFrame) -> dict[str, Any]:
    """Per-partner affect tracks model fitness rather than cached reward."""

    summary = _summary_by_variant(results)
    reward_control_names = {"reward_average", "reward_control"}
    variant_ids = _variants(results)
    beta_columns = [column for column in ("betas", "terminal_values", "beta_mean") if column in results.columns]
    available = bool(beta_columns) or bool(variant_ids & reward_control_names)
    evidence = {
        "beta_signal_columns": beta_columns,
        "reward_control_variants": sorted(variant_ids & reward_control_names),
    }
    if "total_payoff" in summary.columns:
        evidence["mean_total_payoff_by_variant"] = {
            str(variant): _mean(group["total_payoff"])
            for variant, group in summary.groupby("variant_id", sort=True)
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

    summary = _summary_by_variant(results)
    lesion_name = "lesioned"
    intact_name = "affect"
    if lesion_name not in set(summary.get("variant_id", [])) or intact_name not in set(
        summary.get("variant_id", [])
    ):
        return _payload(
            HYPOTHESES["H2"],
            available=False,
            summary={"claim": "knowledge can remain intact while action deployment worsens"},
            reason="Requires lesioned and affect variants.",
        )

    accuracy_column = "mean_joint_accuracy" if "mean_joint_accuracy" in summary.columns else "mean_accuracy"
    lesion_accuracy = _variant_values(summary, lesion_name, accuracy_column)
    intact_accuracy = _variant_values(summary, intact_name, accuracy_column)
    lesion_payoff = _variant_values(summary, lesion_name, "total_payoff")
    intact_payoff = _variant_values(summary, intact_name, "total_payoff")
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
            "accuracy_difference_lesioned_minus_affect": accuracy_diff,
            "payoff_difference_lesioned_minus_affect": payoff_diff,
            "accuracy_margin": float(accuracy_margin),
            "payoff_welch": _welch_ttest(lesion_payoff, intact_payoff),
            "payoff_cohens_d": _cohen_d(lesion_payoff, intact_payoff),
        },
    )


def test_h3_locality(results: pd.DataFrame) -> dict[str, Any]:
    """Local beta should preserve partner-specific signal quality versus global beta."""

    variant_ids = _variants(results)
    local_present = bool(variant_ids & {"affect", "local_beta"})
    global_present = "global_beta" in variant_ids
    summary = _summary_by_variant(results)
    evidence: dict[str, Any] = {
        "local_variants": sorted(variant_ids & {"affect", "local_beta"}),
        "global_beta_present": global_present,
    }
    if "total_payoff" in summary.columns:
        evidence["mean_total_payoff_by_variant"] = {
            str(variant): _mean(group["total_payoff"])
            for variant, group in summary.groupby("variant_id", sort=True)
        }
    return _payload(
        HYPOTHESES["H3"],
        available=local_present and global_present,
        summary={"claim": "local beta and global beta separate signal quality from shared precision"},
        evidence=evidence,
        reason=None if local_present and global_present else "Requires local/affect and global_beta variants.",
    )


def test_h5_timescale_volatility(results: pd.DataFrame) -> dict[str, Any]:
    """Affect should matter most under betrayal, stance shifts, or partner volatility."""

    if not has_switch_events(results):
        return _payload(
            HYPOTHESES["H5"],
            available=False,
            summary={"claim": "affect should be most visible after social volatility"},
            reason="Requires scheduled or observed switch events.",
        )

    affect_name = "affect"
    control_name = "no_affect"
    affect_payoff = _switch_window_metric(results, affect_name, "mean_payoff", window=5)
    control_payoff = _switch_window_metric(results, control_name, "mean_payoff", window=5)
    affect_detection = _latency_metric(results, affect_name, "detection_latency")
    control_detection = _latency_metric(results, control_name, "detection_latency")
    available = affect_payoff.size > 0 and control_payoff.size > 0
    evidence = {
        "mean_post_switch_payoff_affect": _mean(affect_payoff),
        "mean_post_switch_payoff_no_affect": _mean(control_payoff),
        "payoff_difference_affect_minus_no_affect": (
            (_mean(affect_payoff) or 0.0) - (_mean(control_payoff) or 0.0) if available else None
        ),
        "detection_latency_difference_no_affect_minus_affect": (
            (_mean(control_detection) or 0.0) - (_mean(affect_detection) or 0.0)
            if affect_detection.size > 0 and control_detection.size > 0
            else None
        ),
        "payoff_welch": _welch_ttest(affect_payoff, control_payoff),
    }
    reason = None if available else "Requires affect and no_affect post-switch windows."
    return _payload(
        HYPOTHESES["H5"],
        available=available,
        summary={"claim": "post-switch behavior is the primary volatility readout"},
        evidence=evidence,
        reason=reason,
    )


def test_h4_social_allocation(results: pd.DataFrame) -> dict[str, Any]:
    """Per-partner affect should shape who the agent selects, avoids, or revisits."""

    partner_column = "selected_partner_idx" if "selected_partner_idx" in results.columns else "partner_idx"
    available = partner_column in results.columns and ("variant_id" in results.columns)
    counts: dict[str, dict[str, int]] = {}
    if available:
        grouped = results.groupby(["variant_id", partner_column]).size()
        for (variant_id, partner_idx), count in grouped.items():
            counts.setdefault(str(variant_id), {})[str(partner_idx)] = int(count)
    return _payload(
        HYPOTHESES["H4"],
        available=available,
        summary={"claim": "agent-choice settings expose partner approach and avoidance"},
        evidence={"partner_selection_counts": counts, "partner_column": partner_column if available else None},
        reason=None if available else "Requires partner-choice or partner-index columns.",
    )


def test_h6_perturbation_phenotypes(results: pd.DataFrame) -> dict[str, Any]:
    """Phenotype-inspired perturbations should separate by task regime."""

    perturbation_names = {"low_gain", "high_gain", "cautious_prior"}
    variant_ids = _variants(results)
    present = sorted(variant_ids & perturbation_names)
    summary = _summary_by_variant(results)
    evidence: dict[str, Any] = {"perturbation_variants": present}
    if present and "total_payoff" in summary.columns:
        evidence["mean_total_payoff_by_perturbation_variant"] = {
            variant: _mean(_variant_values(summary, variant, "total_payoff")) for variant in present
        }
    return _payload(
        HYPOTHESES["H6"],
        available=bool(present),
        summary={"claim": "perturbation phenotypes are task-regime dependent, not global traits"},
        evidence=evidence,
        reason=None if present else "Requires low_gain, high_gain, or cautious_prior variants.",
    )


def test_h7_signal_source(results: pd.DataFrame) -> dict[str, Any]:
    """Signal-source alternatives are future work unless explicit columns exist."""

    columns = [column for column in ("affect_signal_source", "prediction_error_source") if column in results.columns]
    return _payload(
        HYPOTHESES["H7"],
        available=bool(columns),
        summary={"claim": "partner-action surprisal should stay cleaner than joint surprise"},
        evidence={"signal_source_columns": columns},
        reason=None if columns else "Requires explicit signal-source variants or columns.",
    )


def test_h8_observation_noise(results: pd.DataFrame) -> dict[str, Any]:
    """Observation-noise robustness is exploratory unless noise conditions are present."""

    has_noise = "observation_noise" in results.columns
    noise_levels = (
        sorted(results["observation_noise"].dropna().astype(float).unique().tolist()) if has_noise else []
    )
    return _payload(
        HYPOTHESES["H8"],
        available=bool(noise_levels),
        summary={"claim": "beta inertia may stabilize or slow behavior under noisy observations"},
        evidence={"observation_noise_levels": noise_levels},
        reason=None if noise_levels else "Requires observation-noise conditions.",
    )


def run_all_hypothesis_tests(results: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Run the current H0-H8 behavior-card suite and return a JSON-safe dictionary."""

    return {
        "h0": test_h0_openness_gate(results),
        "h1": test_h1_model_fitness(results),
        "h2": test_h2_deployment(results),
        "h3": test_h3_locality(results),
        "h4": test_h4_social_allocation(results),
        "h5": test_h5_timescale_volatility(results),
        "h6": test_h6_perturbation_phenotypes(results),
        "h7": test_h7_signal_source(results),
        "h8": test_h8_observation_noise(results),
    }
