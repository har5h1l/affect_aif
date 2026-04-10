#!/usr/bin/env python3
"""Paper-quality benchmark analysis with statistical tests and time-series data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.common_metrics import (
    adaptation_speed,
    cooperation_rate,
    cumulative_payoff,
    mean_payoff,
    partner_discrimination,
    type_identification_accuracy,
)


def episode_rewards(df: pd.DataFrame) -> pd.DataFrame:
    """Per-episode total reward for each agent and seed."""
    return (
        df.groupby(["agent_name", "seed", "episode_id"], as_index=False)
        .agg(episode_reward=("reward", "sum"), num_rounds=("step", "count"))
    )


def agent_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-agent summary with confidence intervals."""
    ep = episode_rewards(df)
    rows = []
    for agent, group in ep.groupby("agent_name"):
        rewards = group["episode_reward"].values
        n = len(rewards)
        mean = np.mean(rewards)
        std = np.std(rewards, ddof=1)
        se = std / np.sqrt(n)
        ci95 = 1.96 * se
        rows.append({
            "agent_name": agent,
            "n_episodes": n,
            "mean_reward": mean,
            "std_reward": std,
            "ci95_low": mean - ci95,
            "ci95_high": mean + ci95,
            "cooperation_rate": cooperation_rate(df[df["agent_name"] == agent]),
            "mean_payoff": mean_payoff(df[df["agent_name"] == agent]),
            "partner_discrimination": partner_discrimination(df[df["agent_name"] == agent]),
            "type_id_accuracy": type_identification_accuracy(df[df["agent_name"] == agent]),
        })
    return pd.DataFrame(rows).sort_values("mean_reward", ascending=False)


def pairwise_tests(df: pd.DataFrame) -> pd.DataFrame:
    """Mann-Whitney U tests between all agent pairs on episode reward."""
    ep = episode_rewards(df)
    agents = sorted(ep["agent_name"].unique())
    rows = []
    for i, a1 in enumerate(agents):
        for a2 in agents[i + 1:]:
            r1 = ep[ep["agent_name"] == a1]["episode_reward"].values
            r2 = ep[ep["agent_name"] == a2]["episode_reward"].values
            u_stat, p_val = stats.mannwhitneyu(r1, r2, alternative="two-sided")
            # Effect size: rank-biserial correlation
            n1, n2 = len(r1), len(r2)
            effect_size = 1 - (2 * u_stat) / (n1 * n2)
            rows.append({
                "agent_1": a1,
                "agent_2": a2,
                "mean_1": np.mean(r1),
                "mean_2": np.mean(r2),
                "U_statistic": u_stat,
                "p_value": p_val,
                "effect_size_r": effect_size,
                "significant_005": p_val < 0.05,
            })
    return pd.DataFrame(rows)


