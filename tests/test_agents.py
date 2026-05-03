import numpy as np
import pytest


def test_base_agent_plan_returns_valid_action(representative_agents):
    agent = representative_agents["base"]
    action = agent.plan_and_act(active_partner=0)
    assert action in {0, 1}


def test_affective_agent_has_beta_per_partner(representative_agents):
    agent = representative_agents["affective"]
    assert agent.get_betas().shape == (agent.num_partners,)


def test_lesioned_agent_decouple_updates_affect(representative_agents):
    agent = representative_agents["lesioned"]
    agent.plan_and_act(active_partner=0)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert not np.isnan(agent.get_prediction_errors()[0])


@pytest.mark.skip(reason="RewardAvgAgent removed in restructuring")
def test_reward_avg_agent_updates_reward_signal(representative_agents):
    pass


@pytest.mark.skip(reason="RewardAvgAgent removed in restructuring")
def test_reward_avg_terminal_signal_matches_beta_scale(representative_agents):
    pass


@pytest.mark.skip(reason="RewardAvgAgent removed in restructuring")
def test_reward_avg_agent_precision_signal_stays_at_baseline(representative_agents):
    pass


def test_precision_signal_matches_betas(representative_agents):
    agent = representative_agents["affective"]
    assert np.allclose(np.asarray(agent.precision_signal(), dtype=float), agent.get_betas())
