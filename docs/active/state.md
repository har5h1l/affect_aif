# Current Mission

Rebaseline the H0-H6 evidence narrative on the official
`inferactively-pymdp==1.0.0` runtime after shifting the affect update to
Hesp-style partner-action surprisal. The active follow-up surface now combines
the main H0-H5 mechanism tests with global-beta controls, so partner-local and
shared affective precision can be compared in the same rerun pass.

## Scope

- Use official `inferactively-pymdp==1.0.0` as the supported active-inference runtime.
- Keep trust-game model construction, affective precision tracking, experiment
  runners, logging, and analysis in project-owned task and experiment modules.
- Do not reintroduce a custom active-inference engine or supported `aif/` runtime.
- Keep scripts as the canonical experiment and analysis entry points.
- Preserve the Hesp-extension behavior-card spine in
  `docs/theory/hypotheses.md`.
- Keep current docs aligned with the supported H0-H6 experiment surface.
- Treat pre-May-27 bounded-error results as historical/provisional until
  rebaseline runs complete under `-log P(observed partner action)`.

## Constraints

- Do not treat partial detached rerun outputs as current evidence.
- Do not update result interpretation from new experiment outputs without user
  approval.
- Do not add orchestration or deployment scripts to this repo; use Mango for
  remote VM, sync, and merge flows.
- Do not reintroduce the removed external benchmark integration.
- Re-run the verification gate in `docs/active/progress.md` immediately
  before scheduling any further full experiment reruns.

## Completion State

- The active runtime cutover is complete for official
  `inferactively-pymdp==1.0.0` plus project-owned trust-task wrappers and
  external affective precision tracking.
- The May 18 H0-H5 queue is complete but now historical/provisional because the
  affect update has changed to log-surprisal.
- The manuscript draft has been revised toward a traditional results/discussion
  structure, with clearer game and generative-model descriptions.
- H6 `global_beta` support, a locality/interference smoke config, and generic
  analysis outputs for cross-partner interference have been added.
- A two-seed H6 smoke run completed at `--workers 1`; it verifies the new
  condition and analysis path but should not yet be treated as manuscript
  evidence.
- The H6 discovery batch completed at
  `results/h6_global_beta_discovery_20260525/` and standalone analysis outputs
  exist under each `h6/<experiment_id>/analysis/` directory. Treat these as
  documented discovery outputs, not promoted manuscript evidence.
- The focused H6 locality/interference probe completed at
  `results/h6_global_beta_locality_probe_20260526/` with five seeds and
  `--workers 1`. It is mixed discovery evidence: local beta preserves a cleaner
  model-fitness signal, but global beta has higher aggregate payoff in this
  small probe. Do not promote H6 to a necessity claim without a revised design.
- The H6 focal-switch follow-up completed at
  `results/h6_global_beta_focal_switch_probe_20260526/` with five seeds and
  `--workers 1`. It replicated the mixed H6 pattern: local beta preserved the
  cleaner model-fitness signal, while global beta had higher aggregate payoff.
- The core H0/H1/H2/H3/H4 configs now include `global_beta` variants where
  relevant, so the next rerun can evaluate locality alongside the main
  mechanism spine.
- The manuscript now includes script-generated figure panels for model fitness,
  deployment/social choice, betrayal boundary, shock shape, and
  precision-dynamics phenotypes. It compiles to 11 LNCS pages.

## Current Handoff

Read this folder in order: `state.md`, `progress.md`, then `blockers.md`.
Paper-facing evidence remains in `docs/paper/manuscript/` and interpreted
results remain in `docs/results/`.

The next active experiment lane is the log-surprisal rebaseline queue in
`docs/active/progress.md`. Run smoke-scale H0-H4/H6 checks first, then promote
only stable readouts to confirmation-scale reruns.

Do not create a separate handoff document; keep the live handoff in this
`docs/active/` state/progress surface.

## Stop Conditions

- A required verification command fails in a way that suggests a design problem
  rather than a local fix.
- Shallow reruns on the current architecture contradict H0 by showing no affect
  benefit in any policy-space regime.
- Clinical reruns on the current architecture qualitatively invert the expected
  phenotype ordering.
