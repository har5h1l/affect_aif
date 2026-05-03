# Current Mission

Re-ground affect_aif around a reusable JAX-based `aif/` core, task packages,
current Hesp-extension hypotheses, canonical script-driven experiments, and
docs/state steering.

## Scope

- Preserve `aif/` as the reusable active-inference core.
- Move trust-game semantics toward task packages without changing scientific
  behavior inside topology-only phases.
- Replace the old H1-H5 narrative with the Hesp-extension H1-H7 spine in
  `docs/theory/hypotheses.md`.
- Keep scripts as the canonical experiment and analysis entry points.
- Salvage useful conductor, archive, and paper context into current docs before
  deleting stale surfaces.

## Constraints

- Do not treat pre-apashea, pre-restructure, or partial detached rerun outputs
  as current evidence.
- Do not update result interpretation from new experiment outputs without user
  approval.
- Do not add orchestration or deployment scripts to this repo; use Mango for
  remote VM, sync, and merge flows.
- Re-run the verification gate in `docs/state/current/next_runs.md` immediately
  before scheduling full experiment reruns.

## Completion State

- `master` has been fast-forwarded through the reusable-core/task-package
  restructure.
- Local verification passed on `master` after the fast-forward merge.
- The cleaned workspace was synced to the Mango `server` target, with targeted
  removal of stale remote-only repo surfaces left behind by the non-deleting
  rsync path.
- The next research action is the post-restructure experiment queue in
  `docs/state/current/next_runs.md`.

## Stop Conditions

- A required verification command fails in a way that suggests a design problem
  rather than a local fix.
- Shallow reruns on the current architecture contradict H2 by showing no affect
  benefit in any policy-space regime.
- Clinical reruns on the current architecture qualitatively invert the expected
  phenotype ordering.
