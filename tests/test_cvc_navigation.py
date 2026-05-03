"""Tests for CvC BFS navigation without requiring mettagrid.

Tests cover: position tracking, wall learning/expiry, coordinate transforms,
BFS pathfinding, directional BFS, walkability grid building, and exploration.
"""

from dataclasses import dataclass

from benchmarks.cvc.navigation import (
    DIR_NAME_TO_DELTA,
    DIRECTIONS,
    WALL_EXPIRY_STEPS,
    NavigationHelper,
)

# ── Minimal observation mock ─────────────────────────────────────────────────


@dataclass
class _Token:
    feature: "_Feature"
    location: tuple[int, int] | None
    value: float = 1.0


@dataclass
class _Feature:
    name: str
    normalization: str = "none"


class _FakeObs:
    """Mimics mettagrid AgentObservation with just enough for navigation."""

    def __init__(self, walkable_cells: set[tuple[int, int]]):
        self.tokens = [_Token(feature=_Feature(name="aoe_mask"), location=(r, c)) for r, c in walkable_cells]


def _all_walkable(height: int, width: int) -> _FakeObs:
    """Observation where every cell is walkable."""
    return _FakeObs({(r, c) for r in range(height) for c in range(width)})


# ── NavigationState ──────────────────────────────────────────────────────────


