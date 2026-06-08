# Blockers

## Requires Human Decision

- **H1 reviewer-control decision**: the June 6 confirmation supports
  surprise-over-reward model-fitness tracking after active-encounter controls,
  while payoff favors no-affect. This is sufficient for the current manuscript
  framing. If reviewers ask for a stronger reward/exposure decomposition, use
  the bounded diagnostic ladder in `progress.md`: balanced-exposure graded
  reliability spine -> reward-matched graded spine -> strict reward-neutral H1.

- **H0/H2/H4 language**: payoff remains flat in smoke for these hypotheses.
  The manuscript has been softened to deployment/entropy language for H0/H2
  and allocation-reorganisation language for H4 rather than broad payoff
  advantage claims. Decide whether these diagnostic claims still need
  confirmation-scale seeds for manuscript support, or whether they can remain
  as smoke-scale mechanism readouts while H1 and H5 carry the main
  confirmation evidence.

- **Exp D discrimination caution**: Exp D has been interpreted narrowly. The
  whole-episode `discrimination_index` does not support the originally stronger
  sensitivity-specificity prediction, so the manuscript now states the
  boundary: higher gain can raise payoff while worsening discrimination and
  false-positive suppression. Do not restore the older stronger claim without a
  new diagnostic.

## Current Interpretation Guardrails

- Pre-fix and bounded-error result numbers are not comparable to current
  architecture runs. Do not cite them in manuscript sections.
- The user approved interpretation updates on June 6 for Exp C, H5, H1, and
  related paper cleanup. Resume the ask-first rule for future new outputs.
- The post-fix smoke numbers remain diagnostic provenance. The current paper
  uses 30-seed H1/H5 confirmation values and reviewed 20-seed Exp A-D phenotype
  source tables.

## Technical Follow-Ups

- No live affect_aif experiment is currently blocking the manuscript packet.
- H5 confirmation reached structural finality under
  `results/paper/betrayal_adaptation/raw/h5/betrayal_reallocation_confirm/`
  and has been interpreted in the paper packet.
- H1 confirmation reached structural finality under
  `results/paper/model_fitness/raw/h1/reliability_vs_reward_confirm/`
  and has been interpreted in the paper packet. The controlled H1 configs are
  reviewer-driven diagnostic surfaces, not current evidence.
- Exp A-D generic analyses and manuscript figures now exist, including
  `fig_forgiveness.pdf`, and have been reviewed for the current manuscript
  framing. Future changes should preserve the non-monotonic phenotype language.

## Not Blockers (Resolved or Deferred)

- Agent-choice candidate-aggregation bug: fixed (centered precision logits).
  Post-fix smoke verifies the fix.
- Full pytest gate: clean on June 2 after replacing oversized full-H5
  integration/theory fixtures with tiny scheduled-switch fixtures. Evidence:
  `308 passed, 7 skipped, 74 warnings` in
  `/tmp/affect_aif_full_pytest_20260602_final.log`; static gates also passed.
- H6 supplemental perturbation results: included in manuscript as
  Section 3.5, designated as supplemental computational perturbations.
- Manuscript evidence-boundary language: originally aligned through `07b31d0`;
  June 6 updates now include final H1, H5, and Exp A-D interpretations.
- Exp C/D pre-run metric alignment: fixed through `e66fc16` before those
  scripts started; Exp C recovery and Exp D false-positive readouts now match
  the manuscript plan.
- Exp B compact metric/figure alignment: fixed while Exp B was still running.
  Raw trajectories are not obsolete, and final compact outputs have since been
  regenerated with the updated readout contract.
- Exp A compact metric/figure alignment: fixed after Exp A raw outputs had
  already been written. Raw trajectories are not obsolete, and final compact
  outputs have since been regenerated so the 1--30 early-exploitation window,
  entropy trajectory panel, and confidence intervals are reflected in
  `metrics.csv`, source tables, and `fig_alpha_sweep.pdf`.
- Exp C/D figure-contract alignment: fixed before Exp C/D had started. Exp C
  now emits the beta recovery trajectory columns needed by the forgiveness
  figure, and Exp D now emits beta and P0-selection trajectory snapshots needed
  by the mixed-volatility figure. No interruption or rerun is required.
- Exp A/B betrayal readout language: resolved at the compact-analysis layer.
  Exp A/B raw trajectories are complete and do not need deletion or raw rerun;
  source tables now include explicit post-betrayal P0 selection and
  high-investment commitment rates so `betrayal_recovery_time` does not need to
  carry withdrawal-language claims by itself.
- Import-boundary cleanup: the historical trust-task benchmark arena was
  removed from the active public surface, and `tasks/` is guarded against
  imports from `experiments` or `analysis`.
