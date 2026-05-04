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


def compute_cvc_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Summarize CvC-local metrics from episode-level records."""
    cvc = results[results["backend"] == "cvc_local"]
    if cvc.empty:
        return pd.DataFrame()

    aggregate_fields = {
        "reward": "mean",
        "team_reward_sum": "mean",
        "team_reward_var": "mean",
        "aligned_junctions": "mean",
        "scrambled_junctions": "mean",
        "hearts_gained": "mean",
        "miner_role_gains": "mean",
        "aligner_role_gains": "mean",
        "scrambler_role_gains": "mean",
        "scout_role_gains": "mean",
    }
    available = {key: value for key, value in aggregate_fields.items() if key in cvc.columns}
    if not available:
        return cvc.groupby("agent_name", as_index=False).agg(mean_episode_reward=("reward", "mean"))

    return cvc.groupby("agent_name", as_index=False).agg(**{f"mean_{k}": (k, v) for k, v in available.items()})


def format_comparison_report(results: pd.DataFrame) -> str:
    """Generate a backend-aware benchmark report."""
    shared = compute_shared_summary(results)
    trust = compute_trust_summary(results)
    cvc = compute_cvc_summary(results)

    lines = ["# Benchmark Comparison Report", ""]
    lines.append("## Shared Summary")
    lines.append("")
    lines.append(shared.to_string(index=False) if not shared.empty else "No data available.")

    lines.append("")
    lines.append("## Trust Backend")
    lines.append("")
    lines.append(trust.to_string(index=False) if not trust.empty else "No trust backend data.")

    lines.append("")
    lines.append("## CvC Backend")
    lines.append("")
    lines.append(cvc.to_string(index=False) if not cvc.empty else "No CvC backend data.")

    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(
        "Cross-backend comparison uses shared reward summaries only. Trust-specific and CvC-specific metrics are "
        "reported separately rather than forcing action semantics into a fake shared environment model."
    )

    return "\n".join(lines)
