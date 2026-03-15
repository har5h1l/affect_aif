"""Plot helpers for the main experiment figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from affect_aif.analysis.metrics import beta_reward_divergence, final_round_summary, payoff_by_partner_type


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
    fig.tight_layout()
    fig.savefig(out / "figure_1_cumulative_payoff.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary, x="condition_name", y="mean_accuracy", ax=ax, errorbar="sd")
    ax.set_title("Partner-Type Identification Accuracy")
    ax.set_xlabel("")
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
    fig.tight_layout()
    fig.savefig(out / "figure_4_planning_cost.png", dpi=180)
    plt.close(fig)

    divergence = beta_reward_divergence(results)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=divergence, x="round", y="divergence", hue="condition_name", ax=ax, errorbar="sd")
    ax.set_title("β vs Reward-Average Divergence")
    fig.tight_layout()
    fig.savefig(out / "figure_5_beta_reward_divergence.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=summary, x="condition_name", y="mean_abs_step_efe", ax=ax, errorbar="sd")
    ax.set_title("Mean |EFE| per Deep-Policy Step")
    ax.set_xlabel("")
    fig.tight_layout()
    fig.savefig(out / "figure_6_mean_abs_step_efe.png", dpi=180)
    plt.close(fig)
