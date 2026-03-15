"""Reward-average control agent."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from affect_aif.agent.base_agent import BaseAgent


class RewardAvgAgent(BaseAgent):
    """Shallow planner with a slow reward-average signal centered onto the beta scale."""

    def __init__(
        self,
        *args,
        num_partners: int = 4,
        lambda_smooth: float = 0.6,
        mu: float = 0.0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.reward_lambda = float(lambda_smooth)
        self.mu = float(mu)
        self.reward_avgs = jnp.zeros((num_partners,), dtype=jnp.float32)

    def reset(self):
        super().reset()
        if hasattr(self, "reward_avgs"):
            self.reward_avgs = jnp.zeros((self.num_partners,), dtype=jnp.float32)

    def current_mu(self) -> float:
        return float(self.mu)

    def terminal_signal(self):
        scale = max(self.max_abs_payoff, 1e-6)
        return 0.5 * (1.0 + jnp.tanh(self.reward_avgs / scale))

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float):
        del partner_action
        updated = self.reward_lambda * self.reward_avgs[partner_idx] + (1.0 - self.reward_lambda) * float(payoff)
        self.reward_avgs = self.reward_avgs.at[int(partner_idx)].set(updated)

    def get_reward_avgs(self) -> np.ndarray:
        return np.asarray(self.reward_avgs, dtype=float)
