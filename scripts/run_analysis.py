"""CLI entry point for post-hoc analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.analysis.hypotheses import run_all_hypothesis_tests
from affect_aif.analysis.metrics import (
    affective_movement_summary,
    betrayal_latency_summary,
    betrayal_trajectory,
    final_round_summary,
    has_switch_events,
    post_switch_condition_comparison,
    post_switch_window_summary,
)
from affect_aif.analysis.plots import save_all_figures
from affect_aif.analysis.statistics import cumulative_payoff_anova, pairwise_payoff_tests
from affect_aif.cli.common import filter_primary_runs, load_results_table


def _hypothesis_summary_frame(results: dict) -> pd.DataFrame:
    rows = []
    for hypothesis_id, payload in results["tests"].items():
        row = {
            "hypothesis": hypothesis_id.upper(),
            "label": payload.get("label", ""),
            "available": bool(payload.get("available", False)),
        }
        if hypothesis_id == "h1":
            row["primary_metric"] = payload.get("payoff_ratio_c2_over_c1")
            row["secondary_metric"] = payload.get("welch_p_value")
        elif hypothesis_id == "h2":
            row["primary_metric"] = payload.get("accuracy_difference_c3_minus_c1")
            row["secondary_metric"] = payload.get("payoff_difference_c3_minus_c2")
        elif hypothesis_id == "h3":
            row["primary_metric"] = payload.get("payoff_difference_c2_minus_c5")
            row["secondary_metric"] = payload.get("exploiter_payoff_difference_c2_minus_c5")
        elif hypothesis_id == "h4":
            row["primary_metric"] = payload.get("payoff_difference_c2_minus_c4")
            row["secondary_metric"] = payload.get("payoff_difference_c2_minus_c1")
        elif hypothesis_id == "h5":
            row["primary_metric"] = payload.get("mean_beta_selection_correlation")
            row["secondary_metric"] = payload.get("p_value_vs_zero")
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

    if has_switch_events(results):
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
                mean_terminal_signal_range=("terminal_signal_range", "mean"),
                fraction_beta_moved=("beta_moved_materially", "mean"),
                fraction_terminal_signal_moved=("terminal_signal_moved_materially", "mean"),
            )
            .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
        )
        movement_lines = ["\nAffective movement summary\n", grouped, "\n"]
    betrayal_lines = []
    if has_switch_events(results):
        betrayal_comp = post_switch_condition_comparison(results, windows=(5, 10))
        if not betrayal_comp.empty:
            grouped = (
                betrayal_comp.groupby(["window"], as_index=False)
                .agg(
                    mean_payoff_difference_c2_minus_c5=("payoff_difference_c2_minus_c5", "mean"),
                    mean_accuracy_difference_c2_minus_c5=("accuracy_difference_c2_minus_c5", "mean"),
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
                mean_terminal_signal_range=("terminal_signal_range", "mean"),
                fraction_beta_moved=("beta_moved_materially", "mean"),
                fraction_terminal_signal_moved=("terminal_signal_moved_materially", "mean"),
            )
            .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
        )
    if has_switch_events(results):
        betrayal_comp = post_switch_condition_comparison(results, windows=(5, 10))
        if not betrayal_comp.empty:
            print("\nBetrayal post-switch comparison")
            print(
                betrayal_comp.groupby(["window"], as_index=False)
                .agg(
                    mean_payoff_difference_c2_minus_c5=("payoff_difference_c2_minus_c5", "mean"),
                    mean_accuracy_difference_c2_minus_c5=("accuracy_difference_c2_minus_c5", "mean"),
                )
                .to_string(index=False, float_format=lambda value: f"{value:0.4f}")
            )
    print(f"\nSaved figures and statistics to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
