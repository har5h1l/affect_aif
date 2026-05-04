#!/usr/bin/env python3
"""Analyze standardized benchmark results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmarks.core.comparison import (
    compute_cvc_summary,
    compute_shared_summary,
    compute_trust_summary,
    format_comparison_report,
)


def main():
    parser = argparse.ArgumentParser(description="Analyze backend-aware benchmark result CSVs.")
    parser.add_argument("--results", required=True, help="Path to benchmark_results.csv")
    parser.add_argument("--output-dir", required=False, help="Directory for derived tables and report")
    args = parser.parse_args()

    results = pd.read_csv(args.results)
    output_dir = Path(args.output_dir) if args.output_dir else Path(args.results).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    shared = compute_shared_summary(results)
    trust = compute_trust_summary(results)
    cvc = compute_cvc_summary(results)
    report = format_comparison_report(results)

    shared.to_csv(output_dir / "benchmark_shared_summary.csv", index=False)
    if not trust.empty:
        trust.to_csv(output_dir / "benchmark_trust_summary.csv", index=False)
    if not cvc.empty:
        cvc.to_csv(output_dir / "benchmark_cvc_summary.csv", index=False)
    (output_dir / "benchmark_report.txt").write_text(report)

    print(report)


if __name__ == "__main__":
    main()
