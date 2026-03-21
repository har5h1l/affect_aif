"""Tests for benchmark runner output schema and calibration behavior."""

import numpy as np

from affect_aif.benchmark.benchmark_config import BenchmarkConfig
from affect_aif.benchmark.benchmark_runner import BenchmarkRunner


def test_runner_uses_numeric_condition_and_condition_name():
    config = BenchmarkConfig(
        scenario="resource_sharing",
        agents=["affective_shallow", "random"],
        num_replications=1,
        num_rounds=5,
        run_trust_game=True,
        run_gridworld=False,
        random_seed=1,
    )
    results = BenchmarkRunner(config).run_all()

    assert np.issubdtype(results["condition"].dtype, np.integer)
    affective_rows = results[results["agent_name"] == "affective_shallow"]
    random_rows = results[results["agent_name"] == "random"]
    assert set(affective_rows["condition"].unique()) == {2}
    assert set(affective_rows["condition_name"].unique()) == {"affective_shallow"}
    assert set(random_rows["condition"].unique()) == {-2}
    assert set(random_rows["condition_name"].unique()) == {"random"}


def test_runner_sets_nan_type_accuracy_for_baselines():
    config = BenchmarkConfig(
        scenario="resource_sharing",
        agents=["random"],
        num_replications=1,
        num_rounds=10,
        run_trust_game=True,
        run_gridworld=False,
        random_seed=2,
    )
    results = BenchmarkRunner(config).run_all()
    assert results["inferred_type_correct"].isna().all()

