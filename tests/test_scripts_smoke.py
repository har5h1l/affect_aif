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
            "experiments/trust/configs/smoke.json",
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
