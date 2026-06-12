# Documentation

This tree is organized by public reader task. Update the owning doc rather than
copying the same state into several places.

## Routes

- `overview/`: stable model surface (`core/`), optional background (`background/`),
  and model context.
- `experiments/`: config schema, runnable suites, diagnostics, and run
  procedures.
- `results/`: interpreted evidence status, provenance, and result-card policy.
- `manuscript/`: LaTeX source, rendered PDF, source tables, figures, and
  paper-facing notes.

## Update Rules

- Do not duplicate interpreted evidence. `results/current.md` owns headline
  evidence and include/exclude rules; manuscript notes point back to it.
- Do not update result interpretation from new outputs without explicit user
  approval. It is fine to record operational finality, paths, commands, and
  provenance separately from interpretation.
- If model assumptions change, update `overview/` and the matching experiment
  docs in the same change.
- If config or script behavior changes, update `experiments/`, root
  `README.md`, and any affected subtree README.
- If manuscript claims or statistics change, verify against
  `results/current.md` and `manuscript/source_tables/`, then sync manuscript
  notes and figure/table notes.
- Prefer hard renames and direct removals. Do not keep legacy docs, deprecated
  paths, compatibility aliases, or old entry-point instructions unless the user
  explicitly asks for a compatibility bridge.

## Data

Raw per-round results are gitignored and can be regenerated from
`configs/paper/` or obtained from the public Drive packet. Tracked docs point
to compact summaries, manifests, configs, and source tables.

Older planning material has been folded into these routes where it is still
needed.
