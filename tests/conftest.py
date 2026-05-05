import os

import pytest

from experiments.trust.config import ExperimentConfig


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: multi-minute statistical simulations (set RUN_SLOW_TESTS=1)")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_SLOW_TESTS", "").strip() in ("1", "true", "yes"):
        return
    skip = pytest.mark.skip(reason="slow test; set RUN_SLOW_TESTS=1 to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)


from experiments.trust.runner import ExperimentRunner
from experiments.trust.factory import create_native_runtime
from tasks.trust.pomdp import build_trust_pomdp_template


def _build_model(config):
    return build_trust_pomdp_template(config, planning_horizon=1, max_policies=64)


@pytest.fixture
def tiny_config():
    return ExperimentConfig(
        payoff_mode="binary",
        num_rounds=3,
        num_replications=1,
        random_seed=0,
    )


@pytest.fixture
def betrayal_config():
    return ExperimentConfig(
        experiment_name="betrayal_stress",
        payoff_mode="binary",
        num_partners=2,
        num_rounds=8,
        num_replications=1,
        random_seed=0,
        assignment_mode="agent_choice",
        p_switch=0.0,
        observation_noise=0.0,
        initial_partner_types=["cooperator", "random"],
        initial_partner_stances=["trusting", "neutral"],
        scheduled_stance_switches=[{"round": 3, "partner_idx": 0, "to_stance": "hostile"}],
        conditions=[5, 6],
        run_sensitivity=False,
    )


@pytest.fixture
def tiny_model(tiny_config):
    return _build_model(tiny_config)


@pytest.fixture
def agent_factory(tiny_config):
    def _make(condition=1, **kwargs):
        config = tiny_config
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return create_native_runtime(config, condition=condition, seed=0)

    return _make


@pytest.fixture
def representative_agents(agent_factory):
    return {
        "base": agent_factory(1),
        "affective": agent_factory(2),
        "lesioned": agent_factory("lesioned"),
    }


@pytest.fixture
def tiny_runner(tiny_config):
    return ExperimentRunner(tiny_config)
