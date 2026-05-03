"""Decision #9: each per-partner aif.Agent holds its OWN A, B, pA, pB.
C, D, E remain shared by reference."""

from __future__ import annotations

import numpy as np


def test_each_partner_has_independent_pA():
    from tasks.trust.agents import TrustGameAgent
    from tasks.trust.models import TrustGameModel

    cfg = {"payoff_mode": "binary", "num_partners": 3}
    agent = TrustGameAgent(TrustGameModel(cfg), learn_A=True, pA_scale=1.0)

    for i in range(1, 3):
        np.testing.assert_allclose(agent.partners[0].pA[0], agent.partners[i].pA[0])

    agent.partners[0].pA[0] += 5.0
    for i in range(1, 3):
        assert not np.allclose(agent.partners[0].pA[0], agent.partners[i].pA[0])


def test_each_partner_has_independent_A():
    from tasks.trust.agents import TrustGameAgent
    from tasks.trust.models import TrustGameModel

    cfg = {"payoff_mode": "binary", "num_partners": 3}
    agent = TrustGameAgent(TrustGameModel(cfg))
    for i in range(1, 3):
        np.testing.assert_allclose(agent.partners[0].A[0], agent.partners[i].A[0])

    agent.partners[0].A[0][0, 0, 0] = 999.0
    assert agent.partners[1].A[0][0, 0, 0] != 999.0


def test_C_D_shared_by_reference():
    from tasks.trust.agents import TrustGameAgent
    from tasks.trust.models import TrustGameModel

    cfg = {"payoff_mode": "binary", "num_partners": 3}
    agent = TrustGameAgent(TrustGameModel(cfg))
    for i in range(1, 3):
        assert agent.partners[0].C is agent.partners[i].C
        assert agent.partners[0].D is agent.partners[i].D


def test_observe_outcome_only_updates_active_partner_pA():
    from tasks.trust.agents import TrustGameAgent
    from tasks.trust.models import TrustGameModel

    cfg = {"payoff_mode": "binary", "num_partners": 3, "observation_noise": 0.0}
    agent = TrustGameAgent(TrustGameModel(cfg), learn_A=True)
    agent.reset()

    pA_before = [np.asarray(p.pA[0]).copy() for p in agent.partners]
    agent.observe_outcome(
        partner_idx=1,
        observation=[0, 0],
        action_taken=0,
        partner_action=0,
        payoff=3.0,
    )
    pA_after = [np.asarray(p.pA[0]).copy() for p in agent.partners]

    np.testing.assert_array_equal(pA_after[0], pA_before[0])
    assert not np.allclose(pA_after[1], pA_before[1])
    np.testing.assert_array_equal(pA_after[2], pA_before[2])
