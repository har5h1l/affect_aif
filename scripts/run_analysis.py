"""CLI entry point for post-hoc analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from affect_aif.analysis.plots import save_all_figures
from affect_aif.analysis.statistics import cumulative_payoff_anova, pairwise_payoff_tests


def load_results(path: str) -> pd.DataFrame:
    source = Path(path)
    if source.suffix == ".parquet":
        return pd.read_parquet(source)
    return pd.read_csv(source)


def main():
    parser = argparse.ArgumentParser(description="Analyze affect_aif results.")
    parser.add_argument("--results", required=True, help="Path to the results CSV or parquet.")
    parser.add_argument("--output-dir", required=True, help="Directory for figures and summary tables.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = load_results(args.results)

    save_all_figures(results, str(output_dir))
    anova = cumulative_payoff_anova(results)
    pairwise = pairwise_payoff_tests(results)
    pairwise.to_csv(output_dir / "pairwise_payoff_tests.csv", index=False)

    summary_path = output_dir / "statistics_summary.txt"
    summary_path.write_text(
        "Cumulative payoff ANOVA\n"
        f"F = {anova['f_stat']:.6f}\n"
        f"p = {anova['p_value']:.6g}\n"
    )
    print(f"Saved figures and statistics to {output_dir}")


if __name__ == "__main__":
    main()
