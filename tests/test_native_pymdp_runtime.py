from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents
from tasks.trust.runtime import (
    PartnerBank,
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
