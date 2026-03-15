"""CLI entry point for running the experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(description="Run the affect_aif experiment.")
    parser.add_argument("--config", required=True, help="Path to a JSON config file.")
    parser.add_argument("--output", required=True, help="Where to write the results table.")
    args = parser.parse_args()

    config = ExperimentConfig.from_json(args.config)
    runner = ExperimentRunner(config)
    results = runner.run_all()
    runner.save_results(results, args.output)

    print(f"Saved {len(results)} rows to {Path(args.output)}")
    if runner.calibration_summary is not None:
        print(f"Derived mu: {runner.calibration_summary['derived_mu']:.6f}")
        print(f"Mean |EFE| per step: {runner.calibration_summary['mean_abs_efe_per_step']:.6f}")


if __name__ == "__main__":
    main()
