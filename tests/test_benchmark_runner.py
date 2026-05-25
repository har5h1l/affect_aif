"""Tests for benchmark runner output schema and calibration behavior."""

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


def test_runner_registry_is_trust_only():
    from benchmarks.core import benchmark_runner

    assert set(benchmark_runner.BACKEND_REGISTRY) == {"trust"}
