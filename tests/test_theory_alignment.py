import numpy as np
from runtime_helpers import build_runtime

from experiments.trust.config import ExperimentConfig
from experiments.trust.runner import ExperimentRunner
from experiments.trust.spec import (
    ExperimentMeta,
    ExperimentSpec,
    HypothesisSpec,
    ScenarioSpec,
    StanceSwitchSpec,
    VariantSpec,
)
from tasks.trust.runtime import update_beta_after_observation


def test_affective_beta_decreases_under_consistent_accuracy():
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=1.0),
        variant_id="affect",
        affect="precision",
    )
    beta = runtime.partner_bank.beta
    assert beta is not None
    for _ in range(5):
        update_beta_after_observation(
            bank=runtime.partner_bank,
            partner_idx=0,
            predicted_partner_action_probs=np.asarray([0.95, 0.05], dtype=float),
            observed_partner_action=0,
            affect_mode=runtime.affect_mode,
        )
    assert beta.expected_beta()[0] < 1.0


def test_affective_beta_increases_under_consistent_surprise():
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=1.0),
        variant_id="affect",
        affect="precision",
    )
    beta = runtime.partner_bank.beta
    assert beta is not None
    for _ in range(3):
        update_beta_after_observation(
            bank=runtime.partner_bank,
            partner_idx=0,
            predicted_partner_action_probs=np.asarray([0.95, 0.05], dtype=float),
            observed_partner_action=1,
            affect_mode=runtime.affect_mode,
        )
    assert beta.expected_beta()[0] > 1.0


def test_lesion_freeze_constant_beta():
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=0.5),
        variant_id="lesioned",
        affect="tracked_only",
    )
    update_beta_after_observation(
        bank=runtime.partner_bank,
        partner_idx=0,
        predicted_partner_action_probs=np.asarray([0.95, 0.05], dtype=float),
        observed_partner_action=0,
        affect_mode="fixed",
    )
    assert runtime.partner_bank.beta is not None
    assert np.allclose(runtime.partner_bank.beta.expected_beta(), 0.5)


def test_betrayal_run_affect_mechanism_is_active():
    switch_round = 2
    spec = ExperimentSpec(
        hypothesis=HypothesisSpec(id="h5", name="timescale_volatility"),
        experiment=ExperimentMeta(id="tiny_betrayal", rounds=5, replications=1, seed=42),
        scenario=ScenarioSpec(
            payoff="binary",
            assignment="agent_choice",
            partners=2,
            type_volatility=0.0,
            observation_noise=0.0,
            initial_types=("cooperator", "random"),
            initial_stances=("trusting", "neutral"),
            stance_switches=(StanceSwitchSpec(round=switch_round, partner=0, to="hostile"),),
        ),
        variants=(
            VariantSpec(id="no_affect", affect="none", planning_horizon=1),
            VariantSpec(id="affect", affect="precision", planning_horizon=1),
        ),
    )
    results = ExperimentRunner.from_spec(spec).run_all()

    no_affect = results[results["variant_id"] == "no_affect"].sort_values("round")
    affect = results[results["variant_id"] == "affect"].sort_values("round")

    no_affect_betas_0 = no_affect["betas"].apply(lambda b: b[0])
    affect_betas_0 = affect["betas"].apply(lambda b: b[0])
    assert no_affect_betas_0.isna().all() or np.isnan(no_affect_betas_0.values).all()
    assert not np.isnan(affect_betas_0.values).all()
    assert len(affect_betas_0[affect["round"] >= switch_round].dropna().values) > 0


def test_clinical_variants_configure_native_beta_path():
    alex = build_runtime(ExperimentConfig(alpha_charge=0.1), variant_id="alexithymia", affect="precision")
    border = build_runtime(ExperimentConfig(alpha_charge=12.0), variant_id="borderline", affect="precision")
    depressed = build_runtime(ExperimentConfig(initial_beta=2.0), variant_id="depression", affect="precision")

    assert alex.partner_bank.beta is not None
    assert border.partner_bank.beta is not None
    assert depressed.partner_bank.beta is not None
    assert alex.partner_bank.beta.alpha_charge == 0.1
    assert border.partner_bank.beta.alpha_charge == 12.0
    assert depressed.partner_bank.beta.initial_beta == 2.0
    assert np.allclose(depressed.partner_bank.beta.expected_beta(), 2.0)
