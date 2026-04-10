"""Submission-shaped local CvC policy that tracks teammate reliability."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from mettagrid.policy.policy import MultiAgentPolicy, StatefulAgentPolicy, StatefulPolicyImpl
from mettagrid.policy.policy_env_interface import PolicyEnvInterface
from mettagrid.simulator import Action
from mettagrid.simulator.interface import AgentObservation

from affect_aif.benchmark.cvc_navigation import NavigationHelper, NavigationState

GEAR = ("aligner", "scrambler", "miner", "scout")
ELEMENTS = ("carbon", "oxygen", "germanium", "silicon")
WANDER_DIRECTIONS = ("east", "south", "west", "north")
WANDER_STEPS = 8


@dataclass
class ReliabilityCogState:
    wander_direction_index: int = 0
    wander_steps_remaining: int = WANDER_STEPS
    nav: NavigationState = field(default_factory=NavigationState)


class TeamReliabilityCoordinator:
    """Shared per-teammate reliability table used for role allocation."""

    BASE_ROLE_PLAN = ("miner", "miner", "miner", "aligner", "aligner", "scrambler", "scout", "miner")

    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.reliability = {agent_id: 0.5 for agent_id in range(num_agents)}

    def update(self, agent_id: int, reward_signal: float, moved: bool) -> None:
        target = 0.5
        target += 0.15 if moved else -0.10
        if reward_signal > 0:
            target += min(reward_signal, 1.0) * 0.20
        elif reward_signal == 0:
            target -= 0.05
        target = max(0.05, min(0.95, target))
        self.reliability[agent_id] = 0.85 * self.reliability[agent_id] + 0.15 * target

    def desired_role(self, agent_id: int, episode_pct: float) -> str:
        role = self.BASE_ROLE_PLAN[agent_id % len(self.BASE_ROLE_PLAN)]
        reliability = self.reliability.get(agent_id, 0.5)

        if episode_pct >= 0.55 and role == "miner" and reliability >= 0.55 and agent_id % 3 == 0:
            role = "aligner"
        if episode_pct >= 0.75 and role in {"miner", "aligner"} and reliability >= 0.60 and agent_id % 5 == 0:
            role = "scrambler"
        if reliability < 0.35 and role in {"aligner", "scrambler"}:
            role = "miner"
        return role


class TeammateReliabilityPolicyImpl(StatefulPolicyImpl[ReliabilityCogState]):
    """Rule-based local policy with shared teammate reliability tracking."""

    def __init__(self, policy_env_info: PolicyEnvInterface, agent_id: int, coordinator: TeamReliabilityCoordinator):
        self._agent_id = agent_id
        self._policy_env_info = policy_env_info
        self._coordinator = coordinator

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
            items[item_name] = items.get(item_name, 0) + value * (base**power)
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

    def _action(self, name: str) -> Action:
        if name in self._action_name_set:
            return Action(name=name)
        return Action(name=self._fallback_action_name)

    def _wander(self, state: ReliabilityCogState) -> tuple[Action, ReliabilityCogState]:
        if state.wander_steps_remaining <= 0:
            state.wander_direction_index = (state.wander_direction_index + 1) % len(WANDER_DIRECTIONS)
            state.wander_steps_remaining = WANDER_STEPS
        direction = WANDER_DIRECTIONS[state.wander_direction_index]
        state.wander_steps_remaining -= 1
        return self._action(f"move_{direction}"), state

    def _move_toward(
        self,
        state: ReliabilityCogState,
        target: Optional[tuple[int, int]],
    ) -> tuple[Action, ReliabilityCogState]:
        if target is None:
            return self._wander(state)
        delta_row = target[0] - self._center[0]
        delta_col = target[1] - self._center[1]
        if delta_row == 0 and delta_col == 0:
            return self._action(self._fallback_action_name), state
        if abs(delta_row) >= abs(delta_col):
            direction = "south" if delta_row > 0 else "north"
        else:
            direction = "east" if delta_col > 0 else "west"
        return self._action(f"move_{direction}"), state

    def _current_gear(self, items: dict[str, int]) -> Optional[str]:
        for gear in GEAR:
            if items.get(gear, 0) > 0:
                return gear
        return None

    def step_with_state(self, obs: AgentObservation, state: ReliabilityCogState) -> tuple[Action, ReliabilityCogState]:
        items = self._inventory_amounts(obs)
        reward_signal = self._global_value(obs, "last_reward", default=0.0)
        moved = self._global_value(obs, "last_action_move", default=0.0) > 0.0
        episode_pct = self._global_value(obs, "episode_completion_pct", default=0.0)
        self._coordinator.update(self._agent_id, reward_signal=reward_signal, moved=moved)

        # Update navigation state from movement result
        state.nav = self._nav.update_position(state.nav, moved)

        desired_role = self._coordinator.desired_role(self._agent_id, episode_pct=episode_pct)
        gear = self._current_gear(items)
        cargo = sum(items.get(element, 0) for element in ELEMENTS)
        has_heart = items.get("heart", 0) > 0

        if gear != desired_role:
            target_tags = self._gear_station_tags_by_gear.get(desired_role, self._gear_station_tags)
        elif gear == "miner":
            target_tags = self._heart_source_tags if cargo >= 12 else self._extractor_tags
        elif gear == "aligner":
            target_tags = self._junction_tags if has_heart else self._heart_source_tags
        elif gear == "scrambler":
            target_tags = self._junction_tags if has_heart else self._heart_source_tags
        elif gear == "scout":
            target_tags = self._junction_tags
        else:
            target_tags = self._gear_station_tags_by_gear.get(desired_role, self._gear_station_tags)

        target_location = self._closest_tag_location(obs, target_tags)

        # Try BFS pathfinding first
        action_name = self._nav.pathfind_toward(obs, state.nav, target_location)

        # Fall back to exploration if no path or no target
        if action_name is None:
            action_name = self._nav.explore_action(obs, state.nav)

        # Fall back to greedy movement if pathfinding/exploration both fail
        if action_name is None:
            action, state = self._move_toward(state, target_location)
            state.nav.last_action_name = action.name if hasattr(action, "name") else None
            return action, state

        state.nav.last_action_name = action_name
        return self._action(action_name), state

    def initial_agent_state(self) -> ReliabilityCogState:
        return ReliabilityCogState(
            wander_direction_index=self._agent_id % len(WANDER_DIRECTIONS),
            nav=self._nav.initial_state(),
        )


class TeammateReliabilityPolicy(MultiAgentPolicy):
    """Local CvC policy with shared teammate reliability tracking."""

    short_names = ["teammate_reliability", "reliability"]

    def __init__(self, policy_env_info: PolicyEnvInterface, device: str = "cpu"):
        super().__init__(policy_env_info, device=device)
        self._coordinator = TeamReliabilityCoordinator(policy_env_info.num_agents)
        self._agent_policies: dict[int, StatefulAgentPolicy[ReliabilityCogState]] = {}

    def agent_policy(self, agent_id: int) -> StatefulAgentPolicy[ReliabilityCogState]:
        if agent_id not in self._agent_policies:
            self._agent_policies[agent_id] = StatefulAgentPolicy(
                TeammateReliabilityPolicyImpl(self._policy_env_info, agent_id, self._coordinator),
                self._policy_env_info,
                agent_id=agent_id,
            )
        return self._agent_policies[agent_id]
