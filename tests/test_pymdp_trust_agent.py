from __future__ import annotations

import numpy as np
from runtime_helpers import build_runtime

from experiments.trust.config import ExperimentConfig
from tasks.trust.runtime import (
    _agent_choice_policy_arrays,
    _infer_agent_choice_policies_batched,
    _infer_partner_policy,
    _softmax,
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


def test_agent_choice_reuses_gamma_vector_for_candidate_scoring() -> None:
    config = ExperimentConfig(
        payoff_mode="graded",
        num_partners=2,
        num_investment_levels=6,
        assignment_mode="agent_choice",
    )
    runtime = build_runtime(config, variant_id="affect", affect="precision", seed=0)

    class CountingBeta:
        def __init__(self) -> None:
            self.calls = 0

        def expected_beta(self) -> np.ndarray:
            self.calls += 1
            return np.asarray([0.5, 2.0], dtype=float)

    beta = CountingBeta()
    runtime.partner_bank.beta = beta

    select_decision(
        bank=runtime.partner_bank,
        template=runtime.template,
        active_partner=None,
        assignment_mode="agent_choice",
        base_gamma=runtime.base_gamma,
        action_selection="sample",
        rng=np.random.default_rng(0),
        affect_mode="normal",
    )

    assert beta.calls == runtime.template.num_partners


def test_agent_choice_high_precision_partner_is_not_penalized_when_scores_match() -> None:
    config = ExperimentConfig(
        payoff_mode="graded",
        num_partners=2,
        num_investment_levels=6,
        assignment_mode="agent_choice",
    )
    runtime = build_runtime(config, variant_id="affect", affect="precision", seed=0)
    assert runtime.partner_bank.beta is not None
    runtime.partner_bank.beta.betas[:] = [0.5, 2.0]

    decision = select_decision(
        bank=runtime.partner_bank,
        template=runtime.template,
        active_partner=None,
        assignment_mode="agent_choice",
        base_gamma=runtime.base_gamma,
        action_selection="sample",
        rng=np.random.default_rng(0),
        affect_mode="normal",
    )

    policies_per_partner = len(runtime.template.policies)
    high_precision_mass = decision.q_pi[:policies_per_partner].sum()
    low_precision_mass = decision.q_pi[policies_per_partner:].sum()

    assert high_precision_mass >= low_precision_mass


def test_agent_choice_policy_arrays_preserve_candidate_order_and_logits() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=2, assignment_mode="agent_choice"),
    )
    policy_scores_by_partner = [
        np.asarray([1.0, 2.0, 3.0, 4.0], dtype=float),
        np.asarray([0.5, 1.5, 2.5, 3.5], dtype=float),
    ]

    partners, policy_indices, first_steps, scores, logits = _agent_choice_policy_arrays(
        template=runtime.template,
        policy_scores_by_partner=policy_scores_by_partner,
        gammas=np.asarray([1.0, 2.0], dtype=float),
    )

    expected_first_steps = np.tile(np.asarray(runtime.template.policies[:, 0], dtype=int), (2, 1))
    np.testing.assert_array_equal(partners, np.asarray([0, 0, 0, 0, 1, 1, 1, 1]))
    np.testing.assert_array_equal(policy_indices, np.asarray([0, 1, 2, 3, 0, 1, 2, 3]))
    np.testing.assert_array_equal(first_steps, expected_first_steps)
    np.testing.assert_allclose(scores, np.asarray([1.0, 2.0, 3.0, 4.0, 0.5, 1.5, 2.5, 3.5]))
    np.testing.assert_allclose(logits, np.asarray([1.0, 2.0, 3.0, 4.0, -1.0, 1.0, 3.0, 5.0]))


def test_batched_agent_choice_policy_scores_match_separate_agents() -> None:
    runtime = build_runtime(
        ExperimentConfig(payoff_mode="graded", num_partners=3, assignment_mode="agent_choice"),
        planning_horizon=2,
    )

    separate_scores = []
    for partner_idx in range(len(runtime.partner_bank.agents)):
        _q_pi, policy_scores = _infer_partner_policy(
            bank=runtime.partner_bank,
            template=runtime.template,
            partner_idx=partner_idx,
            base_gamma=runtime.base_gamma,
            affect_mode=runtime.affect_mode,
        )
        separate_scores.append(policy_scores)

    _batched_q_pi, batched_scores, _gammas = _infer_agent_choice_policies_batched(
        bank=runtime.partner_bank,
        template=runtime.template,
        base_gamma=runtime.base_gamma,
        affect_mode=runtime.affect_mode,
    )

    np.testing.assert_array_equal(batched_scores, np.asarray(separate_scores, dtype=float))


def test_batched_agent_choice_selector_matches_separate_candidate_reconstruction() -> None:
    config = ExperimentConfig(payoff_mode="graded", num_partners=3, assignment_mode="agent_choice")
    separate_runtime = build_runtime(config, planning_horizon=2, seed=0)
    batched_runtime = build_runtime(config, planning_horizon=2, seed=0)
    separate_scores = []
    gammas = []
    for partner_idx in range(len(separate_runtime.partner_bank.agents)):
        _q_pi, policy_scores = _infer_partner_policy(
            bank=separate_runtime.partner_bank,
            template=separate_runtime.template,
            partner_idx=partner_idx,
            base_gamma=separate_runtime.base_gamma,
            affect_mode=separate_runtime.affect_mode,
        )
        separate_scores.append(policy_scores)
        gammas.append(separate_runtime.base_gamma)
    _partners, _policy_indices, _first_steps, scores, logits = _agent_choice_policy_arrays(
        template=separate_runtime.template,
        policy_scores_by_partner=separate_scores,
        gammas=np.asarray(gammas, dtype=float),
    )
    expected_q_pi = _softmax(logits)

    decision = select_decision(
        bank=batched_runtime.partner_bank,
        template=batched_runtime.template,
        active_partner=None,
        assignment_mode="agent_choice",
        base_gamma=batched_runtime.base_gamma,
        action_selection="sample",
        rng=np.random.default_rng(0),
        affect_mode=batched_runtime.affect_mode,
    )

    np.testing.assert_array_equal(decision.policy_scores, scores)
    np.testing.assert_array_equal(decision.q_pi, expected_q_pi)


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
