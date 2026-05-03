"""CLI entry point for post-hoc analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.hypotheses import run_all_hypothesis_tests
from analysis.metrics import (
    affective_movement_summary,
    betrayal_latency_summary,
    betrayal_trajectory,
    final_round_summary,
    has_switch_events,
    post_switch_condition_comparison,
    post_switch_window_summary,
)
from analysis.plots import save_all_figures
from analysis.statistics import cumulative_payoff_anova, pairwise_payoff_tests
from cli.common import filter_primary_runs, load_results_table


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
        if hypothesis_id == "h1":
            row["primary_metric"] = len(evidence.get("beta_signal_columns", []))
            row["secondary_metric"] = len(evidence.get("reward_control_conditions", []))
        elif hypothesis_id == "h2":
            row["primary_metric"] = evidence.get("num_partners_observed")
            row["secondary_metric"] = len(evidence.get("factorized_columns", []))
        elif hypothesis_id == "h3":
            row["primary_metric"] = evidence.get("payoff_difference_lesioned_minus_tau4_affect")
            row["secondary_metric"] = evidence.get("accuracy_difference_lesioned_minus_tau4_affect")
        elif hypothesis_id == "h4":
            row["primary_metric"] = evidence.get("payoff_difference_tau4_affect_minus_tau4_no_affect")
            row["secondary_metric"] = evidence.get("detection_latency_difference_tau4_no_affect_minus_tau4_affect")
        elif hypothesis_id == "h5":
            row["primary_metric"] = len(evidence.get("partner_selection_counts", {}))
            row["secondary_metric"] = evidence.get("partner_column")
        elif hypothesis_id == "h6":
            row["primary_metric"] = evidence.get("mean_affect_payoff_gain")
            row["secondary_metric"] = len(evidence.get("mean_q_pi_entropy_by_condition", {}))
        elif hypothesis_id == "h7":
            row["primary_metric"] = len(evidence.get("clinical_conditions", []))
            row["secondary_metric"] = None
        rows.append(row)
    return pd.DataFrame(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze affect_aif results.")
    parser.add_argument("--results", required=True, help="Path to the results CSV or parquet.")
    parser.add_argument("--output-dir", required=True, help="Directory for figures and summary tables.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = filter_primary_runs(load_results_table(args.results))
    switch_events_present = has_switch_events(results)

    save_all_figures(results, str(output_dir))
    summary = final_round_summary(results)
    anova = cumulative_payoff_anova(results)
    pairwise = pairwise_payoff_tests(results)
    hypotheses = run_all_hypothesis_tests(results)
    movement = affective_movement_summary(results)

    summary.to_csv(output_dir / "final_round_summary.csv", index=False)
    pairwise.to_csv(output_dir / "pairwise_payoff_tests.csv", index=False)
    (output_dir / "hypothesis_tests.json").write_text(json.dumps(hypotheses, indent=2))
    hypothesis_summary = _hypothesis_summary_frame(hypotheses)
    hypothesis_summary.to_csv(output_dir / "hypothesis_summary.csv", index=False)
    movement.to_csv(output_dir / "affective_movement_summary.csv", index=False)

    if switch_events_present:
        post_switch_5 = post_switch_window_summary(results, window=5)
        post_switch_10 = post_switch_window_summary(results, window=10)
        betrayal_comp = post_switch_condition_comparison(results, windows=(5, 10))
        betrayal_latencies = betrayal_latency_summary(results, max_encounters=10)
        betrayal_traj = betrayal_trajectory(results, max_encounters=10)

        post_switch_5.to_csv(output_dir / "betrayal_post_switch_window_1_5.csv", index=False)
        post_switch_10.to_csv(output_dir / "betrayal_post_switch_window_1_10.csv", index=False)
        betrayal_comp.to_csv(output_dir / "betrayal_condition_comparison.csv", index=False)
        betrayal_latencies.to_csv(output_dir / "betrayal_detection_latency.csv", index=False)
        betrayal_traj.to_csv(output_dir / "betrayal_trajectories.csv", index=False)

    summary_path = output_dir / "statistics_summary.txt"
    movement_lines = []
    if not movement.empty:
        grouped = (
            movement.groupby(["condition", "condition_name"], as_index=False)
            .agg(
                mean_beta_range=("beta_range", "mean"),
                fraction_beta_moved=("beta_moved_materially", "mean"),
            )
            .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
        )
        movement_lines = ["\nAffective movement (beta) summary\n", grouped, "\n"]
    betrayal_lines = []
    if switch_events_present:
        betrayal_comp = post_switch_condition_comparison(results, windows=(5, 10))
        if not betrayal_comp.empty:
            grouped = (
                betrayal_comp.groupby(["window"], as_index=False)
                .agg(
                    mean_payoff_difference_tau4_affect_minus_tau4_no_affect=(
                        "payoff_difference_tau4_affect_minus_tau4_no_affect",
                        "mean",
                    ),
                    mean_stance_accuracy_difference_tau4_affect_minus_tau4_no_affect=(
                        "stance_accuracy_difference_tau4_affect_minus_tau4_no_affect",
                        "mean",
                    ),
                )
                .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
            )
            betrayal_lines = ["\nBetrayal post-switch comparison\n", grouped, "\n"]
    summary_path.write_text(
        "Cumulative payoff ANOVA\n"
        f"F = {anova['f_stat']:.6f}\n"
        f"p = {anova['p_value']:.6g}\n" + "".join(movement_lines) + "".join(betrayal_lines)
    )
    print("Per-condition final summary")
    print(
        summary.groupby(["condition", "condition_name"], as_index=False)
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
            movement.groupby(["condition", "condition_name"], as_index=False)
            .agg(
                mean_beta_range=("beta_range", "mean"),
                fraction_beta_moved=("beta_moved_materially", "mean"),
            )
            .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
        )
    if switch_events_present:
        betrayal_comp = post_switch_condition_comparison(results, windows=(5, 10))
        if not betrayal_comp.empty:
            print("\nBetrayal post-switch comparison")
            print(
                betrayal_comp.groupby(["window"], as_index=False)
                .agg(
                    mean_payoff_difference_tau4_affect_minus_tau4_no_affect=(
                        "payoff_difference_tau4_affect_minus_tau4_no_affect",
                        "mean",
                    ),
                    mean_stance_accuracy_difference_tau4_affect_minus_tau4_no_affect=(
                        "stance_accuracy_difference_tau4_affect_minus_tau4_no_affect",
                        "mean",
                    ),
                )
                .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
            )
    print(f"\nSaved figures and statistics to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
