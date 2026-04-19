"""Graded investment trust game environment."""

from __future__ import annotations

from env.trust_game import TrustGameEnv
from trust.model import TrustGameModel


class GradedTrustGameEnv(TrustGameEnv):
    """Trust game where the agent chooses an investment level (0 to N-1)."""

    def __init__(self, config: dict, seed: int | None = None):
        super().__init__(config, seed=seed)
        self.model = TrustGameModel(config)
