# Blockers

## Requires Human Decision

- **H1 confirmation/design**: the old post-fix smoke read used a mismatched
  denominator, comparing carried per-partner precision/surprise state against
  active-encounter payoff. The corrected active-encounter readout restores
  surprise-over-reward dominance in the smoke, including partial correlations
  controlling active payoff and encounter count. This is still smoke evidence;
  run confirmation before manuscript use. If confirmation remains heavily
  reward/exposure-confounded, construct a balanced-exposure reliability-vs-
  reward task with matched expected payoff across partner cases.

- **H0/H2/H4 language**: payoff remains flat in smoke for these hypotheses.
  The manuscript currently uses deployment/entropy language for H0/H2 and
  allocation-reorganisation language for H4, both with `\resultp{}` placeholders
  for confirmation-scale payoff results. Decide whether to run confirmation-
  scale seeds for these or to soften language to entropy/deployment only.

- **Exp A-D review**: once the server runs complete, inspect the phenotype
  outputs before filling `\resultp{}` placeholders. Do not update the
  Section 3.6 interpretation narrative without user review of the phenotype
  metric values (see AGENTS.md rule on result interpretation).

## Current Interpretation Guardrails

- Pre-fix and bounded-error result numbers are not comparable to current
  architecture runs. Do not cite them in manuscript sections.
- Result interpretation docs (`docs/results/current.md`) should not be updated
  from new experiment outputs without asking the user first.
- The post-fix smoke numbers (H5: 1322.3 vs 1225.0; H2 entropy 8.59 vs 8.79;
  H3 local corr 0.943) are used directly in the manuscript and are the only
  confirmed numbers in the current draft.

## Technical Follow-Ups

- H5 confirmation is the top priority after Exp A-D complete. Run at 30+ seeds
  with `--workers 1` after the verification gate passes.
- H1 needs confirmation with the corrected active-aligned and partial
  model-fitness diagnostics before manuscript use. Do not promote the corrected
  smoke read directly to a publication claim.
- Complete any remaining import-boundary cleanup toward
  `scripts -> experiments -> tasks -> inferactively-pymdp`.
- After Exp A-D: run `scripts/analysis/analyze.py` on each `results/exp_*/`
  and generate the four manuscript figures specified in `docs/active/progress.md`.
- Phenotype figures (fig_alpha_sweep.pdf, fig_phenotype_quadrants.pdf,
  fig_forgiveness.pdf, fig_mixed_volatility.pdf) need to be generated and
  placed under `docs/paper/manuscript/figures/` once Exp A-D complete.

## Not Blockers (Resolved or Deferred)

- Agent-choice candidate-aggregation bug: fixed (centered precision logits).
  Post-fix smoke verifies the fix.
- H6 supplemental perturbation results: included in manuscript as
  Section 3.5, designated as supplemental computational perturbations.
- Manuscript hedging language: removed in May 31 revision; replaced with
  clean narrative + `\resultp{}` placeholders.
