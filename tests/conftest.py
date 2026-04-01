import pytest

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.agent.base_agent import BaseAgent
from affect_aif.agent.lesioned_agent import LesionedAgent
from affect_aif.agent.reward_avg_agent import RewardAvgAgent
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner
from affect_aif.generative_model.model import TrustGameModel


@pytest.fixture
def tiny_config():
    return ExperimentConfig(
        num_rounds=3,
        num_replications=1,
        calibration_episodes=1,
        random_seed=0,
    )


@pytest.fixture
def betrayal_config():
    return ExperimentConfig(
        experiment_name="betrayal_stress",
        num_partners=2,
        num_rounds=8,
        num_replications=1,
        calibration_episodes=1,
        random_seed=0,
        assignment_mode="agent_choice",
        p_switch=0.0,
        observation_noise=0.0,
        initial_partner_types=["cooperator", "random"],
        initial_partner_stances=["trusting", "neutral"],
        scheduled_stance_switches=[{"round": 3, "partner_idx": 0, "to_stance": "hostile"}],
        conditions=[5, 6],
        presets=["reward_average"],
        run_sensitivity=False,
    )


@pytest.fixture
def tiny_model(tiny_config):
    return TrustGameModel(tiny_config)


@pytest.fixture
def agent_factory(tiny_config, tiny_model):
    A, B, C, D = tiny_model.get_matrices()

    def _make(agent_cls, **kwargs):
        return agent_cls(
            A=A,
            B=B,
            C=C,
            D=D,
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
        "base": agent_factory(BaseAgent),
        "affective": agent_factory(AffectiveAgent, num_partners=tiny_model.num_partners, mu=1.0),
        "lesioned": agent_factory(
            LesionedAgent,
            num_partners=tiny_model.num_partners,
            mu=2.0,
            lesion_mode="decouple",
        ),
        "reward_avg": agent_factory(RewardAvgAgent, num_partners=tiny_model.num_partners, mu=1.0),
    }


@pytest.fixture
def tiny_runner(tiny_config):
    return ExperimentRunner(tiny_config)
