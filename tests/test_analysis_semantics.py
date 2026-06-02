"""Tests for analysis-layer interpretation semantics."""

from __future__ import annotations

import pandas as pd

from analysis.hypotheses import run_all_hypothesis_tests
from analysis.metrics import (
    betrayal_misdeployment_summary,
    betrayal_phase_summary,
    betrayal_reallocation_summary,
    deployment_dissociation_summary,
    evidence_effect_summary,
    final_round_summary,
    model_fitness_correlation_summary,
    partner_choice_summary,
    partner_model_fitness_summary,
    phenotype_validation_summary,
)
from analysis.model_comparison import model_comparison_report
from cli.common import load_results_table
from experiments.trust.runner import ExperimentRunner
from scripts.analysis.analyze import _hypothesis_summary_frame
from scripts.analysis.analyze import main as run_analysis_main
from scripts.analysis.model_comparison import main as run_model_comparison_main


def test_behavior_cards_export_current_labels_and_summary_frame_uses_them(tiny_spec):
    results = ExperimentRunner.from_spec(tiny_spec).run_all()

    hypotheses = run_all_hypothesis_tests(results)
    assert hypotheses["h0"]["label"] == "policy_openness"
    assert hypotheses["h1"]["label"] == "model_fitness"

    summary = _hypothesis_summary_frame(hypotheses)
    h0_row = summary.loc[summary["hypothesis"] == "H0"].iloc[0]
    assert h0_row["label"] == "policy_openness"
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


def test_betrayal_phase_summary_splits_pre_acute_and_tail_windows():
    rows = []
    for variant_id in ["no_affect", "affect"]:
        for round_idx in range(1, 8):
            rows.append(
                {
                    "variant_id": variant_id,
                    "seed": 0,
                    "round": round_idx,
                    "partner_idx": 0,
                    "payoff": 10 + round_idx if variant_id == "affect" else round_idx,
                    "q_pi_entropy": 0.1 * round_idx,
                    "selected_partner": 0,
                    "selected_action": round_idx % 2,
                    "scheduled_stance_switch_partner_ids": [0] if round_idx == 4 else [],
                    "scheduled_switch_partner_ids": [],
                    "type_switched": False,
                    "stance_switched": False,
                    "switch_kind": "scheduled_stance" if round_idx == 4 else "",
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 1.0,
                    "inferred_joint_correct": 1.0,
                }
            )
    summary = betrayal_phase_summary(pd.DataFrame(rows), pre_window=2, acute_window=2)

    phases = set(summary["phase"])
    assert phases == {"pre_switch", "acute_post_switch", "post_acute_tail"}
    affect_pre = summary[(summary["variant_id"] == "affect") & (summary["phase"] == "pre_switch")].iloc[0]
    affect_acute = summary[(summary["variant_id"] == "affect") & (summary["phase"] == "acute_post_switch")].iloc[0]
    affect_tail = summary[(summary["variant_id"] == "affect") & (summary["phase"] == "post_acute_tail")].iloc[0]
    assert affect_pre["encounters"] == 2
    assert affect_pre["mean_payoff"] == 12.5
    assert affect_acute["mean_payoff"] == 14.5
    assert affect_tail["mean_payoff"] == 16.5


def test_betrayal_phase_summary_treats_nan_switch_cells_as_empty():
    rows = []
    for round_idx in range(1, 4):
        rows.append(
            {
                "variant_id": "affect",
                "seed": 0,
                "round": round_idx,
                "partner_idx": 0,
                "payoff": 1.0,
                "q_pi_entropy": 0.5,
                "selected_partner": 0,
                "scheduled_stance_switch_partner_ids": float("nan"),
                "scheduled_switch_partner_ids": float("nan"),
                "type_switched": False,
                "stance_switched": False,
                "switch_kind": "",
            }
        )

    summary = betrayal_phase_summary(pd.DataFrame(rows))

    assert summary.empty


