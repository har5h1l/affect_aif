# Handoffs

This directory holds task-specific transfer packets for future agents.
`docs/active/` remains the required current context and should be read first.

Read files here only when a handoff is named, linked, newly created, or
directly matched to the task. Do not sweep all handoffs by default.

Create handoffs as `YYYY-MM-DD-lowercase-kebab-slug.md`. Preserve durable
project state in `docs/active/`, stable model/experiment references in
`docs/model/` and `docs/experiments/`, interpreted evidence in
`docs/results/`, and implementation plans in `docs/superpowers/plans/`.

For server work, include tmux session, Mango process name, working directory,
command, log path, finality markers, and stop conditions. Long experiments
belong in tmux plus Mango registration, not as direct children of Codex Remote
app-server processes.
