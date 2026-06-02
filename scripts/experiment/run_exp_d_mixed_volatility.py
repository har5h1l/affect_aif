"""Run Experiment D: mixed stationary and volatile partner environment."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from math import sqrt
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
    variant_label,
    vector_value,
)

EXP_D_PANELS = (
    "default_beta_trajectories",
    "high_alpha_beta_trajectories",
    "discrimination_index",
    "concentration_toward_p0",
)
TRAJECTORY_ROUNDS = (50, 100, 150, 200)


def build_specs(*, rounds: int, seeds: int, seed: int):
    variants = (
        affect_variant("default_reference", alpha=3.0),
        affect_variant("low_alpha", alpha=0.1),
        affect_variant("high_alpha", alpha=8.0),
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


def _partner_beta_at_round(group: pd.DataFrame, partner: int, target_round: int) -> float:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    rows = group[rounds == int(target_round)]
    if rows.empty:
        rows = group[rounds == rounds[rounds <= int(target_round)].max()]
    if rows.empty:
        return float("nan")
    values = [vector_value(value, partner) for value in rows["local_betas"]]
    return float(pd.Series(values).mean()) if values else float("nan")


def _p0_selection_at_round(group: pd.DataFrame, target_round: int, *, window: int = 20) -> float:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    selected = (pd.to_numeric(group["partner_idx"], errors="coerce") == 0).astype(float)
    mask = (rounds <= int(target_round)) & (rounds > int(target_round) - int(window))
    values = selected[mask]
    return float(values.mean()) if len(values) else float("nan")


def _stable_partner_false_positive_rate(
    group: pd.DataFrame,
    *,
    partner: int = 0,
    baseline_end: int = 50,
    evaluation_start: int = 51,
    window: int = 20,
    drop_fraction: float = 0.15,
) -> float:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    selected = (pd.to_numeric(group["partner_idx"], errors="coerce") == int(partner)).astype(float)
    baseline = selected[rounds <= baseline_end]
    evaluation = pd.DataFrame(
        {
            "round": rounds[rounds >= evaluation_start],
            "selected": selected[rounds >= evaluation_start],
        }
    )
    if baseline.empty or evaluation.empty:
        return float("nan")
    baseline_rate = float(baseline.mean())
    if baseline_rate <= 0.0:
        return float("nan")
    threshold = baseline_rate * (1.0 - float(drop_fraction))
    rolling = evaluation["selected"].rolling(window, min_periods=1).mean()
    return float((rolling < threshold).mean())


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
                "false_positive_rate": _stable_partner_false_positive_rate(group),
                "p0_beta_range": _partner_beta_range(group, 0),
                "p1_beta_range": _partner_beta_range(group, 1),
                "p2_beta_range": _partner_beta_range(group, 2),
                "p3_beta_range": _partner_beta_range(group, 3),
                **{
                    f"p{partner_idx}_beta_r{target_round:03d}": _partner_beta_at_round(
                        group,
                        partner_idx,
                        target_round,
                    )
                    for partner_idx in range(4)
                    for target_round in TRAJECTORY_ROUNDS
                },
                **{
                    f"p0_selection_r{target_round:03d}": _p0_selection_at_round(group, target_round)
                    for target_round in TRAJECTORY_ROUNDS
                },
            }
        )
    return data.merge(pd.DataFrame(rows), on=["experiment_id", "variant_id", "seed"], how="left")


def _summary_with_ci(metrics_df: pd.DataFrame, by: list[str], metric: str) -> pd.DataFrame:
    summary = (
        metrics_df.groupby(by, dropna=False)[metric]
        .agg(mean="mean", std="std", count="count")
        .reset_index()
    )
    summary["ci95"] = summary.apply(
        lambda row: 0.0 if row["count"] <= 1 else 1.96 * float(row["std"]) / sqrt(float(row["count"])),
        axis=1,
    ).fillna(0.0)
    return summary


def figure(metrics_df: pd.DataFrame, figure_dir: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, metric in zip(axes.reshape(-1), EXP_D_PANELS, strict=True):
        if metric in {"default_beta_trajectories", "high_alpha_beta_trajectories"}:
            variant_id = "default_reference" if metric == "default_beta_trajectories" else "high_alpha"
            rows = metrics_df[metrics_df["variant_id"].astype(str) == variant_id]
            for partner_idx in range(4):
                cols = [f"p{partner_idx}_beta_r{target_round:03d}" for target_round in TRAJECTORY_ROUNDS]
                means = rows[cols].mean(numeric_only=True)
                ax.plot(TRAJECTORY_ROUNDS, [means[col] for col in cols], marker="o", label=f"P{partner_idx}")
            ax.axvline(100, color="0.4", linestyle="--", linewidth=1)
            ax.axvline(50, color="0.7", linestyle=":", linewidth=1)
            ax.axvline(150, color="0.7", linestyle=":", linewidth=1)
            ax.set_title(variant_label(metric))
            ax.set_xlabel("round")
            ax.legend(frameon=False, fontsize=7)
        elif metric == "discrimination_index":
            summary = _summary_with_ci(metrics_df, ["variant_id"], metric)
            ax.bar([variant_label(item) for item in summary["variant_id"]], summary["mean"], yerr=summary["ci95"])
            ax.set_title("Discrimination index")
            ax.tick_params(axis="x", rotation=30)
        else:
            cols = [f"p0_selection_r{target_round:03d}" for target_round in TRAJECTORY_ROUNDS]
            summary = metrics_df.groupby("variant_id", dropna=False)[cols].mean().reset_index()
            for _, row in summary.iterrows():
                ax.plot(
                    TRAJECTORY_ROUNDS,
                    [row[col] for col in cols],
                    marker="o",
                    label=variant_label(str(row["variant_id"])),
                )
            ax.axvline(100, color="0.4", linestyle="--", linewidth=1)
            ax.axvline(50, color="0.7", linestyle=":", linewidth=1)
            ax.axvline(150, color="0.7", linestyle=":", linewidth=1)
            ax.set_title("Concentration toward P0")
            ax.set_xlabel("round")
            ax.legend(frameon=False, fontsize=7)
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
