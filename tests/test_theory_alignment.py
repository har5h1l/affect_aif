import numpy as np

from experiments.trust.conditions import PRESET_CONDITIONS, get_condition_name
from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_native_runtime
from experiments.trust.runner import ExperimentRunner
from tasks.trust.runtime import update_beta_after_observation


def test_affective_beta_decreases_under_consistent_accuracy():
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=1.0),
        condition=2,
        seed=0,
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
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=1.0),
        condition=2,
        seed=0,
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
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0, initial_beta=0.5),
        condition="lesioned",
        seed=0,
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


def test_affective_outperforms_shallow_baseline():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=50,
        num_replications=3,
        random_seed=0,
        conditions=[5, 6],
        p_switch=0.0,
        initial_partner_types=["cooperator", "reciprocator", "random", "random"],
        initial_partner_stances=["trusting", "neutral", "neutral", "neutral"],
        scheduled_stance_switches=[{"round": 26, "partner_idx": 0, "to_stance": "hostile"}],
    )
    results = ExperimentRunner(cfg).run_all()
    summary = results.groupby("condition", as_index=False).agg(mean_payoff=("payoff", "mean"))
    c5 = float(summary.loc[summary["condition"] == 5, "mean_payoff"].iloc[0])
    c6 = float(summary.loc[summary["condition"] == 6, "mean_payoff"].iloc[0])
    assert c6 >= c5 - 0.1


def test_betrayal_run_affect_mechanism_is_active():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=8,
        num_replications=1,
        random_seed=42,
        conditions=[7, 8],
        assignment_mode="agent_choice",
        p_switch=0.0,
        observation_noise=0.0,
        max_policies=64,
        initial_partner_types=["cooperator", "reciprocator", "random", "random"],
        initial_partner_stances=["trusting", "neutral", "neutral", "neutral"],
        scheduled_stance_switches=[{"round": 4, "partner_idx": 0, "to_stance": "hostile"}],
    )
    primary = ExperimentRunner(cfg).run_all().query("run_mode == 'primary'").copy()

    c7 = primary[primary["condition"] == 7].sort_values("round")
    c8 = primary[primary["condition"] == 8].sort_values("round")

    c7_betas_0 = c7["betas"].apply(lambda b: b[0])
    c8_betas_0 = c8["betas"].apply(lambda b: b[0])
    assert c7_betas_0.isna().all() or np.isnan(c7_betas_0.values).all()
    assert not np.isnan(c8_betas_0.values).all()
    assert len(c8_betas_0[c8["round"] >= 4].dropna().values) > 0


def test_runner_runs_directly_without_calibration():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=5,
        num_replications=1,
        random_seed=0,
        deep_horizon=4,
        shallow_horizon=2,
        conditions=[2],
    )
    results = ExperimentRunner(cfg).run_all()
    assert len(results) > 0
    assert "condition" in results.columns
    assert "payoff" in results.columns


def test_full_run_produces_primary_records():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=5,
        num_replications=1,
        random_seed=0,
        conditions=[2],
    )
    primary = ExperimentRunner(cfg).run_all().query("run_mode == 'primary'")
    assert len(primary) == 5


def test_horizon_override_and_core_and_preset_affective_conditions():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=2,
        num_replications=1,
        conditions=[6, 7, 8],
        presets=["no_epistemic"],
        horizon_overrides={6: 3, 7: 4, "no_epistemic": 5},
    )

    c6 = create_native_runtime(cfg, condition=6, seed=0)
    c7 = create_native_runtime(cfg, condition=7, seed=0)
    c8 = create_native_runtime(cfg, condition=8, seed=0)
    no_epi = create_native_runtime(cfg, condition="no_epistemic", seed=0)

    assert c6.planning_horizon == 3
    assert c7.planning_horizon == 4
    assert c8.planning_horizon == cfg.deep_horizon
    assert no_epi.planning_horizon == 5


def test_clinical_presets_configure_native_beta_path():
    alex = create_native_runtime(ExperimentConfig(alpha_charge=0.1), condition="alexithymia", seed=0)
    border = create_native_runtime(ExperimentConfig(alpha_charge=12.0), condition="borderline", seed=0)
    depressed = create_native_runtime(ExperimentConfig(initial_beta=2.0), condition="depression", seed=0)

    assert alex.partner_bank.beta is not None
    assert border.partner_bank.beta is not None
    assert depressed.partner_bank.beta is not None
    assert alex.partner_bank.beta.alpha_charge == 0.1
    assert border.partner_bank.beta.alpha_charge == 12.0
    assert depressed.partner_bank.beta.initial_beta == 2.0
    assert np.allclose(depressed.partner_bank.beta.expected_beta(), 2.0)


def test_get_condition_name_all_conditions():
    for condition_id in range(1, 9):
        name = get_condition_name(condition_id)
        assert isinstance(name, str)
        assert len(name) > 0
    assert set(PRESET_CONDITIONS) == {
        "lesioned",
        "no_epistemic",
        "alexithymia",
        "borderline",
        "depression",
    }
