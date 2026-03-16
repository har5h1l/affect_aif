import numpy as np

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.agent.lesioned_agent import LesionedAgent
from affect_aif.agent.reward_avg_agent import RewardAvgAgent
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner
from affect_aif.generative_model.model import TrustGameModel


def make_agent(agent_cls, **kwargs):
    cfg = ExperimentConfig(num_rounds=2, calibration_episodes=1, num_replications=1, random_seed=0)
    model = TrustGameModel(cfg)
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


def test_affective_terminal_value_deviates_from_initial():
    agent = make_agent(AffectiveAgent, num_partners=4, mu=1.0, initial_beta=0.5)
    agent.pending_prediction_partner = 0
    agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert agent.get_betas()[0] > 0.55


def test_affective_state_moves_materially_on_large_prediction_error():
    agent = make_agent(AffectiveAgent, num_partners=4, mu=1.0, initial_beta=0.5)
    agent.pending_prediction_partner = 0
    agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
    agent.observe_outcome(partner_idx=0, observation=[1, 0], action_taken=0, partner_action=1, payoff=-1.0)
    assert agent.get_betas()[0] < 0.4


def test_lesion_freeze_constant_beta():
    agent = make_agent(LesionedAgent, num_partners=4, mu=1.0, initial_beta=0.5, lesion_mode="freeze")
    agent.pending_prediction_partner = 0
    agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert np.allclose(agent.get_betas(), 0.5)


def test_reward_avg_precision_signal_zeros():
    agent = make_agent(RewardAvgAgent, num_partners=4, mu=1.0)
    assert np.allclose(np.asarray(agent.precision_signal(), dtype=float), 0.0)


def test_affective_outperforms_shallow_baseline():
    cfg = ExperimentConfig(
        num_rounds=50,
        num_replications=3,
        calibration_episodes=1,
        random_seed=0,
        conditions=[2, 4],
        p_switch=0.0,
        initial_partner_types=["cooperator", "reciprocator", "random", "random"],
        scheduled_type_switches=[{"round": 26, "partner_idx": 0, "to_type": "exploiter"}],
    )
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    summary = results.groupby("condition", as_index=False).agg(mean_payoff=("payoff", "mean"))
    c2 = float(summary.loc[summary["condition"] == 2, "mean_payoff"].iloc[0])
    c4 = float(summary.loc[summary["condition"] == 4, "mean_payoff"].iloc[0])
    assert c2 >= c4


def test_betrayal_run_separates_deep_and_affective_actions():
    cfg = ExperimentConfig(
        num_rounds=40,
        num_replications=1,
        calibration_episodes=1,
        random_seed=42,
        conditions=[1, 2],
        assignment_mode="agent_choice",
        p_switch=0.0,
        observation_noise=0.0,
        initial_partner_types=["cooperator", "reciprocator", "random", "random"],
        scheduled_type_switches=[{"round": 16, "partner_idx": 0, "to_type": "exploiter"}],
    )
    results = ExperimentRunner(cfg).run_all()
    primary = results[results["run_mode"] == "primary"].copy()

    c1 = primary[primary["condition"] == 1].sort_values("round")
    c2 = primary[primary["condition"] == 2].sort_values("round")

    assert c1["selected_action"].tolist() != c2["selected_action"].tolist()
    assert float(c1["payoff"].sum()) != float(c2["payoff"].sum())


def test_affect_tracks_precision_not_reward():
    affective = make_agent(AffectiveAgent, num_partners=4, mu=1.0, initial_beta=0.5)
    reward_avg = make_agent(RewardAvgAgent, num_partners=4, mu=1.0)
    sucker_idx = affective.model.payoff_levels.index(-1.0)

    for _ in range(5):
        affective.pending_prediction_partner = 0
        affective.pending_prediction_probs = np.asarray([0.05, 0.95], dtype=float)
        affective.observe_outcome(
            partner_idx=0,
            observation=[1, sucker_idx],
            action_taken=0,
            partner_action=1,
            payoff=-1.0,
        )
        reward_avg.observe_outcome(
            partner_idx=0,
            observation=[1, sucker_idx],
            action_taken=0,
            partner_action=1,
            payoff=-1.0,
        )

    assert affective.get_betas()[0] > 0.5
    assert float(np.asarray(reward_avg.terminal_signal(), dtype=float)[0]) < 0.5


def test_mu_calibration_positive():
    cfg = ExperimentConfig(num_rounds=5, num_replications=1, calibration_episodes=1, random_seed=0, deep_horizon=4, shallow_horizon=2)
    runner = ExperimentRunner(cfg)
    mu = runner.calibrate_mu()
    assert mu > 0.0


def test_full_run_enforces_minimum_calibration_episodes():
    cfg = ExperimentConfig(
        num_rounds=5,
        num_replications=1,
        calibration_episodes=2,
        random_seed=0,
        deep_horizon=4,
        shallow_horizon=2,
        conditions=[2],
    )
    runner = ExperimentRunner(cfg)
    runner.run_all()
    assert runner.calibration_summary is not None
    assert runner.calibration_summary["requested_calibration_episodes"] == 2
    assert runner.calibration_summary["calibration_episodes"] == runner.MIN_FULL_RUN_CALIBRATION_EPISODES


def test_horizon_override_and_deep_affective_conditions():
    cfg = ExperimentConfig(
        num_rounds=2,
        num_replications=1,
        calibration_episodes=1,
        conditions=[6, 7, 8],
        horizon_overrides={6: 3, 7: 4},
    )
    runner = ExperimentRunner(cfg)
    model = TrustGameModel(cfg)

    c6 = runner._create_agent(condition=6, model=model, seed=0)
    c7 = runner._create_agent(condition=7, model=model, seed=0)
    c8 = runner._create_agent(condition=8, model=model, seed=0)

    assert c6.planning_horizon == 3
    assert c7.planning_horizon == 4
    assert c8.planning_horizon == cfg.deep_horizon
    assert c8.current_mu() == 0.0
