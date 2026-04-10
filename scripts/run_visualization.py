"""CLI entry point for experiment GIF generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.visualization import build_run_gifs, load_results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate experiment GIFs from saved results.")
    parser.add_argument("--results", required=True, help="Path to the results CSV or parquet.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated GIFs.")
    return parser


def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    results = load_results(args.results)
    written = build_run_gifs(results, args.output_dir)
    print(f"Saved {len(written)} GIFs to {Path(args.output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
