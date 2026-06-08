"""Experiment C forgiveness metrics and figure builders."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from analysis.phenotypes.common import (
    build_phenotype_variants,
    common_group_metrics,
    forgiveness_scenario,
    make_spec,
    save_figure,
    summarize_for_plot,
    variant_label,
    vector_value,
)

EXP_C_PANELS = (
    "reengagement_rate",
    "beta_recovery_trajectory",
    "payoff_recovery",
)
BETA_RECOVERY_ROUNDS = (80, 100, 120, 140, 160, 180, 200)


def build_specs(*, rounds: int, seeds: int, seed: int):
    return (
        make_spec(
            hypothesis_id="exp_c",
            hypothesis_name="forgiveness",
            experiment_id="forgiveness",
            scenario=forgiveness_scenario(),
            variants=build_phenotype_variants(),
            rounds=rounds,
            replications=seeds,
            seed=seed,
        ),
    )


def _reengagement_latency(group: pd.DataFrame) -> float:
    post = group[pd.to_numeric(group["round"], errors="coerce") >= 121]
    hits = post[pd.to_numeric(post["partner_idx"], errors="coerce") == 0]
    if hits.empty:
        return float("nan")
    return float(pd.to_numeric(hits["round"], errors="coerce").min() - 121)


def _payoff_recovery(group: pd.DataFrame) -> float:
    pre = pd.to_numeric(group.loc[group["round"].between(50, 80), "payoff"], errors="coerce").mean()
    repaired = pd.to_numeric(group.loc[group["round"].between(151, 200), "payoff"], errors="coerce").mean()
    if pd.isna(pre) or abs(float(pre)) < 1e-12:
        return float("nan")
    return float(repaired / pre)


def _partner0_beta_epoch(group: pd.DataFrame, start: int, end: int) -> float:
    rows = group[group["round"].between(start, end)]
    values = [vector_value(value, 0) for value in rows["local_betas"]]
    return float(pd.Series(values).mean()) if values else float("nan")


def _partner0_beta_at_round(group: pd.DataFrame, target_round: int) -> float:
    rounds = pd.to_numeric(group["round"], errors="coerce")
    rows = group[rounds == int(target_round)]
    if rows.empty:
        rows = group[rounds == rounds[rounds <= int(target_round)].max()]
    if rows.empty:
        return float("nan")
    values = [vector_value(value, 0) for value in rows["local_betas"]]
    return float(pd.Series(values).mean()) if values else float("nan")


def metrics(results: pd.DataFrame) -> pd.DataFrame:
    data = pd.DataFrame(common_group_metrics(results))
    rows = []
    for keys, group in results.groupby(["experiment_id", "variant_id", "seed"], dropna=False):
        experiment_id, variant_id, seed = keys
        post = group[pd.to_numeric(group["round"], errors="coerce") >= 121]
        rows.append(
            {
                "experiment_id": experiment_id,
                "variant_id": variant_id,
                "seed": int(seed),
                "reengagement_rate": float((pd.to_numeric(post["partner_idx"], errors="coerce") == 0).mean())
                if len(post)
                else float("nan"),
                "payoff_recovery": _payoff_recovery(group),
                "reengagement_latency": _reengagement_latency(group),
                "beta_pre": _partner0_beta_epoch(group, 1, 80),
                "beta_betrayal": _partner0_beta_epoch(group, 81, 120),
                "beta_repair": _partner0_beta_epoch(group, 121, 200),
                **{
                    f"beta_recovery_r{target_round:03d}": _partner0_beta_at_round(group, target_round)
                    for target_round in BETA_RECOVERY_ROUNDS
                },
            }
        )
    return data.merge(pd.DataFrame(rows), on=["experiment_id", "variant_id", "seed"], how="left")


def figure(metrics_df: pd.DataFrame, figure_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, metric in zip(axes, EXP_C_PANELS, strict=True):
        if metric == "beta_recovery_trajectory":
            trajectory_cols = [f"beta_recovery_r{target_round:03d}" for target_round in BETA_RECOVERY_ROUNDS]
            summary = metrics_df.groupby("variant_id", dropna=False)[trajectory_cols].mean().reset_index()
            for _, row in summary.iterrows():
                ax.plot(
                    BETA_RECOVERY_ROUNDS,
                    [row[col] for col in trajectory_cols],
                    marker="o",
                    label=variant_label(str(row["variant_id"])),
                )
            ax.axvline(81, color="0.4", linestyle="--", linewidth=1)
            ax.axvline(121, color="0.4", linestyle="--", linewidth=1)
            ax.set_title("Beta recovery trajectory")
            ax.set_xlabel("round")
            ax.legend(frameon=False, fontsize=7)
        else:
            summary = summarize_for_plot(metrics_df, ["variant_id"], metric)
            ax.bar([variant_label(item) for item in summary["variant_id"]], summary[metric])
            ax.set_title(variant_label(metric))
            ax.tick_params(axis="x", rotation=35)
            if metric == "payoff_recovery":
                ax.axhline(1.0, color="0.4", linestyle="--", linewidth=1)
    save_figure(fig, figure_dir / "fig_forgiveness.pdf")
