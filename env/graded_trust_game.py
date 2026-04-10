"""Graded investment trust game environment."""

from __future__ import annotations

from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.generative_model.model import GradedTrustGameModel


class GradedTrustGameEnv(TrustGameEnv):
    """Trust game where the agent chooses an investment level (0 to N-1)."""

    def __init__(self, config: dict, seed: int | None = None):
        super().__init__(config, seed=seed)
        self.model = GradedTrustGameModel(self.config)
