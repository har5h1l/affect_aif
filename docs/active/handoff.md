# Handoff

## Current State

The project is in write-up stabilization plus targeted H6 discovery. The
supported story is
partner-specific affective precision as a model-fitness/deployment signal in a
repeated trust-game simulation, with abrupt betrayal as a boundary condition.
The new follow-up question is whether partner-local beta matters beyond a
single shared global beta tracker.

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

Do not run broad new experiments by default. Start by reviewing the H6
global-beta smoke and deciding whether the locality/interference design needs a
small tweak before any 3-5 seed follow-up. H5 should stay a dynamics phenotype
claim unless the paper elevates payoff claims.

## Latest Work

- Added `affect = "global_beta"` as a supported trust variant. It uses one
  shared beta posterior, preserves partner-local POMDP beliefs, and applies the
  shared beta-derived gamma to all partner policies.
- Added `configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml`
  for `none`, `precision`, `tracked_only`, and `global_beta`.
- Added standalone analysis outputs:
  `cross_partner_interference_summary.csv` and
  `global_vs_local_beta_summary.csv`.
- Fixed `affective_movement_summary` so beta range is temporal movement per
  seed rather than within-round cross-partner spread.
- Revised the LNCS manuscript away from hypothesis-table framing, added clearer
  trust-game/generative-model exposition, rewrote limitations as model
  limitations, and rendered a 9-page PDF at
  `docs/paper/manuscript/manuscript_draft.pdf`.

## Latest Smoke Run

Command:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml --output-dir results --batch-name global_beta_locality_smoke_quick_20260525 --workers 1
```

Completed results:

```text
results/global_beta_locality_smoke_quick_20260525/h6/global_beta_smoke/results.csv
results/global_beta_locality_smoke_quick_20260525/h6/global_beta_smoke/analysis/
```

This was two seeds, 40 rounds, horizon 2. Treat it as smoke/provenance only.
The analysis now shows `global_beta` temporal movement
(`mean_beta_range = 0.4647`) and writes the H6 locality tables, but these
outputs are not yet part of the manuscript evidence hierarchy.

## Verification Gate

Before interpreting new outputs or pushing final changes:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
git diff --check
```
