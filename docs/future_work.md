# Future Work

This document tracks remaining work and future directions. Phases 1-7 of the trust-game research are complete. The current focus is on the CoGames/CvC benchmark and paper preparation.

---

## §1: CoGames/CvC Benchmark — AIF Affect Model (active)

**Goal:** Adapt our affect-augmented active inference model to the CoGames (CvC) environment and benchmark it. This demonstrates that the architecture generalizes beyond the trust-game family to a real multi-agent spatial domain.

**Why this matters for the paper:** The trust-game results (Phases 1-7) establish the orthogonal augmentation claim within social dilemmas. Showing the same AIF affect mechanism working in CvC — a partially-observed, tick-level, multi-agent territory-control game — would demonstrate architectural generality. Built-in cogames policies are comparison baselines only; the point is our model's performance.

**Current status:** Benchmark pipeline complete and tested. All current policies (rule-based) score 0 reward due to navigation failures in wall-heavy maps.

**Design challenges:**

1. **CvC generative model.** The trust game has a compact state space (partner types, cooperation history). CvC has spatial observations (local grid view), resource states, agent positions, and role assignments. A CvC generative model must map these observations into hidden states the AIF agent can do inference over.

2. **Affect mechanism adaptation.** Per-partner precision tracking (beta) should modulate how the agent weighs teammate observations. High-beta teammates get trusted for coordination tasks; low-beta teammates get deprioritized. The mapping is natural: teammate reliability in CvC (do they show up where expected? do they complete their role?) parallels partner reliability in the trust game.

3. **Navigation as EFE planning.** Rather than bolting on heuristic pathfinding, the generative model should predict movement outcomes — will a move hit a wall, reach a resource, or bring the agent closer to a teammate? Expected free energy over the 5 CvC actions then implicitly handles navigation through the planning mechanism.

4. **Action space.** CvC has only 5 actions (noop + 4 cardinal directions). All object interaction is proximity-based. The generative model needs to encode the sequential structure: navigate to X, then proximity-interact, then navigate to Y.

**Practical approach:**
- Start with simpler/more open missions to get non-zero baseline scores
- Add wall-avoidance to existing policies as a comparison baseline
- Build the AIF generative model incrementally: start with spatial navigation only, then add teammate tracking, then add the affect mechanism
- Compare AIF policy against built-in cogames baselines

**Dependencies:** cogames >= 0.19.2, mettagrid >= 0.19.3, Python 3.12 for execution.

---

## §2: Phase 4 — Variational Beta Reformulation (complete)

**Status: COMPLETE.** Discrete Bayesian beta formulation implemented and validated. Behaviorally equivalent to continuous EMA in stable environments (d = 0.001). Moderate divergence under betrayal (d = 0.41) due to transition matrix persistence — a difference in the prior on precision volatility, not mechanism.

---

## §3: Phase 5 — Clinical Parameter Sensitivity (complete)

**Status: COMPLETE.** Graded betrayal environment identified as the critical test bed. Between-clinical spread: 80.5 points (2700x improvement over graded default). Alexithymia paradoxically protective (d=+0.80); borderline shows progressive deterioration (d=-1.14); depression self-corrects within ~30 rounds.

---

## §4: Phase 6 — Bayesian Model Comparison (complete)

**Status: COMPLETE.** C2 (precision tracking) is the decisively best predictive model under betrayal stress (log10 BF = 3.0 vs C1, 2.7 vs C5). In stable conditions, C5 wins at the population level.

---

## §5: Phase 7 — Cross-Game Generalization (complete)

**Status: COMPLETE.** Augmentation generalizes under volatility across PD, Stag Hunt, and Chicken (d > 1.0 in all). Game-dependent in stable conditions. Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.

---

## §6: Phase 8 — Human Data Fitting (future, requires user decision)

**Goal:** Fit model parameters to individual human participants' trust game behavior.

**Scope:**
- Obtain trust-game behavioral data from healthy participants and vmPFC-lesioned patients
- Estimate individual-difference parameters (alpha_charge, lambda_smooth, beta_0) from action sequences
- Test whether the affect-on/affect-off distinction predicts patient/control behavioral split
- Examine whether fitted parameters cluster with known individual differences (trait empathy, interoceptive accuracy)

**Entry condition:** Paper draft stable. User approval required — do not start autonomously.

**Status: NOT STARTED.**

---

## §7: Trust-Game Gaps and Paper Preparation (active)

**Goal:** Identify and fill any remaining gaps in the trust-game results before paper submission.

**Checklist:**
- Verify all claimed statistical results match saved data in results/
- Check consistency across theory.md, results_tracking.md, experiment.md
- Ensure all benchmark configs are documented and reproducible
- Full test suite passes (currently 178 tests)
- Spot-check key results reproduce with saved configs

---

## Dependency Graph

```
Trust Game (Phases 1-7) ← COMPLETE
    │
    ├──► Paper Preparation (§7) ← ACTIVE
    │
    ├──► CoGames/CvC Benchmark (§1) ← ACTIVE
    │       Goal: AIF affect model in CvC
    │
    └──► Phase 8: Human Data (§6) ← FUTURE (requires user)
```
