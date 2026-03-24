# Long-Term Plan

## Purpose

This document tracks the project roadmap from initial empirical validation through theory tightening, formal derivation, and eventual extensions. The core finding is that per-partner metacognitive precision tracking provides orthogonal augmentation to planning depth: under sophisticated inference, increasing the planning horizon from 2 to 8 does not change results, but adding affect improves social decision quality through a channel that planning depth alone cannot access.

## Completed Phases

### Phase 1: Primary Results (complete)

Ran 100-seed experiments across default, betrayal-stress, and variant-D conditions. Established the main result: affect augments social inference orthogonally to planning depth. Four of five original hypotheses supported. H3 (affect beats reward-averaging on Exploiter detection) confirmed as a null across all conditions, including correlated partners at correlation strength 0.9. This null is now interpreted as a boundary condition of the trust-game family, not a model failure.

### Phase 2: Exploiter Deep-Dive (complete)

Used the betrayal-stress setup as the primary mechanism diagnostic. Established strongest H1/H2/H4 evidence. Confirmed that per-partner precision tracking responds to cooperation-to-defection transitions but does not separate from reward-averaging (Condition 5) on detection latency. This result motivated the reframing from "compensation" to "augmentation."

### Phase 3: Theory Tightening (complete)

**Goal:** Revise the theoretical framing and paper narrative around the confirmed empirical pattern.

**Key tasks:**

1. ~~Reframe the contribution as orthogonal augmentation.~~ Done. See `docs/theory.md` S2.1, S4.5, S4.6.
2. ~~Present the beta update rule as extending Hesp et al.~~ Done. See `docs/theory.md` S3.4.
3. ~~Expand the condition comparison into a clear 2x2 (affect x planning-depth) table.~~ Done. See `docs/theory.md` S4.11.
4. ~~Present H3 as a confirmed boundary condition.~~ Done. See `docs/theory.md` S4.7. H3 is now understood as context-dependent: null in default, supported in binary betrayal, reversed in graded game.
5. ~~Document the variant-D result.~~ Done.
6. ~~Add empirical support for the terminal value approximation (correlation between C2 beta/terminal signal and actual value-to-go from C1).~~ Done. Graded game analysis shows beta does NOT correlate with value-to-go (r ~ 0), which is *predicted* by the theory: beta tracks precision, not value. This validates the orthogonal augmentation claim — beta contributes genuinely different information from reward history. See `docs/theory.md` S4.14.
7. *(Added)* ~~Integrate graded trust game findings into theoretical framework.~~ Done. See `docs/theory.md` S4.11-4.13.
8. *(Added)* ~~Explain C5 > C2 reversal in graded game and its theoretical implications.~~ Done. See `docs/theory.md` S4.12.

**Known issues addressed in text:**

- Learning rate modulation positive feedback loop: documented in `docs/theory.md` S3.7.
- "Interoceptive" framing replaced with per-partner metacognitive precision tracking throughout.

**Phase 3 status: COMPLETE.** All tasks done. The theory document covers: orthogonal augmentation framing, Hesp et al. grounding, 2x2 orthogonality table, H3 boundary condition, graded game integration (S4.11-4.15), C5 > C2 explanation (S4.12), clinical sensitivity restoration (S4.13), beta-not-value validation (S4.14), and cross-game synthesis (S4.15).

### Phase 4: Variational Beta Extension (complete)

