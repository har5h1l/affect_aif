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
