import subprocess
import sys
from pathlib import Path

import numpy as np

from affect_aif.analysis.metrics import post_switch_window_summary
from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner


def test_full_experiment_runs_and_derives_mu(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2, 3, 4, 5]})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    assert len(results) == 15
    assert runner.calibration_summary is not None
    assert runner.calibration_summary["derived_mu"] >= 0.0
    assert {
        "true_partner_type",
        "partner_idx",
        "betas",
        "prediction_errors",
        "reward_avgs",
        "terminal_signal",
    }.issubset(results.columns)


def test_lesion_condition_has_zero_mu(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "num_rounds": 2, "conditions": [3]})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    assert (results["mu"] == 0.0).all()


def test_parameter_learning_updates_likelihoods_in_episode(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1], "use_parameter_learning": True})
    runner = ExperimentRunner(cfg)
    model = runner._create_model()
    agent = runner._create_agent(condition=1, model=model, seed=cfg.random_seed)
    env = TrustGameEnv(cfg, seed=cfg.random_seed)
    initial = np.asarray(agent.partner_action_prob_table, dtype=float).copy()

    records = runner._run_episode(agent=agent, env=env, seed=cfg.random_seed, condition=1)
    updated = np.asarray(agent.partner_action_prob_table, dtype=float)

    assert len(records) == 3
    assert not np.allclose(updated, initial)


def test_parameter_sensitivity_sweeps_mu_lambda_charge_and_sigma(tiny_config):
    cfg = ExperimentConfig(
        **{
            **tiny_config.__dict__,
            "num_rounds": 1,
            "conditions": [2],
            "run_sensitivity": True,
        }
    )
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    sensitivity_rows = results[results["run_mode"] == "sensitivity"]

    assert len(results) == 16
    assert set(sensitivity_rows["sensitivity_parameter"]) == {"mu", "lambda_smooth", "alpha_charge", "sigma_0_sq"}


def test_sensitivity_config_normalization_includes_sigma():
    cfg = ExperimentConfig(sensitivity_factors=[0.5, 1.0])
    assert cfg.sensitivity_factors["mu"] == [0.5, 1.0]
    assert cfg.sensitivity_factors["sigma_0_sq"] == [0.1, 0.25, 0.4]


def test_betrayal_metrics_and_analysis_outputs(tmp_path, betrayal_config):
    runner = ExperimentRunner(betrayal_config)
    results = runner.run_all()
    results_path = tmp_path / "betrayal.csv"
    output_dir = tmp_path / "analysis"
    results.to_csv(results_path, index=False)

    windows = post_switch_window_summary(results, window=5)
    assert not windows.empty
    assert set(windows["window_label"]) == {"1-5"}

    command = [
        sys.executable,
        str(Path("scripts/run_analysis.py")),
        "--results",
        str(results_path),
        "--output-dir",
        str(output_dir),
    ]
    subprocess.run(command, cwd=Path(__file__).resolve().parents[1], check=True)

    assert (output_dir / "affective_movement_summary.csv").exists()
    assert (output_dir / "betrayal_post_switch_window_1_5.csv").exists()
    assert (output_dir / "betrayal_post_switch_window_1_10.csv").exists()
    assert (output_dir / "betrayal_detection_latency.csv").exists()
