"""Tests for benchmark configuration and agent specs."""

from pathlib import Path

from benchmarks.core.benchmark_config import BenchmarkConfig
from experiments.trust.spec import ExperimentSpec


def test_trust_registry_agents_default_to_first_backend():
    config = BenchmarkConfig.from_dict(
        {
            "backends": ["trust"],
            "agents": ["affect", "random"],
        }
    )

    assert config.backends == ["trust"]
    assert [agent.backend for agent in config.agents] == ["trust", "trust"]
    assert [agent.implementation for agent in config.agents] == ["affect", "random"]


def test_checked_in_benchmark_configs_load_as_unified_specs():
    paths = sorted(Path("configs/benchmark").glob("**/*.toml"))

    assert paths
    for path in paths:
        spec = ExperimentSpec.from_toml(path)
        assert spec.experiment.family == "benchmark"
        assert spec.benchmark is not None


def test_no_root_benchmark_json_configs_remain():
    assert not sorted(Path("configs").glob("benchmark*.json"))


def test_benchmark_config_builds_from_experiment_spec():
    spec = ExperimentSpec.from_toml("configs/benchmark/e1_arena/default.toml")

    config = BenchmarkConfig.from_experiment_spec(spec)

    assert config.backends == ["trust"]
    assert [agent.name for agent in config.agents]
    assert config.num_rounds == spec.experiment.rounds
    assert config.num_replications == spec.experiment.replications
    assert config.random_seed == spec.experiment.seed
    assert config.backend_configs["trust"]["scenario"] == "resource_sharing"


def test_benchmark_config_keeps_json_compatibility_surface(tmp_path):
    config = BenchmarkConfig.from_dict({"backends": ["trust"], "agents": ["random"]})
    path = tmp_path / "benchmark.json"

    config.to_json(path)
    loaded = BenchmarkConfig.from_json(path)

    assert loaded.backends == ["trust"]
    assert loaded.agents[0].name == "random"
