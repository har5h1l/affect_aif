from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.affect import DiscreteBetaState
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents
from tasks.trust.runtime import PartnerBank, gamma_for_partner, update_beta_after_observation


def test_gamma_for_partner_uses_hesp_inverse_beta() -> None:
    beta = DiscreteBetaState(num_entities=1, initial_beta=2.0)

    gamma = gamma_for_partner(base_gamma=4.0, beta=beta, partner_idx=0, affect_mode="normal")

    assert np.isclose(gamma, 2.0)


def test_decouple_mode_does_not_modulate_gamma() -> None:
    beta = DiscreteBetaState(num_entities=1, initial_beta=2.0)

    gamma = gamma_for_partner(base_gamma=4.0, beta=beta, partner_idx=0, affect_mode="decouple")

    assert np.isclose(gamma, 4.0)


def test_global_mode_uses_shared_beta_for_all_partners() -> None:
    beta = DiscreteBetaState(num_entities=1, initial_beta=2.0)

    gamma = gamma_for_partner(base_gamma=4.0, beta=beta, partner_idx=3, affect_mode="global")

    assert np.isclose(gamma, 2.0)


def test_beta_update_uses_prediction_probability() -> None:
    template = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary", num_partners=1), planning_horizon=1)
    bank = PartnerBank(
        agents=create_partner_agents(template, num_partners=1, gamma=1.0),
        beta=DiscreteBetaState(num_entities=1, initial_beta=1.0),
    )

    before = bank.beta.expected_beta()[0]
    update_beta_after_observation(
        bank=bank,
        partner_idx=0,
        predicted_partner_action_probs=np.array([0.1, 0.9]),
        observed_partner_action=0,
        affect_mode="normal",
    )
    after = bank.beta.expected_beta()[0]

    assert after > before


def test_global_beta_update_routes_to_shared_entity() -> None:
    template = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary", num_partners=3), planning_horizon=1)
    bank = PartnerBank(
        agents=create_partner_agents(template, num_partners=3, gamma=1.0),
        beta=DiscreteBetaState(num_entities=1, initial_beta=1.0),
    )

    before = bank.beta.expected_beta()[0]
    update_beta_after_observation(
        bank=bank,
        partner_idx=2,
        predicted_partner_action_probs=np.array([0.1, 0.9]),
        observed_partner_action=0,
        affect_mode="global",
    )
    after = bank.beta.expected_beta()[0]

    assert after > before
    assert np.isclose(bank.latest_surprise[2], 0.9)
