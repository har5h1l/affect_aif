# AGENTS.md - experiments/

This subtree owns experiment orchestration around the trust task.

- Read `docs/experiments/README.md`, `docs/experiments/configs.md`, and
  `docs/experiments/running.md` before changing config expansion, runner
  behavior, logging, progress reporting, or batch execution.
- Paper evidence uses `experiments/trust/` with one focal active-inference
  agent against scripted environment-side partners.
- `experiments/multifocal/` is tested future work; do not route paper configs
  through it unless the paper scope is explicitly changed.
- Keep `ExperimentConfig` as a runtime adapter derived from expanded TOML specs.
  Do not reintroduce numeric condition IDs, old presets, or legacy wrappers.
- Expensive or full-scale experiment runs belong on `server` via Mango and
  tmux. Local runs should be demos, dry-runs, or focused verification unless
  the user asks otherwise.

