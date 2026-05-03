"""Write a compact final-round summary for an existing results table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.metrics import final_round_summary
from cli.common import filter_primary_runs, load_results_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize affect_aif results.")
    parser.add_argument("--results", required=True, help="Path to the results CSV or parquet.")
    parser.add_argument("--output", required=True, help="Path for the summary CSV.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = final_round_summary(filter_primary_runs(load_results_table(args.results)))
    summary.to_csv(output, index=False)
    print(f"Saved {len(summary)} rows to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
