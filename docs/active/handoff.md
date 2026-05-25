# Handoff

## Current State

The project is in write-up stabilization. The supported story is
partner-specific affective precision as a model-fitness/deployment signal in a
repeated trust-game simulation, with abrupt betrayal as a boundary condition.

## Read First

1. `docs/active/state.md`
2. `docs/active/progress.md`
3. `docs/paper/claims_and_evidence.md`
4. `docs/results/current.md`
5. `docs/experiments/manifest.md`

## Repository Shape

- Trust configs remain under `configs/trust/hypotheses/`; no paper-specific
  config folder exists.
- Benchmark configs are trust-task arena configs under `configs/benchmark/`.
- Paper-facing docs live in `docs/paper/` with no supplement subfolder.
- Stale plans/specs live in `docs/archive/`.
- The removed external benchmark integration is not part of the current
  supported surface.

## Next Research Thread

Do not run broad new experiments by default. Start by drafting or tightening
the manuscript narrative. If a follow-up is needed, prefer a narrow H3
boundary-condition run that answers a specific reviewer-style question about
abrupt versus gradual betrayal or precision caution. H5 should stay a dynamics
phenotype claim unless the paper elevates payoff claims.

## Verification Gate

Before interpreting new outputs or pushing final changes:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
git diff --check
```
