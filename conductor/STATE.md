---
status: CONTINUE
next_priority: 2
pending_work:
  - "Run cvc_obs_diagnostic.py on server (Python 3.12) to discover wall encoding format"
  - "Smoke-test ScoringLoopPolicy + pathfinding on server (3 seeds, 1000 steps)"
  - "Track 2.3: Build AffectCvCPolicy with per-partner beta tracking"
  - "Track 2.5: Try simpler CvC missions in parallel"
  - "Track 3.2: Results reproducibility spot-check"
  - "Track 1.2: Awaiting user decision on precision modulation (test or cut)"
next_session_focus: "Run obs diagnostic and smoke-test on server, then iterate on navigation"
model_hint: opus
---

# Research State

## Last Updated
2026-03-25 (Session 9)

## Session Count
9

## Current Findings

### Trust-Game Results (Phases 1-7: COMPLETE)

All trust-game phases are complete with publication-quality results:
- Orthogonal augmentation confirmed across binary and graded games
- Clinical sensitivity validated in graded betrayal environment
- Bayesian model comparison shows C2 decisive under volatility
- Cross-game generalization across PD, Stag Hunt, Chicken
- Full results in docs/results_tracking.md

### Session 7 Output: Stag Hunt Clinical Sensitivity (2026-03-24)

**Branch:** `origin/mango/affect_aif/20260324-143607` — MERGED to master at `ba42b00`.

SH betrayal (50 seeds x 120 rounds): borderline d=0.72 (decisive BF=-2.89), alexithymia protective, depression self-correcting. First env with stat-sig between-clinical differentiation.

### Session 9 Output: Paper Theory Gaps + CvC Navigation (2026-03-25)

**Branch:** `mango/affect_aif/20260325-135703` (this session)

DECISION: Track 1 paper theory gaps substantially addressed. Track 2 navigation infrastructure built. Track 3.1 consistency check complete.

#### Track 1: Paper Theory Gaps — DONE (except 1.2 awaiting user)

**1.1 Triple dissociation framing: COMPLETE.**
Added paragraph in Introduction (main.tex) explicitly framing outside-in empathy (Pitliya) / cognitive ToM (Yoshida) / inside-out precision monitoring (this work) as three distinct computational strategies for social cognition. Updated abstract to include this framing. Updated theory.md Section 1.5 to match.

**1.2 Precision modulation: AWAITING USER DECISION.**
Presented options (test in graded game or cut from paper). Recommendation: Option B (cut). The paper is cleaner with one well-tested pathway. The Future Work paragraph already notes it as an open direction.

**1.3 vmPFC neuroscience: COMPLETE.**
Added Discussion subsection "Neural Grounding: vmPFC as Precision Over Social Schemas" connecting Bancee (2026, vmPFC emotion geometry) + Baram (2026, OFC schema manifolds) + Damasio. Shows vmPFC is where precision over social schemas intersects with affective state.

**1.4 BMR trigger framing: COMPLETE.**
Expanded Future Work structure-learning paragraph with Behrens (2025, hippocampal ripples for structural updates) + Mishchanchuk (2024, causal dissociation). Preserves the clean-test caveat from experiment.md Section 8.2.

**1.5 SH clinical results in paper: COMPLETE.**
Added new Results subsubsection "Stag Hunt Betrayal: Qualitative Between-Clinical Differentiation" with Table 2 (borderline d=0.72, decisive BF). Updated abstract, Limitations. Paper now leads with SH as primary clinical story.

**Bibliography:** Added Bancee 2026, Baram 2026, Behrens 2025, Mishchanchuk 2024.

#### Track 2: CvC Benchmark — Navigation Built, Needs Server Testing

**2.1 BFS pathfinding: IMPLEMENTED.**
- `affect_aif/benchmark/cvc_navigation.py`: NavigationHelper with BFS pathfinding, movement-failure wall learning, global position tracking, exploration mode
- Wired into TeammateReliabilityPolicy (cvc_policy.py)
- Navigation state tracks global position, known walls, visited cells
- `scripts/cvc_obs_diagnostic.py`: diagnostic to discover wall encoding (run on server with Python 3.12)

NEXT: Run diagnostic on server to determine how walls are encoded in observations. The movement-failure approach works regardless, but observation-based wall detection would be much faster.