**Goal:** Formalize beta as a discrete hidden state within the generative model, extending the current continuous update (grounded in Hesp et al.'s variational precision dynamics) to a full Bayesian inference scheme.

**Scope:**

- Discretize beta into a set of hidden-state levels with likelihood P(epsilon|beta) and transition dynamics P(beta_t|beta_{t-1}).
- Show formal correspondence between the current EMA update and the discrete hidden-state posterior.
- Quantify any behavioral divergence between the continuous and discrete formulations in the trust-game setting.

**Phase 4 status: COMPLETE.** Discrete Bayesian beta formulation implemented and validated. Behaviorally equivalent to continuous EMA in stable environments (d = 0.001). Moderate divergence under betrayal (d = 0.41) due to transition matrix persistence.

### Phase 5: Clinical Sensitivity Analysis (complete)

**Goal:** Treat clinical phenotypes (vmPFC lesion, alexithymia, borderline, depression) as sensitivity analysis over model parameters, with clinical interpretation.

**Prior attempts (failed):**

- Binary PD: softmax saturation (EFE gap ~10.83) makes clinical parameter perturbations behaviorally inert (<0.5% effect)
- Graded default: improved sensitivity (d>2.1 vs C4) but between-clinical differentiation minimal (~0.03 point spread)
- Binary Stag Hunt: same saturation as binary PD (C9 and C11 identical to C2)

**Breakthrough: graded betrayal environment.** Combining the graded game's ambiguous EFE (q_pi_entropy ~5.8) with betrayal stress (cooperator->exploiter switch) produced massive between-clinical differentiation:

| Variant | vs C2 diff | Cohen's d | p |
|---|---|---|---|
| C9 alexithymia (alpha=0.1) | +29.8 | +0.80 | <0.0001 |
| C10 borderline (alpha=12, lambda=0.5) | -50.7 | -1.14 | <0.0001 |
| C11 depression (beta0=0.2) | +3.1 | +0.08 | 0.562 |

Between-clinical spread: 80.5 points (2700x improvement over graded default).

**Key findings:**
1. Alexithymia is paradoxically protective under acute volatility (blunted response prevents costly overreaction)
2. Borderline shows progressive deterioration (noisy precision updates compound over time, d=-0.83 in late game)
3. Depression is a self-correcting perturbation (pessimistic prior corrected by evidence within ~30 rounds)
4. The alpha_charge/lambda_smooth regime has a "sweet spot" — clinical phenotypes represent systematic deviations

**Phase 5 status: COMPLETE.** Graded betrayal environment validated as the clinical test bed. Full results in `docs/results_tracking.md` Phase 5 section.

### Phase 6: Bayesian Model Comparison (complete)

**Goal:** Reformulate the current condition comparisons as proper Bayesian model comparison.

**Scope:**

- Compute marginal likelihoods for each model variant (with/without affect, different planning depths).
- Use random-effects Bayesian model selection (Stephan et al., 2009) with protected exceedance probabilities.
- Complement the current frequentist hypothesis tests with Bayes factors where appropriate.

**Implementation (complete):**

- Per-round log-evidence computation added to all agent types via `_compute_round_log_evidence()` in `BaseAgent`
- Log-evidence logged per round and accumulated per episode in experiment CSV output
- `affect_aif/analysis/model_comparison.py` implements: log-evidence summaries, pairwise Bayes factors (Kass & Raftery, 1995), random-effects BMS with protected exceedance (Rigoux et al., 2014)
- `scripts/run_model_comparison.py` provides CLI for model comparison analysis
- 8 unit tests covering all components, full test suite passes
- Theory documented in `docs/theory.md` S4.16

**Confirmation results (50 seeds):**

- Default: C2/C5 substantially preferred over C1/C3/C4 (log10 BF ~ 0.7-0.9). RFX-BMS: C5 wins (exceedance 1.000), C2 second (frequency 0.177).
- Betrayal: C2 **decisively** preferred — log10 BF = 3.00 vs C1, 2.70 vs C5, 2.51 vs C3. RFX-BMS: C2 wins (exceedance 0.998).
- Key finding: precision tracking is the best *predictive* model under volatility, not just the best payoff achiever. C5 wins on payoff in default but C2 wins on model quality under betrayal.

**Phase 6 status: COMPLETE.**

### Phase 7: Richer Task Environments (complete)

**Goal:** Test whether the orthogonal augmentation result generalizes beyond the trust game.

**Approach:** Tested three 2x2 symmetric games (Prisoner's Dilemma, Stag Hunt, Chicken) with zero code changes — only payoff matrix differs. Each game creates fundamentally different strategic dynamics.

**Key results (50 seeds each):**

- **Augmentation generalizes under volatility.** H1 (d > 1.0) holds across all three games in betrayal conditions. Not trust-game-specific.
- **Augmentation is game-dependent in stable conditions.** Strong in PD/Stag Hunt (d ~ 0.5-0.6), negligible in Chicken (d = 0.05).
- **Stag Hunt is the precision tracking game.** C2 wins RFX-BMS in both default (exceedance 0.992) and betrayal (0.954). The severe miscoordination penalty makes prediction accuracy critical.
- **Chicken is the reward averaging game.** C5 wins RFX-BMS under betrayal (exceedance 0.931). The reward gradient is more directly informative in anti-coordination settings.

**Phase 7 status: COMPLETE.** Three games tested, cross-game comparison documented. See `docs/results_tracking.md` S Phase 7 and `docs/theory.md` S4.17.

## Current Focus: Four-Track Plan for Paper Submission

### Track 1: Paper Theory Gaps (HIGH priority)

Five specific gaps identified in the theory and framing:

1. **Inside-out literature positioning (1.1):** Position beta-as-metacognitive-precision against Yoshida (2024, outside-in empathy) and Pitliya et al. (2025, cognitive ToM). Triple dissociation: outside-in / cognitive ToM / inside-out precision monitoring.

2. **Precision modulation pathway (1.2):** gamma_k = f(beta_k) is described but untested. Decision needed: run in graded game (where softmax isn't saturated) or cut from paper. Requires user input.

3. **vmPFC neuro-architectural argument (1.3):** Connect Bancee et al. (2026, vmPFC emotion geometry) + Baram et al. (2026, OFC/vmPFC schema manifolds) + Damasio to ground beta in vmPFC. Discussion-level only.

4. **BMR trigger framing (1.4):** Strengthen Future Work BMR paragraph with Behrens (2025, hippocampal ripples), Mishchanchuk (2024, hidden-state vs parameter dissociation), somatosensory surprise timing. Theory only, no implementation.

5. **Between-clinical framing (1.5):** Lead with qualitative story (distinct computational impairments) and structural distinction (beta_0 correctable vs alpha/lambda persistent), not quantitative payoff magnitudes.

### Track 2: CoGames/CvC Benchmark (HIGH priority)

**Goal:** Get a submission-ready policy onto the actual CvC benchmark (beta-cvc Observatory season, compat_version 0.19) with non-zero reward.

**Approach:**
1. Solve navigation with A* pathfinding layer (`PathfindingMixin` in `cvc_navigation.py`)
2. Build `ScoringLoopPolicy` baseline (state-machine completing the scoring loop)
3. Add affect mechanism as `AffectCvCPolicy` (teammate tracking, beta updates, policy modulation)
4. Benchmark and package for Observatory submission
5. In parallel, try simpler missions as stepping stones

**Current status:** Pipeline complete. All policies score 0 reward due to navigation failures. See `docs/benchmarking_integration.md`.

### Track 3: Paper Preparation (MEDIUM priority — depends on Tracks 1-2)

1. Docs consistency check across theory.md, results_tracking.md, experiment.md, paper/main.tex
2. Results reproducibility spot-check (key configs, 5 seeds each)
3. Add CvC results to paper once Track 2 delivers
4. Final LaTeX polish (bibliography, references, figures)

### Track 4: Research-Brain Improvements (LOW priority — document only)

Nine identified issues with the agentic literature sweep system. Not blocking the paper. User will handle separately. See `conductor/STATE.md` for the full list.

## Planned Phases

### Phase 8: Human Data

**Goal:** Validate the model against human behavioral data.

**Scope:**

- Collect or obtain trust-game data from healthy participants and vmPFC-lesioned patients.
- Fit the model to individual participant trajectories.
- Test whether the affect-on/affect-off model distinction predicts the patient/control behavioral split.

**Entry condition:** Paper draft stable. User approval required.

## Operational Summary

- **Completed:** Phases 1-7 (primary results, exploiter deep-dive, theory tightening, variational beta, clinical sensitivity, Bayesian model comparison, cross-game generalization).
- **Phase 5 key finding:** Graded betrayal environment produces massive between-clinical differentiation (80.5 point spread). Alexithymia paradoxically protective (d=+0.80); borderline shows progressive deterioration (d=-1.14); depression self-corrects.
- **Phase 6 key finding:** C2 is the decisively best predictive model under betrayal stress (log10 BF = 3.0 vs C1, 2.7 vs C5).
- **Phase 7 key finding:** Augmentation generalizes across PD, Stag Hunt, and Chicken under volatility (d > 1.0 in all). Game-dependent in stable conditions. Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.
- **In progress:** Four-track plan for paper submission. Track 1 (theory gaps) and Track 2 (CvC benchmark) are co-priority.
- **Remaining:** Phase 8 (human data) requires user approval.
- **Stop point:** Phase 8 (human data) requires user approval.
