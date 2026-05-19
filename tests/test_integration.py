import json
import subprocess
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd
from experiment_spec_helpers import write_example_toml

from analysis.metrics import post_switch_window_summary
from analysis.visualization import build_run_gifs, load_results
from experiments.trust.batch import BatchExperimentRunner
from experiments.trust.runner import ExperimentRunner
from experiments.trust.spec import ExperimentSpec


def test_full_experiment_runs_and_produces_records(tiny_spec):
    runner = ExperimentRunner.from_spec(tiny_spec)
    results = runner.run_all()
    assert len(results) == 6
    assert {
        "true_partner_type",
        "partner_idx",
        "betas",
        "prediction_errors",
    }.issubset(results.columns)


def test_runner_outputs_variant_identity(tmp_path):
    spec = ExperimentSpec.from_toml(write_example_toml(tmp_path / "betrayal_choice.toml"))
    tiny = spec.with_overrides(rounds=2, replications=1)

    results = ExperimentRunner.from_spec(tiny).run_all()

    assert {"hypothesis_id", "experiment_id", "variant_id", "replication", "seed", "round"} <= set(results.columns)
    assert "condition" not in results.columns


def test_runner_logs_joint_posteriors(tiny_spec):
    runner = ExperimentRunner.from_spec(tiny_spec)
    records = runner.run_replication(run=tiny_spec.expand_runs()[0])

    assert len(records) == 3
    assert "partner_joint_posteriors" in records[-1]


def test_betrayal_metrics_and_analysis_outputs(tmp_path):
    spec = ExperimentSpec.from_toml("configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml")
    spec = spec.with_overrides(rounds=35, replications=1)
    runner = ExperimentRunner.from_spec(spec)
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
    assert (output_dir / "betrayal_reallocation_summary.csv").exists()


def test_verbose_stage_stream_emits_progress_without_changing_results(tiny_spec, capsys):
    quiet_results = ExperimentRunner.from_spec(tiny_spec).run_all()
    quiet_stdout = capsys.readouterr().out
    verbose_results = ExperimentRunner.from_spec(tiny_spec, verbose=True).run_all()
    verbose_stdout = capsys.readouterr().out

    assert quiet_stdout == ""
    assert len(quiet_results) == len(verbose_results)
    assert quiet_results["payoff"].tolist() == verbose_results["payoff"].tolist()
    assert "stage=planning_start" in verbose_stdout
    assert "stage=logging_end" in verbose_stdout


def test_build_run_gifs_writes_one_file_per_primary_run(tmp_path, tiny_spec):
    results = ExperimentRunner.from_spec(tiny_spec).run_all()

    written = build_run_gifs(results, str(tmp_path / "gifs"))

    assert len(written) == 2
    assert all(path.exists() for path in written)


def test_visualization_handles_betrayal_switch_runs(tmp_path):
    spec = ExperimentSpec.from_toml("configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml")
    spec = spec.with_overrides(rounds=35, replications=1)
    results = ExperimentRunner.from_spec(spec).run_all()
    output_csv = tmp_path / "betrayal.csv"
    results.to_csv(output_csv, index=False)
    loaded = load_results(str(output_csv))
    written = build_run_gifs(loaded, str(tmp_path / "gifs"))

    assert any(bool(ids) for ids in loaded["scheduled_stance_switch_partner_ids"].tolist())
    assert len(written) == len(loaded.groupby(["variant_id", "seed"]))


def test_visualization_handles_non_affective_variant(tmp_path, tiny_spec):
    single_variant = tiny_spec.with_overrides(rounds=3, replications=1)
    single_variant = single_variant.__class__(
        hypothesis=single_variant.hypothesis,
        experiment=single_variant.experiment,
        scenario=single_variant.scenario,
        variants=(single_variant.variants[0],),
        runtime=single_variant.runtime,
        analysis=single_variant.analysis,
        path=single_variant.path,
    )
    results = ExperimentRunner.from_spec(single_variant).run_all()

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
            "configs/trust/smoke/smoke.toml",
            "--config",
            "configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml",
            "--output-dir",
            "results",
            "--workers",
            "3",
        ]
    )

    assert args.config == [
        "configs/trust/smoke/smoke.toml",
        "configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml",
    ]
    assert args.output_dir == "results"
    assert args.workers == 3


def test_batch_runner_writes_per_config_subdirs_and_provenance(tmp_path):
    config_a_path = write_example_toml(tmp_path / "config_a.toml", rounds=2, replications=1)
    config_b_path = write_example_toml(tmp_path / "config_b.toml", rounds=2, replications=1)
    config_b_path.write_text(
        config_b_path.read_text().replace('id = "betrayal_choice"', 'id = "secondary"', 1),
        encoding="utf-8",
    )

    batch = BatchExperimentRunner(
        config_paths=[str(config_a_path), str(config_b_path)],
        output_root=str(tmp_path / "results"),
        batch_id="test_batch",
        workers=2,
        verbose=False,
    )
    result = batch.run_all()

    config_dirs = {state.config_name: state.output_dir for state in result.config_states}
    assert set(config_dirs) == {"betrayal_choice", "secondary"}

    results_a = pd.read_csv(config_dirs["betrayal_choice"] / "results.csv")
    results_b = pd.read_csv(config_dirs["secondary"] / "results.csv")

    assert {"config_path", "config_name", "batch_id", "variant_id"}.issubset(results_a.columns)
    assert {"config_path", "config_name", "batch_id", "variant_id"}.issubset(results_b.columns)
    assert set(results_a["config_name"]) == {"betrayal_choice"}
    assert set(results_b["config_name"]) == {"secondary"}
    assert set(results_a["batch_id"]) == {"test_batch"}
    assert set(results_b["batch_id"]) == {"test_batch"}
    assert (config_dirs["betrayal_choice"] / "batch_metadata.json").exists()
    assert (config_dirs["secondary"] / "batch_metadata.json").exists()


