# Results Documentation

This directory records interpreted result status and provenance.

- `current.md`: current evidence status for the active architecture
- `runs/`: per-run provenance notes for completed current-architecture runs

## Artifact hygiene

May 2026: bulk `results/` outputs were cleared locally. `mango cloud sync push
affect_aif` rsyncs to `server:~/repos/affect_aif` but does not delete
**remote-only** paths under `results/`; after a local purge, remove orphan batch
dirs on the server over SSH (or they linger). If rsync updated files while git
was behind, run `git fetch` and `git reset --hard origin/master` on the server so
HEAD matches GitHub. Re-run experiments before refreshing interpreted numbers.

## Evidence Contract

A result is current only when it comes from a completed run on the current
apashea-aligned, factorized-control architecture and records enough provenance
to reproduce or audit it: config, command, seed count, date, branch or commit,
and analysis entry point.

Primary trust-task outputs should use the card-root layout documented in
`docs/experiments/manifest.md`, for example
`results/h0_openness/h0/shallow_binary/results.csv`.

Partial runs are not current evidence.

## Current Evidence

The May 18, 2026 H0-H5 queue is now the current interpreted evidence for the
supported architecture. See `docs/results/current.md` for the scorecard and
`docs/results/runs/2026-05-18-h0-h5-rerun.md` for run-level details. The full
raw row-level result CSVs remain on the Mango server because the completed
outputs are large; compact analysis artifacts are mirrored locally under
`results/`.

The May 19, 2026 H3 reallocation follow-up is recorded as a small pilot. It
updates the H3 interpretation by adding cautious reallocation and conditional
return evidence, but it should not be promoted to the same evidential level as
the May 18 H0-H5 queue without higher-replication confirmation.
