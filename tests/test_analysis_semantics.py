"""Tests for analysis-layer interpretation semantics."""

from __future__ import annotations

from affect_aif.analysis.hypotheses import run_all_hypothesis_tests
from affect_aif.analysis.model_comparison import model_comparison_report
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner
from scripts.run_analysis import _hypothesis_summary_frame
from scripts.run_model_comparison import main as run_model_comparison_main


def test_h1_exports_canonical_label_and_summary_frame_uses_it(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2]})
    results = ExperimentRunner(cfg).run_all()

    hypotheses = run_all_hypothesis_tests(results)
    assert hypotheses["tests"]["h1"]["label"] == "orthogonal_augmentation"

    summary = _hypothesis_summary_frame(hypotheses)
    h1_row = summary.loc[summary["hypothesis"] == "H1"].iloc[0]
    assert h1_row["label"] == "orthogonal_augmentation"


def test_model_comparison_report_uses_predictive_log_score_language(tiny_config):
    cfg = ExperimentConfig(
        **{**tiny_config.__dict__, "conditions": [1, 2], "num_replications": 3, "num_rounds": 10}
    )
    results = ExperimentRunner(cfg).run_all()

    report = model_comparison_report(results)

    assert "predictive_log_score_summary" in report
    assert "pairwise_predictive_log_scores" in report
    assert "log_evidence_summary" in report
    assert "pairwise_bayes_factors" in report
    assert report["predictive_log_score_summary"][0]["mean_predictive_log_score"] == report[
        "log_evidence_summary"
    ][0]["mean_log_evidence"]


def test_run_model_comparison_cli_uses_predictive_language(tmp_path, capsys, tiny_config):
    cfg = ExperimentConfig(
        **{**tiny_config.__dict__, "conditions": [1, 2], "num_replications": 3, "num_rounds": 10}
    )
    results = ExperimentRunner(cfg).run_all()
    results_path = tmp_path / "results.csv"
    output_dir = tmp_path / "model"
    results.to_csv(results_path, index=False)

    exit_code = run_model_comparison_main(["--results", str(results_path), "--output-dir", str(output_dir)])
    captured = capsys.readouterr().out.lower()

    assert exit_code == 0
    assert "predictive log-score" in captured
    assert "predictive model comparison" in captured
