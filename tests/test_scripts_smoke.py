import json
import subprocess
import sys


def test_experiment_run_help():
    result = subprocess.run(
        [sys.executable, "scripts/experiment/run.py", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "--config" in result.stdout


def test_experiment_run_dry_run_writes_manifest(tmp_path):
    out = tmp_path / "results"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/experiment/run.py",
            "--config",
            "configs/diagnostics/smoke/trust_smoke.toml",
            "--output-dir",
            str(out),
            "--batch-name",
            "dry_run",
            "--dry-run",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    manifest = json.loads((out / "dry_run" / "manifest.json").read_text())
    assert manifest["batch_name"] == "dry_run"
    assert "git_commit" in manifest


def test_demo_configs_dry_run_through_run_py_writes_manifest(tmp_path):
    out = tmp_path / "results"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/experiment/run.py",
            "--config",
            "configs/demo/model_fitness.toml",
            "--config",
            "configs/demo/betrayal_adaptation.toml",
            "--config",
            "configs/demo/alpha_sweep.toml",
            "--output-dir",
            str(out),
            "--batch-name",
            "demo_dry",
            "--workers",
            "1",
            "--dry-run",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "demo_dry" / "manifest.json").read_text())
    assert manifest["batch_name"] == "demo_dry"
    assert [entry["experiment_id"] for entry in manifest["configs"]] == [
        "model_fitness_demo",
        "betrayal_adaptation_demo",
        "alpha_sweep_demo",
    ]


def test_experiment_inspect_accepts_suite_config():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/experiment/inspect.py",
            "--config",
            "configs/paper/alpha_sweep.toml",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["suite"] is True
    assert [spec["experiment"]["id"] for spec in payload["specs"]] == [
        "open_graded",
        "betrayal",
    ]
    assert payload["expanded_runs"] == 320
