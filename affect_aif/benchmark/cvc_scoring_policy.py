"""State-machine CvC policy that completes the scoring loop.

Implements the full CvC scoring sequence:
  1. Get gear (navigate to gear station)
  2. Mine ore (navigate to extractor, proximity-interact)
  3. Deposit at base (navigate to hub/chest, trade ore for hearts)
  4. Align junction (navigate to junction with heart)

Uses BFS pathfinding from cvc_navigation.py for wall avoidance.
Designed as the baseline policy for measuring the affect mechanism's
contribution in CvC.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Iterable, Optional

from mettagrid.policy.policy import MultiAgentPolicy, StatefulAgentPolicy, StatefulPolicyImpl
from mettagrid.policy.policy_env_interface import PolicyEnvInterface
from mettagrid.simulator import Action
from mettagrid.simulator.interface import AgentObservation

from affect_aif.benchmark.cvc_navigation import NavigationHelper, NavigationState

GEAR = ("aligner", "scrambler", "miner", "scout")
ELEMENTS = ("carbon", "oxygen", "germanium", "silicon")


class ScoringPhase(Enum):
    GET_GEAR = auto()
    MINE_ORE = auto()
    DEPOSIT = auto()
    ALIGN_JUNCTION = auto()


# Role assignment pattern for 8 agents: mostly miners + aligners
ROLE_PLAN = ("miner", "miner", "miner", "aligner", "aligner", "miner", "miner", "aligner")

# How much ore to collect before depositing
CARGO_THRESHOLD = 8


@dataclass
class ScoringState:
    phase: ScoringPhase = ScoringPhase.GET_GEAR
    assigned_role: str = "miner"
    nav: NavigationState = field(default_factory=NavigationState)
    stuck_steps: int = 0


class ScoringLoopPolicyImpl(StatefulPolicyImpl[ScoringState]):
    """State-machine policy that follows the CvC scoring loop with BFS navigation."""

    def __init__(self, policy_env_info: PolicyEnvInterface, agent_id: int):
        self._agent_id = agent_id
        self._policy_env_info = policy_env_info

        self._action_names = policy_env_info.action_names
        self._action_name_set = set(self._action_names)
        self._fallback_action_name = "noop" if "noop" in self._action_name_set else self._action_names[0]
        self._center = (policy_env_info.obs_height // 2, policy_env_info.obs_width // 2)
        self._nav = NavigationHelper(policy_env_info.obs_height, policy_env_info.obs_width, self._center)

        self._tag_name_to_id = {name: idx for idx, name in enumerate(policy_env_info.tags)}
        self._gear_station_tags_by_gear = {gear: self._resolve_tag_ids([f"c:{gear}"]) for gear in GEAR}
        self._gear_station_tags = set().union(*self._gear_station_tags_by_gear.values())
        self._extractor_tags = self._resolve_tag_ids([f"{element}_extractor" for element in ELEMENTS])
        self._junction_tags = self._resolve_tag_ids(["junction"])
        self._heart_source_tags = self._resolve_tag_ids(["hub", "chest"])

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

    def _navigate_to(self, obs: AgentObservation, state: ScoringState, tag_ids: set[int]) -> tuple[Action, ScoringState]:
        """Navigate toward the closest entity matching tag_ids."""
        target = self._closest_tag_location(obs, tag_ids)
        action_name = self._nav.pathfind_toward(obs, state.nav, target)

        if action_name is None:
            action_name = self._nav.explore_action(obs, state.nav)

        if action_name is None:
            action_name = self._fallback_action_name

        state.nav.last_action_name = action_name
        return self._action(action_name), state

    def step_with_state(self, obs: AgentObservation, state: ScoringState) -> tuple[Action, ScoringState]:
        items = self._inventory_amounts(obs)
        moved = self._global_value(obs, "last_action_move", default=0.0) > 0.0

        # Update navigation state
        state.nav = self._nav.update_position(state.nav, moved)

        gear = self._current_gear(items)
        cargo = sum(items.get(element, 0) for element in ELEMENTS)
        has_heart = items.get("heart", 0) > 0

        # Track stuck-ness for phase transitions
        if not moved and state.nav.last_action_name is not None:
            state.stuck_steps += 1
        else:
            state.stuck_steps = 0

        # State machine: determine phase based on actual inventory
        if gear is None:
            state.phase = ScoringPhase.GET_GEAR
        elif gear == "miner":
            if cargo >= CARGO_THRESHOLD:
                state.phase = ScoringPhase.DEPOSIT
            else:
                state.phase = ScoringPhase.MINE_ORE
        elif gear in ("aligner", "scrambler"):
            if has_heart:
                state.phase = ScoringPhase.ALIGN_JUNCTION
            else:
                state.phase = ScoringPhase.DEPOSIT  # go get hearts
        elif gear == "scout":
            state.phase = ScoringPhase.ALIGN_JUNCTION  # scouts explore junctions
        else:
            state.phase = ScoringPhase.GET_GEAR

        # Execute phase
        if state.phase == ScoringPhase.GET_GEAR:
            target_tags = self._gear_station_tags_by_gear.get(state.assigned_role, self._gear_station_tags)
            return self._navigate_to(obs, state, target_tags)

        elif state.phase == ScoringPhase.MINE_ORE:
            return self._navigate_to(obs, state, self._extractor_tags)

        elif state.phase == ScoringPhase.DEPOSIT:
            return self._navigate_to(obs, state, self._heart_source_tags)

        elif state.phase == ScoringPhase.ALIGN_JUNCTION:
            return self._navigate_to(obs, state, self._junction_tags)

        # Should not reach here
        state.nav.last_action_name = self._fallback_action_name
        return self._action(self._fallback_action_name), state

    def initial_agent_state(self) -> ScoringState:
        role = ROLE_PLAN[self._agent_id % len(ROLE_PLAN)]
        return ScoringState(
            assigned_role=role,
            nav=self._nav.initial_state(),
        )


class ScoringLoopPolicy(MultiAgentPolicy):
    """State-machine CvC policy that completes the scoring loop with BFS navigation."""

    short_names = ["scoring_loop", "scoring"]

    def __init__(self, policy_env_info: PolicyEnvInterface, device: str = "cpu"):
        super().__init__(policy_env_info, device=device)
        self._agent_policies: dict[int, StatefulAgentPolicy[ScoringState]] = {}

    def agent_policy(self, agent_id: int) -> StatefulAgentPolicy[ScoringState]:
        if agent_id not in self._agent_policies:
            self._agent_policies[agent_id] = StatefulAgentPolicy(
                ScoringLoopPolicyImpl(self._policy_env_info, agent_id),
                self._policy_env_info,
                agent_id=agent_id,
            )
        return self._agent_policies[agent_id]
