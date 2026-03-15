import numpy as np

from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner


def test_full_experiment_runs_and_derives_mu():
    cfg = ExperimentConfig(num_rounds=3, num_replications=1, calibration_episodes=1, conditions=[1, 2, 3, 4, 5])
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    assert len(results) == 15
    assert runner.calibration_summary is not None
    assert runner.calibration_summary["derived_mu"] >= 0.0
    assert {"true_partner_type", "partner_idx", "betas", "prediction_errors", "reward_avgs"}.issubset(results.columns)


def test_lesion_condition_has_zero_mu():
    cfg = ExperimentConfig(num_rounds=2, num_replications=1, calibration_episodes=1, conditions=[3])
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    assert (results["mu"] == 0.0).all()


def test_parameter_learning_updates_likelihoods_in_episode():
    cfg = ExperimentConfig(
        num_rounds=3,
        num_replications=1,
        calibration_episodes=1,
        conditions=[1],
        use_parameter_learning=True,
        random_seed=0,
    )
    runner = ExperimentRunner(cfg)
    model = runner._create_model()
    agent = runner._create_agent(condition=1, model=model, seed=cfg.random_seed)
    env = TrustGameEnv(cfg, seed=cfg.random_seed)
    initial = np.asarray(agent.partner_action_prob_table, dtype=float).copy()

    records = runner._run_episode(agent=agent, env=env, seed=cfg.random_seed, condition=1)
    updated = np.asarray(agent.partner_action_prob_table, dtype=float)

    assert len(records) == 3
    assert not np.allclose(updated, initial)


def test_parameter_sensitivity_sweeps_mu_lambda_and_charge():
    cfg = ExperimentConfig(
        num_rounds=1,
        num_replications=1,
        calibration_episodes=1,
        conditions=[2],
        run_sensitivity=True,
        random_seed=0,
    )
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    sensitivity_rows = results[results["run_mode"] == "sensitivity"]

    assert len(results) == 13
    assert set(sensitivity_rows["sensitivity_parameter"]) == {"mu", "lambda_smooth", "alpha_charge"}
