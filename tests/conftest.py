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


from experiments.trust.factory import create_native_runtime_from_variant
from experiments.trust.runner import ExperimentRunner
from experiments.trust.spec import (
    AnalysisSpec,
    ExperimentMeta,
    ExperimentSpec,
    HypothesisSpec,
    ScenarioSpec,
    StanceSwitchSpec,
    VariantSpec,
)
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
    )


def make_spec(
    *,
    payoff: str = "binary",
    assignment: str = "random",
    partners: int = 4,
    rounds: int = 3,
    replications: int = 1,
    seed: int = 0,
    variants: tuple[VariantSpec, ...] | None = None,
    initial_types: tuple[str, ...] | None = None,
    initial_stances: tuple[str, ...] | None = None,
    stance_switches: tuple[StanceSwitchSpec, ...] = (),
) -> ExperimentSpec:
    return ExperimentSpec(
        hypothesis=HypothesisSpec(id="test", name="test"),
        experiment=ExperimentMeta(id="test", rounds=rounds, replications=replications, seed=seed),
        scenario=ScenarioSpec(
            payoff=payoff,
            assignment=assignment,
            partners=partners,
            initial_types=initial_types,
            initial_stances=initial_stances,
            stance_switches=stance_switches,
        ),
        variants=variants
        or (
            VariantSpec(id="no_affect", affect="none", planning_horizon=1),
            VariantSpec(id="affect", affect="precision", planning_horizon=1),
        ),
        analysis=AnalysisSpec(auto=False),
    )


@pytest.fixture
def tiny_spec(tiny_config):
    return make_spec(
        payoff=tiny_config.payoff_mode,
        rounds=tiny_config.num_rounds,
        replications=tiny_config.num_replications,
        seed=tiny_config.random_seed,
    )


@pytest.fixture
def tiny_model(tiny_config):
    return _build_model(tiny_config)


@pytest.fixture
def agent_factory(tiny_config):
    def _make(variant_id="no_affect", **kwargs):
        config = tiny_config
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        affect = "precision" if variant_id in {"affect", "low_gain", "high_gain", "cautious_prior"} else "none"
        if variant_id in {"lesioned", "tracked_only"}:
            affect = "tracked_only"
        variant = VariantSpec(id=str(variant_id), affect=affect, planning_horizon=1)
        return create_native_runtime_from_variant(config, variant=variant, seed=0)

    return _make


@pytest.fixture
def representative_agents(agent_factory):
    return {
        "base": agent_factory("no_affect"),
        "affective": agent_factory("affect"),
        "lesioned": agent_factory("lesioned"),
    }


@pytest.fixture
def tiny_runner(tiny_spec):
    return ExperimentRunner.from_spec(tiny_spec)
