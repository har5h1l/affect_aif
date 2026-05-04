"""Tests for backend-aware benchmark reporting."""

import pandas as pd

from benchmarks.core.comparison import compute_shared_summary, format_comparison_report


def test_shared_summary_aggregates_episode_reward_per_backend():
    results = pd.DataFrame(
        [
            {
                "backend": "trust",
                "scenario": "resource_sharing",
                "agent_name": "a",
                "seed": 1,
                "episode_id": "t-1",
                "step": 0,
                "reward": 3.0,
                "schema_version": 2,
            },
            {
                "backend": "trust",
                "scenario": "resource_sharing",
                "agent_name": "a",
                "seed": 1,
                "episode_id": "t-1",
                "step": 1,
                "reward": 2.0,
                "schema_version": 2,
            },
            {
                "backend": "cvc_local",
                "scenario": "machina_1",
                "agent_name": "b",
                "seed": 1,
                "episode_id": "c-1",
                "step": 100,
                "reward": 7.0,
                "schema_version": 2,
            },
        ]
    )

    summary = compute_shared_summary(results)

    assert set(summary["backend"]) == {"trust", "cvc_local"}
    assert "mean_episode_reward" in summary.columns


def test_report_mentions_backend_specific_sections():
    results = pd.DataFrame(
        [
            {
                "backend": "trust",
                "scenario": "resource_sharing",
                "agent_name": "a",
                "seed": 1,
                "episode_id": "t-1",
                "step": 0,
                "reward": 3.0,
                "schema_version": 2,
                "payoff": 3.0,
                "agent_action": 0,
                "true_partner_type": "cooperator",
                "partner_action": 0,
                "inferred_type_correct": True,
            },
            {
                "backend": "cvc_local",
                "scenario": "machina_1",
                "agent_name": "b",
                "seed": 1,
                "episode_id": "c-1",
                "step": 100,
                "reward": 7.0,
                "schema_version": 2,
                "team_reward_mean": 7.0,
            },
        ]
    )

    report = format_comparison_report(results)

    assert "Shared Summary" in report
    assert "Trust Backend" in report
    assert "CvC Backend" in report
