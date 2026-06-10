from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents
from tasks.trust.runtime import (
    PartnerBank,
    _batched_categorical_observations,
    _infer_states,
    select_decision,
    snapshot_partner_bank,
    update_partner_after_observation,
)


def test_partner_bank_is_not_an_agent_wrapper() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=2),
        planning_horizon=1,
    )
    bank = PartnerBank(agents=create_partner_agents(template, num_partners=2, gamma=1.0))

    assert not hasattr(bank, "plan_and_act")
    assert not hasattr(bank, "observe_outcome")
    assert not hasattr(bank, "get_metrics")


def test_select_decision_returns_raw_environment_action() -> None:
    config = ExperimentConfig(payoff_mode="binary", num_partners=2)
    template = build_trust_pomdp_template(config, planning_horizon=1)
    bank = PartnerBank(agents=create_partner_agents(template, num_partners=2, gamma=1.0))

    decision = select_decision(
        bank=bank,
        template=template,
        active_partner=0,
        assignment_mode="random",
        base_gamma=1.0,
        action_selection="deterministic",
        rng=np.random.default_rng(0),
    )

    assert isinstance(decision.raw_action, int)
    assert decision.selected_partner == 0
    assert decision.q_pi.ndim == 1


def test_update_partner_after_observation_updates_snapshots() -> None:
    config = ExperimentConfig(payoff_mode="binary", num_partners=1)
    template = build_trust_pomdp_template(config, planning_horizon=1)
    bank = PartnerBank(agents=create_partner_agents(template, num_partners=1, gamma=1.0))

    update_partner_after_observation(
        bank=bank,
        template=template,
        partner_idx=0,
        obs=[0, 2],
        own_action=0,
    )
    snapshot = snapshot_partner_bank(bank=bank, template=template)

    assert snapshot.partner_joint_beliefs.shape == (1, 4, 3)
    np.testing.assert_allclose(snapshot.partner_joint_beliefs[0].sum(), 1.0)


def test_infer_states_without_return_info_matches_return_info() -> None:
    config = ExperimentConfig(payoff_mode="binary", num_partners=1)
    template = build_trust_pomdp_template(config, planning_horizon=1)
    agent_with_info, agent_without_info = create_partner_agents(template, num_partners=2, gamma=1.0)
    observation = [0, 2]

    qs_with_info, _info = agent_with_info.infer_states(
        observation,
        agent_with_info.D,
        return_info=True,
        preprocess_fn=lambda observations: _batched_categorical_observations(
            observations,
            num_obs=agent_with_info.num_obs,
            batch_size=agent_with_info.batch_size,
        ),
    )
    qs_without_info, info = _infer_states(agent_without_info, observation)

    assert info == {}
    for actual, expected in zip(qs_without_info, qs_with_info, strict=True):
        np.testing.assert_array_equal(actual, expected)


def test_infer_states_does_not_request_unused_return_info() -> None:
    config = ExperimentConfig(payoff_mode="binary", num_partners=1)
    template = build_trust_pomdp_template(config, planning_horizon=1)
    agent = create_partner_agents(template, num_partners=1, gamma=1.0)[0]
    original_infer_states = agent.infer_states
    observed_kwargs = []

    def wrapped_infer_states(observations, empirical_prior, *, preprocess_fn=None, return_info=False, **kwargs):
        if preprocess_fn is not None:
            kwargs["preprocess_fn"] = preprocess_fn
        if return_info:
            kwargs["return_info"] = return_info
        observed_kwargs.append(dict(kwargs))
        return original_infer_states(observations, empirical_prior, **kwargs)

    object.__setattr__(agent, "infer_states", wrapped_infer_states)

    _infer_states(agent, [0, 2])

    assert observed_kwargs
    assert "return_info" not in observed_kwargs[0]
