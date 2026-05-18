# Blockers

## Requires Human Decision

- Whether to treat the May 18 H0-H5 rerun as pilot evidence and launch a
  higher-replication confirmation, or first revise the H3 betrayal design.
- Whether H3 should be framed as a boundary condition for affective precision
  under miscalibrated confidence, or rerun after adding cleaner reallocation and
  return-latency readouts.

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
- Full row-level May 18 result CSVs are still server-resident because the raw
  completed outputs are roughly 27 GB. Compact analysis artifacts are mirrored
  locally.
