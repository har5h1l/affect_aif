"""Build phenotype paper artifacts from existing Exp A-D result CSVs."""

# ruff: noqa: E402,I001

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from analysis.phenotypes import alpha_sweep, forgiveness, mixed_volatility, prior_factorial
from analysis.phenotypes.common import write_metrics, write_readme


ARTIFACTS = {
    "alpha_sweep": {
        "metrics": alpha_sweep.metrics,
        "figure": alpha_sweep.figure,
        "table_folder": "exp_a_alpha_sweep",
        "readme": "Experiment A alpha sweep compact metrics and figure artifacts.",
    },
    "prior_factorial": {
        "metrics": prior_factorial.metrics,
        "figure": prior_factorial.figure,
        "table_folder": "exp_b_prior_factorial",
        "readme": "Experiment B prior x alpha factorial compact metrics and figure artifacts.",
    },
    "forgiveness": {
        "metrics": forgiveness.metrics,
        "figure": forgiveness.figure,
        "table_folder": "exp_c_forgiveness",
        "readme": "Experiment C forgiveness/reengagement compact metrics and figure artifacts.",
    },
    "mixed_volatility": {
        "metrics": mixed_volatility.metrics,
        "figure": mixed_volatility.figure,
        "table_folder": "exp_d_mixed_volatility",
        "readme": "Experiment D mixed-volatility compact metrics and figure artifacts.",
    },
}


def _load_results(results_root: Path) -> pd.DataFrame:
    combined = results_root / "results.csv"
    if combined.exists():
        return pd.read_csv(combined, low_memory=False)
    paths = sorted(path for path in results_root.glob("**/results.csv") if path.name == "results.csv")
    if not paths:
        raise FileNotFoundError(f"No results.csv found under {results_root}")
    return pd.concat((pd.read_csv(path, low_memory=False) for path in paths), ignore_index=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build phenotype paper artifacts from existing result CSVs.")
    parser.add_argument("experiment", choices=sorted(ARTIFACTS), help="Phenotype artifact family to build.")
    parser.add_argument(
        "--results-root",
        required=True,
        help="Directory containing combined or nested results.csv files.",
    )
    parser.add_argument("--paper-dir", default="docs/manuscript", help="Manuscript artifact root.")
    parser.add_argument("--no-figures", action="store_true", help="Only write metrics/source tables.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results_root = Path(args.results_root)
    paper_dir = Path(args.paper_dir)
    artifact = ARTIFACTS[args.experiment]
    results = _load_results(results_root)
    metrics = artifact["metrics"](results)
    write_metrics(
        metrics,
        output_dir=results_root,
        paper_dir=paper_dir,
        table_folder=str(artifact["table_folder"]),
    )
    if not args.no_figures:
        artifact["figure"](metrics, paper_dir / "figures")
    write_readme(results_root, str(artifact["readme"]))
    print(f"Wrote phenotype artifacts for {args.experiment} from {results_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
