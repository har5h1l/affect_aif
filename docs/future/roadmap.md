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
- **Discrete beta:** The native runtime uses `DiscreteBetaState` inside the standard affective path.
- **CvC benchmark:** Early WIP / proof-of-concept. Navigation-only baseline works (BFS + wall detection, 84-91% move success). Reward results minimal. Not publication-ready.
- **Paper:** Draft complete (theory gaps addressed, results integrated, figures included). Architecture needs justification of departures from standard AIF before submission.

### Completed Phase Reference

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 4 | Discrete Beta Reformulation | Complete; native helper supported |
| Phase 5 | Clinical Parameter Sensitivity | Complete |
| Phase 6 | Bayesian Model Comparison | Complete |
| Phase 7 | Cross-Game Generalization | Complete |

**Phase 4 details:** Discrete Bayesian beta tracking is implemented through `DiscreteBetaState` and deployed through partner-local gamma.

**Phase 5 details:** Graded betrayal environment identified as the critical test bed. Between-clinical spread: 80.5 points (2700x improvement over graded default). Alexithymia paradoxically protective (d=+0.80); borderline shows progressive deterioration (d=-1.14); depression self-corrects within ~30 rounds.

**Phase 6 details:** C2 (precision tracking) is the decisively best predictive model under betrayal stress (log10 BF = 3.0 vs C1, 2.7 vs C5). In stable conditions, C5 wins at the population level.

**Phase 7 details:** Augmentation generalizes under volatility across PD, Stag Hunt, and Chicken (d > 1.0 in all). Game-dependent in stable conditions. Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.

### Current Direction: Post-Restructure Reframe

Action-dependent stance is now implemented and the first post-restructure experiment family is in hand. The current task is to reframe the hypothesis story around what the new architecture actually shows, clean up stale artifacts, and finish the remaining runs on the action-dependent trust-game surface.

**Operational summary:**
- MVP: Complete (Phases 1-7, paper draft, CvC proof-of-concept).
- Current focus: Post-restructure reframe — action-dependent stance results in hand, reframing hypotheses and completing remaining experiments.
- Paper status: Binary trust-game results need updated framing before the next paper iteration.
- Benchmark: Early WIP / proof-of-concept. Not publication-ready.

---

## 2. Architectural Decisions Status

These track what remains open after the action-dependent stance redesign.

### Decision 1: The B matrix question (resolved)

This decision is now resolved. The supported trust-game path includes action-dependent stance transitions, and the current results show that depth redundancy persists as a structural property of the binary trust-game policy landscape.

Implication for the paper: document action-dependent stance as the supported architecture and present G compression / depth redundancy as a domain finding of the binary-action task, not as a bug that still needs fixing.

### Decision 2: pymdp alignment path (removed)

The pymdp hard cutover is the supported path. Future runtime work should extend trust-task wrappers around official `inferactively-pymdp==1.0.0`, not revive a project-owned active-inference engine.

### Decision 3: Partner-local precision deployment (resolved)

The native runtime deploys affect by setting partner-local pymdp policy precision:
`gamma_k = gamma_base / E[beta_k]`.

### Decision 4: AIF partners vs rule-based partners

Currently all partners are rule-based (cooperator, reciprocator, exploiter, random). Using AIF agents as partners would be a fundamental change — genuine multi-agent inference rather than learning about scripted opponents. This is a future direction, not a current priority, but worth discussing with Andrew as a subsequent phase.

### Improvement Areas (can proceed in parallel)

Work that can proceed without waiting for the decisions above, organized by category:

**Area 1: Code Correctness Fixes**
1. **Native pymdp boundary checks** — keep policy/state inference inside official `pymdp.Agent` and keep repository code focused on matrix construction, partner banking, beta tracking, and logging.
2. **Factorized-state documentation** — document the native `type × stance` hidden state and `own_action` control factor so theory, tests, and matrix construction stay aligned.

**Area 2: Test Coverage**
3. **Native policy tests** — Direct tests that `pymdp.Agent.infer_policies(...)` receives task matrices with aligned preferences, controls, and partner-local priors.
4. **Affective state convergence tests** — Beta moves toward low-beta/high-precision levels under consistent correct predictions and toward high-beta/low-precision levels under consistent surprise. Clinical parameter regimes produce different trajectories.
5. **Generative model likelihood tests** — Verify A matrix produces correct observation probabilities for each partner type under each action.

