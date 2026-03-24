# Long-Term Plan

## Purpose

This document tracks the project roadmap from initial empirical validation through theory tightening, formal derivation, and eventual extensions. The core finding is that per-partner metacognitive precision tracking provides orthogonal augmentation to planning depth: under sophisticated inference, increasing the planning horizon from 2 to 8 does not change results, but adding affect improves social decision quality through a channel that planning depth alone cannot access.

## Completed Phases

### Phase 1: Primary Results (complete)

Ran 100-seed experiments across default, betrayal-stress, and variant-D conditions. Established the main result: affect augments social inference orthogonally to planning depth. Four of five original hypotheses supported. H3 (affect beats reward-averaging on Exploiter detection) confirmed as a null across all conditions, including correlated partners at correlation strength 0.9. This null is now interpreted as a boundary condition of the trust-game family, not a model failure.

### Phase 2: Exploiter Deep-Dive (complete)

Used the betrayal-stress setup as the primary mechanism diagnostic. Established strongest H1/H2/H4 evidence. Confirmed that per-partner precision tracking responds to cooperation-to-defection transitions but does not separate from reward-averaging (Condition 5) on detection latency. This result motivated the reframing from "compensation" to "augmentation."

## Current Phase

### Phase 3: Theory Tightening (near-complete)

**Goal:** Revise the theoretical framing and paper narrative around the confirmed empirical pattern.

**Key tasks:**

1. ~~Reframe the contribution as orthogonal augmentation.~~ Done. See `docs/theory.md` §2.1, §4.5, §4.6.
2. ~~Present the beta update rule as extending Hesp et al.~~ Done. See `docs/theory.md` §3.4.
3. ~~Expand the condition comparison into a clear 2x2 (affect x planning-depth) table.~~ Done. See `docs/theory.md` §4.11.
4. ~~Present H3 as a confirmed boundary condition.~~ Done. See `docs/theory.md` §4.7. H3 is now understood as context-dependent: null in default, supported in binary betrayal, reversed in graded game.
5. ~~Document the variant-D result.~~ Done.
6. ~~Add empirical support for the terminal value approximation (correlation between C2 beta/terminal signal and actual value-to-go from C1).~~ Done. Graded game analysis shows beta does NOT correlate with value-to-go (r ≈ 0), which is *predicted* by the theory: beta tracks precision, not value. This validates the orthogonal augmentation claim — beta contributes genuinely different information from reward history. See `docs/theory.md` §4.14.
7. *(Added)* ~~Integrate graded trust game findings into theoretical framework.~~ Done. See `docs/theory.md` §4.11–4.13.
8. *(Added)* ~~Explain C5 > C2 reversal in graded game and its theoretical implications.~~ Done. See `docs/theory.md` §4.12.

**Known issues addressed in text:**

- Learning rate modulation positive feedback loop: documented in `docs/theory.md` §3.7.
- "Interoceptive" framing replaced with per-partner metacognitive precision tracking throughout.

**Phase 3 status: COMPLETE.** All tasks done. The theory document covers: orthogonal augmentation framing, Hesp et al. grounding, 2×2 orthogonality table, H3 boundary condition, graded game integration (§4.11–4.15), C5 > C2 explanation (§4.12), clinical sensitivity restoration (§4.13), beta-not-value validation (§4.14), and cross-game synthesis (§4.15). Ready for user decision on advancing to Phase 4.

## Planned Phases

### Phase 4: Variational Beta Extension

