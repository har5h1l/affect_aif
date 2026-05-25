"""Backend-aware benchmark analysis and reporting."""

from __future__ import annotations

import numpy as np
import pandas as pd

from benchmarks.core.common_metrics import (
    cooperation_rate,
    cumulative_payoff,
    mean_payoff,
    partner_discrimination,
    type_identification_accuracy,
)


def compute_shared_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate reward-centric metrics that are comparable across backends."""
    if results.empty:
        return pd.DataFrame()

    episode_rewards = results.groupby(["backend", "agent_name", "seed", "episode_id"], as_index=False).agg(
        episode_reward=("reward", "sum"),
        scenario=("scenario", "first"),
        episode_runtime_s=("episode_runtime_s", "max")
        if "episode_runtime_s" in results.columns
        else ("reward", lambda s: np.nan),
    )

    return (
        episode_rewards.groupby(["backend", "agent_name"], as_index=False)
        .agg(
            scenario=("scenario", "first"),
            num_episodes=("episode_id", "nunique"),
            mean_episode_reward=("episode_reward", "mean"),
            std_episode_reward=("episode_reward", "std"),
            reward_variance=("episode_reward", "var"),
            mean_episode_runtime_s=("episode_runtime_s", "mean"),
        )
        .fillna({"std_episode_reward": 0.0, "reward_variance": 0.0})
    )


def compute_trust_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize trust-only metrics."""
    trust = results[results["backend"] == "trust"]
    if trust.empty:
        return pd.DataFrame()

    rows = []
    for agent_name, group in trust.groupby("agent_name"):
        row = {
            "agent_name": agent_name,
            "cooperation_rate": cooperation_rate(group),
            "mean_payoff": mean_payoff(group),
            "cumulative_payoff": cumulative_payoff(group),
            "partner_discrimination": partner_discrimination(group),
        }
        acc = type_identification_accuracy(group)
        if not np.isnan(acc):
            row["type_id_accuracy"] = acc
        rows.append(row)

    return pd.DataFrame(rows)


def format_comparison_report(results: pd.DataFrame) -> str:
    """Generate a backend-aware benchmark report."""
    shared = compute_shared_summary(results)
    trust = compute_trust_summary(results)

    lines = ["# Benchmark Comparison Report", ""]
    lines.append("## Shared Summary")
    lines.append("")
    lines.append(shared.to_string(index=False) if not shared.empty else "No data available.")

    lines.append("")
    lines.append("## Trust Backend")
    lines.append("")
    lines.append(trust.to_string(index=False) if not trust.empty else "No trust backend data.")

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "The maintained benchmark surface is the trust-task evaluation arena. "
        "Trust-specific metrics are reported separately from shared reward summaries."
    )

    return "\n".join(lines)
