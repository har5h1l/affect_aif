import pandas as pd

from scripts.experiment.run_exp_b_prior_factorial import EXP_B_RADAR_METRICS
from scripts.experiment.run_exp_b_prior_factorial import metrics as exp_b_metrics
from scripts.experiment.run_exp_c_forgiveness import _payoff_recovery
from scripts.experiment.run_exp_d_mixed_volatility import build_specs, metrics


def test_exp_d_alpha_conditions_are_distinct_and_ordered():
    (spec,) = build_specs(rounds=10, seeds=1, seed=123)

    alphas = {variant.id: variant.alpha_charge for variant in spec.variants if variant.affect == "precision"}

    assert alphas["low_alpha"] < alphas["default_reference"] < alphas["high_alpha"]


def test_exp_c_payoff_recovery_uses_late_pre_betrayal_baseline():
    rows = []
    for round_idx in range(1, 201):
        payoff = 1.0
        if 50 <= round_idx <= 80:
            payoff = 4.0
        if 151 <= round_idx <= 200:
            payoff = 8.0
        rows.append({"round": round_idx, "payoff": payoff})

    assert _payoff_recovery(pd.DataFrame(rows)) == 2.0


def test_exp_d_false_positive_rate_tracks_stable_partner_drop_not_non_p0_selection():
    rows = []
    for round_idx in range(1, 101):
        rows.append(
            {
                "experiment_id": "mixed_volatility",
                "variant_id": "default_reference",
                "seed": 1,
                "round": round_idx,
                "partner_idx": 0 if round_idx <= 50 else 1,
                "local_betas": "[0.5, 0.8, 1.2, 1.5]",
                "payoff": 1.0,
                "true_partner_type": "cooperator",
                "agent_action": 1,
                "q_pi_entropy": 0.5,
            }
        )

    summary = metrics(pd.DataFrame(rows))

    assert float(summary.loc[0, "concentration_toward_p0"]) == 0.5
    assert float(summary.loc[0, "false_positive_rate"]) == 1.0


def test_exp_b_trust_asymmetry_reports_component_latencies_and_direction():
    rows = [
        {
            "experiment_id": "partner_choice",
            "variant_id": "naive_high_alpha",
            "seed": 1,
            "round": 1,
            "partner_idx": 0,
            "agent_action": 1,
            "partner_action": 0,
            "payoff": 1.0,
            "true_partner_type": "cooperator",
            "q_pi_entropy": 0.5,
            "local_betas": "[0.5, 0.8, 1.2, 1.5]",
        },
        {
            "experiment_id": "partner_choice",
            "variant_id": "naive_high_alpha",
            "seed": 1,
            "round": 2,
            "partner_idx": 0,
            "agent_action": 5,
            "partner_action": 0,
            "payoff": 1.0,
            "true_partner_type": "cooperator",
            "q_pi_entropy": 0.5,
            "local_betas": "[0.5, 0.8, 1.2, 1.5]",
        },
        {
            "experiment_id": "partner_choice",
            "variant_id": "naive_high_alpha",
            "seed": 1,
            "round": 4,
            "partner_idx": 1,
            "agent_action": 5,
            "partner_action": 1,
            "payoff": 1.0,
            "true_partner_type": "exploiter",
            "q_pi_entropy": 0.5,
            "local_betas": "[0.5, 0.8, 1.2, 1.5]",
        },
        {
            "experiment_id": "partner_choice",
            "variant_id": "naive_high_alpha",
            "seed": 1,
            "round": 10,
            "partner_idx": 1,
            "agent_action": 1,
            "partner_action": 1,
            "payoff": 1.0,
            "true_partner_type": "exploiter",
            "q_pi_entropy": 0.5,
            "local_betas": "[0.5, 0.8, 1.2, 1.5]",
        },
    ]

    summary = exp_b_metrics(pd.DataFrame(rows))

    assert float(summary.loc[0, "trust_approach_latency"]) == 2.0
    assert float(summary.loc[0, "trust_withdrawal_latency"]) == 6.0
    assert float(summary.loc[0, "trust_asymmetry"]) == 3.0


def test_exp_b_radar_metrics_match_manuscript_plan():
    assert EXP_B_RADAR_METRICS == (
        "early_exploitation_rate",
        "betrayal_recovery_time",
        "selection_gini",
        "trust_asymmetry",
        "mean_payoff",
    )
