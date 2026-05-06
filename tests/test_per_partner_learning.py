"""Native per-partner pymdp state independence tests."""

from __future__ import annotations

import numpy as np
from runtime_helpers import build_runtime

from experiments.trust.config import ExperimentConfig
from tasks.trust.runtime import snapshot_partner_bank, update_partner_after_observation


def test_each_partner_has_independent_official_agent_instance():
    runtime = build_runtime(ExperimentConfig(payoff_mode="binary", num_partners=3))

    assert len({id(agent) for agent in runtime.partner_bank.agents}) == 3
    for i in range(1, 3):
        np.testing.assert_allclose(runtime.partner_bank.agents[0].A[0], runtime.partner_bank.agents[i].A[0])


def test_observation_only_updates_active_partner_snapshot():
    runtime = build_runtime(ExperimentConfig(payoff_mode="binary", num_partners=3))
    before = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template).partner_joint_beliefs.copy()

    update_partner_after_observation(
        bank=runtime.partner_bank,
        template=runtime.template,
        partner_idx=1,
        obs=[0, 2],
        own_action=0,
    )
    after = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template).partner_joint_beliefs

    np.testing.assert_array_equal(after[0], before[0])
    assert not np.allclose(after[1], before[1])
    np.testing.assert_array_equal(after[2], before[2])
