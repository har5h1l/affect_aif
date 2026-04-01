# Long-Term Plan

## Purpose

This document tracks the project roadmap for the affect_aif system: per-partner metacognitive precision tracking as orthogonal augmentation to active inference planning in multi-agent social inference. The first MVP (Phases 1-7, paper draft) is complete. The current focus is tightening the architecture, addressing departures from standard active inference, and re-running experiments before the next paper.

## MVP Summary (Complete)

The first major iteration established the core finding and produced a paper draft. Key results:

- **Core finding:** Per-partner affective precision tracking provides orthogonal augmentation to planning depth. Under sophisticated inference in the shipped binary-action task, planning horizon τ=2 through τ=8 produces identical non-affective performance, yet adding affect yields ~+46 payoff points at any depth.
- **Hypothesis scorecard:** H1 (affect > baselines) strongly supported (d=0.64 default, d=1.30 betrayal). H2 (lesion dissociation / Damasio pattern) strongly supported. H3 (precision > reward averaging) context-dependent — supported only when prediction error and reward diverge (binary betrayal). H4 (post-switch robustness) supported. H5 (partner selection) supported.
- **Cross-game generalization:** Augmentation holds across PD, Stag Hunt, and Chicken under volatility (d > 1.0 in all). Game-dependent in stable conditions.
- **Clinical sensitivity:** Requires graded/betrayal environments (binary games saturate softmax). Graded betrayal produces 80.5-point between-clinical spread. Alexithymia paradoxically protective (d=+0.80); borderline shows progressive deterioration (d=-1.14); depression self-corrects.
- **Predictive score comparison:** C2 decisively preferred under betrayal stress (log10 proxy = 3.0 vs C1). Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.
- **Variational beta:** Supported auxiliary variational-beta path in Condition 12 is behaviorally equivalent to continuous EMA in stable environments (d=0.001). Moderate divergence under betrayal (d=0.41).
- **CvC benchmark:** Early WIP / proof-of-concept. Navigation-only baseline works (BFS + wall detection, 84-91% move success). Reward results minimal. Not publication-ready.
- **Paper:** Draft complete (theory gaps addressed, results integrated, figures included). Architecture needs justification of departures from standard AIF before submission.

Detailed phase-by-phase history is in git commits and prior versions of this document.

---

## Current Direction: Architectural Tightening

Prompted by external review (Andrew Pashea, 2026-03-30) and internal three-agent codebase audit. The goal is to align the implementation with standard active inference conventions, fix known issues, and re-run experiments on a cleaner foundation before the next paper.

### Open Decisions

These require the user's thinking before implementation can proceed.

#### Decision 1: The B matrix question (most important)

The partner-type B matrix is action-independent: cooperate/defect doesn't affect type transitions. This is domain-correct (your action genuinely doesn't change what type your partner is), but it has consequences:

- The agent can't model at the B-matrix level how sustained cooperation stabilizes a reciprocator. Reciprocator dynamics are handled entirely through the A matrix (likelihood conditions on last_action).
- Planning depth may be structurally uninformative because looking further ahead doesn't reveal new state transitions — the B matrix just drifts with p_switch regardless of what the agent does.
- **The flat depth curve might be a structural consequence of this design choice, not a finding about the domain.**

If you added an action-dependent B (e.g., cooperating increases probability that a reciprocator stays reciprocating), deeper planning could start to matter. That would reframe the "orthogonal augmentation" claim: affect might still be orthogonal, but depth might no longer be irrelevant.

**Options:**
- (a) Keep current design, explicitly justify in paper — "in domains where actions don't affect hidden state transitions, affect provides orthogonal value" (defensible, narrows claim)
- (b) Add action-dependent B for reciprocator dynamics, re-run experiments — tests whether depth matters when B is action-dependent (high effort, could strengthen or weaken the story)
- (c) Test both and compare — run a small experiment with action-dependent B to see if depth separates, then decide

#### Decision 2: pymdp alignment path

Andrew offered to help formalize in pymdp. Options:
- (a) **Notation only** — keep JAX code, make docs/paper match pymdp conventions. Fastest but reviewers may push back on custom implementation.
- (b) **pymdp wrapper** — use pymdp for generative model definition, keep custom JAX planning. Middle ground.
- (c) **Full pymdp** — re-implement in pymdp 1.0 with Andrew's help. Most credible for AIF community, but significant effort and may require extending pymdp for the affect mechanism.
- (d) **Keep JAX, document departures** — add explicit section to theory.md justifying each departure.

#### Decision 3: Multiplicative vs additive precision weighting

