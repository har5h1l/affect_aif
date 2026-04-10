# Project Roadmap

This document tracks the project roadmap for the affect_aif system: per-partner metacognitive precision tracking as orthogonal augmentation to active inference planning in multi-agent social inference. It merges the long-term phase plan with the active future-work tracks.

---

## 1. Phase Status

### MVP Summary (Phases 1-7: Complete)

The first major iteration established the core finding and produced a paper draft. Key results:

- **Core finding:** Per-partner affective precision tracking provides orthogonal augmentation to planning depth. Under sophisticated inference in the shipped binary-action task, planning horizon τ=2 through τ=8 produces identical non-affective performance, yet adding affect yields ~+46 payoff points at any depth.
- **Hypothesis scorecard:** H1 (affect > baselines) strongly supported (d=0.64 default, d=1.30 betrayal). H2 (lesion dissociation / Damasio pattern) strongly supported. H3 (precision > reward averaging) context-dependent — supported only when prediction error and reward diverge (binary betrayal). H4 (post-switch robustness) supported. H5 (partner selection) supported.
- **Cross-game generalization:** Augmentation holds across PD, Stag Hunt, and Chicken under volatility (d > 1.0 in all). Game-dependent in stable conditions.
- **Clinical sensitivity:** Requires graded/betrayal environments (binary games saturate softmax). Graded betrayal produces 80.5-point between-clinical spread. Alexithymia paradoxically protective (d=+0.80); borderline shows progressive deterioration (d=-1.14); depression self-corrects.
- **Predictive score comparison:** C2 decisively preferred under betrayal stress (log10 proxy = 3.0 vs C1). Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.
- **Variational beta:** Supported auxiliary variational-beta path in Condition 12 is behaviorally equivalent to continuous EMA in stable environments (d=0.001). Moderate divergence under betrayal (d=0.41).
- **CvC benchmark:** Early WIP / proof-of-concept. Navigation-only baseline works (BFS + wall detection, 84-91% move success). Reward results minimal. Not publication-ready.
- **Paper:** Draft complete (theory gaps addressed, results integrated, figures included). Architecture needs justification of departures from standard AIF before submission.

### Completed Phase Reference

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 4 | Variational Beta Reformulation | Complete |
| Phase 5 | Clinical Parameter Sensitivity | Complete |
| Phase 6 | Bayesian Model Comparison | Complete |
| Phase 7 | Cross-Game Generalization | Complete |

**Phase 4 details:** Discrete Bayesian beta formulation implemented and validated. Behaviorally equivalent to continuous EMA in stable environments (d = 0.001). Moderate divergence under betrayal (d = 0.41) due to transition matrix persistence.

**Phase 5 details:** Graded betrayal environment identified as the critical test bed. Between-clinical spread: 80.5 points (2700x improvement over graded default). Alexithymia paradoxically protective (d=+0.80); borderline shows progressive deterioration (d=-1.14); depression self-corrects within ~30 rounds.

**Phase 6 details:** C2 (precision tracking) is the decisively best predictive model under betrayal stress (log10 BF = 3.0 vs C1, 2.7 vs C5). In stable conditions, C5 wins at the population level.

**Phase 7 details:** Augmentation generalizes under volatility across PD, Stag Hunt, and Chicken (d > 1.0 in all). Game-dependent in stable conditions. Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.

### Current Direction: Architectural Tightening

Prompted by external review (Andrew Pashea, 2026-03-30) and internal three-agent codebase audit. The goal is to align the implementation with standard active inference conventions, fix known issues, and re-run experiments on a cleaner foundation before the next paper.

**Operational summary:**
- MVP: Complete (Phases 1-7, paper draft, CvC proof-of-concept).
- Current focus: Architectural tightening — fix known issues, address standard-AIF departures, make design decisions.
- Paper status: Results solid. Architecture needs justification/revision before submission to AIF venue.
- Benchmark: Early WIP / proof-of-concept. Not publication-ready.

---

## 2. Open Architectural Decisions

These require the user's thinking before implementation can proceed.

