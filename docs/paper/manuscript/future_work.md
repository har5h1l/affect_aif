# Future Work And Two-Week Follow-Up Menu

## Highest-Value Follow-Up Before Deadline

### 1. Global-Beta Ablation

Question: is partner-specific affective precision necessary, or would one
global beta summary explain the same behavior?

Why it matters: the manuscript's architectural novelty is partner-local affect.
Right now, partner specificity is a premise of the model and indirectly useful
in H4, but it has not been directly compared to a global-affect control.

Implemented starting point:

- `affect = "global_beta"` now shares one beta tracker across partners while
  preserving partner-local POMDP beliefs.
- `configs/trust/hypotheses/h3_locality/global_beta_smoke.toml`
  provides a first locality/interference smoke run.
- The next queued global-beta discovery batch extends this to model-fitness,
  deployment, partner-choice, betrayal, and lesion-family probes.
- Optional H5 abrupt/gradual stress check if time allows.
- Primary readout: partner choice, entropy, payoff, and precision-reward versus
  precision-surprise association.

Risk: the first global-beta run is smoke-scale only; do not promote it to manuscript
evidence until the design and diagnostics are reviewed.

### 2. Focused Shock-Shape Gradient

Question: is H5 failure driven by temporal abruptness rather than generic
overconfidence?

Why it matters: the H5 precision-sensitivity follow-up suggests shock shape is
the right axis. This would strengthen the boundary-condition story without
another broad sweep.

Suggested design:

- Hold default affect fixed.
- Vary scheduled stance-switch abruptness or number/timing of pre-switch
  confirmations.
- Use 20-30 seeds per variant depending on manuscript role: 20 seeds is enough
  for a supplemental shock-shape figure, while 30 seeds is reserved for a main
  behavioural confirmation.
- Report payoff, entropy, reencounters, payoff-on-return, wrong-type rate, and
  overconfident-wrong rate.

Risk: new configs should be easy, but interpretation must be approved before
updating result docs.

### 3. Figure-Quality Composite Script

Question: can the current evidence be made visually clear enough for the paper?

Why it matters: this may help more than another experiment. Current figures are
useful diagnostics but not final manuscript panels.

Suggested design:

- One script under `scripts/analysis/` or `docs/paper/manuscript/` that reads
  copied source tables and emits 4-5 clean composite PNG/PDF figures.
- Use existing analysis outputs only; do not recompute experiment results.
- Panels: H2 deployment, H1 model fitness, H5 boundary, H5 shock shape, H6
  supplement.

Risk: low scientific risk, high manuscript value.

## Longer-Term Work

- Human or behavioral validation: test whether beta-like reliability signals
  predict human partner choice or return behavior.
- Model comparison: compare partner-specific beta against global beta, reward
  averaging, and belief-only baselines.
- Variational beta: implement beta as a fuller auxiliary state rather than the
  current external discrete tracker.
- Richer social environments: noisy observations, correlated partners, and
  multi-focal agents interacting with each other.
- Clinical modeling: only after stronger validation; current variants are
  computational perturbations, not diagnoses.

## Current Recommendation

For a two-week deadline, prioritize reviewing the global-beta discovery batch and
deciding whether global beta needs a manuscript paragraph. Avoid another broad
hyperparameter sweep until these structural probes are interpreted.
