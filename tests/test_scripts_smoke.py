import json
import os
import subprocess
import sys
import textwrap


def test_experiment_run_help():
    result = subprocess.run(
        [sys.executable, "scripts/experiment/run.py", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "--config" in result.stdout


def test_experiment_run_import_stays_light():
    code = textwrap.dedent(
        """
        import importlib.util
        import json
        import sys
        from pathlib import Path

        script_path = Path("scripts/experiment/run.py").resolve()
        spec = importlib.util.spec_from_file_location("run_experiment_module", script_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        print(json.dumps({
            "analysis_configured": "analysis.configured" in sys.modules,
            "analysis_visualization": "analysis.visualization" in sys.modules,
            "matplotlib": any(name == "matplotlib" or name.startswith("matplotlib.") for name in sys.modules),
            "jax": any(name == "jax" or name.startswith("jax.") for name in sys.modules),
        }))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    loaded = json.loads(result.stdout)
    assert loaded == {
        "analysis_configured": False,
        "analysis_visualization": False,
        "matplotlib": False,
        "jax": False,
    }


def test_experiment_run_import_sets_writable_matplotlib_cache_without_overriding_user_env(tmp_path):
    code = textwrap.dedent(
        """
        import importlib.util
        import json
        import os
        import sys
        from pathlib import Path

        script_path = Path("scripts/experiment/run.py").resolve()
        spec = importlib.util.spec_from_file_location("run_experiment_module", script_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        print(json.dumps({
            "mplconfigdir": os.environ.get("MPLCONFIGDIR"),
            "exists": Path(os.environ["MPLCONFIGDIR"]).exists(),
        }))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    loaded = json.loads(result.stdout)
    assert loaded["mplconfigdir"].endswith("affect_aif_matplotlib")
    assert loaded["exists"] is True

    user_cache = tmp_path / "user_mpl"
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "MPLCONFIGDIR": str(user_cache)},
    )

    assert result.returncode == 0, result.stderr
    loaded = json.loads(result.stdout)
    assert loaded == {"mplconfigdir": str(user_cache), "exists": False}


def test_experiment_run_import_configures_explicit_jax_cache_before_jax_import(tmp_path):
    cache_dir = tmp_path / "jax_cache"
    code = textwrap.dedent(
        f"""
        import importlib.util
        import json
        import os
        import sys
        from pathlib import Path

        sys.argv = ["scripts/experiment/run.py", "--jax-cache-dir", {str(cache_dir)!r}]
        script_path = Path("scripts/experiment/run.py").resolve()
        spec = importlib.util.spec_from_file_location("run_experiment_module", script_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        print(json.dumps({{
            "jax_imported": any(name == "jax" or name.startswith("jax.") for name in sys.modules),
            "enable_cache": os.environ.get("JAX_ENABLE_COMPILATION_CACHE"),
            "cache_dir": os.environ.get("JAX_COMPILATION_CACHE_DIR"),
            "min_compile_time": os.environ.get("JAX_PERSISTENT_CACHE_MIN_COMPILE_TIME_SECS"),
            "min_entry_size": os.environ.get("JAX_PERSISTENT_CACHE_MIN_ENTRY_SIZE_BYTES"),
            "exists": Path(os.environ["JAX_COMPILATION_CACHE_DIR"]).exists(),
        }}))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    loaded = json.loads(result.stdout)
    assert loaded == {
        "jax_imported": False,
        "enable_cache": "true",
        "cache_dir": str(cache_dir),
        "min_compile_time": "0",
        "min_entry_size": "0",
        "exists": True,
    }


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
            "configs/demo/01_predictability_value.toml",
            "--config",
            "configs/demo/02_deployment_ablation.toml",
            "--config",
            "configs/demo/03_partner_selection.toml",
            "--config",
            "configs/demo/04_betrayal_adaptation.toml",
            "--config",
            "configs/demo/05a_alpha_sweep.toml",
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
        "predictability_value_demo",
        "deployment_ablation_demo",
        "partner_selection_demo",
        "betrayal_adaptation_demo",
        "open_graded",
        "betrayal",
    ]


def test_experiment_inspect_accepts_suite_config():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/experiment/inspect.py",
            "--config",
            "configs/paper/05a_alpha_sweep.toml",
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
