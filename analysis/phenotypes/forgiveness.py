"""Forgiveness metrics and figure builders."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from analysis.figure_style import apply_manuscript_figure_style
from analysis.phenotypes.common import (
    build_phenotype_variants,
    common_group_metrics,
    forgiveness_scenario,
    make_spec,
    protocol_rounds,
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
EXP_C_PROFILE_ORDER = (
    "cautious_high_alpha",
    "cautious_low_alpha",
    "default_reference",
    "naive_high_alpha",
    "naive_low_alpha",
    "no_affect",
)
EXP_C_BETA_TRAJECTORY_VARIANTS = tuple(item for item in EXP_C_PROFILE_ORDER if item != "no_affect")


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
    post = group[protocol_rounds(group) >= 121]
    hits = post[pd.to_numeric(post["partner_idx"], errors="coerce") == 0]
    if hits.empty:
        return float("nan")
    return float(protocol_rounds(hits).min() - 121)


def _payoff_recovery(group: pd.DataFrame) -> float:
    pre = pd.to_numeric(group.loc[protocol_rounds(group).between(50, 80), "payoff"], errors="coerce").mean()
    repaired = pd.to_numeric(group.loc[protocol_rounds(group).between(151, 200), "payoff"], errors="coerce").mean()
    if pd.isna(pre) or abs(float(pre)) < 1e-12:
        return float("nan")
    return float(repaired / pre)


def _partner0_beta_epoch(group: pd.DataFrame, start: int, end: int) -> float:
    rows = group[protocol_rounds(group).between(start, end)]
    values = [vector_value(value, 0) for value in rows["local_betas"]]
    return float(pd.Series(values).mean()) if values else float("nan")


def _partner0_beta_at_round(group: pd.DataFrame, target_round: int) -> float:
    rounds = protocol_rounds(group)
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
        post = group[protocol_rounds(group) >= 121]
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
    apply_manuscript_figure_style()
    fig = plt.figure(figsize=(12.2 / 2.54, 3.9))
    # The trajectory uses the full width; only the lower bars reserve a label margin.
    trajectory = fig.add_axes([0.13, 0.64, 0.84, 0.28])
    legend_ax = fig.add_axes([0.13, 0.415, 0.84, 0.13])
    legend_ax.axis("off")
    reengagement = fig.add_axes([0.30, 0.12, 0.28, 0.21])
    payoff = fig.add_axes([0.69, 0.12, 0.28, 0.21], sharey=reengagement)
    axes = [reengagement, trajectory, payoff]
    table = metrics_df.groupby("variant_id", dropna=False)[["reengagement_rate", "payoff_recovery"]].mean()
    missing = sorted(item for item in EXP_C_PROFILE_ORDER if item not in table.index)
    if missing:
        raise ValueError(f"forgiveness figure missing profiles: {', '.join(missing)}")
    table = table.loc[list(EXP_C_PROFILE_ORDER)].reset_index()
    display_labels = {
        "cautious_high_alpha": r"cautious-high-$\alpha$",
        "cautious_low_alpha": r"cautious-low-$\alpha$",
        "default_reference": "default",
        "naive_high_alpha": r"naive-high-$\alpha$",
        "naive_low_alpha": r"naive-low-$\alpha$",
        "no_affect": "no-affect",
    }
    labels = [display_labels.get(str(item), variant_label(item)) for item in table["variant_id"]]

    y_positions = range(len(table))
    axes[0].barh(y_positions, table["reengagement_rate"], color="#4c78a8")
    axes[0].set_yticks(y_positions)
    axes[0].set_yticklabels(labels, fontsize=9)
    axes[0].invert_yaxis()
    axes[0].set_title("B. Reengagement")
    axes[0].set_xlabel("post-repair P0 selection")
    axes[0].set_xlim(0.0, 0.7)
    axes[0].set_xticks([0.0, 0.2, 0.4, 0.6])

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
    for style_idx, (_, row) in enumerate(summary.iterrows()):
        axes[1].plot(
            BETA_RECOVERY_ROUNDS,
            [row[col] for col in trajectory_cols],
            marker=("o", "s", "^", "D", "v")[style_idx],
            linestyle=("-", "--", ":", "-.", (0, (3, 1, 1, 1)))[style_idx],
            linewidth=1.8,
            markersize=4,
            label=display_labels.get(str(row["variant_id"]), variant_label(str(row["variant_id"]))),
        )
    axes[1].set_title(r"A. Reverted-partner posterior mean $\beta_k$")
    axes[1].set_xlabel("round")
    axes[1].set_ylabel(r"P0 posterior mean $\beta_k$")
    axes[1].set_xlim(78, 200)
    axes[1].set_xticks(BETA_RECOVERY_ROUNDS)
    axes[1].text(
        100.5,
        0.05,
        "betrayal",
        transform=axes[1].get_xaxis_transform(),
        ha="center",
        va="bottom",
        fontsize=8,
        color="0.35",
    )
    legend_ax.legend(*axes[1].get_legend_handles_labels(), frameon=False, fontsize=9, ncol=2, loc="center")

    axes[2].barh(y_positions, table["payoff_recovery"], color="#f58518")
    axes[2].axvline(1.0, color="0.4", linestyle="--", linewidth=1)
    axes[2].set_yticks(y_positions)
    axes[2].tick_params(axis="y", labelleft=False)
    axes[2].set_title("C. Payoff recovery")
    axes[2].set_xlabel("late repair /\npre-betrayal payoff")
    axes[2].set_xlim(0.94, 1.08)
    axes[2].set_xticks([0.95, 1.00, 1.05])
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, figure_dir / "fig_forgiveness.pdf", tight_layout=False)
