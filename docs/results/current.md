# Current Results

No current result interpretation is promoted in this docs-state reset. Local
`results/` CSV batches were cleared in May 2026; the Mango `server` checkout
under `~/repos/affect_aif/results/` was emptied after sync plus manual removal
of rsync-leftover dirs (sync alone does not delete remote-only paths). Do not
expect paths cited in older docs to exist on disk until new runs are saved.

The next current-evidence runs should happen only after the restructure
verification gate in `docs/state/current/next_runs.md` passes. Until then, the
repository should treat prior paper, archive, and conductor-reported outputs as
historical context unless a user explicitly asks to analyze them as historical
artifacts.

## Current Architecture Requirement

Current evidence must use the apashea-aligned model surface:

- factorized binary controls
- policy log-priors
- optional Dirichlet learning hooks where configured
- conditions 9 and 10 for tau=3 shallow-policy checks
- current Hesp-extension H1-H7 hypotheses

## Interpretation Guard

Before updating result interpretation from new experiment outputs, ask the user.
