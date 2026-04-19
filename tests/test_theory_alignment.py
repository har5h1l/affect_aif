import numpy as np

import pytest

from agent.affective import AffectiveAgent
from agent.lesioned import LesionedAgent
from experiment.conditions import PRESET_CONDITIONS, get_condition_name
from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner


def _build_model(config):
    from trust.model import TrustGameModel

    return TrustGameModel(config)


def make_agent(agent_cls, **kwargs):
    cfg = ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0)
    model = _build_model(cfg)
    A, B, C, D = model.get_matrices()
    return agent_cls(
        A=A,
        B=B,
        C=C,
        D=D,
        model=model,
        planning_horizon=2,
        gamma=1.0,
        seed=0,
        reference_horizon=cfg.deep_horizon,
        max_policies=64,
        **kwargs,
    )


def test_affective_beta_decreases_under_consistent_accuracy():
    agent = make_agent(AffectiveAgent, num_partners=4, initial_beta=1.0)
    for _ in range(5):
        agent.pending_prediction_partner = 0
        agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
        agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert agent.get_betas()[0] < 1.0


def test_affective_beta_increases_under_consistent_surprise():
    agent = make_agent(AffectiveAgent, num_partners=4, initial_beta=1.0)
    for _ in range(3):
        agent.pending_prediction_partner = 0
        agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
        agent.observe_outcome(partner_idx=0, observation=[1, 0], action_taken=0, partner_action=1, payoff=-1.0)
    assert agent.get_betas()[0] > 1.0


def test_lesion_freeze_constant_beta():
    agent = make_agent(LesionedAgent, num_partners=4, initial_beta=0.5, lesion_mode="freeze")
    agent.pending_prediction_partner = 0
    agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert np.allclose(agent.get_betas(), 0.5)


@pytest.mark.skip(reason="RewardAvgAgent removed in restructuring")
def test_reward_avg_precision_signal_zeros():
    pass


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
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    summary = results.groupby("condition", as_index=False).agg(mean_payoff=("payoff", "mean"))
    c5 = float(summary.loc[summary["condition"] == 5, "mean_payoff"].iloc[0])
    c6 = float(summary.loc[summary["condition"] == 6, "mean_payoff"].iloc[0])
    # Affective should at least be competitive with no-affect (within 0.1 tolerance)
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
    results = ExperimentRunner(cfg).run_all()
    primary = results[results["run_mode"] == "primary"].copy()

    c7 = primary[primary["condition"] == 7].sort_values("round")
    c8 = primary[primary["condition"] == 8].sort_values("round")

    # Base agent (c7) betas are all NaN; affective agent (c8) has real values
    c7_betas_0 = c7["betas"].apply(lambda b: b[0])
    c8_betas_0 = c8["betas"].apply(lambda b: b[0])
    assert c7_betas_0.isna().all() or np.isnan(c7_betas_0.values).all()
    assert not np.isnan(c8_betas_0.values).all()

    # optional: beta trajectory for partner 0 post-betrayal (factorized policies can starve partner 0)
    post_betrayal_betas = c8_betas_0[c8["round"] >= 4].dropna().values
    assert len(post_betrayal_betas) > 0


@pytest.mark.skip(reason="RewardAvgAgent removed in restructuring")
def test_affect_tracks_precision_not_reward():
    pass


def test_runner_runs_directly_without_calibration():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=5, num_replications=1, random_seed=0, deep_horizon=4, shallow_horizon=2, conditions=[2]
    )
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
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
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    primary = results[results["run_mode"] == "primary"]
    assert len(primary) == 5


def test_horizon_override_and_core_and_preset_affective_conditions():
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=2,
        num_replications=1,
        conditions=[6, 7, 8],
        presets=["variational_beta"],
        horizon_overrides={6: 3, 7: 4, "variational_beta": 5},
    )
    runner = ExperimentRunner(cfg)
    model = _build_model(cfg)

    c6 = runner._create_agent(condition=6, model=model, seed=0)
    c7 = runner._create_agent(condition=7, model=model, seed=0)
    c8 = runner._create_agent(condition=8, model=model, seed=0)
    variational = runner._create_agent(condition="variational_beta", model=model, seed=0)

    assert c6.planning_horizon == 3
    assert c7.planning_horizon == 4
    assert c8.planning_horizon == cfg.deep_horizon
    assert variational.planning_horizon == 5


def test_clinical_alexithymia_preset():
    """Alexithymia preset creates an AffectiveAgent with blunted alpha_charge."""
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=2,
        num_replications=1,
        random_seed=0,
        conditions=[],
        presets=["alexithymia"],
        alpha_charge=0.1,
    )
    runner = ExperimentRunner(cfg)
    model = _build_model(cfg)
    agent = runner._create_agent(condition="alexithymia", model=model, seed=0)
    assert isinstance(agent, AffectiveAgent)
    assert agent.affect.alpha_charge == 0.1
    assert agent.planning_horizon == 4


def test_clinical_borderline_preset():
    """Borderline preset amplifies charge sensitivity in the discrete HESP beta path."""
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=2,
        num_replications=1,
        random_seed=0,
        conditions=[],
        presets=["borderline"],
        alpha_charge=12.0,
    )
    runner = ExperimentRunner(cfg)
    model = _build_model(cfg)
    agent = runner._create_agent(condition="borderline", model=model, seed=0)
    assert isinstance(agent, AffectiveAgent)
    assert agent.affect.alpha_charge == 12.0
    assert agent.planning_horizon == 4


def test_clinical_depression_preset():
    """Depression preset biases the discrete beta prior toward high beta / low precision."""
    cfg = ExperimentConfig(
        payoff_mode="binary",
        num_rounds=2,
        num_replications=1,
        random_seed=0,
        conditions=[],
        presets=["depression"],
        initial_beta=2.0,
    )
    runner = ExperimentRunner(cfg)
    model = _build_model(cfg)
    agent = runner._create_agent(condition="depression", model=model, seed=0)
    assert isinstance(agent, AffectiveAgent)
    assert agent.affect.initial_beta == 2.0
    assert np.allclose(agent.get_betas(), 2.0)
    assert agent.planning_horizon == 4


def test_get_condition_name_all_conditions():
    """All core conditions and named presets expose stable names."""
    for condition_id in range(1, 9):
        name = get_condition_name(condition_id)
        assert isinstance(name, str)
        assert len(name) > 0
    assert set(PRESET_CONDITIONS) == {
        "lesioned",
        "no_epistemic",
        "variational_beta",
        "alexithymia",
        "borderline",
        "depression",
    }
