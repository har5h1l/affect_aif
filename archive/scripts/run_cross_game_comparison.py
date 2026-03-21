"""Cross-game comparison analysis for Phase 7.

Compares model performance across different game types (PD, Stag Hunt, Chicken)
to test whether the orthogonal augmentation result generalizes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.analysis.metrics import final_round_summary
from affect_aif.analysis.model_comparison import log_evidence_summary, pairwise_bayes_factors


def load_results(path: str) -> pd.DataFrame:
    source = Path(path)
    if source.suffix == ".parquet":
        return pd.read_parquet(source)
    return pd.read_csv(source)


def filter_primary(results: pd.DataFrame) -> pd.DataFrame:
    if "run_mode" not in results.columns:
        return results
    primary = results[results["run_mode"] == "primary"].copy()
    return primary if not primary.empty else results


def analyze_game(name: str, results: pd.DataFrame) -> dict:
    """Analyze a single game's results."""
    summary = final_round_summary(results)
    cond_stats = summary.groupby(["condition", "condition_name"]).agg(
        mean_payoff=("total_payoff", "mean"),
        std_payoff=("total_payoff", "std"),
        n=("total_payoff", "count"),
    ).reset_index()

    # H1: C2 vs C1 (affect augmentation)
    c1 = summary[summary["condition"] == 1]["total_payoff"].to_numpy()
    c2 = summary[summary["condition"] == 2]["total_payoff"].to_numpy()
    if len(c1) >= 2 and len(c2) >= 2:
        t, p = stats.ttest_ind(c2, c1, equal_var=False)
        d_h1 = float((c2.mean() - c1.mean()) / np.sqrt((c1.var(ddof=1) + c2.var(ddof=1)) / 2))
    else:
        t, p, d_h1 = float("nan"), float("nan"), float("nan")

    # C3 = C4 check
    c3 = summary[summary["condition"] == 3]["total_payoff"].to_numpy()
    c4 = summary[summary["condition"] == 4]["total_payoff"].to_numpy()
    if len(c3) >= 2 and len(c4) >= 2:
        _, p_c3c4 = stats.ttest_ind(c3, c4, equal_var=False)
    else:
        p_c3c4 = float("nan")

    # C2 vs C5
    c5 = summary[summary["condition"] == 5]["total_payoff"].to_numpy()
    if len(c2) >= 2 and len(c5) >= 2:
        _, p_c2c5 = stats.ttest_ind(c2, c5, equal_var=False)
        d_c2c5 = float((c2.mean() - c5.mean()) / np.sqrt((c2.var(ddof=1) + c5.var(ddof=1)) / 2))
    else:
        p_c2c5, d_c2c5 = float("nan"), float("nan")

    result = {
        "game": name,
        "conditions": cond_stats.to_dict(orient="records"),
        "h1_affect_augmentation": {
            "c2_mean": float(c2.mean()) if len(c2) > 0 else float("nan"),
            "c1_mean": float(c1.mean()) if len(c1) > 0 else float("nan"),
            "cohen_d": d_h1,
            "p_value": float(p),
        },
        "c3_equals_c4": {"p_value": float(p_c3c4)},
        "c2_vs_c5": {"cohen_d": d_c2c5, "p_value": float(p_c2c5)},
    }

    # Model comparison if available
    if "cumulative_log_evidence" in results.columns:
        le_sum = log_evidence_summary(results)
        bf_table = pairwise_bayes_factors(results)
        result["log_evidence"] = le_sum.to_dict(orient="records")
        result["bayes_factors"] = bf_table.to_dict(orient="records")

    return result


def main():
    parser = argparse.ArgumentParser(description="Cross-game comparison for Phase 7.")
    parser.add_argument("--results", nargs="+", required=True,
                        help="Paths to results CSV files (one per game).")
    parser.add_argument("--names", nargs="+", required=True,
                        help="Game names (same order as --results).")
    parser.add_argument("--output-dir", required=True, help="Output directory.")
    args = parser.parse_args()

    if len(args.results) != len(args.names):
        print("ERROR: --results and --names must have the same number of entries.")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    analyses = []
    for name, path in zip(args.names, args.results):
        results = filter_primary(load_results(path))
        analysis = analyze_game(name, results)
        analyses.append(analysis)

    # Summary table
    rows = []
    for a in analyses:
        h1 = a["h1_affect_augmentation"]
        c2c5 = a["c2_vs_c5"]
        rows.append({
            "game": a["game"],
            "C1_mean": h1["c1_mean"],
            "C2_mean": h1["c2_mean"],
            "H1_d": h1["cohen_d"],
            "H1_p": h1["p_value"],
            "C2vsC5_d": c2c5["cohen_d"],
            "C2vsC5_p": c2c5["p_value"],
            "C3=C4_p": a["c3_equals_c4"]["p_value"],
        })

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(output_dir / "cross_game_summary.csv", index=False)

    print("Cross-game comparison summary:")
    print(summary_df.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # Bayes factor summary across games
    if all("log_evidence" in a for a in analyses):
        print("\nLog-evidence comparison across games:")
        for a in analyses:
            print(f"\n  {a['game']}:")
            for le in a["log_evidence"]:
                print(f"    C{le['condition']} ({le['condition_name']}): "
                      f"mean={le['mean_log_evidence']:.2f} ± {le['se_log_evidence']:.2f}")

    # Save full report
    (output_dir / "cross_game_report.json").write_text(
        json.dumps(analyses, indent=2, default=str)
    )
    print(f"\nSaved cross-game comparison to {output_dir}")


if __name__ == "__main__":
    main()
