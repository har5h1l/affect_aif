# Current Mission

Stabilize the current H0-H5 evidence narrative on the official
`inferactively-pymdp==1.0.0` runtime, with active handoff docs kept aligned to
the supported trust-task wrappers, external affective precision tracking, and
canonical script-driven experiments. The active follow-up surface is H6
locality/interference: a global-beta ablation that asks whether partner-local
precision is doing work beyond a shared model-fitness tracker.

## Scope

- Use official `inferactively-pymdp==1.0.0` as the supported active-inference runtime.
- Keep trust-game model construction, affective precision tracking, experiment
  runners, logging, and analysis in project-owned task and experiment modules.
- Do not reintroduce a custom active-inference engine or supported `aif/` runtime.
- Keep scripts as the canonical experiment and analysis entry points.
- Preserve the Hesp-extension behavior-card spine in
  `docs/theory/hypotheses.md`.
- Keep current docs aligned with the supported H0-H6 experiment surface.
- Treat the May 19 H3 reallocation run as a small follow-up pilot. Use the
  completed H1/H3 confirmation batch as the current targeted follow-up evidence.
- Treat H6 global-beta outputs as smoke/discovery evidence until the user
  explicitly approves changing manuscript interpretation.

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
- The May 18 H0-H5 queue is complete and interpreted in
  `docs/results/current.md`.
- The manuscript draft has been revised toward a traditional results/discussion
  structure, with clearer game and generative-model descriptions.
- H6 `global_beta` support, a locality/interference smoke config, and generic
  analysis outputs for cross-partner interference have been added.
- A two-seed H6 smoke run completed at `--workers 1`; it verifies the new
  condition and analysis path but should not yet be treated as manuscript
  evidence.

## Stop Conditions

- A required verification command fails in a way that suggests a design problem
  rather than a local fix.
- Shallow reruns on the current architecture contradict H0 by showing no affect
  benefit in any policy-space regime.
- Clinical reruns on the current architecture qualitatively invert the expected
  phenotype ordering.
