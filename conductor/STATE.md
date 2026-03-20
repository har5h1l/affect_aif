# Research State

## Last Updated
2026-03-19

## Session Count
5

## Current Findings

### Phase 5 (COMPLETE) — Clinical Sensitivity

**Binary Stag Hunt clinical: FAILED** — Same softmax saturation as binary PD.

**Graded betrayal clinical: SUCCESS (50 seeds)**

Between-clinical spread: **80.5 points** (vs ~0.03 in graded default — 2700x improvement).

| Variant | vs C2 diff | Cohen's d | p |
|---|---|---|---|
| C9 alexithymia (alpha=0.1) | +29.8 | +0.80 | <0.0001 |
| C10 borderline (alpha=12, lambda=0.5) | -50.7 | -1.14 | <0.0001 |
| C11 depression (beta0=0.2) | +3.1 | +0.08 | 0.562 |

Key findings:
1. Alexithymia paradoxically protective under acute volatility (blunted response prevents overreaction)
2. Borderline shows progressive deterioration (d=-0.83 in late game, noisy precision compounds)
3. Depression self-corrects within ~30 rounds (initial condition, not dynamical perturbation)
4. The (alpha, lambda) parameter space has a "sweet spot" — clinical phenotypes are deviations

### Phase 6 (COMPLETE)
Bayesian model comparison. C2 decisive winner under betrayal (log10 BF=3.0).

### Phase 7 (COMPLETE)
Cross-game generalization. Augmentation generalizes under volatility across PD, Stag Hunt, Chicken.

### Infrastructure
- Added incremental checkpoint saving to experiment runner (serial + batch)
- `--checkpoint-interval` CLI flag for `run_experiment.py`
- Stag Hunt clinical configs (3), graded betrayal clinical configs (3), analysis scripts (2)

## Auto Handoff
- **What changed:** Phase 5 complete. Graded betrayal identified as the critical environment for clinical sensitivity. All three phenotypes characterized with 50-seed confirmation runs. Documentation updated across theory.md, results_tracking.md, and long_term_plan.md.
- **What is still in flight:** Nothing.
- **What next session should do:** Phase 8 (human data) requires user decision. All autonomous phases complete.

## Status
DONE — Phases 5, 6, 7 complete. Phase 8 requires user decision.
