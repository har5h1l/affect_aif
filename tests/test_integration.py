import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.metrics import post_switch_window_summary
from analysis.visualization import build_run_gifs, load_results
from experiments.trust.batch import BatchExperimentRunner
from experiments.trust.config import ExperimentConfig
from experiments.trust.runner import ExperimentRunner
from tasks.trust.envs import TrustGameEnv


def test_full_experiment_runs_and_produces_records(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2, 3, 4, 5]})
    runner = ExperimentRunner(cfg)
    results = runner.run_all()
    assert len(results) == 15
    assert {
        "true_partner_type",
        "partner_idx",
        "betas",
        "prediction_errors",
    }.issubset(results.columns)


def test_parameter_learning_updates_likelihoods_in_episode(tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1], "use_parameter_learning": True})
    runner = ExperimentRunner(cfg)
    env = TrustGameEnv(cfg, seed=cfg.random_seed)

    records = runner._run_episode(
        runtime=runner._create_runtime(condition=1, seed=cfg.random_seed),
        env=env,
        seed=cfg.random_seed,
        condition=1,
    )

    assert len(records) == 3
    assert "partner_joint_posteriors" in records[-1]


def test_parameter_sensitivity_sweeps_charge_sigma_persistence_and_initial_beta(tiny_config):
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

    assert len(sensitivity_rows) > 0
    assert set(sensitivity_rows["sensitivity_parameter"]) == {
        "alpha_charge",
        "sigma_0_sq",
        "beta_persistence",
        "initial_beta",
    }


def test_sensitivity_config_normalization_uses_new_keys():
    cfg = ExperimentConfig(sensitivity_factors=[0.5, 1.0])
    assert cfg.sensitivity_factors["alpha_charge"] == [0.5, 1.0]
    assert cfg.sensitivity_factors["sigma_0_sq"] == [0.1, 0.25, 0.4, 0.6]
    assert cfg.sensitivity_factors["beta_persistence"] == [0.5, 0.7, 0.8, 0.9, 0.95]
    assert cfg.sensitivity_factors["initial_beta"] == [0.5, 0.67, 1.0, 1.5, 2.0]


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
        str(Path("scripts/analysis/analyze.py")),
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


def test_verbose_stage_stream_emits_progress_without_changing_results(tiny_config, capsys):
    quiet_cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1], "verbose": False})
    verbose_cfg = ExperimentConfig(
        **{
            **tiny_config.__dict__,
            "conditions": [1],
            "verbose": True,
            "verbosity_mode": "stage_stream",
        }
    )

    quiet_results = ExperimentRunner(quiet_cfg).run_all()
    quiet_stdout = capsys.readouterr().out
    verbose_results = ExperimentRunner(verbose_cfg).run_all()
    verbose_stdout = capsys.readouterr().out

    assert quiet_stdout == ""
    assert len(quiet_results) == len(verbose_results)
    assert quiet_results["payoff"].tolist() == verbose_results["payoff"].tolist()
    assert "stage=planning_start" in verbose_stdout
    assert "stage=logging_end" in verbose_stdout


def test_build_run_gifs_writes_one_file_per_primary_run(tmp_path, tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2]})
    results = ExperimentRunner(cfg).run_all()

    written = build_run_gifs(results, str(tmp_path / "gifs"))

    assert len(written) == 2
    assert all(path.exists() for path in written)


def test_visualization_handles_betrayal_switch_runs(tmp_path, betrayal_config):
    results = ExperimentRunner(betrayal_config).run_all()
    output_csv = tmp_path / "betrayal.csv"
    results.to_csv(output_csv, index=False)
    loaded = load_results(str(output_csv))
    written = build_run_gifs(loaded, str(tmp_path / "gifs"))

    assert any(bool(ids) for ids in loaded["scheduled_stance_switch_partner_ids"].tolist())
    assert len(written) == len(loaded[loaded["run_mode"] == "primary"].groupby(["condition", "seed"]))


def test_visualization_handles_non_affective_conditions(tmp_path, tiny_config):
    cfg = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1]})
    results = ExperimentRunner(cfg).run_all()

    written = build_run_gifs(results, str(tmp_path / "base_gifs"))

    assert len(written) == 1
    assert written[0].exists()


def test_run_experiment_parser_accepts_repeated_configs_and_workers():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "experiment" / "run.py"
    spec = spec_from_file_location("run_experiment_module", script_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    parser = module.build_parser()
    args = parser.parse_args(
        [
            "--config",
            "configs/default.json",
            "--config",
            "configs/betrayal_stress.json",
            "--output-dir",
            "results",
            "--workers",
            "3",
        ]
    )

    assert args.config == ["configs/default.json", "configs/betrayal_stress.json"]
    assert args.output_dir == "results"
    assert args.workers == 3


def test_batch_runner_writes_per_config_subdirs_and_provenance(tmp_path, tiny_config):
    cfg_a = ExperimentConfig(**{**tiny_config.__dict__, "conditions": [1, 2], "run_sensitivity": False})
    cfg_b = ExperimentConfig(
        **{**tiny_config.__dict__, "conditions": [1], "experiment_name": "secondary", "run_sensitivity": False}
    )
    config_a_path = tmp_path / "config_a.json"
    config_b_path = tmp_path / "config_b.json"
    cfg_a.to_json(str(config_a_path))
    cfg_b.to_json(str(config_b_path))

    batch = BatchExperimentRunner(
        config_paths=[str(config_a_path), str(config_b_path)],
        output_root=str(tmp_path / "results"),
        batch_id="test_batch",
        workers=2,
        verbose=False,
    )
    result = batch.run_all()

    config_dirs = {state.config_name: state.output_dir for state in result.config_states}
    assert set(config_dirs) == {"config_a", "config_b"}

    results_a = pd.read_csv(config_dirs["config_a"] / "results.csv")
    results_b = pd.read_csv(config_dirs["config_b"] / "results.csv")

    assert {"config_path", "config_name", "batch_id", "run_mode"}.issubset(results_a.columns)
    assert {"config_path", "config_name", "batch_id", "run_mode"}.issubset(results_b.columns)
    assert set(results_a["config_name"]) == {"config_a"}
    assert set(results_b["config_name"]) == {"config_b"}
    assert set(results_a["batch_id"]) == {"test_batch"}
    assert set(results_b["batch_id"]) == {"test_batch"}
    assert (config_dirs["config_a"] / "batch_metadata.json").exists()
    assert (config_dirs["config_b"] / "batch_metadata.json").exists()
