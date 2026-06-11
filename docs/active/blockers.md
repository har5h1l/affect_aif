# Blockers

## Requires Human Decision

- **H1 reviewer-control decision**: the June 6 binary confirmation is now
  appendix/diagnostic only because the saturated binary regime is uninformative for the main
  behavioral mechanism. If reviewers ask for a stronger reward/exposure
  decomposition, use the bounded diagnostic ladder in `progress.md`:
  balanced-exposure graded reliability spine -> reward-matched graded spine ->
  strict reward-neutral H1.

- **H0/H2/H4 language**: payoff remains flat in smoke for these hypotheses.
  The manuscript has been softened to deployment/entropy language for H0/H2
  and allocation-reorganisation language for H4 rather than broad payoff
  advantage claims. The completed 30-seed binary H4 confirmation is
  diagnostics-only and should not be used as the paper Section 3.3
  confirmation. If H4 needs confirmation-scale manuscript support, run the
  graded paper partner-selection config.

- **Mixed-volatility extension boundary**: Exp D is implemented and
  operationally valid, but it is no longer reported as paper evidence. It opens
  a distinct heterogeneous-volatility/change-detection question and should stay
  in `configs/future/` unless a future study defines that target explicitly.

## Current Interpretation Guardrails

- Pre-fix and bounded-error result numbers are not comparable to current
  architecture runs. Do not cite them in manuscript sections.
- The user approved interpretation updates on June 6 for Exp C, H5, H1, and
  related paper cleanup; H1 has since been demoted to diagnostics. Resume the
  ask-first rule for future new outputs.
- The post-fix smoke numbers, binary H1 confirmation, and binary H4
  confirmation remain diagnostic provenance. The current paper uses 30-seed H5
  confirmation values and reviewed 20-seed Exp A-C profile source tables.

## Technical Follow-Ups

- No live affect_aif experiment is currently blocking the manuscript packet.
- Before making the repository public, remove or consolidate internal-only
  Markdown routing files that are not useful to external readers. The subtree
  `AGENTS.md` files are helpful during cleanup, but they should be reviewed
  against the public README/docs surface before release.
- Before making the repository public, remove or archive internal planning
  transcripts such as `docs/superpowers/plans/` and `docs/superpowers/specs/`.
  They mention old paths, local/server cleanup details, and stale public-surface
  designs; keep only current docs that name present-day configs and result
  cards.
- Keep old-run provenance out of the tracked public docs surface unless it has
  been rewritten to point at current `configs/paper/`, `configs/diagnostics/`,
  or `configs/future/` paths. Historical run notes with removed config paths
  should live in local or server archives instead.
- H5 confirmation reached structural finality under
  `results/paper/04_betrayal_adaptation/raw/betrayal_adaptation/betrayal_adaptation/`
  and has been interpreted in the paper packet.
- H1 confirmation reached structural finality under
  `results/diagnostics/model_fitness/raw/h1/reliability_vs_reward_confirm/`
  and is retained as appendix/diagnostic provenance. The controlled H1 configs
  are reviewer-driven diagnostic surfaces, not current evidence.
- H4 binary confirmation reached structural finality under
  `results/diagnostics/social_allocation/raw/partner_choice_confirm_20260609/`
  and is retained as diagnostic provenance. It is not the graded paper
  partner-selection surface.
- Exp A-C generic analyses and manuscript figures now exist, including
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
  June 6 updates now include final H1, H5, and Exp A-C interpretations.
- Exp C/D pre-run metric alignment: fixed through `e66fc16` before those
  scripts started; Exp C recovery matches the manuscript plan, while Exp D is
  now retained as a future extension.
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
  figure. Exp D remains available only as a future extension under
  `configs/future/mixed_volatility.toml`; manuscript Exp D assets were removed.
- Exp A/B betrayal readout language: resolved at the compact-analysis layer.
  Exp A/B raw trajectories are complete and do not need deletion or raw rerun;
  source tables now include explicit post-betrayal P0 selection and
  high-investment commitment rates so `betrayal_recovery_time` does not need to
  carry withdrawal-language claims by itself.
- Import-boundary cleanup: the historical trust-task benchmark arena was
  removed from the active public surface, and `tasks/` is guarded against
  imports from `experiments` or `analysis`.
