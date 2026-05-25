"""Tests for predictive model comparison (Phase 6)."""

import numpy as np
import pandas as pd

from analysis.model_comparison import (
    _spm_bms,
    model_comparison_report,
    pairwise_predictive_log_scores,
)
from experiments.trust.runner import ExperimentRunner


def test_log_evidence_tracked_in_agent_metrics(tiny_spec):
    """All native variant families should log finite evidence through the runner."""
    results = ExperimentRunner.from_spec(tiny_spec.with_overrides(rounds=5, replications=1)).run_all()
    assert results["round_log_evidence"].notna().all()
    assert results["cumulative_log_evidence"].notna().all()
    assert (results.groupby("variant_id")["cumulative_log_evidence"].last() < 0).all()


def test_log_evidence_logged_in_experiment_results(tiny_spec):
    """ExperimentRunner should log log-evidence columns in results."""
    runner = ExperimentRunner.from_spec(tiny_spec)
    results = runner.run_all()
    assert "round_log_evidence" in results.columns
    assert "cumulative_log_evidence" in results.columns
    assert results["round_log_evidence"].notna().all()
    assert results["cumulative_log_evidence"].notna().all()


def test_log_evidence_accumulates_correctly(tiny_spec):
    """Cumulative log-evidence at the last round should equal sum of per-round values."""
    runner = ExperimentRunner.from_spec(tiny_spec.with_overrides(rounds=10, replications=1))
    results = runner.run_all()

    for _, seed_data in results.groupby(["variant_id", "seed"]):
        seed_data = seed_data.sort_values("round")
        cumulative_last = seed_data["cumulative_log_evidence"].iloc[-1]
        sum_rounds = seed_data["round_log_evidence"].sum()
        assert abs(cumulative_last - sum_rounds) < 1e-6, (
            f"Cumulative ({cumulative_last}) != sum of rounds ({sum_rounds})"
        )


def test_final_round_summary_includes_log_evidence(tiny_spec):
    """final_round_summary should include total_log_evidence when available."""
    from analysis.metrics import final_round_summary

    runner = ExperimentRunner.from_spec(tiny_spec)
    results = runner.run_all()
    summary = final_round_summary(results)
    assert "total_log_evidence" in summary.columns
    assert summary["total_log_evidence"].notna().all()


def test_pairwise_predictive_log_scores_runs(tiny_spec):
    """pairwise_predictive_log_scores should produce valid output."""
    runner = ExperimentRunner.from_spec(tiny_spec.with_overrides(rounds=10, replications=3))
    results = runner.run_all()
    bf_table = pairwise_predictive_log_scores(results)

    assert len(bf_table) == 1
    assert "mean_predictive_log_score_difference" in bf_table.columns
    assert "log10_predictive_log_score_difference" in bf_table.columns
    assert bf_table["mean_predictive_log_score_difference"].notna().all()


def test_pairwise_predictive_log_scores_matches_by_seed():
    rows = []
    for variant_id, seed, total in [
        ("a", 1, 1_000.0),
        ("a", 2, 0.0),
        ("b", 2, 100.0),
        ("b", 3, -100.0),
    ]:
        rows.append(
            {
                "variant_id": variant_id,
                "seed": seed,
                "round": 0,
                "payoff": 1.0,
                "inferred_type_correct": 1.0,
                "inferred_stance_correct": 1.0,
                "inferred_joint_correct": 1.0,
                "q_pi_entropy": 0.0,
                "mean_abs_step_efe": 0.0,
                "planning_cost": 1.0,
                "planning_cost_ratio": 1.0,
                "cumulative_log_evidence": total,
            }
        )

    table = pairwise_predictive_log_scores(pd.DataFrame(rows))
    row = table.iloc[0]

    assert row["n_matched_seeds"] == 1
    assert np.isnan(row["prop_a_preferred"])


def test_spm_bms_recovers_strong_model():
    """RFX-BMS should assign high probability to the model with better evidence."""
    rng = np.random.default_rng(42)
    n_subjects = 50
    # Model 0 is clearly better (higher log-evidence)
    le_matrix = np.column_stack(
        [
            rng.normal(-50, 5, n_subjects),  # good model
            rng.normal(-100, 5, n_subjects),  # bad model
        ]
    )
    result = _spm_bms(le_matrix)
    assert result["expected_frequency"][0] > 0.9
    assert result["exceedance_probability"][0] > 0.99
    assert result["protected_exceedance_probability"][0] > 0.9


def test_spm_bms_indistinguishable_models():
    """When models are equal, BMS should give similar probabilities."""
    rng = np.random.default_rng(42)
    n_subjects = 50
    # Use the SAME samples for both models to ensure true indistinguishability
    shared = rng.normal(-75, 5, n_subjects)
    noise = rng.normal(0, 0.01, n_subjects)  # tiny noise to avoid identical columns
    le_matrix = np.column_stack([shared, shared + noise])
    result = _spm_bms(le_matrix)
    freq = result["expected_frequency"]
    assert abs(freq[0] - freq[1]) < 0.3, "Indistinguishable models should have similar frequencies"


def test_model_comparison_report_structure(tiny_spec):
    """model_comparison_report should return the expected structure."""
    runner = ExperimentRunner.from_spec(tiny_spec.with_overrides(rounds=10, replications=5))
    results = runner.run_all()
    report = model_comparison_report(results)

    assert "predictive_log_score_summary" in report
    assert "pairwise_predictive_log_scores" in report
    assert "random_effects_bms" in report
    assert len(report["predictive_log_score_summary"]) == 2
    assert len(report["pairwise_predictive_log_scores"]) == 1
