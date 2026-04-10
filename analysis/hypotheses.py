"""Hypothesis-specific statistical checks for experiment outputs."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from analysis.metrics import betrayal_latency_summary, final_round_summary, post_switch_window_summary


DEPTH_CONDITION_NAMES = {
    1: ("tau1_no_affect", "tau1_affect"),
    2: ("tau2_no_affect", "tau2_affect"),
    4: ("tau4_no_affect", "tau4_affect"),
    8: ("tau8_no_affect", "tau8_affect"),
}


def _clean(values) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    return array[np.isfinite(array)]


def _mean(values) -> float:
    clean = _clean(values)
    if clean.size == 0:
        return float("nan")
    return float(clean.mean())


def _std(values) -> float:
    clean = _clean(values)
    if clean.size < 2:
        return float("nan")
    return float(clean.std(ddof=1))


def _welch_ttest(values_a, values_b) -> dict:
    sample_a = _clean(values_a)
    sample_b = _clean(values_b)
    if sample_a.size < 2 or sample_b.size < 2:
        return {"t_stat": float("nan"), "p_value": float("nan")}
    t_stat, p_value = stats.ttest_ind(sample_a, sample_b, equal_var=False)
    return {"t_stat": float(t_stat), "p_value": float(p_value)}


def _cohen_d(values_a, values_b) -> float:
    sample_a = _clean(values_a)
    sample_b = _clean(values_b)
    if sample_a.size < 2 or sample_b.size < 2:
        return float("nan")
    var_a = sample_a.var(ddof=1)
    var_b = sample_b.var(ddof=1)
    pooled_num = (sample_a.size - 1) * var_a + (sample_b.size - 1) * var_b
    pooled_den = sample_a.size + sample_b.size - 2
    if pooled_den <= 0:
        return float("nan")
    pooled_sd = math.sqrt(max(pooled_num / pooled_den, 0.0))
    if pooled_sd == 0.0:
        return 0.0
    return float((sample_a.mean() - sample_b.mean()) / pooled_sd)


def _summary_by_condition(results: pd.DataFrame) -> pd.DataFrame:
    return final_round_summary(results)


def _condition_values(summary: pd.DataFrame, condition_name: str, column: str) -> np.ndarray:
    return summary.loc[summary["condition_name"] == condition_name, column].to_numpy(dtype=float)


def _paired_seed_differences(
    summary: pd.DataFrame,
    left_condition_name: str,
    right_condition_name: str,
    column: str,
) -> np.ndarray:
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
    windows = post_switch_window_summary(results, window=window)
    if windows.empty or condition_name not in set(windows["condition_name"]):
        return np.asarray([], dtype=float)
    return windows.loc[windows["condition_name"] == condition_name, column].to_numpy(dtype=float)


def _latency_metric(results: pd.DataFrame, condition_name: str, column: str) -> np.ndarray:
    latency = betrayal_latency_summary(results, max_encounters=10)
    if latency.empty or condition_name not in set(latency["condition_name"]):
        return np.asarray([], dtype=float)
    return latency.loc[latency["condition_name"] == condition_name, column].to_numpy(dtype=float)


def test_h1_orthogonal_augmentation(results: pd.DataFrame) -> dict:
    """Affect adds value beyond matched planning depth across the core depth sweep."""

    summary = _summary_by_condition(results)
    payoff_gains_by_depth, payoff_deltas = _depth_gain_payload(summary, "total_payoff")
    joint_gains_by_depth, joint_deltas = _depth_gain_payload(summary, "mean_joint_accuracy")
    if payoff_deltas.size == 0:
        return {
            "hypothesis": "H1",
            "label": "orthogonal_augmentation",
            "available": False,
            "reason": "Matched affect/no-affect depth pairs are missing from the results.",
        }

    test = _welch_ttest(payoff_deltas, np.zeros_like(payoff_deltas))
    overall_baseline = []
    overall_affect = []
    for no_affect_name, affect_name in DEPTH_CONDITION_NAMES.values():
        overall_baseline.extend(_condition_values(summary, no_affect_name, "total_payoff"))
        overall_affect.extend(_condition_values(summary, affect_name, "total_payoff"))
    interaction_range = (
        float(max(payoff_gains_by_depth.values()) - min(payoff_gains_by_depth.values()))
        if len(payoff_gains_by_depth) >= 2
        else float("nan")
    )

    return {
        "hypothesis": "H1",
        "label": "orthogonal_augmentation",
        "available": True,
        "depths_evaluated": sorted(payoff_gains_by_depth),
        "mean_affect_payoff_gain": _mean(payoff_deltas),
        "mean_affect_joint_accuracy_gain": _mean(joint_deltas),
        "payoff_gain_by_depth": {str(depth): value for depth, value in payoff_gains_by_depth.items()},
        "joint_accuracy_gain_by_depth": {str(depth): value for depth, value in joint_gains_by_depth.items()},
        "interaction_range": interaction_range,
        "payoff_ratio_affect_over_no_affect": (
            float(_mean(overall_affect) / _mean(overall_baseline))
            if np.isfinite(_mean(overall_baseline)) and _mean(overall_baseline) != 0.0
            else float("nan")
        ),
        "welch_t_stat": test["t_stat"],
        "welch_p_value": test["p_value"],
        "cohens_d": _cohen_d(payoff_deltas, np.zeros_like(payoff_deltas)),
    }


def test_h2_depth_matters(results: pd.DataFrame) -> dict:
    """Deeper planning helps in the action-dependent trust environment."""

    summary = _summary_by_condition(results)
    tau1 = _condition_values(summary, "tau1_no_affect", "total_payoff")
    tau8 = _condition_values(summary, "tau8_no_affect", "total_payoff")
    if tau1.size == 0 or tau8.size == 0:
        return {
            "hypothesis": "H2",
            "label": "depth_matters",
            "available": False,
            "reason": "Tau-1 and tau-8 no-affect conditions are required.",
        }

    no_affect_curve = {
        str(depth): _mean(_condition_values(summary, condition_names[0], "total_payoff"))
        for depth, condition_names in DEPTH_CONDITION_NAMES.items()
    }
    test = _welch_ttest(tau8, tau1)
    return {
        "hypothesis": "H2",
        "label": "depth_matters",
        "available": True,
        "mean_payoff_tau1_no_affect": _mean(tau1),
        "mean_payoff_tau8_no_affect": _mean(tau8),
        "payoff_difference_tau8_minus_tau1": _mean(tau8) - _mean(tau1),
        "no_affect_payoff_curve": no_affect_curve,
        "welch_t_stat": test["t_stat"],
        "welch_p_value": test["p_value"],
        "cohens_d": _cohen_d(tau8, tau1),
    }


def test_h3_lesion_dissociation(results: pd.DataFrame, accuracy_margin: float = 0.05) -> dict:
    """Lesioned agents preserve type inference better than stance recovery."""

    summary = _summary_by_condition(results)
    switch_source = post_switch_window_summary(results, window=5)
    if switch_source.empty:
        switch_source = summary.rename(
            columns={
                "mean_accuracy": "mean_accuracy",
                "mean_stance_accuracy": "mean_stance_accuracy",
                "total_payoff": "mean_payoff",
            }
        )
    lesion_name = "lesioned"
    intact_name = "tau4_affect"
    if lesion_name not in set(summary["condition_name"]) or intact_name not in set(summary["condition_name"]):
        return {
            "hypothesis": "H3",
            "label": "lesion_dissociation",
            "available": False,
            "reason": "Tau-4 affective and lesioned runs are required.",
        }

    lesion_type = _condition_values(summary, lesion_name, "mean_accuracy")
    intact_type = _condition_values(summary, intact_name, "mean_accuracy")
    lesion_window = switch_source.loc[switch_source["condition_name"] == lesion_name]
    intact_window = switch_source.loc[switch_source["condition_name"] == intact_name]
    lesion_stance = lesion_window["mean_stance_accuracy"].to_numpy(dtype=float)
    intact_stance = intact_window["mean_stance_accuracy"].to_numpy(dtype=float)
    lesion_payoff = lesion_window["mean_payoff"].to_numpy(dtype=float)
    intact_payoff = intact_window["mean_payoff"].to_numpy(dtype=float)

    type_diff = _mean(lesion_type) - _mean(intact_type)
    stance_diff = _mean(lesion_stance) - _mean(intact_stance)
    payoff_diff = _mean(lesion_payoff) - _mean(intact_payoff)
    return {
        "hypothesis": "H3",
        "label": "lesion_dissociation",
        "available": True,
        "type_accuracy_difference_lesioned_minus_tau4_affect": type_diff,
        "stance_accuracy_difference_lesioned_minus_tau4_affect": stance_diff,
        "payoff_difference_lesioned_minus_tau4_affect": payoff_diff,
        "type_accuracy_preserved": bool(np.isfinite(type_diff) and abs(type_diff) <= float(accuracy_margin)),
        "stance_recovery_worse_than_intact": bool(np.isfinite(stance_diff) and stance_diff < 0.0),
        "payoff_lower_than_intact": bool(np.isfinite(payoff_diff) and payoff_diff < 0.0),
        "accuracy_margin": float(accuracy_margin),
    }


def test_h4_betrayal_recovery(results: pd.DataFrame) -> dict:
    """Affect should improve betrayal detection and recovery over matched-depth no-affect controls."""

    affect_name = "tau4_affect"
    control_name = "tau4_no_affect"
    affect_payoff = _switch_window_metric(results, affect_name, "mean_payoff", window=5)
    control_payoff = _switch_window_metric(results, control_name, "mean_payoff", window=5)
    affect_detection = _latency_metric(results, affect_name, "detection_latency")
    control_detection = _latency_metric(results, control_name, "detection_latency")
    affect_recovery = _latency_metric(results, affect_name, "payoff_recovery_latency")
    control_recovery = _latency_metric(results, control_name, "payoff_recovery_latency")
    if affect_payoff.size == 0 or control_payoff.size == 0:
        return {
            "hypothesis": "H4",
            "label": "betrayal_recovery",
            "available": False,
            "reason": "Scheduled stance-switch runs for tau-4 affect and tau-4 no-affect are required.",
        }

    payoff_test = _welch_ttest(affect_payoff, control_payoff)
    return {
        "hypothesis": "H4",
        "label": "betrayal_recovery",
        "available": True,
        "mean_post_switch_payoff_tau4_affect": _mean(affect_payoff),
        "mean_post_switch_payoff_tau4_no_affect": _mean(control_payoff),
        "payoff_difference_tau4_affect_minus_tau4_no_affect": _mean(affect_payoff) - _mean(control_payoff),
        "detection_latency_difference_tau4_no_affect_minus_tau4_affect": (
            _mean(control_detection) - _mean(affect_detection)
        ),
        "recovery_latency_difference_tau4_no_affect_minus_tau4_affect": (
            _mean(control_recovery) - _mean(affect_recovery)
        ),
        "welch_t_stat": payoff_test["t_stat"],
        "welch_p_value": payoff_test["p_value"],
    }


def test_h5_precision_vs_reward(results: pd.DataFrame) -> dict:
    """Precision tracking should beat reward averaging around stance shifts."""

    affect_name = "tau4_affect"
    reward_name = "reward_average"
    affect_payoff = _switch_window_metric(results, affect_name, "mean_payoff", window=5)
    reward_payoff = _switch_window_metric(results, reward_name, "mean_payoff", window=5)
    affect_detection = _latency_metric(results, affect_name, "detection_latency")
    reward_detection = _latency_metric(results, reward_name, "detection_latency")
    affect_stance = _switch_window_metric(results, affect_name, "mean_stance_accuracy", window=5)
    reward_stance = _switch_window_metric(results, reward_name, "mean_stance_accuracy", window=5)
    if affect_payoff.size == 0 or reward_payoff.size == 0:
        return {
            "hypothesis": "H5",
            "label": "precision_vs_reward",
            "available": False,
            "reason": "Tau-4 affect and reward-average preset runs are required.",
        }

    overall_test = _welch_ttest(affect_payoff, reward_payoff)
    return {
        "hypothesis": "H5",
        "label": "precision_vs_reward",
        "available": True,
        "mean_post_switch_payoff_tau4_affect": _mean(affect_payoff),
        "mean_post_switch_payoff_reward_average": _mean(reward_payoff),
        "payoff_difference_tau4_affect_minus_reward_average": _mean(affect_payoff) - _mean(reward_payoff),
        "stance_accuracy_difference_tau4_affect_minus_reward_average": _mean(affect_stance) - _mean(reward_stance),
        "detection_latency_difference_reward_average_minus_tau4_affect": (
            _mean(reward_detection) - _mean(affect_detection)
        ),
        "welch_t_stat": overall_test["t_stat"],
        "welch_p_value": overall_test["p_value"],
        "cohens_d": _cohen_d(affect_payoff, reward_payoff),
    }


def run_all_hypothesis_tests(results: pd.DataFrame) -> dict:
    """Run the current H1-H5 suite and return a JSON-safe dictionary."""

    tests = {
        "h1": test_h1_orthogonal_augmentation(results),
        "h2": test_h2_depth_matters(results),
        "h3": test_h3_lesion_dissociation(results),
        "h4": test_h4_betrayal_recovery(results),
        "h5": test_h5_precision_vs_reward(results),
    }
    return {"tests": tests}


test_h1_depth_compensation = test_h1_orthogonal_augmentation
