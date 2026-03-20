"""Simple baseline agents for benchmarking.

These agents implement the same protocol as BaseAgent (reset, plan_and_act,
observe_outcome, get_metrics) but do NOT inherit from BaseAgent or depend on
the generative model infrastructure. They provide anchoring context for
interpreting active inference agent performance.
"""

from __future__ import annotations

import numpy as np


class RandomAgent:
    """Uniformly random cooperate/defect."""

    def __init__(self, num_partners: int = 4, seed: int = 0):
        self.num_partners = num_partners
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._last_action: int | None = None
        self._last_payoff: float = np.nan
        self._interaction_counts = np.zeros(num_partners, dtype=int)

    def reset(self):
        self.rng = np.random.default_rng(self.seed)
        self._last_action = None
        self._last_payoff = np.nan
        self._interaction_counts = np.zeros(self.num_partners, dtype=int)

    def plan_and_act(self, active_partner: int | None) -> int:
        self._last_action = int(self.rng.integers(2))
        return self._last_action

    def observe_outcome(
        self,
        partner_idx: int,
        observation: list[int],
        action_taken: int,
        partner_action: int,
        payoff: float,
        true_partner_type: str | None = None,
    ):
        self._last_payoff = float(payoff)
        self._interaction_counts[partner_idx] += 1

    def get_metrics(self) -> dict:
        return {
            "agent_type": "random",
            "last_action": self._last_action,
            "last_payoff": self._last_payoff,
        }


class TitForTatAgent:
    """Cooperates initially, then mirrors each partner's last action."""

    def __init__(self, num_partners: int = 4, seed: int = 0):
        self.num_partners = num_partners
        self.seed = seed
        self._partner_last_actions = np.zeros(num_partners, dtype=int)
        self._last_action: int | None = None
        self._last_payoff: float = np.nan
        self._active_partner: int | None = None

    def reset(self):
        self._partner_last_actions = np.zeros(self.num_partners, dtype=int)
        self._last_action = None
        self._last_payoff = np.nan
        self._active_partner = None

    def plan_and_act(self, active_partner: int | None) -> int:
        self._active_partner = active_partner
        if active_partner is not None:
            self._last_action = int(self._partner_last_actions[active_partner])
        else:
            self._last_action = 0
        return self._last_action

    def observe_outcome(
        self,
        partner_idx: int,
        observation: list[int],
        action_taken: int,
        partner_action: int,
        payoff: float,
        true_partner_type: str | None = None,
    ):
        self._partner_last_actions[partner_idx] = partner_action
        self._last_payoff = float(payoff)

    def get_metrics(self) -> dict:
        return {
            "agent_type": "tit_for_tat",
            "last_action": self._last_action,
            "last_payoff": self._last_payoff,
        }


class WinStayLoseShiftAgent:
    """Repeats action if payoff was positive, switches otherwise.

    Per-partner memory: tracks the last action and payoff for each partner.
    """

    def __init__(self, num_partners: int = 4, seed: int = 0, threshold: float = 0.0):
        self.num_partners = num_partners
        self.seed = seed
        self.threshold = threshold
        self._partner_last_actions = np.zeros(num_partners, dtype=int)
        self._partner_last_payoffs = np.full(num_partners, np.nan)
        self._last_action: int | None = None
        self._last_payoff: float = np.nan

    def reset(self):
        self._partner_last_actions = np.zeros(self.num_partners, dtype=int)
        self._partner_last_payoffs = np.full(self.num_partners, np.nan)
        self._last_action = None
        self._last_payoff = np.nan

    def plan_and_act(self, active_partner: int | None) -> int:
        if active_partner is None:
            self._last_action = 0
            return self._last_action

        last_payoff = self._partner_last_payoffs[active_partner]
        last_action = self._partner_last_actions[active_partner]

        if np.isnan(last_payoff):
            self._last_action = 0  # cooperate initially
        elif last_payoff > self.threshold:
            self._last_action = int(last_action)  # win-stay
        else:
            self._last_action = 1 - int(last_action)  # lose-shift

        return self._last_action

    def observe_outcome(
        self,
        partner_idx: int,
        observation: list[int],
        action_taken: int,
        partner_action: int,
        payoff: float,
        true_partner_type: str | None = None,
    ):
        self._partner_last_actions[partner_idx] = action_taken
        self._partner_last_payoffs[partner_idx] = payoff
        self._last_payoff = float(payoff)

    def get_metrics(self) -> dict:
        return {
            "agent_type": "win_stay_lose_shift",
            "last_action": self._last_action,
            "last_payoff": self._last_payoff,
        }


class QLearningAgent:
    """Tabular Q-learner with per-partner Q-tables.

    State: last partner action (0=cooperate, 1=defect), or 2 for initial state.
    Actions: 0=cooperate, 1=defect.
    """

    def __init__(
        self,
        num_partners: int = 4,
        seed: int = 0,
        alpha: float = 0.1,
        gamma: float = 0.95,
        epsilon: float = 0.1,
    ):
        self.num_partners = num_partners
        self.seed = seed
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = np.random.default_rng(seed)

        self.num_states = 3  # 0=partner cooperated, 1=partner defected, 2=initial
        self.num_actions = 2
        self._q_tables = np.zeros((num_partners, self.num_states, self.num_actions))
        self._partner_states = np.full(num_partners, 2, dtype=int)  # initial state
        self._last_action: int | None = None
        self._last_payoff: float = np.nan
        self._last_partner: int | None = None

    def reset(self):
        self.rng = np.random.default_rng(self.seed)
        self._q_tables = np.zeros((self.num_partners, self.num_states, self.num_actions))
        self._partner_states = np.full(self.num_partners, 2, dtype=int)
        self._last_action = None
        self._last_payoff = np.nan
        self._last_partner = None

    def plan_and_act(self, active_partner: int | None) -> int:
        if active_partner is None:
            self._last_action = 0
            self._last_partner = None
            return self._last_action

        self._last_partner = active_partner
        state = self._partner_states[active_partner]

        if self.rng.random() < self.epsilon:
            self._last_action = int(self.rng.integers(2))
        else:
            q_values = self._q_tables[active_partner, state]
            self._last_action = int(np.argmax(q_values))

        return self._last_action

    def observe_outcome(
        self,
        partner_idx: int,
        observation: list[int],
        action_taken: int,
        partner_action: int,
        payoff: float,
        true_partner_type: str | None = None,
    ):
        state = self._partner_states[partner_idx]
        next_state = partner_action  # 0 or 1

        # Q-learning update
        best_next_q = np.max(self._q_tables[partner_idx, next_state])
        td_target = payoff + self.gamma * best_next_q
        td_error = td_target - self._q_tables[partner_idx, state, action_taken]
        self._q_tables[partner_idx, state, action_taken] += self.alpha * td_error

        self._partner_states[partner_idx] = next_state
        self._last_payoff = float(payoff)

    def get_metrics(self) -> dict:
        return {
            "agent_type": "q_learning",
            "last_action": self._last_action,
            "last_payoff": self._last_payoff,
            "q_tables": self._q_tables.copy(),
        }
