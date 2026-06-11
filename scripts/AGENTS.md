# AGENTS.md - scripts/

Scripts are supported CLI entry points, not private one-off launchers.

- Read `scripts/README.md` and the matching docs under `docs/experiments/` or
  `docs/results/` before changing script behavior.
- Keep experiment execution under `scripts/experiment/run.py` and config
  inspection under `scripts/experiment/inspect.py`.
- Keep post-hoc analysis under `scripts/analysis/`.
- Do not add wrapper scripts, compatibility launchers, or deployment scripts
  when a documented command can be updated directly.
- If a command-line interface changes, update `scripts/README.md`,
  `README.md`, and the relevant experiment/result docs.

