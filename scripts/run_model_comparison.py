"""CLI entry point for predictive log-score comparison analysis."""

from __future__ import annotations

import argparse
import json
import sys
from numbers import Integral, Real
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.model_comparison import (
    log_score_summary,
    model_comparison_report,
    pairwise_predictive_log_scores,
)
from cli.common import filter_primary_runs, load_results_table


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Predictive log-score comparison for affect_aif.")
    parser.add_argument("--results", required=True, help="Path to results CSV or parquet.")
    parser.add_argument("--output-dir", required=True, help="Directory for comparison outputs.")
    return parser


def _condition_label(value) -> str:
    if isinstance(value, Integral):
        return f"C{int(value)}"
    if isinstance(value, Real) and float(value).is_integer():
        return f"C{int(float(value))}"
    return str(value)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = filter_primary_runs(load_results_table(args.results))

    if "cumulative_log_evidence" not in results.columns:
        print("ERROR: Results do not contain predictive log-score data.")
        print("Re-run experiments with the updated agent code.")
        return 1

    # Predictive log-score summary
    le_summary = log_score_summary(results)
    le_summary.to_csv(output_dir / "log_evidence_summary.csv", index=False)
    print("Predictive log-score summary per condition:")
    print(le_summary.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    # Pairwise predictive log-score differences
    bf_table = pairwise_predictive_log_scores(results)
    bf_table.to_csv(output_dir / "pairwise_bayes_factors.csv", index=False)
    print("\nPairwise predictive log-score differences (log10 scale):")
    cols = ["condition_a", "condition_b", "log10_predictive_log_score_difference", "prop_a_preferred", "p_value"]
    print(bf_table[cols].to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # Heuristic interpretation of score differences
    print("\nInterpretation of predictive log-score differences:")
    for _, row in bf_table.iterrows():
        abs_score_diff = abs(row["log10_predictive_log_score_difference"])
        if abs_score_diff < 0.5:
            strength = "small"
        elif abs_score_diff < 1:
            strength = "moderate"
        elif abs_score_diff < 2:
            strength = "large"
        else:
            strength = "very large"
        favored = row["condition_a"] if row["log10_predictive_log_score_difference"] > 0 else row["condition_b"]
        print(
            f"  {_condition_label(row['condition_a'])} vs {_condition_label(row['condition_b'])}: "
            f"|log10 score diff| = {abs_score_diff:.2f} ({strength}), favors C{favored}"
        )

    # Full report with RFX-BMS
    report = model_comparison_report(results)
    (output_dir / "model_comparison_report.json").write_text(json.dumps(report, indent=2))

    bms = report["random_effects_bms"]
    if "error" not in bms:
        print(f"\nRandom-effects BMS over predictive log scores ({bms['n_valid_seeds']} seeds):")
        print(f"  Conditions: {bms['conditions']}")
        print(f"  Expected frequencies: {[f'{f:.3f}' for f in bms['expected_frequency']]}")
        print(f"  Protected exceedance: {[f'{p:.3f}' for p in bms['protected_exceedance_probability']]}")
        print(f"  Bayesian omnibus risk: {bms['bayesian_omnibus_risk']:.4f}")
    else:
        print(f"\nRFX-BMS on predictive log scores: {bms['error']}")

    print(f"\nSaved predictive model comparison outputs to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