**2.2 ScoringLoopPolicy: IMPLEMENTED.**
- `affect_aif/benchmark/cvc_scoring_policy.py`: state-machine that follows GET_GEAR -> MINE_ORE -> DEPOSIT -> ALIGN_JUNCTION loop with BFS navigation
- `affect_aif/configs/benchmark_cvc_scoring_smoke.json`: smoke test config (3 seeds, 1000 steps)
- Role assignment: 5 miners + 3 aligners (8 agents)

NEXT: Smoke-test on server to see if BFS pathfinding produces >0 aligned junctions.

**2.3-2.5: NOT STARTED.** Depend on 2.1/2.2 server testing.

#### Track 3: Paper Preparation

**3.1 Docs consistency check: COMPLETE.**
All docs (main.tex, theory.md, results_tracking.md, experiment.md) are numerically consistent. Zero disagreements on condition definitions, effect sizes, p-values, Bayes factors, or payoff values. Fixed one stale phase number in CLAUDE.md.

**3.2-3.4: NOT STARTED.**

#### Track 4: Research-Brain Improvements
Documented in previous state. No changes.

## Known Gaps / Next Steps

### Track 1: Paper Theory Gaps (HIGH priority)

| Step | Description | Status | Depends on |
|------|-------------|--------|------------|
| 1.1 | Inside-out literature positioning | COMPLETE | — |
| 1.2 | Precision modulation: test or cut | AWAITING USER | — |
| 1.3 | vmPFC neuro-architectural argument | COMPLETE | — |
| 1.4 | BMR trigger framing | COMPLETE | — |
| 1.5 | Between-clinical SH results in paper | COMPLETE | — |

### Track 2: CvC Benchmark (HIGH priority)

| Step | Description | Status | Depends on |
|------|-------------|--------|------------|
| 2.1 | BFS pathfinding layer | IMPLEMENTED (needs server test) | — |
| 2.2 | ScoringLoopPolicy baseline | IMPLEMENTED (needs server test) | 2.1 |
| 2.3 | Add affect mechanism (AffectCvCPolicy) | NOT STARTED | 2.2 server test |
| 2.4 | Benchmark + Observatory submission | NOT STARTED | 2.3 |
| 2.5 | Try simpler missions (parallel) | NOT STARTED | — |

### Track 3: Paper Preparation (MEDIUM priority)

| Step | Description | Status | Depends on |
|------|-------------|--------|------------|
| 3.1 | Docs consistency check | COMPLETE | — |
| 3.2 | Results reproducibility spot-check | NOT STARTED | — |
| 3.3 | Add CvC results to paper | NOT STARTED | Track 2 |
| 3.4 | Final LaTeX polish | NOT STARTED | 3.1, 3.3 |

## Mango Sync Lesson
`mango run --cloud server` does NOT update the server's local master from origin. Must run `ssh server 'cd <repo> && git fetch origin && git merge origin/master --ff-only'` before launching, or the session will branch from stale state.

## Auto Handoff
- **What changed:** Session 9 completed Track 1 (paper theory gaps: triple dissociation, vmPFC, BMR, SH clinical results all added to main.tex). Built CvC navigation infrastructure (BFS pathfinding + ScoringLoopPolicy). Ran docs consistency check (all clean). Fixed stale CLAUDE.md phase number. 183 tests pass. 4 commits on branch.
- **What is still in flight:** Track 2 navigation needs server testing (Python 3.12 required). Track 1.2 awaits user decision. Track 3.2-3.4 not started.
- **What next session should do:**
  1. Run `scripts/cvc_obs_diagnostic.py` on server to discover wall encoding format
  2. Run smoke test: `python scripts/run_benchmark.py --config affect_aif/configs/benchmark_cvc_scoring_smoke.json`
  3. If navigation works (>0 aligned junctions): proceed to Track 2.3 (AffectCvCPolicy)
  4. If navigation still fails: iterate on wall detection using diagnostic output
  5. Track 3.2: spot-check reproducibility (default.json, betrayal_stress.json, 5 seeds each)
- **BLOCKER for Track 1.2:** Need user to decide: test precision modulation in graded game or cut from paper

## Status
CONTINUE — Track 2 needs server testing, Track 1.2 awaits user decision
