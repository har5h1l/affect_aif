"""Tests for predictive model comparison (Phase 6)."""

import numpy as np

from analysis.model_comparison import (
    _spm_bms,
    model_comparison_report,
    pairwise_predictive_log_scores,
)
from experiments.trust.config import ExperimentConfig
from experiments.trust.runner import ExperimentRunner


def test_log_evidence_tracked_in_agent_metrics(representative_agents, tiny_model):
    """All native condition families should log finite evidence through the runner."""
    del representative_agents, tiny_model
    config = ExperimentConfig(num_rounds=5, num_replications=1, random_seed=0, conditions=[1, 2], presets=["lesioned"])
    results = ExperimentRunner(config).run_all()
    assert results["round_log_evidence"].notna().all()
    assert results["cumulative_log_evidence"].notna().all()
    assert (results.groupby("condition")["cumulative_log_evidence"].last() < 0).all()


def test_log_evidence_logged_in_experiment_results(tiny_config):
    """ExperimentRunner should log log-evidence columns in results."""
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2]})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    assert "round_log_evidence" in results.columns
    assert "cumulative_log_evidence" in results.columns
    assert results["round_log_evidence"].notna().all()
    assert results["cumulative_log_evidence"].notna().all()


def test_log_evidence_accumulates_correctly(tiny_config):
    """Cumulative log-evidence at the last round should equal sum of per-round values."""
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [2], "num_rounds": 10})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()

    for seed in results["seed"].unique():
        seed_data = results[results["seed"] == seed].sort_values("round")
        cumulative_last = seed_data["cumulative_log_evidence"].iloc[-1]
        sum_rounds = seed_data["round_log_evidence"].sum()
        assert abs(cumulative_last - sum_rounds) < 1e-6, (
            f"Cumulative ({cumulative_last}) != sum of rounds ({sum_rounds})"
        )


def test_final_round_summary_includes_log_evidence(tiny_config):
    """final_round_summary should include total_log_evidence when available."""
    from analysis.metrics import final_round_summary

    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2]})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    summary = final_round_summary(results)
    assert "total_log_evidence" in summary.columns
    assert summary["total_log_evidence"].notna().all()


def test_pairwise_predictive_log_scores_runs(tiny_config):
    """pairwise_predictive_log_scores should produce valid output."""
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2, 4], "num_replications": 3, "num_rounds": 10})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    bf_table = pairwise_predictive_log_scores(results)

    assert len(bf_table) == 3  # C(3,2) = 3 pairs
    assert "mean_predictive_log_score_difference" in bf_table.columns
    assert "log10_predictive_log_score_difference" in bf_table.columns
    assert bf_table["mean_predictive_log_score_difference"].notna().all()


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


def test_model_comparison_report_structure(tiny_config):
    """model_comparison_report should return the expected structure."""
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2], "num_replications": 5, "num_rounds": 10})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    report = model_comparison_report(results)

    assert "predictive_log_score_summary" in report
    assert "pairwise_predictive_log_scores" in report
    assert "random_effects_bms" in report
    assert len(report["predictive_log_score_summary"]) == 2  # 2 conditions
    assert len(report["pairwise_predictive_log_scores"]) == 1  # 1 pair
