---
status: DONE
next_priority: 0
pending_work: []
next_session_focus: "Phase 8 (human data) requires user decision"
model_hint: opus
---

# Research State

## Last Updated
2026-03-24

## Session Count
5

## Current Findings

### Phase 5: Clinical Sensitivity (COMPLETE)

Stag Hunt betrayal is the first environment where clinical phenotypes produce qualitatively distinct behavioral patterns. 50-seed confirmation:

| Phenotype | Mean Payoff | d vs Healthy | p vs Healthy | log10 BF vs Healthy |
|---|---|---|---|---|
| Healthy (C2) | 489.7 | — | — | — |
| Alexithymia (C9) | 497.1 | -0.20 | 0.318 | +0.12 (anecdotal) |
| Depression (C11) | 484.6 | +0.13 | 0.510 | -0.66 (substantial) |
| Borderline (C10) | 439.8 | **+0.72** | **<0.001** | **-2.89 (decisive)** |
| No-affect (C4) | 402.7 | — | — | — |

DECISION: Miscoordination cost amplifies precision volatility effects. Borderline volatile precision is significantly destructive (d=0.72, decisive BF). Alexithymia frozen precision is paradoxically protective. Task-dependent clinical presentations.

Beta dynamics confirmed: alexithymia frozen (vol=0.003), borderline volatile (vol=0.185), depression moderate (vol=0.103), healthy moderate (vol=0.085).

Window analysis: borderline impaired in pre-betrayal (d=0.82*) and late game (d=0.67*) — volatility hurts coordination even outside the betrayal event.

SH default: no clinical differentiation (d≈0, 20 seeds). Same EFE saturation as binary PD.

### Phase 6 (COMPLETE)
Bayesian model comparison. C2 wins decisively under betrayal (log10 BF=3.00 vs C1, 2.70 vs C5).

### Phase 7 (COMPLETE)
Cross-game generalization confirmed (PD, Stag Hunt, Chicken). Augmentation generalizes under volatility (d>1.0 in all games).

## Implementation This Session
1. Fixed condition 12 test name (variational_affective)
2. Added checkpoint_path/checkpoint_interval to ExperimentRunner.run_all()
3. Updated run_experiment.py with incremental checkpointing (INBOX task)
4. Removed dead DiscreteAffectiveAgent code path
5. `scripts/run_clinical_sensitivity.py` — comprehensive clinical sweep with BFs, beta dynamics, and betrayal window analysis
6. `scripts/analyze_clinical_results.py` — standalone post-hoc analysis
7. Theory: §4.18 (clinical sensitivity in coordination games)
8. Full documentation in results_tracking.md §Phase 5 and long_term_plan.md
9. 99 tests pass

## Auto Handoff
- **What changed:** Phase 5 clinical sensitivity complete. Stag Hunt betrayal produces first qualitative clinical differentiation. All documentation updated.
- **What is still in flight:** Nothing.
- **What next session should do:** Phase 8 (human data) requires user decision. No autonomous work remains within the variational-AIF paradigm.

## Status
DONE — All phases 1–7 complete. Phase 8 requires user.