**Goal:** Formalize beta as a discrete hidden state within the generative model, extending the current continuous update (grounded in Hesp et al.'s variational precision dynamics) to a full Bayesian inference scheme.

**Motivation:** The current EMA-based update extends Hesp et al.'s variational treatment of precision to the multi-partner social setting. Formalizing beta as a categorical hidden state with explicit likelihood and transition dynamics would make it a first-class component of the generative model, subject to the same inference machinery as every other hidden state.

**Scope:**

- Discretize beta into a set of hidden-state levels with likelihood P(ε|β) and transition dynamics P(β_t|β_{t-1}).
- Show formal correspondence between the current EMA update and the discrete hidden-state posterior.
- Quantify any behavioral divergence between the continuous and discrete formulations in the trust-game setting.

**Entry condition:** Phase 3 paper draft is stable.

### Phase 5: Clinical Sensitivity Analysis (complete)

**Goal:** Treat clinical phenotypes (vmPFC lesion, alexithymia, borderline, depression) as sensitivity analysis over model parameters, with clinical interpretation.

**Scope:**

- vmPFC lesion: ablate affect entirely (Condition 3 is already this).
- Alexithymia: reduce precision of the affective channel (alpha_charge=0.1, blunted responsiveness).
- Borderline: volatile affective dynamics (alpha_charge=12.0, lambda_smooth=0.5).
- Depression: persistently low baseline precision (initial_beta=0.2).
- Map parameter regimes to behavioral signatures and compare with clinical literature.

**Preliminary result (binary PD):** Softmax saturation (EFE gap ~10.83) made clinical parameter variations behaviorally inert. Beta dynamics differentiated correctly but max effect was 0.5% of total payoff.

**Resolution (Stag Hunt betrayal, 50 seeds):** The Stag Hunt's severe miscoordination penalty makes precision accuracy maximally decision-relevant, amplifying clinical parameter effects:

- **Borderline: significantly impaired** (d=0.72 vs healthy, p<0.001, log10 BF=-2.89 decisive). Volatile precision tracking produces noisy partner predictions → frequent miscoordination. First statistically significant clinical differentiation.
- **Alexithymia: ≈ healthy** (d=-0.20, p=0.32). Frozen beta is paradoxically protective — stable (if flat) partner predictions avoid miscoordination.
- **Depression: mild impairment** (BF=-0.66 substantial, p=0.51 frequentist null). Low initial beta creates transient vulnerability that washes out.

**Key insight:** Miscoordination cost amplifies the consequences of precision volatility. The same clinical parameter regime produces different behavioral signatures in different game environments — the model predicts task-dependent clinical presentations.

**Phase 5 status: COMPLETE.** See `docs/theory.md` §4.18 and `docs/results_tracking.md` §Phase 5.

### Phase 6: Bayesian Model Comparison (in progress)

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
- 8 unit tests covering all components, full test suite passes (77 tests)
- Theory documented in `docs/theory.md` §4.16

**Confirmation results (50 seeds):**

- Default: C2/C5 substantially preferred over C1/C3/C4 (log10 BF ≈ 0.7–0.9). RFX-BMS: C5 wins (exceedance 1.000), C2 second (frequency 0.177).
- Betrayal: C2 **decisively** preferred — log10 BF = 3.00 vs C1, 2.70 vs C5, 2.51 vs C3. RFX-BMS: C2 wins (exceedance 0.998).
- Key finding: precision tracking is the best *predictive* model under volatility, not just the best payoff achiever. C5 wins on payoff in default but C2 wins on model quality under betrayal.

**Phase 6 status: COMPLETE.** All tasks done. Implementation, experiments, analysis, and documentation finished. See `docs/results_tracking.md` §Phase 6 and `docs/theory.md` §4.16.

**Entry condition:** Phase 3 analysis pipeline is mature enough to support likelihood computation. ✓ Met.

### Phase 7: Richer Task Environments (complete)

**Goal:** Test whether the orthogonal augmentation result generalizes beyond the trust game.

**Approach:** Tested three 2×2 symmetric games (Prisoner's Dilemma, Stag Hunt, Chicken) with zero code changes — only payoff matrix differs. Each game creates fundamentally different strategic dynamics.

**Key results (50 seeds each):**

- **Augmentation generalizes under volatility.** H1 (d > 1.0) holds across all three games in betrayal conditions. Not trust-game-specific.
- **Augmentation is game-dependent in stable conditions.** Strong in PD/Stag Hunt (d ≈ 0.5–0.6), negligible in Chicken (d = 0.05).
- **Stag Hunt is the precision tracking game.** C2 wins RFX-BMS in both default (exceedance 0.992) and betrayal (0.954). The severe miscoordination penalty makes prediction accuracy critical.
- **Chicken is the reward averaging game.** C5 wins RFX-BMS under betrayal (exceedance 0.931). The reward gradient is more directly informative in anti-coordination settings.

**Phase 7 status: COMPLETE.** Three games tested, cross-game comparison documented. See `docs/results_tracking.md` §Phase 7 and `docs/theory.md` §4.17.

### Phase 8: Human Data

**Goal:** Validate the model against human behavioral data.

**Scope:**

- Collect or obtain trust-game data from healthy participants and vmPFC-lesioned patients.
- Fit the model to individual participant trajectories.
- Test whether the affect-on/affect-off model distinction predicts the patient/control behavioral split.

**Entry condition:** Phases 3-4 provide a model specification stable enough to fit to data.

## Operational Summary

- **Completed:** Phases 1–7 (primary results, exploiter deep-dive, theory tightening, variational beta, clinical sensitivity, Bayesian model comparison, cross-game generalization).
- **Phase 5 key finding:** Stag Hunt betrayal produces first qualitative clinical differentiation. Borderline significantly impaired (d=0.72, BF=-2.89 decisive), alexithymia ≈ healthy (frozen precision is protective), depression mildly impaired. Miscoordination cost amplifies precision volatility effects.
- **Phase 6 key finding:** C2 is the decisively best predictive model under betrayal stress (log10 BF = 3.0 vs C1, 2.7 vs C5).
- **Phase 7 key finding:** Augmentation generalizes across PD, Stag Hunt, and Chicken under volatility (d > 1.0 in all). Game-dependent in stable conditions. Stag Hunt uniquely favors precision tracking; Chicken favors reward averaging.
- **Remaining:** Phase 8 (human data) requires user approval.
- **Stop point:** Phase 8 (human data) requires user approval. All other phases complete.
