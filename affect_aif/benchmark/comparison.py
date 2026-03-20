"""Cross-environment comparison analysis and plotting."""

from __future__ import annotations

import numpy as np
import pandas as pd

from affect_aif.benchmark.common_metrics import (
    cooperation_rate,
    cumulative_payoff,
    mean_payoff,
    partner_discrimination,
    type_identification_accuracy,
)


def compute_comparison_table(results: pd.DataFrame) -> pd.DataFrame:
    """Compute a summary table comparing agents across environments.

    Parameters
    ----------
    results : pd.DataFrame
        Combined results with 'environment' and 'agent_name' columns.

    Returns
    -------
    pd.DataFrame
        Summary with one row per (agent_name, environment) combination.
    """
    rows = []
    for (agent_name, env), group in results.groupby(["agent_name", "environment"]):
        row = {
            "agent_name": agent_name,
            "environment": env,
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


def compute_transfer_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Compute how each agent's performance transfers between environments.

    Returns a DataFrame with columns: agent_name, trust_payoff, grid_payoff,
    transfer_gap, trust_coop, grid_coop.
    """
    trust = results[results["environment"] == "trust_game"]
    grid = results[results["environment"].isin(["gridworld", "cogames", "simulated_gridworld"])]

    if trust.empty or grid.empty:
        return pd.DataFrame()

    rows = []
    for agent_name in results["agent_name"].unique():
        t = trust[trust["agent_name"] == agent_name]
        g = grid[grid["agent_name"] == agent_name]
        if t.empty or g.empty:
            continue
        rows.append({
            "agent_name": agent_name,
            "trust_payoff": mean_payoff(t),
            "grid_payoff": mean_payoff(g),
            "transfer_gap": mean_payoff(t) - mean_payoff(g),
            "trust_coop": cooperation_rate(t),
            "grid_coop": cooperation_rate(g),
        })

    return pd.DataFrame(rows)


def format_comparison_report(results: pd.DataFrame) -> str:
    """Generate a human-readable comparison report."""
    comparison = compute_comparison_table(results)
    transfer = compute_transfer_summary(results)

    lines = ["# Benchmark Comparison Report", ""]

    lines.append("## Per-Environment Summary")
    lines.append("")
    if not comparison.empty:
        lines.append(comparison.to_string(index=False))
    else:
        lines.append("No data available.")

    lines.append("")
    lines.append("## Transfer Analysis")
    lines.append("")
    if not transfer.empty:
        lines.append(transfer.to_string(index=False))

        # Highlight key findings
        lines.append("")
        lines.append("### Key Findings")
        best_transfer = transfer.loc[transfer["transfer_gap"].abs().idxmin()]
        worst_transfer = transfer.loc[transfer["transfer_gap"].abs().idxmax()]
        lines.append(
            f"- Best transfer: {best_transfer['agent_name']} "
            f"(gap: {best_transfer['transfer_gap']:.3f})"
        )
        lines.append(
            f"- Worst transfer: {worst_transfer['agent_name']} "
            f"(gap: {worst_transfer['transfer_gap']:.3f})"
        )
    else:
        lines.append("Need both trust_game and gridworld results for transfer analysis.")

    return "\n".join(lines)
