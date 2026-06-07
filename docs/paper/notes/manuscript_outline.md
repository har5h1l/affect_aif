# Manuscript Outline

Synced to the current LNCS source in `docs/paper/manuscript/sections/`.
Incoming edits (explicit POMDP subsection, partner-implementation paragraph) are
not yet in the `.tex` files; this outline reflects what is already written.

## Title

Partner-Specific Affective Precision in Social Active Inference

## Abstract (as written)

- Affect regulates how decisively beliefs are expressed in action (commitment,
  not inference content).
- Active inference formalises affect as metacognitive model-fitness precision.
- Social confidence is relational: per-partner model-fitness and action-confidence
  budgets.
- Results framing: predictability not valence; action sharpening not belief
  quality; engagement reorganisation; abrupt change exposes temporal dependency;
  gain and prior define computational trust-calibration profiles.

## Introduction

1. **Prediction vs commitment.** Social cognition requires forming expectations
   and deciding how decisively to act on them; most formal accounts address only
   the first.
2. **Affect as commitment regulator.** Beyond valence/arousal as experience,
   affect can assign action-relevant weight to inferred beliefs.
3. **Active inference and Hesp et al.** Variational inference, EFE policy
   evaluation, endogenous $\beta$ / model fitness via affective charge.
4. **Social extension.** Relational confidence requires partner-local precision,
   not a single global budget.
5. **Three research questions** (end of intro):
   - Model reliability vs payoff; belief quality vs action confidence.
   - Precision-weighted commitment under partner change and alternatives.
   - How gain $\alpha$ and prior over model fitness shape trust-revision profiles.

## Methods (as written)

- **Focal agent only** runs full active inference; four partners with hidden
  type and disposition (Methods opening; partner-side implementation paragraph
  still to be added explicitly).
- Trust game: binary, graded, partner-choice regimes; payoff table; up to 200
  rounds (120 for abrupt betrayal confirmation).
- Per-partner generative models: $s_k = (\text{type}, \text{disp})$,
  $o_k = (\text{act}, \text{pay})$; official `pymdp`; payoff as observation
  modality.
- Partner-local affective precision: action surprisal, $\phi_k$, categorical
  $q(\beta_k)$, $\gamma_k = \gamma_{\text{base}} / \mathbb{E}[\beta_k]$.
- External auxiliary tracker limitation flagged in Methods and Discussion.
- Tracked-only lesion; centred cross-partner logits (Eq. centered_logits).
- Simulation scale: 20 seeds (phenotypes/figures), 30 seeds (central
  confirmations), 120-round betrayal episode.

## Results (five linked claims)

The manuscript organises results around five claims, not the H-card numbering:

1. **Precision tracks predictability, not partner value** (`sec:model_fitness`).
   Action surprisal; locality probe correlations (0.943 vs 0.110); global-beta
   dilution.
2. **Behavioural gains through action sharpening** (`sec:deployment`). Tracked-only
   dissociation; metacognitive not epistemic; open graded entropy/payoff numbers.
3. **Partner engagement reorganises around reliability** (`sec:partner_choice`).
   Entropy and selection shifts; flat aggregate payoff at current scale.
4. **Abrupt betrayal reveals temporal structure** (`sec:betrayal`). Lower policy
   entropy and higher joint accuracy at confirmation scale, with a small and
   uncertain payoff advantage; temporal dependency, not superior reward seeking.
5. **Precision dynamics as individual differences** (`sec:phenotypes`). Clinical-style
   perturbations; $\alpha$ sweep; phenotype quadrants; forgiveness; mixed-volatility
   discrimination. Exp C separates reengagement from confidence restoration.

## Discussion (as written)

- **Affect as social metacognition** vs theory-of-mind (Pitliya; Ruiz-Serra).
  Tracks confidence in own behavioural model, not partner mental states.
- **Individual differences / phenotype programme.** $\alpha$ and prior control
  speed, amplitude, asymmetry of confidence revision; not validated clinical
  categories.
- **Lesion supports deployment.** Tracked-only rules out $\beta_k$ as extra
  reward/observation signal.
- **Betrayal temporal dependency.** Benefit when confidence redirects quickly;
  risk when stale; link to volatility/change-detection literature.
- **Limitations:** external $\beta_k$; **scripted partners** (not reciprocal AIF);
  predictive phenotypes pending human validation.
- **Future directions:** human fitting; global-$\beta$ ablation; richer ecology +
  explicit ToM.

## Conclusion (as written)

Separates predicting partner behaviour from deciding how confidently to act.
Evidence: reliability tracking, metacognitive deployment, temporal dependency
under change; $\alpha$ and prior as phenotype parameters for individual-difference
research.

## Evidence Mapping (H-cards → manuscript sections)

| H-card | Manuscript section |
|---|---|
| H1 model fitness | §3.1 predictability |
| H2 deployment | §3.2 action sharpening |
| H4 social allocation | §3.3 engagement reorganisation |
| H5 betrayal | §3.4 temporal structure |
| H3 locality | §3.1 global-beta paragraph; Discussion global-$\beta$ |
| H6 / Exp A–D | §3.5 perturbations; §3.6 phenotypes |
| H0 openness | Underpins §3.2 graded open-regime readouts |

## Limitations (paper-facing)

- Simulation-only; scripted parameterized partners; external beta tracker.
- Phenotype taxonomy predictive, not validated.
- H1, H5, and Exp A--D have been interpreted in the current manuscript; no
  numeric experiment placeholder remains.
- Do not claim reciprocal multi-agent AIF or clinical diagnosis.

## Conclusion (packet-level)

Partner-local affective precision is a metacognitive deployment mechanism for
social action confidence. Current manuscript evidence supports mechanism and
boundary conditions at the stated seed scales; human validation and reciprocal
AIF partners remain future work.
