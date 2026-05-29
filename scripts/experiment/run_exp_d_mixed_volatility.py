"""Run Experiment D: mixed stationary and volatile partner environment."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.experiment.followup_phenotypes import (
    affect_variant,
    common_group_metrics,
    make_parser,
    make_spec,
    mixed_volatility_scenario,
    no_affect_variant,
    run_suite_main,
    save_figure,
    summarize_for_plot,
    variant_label,
    vector_value,
)


def build_specs(*, rounds: int, seeds: int, seed: int):
    variants = (
        affect_variant("default_reference", alpha=3.0),
        affect_variant("low_alpha", alpha=0.1),
        affect_variant("high_alpha", alpha=3.0),
        no_affect_variant(),
    )
    return (
        make_spec(
            hypothesis_id="exp_d",
            hypothesis_name="mixed_volatility",
            experiment_id="mixed_volatility",
            scenario=mixed_volatility_scenario(),
            variants=variants,
            rounds=rounds,
            replications=seeds,
            seed=seed,
        ),
    )


def _partner_beta_mean(group: pd.DataFrame, partner: int) -> float:
    values = [vector_value(value, partner) for value in group["local_betas"]]
    return float(pd.Series(values).mean()) if values else float("nan")


def _partner_beta_range(group: pd.DataFrame, partner: int) -> float:
    values = pd.Series([vector_value(value, partner) for value in group["local_betas"]], dtype=float).dropna()
    if values.empty:
        return float("nan")
    return float(values.max() - values.min())


def metrics(results: pd.DataFrame) -> pd.DataFrame:
    data = pd.DataFrame(common_group_metrics(results))
    rows = []
    stability = np.asarray([1.0, 0.8, 0.35, 0.15], dtype=float)
    for keys, group in results.groupby(["experiment_id", "variant_id", "seed"], dropna=False):
        experiment_id, variant_id, seed = keys
        partner = pd.to_numeric(group["partner_idx"], errors="coerce")
        counts = np.asarray([(partner == idx).mean() for idx in range(4)], dtype=float)
        beta_means = np.asarray([_partner_beta_mean(group, idx) for idx in range(4)], dtype=float)
        if np.all(np.isfinite(beta_means)) and float(np.std(beta_means)) > 0.0:
            discrimination = float(np.corrcoef(stability, -beta_means)[0, 1])
        else:
            discrimination = float("nan")
        rows.append(
            {
                "experiment_id": experiment_id,
                "variant_id": variant_id,
                "seed": int(seed),
                "discrimination_index": discrimination,
                "concentration_toward_p0": float(counts[0]),
                "false_positive_rate": float(counts[1:].sum()),
                "p0_beta_range": _partner_beta_range(group, 0),
                "p1_beta_range": _partner_beta_range(group, 1),
                "p2_beta_range": _partner_beta_range(group, 2),
                "p3_beta_range": _partner_beta_range(group, 3),
            }
        )
    return data.merge(pd.DataFrame(rows), on=["experiment_id", "variant_id", "seed"], how="left")


def figure(metrics_df: pd.DataFrame, figure_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    panels = [
        ("discrimination_index", "Discrimination index"),
        ("concentration_toward_p0", "Concentration toward P0"),
        ("false_positive_rate", "False-positive allocation"),
        ("beta_range", "Mean beta range"),
    ]
    for ax, (metric, title) in zip(axes.reshape(-1), panels, strict=True):
        summary = summarize_for_plot(metrics_df, ["variant_id"], metric)
        ax.bar([variant_label(item) for item in summary["variant_id"]], summary[metric])
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=30)
    save_figure(fig, figure_dir / "fig_mixed_volatility.pdf")


def main() -> int:
    parser = make_parser("Run mixed-volatility follow-up.", "results/exp_d")
    args = parser.parse_args()
    run_suite_main(
        args,
        specs=build_specs(rounds=args.rounds, seeds=args.seeds, seed=args.seed),
        metric_builder=metrics,
        figure_builder=figure,
        table_folder="exp_d_mixed_volatility",
        readme=(
            "Experiment D mixes stationary cooperative, stationary exploitative, abrupt-switch, "
            "and gradual-proxy partners in a partner-choice graded trust environment."
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
