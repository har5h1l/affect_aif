"""Tests for Bayesian model comparison (Phase 6)."""

import numpy as np

from affect_aif.analysis.model_comparison import (
    _spm_bms,
    model_comparison_report,
    pairwise_bayes_factors,
)
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner


def test_log_evidence_tracked_in_agent_metrics(representative_agents, tiny_model):
    """All agent types should produce finite log-evidence after observing outcomes."""
    from affect_aif.environment.trust_game import TrustGameEnv

    config = ExperimentConfig(num_rounds=5, num_replications=1, calibration_episodes=1, random_seed=0)
    env = TrustGameEnv(config, seed=0)

    for name, agent in representative_agents.items():
        agent.reset()
        init_result = env.reset()
        active = init_result["active_partner"]

        for _ in range(5):
            action = agent.plan_and_act(active)
            result = env.step(action)
            agent.observe_outcome(
                partner_idx=result["partner_idx"],
                observation=result["observation"],
                action_taken=result["agent_action"],
                partner_action=result["partner_action"],
                payoff=result["agent_payoff"],
                true_partner_type=result["true_partner_type"],
            )
            active = result["active_partner"]

        metrics = agent.get_metrics()
        assert "round_log_evidence" in metrics, f"{name} missing round_log_evidence"
        assert "cumulative_log_evidence" in metrics, f"{name} missing cumulative_log_evidence"
        assert np.isfinite(metrics["round_log_evidence"]), f"{name} round_log_evidence not finite"
        assert np.isfinite(metrics["cumulative_log_evidence"]), f"{name} cumulative_log_evidence not finite"
        assert metrics["cumulative_log_evidence"] < 0, f"{name} cumulative should be negative (log-prob)"


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
    from affect_aif.analysis.metrics import final_round_summary

    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2]})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    summary = final_round_summary(results)
    assert "total_log_evidence" in summary.columns
    assert summary["total_log_evidence"].notna().all()


def test_pairwise_bayes_factors_runs(tiny_config):
    """pairwise_bayes_factors should produce valid output."""
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2, 4], "num_replications": 3, "num_rounds": 10})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    bf_table = pairwise_bayes_factors(results)

    assert len(bf_table) == 3  # C(3,2) = 3 pairs
    assert "mean_log_bf" in bf_table.columns
    assert "log10_bf" in bf_table.columns
    assert bf_table["mean_log_bf"].notna().all()


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

    assert "log_evidence_summary" in report
    assert "pairwise_bayes_factors" in report
    assert "random_effects_bms" in report
    assert len(report["log_evidence_summary"]) == 2  # 2 conditions
    assert len(report["pairwise_bayes_factors"]) == 1  # 1 pair
