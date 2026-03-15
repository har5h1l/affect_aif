import numpy as np

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.agent.base_agent import BaseAgent
from affect_aif.agent.lesioned_agent import LesionedAgent
from affect_aif.agent.reward_avg_agent import RewardAvgAgent
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.generative_model.model import TrustGameModel


def make_agent(agent_cls, **kwargs):
    cfg = ExperimentConfig(num_rounds=2, calibration_episodes=1, num_replications=1)
    model = TrustGameModel(cfg)
    A, B, C, D = model.get_matrices()
    return agent_cls(
        A=A,
        B=B,
        C=C,
        D=D,
        model=model,
        planning_horizon=2,
        gamma=1.0,
        seed=0,
        reference_horizon=cfg.deep_horizon,
        max_policies=64,
        **kwargs,
    )


def test_base_agent_plan_returns_valid_action():
    agent = make_agent(BaseAgent)
    action = agent.plan_and_act(active_partner=0)
    assert action in {0, 1}


def test_affective_agent_has_beta_per_partner():
    agent = make_agent(AffectiveAgent, num_partners=4, mu=1.0)
    assert agent.get_betas().shape == (4,)


def test_lesioned_agent_decouple_uses_zero_mu_but_updates_affect():
    agent = make_agent(LesionedAgent, num_partners=4, mu=2.0, lesion_mode="decouple")
    assert np.isclose(agent.current_mu(), 0.0)
    agent.plan_and_act(active_partner=0)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert not np.isnan(agent.get_prediction_errors()[0])


def test_reward_avg_agent_updates_reward_signal():
    agent = make_agent(RewardAvgAgent, num_partners=4, mu=1.0)
    agent.plan_and_act(active_partner=0)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert agent.get_reward_avgs()[0] > 0.0
