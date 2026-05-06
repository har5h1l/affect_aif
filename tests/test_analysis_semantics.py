"""Tests for analysis-layer interpretation semantics."""

from __future__ import annotations

import pandas as pd

from analysis.hypotheses import run_all_hypothesis_tests
from analysis.metrics import final_round_summary
from analysis.model_comparison import model_comparison_report
from cli.common import load_results_table
from experiments.trust.config import ExperimentConfig
from experiments.trust.runner import ExperimentRunner
from scripts.analysis.analyze import _hypothesis_summary_frame
from scripts.analysis.model_comparison import main as run_model_comparison_main


def test_behavior_cards_export_current_labels_and_summary_frame_uses_them(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2]})
    results = ExperimentRunner(cfg).run_all()

    hypotheses = run_all_hypothesis_tests(results)
    assert hypotheses["h0"]["label"] == "openness_gate"
    assert hypotheses["h1"]["label"] == "model_fitness"

    summary = _hypothesis_summary_frame(hypotheses)
    h0_row = summary.loc[summary["hypothesis"] == "H0"].iloc[0]
    assert h0_row["label"] == "openness_gate"
    h1_row = summary.loc[summary["hypothesis"] == "H1"].iloc[0]
    assert h1_row["label"] == "model_fitness"


def test_model_comparison_report_uses_predictive_log_score_language(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2], "num_replications": 3, "num_rounds": 10})
    results = ExperimentRunner(cfg).run_all()

    report = model_comparison_report(results)

    assert "predictive_log_score_summary" in report
    assert "pairwise_predictive_log_scores" in report
    assert set(report) == {"predictive_log_score_summary", "pairwise_predictive_log_scores", "random_effects_bms"}


def test_run_model_comparison_cli_uses_predictive_language(tmp_path, capsys, tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2], "num_replications": 3, "num_rounds": 10})
    results = ExperimentRunner(cfg).run_all()
    results_path = tmp_path / "results.csv"
    output_dir = tmp_path / "model"
    results.to_csv(results_path, index=False)

    exit_code = run_model_comparison_main(["--results", str(results_path), "--output-dir", str(output_dir)])
    captured = capsys.readouterr().out.lower()

    assert exit_code == 0
    assert "predictive log-score" in captured
    assert "predictive model comparison" in captured


def test_load_results_table_normalizes_mixed_condition_identifiers(tmp_path):
    def row(condition, condition_name, round_idx, payoff):
        return {
            "condition": condition,
            "condition_name": condition_name,
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
        row(1, "tau1_no_affect", 0, 10),
        row("1", "tau1_no_affect", 1, 12),
        row("lesioned", "lesioned", 0, 8),
        row("lesioned", "lesioned", 1, 9),
    ]
    path = tmp_path / "mixed_conditions.csv"
    pd.DataFrame(rows).to_csv(path, index=False)

    loaded = load_results_table(path)
    summary = final_round_summary(loaded)

    assert sorted(loaded["condition"].drop_duplicates(), key=str) == [1, "lesioned"]
    assert len(summary) == 2
    tau1 = summary.loc[summary["condition_name"] == "tau1_no_affect"].iloc[0]
    lesion = summary.loc[summary["condition_name"] == "lesioned"].iloc[0]
    assert tau1["condition"] == 1
    assert tau1["total_payoff"] == 22
    assert lesion["condition"] == "lesioned"
    assert lesion["total_payoff"] == 17
