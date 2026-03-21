import jax.numpy as jnp
import numpy as np


def test_base_agent_plan_returns_valid_action(representative_agents):
    agent = representative_agents["base"]
    action = agent.plan_and_act(active_partner=0)
    assert action in {0, 1}


def test_affective_agent_has_beta_per_partner(representative_agents):
    agent = representative_agents["affective"]
    assert agent.get_betas().shape == (agent.num_partners,)


def test_lesioned_agent_decouple_uses_zero_mu_but_updates_affect(representative_agents):
    agent = representative_agents["lesioned"]
    assert np.isclose(agent.current_mu(), 0.0)
    agent.plan_and_act(active_partner=0)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert not np.isnan(agent.get_prediction_errors()[0])


def test_reward_avg_agent_updates_reward_signal(representative_agents):
    agent = representative_agents["reward_avg"]
    agent.plan_and_act(active_partner=0)
    agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    assert agent.get_reward_avgs()[0] > 0.0


def test_reward_avg_terminal_signal_matches_beta_scale(representative_agents):
    agent = representative_agents["reward_avg"]
    assert np.allclose(np.asarray(agent.terminal_signal(), dtype=float), 0.5)
    agent.reward_avgs = jnp.asarray(
        [agent.max_abs_payoff, -agent.max_abs_payoff, 0.0, 10.0 * agent.max_abs_payoff],
        dtype=jnp.float32,
    )
    signal = np.asarray(agent.terminal_signal(), dtype=float)
    assert np.all((signal >= 0.0) & (signal <= 1.0))
    assert signal[0] > 0.5 > signal[1]


def test_reward_avg_agent_precision_signal_is_zero(representative_agents):
    agent = representative_agents["reward_avg"]
    assert np.allclose(np.asarray(agent.precision_signal(), dtype=float), 0.0)


def test_terminal_signal_is_reported_in_metrics(representative_agents):
    agent = representative_agents["affective"]
    metrics = agent.get_metrics()
    assert "terminal_signal" in metrics
    assert np.allclose(metrics["terminal_signal"], agent.get_betas())
