"""Hypothesis-specific statistical checks for experiment outputs."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from affect_aif.analysis.metrics import _ensure_array, final_round_summary, post_switch_window_summary


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


def _condition_values(summary: pd.DataFrame, condition: int, column: str) -> np.ndarray:
    return summary.loc[summary["condition"] == int(condition), column].to_numpy(dtype=float)


def test_h1_depth_compensation(results: pd.DataFrame) -> dict:
    """Condition 2 approaches condition 1 payoff despite shallower planning."""

    summary = _summary_by_condition(results)
    c1 = _condition_values(summary, 1, "total_payoff")
    c2 = _condition_values(summary, 2, "total_payoff")
    test = _welch_ttest(c2, c1)
    mean_c1 = _mean(c1)
    mean_c2 = _mean(c2)
    return {
        "hypothesis": "H1",
        "label": "depth_compensation",
        "available": True,
        "condition_1_mean_payoff": mean_c1,
        "condition_2_mean_payoff": mean_c2,
        "payoff_ratio_c2_over_c1": float(mean_c2 / mean_c1) if np.isfinite(mean_c1) and mean_c1 != 0.0 else float("nan"),
        "welch_t_stat": test["t_stat"],
        "welch_p_value": test["p_value"],
        "cohens_d": _cohen_d(c2, c1),
    }


def test_h2_lesion_dissociation(results: pd.DataFrame, accuracy_margin: float = 0.05) -> dict:
    """Condition 3 preserves identification accuracy better than payoff."""

    summary = _summary_by_condition(results)
    c1_acc = _condition_values(summary, 1, "mean_accuracy")
    c3_acc = _condition_values(summary, 3, "mean_accuracy")
    c2_payoff = _condition_values(summary, 2, "total_payoff")
    c3_payoff = _condition_values(summary, 3, "total_payoff")
    acc_test = _welch_ttest(c3_acc, c1_acc)
    payoff_test = _welch_ttest(c3_payoff, c2_payoff)
    acc_diff = _mean(c3_acc) - _mean(c1_acc)
    payoff_diff = _mean(c3_payoff) - _mean(c2_payoff)
    return {
        "hypothesis": "H2",
        "label": "lesion_dissociation",
        "available": True,
        "condition_1_mean_accuracy": _mean(c1_acc),
        "condition_3_mean_accuracy": _mean(c3_acc),
        "accuracy_difference_c3_minus_c1": acc_diff,
        "accuracy_within_margin": bool(np.isfinite(acc_diff) and abs(acc_diff) <= float(accuracy_margin)),
        "accuracy_margin": float(accuracy_margin),
        "accuracy_welch_t_stat": acc_test["t_stat"],
        "accuracy_welch_p_value": acc_test["p_value"],
        "condition_2_mean_payoff": _mean(c2_payoff),
        "condition_3_mean_payoff": _mean(c3_payoff),
        "payoff_difference_c3_minus_c2": payoff_diff,
        "payoff_lower_than_c2": bool(np.isfinite(payoff_diff) and payoff_diff < 0.0),
        "payoff_welch_t_stat": payoff_test["t_stat"],
        "payoff_welch_p_value": payoff_test["p_value"],
    }


def test_h3_precision_vs_reward(results: pd.DataFrame) -> dict:
    """Condition 2 outperforms reward averaging, especially against exploiters."""

    summary = _summary_by_condition(results)
    c2 = _condition_values(summary, 2, "total_payoff")
    c5 = _condition_values(summary, 5, "total_payoff")
    overall_test = _welch_ttest(c2, c5)

    exploiter = (
        results[results["true_partner_type"] == "exploiter"]
        .groupby(["condition", "seed"], as_index=False)
        .agg(
            mean_payoff=("payoff", "mean"),
            exploitation_rate=("partner_action", lambda x: float(np.mean(np.asarray(x, dtype=float) == 1.0))),
        )
    )
    c2_exploit = exploiter.loc[exploiter["condition"] == 2, "mean_payoff"].to_numpy(dtype=float)
    c5_exploit = exploiter.loc[exploiter["condition"] == 5, "mean_payoff"].to_numpy(dtype=float)
    c2_exploitation_rate = exploiter.loc[exploiter["condition"] == 2, "exploitation_rate"].to_numpy(dtype=float)
    c5_exploitation_rate = exploiter.loc[exploiter["condition"] == 5, "exploitation_rate"].to_numpy(dtype=float)
    exploiter_test = _welch_ttest(c2_exploit, c5_exploit)

    return {
        "hypothesis": "H3",
        "label": "precision_vs_reward",
        "available": True,
        "condition_2_mean_payoff": _mean(c2),
        "condition_5_mean_payoff": _mean(c5),
        "payoff_difference_c2_minus_c5": _mean(c2) - _mean(c5),
        "welch_t_stat": overall_test["t_stat"],
        "welch_p_value": overall_test["p_value"],
        "cohens_d": _cohen_d(c2, c5),
        "exploiter_mean_payoff_c2": _mean(c2_exploit),
        "exploiter_mean_payoff_c5": _mean(c5_exploit),
        "exploiter_payoff_difference_c2_minus_c5": _mean(c2_exploit) - _mean(c5_exploit),
        "exploiter_welch_t_stat": exploiter_test["t_stat"],
        "exploiter_welch_p_value": exploiter_test["p_value"],
        "exploitation_rate_c2": _mean(c2_exploitation_rate),
        "exploitation_rate_c5": _mean(c5_exploitation_rate),
    }


def test_h4_noise_robustness(results: pd.DataFrame, window: int = 10) -> dict:
    """Compare post-switch behavior in the configured switch window."""

    windows = post_switch_window_summary(results, window=window)
    if windows.empty:
        return {
            "hypothesis": "H4",
            "label": "noise_robustness",
            "available": False,
            "reason": "No switch windows were found in the results.",
        }

    def _window_values(condition: int, column: str) -> np.ndarray:
        return windows.loc[windows["condition"] == int(condition), column].to_numpy(dtype=float)

    c2_payoff = _window_values(2, "mean_payoff")
    c1_payoff = _window_values(1, "mean_payoff")
    c4_payoff = _window_values(4, "mean_payoff")
    c2_accuracy = _window_values(2, "mean_accuracy")
    c1_accuracy = _window_values(1, "mean_accuracy")
    c4_accuracy = _window_values(4, "mean_accuracy")
    test_c2_c1 = _welch_ttest(c2_payoff, c1_payoff)
    test_c2_c4 = _welch_ttest(c2_payoff, c4_payoff)

    return {
        "hypothesis": "H4",
        "label": "noise_robustness",
        "available": True,
        "window": int(window),
        "condition_2_post_switch_payoff": _mean(c2_payoff),
        "condition_1_post_switch_payoff": _mean(c1_payoff),
        "condition_4_post_switch_payoff": _mean(c4_payoff),
        "condition_2_post_switch_accuracy": _mean(c2_accuracy),
        "condition_1_post_switch_accuracy": _mean(c1_accuracy),
        "condition_4_post_switch_accuracy": _mean(c4_accuracy),
        "payoff_difference_c2_minus_c1": _mean(c2_payoff) - _mean(c1_payoff),
        "payoff_difference_c2_minus_c4": _mean(c2_payoff) - _mean(c4_payoff),
        "welch_t_stat_c2_vs_c1": test_c2_c1["t_stat"],
        "welch_p_value_c2_vs_c1": test_c2_c1["p_value"],
        "welch_t_stat_c2_vs_c4": test_c2_c4["t_stat"],
        "welch_p_value_c2_vs_c4": test_c2_c4["p_value"],
    }


def test_h5_partner_selection(results: pd.DataFrame) -> dict:
    """Estimate whether higher β is associated with more partner selection in variant B."""

    if "raw_action" not in results.columns or not (results["raw_action"] > 1).any():
        return {
            "hypothesis": "H5",
            "label": "partner_selection",
            "available": False,
            "reason": "Partner selection is only available when assignment_mode='agent_choice' (variant B-style runs).",
        }

    affective = results[results["condition"] == 2].copy()
    if affective.empty:
        return {
            "hypothesis": "H5",
            "label": "partner_selection",
            "available": False,
            "reason": "Condition 2 rows are missing from the results.",
        }

    records: list[dict] = []
    for seed, group in affective.groupby("seed"):
        group = group.sort_values("round")
        selections = group["partner_idx"].value_counts().to_dict()
        beta_by_partner: dict[int, list[float]] = {}
        max_len = 0
        for _, row in group.iterrows():
            betas = _ensure_array(row["betas"])
            max_len = max(max_len, len(betas))
            for partner_idx, beta in enumerate(betas):
                beta_by_partner.setdefault(int(partner_idx), []).append(float(beta))
        partner_rows = []
        for partner_idx in range(max_len):
            beta_values = beta_by_partner.get(partner_idx, [])
            partner_rows.append(
                {
                    "partner_idx": int(partner_idx),
                    "mean_beta": _mean(beta_values),
                    "selection_count": int(selections.get(partner_idx, 0)),
                }
            )
        partner_frame = pd.DataFrame(partner_rows)
        if len(partner_frame) < 2 or partner_frame["selection_count"].nunique() < 2:
            continue
        corr = partner_frame["mean_beta"].corr(partner_frame["selection_count"])
        if np.isfinite(corr):
            records.append({"seed": int(seed), "beta_selection_corr": float(corr)})

    correlations = np.asarray([row["beta_selection_corr"] for row in records], dtype=float)
    if correlations.size == 0:
        return {
            "hypothesis": "H5",
            "label": "partner_selection",
            "available": False,
            "reason": "Insufficient variation to estimate beta-selection correlations.",
        }

    t_stat, p_value = (float("nan"), float("nan"))
    if correlations.size >= 2:
        t_stat, p_value = stats.ttest_1samp(correlations, popmean=0.0)

    return {
        "hypothesis": "H5",
        "label": "partner_selection",
        "available": True,
        "num_seeds": int(correlations.size),
        "mean_beta_selection_correlation": float(correlations.mean()),
        "std_beta_selection_correlation": _std(correlations),
        "positive_seed_fraction": float(np.mean(correlations > 0.0)),
        "t_stat_vs_zero": float(t_stat),
        "p_value_vs_zero": float(p_value),
    }


def run_all_hypothesis_tests(results: pd.DataFrame) -> dict:
    """Run the full H1-H5 suite and return a JSON-safe dictionary."""

    tests = {
        "h1": test_h1_depth_compensation(results),
        "h2": test_h2_lesion_dissociation(results),
        "h3": test_h3_precision_vs_reward(results),
        "h4": test_h4_noise_robustness(results),
        "h5": test_h5_partner_selection(results),
    }
    return {"tests": tests}