def test_deployment_dissociation_summary_pairs_affect_and_lesion():
    rows = []
    for variant_id, payoff, accuracy, entropy in [
        ("affect", 10.0, 0.8, 0.2),
        ("tracked_only", 7.0, 0.75, 0.5),
    ]:
        for round_idx in [1, 2]:
            rows.append(
                {
                    "variant_id": variant_id,
                    "seed": 0,
                    "round": round_idx,
                    "payoff": payoff,
                    "inferred_type_correct": accuracy,
                    "inferred_stance_correct": accuracy,
                    "inferred_joint_correct": accuracy,
                    "q_pi_entropy": entropy,
                    "mean_abs_step_efe": 1.0,
                    "planning_cost": 1.0,
                    "planning_cost_ratio": 1.0,
                    "round_log_evidence": -0.2 if variant_id == "affect" else -0.22,
                }
            )

    summary = deployment_dissociation_summary(pd.DataFrame(rows), reference_variant="affect")
    lesion = summary.loc[summary["variant_id"] == "tracked_only"].iloc[0]
    assert lesion["delta_total_payoff_vs_affect"] == -6.0
    assert abs(lesion["delta_mean_accuracy_vs_affect"]) < 0.1
    assert lesion["delta_mean_q_pi_entropy_vs_affect"] > 0


def test_partner_choice_summary_reports_selection_rates_and_beta():
    rows = [
        {
            "variant_id": "affect",
            "seed": 0,
            "round": 1,
            "selected_partner": 0,
            "partner_idx": 0,
            "payoff": 3.0,
            "q_pi_entropy": 0.4,
            "betas": [0.5, 2.0],
        },
        {
            "variant_id": "affect",
            "seed": 0,
            "round": 2,
            "selected_partner": 1,
            "partner_idx": 1,
            "payoff": 1.0,
            "q_pi_entropy": 0.6,
            "betas": [0.5, 2.0],
        },
        {
            "variant_id": "affect",
            "seed": 0,
            "round": 3,
            "selected_partner": 0,
            "partner_idx": 0,
            "payoff": 5.0,
            "q_pi_entropy": 0.2,
            "betas": [0.5, 2.0],
        },
    ]

    summary = partner_choice_summary(pd.DataFrame(rows))
    partner_0 = summary.loc[summary["selected_partner"] == 0].iloc[0]
    assert partner_0["selection_count"] == 2
    assert partner_0["selection_rate"] == 2 / 3
    assert partner_0["mean_selected_partner_beta"] == 0.5


def test_partner_model_fitness_summary_separates_surprise_from_reward():
    rows = []
    for round_idx in [1, 2, 3]:
        for partner_idx, payoff, correct in [(0, 1.0, 1.0), (1, 5.0, 0.0), (2, 5.0, 1.0)]:
            rows.append(
                {
                    "variant_id": "affect",
                    "seed": 0,
                    "round": round_idx,
                    "partner_idx": partner_idx,
                    "payoff": payoff,
                    "betas": [0.5, 2.0, 0.67],
                    "prediction_errors": [0.1, 0.8, 0.2],
                    "reward_avgs": [1.0, 5.0, 5.0],
                    "inferred_type_correct": correct,
                }
            )

    partner_summary = partner_model_fitness_summary(pd.DataFrame(rows))
    reliable_low_reward = partner_summary.loc[partner_summary["partner_idx"] == 0].iloc[0]
    volatile_high_reward = partner_summary.loc[partner_summary["partner_idx"] == 1].iloc[0]
    assert reliable_low_reward["precision_mean"] > volatile_high_reward["precision_mean"]
    assert reliable_low_reward["reward_signal_mean"] < volatile_high_reward["reward_signal_mean"]

    corr = model_fitness_correlation_summary(pd.DataFrame(rows)).iloc[0]
    assert corr["corr_precision_surprise"] < 0
    assert corr["abs_corr_precision_surprise"] > corr["abs_corr_precision_reward"]


