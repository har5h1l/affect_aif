"""Encodes gridworld interaction summaries into POMDP observations.

Produces the same observation format as TrustGameEnv:
  [observed_partner_action, payoff_obs_index]

This allows our active inference agents to receive gridworld data in the
format their generative model expects.
"""

from __future__ import annotations

import numpy as np

from affect_aif.benchmark.interaction_tracker import RoundSummary


class ObservationEncoder:
    """Translates RoundSummary into trust-game-compatible observations.

    Parameters
    ----------
    payoff_levels : list[float]
        Sorted unique payoff values used by the generative model for
        discretizing continuous payoffs into observation indices.
    noise_prob : float
        Probability of flipping the observed partner action (observation noise).
    """

    def __init__(
        self,
        payoff_levels: list[float] | None = None,
        noise_prob: float = 0.0,
        seed: int = 0,
    ):
        if payoff_levels is None:
            payoff_levels = [-1.0, 1.0, 3.0, 5.0]
        self.payoff_levels = sorted(payoff_levels)
        self.noise_prob = noise_prob
        self.rng = np.random.default_rng(seed)

    def reset(self, seed: int | None = None):
        """Reset the random state."""
        if seed is not None:
            self.rng = np.random.default_rng(seed)

    def payoff_to_index(self, payoff: float) -> int:
        """Map a continuous payoff to the nearest payoff level index."""
        distances = [abs(payoff - level) for level in self.payoff_levels]
        return int(np.argmin(distances))

    def encode(self, summary: RoundSummary) -> list[int]:
        """Convert a RoundSummary into [partner_action_obs, payoff_obs].

        Parameters
        ----------
        summary : RoundSummary
            The gridworld interaction summary for this round.

        Returns
        -------
        list[int]
            [observed_partner_action, payoff_observation_index]
        """
        # Partner action observation (with possible noise)
        partner_action = summary.partner_action
        if self.noise_prob > 0 and self.rng.random() < self.noise_prob:
            partner_action = 1 - partner_action

        # Map scalar payoff signal to payoff index
        payoff_idx = self.payoff_to_index(self.encode_payoff(summary))

        return [int(partner_action), int(payoff_idx)]

    def encode_payoff(self, summary: RoundSummary) -> float:
        """Extract a scalar payoff from the summary for metric logging.

        Uses the resource_delta directly as the payoff signal.
        """
        return summary.resource_delta