def test_batch_schedules_expanded_variant_runs(tmp_path):
    path = write_example_toml(tmp_path / "betrayal_choice.toml", rounds=2)
    runner = BatchExperimentRunner(
        config_paths=[str(path)],
        output_root=str(tmp_path / "results"),
        batch_id="batch",
        workers=1,
    )

    states = runner._load_states()

    assert states[0].spec.experiment.id == "betrayal_choice"
    assert len(states[0].expanded_runs) == 6


def test_batch_runner_resumes_completed_checkpoint_runs(tmp_path, monkeypatch):
    path = write_example_toml(tmp_path / "betrayal_choice.toml", rounds=2, replications=2)
    runner = BatchExperimentRunner(
        config_paths=[str(path)],
        output_root=str(tmp_path / "results"),
        batch_id="resume_batch",
        workers=1,
    )
    first = runner._load_states()[0]
    completed_run = first.expanded_runs[0]
    first.output_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "variant_id": completed_run.variant_id,
                "seed": completed_run.seed,
                "replication": completed_run.replication,
                "round": 0,
                "payoff": 1.0,
                "config_name": first.config_name,
                "batch_id": "resume_batch",
            },
            {
                "variant_id": completed_run.variant_id,
                "seed": completed_run.seed,
                "replication": completed_run.replication,
                "round": 1,
                "payoff": 1.0,
                "config_name": first.config_name,
                "batch_id": "resume_batch",
            },
        ]
    ).to_csv(first.output_dir / "results_partial.csv", index=False)

    submitted: list[tuple[str, int, int]] = []

    class ImmediateFuture:
        def __init__(self, run):
            self.run = run

        def result(self):
            submitted.append((self.run.variant_id, self.run.seed, self.run.replication))
            return {
                "task_kind": "variant",
                "variant_id": self.run.variant_id,
                "replication": self.run.replication,
                "seed": self.run.seed,
                "records": [
                    {
                        "variant_id": self.run.variant_id,
                        "seed": self.run.seed,
                        "replication": self.run.replication,
                        "round": 0,
                        "payoff": 2.0,
                        "config_name": first.config_name,
                        "batch_id": "resume_batch",
                    },
                    {
                        "variant_id": self.run.variant_id,
                        "seed": self.run.seed,
                        "replication": self.run.replication,
                        "round": 1,
                        "payoff": 2.0,
                        "config_name": first.config_name,
                        "batch_id": "resume_batch",
                    },
                ],
            }

    class ImmediateExecutor:
        def __init__(self, max_workers):
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def submit(self, _fn, _spec_payload, run_payload, **_kwargs):
            from experiments.trust.spec import ExpandedRunSpec

            return ImmediateFuture(ExpandedRunSpec.from_payload(run_payload))

    def immediate_wait(futures, return_when):
        del return_when
        return {next(iter(futures))}, set(futures[1:])

    monkeypatch.setattr("experiments.trust.batch.ProcessPoolExecutor", ImmediateExecutor)
    monkeypatch.setattr("experiments.trust.batch.wait", immediate_wait)

    result = runner.run_all()
    state = result.config_states[0]
    final = pd.read_csv(state.output_dir / "results.csv")

    assert (completed_run.variant_id, completed_run.seed, completed_run.replication) not in submitted
    assert len(submitted) == len(first.expanded_runs) - 1
    assert len(final) == len(first.expanded_runs) * 2
    metadata = json.loads((state.output_dir / "batch_metadata.json").read_text())
    assert metadata["resumed_tasks"] == 1


def test_serial_runner_resumes_completed_checkpoint_runs(tmp_path, tiny_spec, monkeypatch):
    spec = tiny_spec.with_overrides(rounds=2, replications=2)
    runs = spec.expand_runs()
    completed_run = runs[0]
    checkpoint = tmp_path / "results_partial.csv"
    pd.DataFrame(
        [
            {
                "variant_id": completed_run.variant_id,
                "seed": completed_run.seed,
                "replication": completed_run.replication,
                "round": 0,
                "payoff": 1.0,
            },
            {
                "variant_id": completed_run.variant_id,
                "seed": completed_run.seed,
                "replication": completed_run.replication,
                "round": 1,
                "payoff": 1.0,
            },
        ]
    ).to_csv(checkpoint, index=False)

    executed: list[tuple[str, int, int]] = []

    def fake_run_replication(*, run, config_path=None, config_name=None, batch_id=None):
        del config_path, config_name, batch_id
        executed.append((run.variant_id, run.seed, run.replication))
        return [
            {
                "variant_id": run.variant_id,
                "seed": run.seed,
                "replication": run.replication,
                "round": 0,
                "payoff": 2.0,
            },
            {
                "variant_id": run.variant_id,
                "seed": run.seed,
                "replication": run.replication,
                "round": 1,
                "payoff": 2.0,
            },
        ]

    runner = ExperimentRunner.from_spec(spec)
    monkeypatch.setattr(runner, "run_replication", fake_run_replication)

    results = runner.run_all(checkpoint_path=str(checkpoint), checkpoint_interval=1)

    assert (completed_run.variant_id, completed_run.seed, completed_run.replication) not in executed
    assert len(results) == len(runs) * 2
