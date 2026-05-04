# Blockers

## Requires Human Decision

- Whether to relaunch H5 partner-selection and clinical-betrayal batches (prior
  partial `results_partial.csv` artifacts were removed in the May 2026 results
  purge).
- Whether any historical paper/archive claim should be promoted only after a
  fresh rerun on the current architecture.

## Current Interpretation Guardrails

- Historical findings are preserved in `docs/results/historical_findings.md`
  only as context.
- Prior shallow-confirm and factorial numbers are not comparable to current
  architecture runs because factorized controls and environment decoding changed.
- Result interpretation docs should not be updated from new experiment outputs
  without asking the user first.

## Technical Follow-Ups

- Complete the topology move toward `scripts -> experiments -> tasks -> aif`.
- Add import-boundary and package-surface tests for the moved structure in later
  phases.
- Record Mango sync status after branch integration work, not during this local
  docs-state reset.
