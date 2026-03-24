---
status: CONTINUE
next_priority: 1
pending_work:
  - "50-seed SH betrayal experiment running (results/clinical_sensitivity_betrayal)"
  - "20-seed SH default experiment running (results/clinical_sensitivity_default)"
  - "Analyze confirmation results, compute Bayes factors, update docs"
  - "Update theory.md §4.13 and results_tracking.md with SH clinical findings"
next_session_focus: "Check experiment completion, analyze 50-seed results, document findings"
model_hint: opus
---

# Research State

## Last Updated
2026-03-24

## Session Count
5

## Current Findings

### Phase 5: Clinical Sensitivity in Stag Hunt (IN PROGRESS)

DECISION: Stag Hunt betrayal is the first environment where clinical phenotypes produce qualitatively distinct behavioral patterns. Binary PD and SH default both suffer from softmax saturation.

**Smoke test results (5 seeds, SH betrayal):**

| Phenotype | Condition | Mean Payoff | d vs Healthy | d vs No-Affect | log10 BF vs Healthy |
|---|---|---|---|---|---|
| Healthy | C2 | 471.6 | — | — | — |
| Alexithymia | C9 | 493.8 | -0.39 | +5.20 | +0.93 (substantial) |
| Borderline | C10 | 391.4 | +1.02 | -0.15 | -5.26 (decisive against) |
| Depression | C11 | 476.2 | -0.08 | +4.24 | -0.29 (anecdotal) |
| No-affect | C4 | 399.6 | — | — | — |

DECISION: Borderline phenotype (volatile precision) performs BELOW no-affect baseline in SH betrayal. This is the key clinical finding — volatile precision is actively destructive when miscoordination penalty is severe.

**Beta dynamics confirm clinical signatures:**
- Alexithymia: frozen beta (std=0.004) — blunted as intended
- Borderline: volatile beta (std=0.222, range=0.901) — wild swings as intended
- Depression: moderate dynamics (std=0.107), starts low
- Healthy: moderate dynamics (std=0.085)

**SH default:** No clinical differentiation (d≈0 for all phenotypes vs healthy). Same softmax saturation as binary PD.

### Phase 6 (COMPLETE)
See prior session notes. Bayesian model comparison implemented and validated.

### Phase 7 (COMPLETE)
See prior session notes. Cross-game generalization confirmed.

## Implementation This Session
1. Fixed condition 12 test name (variational_affective)
2. Added checkpoint_path/checkpoint_interval to ExperimentRunner.run_all()
3. Updated run_experiment.py with incremental checkpointing (INBOX task)
4. `scripts/run_clinical_sensitivity.py` — comprehensive clinical sweep with BFs and beta dynamics
5. 99 tests pass

## Experiments In Flight
- `results/clinical_sensitivity_betrayal/` — 50 seeds × 4 phenotypes × SH betrayal
- `results/clinical_sensitivity_default/` — 20 seeds × 4 phenotypes × SH default

## Auto Handoff
- **What changed:** Phase 5 clinical sensitivity now running on Stag Hunt betrayal. Smoke test (5 seeds) shows clear clinical differentiation — borderline below no-affect, alexithymia and depression above no-affect. This is the first environment with qualitative clinical separation.
- **What is still in flight:** 50-seed SH betrayal and 20-seed SH default experiments running in background.
- **What next session should do:** Check if experiments completed (look for all_clinical.csv in output dirs). If done, analyze 50-seed results and update docs. If not done, wait or re-run.

NEXT: Analyze 50-seed confirmation results when experiments complete.

## Status
CONTINUE
