import numpy as np

from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_native_runtime
from tasks.trust.runtime import gamma_for_partner, update_beta_after_observation


def test_no_affect_runtime_has_no_beta_precision_state():
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0),
        condition=1,
        seed=0,
    )

    assert runtime.partner_bank.beta is None
    assert runtime.affect_mode == "none"


def test_hesp_beta_increases_on_surprise_and_decreases_on_accuracy():
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=1.0),
        condition=2,
        seed=0,
    )
    beta = runtime.partner_bank.beta
    assert beta is not None
    before = beta.expected_beta()[0]

    for _ in range(5):
        update_beta_after_observation(
            bank=runtime.partner_bank,
            partner_idx=0,
            predicted_partner_action_probs=np.asarray([0.95, 0.05], dtype=float),
            observed_partner_action=0,
            affect_mode=runtime.affect_mode,
        )
    after_accuracy = beta.expected_beta()[0]

    for _ in range(3):
        update_beta_after_observation(
            bank=runtime.partner_bank,
            partner_idx=0,
            predicted_partner_action_probs=np.asarray([0.95, 0.05], dtype=float),
            observed_partner_action=1,
            affect_mode=runtime.affect_mode,
        )
    after_surprise = beta.expected_beta()[0]

    assert after_accuracy < before
    assert after_surprise > after_accuracy
    assert np.isclose(
        gamma_for_partner(base_gamma=1.0, beta=beta, partner_idx=0, affect_mode=runtime.affect_mode),
        1.0 / after_surprise,
    )


def test_lesioned_decouple_updates_beta_but_not_gamma():
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=1.0),
        condition="lesioned",
        seed=0,
    )
    beta = runtime.partner_bank.beta
    assert beta is not None
    before = beta.expected_beta()[0]

    update_beta_after_observation(
        bank=runtime.partner_bank,
        partner_idx=0,
        predicted_partner_action_probs=np.asarray([0.95, 0.05], dtype=float),
        observed_partner_action=1,
        affect_mode=runtime.affect_mode,
    )

    assert not np.isclose(beta.expected_beta()[0], before)
    assert gamma_for_partner(base_gamma=1.0, beta=beta, partner_idx=0, affect_mode=runtime.affect_mode) == 1.0