def time_series_payoff(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Rolling mean payoff per agent over rounds."""
    rows = []
    for agent, group in df.groupby("agent_name"):
        round_means = group.groupby("step")["payoff"].mean()
        rolling = round_means.rolling(window, min_periods=1).mean()
        for step, val in rolling.items():
            rows.append({"agent_name": agent, "step": step, "rolling_mean_payoff": val})
    return pd.DataFrame(rows)


def time_series_cooperation(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Rolling cooperation rate per agent over rounds."""
    rows = []
    for agent, group in df.groupby("agent_name"):
        round_coop = group.groupby("step")["agent_action"].apply(lambda s: (s == 0).mean())
        rolling = round_coop.rolling(window, min_periods=1).mean()
        for step, val in rolling.items():
            rows.append({"agent_name": agent, "step": step, "rolling_cooperation_rate": val})
    return pd.DataFrame(rows)


def adaptation_analysis(df: pd.DataFrame, switch_round: int = 50) -> pd.DataFrame:
    """Pre/post switch performance comparison per agent."""
    # The benchmark CSV uses 'step' not 'round'
    round_col = "round" if "round" in df.columns else "step"
    rows = []
    for agent, group in df.groupby("agent_name"):
        pre = group[group[round_col] < switch_round]
        post = group[group[round_col] >= switch_round]
        pre_payoff = pre["payoff"].mean() if len(pre) > 0 else np.nan
        post_payoff = post["payoff"].mean() if len(post) > 0 else np.nan
        pre_coop = (pre["agent_action"] == 0).mean() if len(pre) > 0 else np.nan
        post_coop = (post["agent_action"] == 0).mean() if len(post) > 0 else np.nan

        # Adaptation speed for AIF agents (requires inferred_type_correct)
        speed = np.nan
        if "inferred_type_correct" in group.columns:
            # adaptation_speed expects 'round' column — add it temporarily
            group_with_round = group.copy()
            if "round" not in group_with_round.columns:
                group_with_round["round"] = group_with_round[round_col]
            speed = adaptation_speed(group_with_round, switch_round, accuracy_threshold=0.7, window=5)

        rows.append({
            "agent_name": agent,
            "pre_switch_payoff": pre_payoff,
            "post_switch_payoff": post_payoff,
            "payoff_drop": pre_payoff - post_payoff,
            "payoff_recovery_ratio": post_payoff / pre_payoff if pre_payoff != 0 else np.nan,
            "pre_switch_coop": pre_coop,
            "post_switch_coop": post_coop,
            "adaptation_speed": speed,
        })
    return pd.DataFrame(rows).sort_values("post_switch_payoff", ascending=False)


def main():
    parser = argparse.ArgumentParser(description="Paper-quality benchmark analysis.")
    parser.add_argument("--results", required=True, help="Path to benchmark_results.csv")
    parser.add_argument("--output-dir", required=False, help="Output directory")
    parser.add_argument("--switch-round", type=int, default=50, help="Round of partner switch (for betrayal analysis)")
    args = parser.parse_args()

    df = pd.read_csv(args.results)
    output_dir = Path(args.output_dir) if args.output_dir else Path(args.results).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Agent summary with CIs
    summary = agent_summary(df)
    summary.to_csv(output_dir / "agent_summary.csv", index=False)
    print("=== Agent Summary ===")
    print(summary.to_string(index=False))
    print()

    # 2. Pairwise statistical tests
    pairwise = pairwise_tests(df)
    pairwise.to_csv(output_dir / "pairwise_tests.csv", index=False)
    sig_pairs = pairwise[pairwise["significant_005"]]
    print(f"=== Pairwise Tests ({len(sig_pairs)}/{len(pairwise)} significant at p<0.05) ===")
    if not sig_pairs.empty:
        print(sig_pairs[["agent_1", "agent_2", "mean_1", "mean_2", "p_value", "effect_size_r"]].to_string(index=False))
    print()

    # 3. Time series
    ts_payoff = time_series_payoff(df)
    ts_payoff.to_csv(output_dir / "time_series_payoff.csv", index=False)
    ts_coop = time_series_cooperation(df)
    ts_coop.to_csv(output_dir / "time_series_cooperation.csv", index=False)
    print(f"=== Time Series Data ===")
    print(f"Saved payoff and cooperation time series ({len(ts_payoff)} rows)")
    print()

    # 4. Adaptation analysis (for betrayal scenarios with scheduled switches)
    has_scheduled = (
        "switch_kind" in df.columns
        and (df["switch_kind"] == "scheduled").any()
    )
    if has_scheduled:
        adapt = adaptation_analysis(df, switch_round=args.switch_round)
        adapt.to_csv(output_dir / "adaptation_analysis.csv", index=False)
        print("=== Adaptation Analysis (pre/post switch) ===")
        print(adapt.to_string(index=False))
        print()

    # 5. Text report
    report_lines = [
        "# Benchmark Analysis Report",
        f"",
        f"Data: {args.results}",
        f"Total records: {len(df)}",
        f"Agents: {sorted(df['agent_name'].unique())}",
        f"Seeds: {df['seed'].nunique()}",
        f"Rounds per episode: {df.groupby('episode_id')['step'].count().max()}",
        "",
        "## Agent Rankings (by mean episode reward)",
        "",
        summary.to_string(index=False),
        "",
        f"## Pairwise Comparisons ({len(sig_pairs)}/{len(pairwise)} significant)",
        "",
        pairwise.to_string(index=False),
    ]
    if has_scheduled:
        report_lines += [
            "",
            "## Adaptation Analysis",
            "",
            adapt.to_string(index=False),
        ]
    report_text = "\n".join(report_lines)
    (output_dir / "analysis_report.txt").write_text(report_text)
    print(f"Full report saved to: {output_dir / 'analysis_report.txt'}")


if __name__ == "__main__":
    main()