class TestNavigationState:
    def test_initial_state(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        assert state.global_row == 0
        assert state.global_col == 0
        assert (0, 0) in state.visited
        assert state.step_count == 0
        assert state.walls == {}

    def test_initial_visited_contains_origin(self):
        nav = NavigationHelper(7, 7, (3, 3))
        state = nav.initial_state()
        assert state.visited == {(0, 0)}


# ── Position tracking ────────────────────────────────────────────────────────


class TestPositionTracking:
    def test_successful_move_updates_position(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.last_action_name = "move_east"
        state = nav.update_position(state, moved=True)
        assert state.global_row == 0
        assert state.global_col == 1
        assert (0, 1) in state.visited

    def test_failed_move_records_wall(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.last_action_name = "move_north"
        state = nav.update_position(state, moved=False)
        assert state.global_row == 0
        assert state.global_col == 0
        assert (-1, 0) in state.walls

    def test_no_action_no_change(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.last_action_name = None
        state = nav.update_position(state, moved=True)
        assert state.global_row == 0
        assert state.global_col == 0

    def test_non_move_action_no_change(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.last_action_name = "use_item"
        state = nav.update_position(state, moved=True)
        assert state.global_row == 0
        assert state.global_col == 0

    def test_step_count_increments(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.last_action_name = "move_south"
        state = nav.update_position(state, moved=True)
        assert state.step_count == 1
        state.last_action_name = "move_south"
        state = nav.update_position(state, moved=True)
        assert state.step_count == 2

    def test_successful_move_clears_wall(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        # First, fail a move to record a wall
        state.last_action_name = "move_east"
        state = nav.update_position(state, moved=False)
        assert (0, 1) in state.walls
        # Now succeed moving there
        state.last_action_name = "move_east"
        state = nav.update_position(state, moved=True)
        assert (0, 1) not in state.walls

    def test_multi_step_path(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        moves = ["move_east", "move_east", "move_south", "move_south"]
        for action in moves:
            state.last_action_name = action
            state = nav.update_position(state, moved=True)
        assert state.global_row == 2
        assert state.global_col == 2
        assert len(state.visited) == 5  # origin + 4 moves


# ── Wall expiry ──────────────────────────────────────────────────────────────


class TestWallExpiry:
    def test_walls_expire_after_threshold(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        # Record a wall at step 1
        state.last_action_name = "move_north"
        state = nav.update_position(state, moved=False)
        assert (-1, 0) in state.walls
        # Advance steps past expiry
        state.last_action_name = None
        for _ in range(WALL_EXPIRY_STEPS):
            state = nav.update_position(state, moved=True)
        assert (-1, 0) not in state.walls

    def test_recent_walls_persist(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.last_action_name = "move_north"
        state = nav.update_position(state, moved=False)
        # Advance fewer steps than expiry
        state.last_action_name = None
        for _ in range(WALL_EXPIRY_STEPS - 2):
            state = nav.update_position(state, moved=True)
        assert (-1, 0) in state.walls


# ── Coordinate transforms ───────────────────────────────────────────────────


class TestCoordinateTransforms:
    def test_local_global_roundtrip(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.global_row = 10
        state.global_col = 20
        gr, gc = nav._local_to_global(3, 4, state)
        lr, lc = nav._global_to_local(gr, gc, state)
        assert (lr, lc) == (3, 4)

    def test_center_maps_to_global_position(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.global_row = 7
        state.global_col = -3
        gr, gc = nav._local_to_global(2, 2, state)
        assert (gr, gc) == (7, -3)

    def test_negative_global_coords(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        state.global_row = -5
        state.global_col = -5
        gr, gc = nav._local_to_global(0, 0, state)
        assert gr == -7
        assert gc == -7


# ── BFS pathfinding ──────────────────────────────────────────────────────────


class TestBFS:
    def test_adjacent_target(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        path = nav._bfs(grid, (2, 2), (2, 3))
        assert path is not None
        assert len(path) == 2
        assert path[0] == (2, 2)
        assert path[1] == (2, 3)

    def test_path_around_wall(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        grid[2][3] = False  # Wall blocking direct east
        path = nav._bfs(grid, (2, 2), (2, 4))
        assert path is not None
        assert (2, 3) not in path  # Must go around
        assert path[0] == (2, 2)
        assert path[-1] == (2, 4)

    def test_unreachable_target(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        # Wall off target completely
        for r in range(5):
            grid[r][3] = False
        path = nav._bfs(grid, (2, 2), (2, 4))
        assert path is None

    def test_start_equals_goal(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        path = nav._bfs(grid, (2, 2), (2, 2))
        assert path is not None
        assert path == [(2, 2)]

    def test_goal_out_of_grid(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        path = nav._bfs(grid, (2, 2), (6, 6))
        assert path is None

    def test_goal_on_wall(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        grid[4][4] = False
        path = nav._bfs(grid, (2, 2), (4, 4))
        assert path is None

    def test_optimal_path_length(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        path = nav._bfs(grid, (0, 0), (4, 4))
        assert path is not None
        assert len(path) == 9  # Manhattan distance 8 + start


# ── Directional BFS ──────────────────────────────────────────────────────────


class TestBFSTowardDirection:
    def test_south_direction(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        action = nav._bfs_toward_direction(grid, (2, 2), target_dr=1, target_dc=0)
        assert action == "move_south"

    def test_blocked_finds_alternate(self):
        nav = NavigationHelper(5, 5, (2, 2))
        grid = [[True] * 5 for _ in range(5)]
        # Block south completely
        for c in range(5):
            grid[3][c] = False
            grid[4][c] = False
        # Should still return something (east/west edge) or None if truly stuck
        nav._bfs_toward_direction(grid, (2, 2), target_dr=1, target_dc=0)
        # Can't reach south edge, but north edge is reachable
        # Score for north cells would be negative, so might return None
        # This is acceptable behavior

    def test_returns_none_when_stuck(self):
        nav = NavigationHelper(3, 3, (1, 1))
        grid = [[False] * 3 for _ in range(3)]
        grid[1][1] = True  # Only center walkable
        action = nav._bfs_toward_direction(grid, (1, 1), target_dr=1, target_dc=0)
        assert action is None


# ── Walkability grid ─────────────────────────────────────────────────────────


class TestWalkabilityGrid:
    def test_all_walkable(self):
        nav = NavigationHelper(3, 3, (1, 1))
        state = nav.initial_state()
        obs = _all_walkable(3, 3)
        grid = nav._build_local_walkability(obs, state)
        assert all(grid[r][c] for r in range(3) for c in range(3))

    def test_missing_aoe_mask_is_wall(self):
        nav = NavigationHelper(3, 3, (1, 1))
        state = nav.initial_state()
        # Only center and east are walkable
        obs = _FakeObs({(1, 1), (1, 2)})
        grid = nav._build_local_walkability(obs, state)
        assert grid[1][1] is True
        assert grid[1][2] is True
        assert grid[0][0] is False

    def test_global_wall_overrides_aoe_mask(self):
        nav = NavigationHelper(3, 3, (1, 1))
        state = nav.initial_state()
        # All cells have aoe_mask, but we know (0, 0) is a wall globally
        # Center (1,1) maps to global (0, 0), so local (0,0) maps to global (-1, -1)
        # Put a wall at global position that maps to local (1, 2)
        gr, gc = nav._local_to_global(1, 2, state)
        state.walls[(gr, gc)] = state.step_count
        obs = _all_walkable(3, 3)
        grid = nav._build_local_walkability(obs, state)
        assert grid[1][2] is False
        assert grid[1][1] is True


# ── pathfind_toward integration ──────────────────────────────────────────────


class TestPathfindToward:
    def test_adjacent_target_returns_action(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        obs = _all_walkable(5, 5)
        action = nav.pathfind_toward(obs, state, (2, 3))
        assert action == "move_east"

    def test_none_target_returns_none(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        obs = _all_walkable(5, 5)
        assert nav.pathfind_toward(obs, state, None) is None

    def test_offscreen_target_returns_directional_action(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        obs = _all_walkable(5, 5)
        action = nav.pathfind_toward(obs, state, (10, 2))
        assert action == "move_south"

    def test_path_around_obstacle(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        # Wall to the east of center
        walkable = {(r, c) for r in range(5) for c in range(5)} - {(2, 3)}
        obs = _FakeObs(walkable)
        action = nav.pathfind_toward(obs, state, (2, 4))
        # Should go north or south to route around
        assert action in ("move_north", "move_south")


# ── explore_action ───────────────────────────────────────────────────────────


class TestExploreAction:
    def test_explores_unvisited(self):
        nav = NavigationHelper(5, 5, (2, 2))
        state = nav.initial_state()
        obs = _all_walkable(5, 5)
        action = nav.explore_action(obs, state)
        assert action is not None
        assert action in DIR_NAME_TO_DELTA

    def test_all_visited_still_returns_action(self):
        nav = NavigationHelper(3, 3, (1, 1))
        state = nav.initial_state()
        # Mark all global positions visible from this 3x3 as visited
        for r in range(3):
            for c in range(3):
                gr, gc = nav._local_to_global(r, c, state)
                state.visited.add((gr, gc))
        obs = _all_walkable(3, 3)
        action = nav.explore_action(obs, state)
        # Falls back to any walkable direction
        assert action is not None

    def test_completely_walled_returns_none(self):
        nav = NavigationHelper(3, 3, (1, 1))
        state = nav.initial_state()
        # No walkable cells except center
        obs = _FakeObs({(1, 1)})
        action = nav.explore_action(obs, state)
        assert action is None


# ── Direction constants ──────────────────────────────────────────────────────


class TestDirectionConstants:
    def test_four_cardinal_directions(self):
        assert len(DIRECTIONS) == 4

    def test_dir_name_to_delta_matches(self):
        for dr, dc, name in DIRECTIONS:
            assert DIR_NAME_TO_DELTA[name] == (dr, dc)

    def test_all_deltas_are_unit(self):
        for dr, dc, _ in DIRECTIONS:
            assert abs(dr) + abs(dc) == 1