### Decision 1: The B matrix question (most important)

The partner-type B matrix is action-independent: cooperate/defect doesn't affect type transitions. This is domain-correct (your action genuinely doesn't change what type your partner is), but it has consequences:

- The agent can't model at the B-matrix level how sustained cooperation stabilizes a reciprocator. Reciprocator dynamics are handled entirely through the A matrix (likelihood conditions on last_action).
- Planning depth may be structurally uninformative because looking further ahead doesn't reveal new state transitions — the B matrix just drifts with p_switch regardless of what the agent does.
- **The flat depth curve might be a structural consequence of this design choice, not a finding about the domain.**

If you added an action-dependent B (e.g., cooperating increases probability that a reciprocator stays reciprocating), deeper planning could start to matter. That would reframe the "orthogonal augmentation" claim: affect might still be orthogonal, but depth might no longer be irrelevant.

**Options:**
- (a) Keep current design, explicitly justify in paper — "in domains where actions don't affect hidden state transitions, affect provides orthogonal value" (defensible, narrows claim)
- (b) Add action-dependent B for reciprocator dynamics, re-run experiments — tests whether depth matters when B is action-dependent (high effort, could strengthen or weaken the story)
- (c) Test both and compare — run a small experiment with action-dependent B to see if depth separates, then decide

### Decision 2: pymdp alignment path

Andrew offered to help formalize in pymdp. Options:
- (a) **Notation only** — keep JAX code, make docs/paper match pymdp conventions. Fastest but reviewers may push back on custom implementation.
- (b) **pymdp wrapper** — use pymdp for generative model definition, keep custom JAX planning. Middle ground.
- (c) **Full pymdp** — re-implement in pymdp 1.0 with Andrew's help. Most credible for AIF community, but significant effort and may require extending pymdp for the affect mechanism.
- (d) **Keep JAX, document departures** — add explicit section to theory.md justifying each departure.

### Decision 3: Multiplicative vs additive precision weighting

Current: `G(π) * (1 + μβ)` — multiplicative. Standard AIF would add a terminal value: `G(π) + μβ`. The multiplicative form means high-beta partners amplify the *entire* EFE, not just add a fixed bias. This is theoretically motivated (precision should scale the whole estimate, not add to it) but non-standard. Options:
- (a) Keep multiplicative, add theoretical justification
- (b) Test additive form and compare
- (c) Implement both, let experiments decide

### Decision 4: AIF partners vs rule-based partners

Currently all partners are rule-based (cooperator, reciprocator, exploiter, random). Using AIF agents as partners would be a fundamental change — genuine multi-agent inference rather than learning about scripted opponents. This is a future direction, not a current priority, but worth discussing with Andrew as a subsequent phase.

### Improvement Areas (can proceed in parallel)

Work that can proceed without waiting for the decisions above, organized by category:

**Area 1: Code Correctness Fixes**
1. **Fix mean-field epistemic term** — `_rollout_policy_trust_game_mean_field()` in `core/rollout.py` line 136 uses channel ambiguity (`-expected_ambiguity`) instead of true information gain. Replace with proper expected entropy reduction. All published results use sophisticated inference (correct), so existing findings are unaffected.
2. **Single-factor documentation** — The model defines two hidden state factors (partner type + interaction context) but only infers over partner type. Context is directly observed, so this is correct — but it should be documented as a single-factor POMDP with partner-indexed beliefs.

**Area 2: Test Coverage**
3. **EFE unit tests** — Direct tests for EFE computation: epistemic value is positive for uncertain beliefs and approaches zero for sharp beliefs; pragmatic value aligns with C matrix preferences; terminal value adjustment works correctly; sophisticated and mean-field rollouts agree for sharp beliefs.
4. **Affective state convergence tests** — Beta converges toward 1.0 under consistent correct predictions, toward 0.0 under consistent surprise. Clinical parameter regimes produce different trajectories.
5. **Generative model likelihood tests** — Verify A matrix produces correct observation probabilities for each partner type under each action.

