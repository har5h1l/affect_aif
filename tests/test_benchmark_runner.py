"""Tests for benchmark runner output schema and calibration behavior."""

import builtins
import importlib
import sys

from benchmarks.core.benchmark_config import BenchmarkConfig
from benchmarks.core.benchmark_runner import BenchmarkRunner


def test_runner_uses_variant_id():
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["trust"],
            "agents": ["affect", "random"],
            "num_replications": 1,
            "num_rounds": 5,
            "random_seed": 1,
            "backend_configs": {"trust": {"scenario": "resource_sharing"}},
        }
    )
    results = BenchmarkRunner(config).run_all()

    assert set(["schema_version", "backend", "scenario", "episode_id", "step", "reward"]).issubset(results.columns)
    assert set(results["backend"].unique()) == {"trust"}
    assert set(results["scenario"].unique()) == {"resource_sharing"}
    assert "condition" not in results.columns
    assert "condition_name" not in results.columns
    affective_rows = results[results["agent_name"] == "affect"]
    random_rows = results[results["agent_name"] == "random"]
    assert set(affective_rows["variant_id"].unique()) == {"affect"}
    assert set(random_rows["variant_id"].unique()) == {"random"}


def test_runner_sets_nan_type_accuracy_for_baselines():
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["trust"],
            "agents": ["random"],
            "num_replications": 1,
            "num_rounds": 10,
            "random_seed": 2,
            "backend_configs": {"trust": {"scenario": "resource_sharing"}},
        }
    )
    results = BenchmarkRunner(config).run_all()
    assert results["inferred_type_correct"].isna().all()


def test_runner_module_imports_when_optional_backend_module_is_missing(monkeypatch):
    module_name = "benchmarks.core.benchmark_runner"
    sys.modules.pop(module_name, None)

    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "benchmarks.cvc.local_backend":
            raise ModuleNotFoundError("No module named 'benchmarks.cvc.local_backend'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    module = importlib.import_module(module_name)

    assert module.BenchmarkRunner is not None
    assert set(module.BACKEND_REGISTRY) == {"trust", "cvc_local"}
