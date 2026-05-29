"""Run Experiment A: fine-grained alpha sweep."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import pandas as pd

from scripts.experiment.followup_phenotypes import (
    betrayal_scenario,
    build_alpha_variants,
    common_group_metrics,
    make_parser,
    make_spec,
    open_graded_scenario,
    run_suite_main,
    save_figure,
    summarize_for_plot,
)

ALPHAS = (0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 4.0, 8.0)


def build_specs(*, rounds: int, seeds: int, seed: int):
    variants = build_alpha_variants(ALPHAS)
    return (
        make_spec(
            hypothesis_id="exp_a",
            hypothesis_name="alpha_sweep",
            experiment_id="open_graded",
            scenario=open_graded_scenario(),
            variants=variants,
            rounds=rounds,
            replications=seeds,
            seed=seed,
        ),
        make_spec(
            hypothesis_id="exp_a",
            hypothesis_name="alpha_sweep",
            experiment_id="betrayal",
            scenario=betrayal_scenario(),
            variants=variants,
            rounds=rounds,
            replications=seeds,
            seed=seed + 10_000,
        ),
    )


def metrics(results: pd.DataFrame) -> pd.DataFrame:
    data = pd.DataFrame(common_group_metrics(results))
    data["alpha"] = (
        data["variant_id"].str.replace("alpha_", "", regex=False).str.replace("p", ".", regex=False).astype(float)
    )
    return data


def figure(metrics_df: pd.DataFrame, figure_dir: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    axes = axes.reshape(-1)
    panels = [
        ("early_exploitation_rate", "Early exploiter investment"),
        ("betrayal_recovery_time", "Betrayal recovery rounds"),
        ("selection_gini", "Selection Gini"),
        ("entropy_late", "Late policy entropy"),
        ("beta_range", "Mean beta range"),
    ]
    for ax, (metric, title) in zip(axes, panels, strict=False):
        summary = summarize_for_plot(metrics_df, ["experiment_id", "alpha"], metric)
        for experiment_id, group in summary.groupby("experiment_id"):
            ax.plot(group["alpha"], group[metric], marker="o", label=str(experiment_id))
        ax.set_xscale("log")
        ax.set_xlabel("alpha")
        ax.set_title(title)
    axes[-1].axis("off")
    axes[0].legend(frameon=False)
    save_figure(fig, figure_dir / "fig_alpha_sweep.pdf")


def main() -> int:
    parser = make_parser("Run fine-grained alpha sweep follow-up.", "results/exp_a")
    args = parser.parse_args()
    run_suite_main(
        args,
        specs=build_specs(rounds=args.rounds, seeds=args.seeds, seed=args.seed),
        metric_builder=metrics,
        figure_builder=figure,
        table_folder="exp_a_alpha_sweep",
        readme=(
            "Experiment A sweeps alpha across open graded and betrayal regimes. "
            "Full per-round outputs live in results/exp_a; compact metrics are mirrored to manuscript source tables."
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
