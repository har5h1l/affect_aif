from __future__ import annotations

import numpy as np
from runtime_helpers import build_runtime

from experiments.trust.config import ExperimentConfig
from tasks.trust.runtime import (
    select_decision,
    snapshot_partner_bank,
    update_beta_after_observation,
    update_partner_after_observation,
)


def test_native_runtime_uses_official_pymdp_partner_agents() -> None:
    runtime = build_runtime(ExperimentConfig(payoff_mode="binary", num_partners=2))

    assert len(runtime.partner_bank.agents) == 2
    assert all(agent.__class__.__module__.startswith("pymdp.") for agent in runtime.partner_bank.agents)


def test_runtime_can_plan_and_observe_single_outcome() -> None:
    runtime = build_runtime(ExperimentConfig(payoff_mode="binary", num_partners=2))

    decision = select_decision(
        bank=runtime.partner_bank,
        template=runtime.template,
        active_partner=0,
        assignment_mode="random",
        base_gamma=runtime.base_gamma,
        action_selection="deterministic",
        rng=runtime.rng,
    )
    assert isinstance(decision.raw_action, int)

    update_partner_after_observation(
        bank=runtime.partner_bank,
        template=runtime.template,
        partner_idx=0,
        obs=[0, 2],
        own_action=decision.own_action,
    )

    snapshot = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template)
    assert snapshot.partner_joint_beliefs.shape[0] == 2
    np.testing.assert_allclose(snapshot.partner_joint_beliefs[0].sum(), 1.0)


def test_agent_choice_stores_candidate_level_policy_distribution() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=3, assignment_mode="agent_choice"),
    )

    decision = select_decision(
        bank=runtime.partner_bank,
        template=runtime.template,
        active_partner=None,
        assignment_mode="agent_choice",
        base_gamma=runtime.base_gamma,
        action_selection="deterministic",
        rng=runtime.rng,
    )

    assert len(decision.q_pi) == runtime.template.num_partners * len(runtime.template.policies)
    assert len(decision.policy_scores) == len(decision.q_pi)
    np.testing.assert_allclose(decision.q_pi.sum(), 1.0)


def test_agent_choice_precision_affect_changes_candidate_distribution() -> None:
    config = ExperimentConfig(
        payoff_mode="graded",
        num_partners=2,
        num_investment_levels=6,
        assignment_mode="agent_choice",
    )
    affective = build_runtime(config, variant_id="affect", affect="precision", seed=0)
    lesioned = build_runtime(config, variant_id="lesioned", affect="precision", seed=0)
    assert affective.partner_bank.beta is not None
    assert lesioned.partner_bank.beta is not None
    affective.partner_bank.beta.betas[:] = [0.5, 2.0]
    lesioned.partner_bank.beta.betas[:] = [0.5, 2.0]

    affective_decision = select_decision(
        bank=affective.partner_bank,
        template=affective.template,
        active_partner=None,
        assignment_mode="agent_choice",
        base_gamma=affective.base_gamma,
        action_selection="sample",
        rng=np.random.default_rng(0),
        affect_mode="normal",
    )
    lesioned_decision = select_decision(
        bank=lesioned.partner_bank,
        template=lesioned.template,
        active_partner=None,
        assignment_mode="agent_choice",
        base_gamma=lesioned.base_gamma,
        action_selection="sample",
        rng=np.random.default_rng(0),
        affect_mode="decouple",
    )

    assert not np.allclose(affective_decision.q_pi, lesioned_decision.q_pi)


def test_agent_choice_selected_fields_match_encoded_raw_action() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=3, assignment_mode="agent_choice"),
    )

    decision = select_decision(
        bank=runtime.partner_bank,
        template=runtime.template,
        active_partner=None,
        assignment_mode="agent_choice",
        base_gamma=runtime.base_gamma,
        action_selection="deterministic",
        rng=runtime.rng,
    )

    assert decision.selected_partner == decision.raw_action // 4
    assert decision.selected_action == decision.raw_action % 2


def test_use_information_gain_false_updates_pymdp_agent_flags() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=2),
        variant_id="no_epistemic",
        epistemic_value=False,
    )

    for agent in runtime.partner_bank.agents:
        if hasattr(agent, "use_states_info_gain"):
            assert agent.use_states_info_gain is False
        if hasattr(agent, "use_param_info_gain"):
            assert agent.use_param_info_gain is False


def test_affective_runtime_updates_beta_after_observation() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=1, initial_beta=1.0),
        variant_id="affect",
        affect="precision",
    )
    beta = runtime.partner_bank.beta
    assert beta is not None

    before = beta.expected_beta()[0]
    update_beta_after_observation(
        bank=runtime.partner_bank,
        partner_idx=0,
        predicted_partner_action_probs=np.array([0.1, 0.9]),
        observed_partner_action=0,
        affect_mode=runtime.affect_mode,
    )
    after = beta.expected_beta()[0]

    assert after != before


def test_lesioned_decouple_updates_beta_but_uses_base_precision() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=1, initial_beta=1.0),
        variant_id="lesioned",
        affect="tracked_only",
    )
    beta = runtime.partner_bank.beta
    assert beta is not None

    before = beta.expected_beta()[0]
    update_beta_after_observation(
        bank=runtime.partner_bank,
        partner_idx=0,
        predicted_partner_action_probs=np.array([0.1, 0.9]),
        observed_partner_action=0,
        affect_mode=runtime.affect_mode,
    )

    assert beta.expected_beta()[0] != before
    assert runtime.affect_mode == "decouple"
