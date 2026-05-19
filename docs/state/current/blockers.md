# Blockers

## Requires Human Decision

- No immediate blocker. Current steering is to pause experiments and consolidate
  the results narrative.
- Optional later decision: whether to run higher-replication H1 and H3
  split-readout confirmation after the write-up narrative stabilizes.

## Current Interpretation Guardrails

- Prior shallow-confirm and factorial numbers are not comparable to current
  architecture runs because factorized controls and environment decoding changed.
- Result interpretation docs should not be updated from new experiment outputs
  without asking the user first, unless the current user request explicitly asks
  to interpret and update docs.

## Technical Follow-Ups

- Complete the topology move toward `scripts -> experiments -> tasks -> aif`.
- Add import-boundary and package-surface tests for the moved structure in later
  phases.
- The server checkout currently retains the current/provenance-bearing result
  batches under `results/`. Older pilot, incomplete, and duplicate local result
  directories were removed during cleanup.