**Area 3: Documentation & Theory**
6. **Document architectural departures** — Add a section to theory.md explicitly addressing: why single-factor inference is sufficient, why B is action-independent, why precision weighting is multiplicative, why one-step Bayes IS VFE minimization for categorical distributions.
7. **Soften depth claims pending Decision 1** — Current paper says depth is "irrelevant." If the flat curve is a structural artifact of action-independent B, the claim needs hedging.
8. **Narrow H3 framing** — Reframe precision-vs-reward-averaging as context-dependent: precision tracking benefits arise specifically when prediction error and reward dissociate (binary betrayal), not universally.

**Area 4: Benchmark & CvC**
9. **Flag CvC as early WIP** — Add clear status documentation to benchmark module. Results are proof-of-concept, not publication-ready.
10. **CvC navigation improvements** — Current BFS heuristic achieves 84-91% move success. Full scoring loop (gear → ore → hearts → aligned junctions) is incomplete. Deprioritized until core architecture is settled.

**Area 5: Experimental Re-runs (after architecture decisions)**
11. **Re-run core experiments** after any architecture changes from Decisions 1-3. Use same configs but on updated codebase.
12. **Test action-dependent B** (if Decision 1 = option b or c) — Small experiment (10 seeds, 100 rounds) to see if depth separates when B is action-dependent.
13. **Test additive precision weighting** (if Decision 3 = option b or c) — Compare multiplicative vs additive forms on default + betrayal configs.

---

## 3. Active Tracks

These tracks are the immediate actionable work, organized by priority. They depend on Decisions 1-4 above for the experimental re-runs, but the theory and benchmark tracks can proceed in parallel.

### Track 1: Paper Theory Gaps (active, HIGH priority)

Specific gaps in theory, related work, and empirical framing that must be addressed before paper submission.

**1.1 Inside-Out Literature Positioning**