def test_model_fitness_correlation_uses_active_encounter_alignment():
    rows = [
        {
            "variant_id": "affect",
            "seed": 0,
            "round": 1,
            "partner_idx": 0,
            "payoff": 3.0,
            "betas": [0.5, 2.0, 1.0],
            "prediction_errors": [0.1, 0.1, 0.5],
            "reward_avgs": [float("nan"), float("nan"), float("nan")],
            "inferred_type_correct": 1.0,
        },
        {
            "variant_id": "affect",
            "seed": 0,
            "round": 2,
            "partner_idx": 1,
            "payoff": 3.0,
            "betas": [0.5, 2.0, 1.0],
            "prediction_errors": [0.9, 0.9, 0.5],
            "reward_avgs": [float("nan"), float("nan"), float("nan")],
            "inferred_type_correct": 0.0,
        },
        {
            "variant_id": "affect",
            "seed": 0,
            "round": 3,
            "partner_idx": 2,
            "payoff": 3.0,
            "betas": [0.5, 2.0, 1.0],
            "prediction_errors": [0.9, 0.1, 0.5],
            "reward_avgs": [float("nan"), float("nan"), float("nan")],
            "inferred_type_correct": 1.0,
        },
    ]

    corr = model_fitness_correlation_summary(pd.DataFrame(rows)).iloc[0]

    assert corr["corr_precision_surprise"] < 0


def test_model_fitness_correlation_reports_partial_signal_dominance():
    rows = []
    for seed, surprise, payoff, precision in [
        (0, 0.10, 4.9, 2.00),
        (1, 0.20, 4.7, 1.80),
        (2, 0.35, 4.4, 1.55),
        (3, 0.55, 4.2, 1.15),
        (4, 0.70, 4.1, 0.85),
        (5, 0.90, 3.8, 0.55),
    ]:
        rows.append(
            {
                "variant_id": "affect",
                "seed": seed,
                "round": 1,
                "partner_idx": 0,
                "payoff": payoff,
                "betas": [1.0 / precision],
                "prediction_errors": [surprise],
                "reward_avgs": [float("nan")],
                "inferred_type_correct": 1.0,
            }
        )

    corr = model_fitness_correlation_summary(pd.DataFrame(rows)).iloc[0]

    assert corr["abs_partial_corr_precision_surprise"] > corr["abs_partial_corr_precision_reward"]
    assert corr["partial_surprise_dominates_reward"]


def test_betrayal_misdeployment_summary_flags_low_entropy_bad_payoff_after_switch():
    rows = []
    for round_idx in range(1, 7):
        rows.append(
            {
                "variant_id": "affect",
                "seed": 0,
                "round": round_idx,
                "partner_idx": 0,
                "payoff": -1.0 if round_idx in {4, 5} else 3.0,
                "q_pi_entropy": 0.05 if round_idx in {4, 5} else 1.0,
                "selected_partner": 0 if round_idx != 6 else 1,
                "selected_action": 1,
                "scheduled_stance_switch_partner_ids": [0] if round_idx == 4 else [],
                "scheduled_switch_partner_ids": [],
                "type_switched": False,
                "stance_switched": False,
                "switch_kind": "scheduled_stance" if round_idx == 4 else "",
                "inferred_type_correct": 0.0 if round_idx in {4, 5} else 1.0,
                "inferred_stance_correct": 1.0,
                "inferred_joint_correct": 0.0 if round_idx in {4, 5} else 1.0,
            }
        )

    summary = betrayal_misdeployment_summary(pd.DataFrame(rows), window=3, entropy_quantile=0.5)
    row = summary.iloc[0]
    assert row["encounters"] == 3
    assert row["bad_payoff_rate"] == 2 / 3
    assert row["wrong_type_rate"] == 2 / 3
    assert row["overconfident_wrong_type_rate"] == 2 / 3
    assert row["overconfident_bad_payoff_rate"] == 2 / 3
    assert row["selected_partner_rate"] == 2 / 3


