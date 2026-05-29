import json

import pandas as pd

from analysis.hypotheses import run_all_hypothesis_tests


def test_run_all_hypothesis_tests_returns_current_behavior_card_labels():
    df = pd.DataFrame(
        [
            {"variant_id": "no_affect__planning_horizon_1", "seed": 1, "round": 0, "payoff": 1.0},
            {"variant_id": "affect__planning_horizon_1", "seed": 1, "round": 0, "payoff": 2.0},
        ]
    )

    result = run_all_hypothesis_tests(df)

    assert set(result) == {"h0", "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"}


def test_hypothesis_payloads_are_json_safe_and_current_shape():
    df = pd.DataFrame(
        [
            {
                "variant_id": "no_affect__planning_horizon_1",
                "seed": 1,
                "round": 0,
                "payoff": 1.0,
                "inferred_type_correct": 1.0,
                "inferred_stance_correct": 1.0,
                "inferred_joint_correct": 1.0,
                "q_pi_entropy": 0.5,
                "mean_abs_step_efe": 1.0,
                "planning_cost": 1.0,
                "planning_cost_ratio": 1.0,
            },
            {
                "variant_id": "affect__planning_horizon_1",
                "seed": 1,
                "round": 0,
                "payoff": 2.0,
                "inferred_type_correct": 1.0,
                "inferred_stance_correct": 1.0,
                "inferred_joint_correct": 1.0,
                "q_pi_entropy": 0.6,
                "mean_abs_step_efe": 1.1,
                "planning_cost": 1.0,
                "planning_cost_ratio": 1.0,
            },
        ]
    )

    result = run_all_hypothesis_tests(df)

    for payload in result.values():
        assert set(payload) >= {"available", "hypothesis", "summary", "evidence"}
    json.dumps(result, allow_nan=False)
