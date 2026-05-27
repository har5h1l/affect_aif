# Results Documentation

This directory records interpreted result status and provenance.

- `current.md`: current evidence status for the active architecture
- `runs/`: per-run provenance notes for completed current-architecture runs
- `../paper/`: submission-readiness, claims, outline, literature positioning,
  and figure/table plan

## Artifact Hygiene

Large row-level result files are not assumed to be present in every checkout.
Current interpreted claims should point to compact provenance notes under this
directory and to reproducible config paths. If a local or remote results mirror
is pruned, keep the documentation trail intact and rerun experiments before
refreshing interpreted numbers.

## Evidence Contract

A result is current only when it comes from a completed run on the current
factorized-control architecture and records enough provenance
to reproduce or audit it: config, command, seed count, date, branch or commit,
and analysis entry point.

Primary trust-task outputs should use the card-root layout documented in
`docs/experiments/manifest.md`, for example
`results/h0_openness/h0/shallow_binary/results.csv`.

Partial runs are not current evidence.

## Current Evidence

As of May 27, 2026, the canonical affect update uses Hesp-style partner-action
surprisal, `-log P(observed partner action)`, with
`sigma_0_sq = (-log 0.5)^2`. Earlier interpreted results were produced with the
bounded action-error proxy. Keep them as historical/provisional evidence until
the current H0-H6 configs are rerun.

The May 18, 2026 H0-H5 queue is now historical interpreted evidence for the
supported architecture. See `docs/results/current.md` for the scorecard and
`docs/results/runs/2026-05-18-h0-h5-rerun.md` for run-level details. Full
row-level CSVs may live outside lightweight checkouts because completed outputs
are large; compact analysis artifacts and provenance notes should be kept with
the repository when practical.

The May 19, 2026 H3 reallocation follow-up is recorded as a small pilot. The
May 2026 H1/H3 split confirmation is now the targeted follow-up evidence: it
promotes H1 as a confirmed model-fitness readout and keeps H3 as a stress
boundary condition rather than an affective recovery win. The May 2026 H3
precision-sensitivity follow-up narrows that boundary condition: generic
caution knobs do not rescue abrupt betrayal, while gradual betrayal makes
default affect nearly payoff-neutral relative to no-affect/lesioned baselines.
The May 26, 2026 H4 social-choice pair check is recorded as a five-seed
replication of the partner-choice deployment pattern, not as a 30-seed
confirmation.

The May 2026 H6 global-beta discovery batch is recorded in
`docs/results/runs/2026-05-26-h6-global-beta-discovery.md`. It is current
discovery evidence for planning the next locality/interference experiment, but
it is not promoted to the main H0-H5 evidence hierarchy. The focused five-seed
locality/interference probe is recorded in
`docs/results/runs/2026-05-26-h6-locality-probe.md`; it is also discovery-scale
and currently argues for softening, not strengthening, any necessity claim
about partner-local beta.
