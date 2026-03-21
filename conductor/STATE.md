# Research State

## Last Updated
2026-03-21

## Session Count
6

## Current Findings

### Trust-Game Results (Phases 1-7: COMPLETE)

All trust-game phases are complete with publication-quality results:
- Orthogonal augmentation confirmed across binary and graded games
- Clinical sensitivity validated in graded betrayal environment
- Bayesian model comparison shows C2 decisive under volatility
- Cross-game generalization across PD, Stag Hunt, Chicken
- Full results in docs/results_tracking.md

### CoGames/CvC Benchmark Integration (IN PROGRESS)

**Pipeline status: COMPLETE.** The full CvC benchmark pipeline runs end-to-end:
- Python 3.10 orchestrator dispatches to Python 3.12 worker subprocess
- Worker imports cogames/mettagrid, resolves mission, runs episode, extracts metrics
- Results flow back as JSON -> DataFrame -> CSV -> comparison report
- All 178 tests pass including CvC backend mock tests

**Benchmark run completed (2026-03-21):** 6 policies x 10 seeds x 10,000 steps = 60 episodes on machina_1 mission.

| Policy | Type | Hearts | Aligned Junctions | Reward |
|--------|------|--------|-------------------|--------|
| TeammateReliabilityPolicy | custom | 6.7 | 0.0 | 0.0 |
| StarterPolicy | cogames built-in | 7.0 | 0.0 | 0.0 |
| MinerRolePolicy | cogames built-in | 6.9 | 0.0 | 0.0 |
| AlignerRolePolicy | cogames built-in | 7.1 | 0.0 | 0.0 |
| ScramblerRolePolicy | cogames built-in | 7.1 | 0.0 | 0.0 |
| ScoutRolePolicy | cogames built-in | 6.9 | 0.0 | 0.0 |

**Blocker: All policies score 0 reward and 0 aligned junctions.** The CvC scoring loop (get gear -> mine -> deposit -> get hearts -> align junction) requires effective navigation, but all rule-based policies have ~80% failed moves (walking into walls). The machina_1 map has complex wall layouts that simple directional heuristics cannot handle.

**Diagnosis:**
- CvC has only 5 actions (noop, move_north/south/east/west); all interaction is proximity-based
- Scoring requires: navigate to gear -> mine ore -> deposit at base -> collect hearts -> align junction
- Simple "move toward nearest tag" heuristic fails because it walks into walls
- This affects ALL policies including cogames' own built-in ones — it's a fundamental limitation of rule-based navigation in this map

### Known Gaps / Next Steps
1. **Primary goal: AIF affect policy for CvC.** Adapt our generative model + per-partner precision tracking to the CvC domain. This is the main deliverable — showing our AIF affect model's performance on the CoGames benchmark.
2. Navigation blocker: all policies (including cogames built-in) score 0 due to wall collisions. Need to solve navigation either through AIF planning or practical pathfinding.
3. Whether simpler missions exist that allow basic policy success as a starting point.
4. Built-in cogames policies serve only as comparison baselines, not as the goal.

## Auto Handoff
- **What changed:** CvC benchmark pipeline completed. 60-episode benchmark run confirmed pipeline works but all policies score 0 reward. Root cause: navigation failure in wall-heavy maps.
- **What is still in flight:** Building an AIF-based CvC policy that uses our affect mechanism. This is the core goal — not improving rule-based policies.
- **What next session should do:** Start designing the CvC generative model for AIF inference. In parallel, try simpler missions and add wall-avoidance to get a working baseline. See MISSION.md Track 2.

## Status
ACTIVE — CvC benchmark integration complete, working on policy quality for non-zero scores.
