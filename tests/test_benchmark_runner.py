"""Tests for benchmark runner output schema and calibration behavior."""

import builtins
import importlib
import sys

import numpy as np

from benchmarks.core.benchmark_config import BenchmarkConfig
from benchmarks.core.benchmark_runner import BenchmarkRunner


def test_runner_uses_numeric_condition_and_condition_name():
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["trust"],
            "agents": ["tau4_affect", "random"],
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
    assert np.issubdtype(results["condition"].dtype, np.integer)
    affective_rows = results[results["agent_name"] == "tau4_affect"]
    random_rows = results[results["agent_name"] == "random"]
    assert set(affective_rows["condition"].unique()) == {6}
    assert set(affective_rows["condition_name"].unique()) == {"tau4_affect"}
    assert set(random_rows["condition"].unique()) == {-2}
    assert set(random_rows["condition_name"].unique()) == {"random"}


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
