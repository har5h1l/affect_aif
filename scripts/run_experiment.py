"""CLI entry point for running the experiment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.analysis.visualization import build_run_gifs
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(description="Run the affect_aif experiment.")
    parser.add_argument("--config", required=True, help="Path to a JSON config file.")
    parser.add_argument("--output", required=True, help="Where to write the results table.")
    parser.add_argument("--verbose", action="store_true", help="Print live stage-by-stage experiment progress.")
    parser.add_argument(
        "--verbosity-mode",
        default="stage_stream",
        choices=["stage_stream"],
        help="Structured progress output mode.",
    )
    parser.add_argument(
        "--no-verbose-calibration",
        action="store_true",
        help="Suppress calibration-stage messages when verbose output is enabled.",
    )
    parser.add_argument("--make-gifs", action="store_true", help="Generate one GIF per primary condition-run after saving results.")
    parser.add_argument("--gif-output-dir", help="Directory for generated experiment GIFs.")
    args = parser.parse_args()

    config = ExperimentConfig.from_json(args.config)
    config.verbose = bool(args.verbose)
    config.verbosity_mode = str(args.verbosity_mode)
    config.verbosity_include_calibration = not bool(args.no_verbose_calibration)
    config.gif_after_run = bool(args.make_gifs)
    config.gif_output_dir = args.gif_output_dir
    runner = ExperimentRunner(config)
    results = runner.run_all()
    runner.save_results(results, args.output)

    print(f"Saved {len(results)} rows to {Path(args.output)}")
    if runner.calibration_summary is not None:
        print(f"Derived mu: {runner.calibration_summary['derived_mu']:.6f}")
        print(f"Mean |EFE| per step: {runner.calibration_summary['mean_abs_efe_per_step']:.6f}")
    if config.gif_after_run:
        gif_output_dir = config.gif_output_dir or str(Path(args.output).with_suffix("")) + "_gifs"
        written = build_run_gifs(results, gif_output_dir, reporter=runner.progress)
        print(f"Saved {len(written)} GIFs to {Path(gif_output_dir)}")


if __name__ == "__main__":
    main()
