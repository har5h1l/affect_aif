"""Classifies gridworld agent interactions as cooperate/defect events.

The InteractionTracker processes raw gridworld events (resource sharing,
attacks, proximity) and produces per-round cooperation/defection summaries
that map to the trust game's binary action space.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class InteractionEvent:
    """A single gridworld interaction between the focal agent and a partner."""

    tick: int
    partner_idx: int
    event_type: str  # "share", "attack", "proximity", "receive"
    resource_delta: float = 0.0


@dataclass
class RoundSummary:
    """Summary of one trust-game 'round' worth of gridworld ticks."""

    partner_idx: int
    partner_action: int  # 0=cooperate, 1=defect
    agent_action: int  # 0=cooperate, 1=defect
    resource_delta: float  # net resource change for focal agent
    num_cooperative_events: int = 0
    num_hostile_events: int = 0
    confidence: float = 1.0  # how confident the classification is


class InteractionTracker:
    """Tracks per-partner interaction histories and classifies behavior.

    Accumulates gridworld events over a configurable interaction window
    (ticks_per_round), then emits a RoundSummary classifying the dominant
    interaction as cooperate or defect.
    """

    COOPERATIVE_EVENTS = {"share", "receive", "heal"}
    HOSTILE_EVENTS = {"attack", "steal", "freeze"}

    def __init__(
        self,
        num_partners: int,
        ticks_per_round: int = 10,
        cooperation_threshold: float = 0.5,
    ):
        self.num_partners = num_partners
        self.ticks_per_round = ticks_per_round
        self.cooperation_threshold = cooperation_threshold

        self._current_tick = 0
        self._round_events: dict[int, list[InteractionEvent]] = {
            i: [] for i in range(num_partners)
        }
        self._cumulative_interactions: dict[int, dict[str, int]] = {
            i: {"cooperative": 0, "hostile": 0} for i in range(num_partners)
        }

    def reset(self):
        """Clear all tracked state."""
        self._current_tick = 0
        self._round_events = {i: [] for i in range(self.num_partners)}
        self._cumulative_interactions = {
            i: {"cooperative": 0, "hostile": 0} for i in range(self.num_partners)
        }

    def record_event(self, event: InteractionEvent):
        """Record a single interaction event."""
        if 0 <= event.partner_idx < self.num_partners:
            self._round_events[event.partner_idx].append(event)

    def record_events(self, events: list[InteractionEvent]):
        """Record multiple events at once."""
        for event in events:
            self.record_event(event)

    def tick(self):
        """Advance the internal tick counter."""
        self._current_tick += 1

    def is_round_complete(self) -> bool:
        """Check if enough ticks have elapsed for a round summary."""
        return self._current_tick > 0 and self._current_tick % self.ticks_per_round == 0

    def classify_partner_behavior(self, partner_idx: int) -> tuple[int, float]:
        """Classify a partner's behavior over the current round.

        Returns (action, confidence) where action is 0 (cooperate) or 1 (defect),
        and confidence is in [0, 1].
        """
        events = self._round_events[partner_idx]
        if not events:
            # No interaction: default to defect (no cooperation observed)
            return 1, 0.0

        cooperative = sum(1 for e in events if e.event_type in self.COOPERATIVE_EVENTS)
        hostile = sum(1 for e in events if e.event_type in self.HOSTILE_EVENTS)
        total = cooperative + hostile

        if total == 0:
            return 1, 0.0

        coop_ratio = cooperative / total
        action = 0 if coop_ratio >= self.cooperation_threshold else 1
        confidence = abs(coop_ratio - 0.5) * 2  # 0 at threshold, 1 at extremes
        return action, confidence

    def classify_focal_behavior(self, partner_idx: int) -> int:
        """Classify the focal agent's behavior toward a partner.

        Inferred from events: if we shared resources, that's cooperation.
        If we attacked, that's defection.
        """
        events = self._round_events[partner_idx]
        shares = sum(1 for e in events if e.event_type == "share")
        attacks = sum(1 for e in events if e.event_type == "attack")

        if shares > attacks:
            return 0
        if attacks > shares:
            return 1
        return 0  # default cooperate on tie

    def compute_resource_delta(self, partner_idx: int) -> float:
        """Net resource change from interactions with this partner."""
        return sum(e.resource_delta for e in self._round_events[partner_idx])

    def summarize_round(self, primary_partner: int | None = None) -> RoundSummary:
        """Produce a RoundSummary for the most-interacted-with partner.

        If primary_partner is specified, summarize that partner specifically.
        Otherwise, pick the partner with the most interaction events.
        """
        if primary_partner is not None:
            partner_idx = primary_partner
        else:
            # Pick partner with most events
            event_counts = {i: len(evts) for i, evts in self._round_events.items()}
            partner_idx = max(event_counts, key=event_counts.get)

        partner_action, confidence = self.classify_partner_behavior(partner_idx)
        agent_action = self.classify_focal_behavior(partner_idx)
        resource_delta = self.compute_resource_delta(partner_idx)

        events = self._round_events[partner_idx]
        cooperative = sum(1 for e in events if e.event_type in self.COOPERATIVE_EVENTS)
        hostile = sum(1 for e in events if e.event_type in self.HOSTILE_EVENTS)

        # Update cumulative counts
        self._cumulative_interactions[partner_idx]["cooperative"] += cooperative
        self._cumulative_interactions[partner_idx]["hostile"] += hostile

        summary = RoundSummary(
            partner_idx=partner_idx,
            partner_action=partner_action,
            agent_action=agent_action,
            resource_delta=resource_delta,
            num_cooperative_events=cooperative,
            num_hostile_events=hostile,
            confidence=confidence,
        )

        # Clear round events
        self._round_events = {i: [] for i in range(self.num_partners)}

        return summary

    def get_partner_cooperation_history(self, partner_idx: int) -> float:
        """Cumulative cooperation ratio for a partner."""
        stats = self._cumulative_interactions[partner_idx]
        total = stats["cooperative"] + stats["hostile"]
        if total == 0:
            return 0.5
        return stats["cooperative"] / total
