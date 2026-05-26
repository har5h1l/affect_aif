from __future__ import annotations

import pandas as pd

from analysis.interference import cross_partner_interference_summary, global_vs_local_beta_summary
from analysis.metrics import affective_movement_summary


def test_cross_partner_interference_summary_separates_untouched_partners() -> None:
    frame = pd.DataFrame(
        [
            {
                "variant_id": "global_beta",
                "seed": 1,
                "round": 0,
                "selected_partner": 0,
                "payoff": 3.0,
                "q_pi_entropy": 1.0,
                "scheduled_stance_switch_partner_ids": "[]",
                "global_beta": 1.0,
                "betas": [1.0, 1.0],
            },
            {
                "variant_id": "global_beta",
                "seed": 1,
                "round": 2,
                "selected_partner": 3,
                "payoff": 1.0,
                "q_pi_entropy": 0.5,
                "scheduled_stance_switch_partner_ids": "[3]",
                "global_beta": 0.8,
                "betas": [0.8, 0.9],
            },
            {
                "variant_id": "global_beta",
                "seed": 1,
                "round": 3,
                "selected_partner": 0,
                "payoff": 5.0,
                "q_pi_entropy": 0.7,
                "scheduled_stance_switch_partner_ids": "[]",
                "global_beta": 0.7,
                "betas": [0.7, 0.8],
            },
        ]
    )

    summary = cross_partner_interference_summary(frame, post_window=3)
    beta = global_vs_local_beta_summary(frame)

    assert summary.loc[0, "switched_partner"] == 3
    assert summary.loc[0, "switched_post_encounters"] == 1
    assert summary.loc[0, "untouched_post_encounters"] == 1
    assert summary.loc[0, "untouched_post_mean_payoff"] == 5.0
    assert beta.loc[0, "global_beta_range"] == 0.30000000000000004
    assert beta.loc[0, "vector_beta_mean_range"] == 0.25


def test_affective_movement_summary_uses_temporal_beta_range() -> None:
    frame = pd.DataFrame(
        [
            {"variant_id": "global_beta", "seed": 1, "betas": [1.0, 1.0, 1.0]},
            {"variant_id": "global_beta", "seed": 1, "betas": [0.8, 0.8, 0.8]},
            {"variant_id": "global_beta", "seed": 1, "betas": [0.7, 0.7, 0.7]},
        ]
    )

    summary = affective_movement_summary(frame)

    assert summary.loc[0, "beta_range"] == 0.30000000000000004
    assert bool(summary.loc[0, "beta_moved_materially"])
