# Research State

## Last Updated
2026-03-19

## Session Count
5

## Current Findings

### Phase 5 (IN PROGRESS) — Clinical Sensitivity

**INBOX task completed:** Added incremental checkpoint saving to experiment runner (serial + batch). `--checkpoint-interval` CLI flag. Partial results saved after every N replications.

**Binary Stag Hunt clinical: FAILED** — Same softmax saturation as binary PD. C9 (alexithymia) and C11 (depression) produce identical payoffs to C2 (normal affect). Clinical parameter perturbations are behaviorally inert in binary games.

**Graded betrayal clinical: BREAKTHROUGH (smoke test, 5 seeds)**

Between-clinical spread: **84.9 points** (vs ~0.03 in graded default — 2830x improvement). The graded game's ambiguous EFE + betrayal's precision stress creates massive clinical differentiation:

| Variant | Payoff | vs C2 diff | d | p |
|---|---|---|---|---|
| C2 normal | 1235.9 | — | — | — |
| C9 alexithymia (alpha=0.1) | 1297.5 | +61.6 | +2.82 | 0.003 |
| C10 borderline (alpha=12, lambda=0.5) | 1212.6 | -23.3 | -0.69 | 0.199 |
| C11 depression (beta0=0.2) | 1251.1 | +15.2 | +0.33 | 0.497 |

Key finding: **Alexithymia is paradoxically protective under acute volatility.** The blunted affect (alpha=0.1) prevents overreaction to betrayal, maintaining stable investment. Borderline (volatile affect) creates late-game deterioration (d=-1.37, p=0.037 in late window). Each phenotype shows a distinct temporal signature in the betrayal response.

**Full 50-seed experiment launched** and running in background.

### Phase 6 (COMPLETE)
Bayesian model comparison. C2 decisive winner under betrayal (log10 BF=3.0).

### Phase 7 (COMPLETE)
Cross-game generalization. Augmentation generalizes under volatility across PD, Stag Hunt, Chicken.

## Auto Handoff
- **What changed:** INBOX checkpoint task done. Binary Stag Hunt clinical failed (saturation). Graded betrayal clinical shows massive between-phenotype differentiation (84.9 point spread vs 0.03 in default). Alexithymia paradoxically protective under betrayal.
- **What is still in flight:** Full 50-seed graded betrayal clinical experiment running. Results will be in `results/graded_betrayal_clinical/`.
- **What next session should do:**
  1. Check if experiment completed (look for `results/graded_betrayal_clinical/overall_analysis.csv`)
  2. If complete: analyze 50-seed results, update docs/results_tracking.md and docs/theory.md
  3. If still running: wait for completion, or check partial results
  4. Consider running Bayesian model comparison on clinical variants
  5. Document Phase 5 findings in long_term_plan.md

Model-Hint: opus

## Status
CONTINUE — graded betrayal clinical experiment running (50 seeds). Next session should check results and analyze.
