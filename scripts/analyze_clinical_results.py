"""Analyze Phase 5 clinical sensitivity results post-hoc.

Run this after experiments complete to get full analysis including
window-based betrayal dynamics and Bayes factors.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_clinical_sensitivity import (
    analyze_betrayal_windows,
    analyze_results,
    compute_beta_dynamics,
    compute_clinical_bayes_factors,
)


def main():
    results_dirs = [
        Path("results/clinical_sensitivity_betrayal"),
        Path("results/clinical_sensitivity_default"),
    ]

    for results_dir in results_dirs:
        csv_path = results_dir / "all_clinical.csv"
        if not csv_path.exists():
            print(f"Skipping {results_dir} — no all_clinical.csv")
            continue

        print(f"\n{'='*70}")
        print(f"Analyzing: {results_dir}")
        print(f"{'='*70}")

        combined = pd.read_csv(csv_path)
        print(f"Loaded {len(combined)} rows")

        analyze_results(combined, results_dir)
        compute_clinical_bayes_factors(combined, results_dir)
        analyze_betrayal_windows(combined, results_dir)
        compute_beta_dynamics(combined, results_dir)


if __name__ == "__main__":
    main()
