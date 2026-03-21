"""CLI entry point for Bayesian model comparison analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.analysis.model_comparison import (
    log_evidence_summary,
    model_comparison_report,
    pairwise_bayes_factors,
)
from affect_aif.cli.common import filter_primary_runs, load_results_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bayesian model comparison for affect_aif.")
    parser.add_argument("--results", required=True, help="Path to results CSV or parquet.")
    parser.add_argument("--output-dir", required=True, help="Directory for model comparison outputs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = filter_primary_runs(load_results_table(args.results))

    if "cumulative_log_evidence" not in results.columns:
        print("ERROR: Results do not contain log-evidence data.")
        print("Re-run experiments with the updated agent code.")
        return 1

    # Log-evidence summary
    le_summary = log_evidence_summary(results)
    le_summary.to_csv(output_dir / "log_evidence_summary.csv", index=False)
    print("Log-evidence summary per condition:")
    print(le_summary.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    # Pairwise Bayes factors
    bf_table = pairwise_bayes_factors(results)
    bf_table.to_csv(output_dir / "pairwise_bayes_factors.csv", index=False)
    print("\nPairwise Bayes factors (log10 scale):")
    cols = ["condition_a", "condition_b", "log10_bf", "prop_a_preferred", "p_value"]
    print(bf_table[cols].to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # Interpret Bayes factors
    print("\nInterpretation (Kass & Raftery, 1995):")
    for _, row in bf_table.iterrows():
        abs_bf = abs(row["log10_bf"])
        if abs_bf < 0.5:
            strength = "not worth more than a bare mention"
        elif abs_bf < 1:
            strength = "substantial"
        elif abs_bf < 2:
            strength = "strong"
        else:
            strength = "decisive"
        favored = int(row["condition_a"]) if row["log10_bf"] > 0 else int(row["condition_b"])
        print(
            f"  C{int(row['condition_a'])} vs C{int(row['condition_b'])}: "
            f"|log10 BF| = {abs_bf:.2f} ({strength}), favors C{favored}"
        )

    # Full report with RFX-BMS
    report = model_comparison_report(results)
    (output_dir / "model_comparison_report.json").write_text(json.dumps(report, indent=2))

    bms = report["random_effects_bms"]
    if "error" not in bms:
        print(f"\nRandom-effects BMS ({bms['n_valid_seeds']} seeds):")
        print(f"  Conditions: {bms['conditions']}")
        print(f"  Expected frequencies: {[f'{f:.3f}' for f in bms['expected_frequency']]}")
        print(f"  Protected exceedance: {[f'{p:.3f}' for p in bms['protected_exceedance_probability']]}")
        print(f"  Bayesian omnibus risk: {bms['bayesian_omnibus_risk']:.4f}")
    else:
        print(f"\nRFX-BMS: {bms['error']}")

    print(f"\nSaved model comparison outputs to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
