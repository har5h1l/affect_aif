from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust import pymdp_helpers
from tasks.trust import AffectiveAgent, LesionedAgent, TrustGameAgent, TrustGameModel


def test_trust_game_agent_uses_pymdp_partner_agents() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=2))
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0)

    assert len(agent.partners) == 2
    assert all(p.__class__.__module__.startswith("pymdp.") for p in agent.partners)


def test_agent_can_plan_and_observe_single_outcome() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=2))
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0)

    action = agent.plan_and_act(active_partner=0)
    assert isinstance(action, int)

    agent.observe_outcome(
        active_partner=0,
        agent_action=action % 2,
        partner_action=0,
        payoff=3.0,
        observation=[0, 2],
    )

    assert agent.partner_beliefs.shape[0] == 2
    np.testing.assert_allclose(agent.partner_beliefs[0].sum(), 1.0)


def test_agent_choice_stores_candidate_level_policy_distribution() -> None:
    model = TrustGameModel(
        ExperimentConfig(payoff_mode="binary", num_partners=3, assignment_mode="agent_choice")
    )
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0)

    agent.plan_and_act(active_partner=None)

    assert len(agent.q_pi) == agent.num_partners * len(agent.bundle.policies)
    assert len(agent.policy_scores) == len(agent.q_pi)
    np.testing.assert_allclose(agent.q_pi.sum(), 1.0)


def test_agent_choice_selected_fields_match_encoded_raw_action() -> None:
    model = TrustGameModel(
        ExperimentConfig(payoff_mode="binary", num_partners=3, assignment_mode="agent_choice")
    )
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0)

    raw_action = agent.plan_and_act(active_partner=None)

    assert agent.selected_partner == raw_action // 4
    assert agent.selected_action == raw_action % 2
    assert agent.last_selected_partner == raw_action // 4
    assert agent.last_selected_action == raw_action % 2


def test_agent_choice_best_policy_idx_is_candidate_indexed_for_nonzero_partner() -> None:
    model = TrustGameModel(
        ExperimentConfig(payoff_mode="binary", num_partners=3, assignment_mode="agent_choice")
    )
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0, action_sampling="deterministic")
    num_policies = len(agent.bundle.policies)

    def infer_partner(partner_idx: int) -> pymdp_helpers.PymdpInferenceResult:
        scores = np.full(num_policies, -100.0, dtype=float)
        scores[1] = float(partner_idx)
        q_pi = np.full(num_policies, 1.0 / num_policies, dtype=float)
        return pymdp_helpers.PymdpInferenceResult(qs=[], q_pi=q_pi, policy_scores=scores, info={})

    agent._infer_partner = infer_partner  # type: ignore[method-assign]

    agent.plan_and_act(active_partner=None)

    expected_local_policy_idx = 1
    expected_candidate_idx = agent.last_selected_partner * num_policies + expected_local_policy_idx
    assert agent.last_selected_partner == 2
    assert agent.best_policy_idx == expected_candidate_idx
    assert agent.q_pi[agent.best_policy_idx] == 1.0


def test_observe_keeps_previous_plan_diagnostics_stable() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=2))
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0)

    action = agent.plan_and_act(active_partner=0)
    q_pi = agent.q_pi.copy()
    policy_scores = agent.policy_scores.copy()
    best_policy_idx = agent.best_policy_idx
    selected_partner = agent.selected_partner
    selected_action = agent.selected_action

    agent.observe_outcome(
        active_partner=0,
        agent_action=action % 2,
        partner_action=0,
        payoff=3.0,
        observation=[0, 2],
    )

    np.testing.assert_allclose(agent.q_pi, q_pi)
    np.testing.assert_allclose(agent.policy_scores, policy_scores)
    assert agent.best_policy_idx == best_policy_idx
    assert agent.selected_partner == selected_partner
    assert agent.selected_action == selected_action
    assert agent.post_observation_q_pi is not None
    assert agent.post_observation_policy_scores is not None


def test_use_information_gain_false_updates_pymdp_agent_flags() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=2))
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0, use_information_gain=False)

    for partner in agent.partners:
        if hasattr(partner, "use_states_info_gain"):
            assert partner.use_states_info_gain is False
        if hasattr(partner, "use_param_info_gain"):
            assert partner.use_param_info_gain is False


def test_affective_agent_updates_beta_after_observation() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=1))
    agent = AffectiveAgent(model=model, planning_horizon=1, seed=0, initial_beta=1.0)

    before = agent.affect.expected_beta()[0]
    agent.observe_outcome(
        active_partner=0,
        agent_action=0,
        partner_action=1,
        payoff=-1.0,
        observation=[1, 0],
    )
    after = agent.affect.expected_beta()[0]

    assert after != before


def test_lesioned_decouple_updates_beta_but_uses_base_precision() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=1))
    agent = LesionedAgent(model=model, planning_horizon=1, seed=0, lesion_mode="decouple", initial_beta=1.0)

    assert agent.affect_modulates_precision is False
    before = agent.affect.expected_beta()[0]
    agent.observe_outcome(
        active_partner=0,
        agent_action=0,
        partner_action=1,
        payoff=-1.0,
        observation=[1, 0],
    )
    after = agent.affect.expected_beta()[0]

    assert after != before

    agent.plan_and_act(active_partner=0)

    applied_gamma = float(np.asarray(agent.partners[0].gamma, dtype=float).squeeze())
    assert applied_gamma == agent.gamma
