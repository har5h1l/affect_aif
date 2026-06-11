"""Forgiveness metrics and figure builders."""

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
    variant_label,
    vector_value,
)

EXP_C_PANELS = (
    "reengagement_rate",
    "beta_recovery_trajectory",
    "payoff_recovery",
)
BETA_RECOVERY_ROUNDS = (80, 100, 120, 140, 160, 180, 200)
EXP_C_TABLE8 = (
    ("cautious_high_alpha", 0.518, 0.996),
    ("cautious_low_alpha", 0.630, 1.014),
    ("default_reference", 0.475, 1.019),
    ("naive_high_alpha", 0.560, 1.005),
    ("naive_low_alpha", 0.527, 1.004),
    ("no_affect", 0.593, 1.033),
)
EXP_C_BETA_TRAJECTORY_VARIANTS = tuple(row[0] for row in EXP_C_TABLE8 if row[0] != "no_affect")


def build_specs(*, rounds: int, seeds: int, seed: int):
    return (
        make_spec(
            hypothesis_id="forgiveness",
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
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.6), gridspec_kw={"width_ratios": [1.1, 2.4, 0.9]})
    table = pd.DataFrame(EXP_C_TABLE8, columns=["variant_id", "reengagement_rate", "payoff_recovery"])
    labels = [variant_label(item) for item in table["variant_id"]]

    y_positions = range(len(table))
    axes[0].barh(y_positions, table["reengagement_rate"], color="#4c78a8")
    axes[0].set_yticks(y_positions)
    axes[0].set_yticklabels(labels, fontsize=7)
    axes[0].invert_yaxis()
    axes[0].set_title("A. Reengagement")
    axes[0].set_xlabel("post-repair P0 selection")
    axes[0].set_xlim(0.0, 0.7)

    trajectory_cols = [f"beta_recovery_r{target_round:03d}" for target_round in BETA_RECOVERY_ROUNDS]
    summary = metrics_df.groupby("variant_id", dropna=False)[trajectory_cols].mean().reset_index()
    summary = summary[summary["variant_id"].isin(EXP_C_BETA_TRAJECTORY_VARIANTS)]
    summary["variant_id"] = pd.Categorical(
        summary["variant_id"], categories=EXP_C_BETA_TRAJECTORY_VARIANTS, ordered=True
    )
    summary = summary.sort_values("variant_id")
    axes[1].axvspan(81, 120, color="0.9", zorder=0)
    axes[1].axvline(80, color="0.45", linestyle="--", linewidth=1)
    axes[1].axvline(121, color="0.45", linestyle="--", linewidth=1)
    for _, row in summary.iterrows():
        axes[1].plot(
            BETA_RECOVERY_ROUNDS,
            [row[col] for col in trajectory_cols],
            marker="o",
            linewidth=1.8,
            markersize=4,
            label=variant_label(str(row["variant_id"])),
        )
    axes[1].set_title(r"B. Reverted-partner $E_q[\beta_k]$")
    axes[1].set_xlabel("round")
    axes[1].set_ylabel(r"P0 $E_q[\beta_k]$ (inverse precision)")
    axes[1].set_xlim(78, 200)
    axes[1].set_xticks(BETA_RECOVERY_ROUNDS)
    axes[1].text(
        100.5,
        0.98,
        "betrayal",
        transform=axes[1].get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=7,
        color="0.35",
    )
    axes[1].legend(frameon=False, fontsize=7, ncol=2, loc="lower right")

    axes[2].barh(y_positions, table["payoff_recovery"], color="#f58518")
    axes[2].axvline(1.0, color="0.4", linestyle="--", linewidth=1)
    axes[2].set_yticks(y_positions)
    axes[2].set_yticklabels([])
    axes[2].invert_yaxis()
    axes[2].set_title("C. Payoff recovery")
    axes[2].set_xlabel("late repair / pre-betrayal payoff")
    axes[2].set_xlim(0.94, 1.06)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, figure_dir / "fig_forgiveness.pdf")
