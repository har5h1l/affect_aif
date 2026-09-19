"""Alpha-sweep metrics and figure builders."""

# ruff: noqa: E402

from __future__ import annotations

from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from analysis.figure_style import apply_manuscript_figure_style
from analysis.phenotypes.common import (
    betrayal_scenario,
    build_alpha_variants,
    common_group_metrics,
    make_spec,
    open_graded_scenario,
    save_figure,
)

ALPHAS = (0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 4.0, 8.0)
EXP_A_PANELS = (
    "early_exploitation_rate",
    "betrayal_recovery_time",
    "selection_gini",
    "entropy_trajectory",
    "beta_range",
)


def build_specs(*, rounds: int, seeds: int, seed: int):
    variants = build_alpha_variants(ALPHAS)
    return (
        make_spec(
            hypothesis_id="alpha_sweep",
            hypothesis_name="alpha_sweep",
            experiment_id="open_graded",
            scenario=open_graded_scenario(),
            variants=variants,
            rounds=rounds,
            replications=seeds,
            seed=seed,
        ),
        make_spec(
            hypothesis_id="alpha_sweep",
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


def _summary_with_ci(metrics_df: pd.DataFrame, by: list[str], metric: str) -> pd.DataFrame:
    summary = metrics_df.groupby(by, dropna=False)[metric].agg(mean="mean", std="std", count="count").reset_index()
    summary["ci95"] = summary.apply(
        lambda row: 0.0 if row["count"] <= 1 else 1.96 * float(row["std"]) / sqrt(float(row["count"])),
        axis=1,
    ).fillna(0.0)
    return summary


def figure(metrics_df: pd.DataFrame, figure_dir: Path) -> None:
    apply_manuscript_figure_style()
    fig, axes = plt.subplots(3, 2, figsize=(12.2 / 2.54, 3.8), layout="constrained")
    axes = axes.reshape(-1)
    titles = {
        "early_exploitation_rate": "Early exploiter investment",
        "betrayal_recovery_time": "Recovery time (rounds)",
        "selection_gini": "Selection gini",
        "entropy_trajectory": "Policy entropy",
        "beta_range": r"Within-episode $\bar{\beta}_k$ range",
    }
    for ax, metric in zip(axes, EXP_A_PANELS, strict=False):
        if metric == "entropy_trajectory":
            for style_idx, (entropy_metric, label) in enumerate(
                (
                    ("entropy_early", "early"),
                    ("entropy_mid", "mid"),
                    ("entropy_late", "late"),
                )
            ):
                summary = _summary_with_ci(metrics_df, ["alpha"], entropy_metric)
                ax.errorbar(
                    summary["alpha"],
                    summary["mean"],
                    yerr=summary["ci95"],
                    marker=("o", "s", "^")[style_idx],
                    linestyle=("-", "--", ":")[style_idx],
                    markersize=3,
                    capsize=2,
                    label=label,
                )
        else:
            summary = _summary_with_ci(metrics_df, ["experiment_id", "alpha"], metric)
            for style_idx, (experiment_id, group) in enumerate(summary.groupby("experiment_id")):
                ax.errorbar(
                    group["alpha"],
                    group["mean"],
                    yerr=group["ci95"],
                    marker=("o", "s", "^")[style_idx],
                    linestyle=("-", "--", ":")[style_idx],
                    markersize=3,
                    capsize=2,
                    label=str(experiment_id).replace("_", " "),
                )
        ax.set_xscale("log")
        ax.set_xlim(0.04, 10)
        ax.tick_params(axis="x", labelsize=9)
        if ax is axes[4]:
            ax.set_xlabel(r"gain $\alpha$")
        ax.set_title(titles[metric])
    axes[-1].axis("off")
    environment_handles, environment_labels = axes[0].get_legend_handles_labels()
    phase_handles, phase_labels = axes[3].get_legend_handles_labels()
    environment_legend = axes[-1].legend(
        environment_handles,
        environment_labels,
        title="Environment",
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0, 1.05),
        fontsize=8,
        title_fontsize=9,
        handlelength=1.2,
    )
    axes[-1].add_artist(environment_legend)
    axes[-1].legend(
        phase_handles,
        phase_labels,
        title="Episode phase",
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0, 0.32),
        ncol=3,
        fontsize=8,
        title_fontsize=9,
        handlelength=1.0,
        columnspacing=0.7,
    )
    save_figure(fig, figure_dir / "fig_alpha_sweep.pdf", tight_layout=False)
