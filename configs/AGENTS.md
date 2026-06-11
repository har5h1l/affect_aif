# AGENTS.md - configs/

TOML configs are the public experiment surface.

- Read `configs/README.md`, `docs/experiments/configs.md`, and
  `docs/experiments/paper.md` before changing maintained configs.
- Keep paper configs under `configs/paper/`, demos under `configs/demo/`,
  reviewer or smoke diagnostics under `configs/diagnostics/`, and future
  extensions under `configs/future/`.
- Use explicit `[[variants]]` and documented sweeps. Do not restore legacy
  condition IDs, old presets, or compatibility config names.
- Paper/manuscript configs should remain graded-payoff unless the user
  explicitly changes the paper evidence boundary.
- Full config runs belong on `server` via Mango/tmux. Local config work should
  use `--dry-run`, demos, or focused smoke checks unless asked otherwise.

