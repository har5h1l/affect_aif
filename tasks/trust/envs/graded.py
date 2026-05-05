"""Graded investment trust game environment."""

from __future__ import annotations

from tasks.trust.envs.binary import TrustGameEnv
from tasks.trust.pomdp import build_trust_pomdp_template


class GradedTrustGameEnv(TrustGameEnv):
    """Trust game where the agent chooses an investment level (0 to N-1)."""

    def __init__(self, config: dict, seed: int | None = None):
        super().__init__(config, seed=seed)
        self.template = build_trust_pomdp_template(
            config,
            planning_horizon=1,
            max_policies=self.config.get("max_policies"),
            rng=self.rng,
        )
        self.model = self.template
