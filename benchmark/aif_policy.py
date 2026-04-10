"""Wraps active inference agents as CoGames-compatible policies.

This enables submitting our agents to the Alignment League benchmark
and running them directly in CoGames tournaments.

The policy translates CoGames observations into our agent's expected
format and maps our agent's actions back to CoGames action space.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from benchmark.interaction_tracker import InteractionEvent, InteractionTracker
from benchmark.observation_encoder import ObservationEncoder


class AIFPolicy:
    """Wraps an active inference agent as a CoGames-compatible policy.

    This policy bridges our agents into the CoGames environment by:
    1. Receiving CoGames observations
    2. Translating them via InteractionTracker + ObservationEncoder
    3. Running our agent's plan_and_act()
    4. Translating the cooperate/defect action back to CoGames action space
    """

    def __init__(
        self,
        agent: Any,
        num_partners: int = 4,
        ticks_per_round: int = 10,
        payoff_levels: list[float] | None = None,
    ):
        self.agent = agent
        self.num_partners = num_partners
        self.ticks_per_round = ticks_per_round
        self.tracker = InteractionTracker(
            num_partners=num_partners,
            ticks_per_round=ticks_per_round,
        )
        self.encoder = ObservationEncoder(payoff_levels=payoff_levels)
        self._tick_count = 0
        self._pending_action: int = 0  # cooperate by default

    def reset(self):
        """Reset the policy for a new episode."""
        self.agent.reset()
        self.tracker.reset()
        self._tick_count = 0
        self._pending_action = 0

    def act(self, observation: dict) -> dict:
        """Compute an action from a CoGames observation.

        Parameters
        ----------
        observation : dict
            CoGames observation dict containing gridworld state.

        Returns
        -------
        dict
            CoGames action dict. The specific format depends on the
            CoGames environment being used.
        """
        # Extract interaction events from observation
        events = self._extract_events(observation)
        self.tracker.record_events(events)
        self.tracker.tick()
        self._tick_count += 1

        # At round boundaries, run our agent's planning
        if self.tracker.is_round_complete():
            summary = self.tracker.summarize_round()
            obs = self.encoder.encode(summary)
            payoff = self.encoder.encode_payoff(summary)

            # Feed observation to agent
            self.agent.observe_outcome(
                partner_idx=summary.partner_idx,
                observation=obs,
                action_taken=summary.agent_action,
                partner_action=summary.partner_action,
                payoff=payoff,
            )

            # Plan next action
            self._pending_action = self.agent.plan_and_act(
                active_partner=summary.partner_idx
            )

        # Map cooperate/defect to gridworld action
        return self._translate_action(self._pending_action)

    def _extract_events(self, observation: dict) -> list[InteractionEvent]:
        """Extract interaction events from a CoGames observation.

        This is environment-specific and will need adaptation for different
        CoGames environments. The default implementation handles the
        basic resource-sharing scenario.
        """
        raise NotImplementedError(
            "Requires real CoGames environment — see the cvc_local backend integration."
        )

    def _translate_action(self, trust_action: int) -> dict:
        """Map a trust game action to a CoGames action dict.

        Parameters
        ----------
        trust_action : int
            0 = cooperate, 1 = defect

        Returns
        -------
        dict
            CoGames-compatible action. Structure depends on the specific
            environment.
        """
        raise NotImplementedError(
            "Requires real CoGames environment — see the cvc_local backend integration."
        )

    def get_metrics(self) -> dict:
        """Return the underlying agent's metrics."""
        return self.agent.get_metrics()
