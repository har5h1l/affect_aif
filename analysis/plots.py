"""Plot helpers for the main experiment figures."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from analysis.metrics import (
    beta_reward_divergence,
    betrayal_trajectory,
    final_round_summary,
    has_switch_events,
    payoff_by_partner_type,
)


def _mean_sd_frame(frame: pd.DataFrame, group_cols: list[str], value_col: str) -> pd.DataFrame:
    """Pre-aggregate repeated trajectories before plotting."""

    return (
        frame.groupby(group_cols, as_index=False)[value_col]
        .agg(["mean", "std"])
        .reset_index()
        .rename(columns={"mean": value_col, "std": f"{value_col}_sd"})
    )


def _plot_mean_sd_lines(
    ax,
    frame: pd.DataFrame,
    *,
    x_col: str,
    y_col: str,
    hue_col: str,
):
    """Draw pre-aggregated mean trajectories with one-sigma bands."""

    for label, group in frame.groupby(hue_col, sort=False):
        group = group.sort_values(x_col)
        ax.plot(group[x_col], group[y_col], label=label)
        sd_col = f"{y_col}_sd"
        if sd_col in group.columns:
            lower = group[y_col] - group[sd_col].fillna(0.0)
            upper = group[y_col] + group[sd_col].fillna(0.0)
            ax.fill_between(group[x_col], lower, upper, alpha=0.2)


def _save_betrayal_figures(results: pd.DataFrame, out: Path):
    trajectory = betrayal_trajectory(results, max_encounters=10)
    if trajectory.empty:
        return
    trajectory = (
        _mean_sd_frame(trajectory, ["variant_id", "encounters_since_switch"], "beta")
        .merge(
            _mean_sd_frame(trajectory, ["variant_id", "encounters_since_switch"], "divergence_beta_minus_reward"),
            on=["variant_id", "encounters_since_switch"],
            how="left",
        )
        .merge(
            _mean_sd_frame(trajectory, ["variant_id", "encounters_since_switch"], "payoff"),
            on=["variant_id", "encounters_since_switch"],
            how="left",
        )
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True)
    _plot_mean_sd_lines(
        axes[0],
        trajectory,
        x_col="encounters_since_switch",
        y_col="beta",
        hue_col="variant_id",
    )
    axes[0].set_title("Post-Betrayal Beta Trajectory")
    axes[0].set_xlabel("Encounters Since Switch")
    axes[0].set_ylabel("Beta")
    axes[1].axis("off")
    axes[0].legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "figure_7_betrayal_signal_trajectories.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    _plot_mean_sd_lines(
        ax,
        trajectory,
        x_col="encounters_since_switch",
        y_col="divergence_beta_minus_reward",
        hue_col="variant_id",
    )
    ax.set_title("Post-Betrayal Beta vs Reward Divergence")
    ax.set_xlabel("Encounters Since Switch")
    ax.set_ylabel("Beta - Reward Signal")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "figure_8_betrayal_beta_reward_divergence.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    _plot_mean_sd_lines(
        ax,
        trajectory,
        x_col="encounters_since_switch",
        y_col="payoff",
        hue_col="variant_id",
    )
    ax.set_title("Post-Betrayal Payoff Recovery")
    ax.set_xlabel("Encounters Since Switch")
    ax.set_ylabel("Payoff")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "figure_9_betrayal_payoff_recovery.png", dpi=180)
    plt.close(fig)


def _save_horizon_sweep_figure(summary: pd.DataFrame, out: Path):
    sweep = summary[summary["variant_id"].astype(str).str.contains("__planning_horizon_")].copy()
    if sweep["variant_id"].nunique() < 2:
        return

    sweep["planning_horizon"] = sweep["variant_id"].map(
        lambda name: int(re.search(r"__planning_horizon_(\d+)", str(name)).group(1))
    )
    sweep["signal_family"] = sweep["variant_id"].map(
        lambda name: "No affect" if str(name).startswith("no_affect") else "Affect"
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(
        data=sweep,
        x="planning_horizon",
        y="total_payoff",
        hue="signal_family",
        marker="o",
        estimator="mean",
        errorbar="sd",
        ax=ax,
    )

    ax.set_title("Payoff vs Planning Horizon")
    ax.set_xlabel("Planning Horizon")
    ax.set_ylabel("Cumulative Payoff")
    fig.tight_layout()
    fig.savefig(out / "figure_10_horizon_sweep.png", dpi=180)
    plt.close(fig)


def save_all_figures(results: pd.DataFrame, output_dir: str):
    """Generate a compact figure set from the results table."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    summary = final_round_summary(results)
    partner_summary = payoff_by_partner_type(results)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary, x="variant_id", y="total_payoff", ax=ax, errorbar="sd")
    ax.set_title("Cumulative Payoff by Variant")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_1_cumulative_payoff.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    accuracy_column = "mean_joint_accuracy" if "mean_joint_accuracy" in summary.columns else "mean_accuracy"
    sns.barplot(data=summary, x="variant_id", y=accuracy_column, ax=ax, errorbar="sd")
    ax.set_title("Joint Type-Stance Identification Accuracy")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_2_accuracy.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=partner_summary, x="true_partner_type", y="mean_payoff", hue="variant_id", ax=ax)
    ax.set_title("Payoff by True Partner Type")
    fig.tight_layout()
    fig.savefig(out / "figure_3_partner_type_payoff.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary, x="variant_id", y="planning_cost_ratio", ax=ax)
    ax.set_title("Deterministic Planning Cost Ratio")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_4_planning_cost.png", dpi=180)
    plt.close(fig)

    divergence = beta_reward_divergence(results)
    divergence = _mean_sd_frame(divergence, ["variant_id", "round"], "divergence")
    fig, ax = plt.subplots(figsize=(8, 5))
    _plot_mean_sd_lines(ax, divergence, x_col="round", y_col="divergence", hue_col="variant_id")
    ax.set_title("Beta vs Reward-Average Divergence")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "figure_5_beta_reward_divergence.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary, x="variant_id", y="mean_abs_step_efe", ax=ax, errorbar="sd")
    ax.set_title("Mean |EFE| per Deep-Policy Step")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_6_mean_abs_step_efe.png", dpi=180)
    plt.close(fig)

    _save_horizon_sweep_figure(summary, out)

    if has_switch_events(results):
        _save_betrayal_figures(results, out)
