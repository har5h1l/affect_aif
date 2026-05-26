"""CLI entry point for post-hoc analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.configured import run_configured_analysis
from analysis.hypotheses import run_all_hypothesis_tests
from analysis.interference import cross_partner_interference_summary, global_vs_local_beta_summary
from analysis.metrics import (
    affective_movement_summary,
    betrayal_latency_summary,
    betrayal_misdeployment_summary,
    betrayal_phase_summary,
    betrayal_reallocation_summary,
    betrayal_trajectory,
    deployment_dissociation_summary,
    evidence_effect_summary,
    final_round_summary,
    has_switch_events,
    model_fitness_correlation_summary,
    partner_choice_summary,
    partner_model_fitness_summary,
    phenotype_validation_summary,
    post_switch_variant_comparison,
    post_switch_window_summary,
)
from analysis.plots import save_all_figures
from analysis.statistics import cumulative_payoff_anova, pairwise_payoff_tests
from cli.common import filter_primary_runs, load_results_table
from experiments.trust.spec import ExperimentSpec


def _hypothesis_summary_frame(results: dict) -> pd.DataFrame:
    rows = []
    hypothesis_items = results.get("tests", results)
    for hypothesis_id, payload in hypothesis_items.items():
        evidence = payload.get("evidence", {})
        row = {
            "hypothesis": hypothesis_id.upper(),
            "label": payload.get("label", ""),
            "available": bool(payload.get("available", False)),
            "summary": payload.get("summary", {}).get("claim", ""),
        }
        if hypothesis_id == "h0":
            row["primary_metric"] = evidence.get("mean_affect_payoff_gain")
            row["secondary_metric"] = len(evidence.get("mean_q_pi_entropy_by_variant", {}))
        elif hypothesis_id == "h1":
            row["primary_metric"] = len(evidence.get("beta_signal_columns", []))
            row["secondary_metric"] = len(evidence.get("reward_control_variants", []))
        elif hypothesis_id == "h2":
            row["primary_metric"] = evidence.get("payoff_difference_lesioned_minus_affect")
            row["secondary_metric"] = evidence.get("accuracy_difference_lesioned_minus_affect")
        elif hypothesis_id == "h3":
            row["primary_metric"] = evidence.get("payoff_difference_affect_minus_no_affect")
            row["secondary_metric"] = evidence.get("detection_latency_difference_no_affect_minus_affect")
        elif hypothesis_id == "h4":
            row["primary_metric"] = len(evidence.get("partner_selection_counts", {}))
            row["secondary_metric"] = evidence.get("partner_column")
        elif hypothesis_id == "h5":
            row["primary_metric"] = len(evidence.get("clinical_variants", []))
            row["secondary_metric"] = None
        rows.append(row)
    return pd.DataFrame(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze affect_aif results.")
    parser.add_argument("--results", required=True, help="Path to the results CSV or parquet.")
    parser.add_argument("--output-dir", required=True, help="Directory for figures and summary tables.")
    parser.add_argument("--config", help="Optional TOML experiment spec for configured analysis dispatch.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.config and str(args.config).endswith(".toml"):
        spec = ExperimentSpec.from_toml(args.config)
        run_configured_analysis(spec, args.results, output_dir)
        return 0
    results = filter_primary_runs(load_results_table(args.results))
    switch_events_present = has_switch_events(results)

    summary = final_round_summary(results)
    anova = cumulative_payoff_anova(results)
    pairwise = pairwise_payoff_tests(results)
    hypotheses = run_all_hypothesis_tests(results)
    movement = affective_movement_summary(results)
    deployment = deployment_dissociation_summary(results)
    partner_model_fitness = partner_model_fitness_summary(results)
    model_fitness_corr = model_fitness_correlation_summary(results)
    partner_choice = partner_choice_summary(results)
    phenotypes = phenotype_validation_summary(results)
    evidence_effects = evidence_effect_summary(results)

    summary.to_csv(output_dir / "final_round_summary.csv", index=False)
    pairwise.to_csv(output_dir / "pairwise_payoff_tests.csv", index=False)
    (output_dir / "hypothesis_tests.json").write_text(json.dumps(hypotheses, indent=2))
    hypothesis_summary = _hypothesis_summary_frame(hypotheses)
    hypothesis_summary.to_csv(output_dir / "hypothesis_summary.csv", index=False)
    movement.to_csv(output_dir / "affective_movement_summary.csv", index=False)
    deployment.to_csv(output_dir / "deployment_dissociation_summary.csv", index=False)
    partner_model_fitness.to_csv(output_dir / "partner_model_fitness_summary.csv", index=False)
    model_fitness_corr.to_csv(output_dir / "model_fitness_correlation_summary.csv", index=False)
    partner_choice.to_csv(output_dir / "partner_choice_summary.csv", index=False)
    phenotypes.to_csv(output_dir / "phenotype_validation_summary.csv", index=False)
    evidence_effects.to_csv(output_dir / "evidence_effect_summary.csv", index=False)

    if switch_events_present:
        post_switch_5 = post_switch_window_summary(results, window=5)
        post_switch_10 = post_switch_window_summary(results, window=10)
        betrayal_phases = betrayal_phase_summary(results, pre_window=20, acute_window=10)
        betrayal_comp = post_switch_variant_comparison(results, windows=(5, 10))
        betrayal_latencies = betrayal_latency_summary(results, max_encounters=10)
        betrayal_traj = betrayal_trajectory(results, max_encounters=10)
        betrayal_misdeployment = betrayal_misdeployment_summary(results, window=10)
        betrayal_reallocation = betrayal_reallocation_summary(results)
        interference = cross_partner_interference_summary(results, post_window=10)
        beta_scope = global_vs_local_beta_summary(results)

        post_switch_5.to_csv(output_dir / "betrayal_post_switch_window_1_5.csv", index=False)
        post_switch_10.to_csv(output_dir / "betrayal_post_switch_window_1_10.csv", index=False)
        betrayal_phases.to_csv(output_dir / "betrayal_phase_summary.csv", index=False)
        betrayal_comp.to_csv(output_dir / "betrayal_variant_comparison.csv", index=False)
        betrayal_latencies.to_csv(output_dir / "betrayal_detection_latency.csv", index=False)
        betrayal_traj.to_csv(output_dir / "betrayal_trajectories.csv", index=False)
        betrayal_misdeployment.to_csv(output_dir / "betrayal_misdeployment_summary.csv", index=False)
        betrayal_reallocation.to_csv(output_dir / "betrayal_reallocation_summary.csv", index=False)
        interference.to_csv(output_dir / "cross_partner_interference_summary.csv", index=False)
        beta_scope.to_csv(output_dir / "global_vs_local_beta_summary.csv", index=False)

    try:
        save_all_figures(results, str(output_dir))
    except (KeyError, ValueError) as exc:
        message = f"Skipped figures: {exc}"
        (output_dir / "skipped_figures.txt").write_text(message + "\n", encoding="utf-8")
        print(message, file=sys.stderr)

    summary_path = output_dir / "statistics_summary.txt"
    movement_lines = []
    if not movement.empty:
        grouped = (
            movement.groupby(["variant_id"], as_index=False)
            .agg(
                mean_beta_range=("beta_range", "mean"),
                fraction_beta_moved=("beta_moved_materially", "mean"),
            )
            .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
        )
        movement_lines = ["\nAffective movement (beta) summary\n", grouped, "\n"]
    betrayal_lines = []
    if switch_events_present:
        betrayal_comp = post_switch_variant_comparison(results, windows=(5, 10))
        if not betrayal_comp.empty:
            grouped = (
                betrayal_comp.groupby(["window"], as_index=False)
                .mean(numeric_only=True)
                .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
            )
            betrayal_lines = ["\nBetrayal post-switch comparison\n", grouped, "\n"]
        betrayal_phases = betrayal_phase_summary(results, pre_window=20, acute_window=10)
        if not betrayal_phases.empty:
            phase_grouped = (
                betrayal_phases.groupby(["phase"], as_index=False)
                .mean(numeric_only=True)
                .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
            )
            betrayal_lines.extend(["\nBetrayal phase summary\n", phase_grouped, "\n"])
    summary_path.write_text(
        "Cumulative payoff ANOVA\n"
        f"F = {anova['f_stat']:.6f}\n"
        f"p = {anova['p_value']:.6g}\n" + "".join(movement_lines) + "".join(betrayal_lines)
    )
    print("Per-variant final summary")
    print(
        summary.groupby(["variant_id"], as_index=False)
        .agg(
            mean_total_payoff=("total_payoff", "mean"),
            std_total_payoff=("total_payoff", "std"),
            mean_accuracy=("mean_accuracy", "mean"),
        )
        .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
    )
    print("\nHypothesis summary")
    print(hypothesis_summary.to_string(index=False, float_format=lambda value: f"{value:0.4f}"))
    if not movement.empty:
        print("\nAffective movement summary")
        print(
            movement.groupby(["variant_id"], as_index=False)
            .agg(
                mean_beta_range=("beta_range", "mean"),
                fraction_beta_moved=("beta_moved_materially", "mean"),
            )
            .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
        )
    if switch_events_present:
        betrayal_comp = post_switch_variant_comparison(results, windows=(5, 10))
        if not betrayal_comp.empty:
            print("\nBetrayal post-switch comparison")
            print(
                betrayal_comp.groupby(["window"], as_index=False)
                .mean(numeric_only=True)
                .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
            )
        betrayal_phases = betrayal_phase_summary(results, pre_window=20, acute_window=10)
        if not betrayal_phases.empty:
            print("\nBetrayal phase summary")
            print(
                betrayal_phases.groupby(["phase"], as_index=False)
                .mean(numeric_only=True)
                .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
            )
    print(f"\nSaved figures and statistics to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
