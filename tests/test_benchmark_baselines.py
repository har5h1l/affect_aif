"""Tests for benchmark baseline agents and compat module.

These tests do NOT require cogames or mettagrid.
"""

import numpy as np

from benchmarks.core.compat import cogames_available, mettagrid_available
from tasks.trust.evaluation.baselines import (
    GrimTriggerAgent,
    PavlovAgent,
    QLearningAgent,
    RandomAgent,
    TitForTatAgent,
    WinStayLoseShiftAgent,
)


def test_compat_returns_bool():
    assert isinstance(cogames_available(), bool)
    assert isinstance(mettagrid_available(), bool)


class TestRandomAgent:
    def test_produces_valid_actions(self):
        agent = RandomAgent(num_partners=4, seed=0)
        for _ in range(20):
            action = agent.plan_and_act(active_partner=0)
            assert action in {0, 1}

    def test_reset_reproduces_sequence(self):
        agent = RandomAgent(num_partners=4, seed=42)
        actions_1 = [agent.plan_and_act(0) for _ in range(10)]
        agent.reset()
        actions_2 = [agent.plan_and_act(0) for _ in range(10)]
        assert actions_1 == actions_2

    def test_observe_outcome_updates_payoff(self):
        agent = RandomAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [0, 1], 0, 0, 3.0)
        metrics = agent.get_metrics()
        assert metrics["last_payoff"] == 3.0

    def test_get_metrics_has_expected_keys(self):
        agent = RandomAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        metrics = agent.get_metrics()
        assert "agent_type" in metrics
        assert metrics["agent_type"] == "random"


class TestTitForTatAgent:
    def test_cooperates_initially(self):
        agent = TitForTatAgent(num_partners=4, seed=0)
        action = agent.plan_and_act(active_partner=0)
        assert action == 0  # cooperate

    def test_mirrors_partner_action(self):
        agent = TitForTatAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)  # partner defected
        action = agent.plan_and_act(0)
        assert action == 1  # defect back

    def test_per_partner_memory(self):
        agent = TitForTatAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)  # partner 0 defected
        agent.plan_and_act(1)
        agent.observe_outcome(1, [0, 2], 0, 0, 3.0)  # partner 1 cooperated

        assert agent.plan_and_act(0) == 1  # defect vs partner 0
        agent.observe_outcome(0, [0, 0], 1, 0, 5.0)
        assert agent.plan_and_act(1) == 0  # cooperate vs partner 1


class TestWinStayLoseShiftAgent:
    def test_cooperates_initially(self):
        agent = WinStayLoseShiftAgent(num_partners=4, seed=0)
        assert agent.plan_and_act(0) == 0

    def test_stays_on_win(self):
        agent = WinStayLoseShiftAgent(num_partners=4, seed=0, threshold=0.0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [0, 2], 0, 0, 3.0)  # positive payoff
        assert agent.plan_and_act(0) == 0  # stay with cooperate

    def test_shifts_on_loss(self):
        agent = WinStayLoseShiftAgent(num_partners=4, seed=0, threshold=0.0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)  # negative payoff
        assert agent.plan_and_act(0) == 1  # shift to defect


class TestQLearningAgent:
    def test_produces_valid_actions(self):
        agent = QLearningAgent(num_partners=4, seed=0)
        for _ in range(20):
            action = agent.plan_and_act(active_partner=0)
            assert action in {0, 1}
            agent.observe_outcome(0, [0, 1], action, 0, 3.0)

    def test_q_table_updates(self):
        agent = QLearningAgent(num_partners=4, seed=0, epsilon=0.0)
        initial_q = agent._q_tables.copy()
        agent.plan_and_act(0)
        agent.observe_outcome(0, [0, 2], 0, 0, 3.0)
        assert not np.allclose(agent._q_tables, initial_q)

    def test_reset_clears_q_tables(self):
        agent = QLearningAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [0, 2], 0, 0, 3.0)
        agent.reset()
        assert np.allclose(agent._q_tables, 0.0)


class TestPavlovAgent:
    def test_cooperates_initially(self):
        agent = PavlovAgent(num_partners=4, seed=0)
        assert agent.plan_and_act(0) == 0

    def test_stays_on_mutual_cooperation(self):
        agent = PavlovAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [0, 2], 0, 0, 3.0)
        assert agent.plan_and_act(0) == 0

    def test_stays_on_mutual_defection(self):
        agent = PavlovAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 1], 1, 1, 1.0)
        assert agent.plan_and_act(0) == 1

    def test_shifts_when_suckered(self):
        agent = PavlovAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)
        assert agent.plan_and_act(0) == 1

    def test_shifts_on_temptation(self):
        agent = PavlovAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [0, 3], 1, 0, 5.0)
        assert agent.plan_and_act(0) == 0


class TestGrimTriggerAgent:
    def test_cooperates_initially(self):
        agent = GrimTriggerAgent(num_partners=4, seed=0)
        assert agent.plan_and_act(0) == 0

    def test_defects_forever_after_partner_defects(self):
        agent = GrimTriggerAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)
        for _ in range(10):
            assert agent.plan_and_act(0) == 1
            agent.observe_outcome(0, [0, 2], 1, 0, 5.0)

    def test_per_partner_triggers(self):
        agent = GrimTriggerAgent(num_partners=4, seed=0)
        agent.plan_and_act(0)
        agent.observe_outcome(0, [1, 0], 0, 1, -1.0)
        assert agent.plan_and_act(0) == 1
        assert agent.plan_and_act(1) == 0


def test_all_baselines_share_protocol():
    """All baseline agents implement the same protocol."""
    agents = [
        RandomAgent(num_partners=4, seed=0),
        TitForTatAgent(num_partners=4, seed=0),
        WinStayLoseShiftAgent(num_partners=4, seed=0),
        PavlovAgent(num_partners=4, seed=0),
        GrimTriggerAgent(num_partners=4, seed=0),
        QLearningAgent(num_partners=4, seed=0),
    ]
    for agent in agents:
        assert hasattr(agent, "reset")
        assert hasattr(agent, "plan_and_act")
        assert hasattr(agent, "observe_outcome")
        assert hasattr(agent, "get_metrics")

        agent.reset()
        action = agent.plan_and_act(active_partner=0)
        assert action in {0, 1}
        agent.observe_outcome(0, [0, 1], action, 0, 3.0)
        metrics = agent.get_metrics()
        assert isinstance(metrics, dict)
