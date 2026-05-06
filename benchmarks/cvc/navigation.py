"""BFS pathfinding for CvC grid observations.

Maintains a global wall map learned from movement failures and uses BFS
to navigate around obstacles. Designed to replace the greedy directional
heuristic in CvC policies.

The observation format (mettagrid AgentObservation) provides a local grid
centered on the agent. Target entities appear as tokens with feature.name
== "tag". Walkable cells are identified by the presence of an "aoe_mask"
token — cells without aoe_mask are walls or outside the field of view.
Movement failures are also tracked to learn walls beyond the current view.

Usage:
    # In policy __init__:
    self._nav = NavigationHelper(obs_height, obs_width, center)

    # In step_with_state:
    nav_state = self._nav.update_position(nav_state, moved)
    action_name = self._nav.pathfind_toward(obs, nav_state, target_loc)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

# Cardinal directions: (delta_row, delta_col, action_name)
DIRECTIONS = [
    (-1, 0, "move_north"),
    (1, 0, "move_south"),
    (0, 1, "move_east"),
    (0, -1, "move_west"),
]

DIR_NAME_TO_DELTA: dict[str, tuple[int, int]] = {
    "move_north": (-1, 0),
    "move_south": (1, 0),
    "move_east": (0, 1),
    "move_west": (0, -1),
}

# Feature name that indicates a walkable cell in mettagrid observations.
# Cells WITH aoe_mask are passable; cells WITHOUT are walls/out-of-view.
AOE_MASK_FEATURE: str = "aoe_mask"

# Movement-failure walls expire after this many steps (handles agent-blocking)
WALL_EXPIRY_STEPS: int = 15


@dataclass
class NavigationState:
    """Persistent navigation state across steps."""

    global_row: int = 0
    global_col: int = 0
    last_action_name: str | None = None
    walls: dict[tuple[int, int], int] = field(default_factory=dict)  # coord -> step_added
    visited: set[tuple[int, int]] = field(default_factory=set)
    step_count: int = 0


class NavigationHelper:
    """BFS pathfinding using movement-failure wall learning."""

    def __init__(self, obs_height: int, obs_width: int, center: tuple[int, int]):
        self._obs_height = obs_height
        self._obs_width = obs_width
        self._center = center

    def initial_state(self) -> NavigationState:
        state = NavigationState()
        state.visited.add((0, 0))
        return state

    def update_position(
        self,
        state: NavigationState,
        moved: bool,
    ) -> NavigationState:
        """Update global position and wall map from movement result."""
        state.step_count += 1

        # Expire stale movement-failure walls (handles agent-blocking)
        if state.walls:
            cutoff = state.step_count - WALL_EXPIRY_STEPS
            state.walls = {k: v for k, v in state.walls.items() if v > cutoff}

        if state.last_action_name is None:
            return state

        delta = DIR_NAME_TO_DELTA.get(state.last_action_name)
        if delta is None:
            return state

        target_r = state.global_row + delta[0]
        target_c = state.global_col + delta[1]

        if moved:
            state.global_row = target_r
            state.global_col = target_c
            state.visited.add((target_r, target_c))
            # If we successfully moved to a cell, it's not a wall
            state.walls.pop((target_r, target_c), None)
        else:
            state.walls[(target_r, target_c)] = state.step_count

        return state

    def _detect_walkable_cells(self, obs) -> set[tuple[int, int]]:
        """Detect walkable cells from aoe_mask feature.

        In mettagrid, cells with aoe_mask=1 are visible/passable.
        Cells without aoe_mask are walls or outside the field of view.
        Returns set of LOCAL grid positions that are walkable.
        """
        walkable: set[tuple[int, int]] = set()
        for token in obs.tokens:
            if token.feature.name == AOE_MASK_FEATURE and token.location is not None:
                walkable.add((token.location[0], token.location[1]))
        return walkable

    def _local_to_global(self, local_row: int, local_col: int, state: NavigationState) -> tuple[int, int]:
        """Convert local observation coords to global coords."""
        return (
            state.global_row + local_row - self._center[0],
            state.global_col + local_col - self._center[1],
        )

    def _global_to_local(self, global_row: int, global_col: int, state: NavigationState) -> tuple[int, int]:
        """Convert global coords to local observation coords."""
        return (
            global_row - state.global_row + self._center[0],
            global_col - state.global_col + self._center[1],
        )

    def _is_in_local_grid(self, row: int, col: int) -> bool:
        return 0 <= row < self._obs_height and 0 <= col < self._obs_width

    def _build_local_walkability(self, obs, state: NavigationState) -> list[list[bool]]:
        """Build a walkability grid for the local observation area.

        Cells are walkable if they have an aoe_mask token AND are not in
        the known global wall map. In mettagrid, walls and out-of-view
        cells simply lack the aoe_mask feature — they are never explicitly
        encoded as wall tokens.
        """
        # Start with all cells unwalkable
        grid = [[False] * self._obs_width for _ in range(self._obs_height)]

        # Mark cells with aoe_mask as walkable
        walkable = self._detect_walkable_cells(obs)
        for r, c in walkable:
            if self._is_in_local_grid(r, c):
                grid[r][c] = True

        # Override with known global walls (from movement failures)
        for r in range(self._obs_height):
            for c in range(self._obs_width):
                gr, gc = self._local_to_global(r, c, state)
                if (gr, gc) in state.walls:
                    grid[r][c] = False

        return grid

    def _bfs(
        self,
        grid: list[list[bool]],
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        """BFS from start to goal on the local walkability grid."""
        if not self._is_in_local_grid(goal[0], goal[1]):
            return None
        if not grid[start[0]][start[1]] or not grid[goal[0]][goal[1]]:
            return None

        visited: set[tuple[int, int]] = {start}
        queue: deque[tuple[tuple[int, int], list[tuple[int, int]]]] = deque()
        queue.append((start, [start]))

        while queue:
            (r, c), path = queue.popleft()
            if (r, c) == goal:
                return path
            for dr, dc, _ in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if self._is_in_local_grid(nr, nc) and (nr, nc) not in visited and grid[nr][nc]:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))

        return None

    def _bfs_toward_direction(
        self,
        grid: list[list[bool]],
        start: tuple[int, int],
        target_dr: int,
        target_dc: int,
    ) -> str | None:
        """BFS to find a path that makes progress toward an off-screen target.

        When the target is outside the visible grid, find the reachable edge
        cell closest to the target direction and navigate there.
        """
        # Find the best edge cell in the target direction
        best_score = float("-inf")

        visited: set[tuple[int, int]] = {start}
        queue: deque[tuple[tuple[int, int], list[tuple[int, int]]]] = deque()
        queue.append((start, [start]))
        best_path: list[tuple[int, int]] | None = None

        while queue:
            (r, c), path = queue.popleft()
            # Score: how much progress toward the target direction
            score = (r - start[0]) * target_dr + (c - start[1]) * target_dc
            # Prefer edge cells
            is_edge = r == 0 or r == self._obs_height - 1 or c == 0 or c == self._obs_width - 1
            if is_edge and score > best_score:
                best_score = score
                best_path = path

            for dr, dc, _ in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if self._is_in_local_grid(nr, nc) and (nr, nc) not in visited and grid[nr][nc]:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))

        if best_path is None or len(best_path) < 2:
            return None

        next_cell = best_path[1]
        dr = next_cell[0] - start[0]
        dc = next_cell[1] - start[1]
        for ddr, ddc, action_name in DIRECTIONS:
            if ddr == dr and ddc == dc:
                return action_name
        return None

    def pathfind_toward(
        self,
        obs,
        state: NavigationState,
        target_local: tuple[int, int] | None,
    ) -> str | None:
        """Find the next move action toward a target using BFS.

        Args:
            obs: The agent's observation
            state: Navigation state (will be mutated with new wall info)
            target_local: Target position in local observation coords, or None

        Returns:
            Action name (e.g., "move_north") or None if no path found.
        """
        if target_local is None:
            return None

        grid = self._build_local_walkability(obs, state)

        # If target is within local grid, BFS directly
        if self._is_in_local_grid(target_local[0], target_local[1]):
            path = self._bfs(grid, self._center, target_local)
            if path is not None and len(path) >= 2:
                next_cell = path[1]
                dr = next_cell[0] - self._center[0]
                dc = next_cell[1] - self._center[1]
                for ddr, ddc, action_name in DIRECTIONS:
                    if ddr == dr and ddc == dc:
                        return action_name

        # Target is outside local grid or no path found — navigate toward it
        target_dr = 1 if target_local[0] > self._center[0] else (-1 if target_local[0] < self._center[0] else 0)
        target_dc = 1 if target_local[1] > self._center[1] else (-1 if target_local[1] < self._center[1] else 0)

        return self._bfs_toward_direction(grid, self._center, target_dr, target_dc)

    def explore_action(
        self,
        obs,
        state: NavigationState,
    ) -> str | None:
        """Choose a move that explores unvisited cells."""
        grid = self._build_local_walkability(obs, state)

        # BFS from center, find nearest unvisited reachable cell
        visited_bfs: set[tuple[int, int]] = {self._center}
        queue: deque[tuple[tuple[int, int], list[tuple[int, int]]]] = deque()
        queue.append((self._center, [self._center]))

        while queue:
            (r, c), path = queue.popleft()
            gr, gc = self._local_to_global(r, c, state)
            if (gr, gc) not in state.visited and len(path) >= 2:
                next_cell = path[1]
                dr = next_cell[0] - self._center[0]
                dc = next_cell[1] - self._center[1]
                for ddr, ddc, action_name in DIRECTIONS:
                    if ddr == dr and ddc == dc:
                        return action_name

            for dr, dc, _ in DIRECTIONS:
                nr, nc = r + dr, c + dc
                if self._is_in_local_grid(nr, nc) and (nr, nc) not in visited_bfs and grid[nr][nc]:
                    visited_bfs.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))

        # All visible cells visited — pick a random walkable direction
        for dr, dc, action_name in DIRECTIONS:
            nr, nc = self._center[0] + dr, self._center[1] + dc
            if self._is_in_local_grid(nr, nc) and grid[nr][nc]:
                return action_name
        return None
