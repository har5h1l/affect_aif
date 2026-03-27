---
status: CONTINUE
next_priority: 2
pending_work:
  - "Run cvc_obs_diagnostic.py on server (Python 3.12) to discover wall encoding"
  - "Run CvC smoke-tests on server: scoring_loop + affect_cvc configs"
  - "Run cvc_list_missions.py on server to discover simpler missions (Track 2.5)"
  - "Track 1.2: Awaiting user decision on precision modulation (test or cut)"
  - "Track 3.3-3.4: Add CvC results to paper, final LaTeX polish"
next_session_focus: "Run all CvC scripts on server (diagnostic, smoke-tests, mission discovery), iterate on navigation"
model_hint: opus
---

# Research State

## Last Updated
2026-03-26 (Session 10)

## Session Count
10

## Current Findings

### Trust-Game Results (Phases 1-7: COMPLETE)

All trust-game phases are complete with publication-quality results. Full results in docs/results_tracking.md.

### Session 10: AffectCvCPolicy + Mission Discovery (2026-03-26)

**Branch:** `mango/affect_aif/20260326-211344` — 2 commits

#### Track 2: CvC Benchmark

| Step | Status | Details |
|------|--------|---------|
| 2.1 | IMPLEMENTED (session 9) | BFS pathfinding with movement-failure wall learning |
| 2.2 | IMPLEMENTED (session 9) | ScoringLoopPolicy state machine |
| 2.3 | IMPLEMENTED | `cvc_affect_policy.py`: AffectCvCPolicy with per-teammate beta tracking. Uses EMA surprise rule (same as trust-game). Team-beta modulates cooperation vs independence. Config: `benchmark_cvc_affect_smoke.json`. |
| 2.3 tests | COMPLETE | `cvc_beta.py` extracted for testability. 14 tests pass (sigmoid, EMA convergence, smoothing, constants). |
| 2.5 | PARTIALLY DONE | `cvc_list_missions.py` written for server discovery. No alternative missions known yet — cogames package defines them. |
| 2.1 diagnostic | NEEDS SERVER | `scripts/cvc_obs_diagnostic.py` ready, needs Python 3.12 |

DECISION: AffectCvCPolicy architecture — beta_k per teammate from positional prediction error. High team_beta (>0.6) = coordinate, low (<0.4) = solo. This mirrors the trust-game mechanism faithfully while adapting to spatial multi-agent context.

DECISION: Beta update helpers extracted to `cvc_beta.py` (no mettagrid dependency) so they're testable locally. Policy class in `cvc_affect_policy.py` imports from there.

#### Track 1: Paper Theory Gaps — DONE (except 1.2 awaiting user)

All complete from session 9. Track 1.2 (precision modulation: test or cut) still awaits user decision.

#### Track 3: Paper Preparation

3.1-3.2 complete from session 9. 3.3-3.4 depend on Track 2 CvC results.

## Known Gaps / Next Steps

### Track 2: CvC Benchmark (HIGH priority — needs server)

Server testing queue (all need Python 3.12 + cogames):
1. `python3.12 scripts/cvc_obs_diagnostic.py --steps 50 --output /tmp/obs_features.json` — discover wall encoding
2. `python3.12 scripts/cvc_list_missions.py` — discover simpler missions
3. Smoke-test scoring_loop: `python scripts/run_benchmark.py --config affect_aif/configs/benchmark_cvc_scoring_smoke.json`
4. Smoke-test affect_cvc: `python scripts/run_benchmark.py --config affect_aif/configs/benchmark_cvc_affect_smoke.json`
5. If >0 aligned junctions → Track 2.4 (full benchmark + packaging)
6. If still 0 → use diagnostic output to improve wall detection, or switch to simpler mission

### Track 1: Track 1.2 awaits user decision (precision modulation — test or cut).

### Track 3: 3.3 (CvC results in paper) and 3.4 (final polish) depend on Track 2 producing results.

## Auto Handoff
- **What changed:** Session 10 built AffectCvCPolicy (per-teammate precision tracking via EMA beta update), extracted pure-Python beta helpers to cvc_beta.py, added 14 tests (all pass, 197 total), created benchmark config for affect_cvc vs scoring_loop comparison, wrote mission discovery script for Track 2.5.
- **What is still in flight:** All CvC testing needs server with Python 3.12 + cogames. Track 1.2 awaits user decision.
- **What next session should do:**
  1. Run obs diagnostic, mission discovery, and smoke-tests on server
  2. If navigation works → full benchmark (Track 2.4)
  3. If not → iterate using diagnostic output or switch missions
  4. Present Track 1.2 decision to user if not yet resolved

## Mango Sync Lesson
`mango run --cloud server` does NOT update the server's local master from origin. Must `ssh server 'cd <repo> && git fetch origin && git merge origin/master --ff-only'` first.

## Status
CONTINUE — Track 2 needs server testing, Track 1.2 awaits user decision
