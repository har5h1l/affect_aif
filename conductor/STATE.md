# Research State

## Last Updated
2026-03-24

## Session Count
7

## Current Findings

### Trust-Game Results (Phases 1-7: COMPLETE)

All trust-game phases are complete with publication-quality results:
- Orthogonal augmentation confirmed across binary and graded games
- Clinical sensitivity validated in graded betrayal environment
- Bayesian model comparison shows C2 decisive under volatility
- Cross-game generalization across PD, Stag Hunt, Chicken
- Full results in docs/results_tracking.md

### Session 7 Output: Stag Hunt Clinical Sensitivity (2026-03-24)

**Note:** Session 7 ran the OLD mission (Phase 5 autonomous) because the four-track MISSION.md was not committed before `mango run` synced to the server. The session produced useful new data but needs to be merged.

**Branch:** `origin/mango/affect_aif/20260324-143607` (9 commits, NOT merged to master)

**Stag Hunt betrayal results (50 seeds x 120 rounds) — first env with stat-sig between-clinical differentiation:**

| Phenotype | Payoff | d vs Healthy | p | log10 BF vs Healthy |
|-----------|--------|-------------|---|---------------------|
| Healthy (C2) | 489.7 | — | — | — |
| Alexithymia (C9) | 497.1 | -0.20 | 0.318 | +0.12 anecdotal |
| Depression (C11) | 484.6 | +0.13 | 0.510 | -0.66 substantial |
| **Borderline (C10)** | **439.8** | **+0.72** | **<0.001** | **-2.89 decisive** |
| No-affect (C4) | 402.7 | — | — | — |

Key findings:
- Borderline is significantly impaired (d=0.72, decisive BF) — first env with stat-sig clinical differentiation from healthy
- Borderline still above no-affect (d=0.57) — volatile affect worse than stable but better than none
- Alexithymia indistinguishable from healthy — frozen precision is protective in high-miscoordination games
- Depression mild Bayesian impairment only (BF=-0.66)
- SH default: d~0 for all phenotypes (same EFE saturation as binary PD)
- Window analysis: borderline impaired pre-betrayal (d=0.82) and late game (d=0.67) — volatility hurts even outside betrayal

Beta dynamics: alexithymia frozen (vol=0.003), borderline volatile (vol=0.185), depression moderate (vol=0.103), healthy moderate (vol=0.085)

**Branch contents (to merge):**
- `scripts/run_clinical_sensitivity.py` (520 lines) — comprehensive clinical sweep with BFs, beta dynamics, window analysis
- `scripts/analyze_clinical_results.py` — standalone post-hoc analysis
- `affect_aif/experiment/runner.py` — refactored (inlined factory, improved checkpointing)
- `tests/test_discrete_beta.py` — 244 lines of Phase 4 tests
- `docs/theory.md` §4.18 — clinical sensitivity in coordination games
- `docs/results_tracking.md` — Phase 5 SH results
- Results CSVs in worktree on server: `/private/tmp/mango-worktree-affect_aif-20260324_143607-12360/results/`

**Merge plan:** Cherry-pick code/doc changes from branch. Keep our MISSION/STATE/future_work/long_term_plan (four-track plan). Conflicts expected in conductor/ and docs/long_term_plan.md only.

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

**Blocker: All policies score 0 reward and 0 aligned junctions.** Root cause: ~80% of moves hit walls. The machina_1 map has complex wall layouts that simple directional heuristics cannot handle.

**Diagnosis and plan:**
- CvC has only 5 actions (noop, move_north/south/east/west); all interaction is proximity-based
- Scoring requires: navigate to gear -> mine ore -> deposit at base -> collect hearts -> align junction
- The navigation problem is engineering, not theory — it must be solved with pathfinding (A*/BFS) before any AIF mechanism can be evaluated
- Plan: PathfindingMixin -> ScoringLoopPolicy (baseline) -> AffectCvCPolicy (with beta) -> package for Observatory submission (beta-cvc season, compat 0.19)

### Paper Theory Gaps Identified

A thorough review of the project and the research-brain literature vault has identified 5 specific theory/framing gaps that need to be addressed before submission:

1. **Inside-out framing not positioned against alternatives.** The beta-as-metacognitive-precision contribution lacks explicit triangulation against Yoshida (2024, outside-in empathy) and Pitliya et al. (2025, cognitive ToM). The triple dissociation is the cleanest positioning but isn't drawn in the paper.

