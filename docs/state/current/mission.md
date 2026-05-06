# Current Mission

Re-ground affect_aif around official `inferactively-pymdp==1.0.0`, trust-task
wrappers, external affective precision tracking, canonical script-driven
experiments, and docs/state steering.

## Scope

- Use official `inferactively-pymdp==1.0.0` as the supported active-inference runtime.
- Keep trust-game model construction, affective precision tracking, experiment
  runners, logging, and analysis in project-owned task and experiment modules.
- Do not reintroduce a custom active-inference engine or supported `aif/` runtime.
- Keep scripts as the canonical experiment and analysis entry points.
- Preserve the Hesp-extension behavior-card spine in
  `docs/theory/hypotheses.md`.
- Keep current docs aligned with the supported H0-H5 experiment surface.

## Constraints

- Do not treat partial detached rerun outputs as current evidence.
- Do not update result interpretation from new experiment outputs without user
  approval.
- Do not add orchestration or deployment scripts to this repo; use Mango for
  remote VM, sync, and merge flows.
- Re-run the verification gate in `docs/state/current/next_runs.md` immediately
  before scheduling full experiment reruns.

## Completion State

- The active runtime cutover targets official `inferactively-pymdp==1.0.0` plus
  project-owned trust-task wrappers and external affective precision tracking.
- The next research action is the H0-H5 experiment queue in
  `docs/state/current/next_runs.md` after the focused verification gate passes.

## Stop Conditions

- A required verification command fails in a way that suggests a design problem
  rather than a local fix.
- Shallow reruns on the current architecture contradict H0 by showing no affect
  benefit in any policy-space regime.
- Clinical reruns on the current architecture qualitatively invert the expected
  phenotype ordering.
