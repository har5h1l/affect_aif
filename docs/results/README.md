# Results Documentation

This directory records interpreted result status and provenance. It is not the
raw data store.

- `current.md`: canonical interpreted evidence, headline numbers, and
  include/exclude rules for the active architecture
- `paper.md`: paper result cards and where their summaries live
- `diagnostics.md`: retained non-paper diagnostic result cards
- `archive.md`: archive policy for historical or incomplete material
- `cleanup/`: local/server cleanup manifests from the public repo cleanup
- `../../results/`: tracked compact public result summaries and manifests
- `runs/`: per-run provenance notes for completed current-architecture runs
- `../manuscript/`: manuscript source, source tables, figures, and
  paper-facing notes

Do not refresh interpreted result prose from new outputs without explicit user
approval. Active run status and finality gates belong in `docs/active/`;
task-specific transfer notes belong in `docs/handoffs/` when needed.

## Artifact Hygiene

Large row-level result files are not assumed to be present in every checkout.
Current interpreted claims should point to compact provenance notes under this
directory, tracked summaries under `results/paper/` or `results/diagnostics/`,
and reproducible config paths. If a local or remote results mirror is pruned,
keep the documentation trail intact and rerun experiments before refreshing
interpreted numbers.

The public result scaffold is:

```text
results/
  paper/          compact summaries and manifests for paper evidence
  diagnostics/    compact summaries and manifests for retained non-paper probes
  archive/        ignored historical or incomplete material
```

Full per-round CSVs live under `raw/` subdirectories when present locally or on
`server`; those files are gitignored. The user-facing Drive packet can include
the full local `results/` tree because tracked summaries and ignored raw files
share the same canonical folder layout.

## Evidence Contract

A result is current only when it comes from a completed run on the current
factorized-control architecture and records enough provenance
to reproduce or audit it: config, command, seed count, date, branch or commit,
and analysis entry point.

Primary trust-task outputs should use the public result-card layout documented
in `results/README.md`. Paper cards must point to `configs/paper/...`;
diagnostic cards must point to `configs/diagnostics/...`.

Partial runs are not current evidence.

## Current Evidence Route

Use `current.md` for the interpreted scorecard, headline numbers, and
include/exclude rules. Use `results/paper/*` and `results/diagnostics/*` for
compact tracked summaries and provenance. Use `docs/manuscript/source_tables/`
for compact CSVs that back manuscript figures.

## Local Vs Server

- Local `results/paper/` should contain the paper-needed raw files plus tracked
  summaries. It is the folder intended for a Drive handoff.
- Local `results/diagnostics/` may be compact-summary only when raw diagnostic
  data is not needed for the paper packet.
- Server `results/` keeps the fuller diagnostic and archive payloads after
  cleanup. Do not delete server raw data unless a later cleanup manifest says
  exactly what was removed and why.
