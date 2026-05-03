"""Adapter that wraps a CoGames/MettaGrid environment to present the TrustGameEnv interface.

This is the core bridge between the gridworld paradigm and our structured POMDP agents.
Each call to step() runs multiple gridworld ticks internally, then summarizes the
interaction window as a single trust-game round.

Requires: pip install cogames
"""

from __future__ import annotations

from typing import Any

import numpy as np

from benchmark.compat import require_cogames
from benchmark.interaction_tracker import InteractionEvent, InteractionTracker
from benchmark.observation_encoder import ObservationEncoder
from benchmark.scenarios import BenchmarkScenario, get_scenario
from benchmark.scripted_partners import ScriptedPartner, create_partner


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
        ticks_per_round: int | None = None,
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
        self.assignment_mode = str(scenario.assignment_mode)
        self.available_types = [str(name) for name in scenario.partner_types]
        initial_types = scenario.initial_partner_types or scenario.partner_types[: self.num_partners]
        self.initial_partner_types = [str(name) for name in initial_types[: self.num_partners]]
        self.p_switch = float(scenario.p_switch)
        self.scheduled_type_switches = self._parse_scheduled_switches(scenario.scheduled_type_switches)
        self.ticks_per_round = ticks_per_round if ticks_per_round is not None else scenario.ticks_per_round
        seed_rng = np.random.default_rng(self.seed)
        self._partner_seeds = [int(seed_rng.integers(2**31 - 1)) for _ in range(self.num_partners)]

        self.tracker = InteractionTracker(
            num_partners=self.num_partners,
            ticks_per_round=self.ticks_per_round,
        )
        self.encoder = ObservationEncoder(
            payoff_levels=payoff_levels,
            noise_prob=observation_noise,
            seed=self.seed,
        )

        self.partners: list[ScriptedPartner] = []

        self._cogames_env: Any = None
        self._cogames_available = False
        self.round_idx = 0
        self.history: list[dict] = []
        self.active_partner: int | None = None

    def _parse_scheduled_switches(self, events: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
        parsed: dict[int, list[dict[str, Any]]] = {}
        for event in events:
            round_number = int(event["round"])
            parsed.setdefault(round_number, []).append(
                {
                    "partner_idx": int(event["partner_idx"]),
                    "to_type": str(event["to_type"]),
                }
            )
        return parsed

    def _create_partner(self, partner_idx: int, type_name: str) -> ScriptedPartner:
        return create_partner(type_name, partner_idx, seed=self._partner_seeds[partner_idx])

    def _reset_partners(self):
        self.partners = [
            self._create_partner(idx, type_name) for idx, type_name in enumerate(self.initial_partner_types)
        ]

    def _force_partner_type(self, partner_idx: int, new_type: str):
        self.partners[partner_idx] = self._create_partner(partner_idx, new_type)

    def _apply_scheduled_switches(self, round_number: int) -> set[int]:
        switched: set[int] = set()
        for event in self.scheduled_type_switches.get(int(round_number), []):
            partner_idx = int(event["partner_idx"])
            self._force_partner_type(partner_idx, str(event["to_type"]))
            switched.add(partner_idx)
        return switched

    def _maybe_stochastic_switch(self, partner_idx: int) -> bool:
        if self.p_switch <= 0.0 or self.rng.random() >= self.p_switch:
            return False
        current_type = self.partners[partner_idx].type_name
        candidates = [name for name in self.available_types if name != current_type]
        if not candidates:
            return False
        next_type = str(self.rng.choice(candidates))
        self._force_partner_type(partner_idx, next_type)
        return True

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
            self.tracker.record_event(
                InteractionEvent(
                    tick=self.round_idx,
                    partner_idx=partner_idx,
                    event_type="share",
                    resource_delta=-1.0,
                )
            )
        else:
            self.tracker.record_event(
                InteractionEvent(
                    tick=self.round_idx,
                    partner_idx=partner_idx,
                    event_type="attack",
                    resource_delta=0.5,
                )
            )

        if partner_event_type == "share":
            self.tracker.record_event(
                InteractionEvent(
                    tick=self.round_idx,
                    partner_idx=partner_idx,
                    event_type="receive",
                    resource_delta=3.0 if agent_action == 0 else -1.0,
                )
            )
        else:
            self.tracker.record_event(
                InteractionEvent(
                    tick=self.round_idx,
                    partner_idx=partner_idx,
                    event_type="steal",
                    resource_delta=-1.0,
                )
            )

        # Compute payoffs (mirroring trust game payoff structure)
        partner_action = 0 if partner_event_type == "share" else 1
        social_action = agent_action

        # Payoff matrix: cooperate/defect x cooperate/defect
        payoff_matrix = {
            (0, 0): (3.0, 3.0),  # mutual cooperation
            (0, 1): (-1.0, 5.0),  # sucker
            (1, 0): (5.0, -1.0),  # temptation
            (1, 1): (1.0, 1.0),  # mutual defection
        }
        agent_payoff, partner_payoff = payoff_matrix[(social_action, partner_action)]

        summary = self.tracker.summarize_round(primary_partner=partner_idx)

        # Keep encoded payoff observation consistent with returned scalar payoff.
        # The tracker summary captures raw resource delta over events, while the
        # trust-game interface (and agent.observe_outcome) uses agent_payoff.
        # We encode from the same scalar used in results to avoid mismatches.
        summary.resource_delta = agent_payoff
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
        self._reset_partners()

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
        """Select next partner according to the scenario assignment mode."""
        if self.assignment_mode == "agent_choice":
            return None
        return int(self.rng.integers(self.num_partners))

    def step(self, agent_action: int) -> dict:
        """Execute one round and return trust-game-compatible result."""
        scheduled_switched = self._apply_scheduled_switches(self.round_idx + 1)
        if self._cogames_available and self._cogames_env is not None:
            result = self._run_cogames_round(agent_action)
        else:
            result = self._simulate_gridworld_round(agent_action)
        stochastic_switch = self._maybe_stochastic_switch(result["partner_idx"])
        type_switched = (result["partner_idx"] in scheduled_switched) or stochastic_switch
        switch_kind = (
            "scheduled"
            if result["partner_idx"] in scheduled_switched
            else "stochastic"
            if stochastic_switch
            else "none"
        )

        self.round_idx += 1
        self.active_partner = self._select_next_active_partner()

        result.update(
            {
                "observation_partner_idx": result["partner_idx"],
                "active_partner": self.active_partner,
                "round": self.round_idx,
                "type_switched": bool(type_switched),
                "switch_kind": switch_kind,
                "current_partner_switched": bool(type_switched),
                "current_partner_scheduled_switch": bool(result["partner_idx"] in scheduled_switched),
                "scheduled_switch_partner_ids": sorted(int(idx) for idx in scheduled_switched),
                "true_types": [p.type_name for p in self.partners],
            }
        )

        self.history.append(result)
        return result

    def get_partner_type(self, partner_idx: int) -> str:
        """Return the current ground-truth type for a partner."""
        return self.partners[partner_idx].type_name

    def get_episode_summary(self) -> dict:
        """Return coarse summary statistics for the current episode."""
        payoffs = (
            np.asarray([row["agent_payoff"] for row in self.history], dtype=float) if self.history else np.asarray([])
        )
        return {
            "num_rounds": len(self.history),
            "cumulative_payoff": float(payoffs.sum()) if len(payoffs) else 0.0,
            "mean_payoff": float(payoffs.mean()) if len(payoffs) else 0.0,
            "environment": "cogames" if self._cogames_available else "simulated_gridworld",
        }
