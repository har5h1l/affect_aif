# Documentation Map

Start with `README.md` for setup and runnable entry points. This directory then
splits the project documentation by job:

- `active/`: current mission, progress, blockers, and always-read operating
  state
- `handoffs/`: task-specific transfer packets, read only when named, linked,
  newly created, or task-matched
- `decisions/`: stable architecture and experiment decisions
- `theory/`: computational claims, hypotheses, and POMDP specification
- `experiment/`: experiment design and config schema
- `experiments/`: config-to-evidence manifest
- `design/`: implementation semantics and task details
- `results/`: interpreted evidence and run provenance
- `roadmap/`: forward plans, milestones, and revisit queues
- `reference/`: stable command, schema, and contract notes
- `paper/`: manuscript-facing claims, outline, figures, and reproducibility
- `operations/`: CLI and benchmark workflows
- `archive/`: stale plans and historical specs retained for traceability

For research continuation, read `active/README.md`, `active/state.md`,
`active/progress.md`, and `active/blockers.md` before scheduling more runs.
Read `handoffs/` only when the task names, links, creates, or matches a
specific handoff.
