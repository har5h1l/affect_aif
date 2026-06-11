# AGENTS.md - tasks/

This subtree owns task mechanics for the trust game.

- Read `docs/overview/core/pomdp.md` and `docs/overview/core/affective_precision.md`
  before changing generative-model matrices, payoffs, partner dynamics,
  beta/gamma handling, or runtime update order.
- Keep policy and state inference inside official `pymdp.Agent` objects.
  Project code may construct matrices, hold partner-local runtime state, and
  update external affective precision.
- Do not import from `experiments/` or `analysis/`.
- Prefer direct removals or renames over legacy aliases when changing public
  task APIs.
- Run focused task/runtime tests after behavior changes; broaden to the active
  verification gate for shared runtime changes.

