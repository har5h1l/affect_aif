# Future Work

This document tracks remaining work and future directions. Phases 1-7 of the trust-game research are complete. The current focus is organized into four tracks: paper theory gaps, CvC benchmark, paper preparation, and research-brain improvements.

---

## Track 1: Paper Theory Gaps (active, HIGH priority)

Specific gaps in theory, related work, and empirical framing that must be addressed before paper submission.

### 1.1 Inside-Out Literature Positioning

The core novelty — beta as metacognitive precision monitoring ("how reliable is my model of partner B?") — needs explicit positioning against three alternative approaches:
- **Yoshida (2024)** — empathic coupling = outside-in (model partner's internal states)
- **Pitliya et al. (2025)** — ToM = cognitive model of other's inference
- **This work** — inside-out metacognitive monitoring of one's own social inference channel

The triple dissociation (outside-in empathy / cognitive ToM / inside-out precision monitoring) is the cleanest positioning. Action: update Discussion in `docs/paper/main.tex` and `docs/theory.md` Section 4.

### 1.2 Precision Modulation Pathway: Test or Cut

Per-partner policy precision modulation (gamma_k = f(beta_k)) is implemented but never tested in production experiments. Decision required:
- **Option A: Run it.** Graded game (q_pi entropy ~5.8) is where it should matter. Run C2 with gamma-modulation in graded betrayal (50-100 seeds).
- **Option B: Cut it.** Remove from paper, keep code, move to future work explicitly.

Requires user decision.

### 1.3 vmPFC Neuro-Architectural Argument

The C3/C4 lesion analogy needs neural grounding from:
- **Bancee et al. (2026)** — vmPFC encodes emotion concepts in geometric form
- **Baram et al. (2026)** — OFC/vmPFC maintains persistent schema representations

Together with Damasio: vmPFC is where precision over social models intersects with affective state. Discussion-level argument only.

### 1.4 BMR Trigger Framing (Theory Only)

Strengthen the Future Work BMR paragraph with neuroscience:
- **Behrens (2025)** — hippocampal ripples mediate structural belief updates
- **Mishchanchuk (2024)** — causal dissociation of hidden-state inference from parameter updating
- **Somatosensory surprise paper** — early ~70ms = model inadequacy, late ~140ms = parameter update

Persistent low beta is computationally analogous to the "model inadequacy" signal. No implementation — theory framing only.

### 1.5 Between-Clinical Differentiation Framing

Phase 5 between-profile payoff differences are small (10.324-10.353). The paper should lead with:
- Qualitative story: alexithymia protective / borderline deteriorating / depression self-correcting as distinct computational impairments
- Structural distinction: beta_0 correctable by inference vs alpha/lambda creating persistent perturbations
- Acknowledge between-profile quantitative differentiation as a limitation/future-work item

---

## Track 2: CoGames/CvC Benchmark (active, HIGH priority)

**Goal:** Get a submission-ready policy onto the actual CvC benchmark (beta-cvc Observatory season, compat_version 0.19) with non-zero reward.

### 2.1 Solve Navigation

A* pathfinding layer to replace directional heuristics:
1. Parse local grid observation to build walkability map
2. A*/BFS to find path to target
3. Return next cardinal action
4. Fall back to random valid moves

Implementation: `PathfindingMixin` in `affect_aif/benchmark/cvc_navigation.py`.

### 2.2 ScoringLoopPolicy Baseline

State-machine policy that completes the CvC scoring loop: get gear -> mine ore -> deposit at base -> collect hearts -> align junction. Uses PathfindingMixin for navigation. Target: non-zero reward.

### 2.3 AffectCvCPolicy

Layer per-partner precision tracking onto the baseline:
1. Teammate observation model (predict position/behavior per teammate)
2. Beta_k update (compare predicted vs actual)
3. Policy modulation (high-beta -> coordinate, low-beta -> independent)

### 2.4 Benchmark and Observatory Submission

Full benchmark, analysis, packaging via `cvc_packaging.py`. Validate compat_version 0.19.

### 2.5 Simpler Missions (Parallel)

Check if simpler/more-open CvC missions exist as stepping stones.

**Current status:** Pipeline complete. All policies score 0 reward due to navigation failures (~80% wall collisions on machina_1). See `docs/benchmarking_integration.md`.

**Dependencies:** cogames >= 0.19.2, mettagrid >= 0.19.3, Python 3.12 for execution.

---

## Track 3: Paper Preparation (active, MEDIUM priority — depends on Tracks 1-2)

### 3.1 Docs Consistency Check
Verify agreement across `docs/theory.md`, `docs/results_tracking.md`, `docs/experiment.md`, and `docs/paper/main.tex` on condition numbering, key numbers, hypothesis status, and phase descriptions.

### 3.2 Results Reproducibility Spot-Check
Spot-check key configs (5 seeds each): `default.json`, `betrayal_stress.json`, `horizon_sweep.json`.

### 3.3 Add CvC Results to Paper
Once Track 2 produces results: describe CvC environment, report benchmark results, show beta dynamics, frame as architectural generality demonstration.

### 3.4 Final LaTeX Polish
Bibliography completeness, figure/table numbering, equation references, add Yoshida/Sennesh/Ramstead/Bancee/Baram, check for TODO/FIXME.

---

## Completed Phases (Reference)

### Phase 4: Variational Beta Reformulation (complete)
Discrete Bayesian beta formulation implemented and validated. Behaviorally equivalent to continuous EMA in stable environments (d = 0.001). Moderate divergence under betrayal (d = 0.41) due to transition matrix persistence.

### Phase 5: Clinical Parameter Sensitivity (complete)
Graded betrayal environment identified as the critical test bed. Between-clinical spread: 80.5 points (2700x improvement over graded default). Alexithymia paradoxically protective (d=+0.80); borderline shows progressive deterioration (d=-1.14); depression self-corrects within ~30 rounds.

### Phase 6: Bayesian Model Comparison (complete)
C2 (precision tracking) is the decisively best predictive model under betrayal stress (log10 BF = 3.0 vs C1, 2.7 vs C5). In stable conditions, C5 wins at the population level.

### Phase 7: Cross-Game Generalization (complete)
Augmentation generalizes under volatility across PD, Stag Hunt, and Chicken (d > 1.0 in all). Game-dependent in stable conditions. Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.

---

## Phase 8: Human Data Fitting (future, requires user decision)

**Goal:** Fit model parameters to individual human participants' trust game behavior.

**Scope:**
- Obtain trust-game behavioral data from healthy participants and vmPFC-lesioned patients
- Estimate individual-difference parameters (alpha_charge, lambda_smooth, beta_0) from action sequences
- Test whether the affect-on/affect-off distinction predicts patient/control behavioral split
- Examine whether fitted parameters cluster with known individual differences (trait empathy, interoceptive accuracy)

**Entry condition:** Paper draft stable. User approval required — do not start autonomously.

**Status: NOT STARTED.**

---

## Dependency Graph

```
Trust Game (Phases 1-7) <- COMPLETE
    |
    |---> Track 1: Paper Theory Gaps (1.1-1.5) <- ACTIVE
    |       |
    |---> Track 2: CvC Benchmark (2.1-2.5) <- ACTIVE
    |       |
    |-------+---> Track 3: Paper Preparation (3.1-3.4) <- BLOCKED on 1+2
    |
    +---> Phase 8: Human Data <- FUTURE (requires user)
```