The core novelty — beta as metacognitive precision monitoring ("how reliable is my model of partner B?") — needs explicit positioning against three alternative approaches:
- **Yoshida (2024)** — empathic coupling = outside-in (model partner's internal states)
- **Pitliya et al. (2025)** — ToM = cognitive model of other's inference
- **This work** — inside-out metacognitive monitoring of one's own social inference channel

The triple dissociation (outside-in empathy / cognitive ToM / inside-out precision monitoring) is the cleanest positioning. Action: update Discussion in `docs/paper/main.tex` and `docs/theory/theory.md` Section 4.

**1.2 Precision Modulation Pathway: Test or Cut**

Per-partner policy precision modulation (gamma_k = f(beta_k)) is implemented but never tested in production experiments. Decision required:
- **Option A: Run it.** Graded game (q_pi entropy ~5.8) is where it should matter. Run C2 with gamma-modulation in graded betrayal (50-100 seeds).
- **Option B: Cut it.** Remove from paper, keep code, move to future work explicitly.

Requires user decision.

**1.3 vmPFC Neuro-Architectural Argument**

The C3/C4 lesion analogy needs neural grounding from:
- **Bancee et al. (2026)** — vmPFC encodes emotion concepts in geometric form
- **Baram et al. (2026)** — OFC/vmPFC maintains persistent schema representations

Together with Damasio: vmPFC is where precision over social models intersects with affective state. Discussion-level argument only.

**1.4 BMR Trigger Framing (Theory Only)**

Strengthen the Future Work BMR paragraph with neuroscience:
- **Behrens (2025)** — hippocampal ripples mediate structural belief updates
- **Mishchanchuk (2024)** — causal dissociation of hidden-state inference from parameter updating
- **Somatosensory surprise paper** — early ~70ms = model inadequacy, late ~140ms = parameter update

Persistent low beta is computationally analogous to the "model inadequacy" signal. No implementation — theory framing only.

**1.5 Between-Clinical Differentiation Framing**

Phase 5 between-profile payoff differences are small (10.324-10.353). The paper should lead with:
- Qualitative story: alexithymia protective / borderline deteriorating / depression self-correcting as distinct computational impairments
- Structural distinction: beta_0 correctable by inference vs alpha/lambda creating persistent perturbations
- Acknowledge between-profile quantitative differentiation as a limitation/future-work item

### Track 2: CoGames/CvC Benchmark (active, HIGH priority)

**Goal:** Get a submission-ready policy onto the actual CvC benchmark (beta-cvc Observatory season, compat_version 0.19) with non-zero reward.

**2.1 Solve Navigation**

A* pathfinding layer to replace directional heuristics:
1. Parse local grid observation to build walkability map
2. A*/BFS to find path to target
3. Return next cardinal action
4. Fall back to random valid moves

Implementation: `PathfindingMixin` in `affect_aif/benchmark/cvc_navigation.py`.

**2.2 ScoringLoopPolicy Baseline**

State-machine policy that completes the CvC scoring loop: get gear -> mine ore -> deposit at base -> collect hearts -> align junction. Uses PathfindingMixin for navigation. Target: non-zero reward.

**2.3 AffectCvCPolicy**

Layer per-partner precision tracking onto the baseline:
1. Teammate observation model (predict position/behavior per teammate)
2. Beta_k update (compare predicted vs actual)
3. Policy modulation (high-beta -> coordinate, low-beta -> independent)

**2.4 Benchmark and Observatory Submission**

Full benchmark, analysis, packaging via `cvc_packaging.py`. Validate compat_version 0.19.

**2.5 Simpler Missions (Parallel)**

Check if simpler/more-open CvC missions exist as stepping stones.

**Current status:** Pipeline complete. All policies score 0 reward due to navigation failures (~80% wall collisions on machina_1). See `docs/operations/benchmark.md`.

**Dependencies:** cogames >= 0.19.2, mettagrid >= 0.19.3, Python 3.12 for execution.

### Track 3: Paper Preparation (active, MEDIUM priority — depends on Tracks 1-2)

**3.1 Docs Consistency Check**
Verify agreement across `docs/theory/theory.md`, `docs/experiment/results.md`, `docs/experiment/design.md`, and `docs/paper/main.tex` on condition numbering, key numbers, hypothesis status, and phase descriptions.

**3.2 Results Reproducibility Spot-Check**
Spot-check key configs (5 seeds each): `default.json`, `betrayal_stress.json`, `horizon_sweep.json`.

**3.3 Add CvC Results to Paper**
Once Track 2 produces results: describe CvC environment, report benchmark results, show beta dynamics, frame as architectural generality demonstration.

**3.4 Final LaTeX Polish**
Bibliography completeness, figure/table numbering, equation references, add Yoshida/Sennesh/Ramstead/Bancee/Baram, check for TODO/FIXME.

---

## 4. Future Directions Beyond Current Tracks

These are post-tightening priorities, roughly ordered by likely sequencing.

1. **pymdp alignment** — depending on Decision 2, either notation alignment or re-implementation with Andrew's help.
2. **AIF partners** — replace rule-based partners with active inference agents for genuine multi-agent inference rather than scripted opponents.
3. **Human data validation** — fit model to human trust-game data from healthy participants and vmPFC-lesioned patients.
4. **CoGames/CvC** — develop AIF-based navigation policy for full benchmark, beyond the rule-based TeammateReliabilityPolicy.
5. **Richer environments** — partial observability, larger action spaces, multi-step belief cascades.

### Phase 8: Human Data Fitting (future, requires user decision)

**Goal:** Fit model parameters to individual human participants' trust game behavior.

**Scope:**
- Obtain trust-game behavioral data from healthy participants and vmPFC-lesioned patients
- Estimate individual-difference parameters (alpha_charge, lambda_smooth, beta_0) from action sequences
- Test whether the affect-on/affect-off distinction predicts patient/control behavioral split
- Examine whether fitted parameters cluster with known individual differences (trait empathy, interoceptive accuracy)

**Entry condition:** Paper draft stable. User approval required — do not start autonomously.

**Status: NOT STARTED.**

### Dependency Graph

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
