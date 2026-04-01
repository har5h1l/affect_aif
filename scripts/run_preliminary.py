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


def _condition_sort_key(value) -> tuple[int, str]:
    if isinstance(value, int):
        return (0, f"{value:04d}")
    return (1, str(value))


def _condition_summary_table(results: pd.DataFrame) -> pd.DataFrame:
    summary = final_round_summary(results)
    grouped = summary.groupby(["condition", "condition_name"], as_index=False).agg(
        mean_payoff=("total_payoff", "mean"),
        std_payoff=("total_payoff", "std"),
        mean_accuracy=("mean_accuracy", "mean"),
        mean_planning_cost_ratio=("planning_cost_ratio", "mean"),
    )
    grouped["_condition_sort"] = grouped["condition"].apply(_condition_sort_key)
    return grouped.sort_values("_condition_sort").drop(columns="_condition_sort")


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
            "status": "PASS" if h1.get("mean_affect_payoff_gain", float("nan")) >= 0.0 else "FAIL",
            "criterion": "Affect adds non-negative payoff over matched no-affect depths",
            "value": h1.get("mean_affect_payoff_gain"),
        },
        {
            "hypothesis": "H2",
            "status": "PASS" if h2.get("payoff_difference_tau8_minus_tau1", float("nan")) > 0.0 else "FAIL",
            "criterion": "Tau-8 no-affect payoff > tau-1 no-affect payoff",
            "value": h2.get("payoff_difference_tau8_minus_tau1"),
        },
        {
            "hypothesis": "H3",
            "status": "PASS"
            if h3.get("type_accuracy_preserved", False)
            and h3.get("stance_recovery_worse_than_intact", False)
            and h3.get("payoff_lower_than_intact", False)
            else "FAIL",
            "criterion": "Lesion preserves type accuracy but harms stance recovery and payoff",
            "value": h3.get("payoff_difference_lesioned_minus_tau4_affect"),
        },
        {
            "hypothesis": "H4",
            "status": "N/A"
            if not h4.get("available", False)
            else (
                "PASS"
                if h4.get("payoff_difference_tau4_affect_minus_tau4_no_affect", float("nan")) > 0.0
                and h4.get("detection_latency_difference_tau4_no_affect_minus_tau4_affect", float("nan")) >= 0.0
                else "FAIL"
            ),
            "criterion": "Tau-4 affect beats tau-4 no-affect after betrayal",
            "value": h4.get("payoff_difference_tau4_affect_minus_tau4_no_affect"),
        },
        {
            "hypothesis": "H5",
            "status": "N/A"
            if not h5.get("available", False)
            else (
                "PASS"
                if h5.get("payoff_difference_tau4_affect_minus_reward_average", float("nan")) > 0.0
                and h5.get("detection_latency_difference_reward_average_minus_tau4_affect", float("nan")) >= 0.0
                else "FAIL"
            ),
            "criterion": "Precision tracking beats reward averaging after stance shifts",
            "value": h5.get("payoff_difference_tau4_affect_minus_reward_average"),
        },
    ]
    return pd.DataFrame(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a small preliminary affect_aif experiment.")
    parser.add_argument(
        "--config",
        default="affect_aif/configs/betrayal_stress.json",
        help=(
            "Path to a JSON config file. Agent-choice configs such as betrayal_stress.json or variant_b.json enable H5."
        ),
    )
    parser.add_argument("--replications", type=int, default=5, help="Number of replications per condition.")
    parser.add_argument("--rounds", type=int, default=200, help="Rounds per replication.")
    parser.add_argument(
        "--output",
        default="results/preliminary.csv",
        help="Where to write the preliminary results table.",
    )
    return parser


def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    config = ExperimentConfig.from_json(args.config)
    config.num_replications = int(args.replications)
    config.num_rounds = int(args.rounds)
    config.conditions = [1, 2, 3, 4, 5, 6, 7, 8]
    config.presets = ["lesioned", "reward_average"]
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