Current: `G(π) * (1 + μβ)` — multiplicative. Standard AIF would add a terminal value: `G(π) + μβ`. The multiplicative form means high-beta partners amplify the *entire* EFE, not just add a fixed bias. This is theoretically motivated (precision should scale the whole estimate, not add to it) but non-standard. Options:
- (a) Keep multiplicative, add theoretical justification
- (b) Test additive form and compare
- (c) Implement both, let experiments decide

#### Decision 4: AIF partners vs rule-based partners

Currently all partners are rule-based (cooperator, reciprocator, exploiter, random). Using AIF agents as partners would be a fundamental change — genuine multi-agent inference rather than learning about scripted opponents. This is a future direction, not a current priority, but worth discussing with Andrew as a subsequent phase.

---

### Improvement Areas

Work that can proceed in parallel, organized by category rather than sequential phases.

#### Area 1: Code Correctness Fixes

Items that don't require design decisions — just fixing known issues.

1. **Fix mean-field epistemic term** — `_rollout_policy_trust_game_mean_field()` in `core/rollout.py` line 136 uses channel ambiguity (`-expected_ambiguity`) instead of true information gain. Replace with proper expected entropy reduction. All published results use sophisticated inference (correct), so existing findings are unaffected.

2. **Single-factor documentation** — The model defines two hidden state factors (partner type + interaction context) but only infers over partner type. Context is directly observed, so this is correct — but it should be documented as a single-factor POMDP with partner-indexed beliefs, not a two-factor system requiring mean-field coordinate ascent.

#### Area 2: Test Coverage

3. **EFE unit tests** — Direct tests for EFE computation: epistemic value is positive for uncertain beliefs and approaches zero for sharp beliefs; pragmatic value aligns with C matrix preferences; terminal value adjustment works correctly; sophisticated and mean-field rollouts agree for sharp beliefs.

4. **Affective state convergence tests** — Beta converges toward 1.0 under consistent correct predictions, toward 0.0 under consistent surprise. Clinical parameter regimes produce different trajectories. Extreme surprise values don't cause numerical issues.

5. **Generative model likelihood tests** — Verify A matrix produces correct observation probabilities for each partner type under each action.

#### Area 3: Documentation & Theory

6. **Document architectural departures** — Add a section to theory.md (e.g., §3.8 "Relationship to Standard Active Inference") explicitly addressing: why single-factor inference is sufficient, why B is action-independent, why precision weighting is multiplicative, why one-step Bayes IS VFE minimization for categorical distributions.

7. **Soften depth claims pending Decision 1** — Current paper says depth is "irrelevant." If the flat curve is a structural artifact of action-independent B, the claim needs hedging.

8. **Narrow H3 framing** — Reframe precision-vs-reward-averaging as context-dependent: precision tracking benefits arise specifically when prediction error and reward dissociate (binary betrayal), not universally.

#### Area 4: Benchmark & CvC

9. **Flag CvC as early WIP** — Add clear status documentation to benchmark module. Results are proof-of-concept, not publication-ready.

10. **CvC navigation improvements** — Current BFS heuristic achieves 84-91% move success. Full scoring loop (gear → ore → hearts → aligned junctions) is incomplete. Deprioritized until core architecture is settled.

#### Area 5: Experimental Re-runs (after architecture decisions)

11. **Re-run core experiments** after any architecture changes from Decisions 1-3. Use same configs but on updated codebase. Compare against MVP results to verify findings hold.

12. **Test action-dependent B** (if Decision 1 = option b or c) — Small experiment (10 seeds, 100 rounds) to see if depth separates when B is action-dependent.

13. **Test additive precision weighting** (if Decision 3 = option b or c) — Compare multiplicative vs additive forms on default + betrayal configs.

---

## Future Directions

These are post-tightening priorities, roughly ordered:

1. **pymdp alignment** — depending on Decision 2, either notation alignment or re-implementation
2. **AIF partners** — replace rule-based partners with active inference agents for genuine multi-agent inference
3. **Human data validation** — fit model to human trust-game data from healthy participants and vmPFC-lesioned patients
4. **CoGames/CvC** — develop AIF-based navigation policy for full benchmark
5. **Richer environments** — partial observability, larger action spaces, multi-step belief cascades

## Operational Summary

- **MVP:** Complete (Phases 1-7, paper draft, CvC proof-of-concept).
- **Current focus:** Architectural tightening — fix known issues, address standard-AIF departures, make design decisions.
- **Blocking on user:** Decisions 1-4 above. Code fixes (Area 1-2) can proceed independently.
- **Paper status:** Results solid. Architecture needs justification/revision before submission to AIF venue.
- **Benchmark:** Early WIP / proof-of-concept. Not publication-ready.
