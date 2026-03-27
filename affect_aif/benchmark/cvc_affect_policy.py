"""Affect-augmented CvC policy with per-teammate precision (beta) tracking.

Extends the ScoringLoopPolicy state-machine with the same metacognitive
precision mechanism used in the trust-game agent. Each agent maintains a
beta_k estimate for each observed teammate, updated via an EMA surprise
rule. The team-average beta modulates coordination strategy:

  high team_beta (>0.6) -> prioritise shared objectives (coordinate)
  low  team_beta (<0.4) -> work independently (solo mining/exploration)
  mid  team_beta        -> default scoring-loop behaviour

The beta update mirrors affect_aif/agent/affect/state.py:
  surprise = manhattan_distance(predicted, actual) / max_distance
  charge   = alpha * (sigma_0_sq - surprise**2)
  beta_k   = lambda_smooth * beta_k + (1 - lambda_smooth) * sigmoid(charge)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Iterable, Optional

from mettagrid.policy.policy import MultiAgentPolicy, StatefulAgentPolicy, StatefulPolicyImpl
from mettagrid.policy.policy_env_interface import PolicyEnvInterface
from mettagrid.simulator import Action
from mettagrid.simulator.interface import AgentObservation

from affect_aif.benchmark.cvc_beta import (
    COOPERATE_THRESHOLD,
    INDEPENDENT_THRESHOLD,
    INITIAL_BETA,
    TEAM_BETA_SMOOTH,
    update_beta,
)
from affect_aif.benchmark.cvc_navigation import NavigationHelper, NavigationState

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GEAR = ("aligner", "scrambler", "miner", "scout")
ELEMENTS = ("carbon", "oxygen", "germanium", "silicon")

CARGO_THRESHOLD = 8

ROLE_PLAN = ("miner", "miner", "miner", "aligner", "aligner", "miner", "miner", "aligner")


class ScoringPhase(Enum):
    GET_GEAR = auto()
    MINE_ORE = auto()
    DEPOSIT = auto()
    ALIGN_JUNCTION = auto()


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

@dataclass
class AffectScoringState:
    phase: ScoringPhase = ScoringPhase.GET_GEAR
    assigned_role: str = "miner"
    nav: NavigationState = field(default_factory=NavigationState)
    stuck_steps: int = 0
    # Per-teammate tracking
    teammate_positions: dict[int, tuple[int, int]] = field(default_factory=dict)
    teammate_velocities: dict[int, tuple[int, int]] = field(default_factory=dict)
    teammate_betas: dict[int, float] = field(default_factory=dict)
    team_beta_ema: float = INITIAL_BETA


# ---------------------------------------------------------------------------
# Policy implementation
# ---------------------------------------------------------------------------

class AffectCvCPolicyImpl(StatefulPolicyImpl[AffectScoringState]):
    """State-machine CvC policy with per-teammate beta modulation."""

    def __init__(self, policy_env_info: PolicyEnvInterface, agent_id: int):
        self._agent_id = agent_id
        self._policy_env_info = policy_env_info

        self._action_names = policy_env_info.action_names
        self._action_name_set = set(self._action_names)
        self._fallback_action_name = "noop" if "noop" in self._action_name_set else self._action_names[0]
        self._center = (policy_env_info.obs_height // 2, policy_env_info.obs_width // 2)
        self._nav = NavigationHelper(policy_env_info.obs_height, policy_env_info.obs_width, self._center)
        self._max_obs_distance = float(policy_env_info.obs_height + policy_env_info.obs_width)

        self._tag_name_to_id = {name: idx for idx, name in enumerate(policy_env_info.tags)}

        # Build tag-id sets for known structures
        self._gear_station_tags_by_gear = {gear: self._resolve_tag_ids([f"c:{gear}"]) for gear in GEAR}
        self._gear_station_tags = set().union(*self._gear_station_tags_by_gear.values())
        self._extractor_tags = self._resolve_tag_ids([f"{element}_extractor" for element in ELEMENTS])
        self._junction_tags = self._resolve_tag_ids(["junction"])
        self._heart_source_tags = self._resolve_tag_ids(["hub", "chest"])

        # All known structure tag ids (used to identify teammates by exclusion)
        self._structure_tag_ids: set[int] = set()
        self._structure_tag_ids.update(self._gear_station_tags)
        self._structure_tag_ids.update(self._extractor_tags)
        self._structure_tag_ids.update(self._junction_tags)
        self._structure_tag_ids.update(self._heart_source_tags)

    # ---- helpers --------------------------------------------------------

    def _resolve_tag_ids(self, names: Iterable[str]) -> set[int]:
        tag_ids: set[int] = set()
        for name in names:
            if name in self._tag_name_to_id:
                tag_ids.add(self._tag_name_to_id[name])
            type_name = f"type:{name}"
            if type_name in self._tag_name_to_id:
                tag_ids.add(self._tag_name_to_id[type_name])
        return tag_ids

    def _inventory_amounts(self, obs: AgentObservation) -> dict[str, int]:
        items: dict[str, int] = {}
        for token in obs.tokens:
            if token.location != self._center:
                continue
            name = token.feature.name
            if not name.startswith("inv:"):
                continue
            suffix = name[4:]
            item_name, sep, power_str = suffix.rpartition(":p")
            if not sep or not item_name or not power_str.isdigit():
                item_name = suffix
                power = 0
            else:
                power = int(power_str)
            value = int(token.value)
            if value <= 0:
                continue
            base = max(int(token.feature.normalization), 1)
            items[item_name] = items.get(item_name, 0) + value * (base ** power)
        return items

    def _global_value(self, obs: AgentObservation, feature_name: str, default: float = 0.0) -> float:
        for token in obs.tokens:
            if token.feature.name != feature_name:
                continue
            norm = max(float(token.feature.normalization), 1.0)
            return float(token.value) / norm
        return default

    def _closest_tag_location(self, obs: AgentObservation, tag_ids: set[int]) -> Optional[tuple[int, int]]:
        if not tag_ids:
            return None
        best_location: Optional[tuple[int, int]] = None
        best_distance = 999
        for token in obs.tokens:
            if token.feature.name != "tag":
                continue
            if token.value not in tag_ids:
                continue
            loc = token.location
            if loc is None:
                continue
            distance = abs(loc[0] - self._center[0]) + abs(loc[1] - self._center[1])
            if distance < best_distance:
                best_distance = distance
                best_location = token.location
        return best_location

    def _current_gear(self, items: dict[str, int]) -> Optional[str]:
        for gear in GEAR:
            if items.get(gear, 0) > 0:
                return gear
        return None

    def _action(self, name: str) -> Action:
        if name in self._action_name_set:
            return Action(name=name)
        return Action(name=self._fallback_action_name)

    def _navigate_to(self, obs: AgentObservation, state: AffectScoringState, tag_ids: set[int]) -> tuple[Action, AffectScoringState]:
        target = self._closest_tag_location(obs, tag_ids)
        action_name = self._nav.pathfind_toward(obs, state.nav, target)
        if action_name is None:
            action_name = self._nav.explore_action(obs, state.nav)
        if action_name is None:
            action_name = self._fallback_action_name
        state.nav.last_action_name = action_name
        return self._action(action_name), state

    # ---- teammate tracking ----------------------------------------------

    def _detect_teammates(self, obs: AgentObservation) -> dict[int, tuple[int, int]]:
        """Detect teammate positions from observation tags.

        Teammates are identified as tag tokens at non-center locations whose
        tag-id is not a known structure. The tag value is used as a proxy
        teammate id.
        """
        teammates: dict[int, tuple[int, int]] = {}
        for token in obs.tokens:
            if token.feature.name != "tag":
                continue
            loc = token.location
            if loc is None or loc == self._center:
                continue
            tag_id = int(token.value)
            if tag_id in self._structure_tag_ids:
                continue
            # Use tag_id as teammate identifier
            teammates[tag_id] = (loc[0], loc[1])
        return teammates

    def _update_teammate_tracking(
        self,
        state: AffectScoringState,
        obs: AgentObservation,
    ) -> AffectScoringState:
        """Update per-teammate position/velocity/beta from current observation."""
        current_teammates = self._detect_teammates(obs)

        for tid, local_pos in current_teammates.items():
            # Convert to global coordinates for persistent tracking
            global_pos = self._nav._local_to_global(local_pos[0], local_pos[1], state.nav)

            if tid in state.teammate_positions:
                prev_pos = state.teammate_positions[tid]

                # Predict where we expected them using PREVIOUS velocity
                prev_vel = state.teammate_velocities.get(tid, (0, 0))
                predicted = (prev_pos[0] + prev_vel[0], prev_pos[1] + prev_vel[1])

                # NOW compute and store current velocity (after prediction)
                vel = (global_pos[0] - prev_pos[0], global_pos[1] - prev_pos[1])
                state.teammate_velocities[tid] = vel

                # Update beta
                prev_beta = state.teammate_betas.get(tid, INITIAL_BETA)
                state.teammate_betas[tid] = update_beta(
                    predicted, global_pos, prev_beta, self._max_obs_distance
                )
            else:
                # First sighting — initialise
                state.teammate_velocities[tid] = (0, 0)
                state.teammate_betas[tid] = INITIAL_BETA

            state.teammate_positions[tid] = global_pos

        # Update team beta EMA
        if state.teammate_betas:
            mean_beta = sum(state.teammate_betas.values()) / len(state.teammate_betas)
            state.team_beta_ema = (
                TEAM_BETA_SMOOTH * state.team_beta_ema
                + (1.0 - TEAM_BETA_SMOOTH) * mean_beta
            )

        return state

    # ---- main step -------------------------------------------------------

    def step_with_state(self, obs: AgentObservation, state: AffectScoringState) -> tuple[Action, AffectScoringState]:
        items = self._inventory_amounts(obs)
        moved = self._global_value(obs, "last_action_move", default=0.0) > 0.0

        # Update navigation
        state.nav = self._nav.update_position(state.nav, moved)

        # Update teammate tracking and beta
        state = self._update_teammate_tracking(state, obs)

        gear = self._current_gear(items)
        cargo = sum(items.get(element, 0) for element in ELEMENTS)
        has_heart = items.get("heart", 0) > 0

        # Track stuck-ness
        if not moved and state.nav.last_action_name is not None:
            state.stuck_steps += 1
        else:
            state.stuck_steps = 0

        # Determine phase from inventory
        if gear is None:
            state.phase = ScoringPhase.GET_GEAR
        elif gear == "miner":
            state.phase = ScoringPhase.DEPOSIT if cargo >= CARGO_THRESHOLD else ScoringPhase.MINE_ORE
        elif gear in ("aligner", "scrambler"):
            state.phase = ScoringPhase.ALIGN_JUNCTION if has_heart else ScoringPhase.DEPOSIT
        elif gear == "scout":
            state.phase = ScoringPhase.ALIGN_JUNCTION
        else:
            state.phase = ScoringPhase.GET_GEAR

        # ---- Policy modulation based on team beta ----
        # High team_beta: coordinate — miners go to extractors near teammates,
        #   aligners prioritise junctions.
        # Low team_beta: go solo — miners avoid teammates, aligners get hearts first.
        # Middle: default scoring loop.

        if state.phase == ScoringPhase.GET_GEAR:
            target_tags = self._gear_station_tags_by_gear.get(state.assigned_role, self._gear_station_tags)
            return self._navigate_to(obs, state, target_tags)

        if state.phase == ScoringPhase.MINE_ORE:
            return self._navigate_to(obs, state, self._extractor_tags)

        if state.phase == ScoringPhase.DEPOSIT:
            return self._navigate_to(obs, state, self._heart_source_tags)

        if state.phase == ScoringPhase.ALIGN_JUNCTION:
            if state.team_beta_ema > COOPERATE_THRESHOLD:
                # High coordination: go straight for junctions (teammates are reliable)
                return self._navigate_to(obs, state, self._junction_tags)
            elif state.team_beta_ema < INDEPENDENT_THRESHOLD:
                # Low coordination: ensure we have hearts before attempting junctions
                if not has_heart:
                    return self._navigate_to(obs, state, self._heart_source_tags)
                return self._navigate_to(obs, state, self._junction_tags)
            else:
                return self._navigate_to(obs, state, self._junction_tags)

        state.nav.last_action_name = self._fallback_action_name
        return self._action(self._fallback_action_name), state

    def initial_agent_state(self) -> AffectScoringState:
        role = ROLE_PLAN[self._agent_id % len(ROLE_PLAN)]
        return AffectScoringState(
            assigned_role=role,
            nav=self._nav.initial_state(),
        )


class AffectCvCPolicy(MultiAgentPolicy):
    """Affect-augmented CvC policy with per-teammate precision tracking."""

    short_names = ["affect_cvc", "affect"]

    def __init__(self, policy_env_info: PolicyEnvInterface, device: str = "cpu"):
        super().__init__(policy_env_info, device=device)
        self._agent_policies: dict[int, StatefulAgentPolicy[AffectScoringState]] = {}

    def agent_policy(self, agent_id: int) -> StatefulAgentPolicy[AffectScoringState]:
        if agent_id not in self._agent_policies:
            self._agent_policies[agent_id] = StatefulAgentPolicy(
                AffectCvCPolicyImpl(self._policy_env_info, agent_id),
                self._policy_env_info,
                agent_id=agent_id,
            )
        return self._agent_policies[agent_id]