2. **Precision modulation pathway described but untested.** Per-partner gamma_k = f(beta_k) is mentioned in the paper but never tested in production experiments. Described-but-untested mechanisms weaken the contribution. Decision needed: test in graded game (where softmax isn't saturated) or cut from paper.

3. **vmPFC argument lacks neuroscience grounding.** The C3/C4 lesion analogy to Damasio needs support from Bancee et al. (2026, vmPFC emotion geometry) and Baram et al. (2026, OFC/vmPFC schema manifolds). Discussion-level addition only.

4. **BMR-as-affect-trigger lacks neuroscience framing.** Future Work paragraph on BMR can be strengthened with Behrens (2025, hippocampal ripples for structural updates), Mishchanchuk (2024, hidden-state vs parameter dissociation), and somatosensory surprise timing. Theory only, no implementation.

5. **Between-clinical framing leads with wrong metric.** Phase 5 graded-game between-profile payoff differences are small (10.324-10.353). However, Session 7's SH betrayal results now provide strong qualitative differentiation (borderline d=0.72 decisive, alexithymia protective, depression self-correcting). The paper should lead with the SH story and frame the graded-game results as a contrast case.

## Known Gaps / Next Steps

### Track 1: Paper Theory Gaps (HIGH priority)

| Step | Description | Status | Depends on |
|------|-------------|--------|------------|
| 1.1 | Inside-out literature positioning (Yoshida/Pitliya triangle) | NOT STARTED | — |
| 1.2 | Precision modulation: test or cut (ASK USER) | NOT STARTED | — |
| 1.3 | vmPFC neuro-architectural argument (Bancee + Baram + Damasio) | NOT STARTED | — |
| 1.4 | BMR trigger framing with neuroscience refs | NOT STARTED | — |
| 1.5 | Between-clinical differentiation framing | PARTIALLY ADDRESSED | — (SH data from session 7 provides the strong story; needs merge + paper integration) |

### Track 2: CvC Benchmark (HIGH priority)

| Step | Description | Status | Depends on |
|------|-------------|--------|------------|
| 2.1 | Solve navigation (A*/BFS pathfinding layer) | NOT STARTED | — |
| 2.2 | Build ScoringLoopPolicy baseline | NOT STARTED | 2.1 |
| 2.3 | Add affect mechanism (AffectCvCPolicy) | NOT STARTED | 2.2 |
| 2.4 | Benchmark and package for Observatory submission | NOT STARTED | 2.3 |
| 2.5 | Try simpler missions (parallel) | NOT STARTED | — |

### Track 3: Paper Preparation (MEDIUM priority — depends on Tracks 1-2)

| Step | Description | Status | Depends on |
|------|-------------|--------|------------|
| 3.1 | Docs consistency check | NOT STARTED | — |
| 3.2 | Results reproducibility spot-check | NOT STARTED | — |
| 3.3 | Add CvC results to paper | NOT STARTED | Track 2 |
| 3.4 | Final LaTeX polish | NOT STARTED | 3.1, 3.3 |

### Track 4: Research-Brain Improvements (LOW priority — document only)

Identified issues for the user to handle separately:
1. `inbox/insights.md` and `inbox/futures.md` empty despite extraction summaries containing insights/futures — extraction agent writes to `extracted/` instead
2. Feedback loop never run — 60+ papers with `___` ratings, no weight adjustments in `profile/interests.md`
3. Project-specific queries underweight in sweep briefs — "What Would Help" sections not driving queries
4. Graph disconnection between projects and papers — paper notes don't link back to `projects/affect-aif.md`
5. Topic note descriptions stale (still from March 18 despite 65 papers found)
6. Idea seeds from extractions don't consistently land in `profile/ideas.md`
7. No fast-path for urgent targeted queries outside full sweep cycle
8. No mechanism for marking known/authored papers (Pitliya 2025 surfaced as new)
9. Context assembly step invisible — no logging of what was included in sweep context

## Auto Handoff
- **What changed:** Session 7 ran old mission (Phase 5 SH clinical sensitivity) due to sync issue. Produced valuable SH betrayal results (borderline d=0.72 decisive — first stat-sig clinical differentiation). Branch `origin/mango/affect_aif/20260324-143607` needs merge. Four-track plan was written locally but not yet committed before session started.
- **What is still in flight:** Branch merge. All four tracks from the plan.
- **What next session should do:**
  1. **First: merge session 7 branch.** Cherry-pick code/doc changes from `origin/mango/affect_aif/20260324-143607` into master. Keep our MISSION/STATE (four-track plan). Resolve conflicts in conductor/ and docs/long_term_plan.md by preferring our versions. Copy results CSVs from server worktree.
  2. Then start Track 2.1 (CvC navigation) and Track 1.1 (literature positioning) in parallel
  3. Present Track 1.2 options (precision modulation: test or cut) to user

## Status
ACTIVE — four-track plan, Tracks 1-2 co-priority. Session 7 branch awaiting merge.
