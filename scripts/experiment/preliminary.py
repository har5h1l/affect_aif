"""Run a small preliminary experiment and print directional hypothesis checks."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.trust.runner import ExperimentRunner
from experiments.trust.spec import ExperimentSpec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a small preliminary affect_aif experiment.")
    parser.add_argument(
        "--config",
        default="configs/trust/smoke/smoke.toml",
        help="Path to a TOML experiment spec.",
    )
    parser.add_argument("--replications", type=int, default=5, help="Number of replications per variant.")
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

    spec = ExperimentSpec.from_toml(args.config).with_overrides(
        rounds=int(args.rounds),
        replications=int(args.replications),
    )
    runner = ExperimentRunner.from_spec(spec)
    results = runner.run_all()
    runner.save_results(results, args.output)

    print(f"Saved {len(results)} rows to {Path(args.output)}")
    if {"variant_id", "payoff"}.issubset(results.columns):
        summary = results.groupby("variant_id", as_index=False).agg(total_payoff=("payoff", "sum"))
        print("\nPer-variant payoff")
        print(summary.to_string(index=False, float_format=lambda value: f"{value:0.4f}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
