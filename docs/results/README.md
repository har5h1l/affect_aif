# Results Documentation

This directory records interpreted result status and provenance.

- `current.md`: current evidence status for the active architecture
- `runs/`: per-run provenance notes for completed current-architecture runs
  (directory may be absent until the first post-purge run is documented)

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

## Post-Restructure Queue

No new full statistical run has been interpreted after the reusable-core/task
package restructure. The next current-evidence queue and exact commands live in
`docs/state/current/next_runs.md` and should be copied into per-run provenance
notes under `docs/results/runs/` after each completed run.