def test_betrayal_reallocation_summary_reports_return_and_no_return_events():
    rows = []
    for variant_id, selected_partners in [
        ("affect", [0, 1, 1, 1, 0, 2]),
        ("no_affect", [0, 1, 1, 2, 2, 2]),
    ]:
        for round_idx, selected_partner in enumerate(selected_partners, start=1):
            rows.append(
                {
                    "variant_id": variant_id,
                    "seed": 0,
                    "round": round_idx,
                    "partner_idx": selected_partner,
                    "payoff": 10.0 + round_idx if selected_partner == 0 else 1.0,
                    "q_pi_entropy": 0.5 * round_idx,
                    "selected_partner": selected_partner,
                    "selected_action": 1,
                    "scheduled_stance_switch_partner_ids": [0] if round_idx == 3 else [],
                    "scheduled_switch_partner_ids": [],
                    "type_switched": False,
                    "stance_switched": False,
                    "switch_kind": "scheduled_stance" if round_idx == 3 else "",
                    "inferred_type_correct": 1.0,
                    "inferred_stance_correct": 1.0,
                    "inferred_joint_correct": 1.0,
                }
            )

    summary = betrayal_reallocation_summary(pd.DataFrame(rows))

    affect = summary.loc[summary["variant_id"] == "affect"].iloc[0]
    assert bool(affect["returned_to_partner"]) is True
    assert affect["post_switch_decisions"] == 4
    assert affect["reencounters"] == 1
    assert affect["decisions_to_first_reencounter"] == 2
    assert affect["rounds_to_first_reencounter"] == 2
    assert affect["mean_payoff_on_reencounter"] == 15.0
    assert affect["reencounter_selection_rate"] == 0.25

    no_affect = summary.loc[summary["variant_id"] == "no_affect"].iloc[0]
    assert bool(no_affect["returned_to_partner"]) is False
    assert no_affect["post_switch_decisions"] == 4
    assert no_affect["reencounters"] == 0
    assert pd.isna(no_affect["decisions_to_first_reencounter"])
    assert no_affect["reencounter_selection_rate"] == 0.0


def test_evidence_effect_summary_reports_h1_and_h3_split_readouts():
    rows = []
    for seed in [0, 1, 2]:
        for variant_id, beta_values, selected_after, payoff_after in [
            ("affect", [0.5, 2.0, 0.67], [1, 1, 0], [1.0, 1.0, 10.0]),
            ("no_affect", [float("nan"), float("nan"), float("nan")], [0, 0, 1], [7.0, 7.0, 1.0]),
        ]:
            for round_idx in range(1, 7):
                after_switch_idx = max(round_idx - 4, 0)
                selected_partner = selected_after[after_switch_idx] if round_idx >= 4 else 0
                payoff = payoff_after[after_switch_idx] if round_idx >= 4 else 3.0
                rows.append(
                    {
                        "variant_id": variant_id,
                        "seed": seed,
                        "round": round_idx,
                        "partner_idx": selected_partner,
                        "true_partner_type": "cooperator",
                        "payoff": payoff,
                        "q_pi_entropy": (0.2 if variant_id == "affect" else 0.8) + 0.01 * seed,
                        "mean_abs_step_efe": 1.0,
                        "planning_cost": 1.0,
                        "planning_cost_ratio": 1.0,
                        "selected_partner": selected_partner,
                        "selected_action": 1,
                        "betas": beta_values,
                        "prediction_errors": [0.1, 0.8, 0.2],
                        "reward_avgs": [1.0, 5.0, 5.0],
                        "scheduled_stance_switch_partner_ids": [0] if round_idx == 4 else [],
                        "scheduled_switch_partner_ids": [],
                        "type_switched": False,
                        "stance_switched": False,
                        "switch_kind": "scheduled_stance" if round_idx == 4 else "",
                        "inferred_type_correct": 1.0,
                        "inferred_stance_correct": 1.0,
                        "inferred_joint_correct": 1.0,
                    }
                )

    summary = evidence_effect_summary(pd.DataFrame(rows), bootstrap_iterations=50, random_seed=0)

    final_entropy = summary.loc[
        (summary["readout"] == "final") & (summary["metric"] == "mean_q_pi_entropy")
    ].iloc[0]
    assert final_entropy["treatment_variant"] == "affect"
    assert final_entropy["reference_variant"] == "no_affect"
    assert final_entropy["difference"] < 0
    assert pd.notna(final_entropy["bootstrap_ci_low"])
    assert pd.notna(final_entropy["cohen_d"])

    h1 = summary.loc[summary["readout"] == "model_fitness"].iloc[0]
    assert h1["metric"] == "abs_corr_precision_surprise_minus_reward"
    assert h1["treatment_mean"] > 0

    reallocation = summary.loc[
        (summary["readout"] == "betrayal_reallocation")
        & (summary["metric"] == "mean_payoff_on_reencounter")
    ].iloc[0]
    assert reallocation["difference"] > 0


