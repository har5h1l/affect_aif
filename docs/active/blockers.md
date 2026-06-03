# Blockers

## Requires Human Decision

- **H1 confirmation/design**: the old post-fix smoke read used a mismatched
  denominator, comparing carried per-partner precision/surprise state against
  active-encounter payoff. The corrected active-encounter readout restores
  surprise-over-reward dominance in the smoke, including partial correlations
  controlling active payoff and encounter count. This is still smoke evidence;
  run confirmation before manuscript use. If confirmation remains heavily
  reward/exposure-confounded, use the bounded diagnostic ladder now documented
  in `progress.md`: corrected confirmation -> balanced-exposure graded
  reliability spine -> reward-matched graded spine -> strict reward-neutral H1.
  Only treat H1 as model-level failure if the strict reward-neutral diagnostic
  also fails.

- **H0/H2/H4 language**: payoff remains flat in smoke for these hypotheses.
  The manuscript has been softened to deployment/entropy language for H0/H2
  and allocation-reorganisation language for H4 rather than broad payoff
  advantage claims. Decide whether these diagnostic claims still need
  confirmation-scale seeds for manuscript support, or whether they can remain
  as smoke-scale mechanism readouts while H5 and H1 carry the main
  confirmation burden.

- **Exp A-D review**: once the server runs complete, inspect the phenotype
  outputs before filling `\resultp{}` placeholders. Do not update the
  Section 3.6 interpretation narrative without user review of the phenotype
  metric values (see AGENTS.md rule on result interpretation). The original
  `affect_aif_exp_abcd_20260529` run stopped during Exp B and has been
  superseded by `affect_aif_exp_recovery_20260603`.

## Current Interpretation Guardrails

- Pre-fix and bounded-error result numbers are not comparable to current
  architecture runs. Do not cite them in manuscript sections.
- Result interpretation docs (`docs/results/current.md`) should not be updated
  from new experiment outputs without asking the user first.
- The post-fix smoke numbers (H5: 1322.3 vs 1225.0; H2 entropy 8.59 vs 8.79;
  H3 local corr 0.943) are used directly in the manuscript and are the only
  confirmed numbers in the current draft.

## Technical Follow-Ups

- Monitor `affect_aif_exp_recovery_20260603`. It runs verification first, then
  Exp A analyze-only, Exp B resume, Exp D, and Exp C, with generic analysis
  after each experiment stage. Treat `RECOVERY_DONE` in
  `results/exp_abcd_recovery_20260603_logs/run.log` plus final
  `results.csv`/`metrics.csv`/`manifest.json`/`README.md` files for Exp A-D as
  the recovery finality gate.
- H5 confirmation is the top priority after Exp A-D complete. Run at 30+ seeds
  with `--workers 1` after the verification gate passes.
- H1 needs confirmation with the corrected active-aligned and partial
  model-fitness diagnostics before manuscript use. Do not promote the corrected
  smoke read directly to a publication claim. The new controlled H1 configs are
  diagnostic surfaces, not current evidence.
- After Exp A-D: run `scripts/analysis/analyze.py` on each `results/exp_*/`
  and generate the four manuscript figures specified in `docs/active/progress.md`.
- Phenotype figures (fig_alpha_sweep.pdf, fig_phenotype_quadrants.pdf,
  fig_forgiveness.pdf, fig_mixed_volatility.pdf) need to be generated and
  placed under `docs/paper/manuscript/figures/` once Exp A-D complete.

## Not Blockers (Resolved or Deferred)

- Agent-choice candidate-aggregation bug: fixed (centered precision logits).
  Post-fix smoke verifies the fix.
- Full pytest gate: clean on June 2 after replacing oversized full-H5
  integration/theory fixtures with tiny scheduled-switch fixtures. Evidence:
  `308 passed, 7 skipped, 74 warnings` in
  `/tmp/affect_aif_full_pytest_20260602_final.log`; static gates also passed.
- H6 supplemental perturbation results: included in manuscript as
  Section 3.5, designated as supplemental computational perturbations.
- Manuscript evidence-boundary language: aligned through `07b31d0`; H1 and H5
  are framed as confirmation targets, and phenotype outputs remain pending
  `\resultp{}` placeholders rather than interpreted results.
- Exp C/D pre-run metric alignment: fixed through `e66fc16` before those
  scripts started; Exp C recovery and Exp D false-positive readouts now match
  the manuscript plan.
- Exp B compact metric/figure alignment: fixed while Exp B was still running.
  Raw trajectories are not obsolete, but the final Exp B compact outputs must
  be regenerated with `--analyze-only` after Exp A-D finality so the metrics,
  source tables, and phenotype radar figure use the updated readout contract.
- Exp A compact metric/figure alignment: fixed after Exp A raw outputs had
  already been written. Raw trajectories are not obsolete, but the Exp A
  compact outputs must be regenerated with `--analyze-only` after Exp A-D
  finality so the 1--30 early-exploitation window, entropy trajectory panel,
  and confidence intervals are reflected in `metrics.csv`, source tables, and
  `fig_alpha_sweep.pdf`.
- Exp C/D figure-contract alignment: fixed before Exp C/D had started. Exp C
  now emits the beta recovery trajectory columns needed by the forgiveness
  figure, and Exp D now emits beta and P0-selection trajectory snapshots needed
  by the mixed-volatility figure. No interruption or rerun is required.
- Import-boundary cleanup: benchmark orchestration moved to
  `benchmarks.trust_backend`, and `tasks/` is guarded against imports from
  `experiments`, `analysis`, or `benchmarks`.
