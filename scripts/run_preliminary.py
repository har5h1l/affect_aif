"""Run a small preliminary experiment and print directional hypothesis checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.analysis.hypotheses import run_all_hypothesis_tests
from affect_aif.analysis.metrics import final_round_summary
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner


def _condition_summary_table(results: pd.DataFrame) -> pd.DataFrame:
    summary = final_round_summary(results)
    return (
        summary.groupby(["condition", "condition_name"], as_index=False)
        .agg(
            mean_payoff=("total_payoff", "mean"),
            std_payoff=("total_payoff", "std"),
            mean_accuracy=("mean_accuracy", "mean"),
            mean_planning_cost_ratio=("planning_cost_ratio", "mean"),
        )
        .sort_values("condition")
    )


def _directional_checks(hypotheses: dict) -> pd.DataFrame:
    tests = hypotheses["tests"]
    h1 = tests["h1"]
    h2 = tests["h2"]
    h3 = tests["h3"]
    h4 = tests["h4"]
    h5 = tests["h5"]

    rows = [
        {
            "hypothesis": "H1",
            "status": "PASS" if h1["payoff_ratio_c2_over_c1"] >= 0.90 else "FAIL",
            "criterion": "C2/C1 payoff ratio >= 0.90",
            "value": h1["payoff_ratio_c2_over_c1"],
        },
        {
            "hypothesis": "H2",
            "status": "PASS" if h2["accuracy_within_margin"] and h2["payoff_lower_than_c2"] else "FAIL",
            "criterion": "|C3-C1| accuracy <= 0.05 and C3 payoff < C2",
            "value": h2["payoff_difference_c3_minus_c2"],
        },
        {
            "hypothesis": "H3",
            "status": "PASS"
            if h3["payoff_difference_c2_minus_c5"] > 0.0 and h3["exploiter_payoff_difference_c2_minus_c5"] > 0.0
            else "FAIL",
            "criterion": "C2 payoff > C5 overall and against exploiters",
            "value": h3["payoff_difference_c2_minus_c5"],
        },
        {
            "hypothesis": "H4",
            "status": "N/A"
            if not h4.get("available", False)
            else ("PASS" if h4["payoff_difference_c2_minus_c4"] > 0.0 and h4["payoff_difference_c2_minus_c1"] >= -0.25 else "FAIL"),
            "criterion": "C2 post-switch payoff > C4 and not much worse than C1",
            "value": h4.get("payoff_difference_c2_minus_c4"),
        },
        {
            "hypothesis": "H5",
            "status": "N/A"
            if not h5.get("available", False)
            else ("PASS" if h5["mean_beta_selection_correlation"] > 0.0 and h5["positive_seed_fraction"] >= 0.60 else "FAIL"),
            "criterion": "Positive beta-selection correlation in an agent-choice run",
            "value": h5.get("mean_beta_selection_correlation"),
        },
    ]
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Run a small preliminary affect_aif experiment.")
    parser.add_argument(
        "--config",
        default="affect_aif/configs/betrayal_stress.json",
        help="Path to a JSON config file. Agent-choice configs such as betrayal_stress.json or variant_b.json enable H5.",
    )
    parser.add_argument("--replications", type=int, default=5, help="Number of replications per condition.")
    parser.add_argument("--rounds", type=int, default=200, help="Rounds per replication.")
    parser.add_argument(
        "--output",
        default="results/preliminary.csv",
        help="Where to write the preliminary results table.",
    )
    args = parser.parse_args()

    config = ExperimentConfig.from_json(args.config)
    config.num_replications = int(args.replications)
    config.num_rounds = int(args.rounds)
    config.conditions = [1, 2, 3, 4, 5]
    config.run_sensitivity = False

    runner = ExperimentRunner(config)
    results = runner.run_all()
    runner.save_results(results, args.output)

    summary_table = _condition_summary_table(results)
    hypotheses = run_all_hypothesis_tests(results)
    directional = _directional_checks(hypotheses)

    print(f"Saved {len(results)} rows to {Path(args.output)}")
    if runner.calibration_summary is not None:
        print(f"Derived mu: {runner.calibration_summary['derived_mu']:.6f}")
        print(f"Mean |EFE| per step: {runner.calibration_summary['mean_abs_efe_per_step']:.6f}")

    print("\nPer-condition summary")
    print(summary_table.to_string(index=False, float_format=lambda value: f"{value:0.4f}"))

    print("\nDirectional hypothesis checks")
    print(directional.to_string(index=False, float_format=lambda value: f"{value:0.4f}"))


if __name__ == "__main__":
    main()