def test_analysis_cli_writes_model_fitness_and_misdeployment_reports(tmp_path):
    rows = []
    for round_idx in range(1, 7):
        rows.append(
            {
                "variant_id": "affect",
                "seed": 0,
                "round": round_idx,
                "partner_idx": 0,
                "true_partner_type": "cooperator",
                "payoff": -1.0 if round_idx in {4, 5} else 3.0,
                "partner_payoff": 1.0,
                "q_pi_entropy": 0.05 if round_idx in {4, 5} else 1.0,
                "mean_abs_step_efe": 1.0,
                "planning_cost": 1.0,
                "planning_cost_ratio": 1.0,
                "selected_partner": 0,
                "selected_action": 1,
                "betas": [0.5, 2.0, 0.67],
                "prediction_errors": [0.1, 0.8, 0.2],
                "reward_avgs": [1.0, 5.0, 5.0],
                "scheduled_stance_switch_partner_ids": [0] if round_idx == 4 else [],
                "scheduled_switch_partner_ids": [],
                "type_switched": False,
                "stance_switched": False,
                "switch_kind": "scheduled_stance" if round_idx == 4 else "",
                "inferred_type_correct": 0.0 if round_idx in {4, 5} else 1.0,
                "inferred_stance_correct": 1.0,
                "inferred_joint_correct": 0.0 if round_idx in {4, 5} else 1.0,
            }
        )
    results_path = tmp_path / "results.csv"
    output_dir = tmp_path / "analysis"
    pd.DataFrame(rows).to_csv(results_path, index=False)

    exit_code = run_analysis_main(["--results", str(results_path), "--output-dir", str(output_dir)])

    assert exit_code == 0
    assert (output_dir / "partner_model_fitness_summary.csv").exists()
    assert (output_dir / "model_fitness_correlation_summary.csv").exists()
    assert (output_dir / "betrayal_misdeployment_summary.csv").exists()
    assert (output_dir / "betrayal_reallocation_summary.csv").exists()
    assert (output_dir / "evidence_effect_summary.csv").exists()


def test_phenotype_validation_summary_includes_dynamics_and_behavior():
    rows = []
    for round_idx, beta in enumerate([1.0, 0.5, 1.5, 0.5], start=1):
        rows.append(
            {
                "variant_id": "borderline",
                "seed": 0,
                "round": round_idx,
                "payoff": 1.0,
                "q_pi_entropy": 0.3,
                "selected_partner": round_idx % 2,
                "selected_action": round_idx % 2,
                "betas": [beta, 1.0],
            }
        )

    summary = phenotype_validation_summary(pd.DataFrame(rows))
    row = summary.iloc[0]
    assert row["variant_id"] == "borderline"
    assert row["beta_range"] == 1.0
    assert row["action_flip_rate"] == 1.0
    assert row["partner_selection_entropy"] > 0
