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

5. **Between-clinical framing leads with wrong metric.** Phase 5 between-profile payoff differences are small (10.324-10.353); the paper should lead with qualitative story (distinct computational impairments) and structural distinction (beta_0 correctable vs alpha/lambda persistent).

## Known Gaps / Next Steps

### Track 1: Paper Theory Gaps (HIGH priority)

| Step | Description | Status | Depends on |
|------|-------------|--------|------------|
| 1.1 | Inside-out literature positioning (Yoshida/Pitliya triangle) | NOT STARTED | — |
| 1.2 | Precision modulation: test or cut (ASK USER) | NOT STARTED | — |
| 1.3 | vmPFC neuro-architectural argument (Bancee + Baram + Damasio) | NOT STARTED | — |
| 1.4 | BMR trigger framing with neuroscience refs | NOT STARTED | — |
| 1.5 | Between-clinical differentiation framing | NOT STARTED | — |

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
- **What changed:** Four-track plan established after thorough review of project, codebase, results, paper draft, and research-brain literature vault. Theory gaps identified. CvC navigation diagnosed as engineering blocker.
- **What is still in flight:** All four tracks. Track 1 and Track 2 are co-priority.
- **What next session should do:**
  1. Start Track 2.1: examine CvC observation format (`affect_aif/benchmark/cvc_policy.py`, cogames docs), implement `PathfindingMixin` in `affect_aif/benchmark/cvc_navigation.py`, wire into `TeammateReliabilityPolicy`, smoke-test (3 seeds, 1000 steps, target >0 aligned junctions)
  2. In parallel, start Track 1.1: literature positioning paragraph (Yoshida + Pitliya + this work triple dissociation)
  3. Present Track 1.2 options (precision modulation: test or cut) to user before proceeding

## Status
ACTIVE — four-track plan, Tracks 1-2 co-priority.
