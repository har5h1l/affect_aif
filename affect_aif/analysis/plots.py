"""Plot helpers for the main experiment figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from affect_aif.analysis.metrics import (
    beta_reward_divergence,
    betrayal_trajectory,
    final_round_summary,
    has_switch_events,
    payoff_by_partner_type,
)


def _save_betrayal_figures(results: pd.DataFrame, out: Path):
    trajectory = betrayal_trajectory(results, max_encounters=10)
    if trajectory.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True)
    sns.lineplot(
        data=trajectory,
        x="encounters_since_switch",
        y="beta",
        hue="condition_name",
        ax=axes[0],
        errorbar="sd",
    )
    axes[0].set_title("Post-Betrayal Beta Trajectory")
    axes[0].set_xlabel("Encounters Since Switch")
    axes[0].set_ylabel("Beta")
    sns.lineplot(
        data=trajectory,
        x="encounters_since_switch",
        y="terminal_signal",
        hue="condition_name",
        ax=axes[1],
        errorbar="sd",
        legend=False,
    )
    axes[1].set_title("Post-Betrayal Terminal Signal")
    axes[1].set_xlabel("Encounters Since Switch")
    axes[1].set_ylabel("Terminal Signal")
    fig.tight_layout()
    fig.savefig(out / "figure_7_betrayal_signal_trajectories.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(
        data=trajectory,
        x="encounters_since_switch",
        y="divergence_beta_minus_reward",
        hue="condition_name",
        ax=ax,
        errorbar="sd",
    )
    ax.set_title("Post-Betrayal Beta vs Reward Divergence")
    ax.set_xlabel("Encounters Since Switch")
    ax.set_ylabel("Beta - Reward Signal")
    fig.tight_layout()
    fig.savefig(out / "figure_8_betrayal_beta_reward_divergence.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(
        data=trajectory,
        x="encounters_since_switch",
        y="payoff",
        hue="condition_name",
        ax=ax,
        errorbar="sd",
    )
    ax.set_title("Post-Betrayal Payoff Recovery")
    ax.set_xlabel("Encounters Since Switch")
    ax.set_ylabel("Payoff")
    fig.tight_layout()
    fig.savefig(out / "figure_9_betrayal_payoff_recovery.png", dpi=180)
    plt.close(fig)


def _save_horizon_sweep_figure(summary: pd.DataFrame, out: Path):
    horizon_map = {
        "tau1_no_affect": (1, "No affect"),
        "tau1_affect": (1, "Affect"),
        "tau2_no_affect": (2, "No affect"),
        "tau2_affect": (2, "Affect"),
        "tau4_no_affect": (4, "No affect"),
        "tau4_affect": (4, "Affect"),
        "tau8_no_affect": (8, "No affect"),
        "tau8_affect": (8, "Affect"),
    }
    sweep = summary[summary["condition_name"].isin(horizon_map)].copy()
    if sweep["condition_name"].nunique() < 2:
        return

    sweep["planning_horizon"] = sweep["condition_name"].map(lambda name: horizon_map[name][0])
    sweep["signal_family"] = sweep["condition_name"].map(lambda name: horizon_map[name][1])
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
    sns.barplot(data=summary, x="condition_name", y="total_payoff", ax=ax, errorbar="sd")
    ax.set_title("Cumulative Payoff by Condition")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_1_cumulative_payoff.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    accuracy_column = "mean_joint_accuracy" if "mean_joint_accuracy" in summary.columns else "mean_accuracy"
    sns.barplot(data=summary, x="condition_name", y=accuracy_column, ax=ax, errorbar="sd")
    ax.set_title("Joint Type-Stance Identification Accuracy")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_2_accuracy.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=partner_summary, x="true_partner_type", y="mean_payoff", hue="condition_name", ax=ax)
    ax.set_title("Payoff by True Partner Type")
    fig.tight_layout()
    fig.savefig(out / "figure_3_partner_type_payoff.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary, x="condition_name", y="planning_cost_ratio", ax=ax)
    ax.set_title("Deterministic Planning Cost Ratio")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_4_planning_cost.png", dpi=180)
    plt.close(fig)

    divergence = beta_reward_divergence(results)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=divergence, x="round", y="divergence", hue="condition_name", ax=ax, errorbar="sd")
    ax.set_title("Beta vs Reward-Average Divergence")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out / "figure_5_beta_reward_divergence.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary, x="condition_name", y="mean_abs_step_efe", ax=ax, errorbar="sd")
    ax.set_title("Mean |EFE| per Deep-Policy Step")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(out / "figure_6_mean_abs_step_efe.png", dpi=180)
    plt.close(fig)

    _save_horizon_sweep_figure(summary, out)

    if has_switch_events(results):
        _save_betrayal_figures(results, out)
