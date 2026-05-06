"""Tests for analysis-layer interpretation semantics."""

from __future__ import annotations

import pandas as pd

from analysis.hypotheses import run_all_hypothesis_tests
from analysis.metrics import final_round_summary
from analysis.model_comparison import model_comparison_report
from cli.common import load_results_table
from experiments.trust.runner import ExperimentRunner
from scripts.analysis.analyze import _hypothesis_summary_frame
from scripts.analysis.model_comparison import main as run_model_comparison_main


def test_behavior_cards_export_current_labels_and_summary_frame_uses_them(tiny_spec):
    results = ExperimentRunner.from_spec(tiny_spec).run_all()

    hypotheses = run_all_hypothesis_tests(results)
    assert hypotheses["h0"]["label"] == "openness_gate"
    assert hypotheses["h1"]["label"] == "model_fitness"

    summary = _hypothesis_summary_frame(hypotheses)
    h0_row = summary.loc[summary["hypothesis"] == "H0"].iloc[0]
    assert h0_row["label"] == "openness_gate"
    h1_row = summary.loc[summary["hypothesis"] == "H1"].iloc[0]
    assert h1_row["label"] == "model_fitness"


def test_model_comparison_report_uses_predictive_log_score_language(tiny_spec):
    results = ExperimentRunner.from_spec(tiny_spec.with_overrides(rounds=10, replications=3)).run_all()

    report = model_comparison_report(results)

    assert "predictive_log_score_summary" in report
    assert "pairwise_predictive_log_scores" in report
    assert set(report) == {"predictive_log_score_summary", "pairwise_predictive_log_scores", "random_effects_bms"}


def test_run_model_comparison_cli_uses_predictive_language(tmp_path, capsys, tiny_spec):
    results = ExperimentRunner.from_spec(tiny_spec.with_overrides(rounds=10, replications=3)).run_all()
    results_path = tmp_path / "results.csv"
    output_dir = tmp_path / "model"
    results.to_csv(results_path, index=False)

    exit_code = run_model_comparison_main(["--results", str(results_path), "--output-dir", str(output_dir)])
    captured = capsys.readouterr().out.lower()

    assert exit_code == 0
    assert "predictive log-score" in captured
    assert "predictive model comparison" in captured


def test_load_results_table_preserves_variant_identity(tmp_path):
    def row(variant_id, round_idx, payoff):
        return {
            "variant_id": variant_id,
            "seed": 0,
            "round": round_idx,
            "payoff": payoff,
            "inferred_type_correct": 1.0,
            "inferred_stance_correct": 1.0,
            "inferred_joint_correct": 1.0,
            "q_pi_entropy": 0.5,
            "mean_abs_step_efe": 1.0,
            "planning_cost": 1.0,
            "planning_cost_ratio": 1.0,
        }

    rows = [
        row("no_affect__planning_horizon_1", 0, 10),
        row("no_affect__planning_horizon_1", 1, 12),
        row("lesioned", 0, 8),
        row("lesioned", 1, 9),
    ]
    path = tmp_path / "mixed_variants.csv"
    pd.DataFrame(rows).to_csv(path, index=False)

    loaded = load_results_table(path)
    summary = final_round_summary(loaded)

    assert sorted(loaded["variant_id"].drop_duplicates(), key=str) == ["lesioned", "no_affect__planning_horizon_1"]
    assert len(summary) == 2
    horizon_1 = summary.loc[summary["variant_id"] == "no_affect__planning_horizon_1"].iloc[0]
    lesion = summary.loc[summary["variant_id"] == "lesioned"].iloc[0]
    assert horizon_1["total_payoff"] == 22
    assert lesion["total_payoff"] == 17
