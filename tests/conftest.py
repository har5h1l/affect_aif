import os

import pytest

from experiment.config import ExperimentConfig


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: multi-minute statistical simulations (set RUN_SLOW_TESTS=1)")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("RUN_SLOW_TESTS", "").strip() in ("1", "true", "yes"):
        return
    skip = pytest.mark.skip(reason="slow test; set RUN_SLOW_TESTS=1 to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)


from experiment.runner import ExperimentRunner
from trust import AffectiveAgent, LesionedAgent, TrustGameAgent


def _build_model(config):
    from trust.model import TrustGameModel

    return TrustGameModel(config)


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
def agent_factory(tiny_config, tiny_model):
    def _make(agent_cls, **kwargs):
        return agent_cls(
            model=tiny_model,
            planning_horizon=2,
            gamma=1.0,
            seed=0,
            reference_horizon=tiny_config.deep_horizon,
            max_policies=64,
            **kwargs,
        )

    return _make


@pytest.fixture
def representative_agents(agent_factory, tiny_model):
    return {
        "base": agent_factory(TrustGameAgent),
        "affective": agent_factory(AffectiveAgent),
        "lesioned": agent_factory(LesionedAgent, lesion_mode="decouple"),
    }


@pytest.fixture
def tiny_runner(tiny_config):
    return ExperimentRunner(tiny_config)
