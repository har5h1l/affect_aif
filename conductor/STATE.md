---
status: CONTINUE
next_priority: 2
pending_work:
  - "Run cvc_obs_diagnostic.py on server (Python 3.12) to discover wall encoding"
  - "Run CvC smoke-tests on server: scoring_loop + affect_cvc configs"
  - "Run cvc_list_missions.py on server to discover simpler missions (Track 2.5)"
  - "Track 1.2: Awaiting user decision on precision modulation (test or cut)"
  - "Track 3.3: Add CvC results to paper once Track 2 produces data"
next_session_focus: "Run all CvC scripts on server (diagnostic, smoke-tests, mission discovery), iterate on navigation"
model_hint: opus
---

# Research State

## Last Updated
2026-03-27 (Session 11)

## Session Count
11

## Current Findings

### Trust-Game Results (Phases 1-7: COMPLETE)

All trust-game phases are complete with publication-quality results. Full results in docs/results_tracking.md.

### Session 11: Critical Bug Fixes + LaTeX Polish (2026-03-27)

**Branch:** `mango/affect_aif/20260326-211344` — 4 commits this session

#### Code Review Findings & Fixes

Thorough code review of all CvC benchmark code found 20 issues. Fixed the 3 highest-priority:

| Issue | Severity | Fix |
|-------|----------|-----|
| **Velocity/prediction ordering** in `cvc_affect_policy.py` | HIGH | Velocity was written *before* prediction was computed, making surprise always 0 and beta always rise. Reordered: prediction uses previous velocity, then current velocity is stored. **This was making the entire affect mechanism non-functional.** |
| **Missing policy aliases** in `run_benchmark.py` | HIGH | `scoring_loop` and `affect_cvc` aliases were missing from `CVC_POLICY_ALIASES`, making configs unable to reference them by short name. |
| **Worker PYTHONPATH** in `cvc_local_backend.py` | HIGH | Worker subprocess had no `PYTHONPATH`, so `import affect_aif` would fail unless run from repo root. Now passes repo root in env. |
| **Agent-blocking as permanent walls** in `cvc_navigation.py` | MEDIUM | Movement failures were permanently added to wall set. Now walls expire after 15 steps — real walls get re-confirmed on each bump, agent-blocking expires. |

DECISION: Wall expiry uses step-count timestamps in a dict (was a set). Expiry of 15 steps is a reasonable default — enough to avoid re-bumping immediately, short enough to recover from agent-blocking.

#### Known Issues NOT Fixed (lower priority, may resolve with server diagnostic)

- Navigation: `WALL_FEATURE_NAMES` are guessed ("wall", "obstacle", "blocked") — diagnostic will reveal actual encoding
- `token.location` type comparison may fail if mettagrid returns lists instead of tuples
- `int(token.feature.normalization)` could crash if None
- `stuck_steps` tracked but never used for recovery
- Beta modulation only wired to ALIGN_JUNCTION phase, not MINE_ORE/DEPOSIT
- Teammate detection may include non-agent entities not in `_structure_tag_ids`

#### Track 3.4: LaTeX Polish (PARTIAL)

Fixed:
- All 5 orphaned bibliography entries now cited (bechara1994, joffily2013, seth2013, smith2020, smith2021)
- Added "(Hypothesis 1)" label to first results subsection for consistency
- Fixed table float specifiers `[h]` → `[ht]`

Remaining (cannot fix without data):
- Table `tab:h3` graded betrayal row: C2/C5 payoffs still `---` (windowed data exists but no overall means in results_tracking)
- Table `tab:horizon` / `tab:orthogonality`: C8 still `≈576` (source data also uses approximation)
- No figures (will need for journal submission)
- Sennesh/Ramstead: no actual citation point identified — may not need a standalone entry

### Session 10: AffectCvCPolicy + Mission Discovery (2026-03-26)

See session 10 notes below for full details.

#### Track 2: CvC Benchmark

| Step | Status | Details |
|------|--------|---------|
| 2.1 | IMPLEMENTED + IMPROVED (wall expiry) | BFS pathfinding with movement-failure wall learning + 15-step expiry |
| 2.2 | IMPLEMENTED (session 9) | ScoringLoopPolicy state machine |
| 2.3 | BUG-FIXED | AffectCvCPolicy velocity ordering fixed — beta tracking now functional |
| 2.3 tests | COMPLETE | 14 tests pass (197 total) |
| 2.5 | PARTIALLY DONE | Mission discovery script ready for server |
| Infrastructure | FIXED | Policy aliases added, PYTHONPATH passed to worker |

#### Track 1: Paper Theory Gaps — DONE (except 1.2 awaiting user)

All complete from session 9. Track 1.2 (precision modulation: test or cut) still awaits user decision.

#### Track 3: Paper Preparation

3.1-3.2 complete. 3.4 partially done (bibliography/labels fixed, data placeholders remain). 3.3 depends on Track 2 CvC results.

## Known Gaps / Next Steps

### Track 2: CvC Benchmark (HIGH priority — needs server)

Server testing queue (all need Python 3.12 + cogames):
1. `python3.12 scripts/cvc_obs_diagnostic.py --steps 50 --output /tmp/obs_features.json` — discover wall encoding
2. `python3.12 scripts/cvc_list_missions.py` — discover simpler missions
3. Smoke-test scoring_loop: `python scripts/run_benchmark.py --config affect_aif/configs/benchmark_cvc_scoring_smoke.json`
4. Smoke-test affect_cvc: `python scripts/run_benchmark.py --config affect_aif/configs/benchmark_cvc_affect_smoke.json`
5. If >0 aligned junctions → Track 2.4 (full benchmark + packaging)
6. If still 0 → use diagnostic output to improve wall detection, or switch to simpler mission

NEXT: The critical bug fixes (velocity ordering, policy aliases, PYTHONPATH) mean server testing should now produce meaningful results. The affect mechanism will actually track teammate reliability instead of always increasing beta.

### Track 1: Track 1.2 awaits user decision (precision modulation — test or cut).

### Track 3: 3.3 (CvC results in paper) depends on Track 2. 3.4 data placeholders need actual numbers.

## Auto Handoff
- **What changed:** Session 11 found and fixed 4 bugs via comprehensive code review: (1) velocity ordering bug that made affect mechanism non-functional, (2) missing policy aliases in run_benchmark.py, (3) missing PYTHONPATH in worker subprocess, (4) permanent wall marking from agent-blocking. Also completed LaTeX polish: cited all 5 orphaned bibliography entries, fixed hypothesis labeling, fixed table float specifiers. All 197 tests pass.
- **What is still in flight:** All CvC testing needs server with Python 3.12 + cogames. Track 1.2 awaits user decision.
- **What next session should do:**
  1. Run obs diagnostic, mission discovery, and smoke-tests on server
  2. If navigation works → full benchmark (Track 2.4)
  3. If not → iterate using diagnostic output or switch missions
  4. Present Track 1.2 decision to user if not yet resolved

## Mango Sync Lesson
`mango run --cloud server` does NOT update the server's local master from origin. Must `ssh server 'cd <repo> && git fetch origin && git merge origin/master --ff-only'` first.

## Status
CONTINUE — Track 2 needs server testing (bugs now fixed, should produce meaningful results), Track 1.2 awaits user decision
