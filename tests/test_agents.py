import numpy as np

from tasks.trust.runtime import (
    gamma_for_partner,
    select_decision,
    update_beta_after_observation,
)


def test_native_runtime_plan_returns_valid_action(representative_agents):
    runtime = representative_agents["base"]
    decision = select_decision(
        bank=runtime.partner_bank,
        template=runtime.template,
        active_partner=0,
        assignment_mode="random",
        base_gamma=runtime.base_gamma,
        action_selection="deterministic",
        rng=runtime.rng,
    )
    assert decision.raw_action in {0, 1}


def test_affective_runtime_has_beta_per_partner(representative_agents):
    runtime = representative_agents["affective"]
    assert runtime.partner_bank.beta is not None
    assert runtime.partner_bank.beta.expected_beta().shape == (runtime.num_partners,)


def test_lesioned_runtime_decouple_updates_affect(representative_agents):
    runtime = representative_agents["lesioned"]
    update_beta_after_observation(
        bank=runtime.partner_bank,
        partner_idx=0,
        predicted_partner_action_probs=np.asarray([0.95, 0.05], dtype=float),
        observed_partner_action=0,
        affect_mode=runtime.affect_mode,
    )
    assert runtime.partner_bank.latest_surprise is not None
    assert not np.isnan(runtime.partner_bank.latest_surprise[0])


def test_gamma_signal_matches_inverse_betas(representative_agents):
    runtime = representative_agents["affective"]
    beta = runtime.partner_bank.beta
    assert beta is not None
    expected = runtime.base_gamma / beta.expected_beta()[0]
    assert np.isclose(
        gamma_for_partner(base_gamma=runtime.base_gamma, beta=beta, partner_idx=0, affect_mode=runtime.affect_mode),
        expected,
    )
