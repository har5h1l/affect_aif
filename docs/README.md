# Documentation

This tree is organized by ownership. Update the owning doc rather than copying
the same state into several places.

## Routes

- `active/`: live project state for humans and agents. Read this first before
  research, restructure, docs, experiment, result, or manuscript work.
- `overview/`: stable model surface (`core/`), optional background (`background/`),
  and extensions not in current paper evidence (`extensions/`).
- `experiments/`: config schema, runnable suites, diagnostics, and run
  procedures.
- `results/`: interpreted evidence status, provenance, and result-card policy.
- `manuscript/`: LaTeX source, rendered PDF, source tables, figures, and
  paper-facing notes.
- `handoffs/`: task-specific transfer packets; read only when named, linked,
  newly created, or directly matched to the task.

## Update Rules

- Do not duplicate live state. `active/` owns current mission, verification
  gates, run status, blockers, and next-run choices.
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
- Keep handoffs task-specific. Durable project state belongs in `active/`, not
  in a handoff.
- Prefer hard renames and direct removals. Do not keep legacy docs, deprecated
  paths, compatibility aliases, or old entry-point instructions unless the user
  explicitly asks for a compatibility bridge.

## Server And Data

Development can happen locally or remotely. Full experiments, long sweeps, and
large data-producing runs belong on `server` under detached `tmux` plus Mango
process registration. Raw per-round results are gitignored and may live locally
or on `server`; tracked docs should point to compact summaries, manifests,
configs, and source tables.

Older planning material has been folded into these routes where it is still
needed.
