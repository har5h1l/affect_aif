# Current Results

No current result interpretation is promoted in this docs-state reset. Local
`results/` CSV batches were cleared in May 2026; the Mango `server` checkout
under `~/repos/affect_aif/results/` was emptied after sync plus manual removal
of rsync-leftover dirs (sync alone does not delete remote-only paths). Do not
expect unpublished result paths to exist on disk until new runs are saved.

The next current-evidence runs should happen only after the restructure
verification gate in `docs/state/current/next_runs.md` passes. Until then, the
repository should treat the H0-H5 experiment queue as the source of truth for
current evidence.

## Current Architecture Requirement

Current evidence must use the apashea-aligned model surface:

- factorized binary controls
- policy log-priors
- optional Dirichlet learning hooks where configured
- explicit `planning_horizon = 3` variants for shallow-policy checks
- current Hesp-extension H0-H5 behavior cards

## Interpretation Guard

Before updating result interpretation from new experiment outputs, ask the user.
