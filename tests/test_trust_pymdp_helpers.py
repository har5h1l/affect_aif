from __future__ import annotations

import numpy as np
import pytest

from experiments.trust.config import ExperimentConfig
from tasks.trust.models import TrustGameModel
from tasks.trust.pymdp_helpers import create_agent, infer_once, select_first_timestep_action


class FakePymdpAgent:
    D = object()

    def __init__(self, q_pi: np.ndarray, policy_scores: np.ndarray):
        self.q_pi = q_pi
        self.policy_scores = policy_scores

    def infer_states(self, obs, empirical_prior=None, return_info=False):
        assert obs == [0]
        assert empirical_prior is self.D
        return "qs", {"return_info": return_info}

    def infer_policies(self, qs):
        assert qs == "qs"
        return self.q_pi, self.policy_scores


class SeriousTypeErrorAgent(FakePymdpAgent):
    def infer_states(self, obs, empirical_prior=None, return_info=False):
        raise TypeError("real pymdp internal failure")


def test_create_agent_uses_official_pymdp_agent() -> None:
    bundle = TrustGameModel(ExperimentConfig(payoff_mode="binary")).to_pymdp_bundle()
    agent = create_agent(bundle, gamma=1.0)

    assert agent.__class__.__module__.startswith("pymdp.")


def test_infer_once_returns_policy_diagnostics() -> None:
    bundle = TrustGameModel(ExperimentConfig(payoff_mode="binary")).to_pymdp_bundle()
    agent = create_agent(bundle, gamma=1.0)

    result = infer_once(agent, obs=[0, 2], bundle=bundle)

    assert result.q_pi.ndim == 1
    assert np.isclose(result.q_pi.sum(), 1.0)
    assert result.policy_scores.shape == result.q_pi.shape


def test_select_first_timestep_action_returns_factor_actions() -> None:
    bundle = TrustGameModel(ExperimentConfig(payoff_mode="binary")).to_pymdp_bundle()
    q_pi = np.zeros(len(bundle.policies), dtype=float)
    q_pi[0] = 1.0

    action = select_first_timestep_action(bundle.policies, q_pi, deterministic=True)

    assert action.shape == (bundle.policies.shape[2],)


def test_infer_once_squeezes_singleton_batch_policy_vectors() -> None:
    agent = FakePymdpAgent(q_pi=np.array([[0.25, 0.75]]), policy_scores=np.array([[1.0, 2.0]]))

    result = infer_once(agent, obs=[0], bundle=None)

    assert result.q_pi.shape == (2,)
    assert result.policy_scores.shape == (2,)
    assert np.allclose(result.q_pi, [0.25, 0.75])
    assert result.info == {"return_info": True}


def test_infer_once_rejects_invalid_q_pi() -> None:
    agent = FakePymdpAgent(q_pi=np.array([0.2, 0.2]), policy_scores=np.array([1.0, 2.0]))

    with pytest.raises(ValueError, match="sum to 1"):
        infer_once(agent, obs=[0], bundle=None)


def test_select_first_timestep_action_stochastic_sampling_is_reproducible() -> None:
    policies = np.array([[[0]], [[1]], [[2]]])
    q_pi = np.array([0.1, 0.2, 0.7])
    rng_a = np.random.default_rng(17)
    rng_b = np.random.default_rng(17)

    actions_a = [select_first_timestep_action(policies, q_pi, deterministic=False, rng=rng_a) for _ in range(8)]
    actions_b = [select_first_timestep_action(policies, q_pi, deterministic=False, rng=rng_b) for _ in range(8)]

    assert [int(action[0]) for action in actions_a] == [int(action[0]) for action in actions_b]


def test_select_first_timestep_action_rejects_policy_q_pi_length_mismatch() -> None:
    policies = np.array([[[0]], [[1]]])
    q_pi = np.array([0.2, 0.3, 0.5])

    with pytest.raises(ValueError, match="len\\(q_pi\\) must match"):
        select_first_timestep_action(policies, q_pi, deterministic=True)


def test_infer_once_does_not_swallow_serious_infer_states_type_errors() -> None:
    agent = SeriousTypeErrorAgent(q_pi=np.array([1.0]), policy_scores=np.array([0.0]))

    with pytest.raises(TypeError, match="real pymdp internal failure"):
        infer_once(agent, obs=[0], bundle=None)
