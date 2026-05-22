# Results Documentation

This directory records interpreted result status and provenance.

- `current.md`: current evidence status for the active architecture
- `runs/`: per-run provenance notes for completed current-architecture runs

## Artifact Hygiene

Large row-level result files are not assumed to be present in every checkout.
Current interpreted claims should point to compact provenance notes under this
directory and to reproducible config paths. If a local or remote results mirror
is pruned, keep the documentation trail intact and rerun experiments before
refreshing interpreted numbers.

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
`docs/results/runs/2026-05-18-h0-h5-rerun.md` for run-level details. Full
row-level CSVs may live outside lightweight checkouts because completed outputs
are large; compact analysis artifacts and provenance notes should be kept with
the repository when practical.

The May 19, 2026 H3 reallocation follow-up is recorded as a small pilot. The
May 2026 H1/H3 split confirmation is now the targeted follow-up evidence: it
promotes H1 as a confirmed model-fitness readout and keeps H3 as a stress
boundary condition rather than an affective recovery win.
