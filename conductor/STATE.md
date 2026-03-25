---
status: CONTINUE
next_priority: 2
pending_work:
  - "Run cvc_obs_diagnostic.py on server (Python 3.12) to discover wall encoding"
  - "Smoke-test ScoringLoopPolicy on server (benchmark_cvc_scoring_smoke.json)"
  - "Track 2.3: Build AffectCvCPolicy with per-partner beta tracking"
  - "Track 2.5: Try simpler CvC missions"
  - "Track 1.2: Awaiting user decision on precision modulation (test or cut)"
  - "Track 3.3-3.4: Add CvC results to paper, final LaTeX polish"
next_session_focus: "Run obs diagnostic and CvC smoke-test on server, iterate on navigation"
model_hint: opus
---

# Research State

## Last Updated
2026-03-25 (Session 9, final update)

## Session Count
9

## Current Findings

### Trust-Game Results (Phases 1-7: COMPLETE)

All trust-game phases are complete with publication-quality results. Full results in docs/results_tracking.md.

### Session 9: Paper Theory Gaps + CvC Navigation + Spot-Checks (2026-03-25)

**Branch:** `mango/affect_aif/20260325-135703` — 5 commits

#### Track 1: Paper Theory Gaps — DONE (except 1.2 awaiting user)

| Step | Status | What was done |
|------|--------|--------------|
| 1.1 | COMPLETE | Triple dissociation paragraph in Introduction: outside-in empathy / cognitive ToM / inside-out precision monitoring. Updated abstract and theory.md §1.5. |
| 1.2 | AWAITING USER | Presented options: test gamma modulation in graded game or cut from paper. Recommended Option B (cut). |
| 1.3 | COMPLETE | vmPFC neuroscience Discussion subsection: Bancee (vmPFC emotion geometry) + Baram (OFC schema manifolds) + Damasio. |
| 1.4 | COMPLETE | BMR Future Work expansion: Behrens (hippocampal ripples) + Mishchanchuk (causal dissociation). Preserves clean-test caveat. |
| 1.5 | COMPLETE | SH betrayal clinical results in Results section (Table 2: borderline d=0.72). Updated abstract, Limitations. |

Bibliography: Added Bancee 2026, Baram 2026, Behrens 2025, Mishchanchuk 2024.

#### Track 2: CvC Benchmark — Infrastructure Built, Needs Server Testing

| Step | Status | Details |
|------|--------|---------|
| 2.1 | IMPLEMENTED | `cvc_navigation.py`: BFS pathfinding with movement-failure wall learning, global position tracking. Wired into TeammateReliabilityPolicy. |
| 2.2 | IMPLEMENTED | `cvc_scoring_policy.py`: state-machine scoring loop (GET_GEAR→MINE_ORE→DEPOSIT→ALIGN_JUNCTION). Config: `benchmark_cvc_scoring_smoke.json`. |
| 2.1 diagnostic | IMPLEMENTED | `scripts/cvc_obs_diagnostic.py`: dumps all observation features to discover wall encoding. Needs Python 3.12 on server. |
| 2.3-2.5 | NOT STARTED | Depend on server testing of 2.1/2.2. |

DECISION: The navigation pathfinding currently uses movement-failure learning (tracks which moves hit walls). If the diagnostic reveals an observation feature for walls (e.g., "wall", "obstacle"), we can add direct wall detection for much faster pathfinding.

#### Track 3: Paper Preparation

| Step | Status | Details |
|------|--------|---------|
| 3.1 | COMPLETE | All docs numerically consistent. Fixed stale CLAUDE.md phase number. |
| 3.2 | COMPLETE | Spot-checks with 5 seeds confirm: default C2>C4 by ~44pts (expected ~45); horizon curve flat (C1≈C4≈C6≈C7); betrayal C2>C4 in right direction. |
| 3.3-3.4 | NOT STARTED | Depend on Track 2 CvC results. No TODOs/FIXMEs in LaTeX. |

#### Track 4: Research-Brain Improvements
Documented in previous session. No changes needed — user handles separately.

## Known Gaps / Next Steps

### Track 1: Paper Theory Gaps

All complete except 1.2 (precision modulation — test or cut). BLOCKER: need user decision.

### Track 2: CvC Benchmark (HIGH priority — needs server)

1. Run `python3.12 scripts/cvc_obs_diagnostic.py --steps 50 --output /tmp/obs_features.json` on server
2. Run smoke-test: `python scripts/run_benchmark.py --config affect_aif/configs/benchmark_cvc_scoring_smoke.json`
3. If >0 aligned junctions: build AffectCvCPolicy (Track 2.3)
4. If still 0: use diagnostic output to improve wall detection, or try simpler missions

### Track 3: Paper Preparation

3.3 (CvC results in paper) and 3.4 (final polish) depend on Track 2 producing results.

## Mango Sync Lesson
`mango run --cloud server` does NOT update the server's local master from origin. Must `ssh server 'cd <repo> && git fetch origin && git merge origin/master --ff-only'` first.

## Auto Handoff
- **What changed:** Session 9 completed Track 1 paper theory gaps (triple dissociation, vmPFC, BMR, SH clinical — all in main.tex with 4 new bib entries). Built CvC navigation (BFS pathfinding + ScoringLoopPolicy + diagnostic script). Ran docs consistency check (all clean) and reproducibility spot-checks (3/3 patterns confirmed with 5 seeds). Fixed CLAUDE.md phase number. 5 commits, 183 tests pass.
- **What is still in flight:** Track 2 navigation needs server testing (Python 3.12). Track 1.2 awaits user decision (precision modulation).
- **What next session should do:**
  1. Run obs diagnostic on server to discover wall encoding format
  2. Run CvC smoke-test on server
  3. If navigation works → Track 2.3 (AffectCvCPolicy)
  4. If not → iterate using diagnostic output
  5. Present Track 1.2 decision to user if not yet resolved

## Status
CONTINUE — Track 2 needs server testing, Track 1.2 awaits user decision
