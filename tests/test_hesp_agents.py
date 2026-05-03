import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust import AffectiveAgent, LesionedAgent, TrustGameAgent


def _build_model(config):
    from tasks.trust.models import TrustGameModel

    return TrustGameModel(config)


def _make_agent(agent_cls, **kwargs):
    cfg = ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0)
    model = _build_model(cfg)
    return agent_cls(
        model=model,
        planning_horizon=2,
        gamma=1.0,
        seed=0,
        reference_horizon=cfg.deep_horizon,
        max_policies=64,
        **kwargs,
    )


def test_base_agent_precision_signal_defaults_to_unity():
    agent = _make_agent(TrustGameAgent)
    np.testing.assert_allclose(np.asarray(agent.precision_signal(), dtype=float), np.ones(agent.num_partners))


def test_hesp_beta_increases_on_surprise_and_decreases_on_accuracy():
    agent = _make_agent(AffectiveAgent, initial_beta=1.0)
    before = agent.get_betas()[0]

    for _ in range(5):
        agent.pending_prediction_partner = 0
        agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
        agent.observe_outcome(partner_idx=0, observation=[0, 2], action_taken=0, partner_action=0, payoff=3.0)
    after_accuracy = agent.get_betas()[0]

    for _ in range(3):
        agent.pending_prediction_partner = 0
        agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
        agent.observe_outcome(partner_idx=0, observation=[1, 0], action_taken=0, partner_action=1, payoff=-1.0)
    after_surprise = agent.get_betas()[0]

    assert after_accuracy < before
    assert after_surprise > after_accuracy
    assert np.isclose(np.asarray(agent.precision_signal(), dtype=float)[0], agent.get_betas()[0])


def test_lesioned_decouple_updates_beta_but_not_precision_signal():
    agent = _make_agent(LesionedAgent, initial_beta=1.0, lesion_mode="decouple")

    agent.pending_prediction_partner = 0
    agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)
    agent.observe_outcome(partner_idx=0, observation=[1, 0], action_taken=0, partner_action=1, payoff=-1.0)

    assert not np.isclose(agent.get_betas()[0], 1.0)
    np.testing.assert_allclose(np.asarray(agent.precision_signal(), dtype=float), np.ones(agent.num_partners))
