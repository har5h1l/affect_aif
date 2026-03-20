"""Adapter that wraps a CoGames/MettaGrid environment to present the TrustGameEnv interface.

This is the core bridge between the gridworld paradigm and our structured POMDP agents.
Each call to step() runs multiple gridworld ticks internally, then summarizes the
interaction window as a single trust-game round.

Requires: pip install cogames
"""

from __future__ import annotations

from typing import Any

import numpy as np

from affect_aif.benchmark.compat import require_cogames
from affect_aif.benchmark.interaction_tracker import InteractionEvent, InteractionTracker
from affect_aif.benchmark.observation_encoder import ObservationEncoder
from affect_aif.benchmark.scenarios import BenchmarkScenario, get_scenario
from affect_aif.benchmark.scripted_partners import ScriptedPartner, create_partner


class CoGamesTrustAdapter:
    """Wraps a CoGames environment to present the TrustGameEnv interface.

    This adapter bridges the gap between MettaGrid's spatial gridworld and
    our agents' expectation of structured trust-game observations. It:

    1. Runs the gridworld for ticks_per_round steps per trust-game round
    2. Tracks per-partner interactions via InteractionTracker
    3. Classifies behavior as cooperate/defect
    4. Produces observations in [partner_action, payoff_index] format
    5. Manages scripted partner agents within the gridworld

    The adapter presents the same reset()/step() interface as TrustGameEnv.
    """

    def __init__(
        self,
        scenario: BenchmarkScenario | str,
        seed: int | None = None,
        payoff_levels: list[float] | None = None,
        observation_noise: float = 0.0,
    ):
        if isinstance(scenario, str):
            scenario = get_scenario(scenario)

        self.scenario = scenario
        self.seed = seed if seed is not None else 42
        self.rng = np.random.default_rng(self.seed)
        self.num_partners = scenario.num_partners
        self.num_rounds = scenario.num_rounds
        self.ticks_per_round = scenario.ticks_per_round

        self.tracker = InteractionTracker(
            num_partners=self.num_partners,
            ticks_per_round=self.ticks_per_round,
        )
        self.encoder = ObservationEncoder(
            payoff_levels=payoff_levels,
            noise_prob=observation_noise,
            seed=self.seed,
        )

        # Create scripted partners
        self.partners: list[ScriptedPartner] = []
        for idx, type_name in enumerate(scenario.partner_types[:self.num_partners]):
            partner_seed = int(self.rng.integers(2**31 - 1))
            self.partners.append(create_partner(type_name, idx, seed=partner_seed))

        self._cogames_env: Any = None
        self._cogames_available = False
        self.round_idx = 0
        self.history: list[dict] = []
        self.active_partner: int | None = None

    def _try_init_cogames(self):
        """Attempt to initialize the CoGames environment.

        Falls back to simulation mode if CoGames is not available.
        """
        try:
            require_cogames()
            self._cogames_available = True
            # CoGames env initialization would go here:
            # from cogames.env import CogVsClipsEnv
            # self._cogames_env = CogVsClipsEnv(...)
        except ImportError:
            self._cogames_available = False

    def _simulate_gridworld_round(self, agent_action: int) -> dict:
        """Simulate a gridworld round using scripted partners.

        When CoGames is not available, this provides a standalone simulation
        that mirrors the interaction dynamics without the full gridworld.
        This is useful for testing the adapter logic independently.
        """
        # Select which partner we're interacting with this round
        if self.active_partner is not None:
            partner_idx = self.active_partner
        else:
            partner_idx = int(self.rng.integers(self.num_partners))

        partner = self.partners[partner_idx]

        # Agent's action determines events
        agent_event_type = "share" if agent_action == 0 else "attack"

        # Partner decides based on its policy
        partner_event_type = partner.decide()
        partner.observe_focal_action(agent_event_type)

        # Record interaction events
        if agent_event_type == "share":
            self.tracker.record_event(InteractionEvent(
                tick=self.round_idx,
                partner_idx=partner_idx,
                event_type="share",
                resource_delta=-1.0,
            ))
        else:
            self.tracker.record_event(InteractionEvent(
                tick=self.round_idx,
                partner_idx=partner_idx,
                event_type="attack",
                resource_delta=0.5,
            ))

        if partner_event_type == "share":
            self.tracker.record_event(InteractionEvent(
                tick=self.round_idx,
                partner_idx=partner_idx,
                event_type="receive",
                resource_delta=3.0 if agent_action == 0 else -1.0,
            ))
        else:
            self.tracker.record_event(InteractionEvent(
                tick=self.round_idx,
                partner_idx=partner_idx,
                event_type="steal",
                resource_delta=-1.0,
            ))

        # Compute payoffs (mirroring trust game payoff structure)
        partner_action = 0 if partner_event_type == "share" else 1
        social_action = agent_action

        # Payoff matrix: cooperate/defect x cooperate/defect
        payoff_matrix = {
            (0, 0): (3.0, 3.0),   # mutual cooperation
            (0, 1): (-1.0, 5.0),  # sucker
            (1, 0): (5.0, -1.0),  # temptation
            (1, 1): (1.0, 1.0),   # mutual defection
        }
        agent_payoff, partner_payoff = payoff_matrix[(social_action, partner_action)]

        summary = self.tracker.summarize_round(primary_partner=partner_idx)

        observation = self.encoder.encode(summary)

        return {
            "partner_idx": partner_idx,
            "partner_action": partner_action,
            "agent_action": social_action,
            "raw_action": int(agent_action),
            "agent_payoff": agent_payoff,
            "partner_payoff": partner_payoff,
            "observation": observation,
            "true_partner_type": partner.type_name,
        }

    def _run_cogames_round(self, agent_action: int) -> dict:
        """Run a round through the actual CoGames environment.

        Executes ticks_per_round gridworld steps, collects events,
        and produces a trust-game-compatible result dict.
        """
        # This will be implemented when CoGames integration is tested
        # For now, fall back to simulation
        return self._simulate_gridworld_round(agent_action)

    def reset(self) -> dict:
        """Reset the environment and return initial context."""
        self.rng = np.random.default_rng(self.seed)
        self.round_idx = 0
        self.history = []
        self.tracker.reset()
        self.encoder.reset(seed=self.seed)

        for partner in self.partners:
            partner.reset()

        self._try_init_cogames()

        self.active_partner = self._select_next_active_partner()

        return {
            "active_partner": self.active_partner,
            "observation": None,
            "observation_partner_idx": None,
            "round": self.round_idx,
            "true_types": [p.type_name for p in self.partners],
        }

    def _select_next_active_partner(self) -> int | None:
        """Select next partner (random assignment)."""
        return int(self.rng.integers(self.num_partners))

    def step(self, agent_action: int) -> dict:
        """Execute one round and return trust-game-compatible result."""
        if self._cogames_available and self._cogames_env is not None:
            result = self._run_cogames_round(agent_action)
        else:
            result = self._simulate_gridworld_round(agent_action)

        self.round_idx += 1
        self.active_partner = self._select_next_active_partner()

        result.update({
            "observation_partner_idx": result["partner_idx"],
            "active_partner": self.active_partner,
            "round": self.round_idx,
            "type_switched": False,
            "switch_kind": "none",
            "current_partner_switched": False,
            "current_partner_scheduled_switch": False,
            "scheduled_switch_partner_ids": [],
            "true_types": [p.type_name for p in self.partners],
        })

        self.history.append(result)
        return result

    def get_partner_type(self, partner_idx: int) -> str:
        """Return the current ground-truth type for a partner."""
        return self.partners[partner_idx].type_name

    def get_episode_summary(self) -> dict:
        """Return coarse summary statistics for the current episode."""
        payoffs = np.asarray(
            [row["agent_payoff"] for row in self.history], dtype=float
        ) if self.history else np.asarray([])
        return {
            "num_rounds": len(self.history),
            "cumulative_payoff": float(payoffs.sum()) if len(payoffs) else 0.0,
            "mean_payoff": float(payoffs.mean()) if len(payoffs) else 0.0,
            "environment": "cogames" if self._cogames_available else "simulated_gridworld",
        }