**Area 3: Documentation & Theory**
6. **Document architectural departures** — Add a section to theory.md explicitly addressing: why beta remains outside the POMDP state space, why partner-local `gamma_k` is the deployment path, and why one-step categorical Bayes is the closed-form VFE optimum for state inference.
7. **Soften depth claims after stance redesign** — Current paper says depth is "irrelevant." The action-dependent stance path needs a narrower claim: depth can matter, while beta supplies orthogonal partner-local precision.
8. **Narrow H3 framing** — Reframe precision-vs-reward-averaging as context-dependent: precision tracking benefits arise specifically when prediction error and reward dissociate (binary betrayal), not universally.

**Area 4: Benchmark & CvC**
9. **Flag CvC as early WIP** — Add clear status documentation to benchmark module. Results are proof-of-concept, not publication-ready.
10. **CvC navigation improvements** — Current BFS heuristic achieves 84-91% move success. Full scoring loop (gear → ore → hearts → aligned junctions) is incomplete. Kept as a future direction, not an active track.

**Area 5: Experimental Re-runs (after architecture decisions)**
11. **Re-run core experiments** after native-runtime changes. Use the maintained configs and confirm result schemas still match analysis.
12. **Stress-test action-dependent stance** — Small experiment (10 seeds, 100 rounds) to check whether depth separates under stance-switch scenarios.
13. **Gamma-channel sensitivity** — Compare `gamma`, `alpha_charge`, `beta_persistence`, and `initial_beta` sweeps on default + betrayal configs.

---

## 3. Active Tracks

These tracks are the immediate actionable work after the restructure.

### Track 1: Paper Theory Gaps (active, HIGH priority)

Specific gaps in theory, related work, and empirical framing that must be addressed before paper submission.

**1.1 Inside-Out Literature Positioning**

The core novelty — beta as metacognitive precision monitoring ("how reliable is my model of partner B?") — needs explicit positioning against three alternative approaches:
- **Yoshida (2024)** — empathic coupling = outside-in (model partner's internal states)
- **Pitliya et al. (2025)** — ToM = cognitive model of other's inference
- **This work** — inside-out metacognitive monitoring of one's own social inference channel

The triple dissociation (outside-in empathy / cognitive ToM / inside-out precision monitoring) is the cleanest positioning. Action: update the next manuscript draft and `docs/theory/theory.md` Section 4.

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

### Track 2: Paper Preparation (active, MEDIUM priority)

**2.1 Docs Consistency Check**
Verify agreement across `docs/theory/hypotheses.md`, `docs/theory/theory.md`,
`docs/experiment/design.md`, and `docs/experiments/manifest.md` on explicit
variant IDs, key numbers, hypothesis status, and phase descriptions.

**2.2 Results Reproducibility Spot-Check**
Spot-check key TOML specs (5 seeds each): the H0 openness, H3 betrayal-choice,
and any horizon-sweep successor specs listed in `docs/experiments/manifest.md`.

**2.3 Final LaTeX Polish**
Bibliography completeness, figure/table numbering, equation references, add Yoshida/Sennesh/Ramstead/Bancee/Baram, check for TODO/FIXME.

---

## 4. Future Directions Beyond Current Tracks

These are post-tightening priorities, roughly ordered by likely sequencing.

1. **AIF partners** — replace rule-based partners with active inference agents for genuine multi-agent inference rather than scripted opponents.
2. **Human data validation** — fit model to human trust-game data from healthy participants and vmPFC-lesioned patients.
3. **CoGames/CvC** — develop AIF-based navigation policy for full benchmark, beyond the rule-based TeammateReliabilityPolicy.
4. **Richer environments** — partial observability, larger action spaces, multi-step belief cascades.

### Phase 8: Human Data Fitting (future, requires user decision)

**Goal:** Fit model parameters to individual human participants' trust game behavior.

**Scope:**
- Obtain trust-game behavioral data from healthy participants and vmPFC-lesioned patients
- Estimate individual-difference parameters (`alpha_charge`, `beta_persistence`, `initial_beta`) from action sequences
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
    |---> Track 2: Paper Preparation (2.1-2.3) <- ACTIVE
    |
    +---> CvC / CoGames <- FUTURE DIRECTION
    |
    +---> Phase 8: Human Data <- FUTURE (requires user)
```
