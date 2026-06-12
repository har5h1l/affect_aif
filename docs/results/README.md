# Results Documentation

This directory records interpreted result status and provenance. It is not the
raw data store.

- `current.md`: canonical interpreted evidence, headline numbers, and
  include/exclude rules for the active architecture
- `paper.md`: paper result cards and where their summaries live
- `provenance.md`: source-table and figure provenance for manuscript results
- `diagnostics.md`: retained non-paper diagnostic result cards
- `../../results/`: tracked compact public result summaries and manifests
- `../manuscript/`: manuscript source, source tables, figures, and
  paper-facing notes

Do not refresh interpreted result prose from new outputs without explicit user
approval.

## Artifact Hygiene

Large row-level result files are not assumed to be present in every checkout.
Current interpreted claims should point to `current.md`, `provenance.md`,
tracked summaries under `results/paper/` or `results/diagnostics/`, and
reproducible config paths. If a local or remote results mirror is pruned, keep
the documentation trail intact and rerun experiments before refreshing
interpreted numbers.

The public result scaffold is:

```text
results/
  paper/          compact summaries and manifests for paper evidence
  diagnostics/    compact summaries and manifests for retained non-paper probes
```

Full per-round CSVs live under `raw/` subdirectories when present; those files
are gitignored. The user-facing Drive packet can include the full `results/`
tree because tracked summaries and ignored raw files share the same canonical
folder layout.

The anonymous public Drive packet is:

<https://drive.google.com/drive/folders/1KIz2unW--qx643vBqvwD1FTOS3TgYhpS?usp=drive_link>

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
for compact CSVs that back manuscript figures. Use `provenance.md` for the
figure/source-table/result-card map.

## Public Data Routes

- `results/paper/` contains paper summaries and, when materialized locally,
  paper-needed raw files under gitignored `raw/` paths.
- `results/diagnostics/` may be compact-summary only when raw diagnostic data
  is not needed for the paper packet.
- The Drive packet is the public row-level data route; git remains the compact
  summary and provenance route.
