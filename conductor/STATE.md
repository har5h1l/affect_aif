---
status: READY
next_priority: 1
model_hint: sonnet
---

# Research State

## Last Updated
2026-04-14 (Session 17 — post-restructure analysis handoff)

## Session Count
17

## Current Direction
Post-restructure reframe. Action-dependent stance experiments (H1, H2, H4) are complete on new architecture. Key finding: G compression is structural — depth is redundant in action-dependent trust games. Affect signal is pooled across depths in current results, masking effect at calibrated (tau=1,2) horizons. Need targeted reanalysis + remaining experiments (H5, clinical).

## What's Been Done This Session

### Architectural restructuring (prior sessions)
- Action-dependent partner stance implemented in B[1]: cooperate/defect actions produce different stance transition matrices
- Package restructured: flat root-level modules, beta tracking external to POMDP state
- Core experiments rerun: H1 factorial (160k rows), H2 lesion (80k rows), H4 betrayal (48k rows)

### Post-restructure analysis (this session)
- **G compression confirmed structural**: Policy entropy 0.37 (tau=1) → 3.90 (tau=8). G range 2.0 → 9.6. Matching tau=1 entropy at tau=8 requires gamma≈41 — exponential scaling. Fixed gamma=1.0 IS standard AIF. Do not change.
- **Depth inversion confirmed**: tau=1 beats tau=8 by ~37 points, d=0.82, p<1e-8
- **Affect effect pooled**: d=0.15-0.26 across all depths, not significant. Expected — softmax saturated at deep horizons
- **Lesion dissociation**: d=0.26, p=.07. Needs retest at tau=1,2
- **Betrayal recovery**: d=0.22, p=.13. Same issue

### Key decisions made
- pymdp: removed from roadmap entirely
- CvC: deprioritized to future work
- Gamma scaling: NOT implementing (non-standard AIF)
- Decision 1 (B matrix): RESOLVED — action-dependent stance is correct and in place

## Pending Work (Phases)

### Phase 1: Cleanup [NOT STARTED]
- Delete `results/clinical_run/` (pre-restructure, 20 reps, wrong arch)
- Delete `results/h5_selection/h5_partner_selection/results_partial.csv`
- Update `docs/future/roadmap.md`: resolve Decision 1, remove pymdp, deprioritize CvC
- Run `python -m pytest tests/ -v` — confirm clean

### Phase 2: Hypothesis Reframe [NOT STARTED]
- Update `docs/experiment/design.md` Section 1 and hypothesis framing (see MISSION.md)
- Update `docs/experiment/results.md` Status Note
- New framing: G compression is H1, affect augmentation is H2, lesion is H3, betrayal is H4, partner selection is H5

### Phase 3: Targeted Re-Analysis [NOT STARTED]
- H1 shallow reanalysis: filter results.csv to conditions 1-4 (tau=1,2), compute affect d
- H2 lesion reanalysis: lesion dissociation at tau=4
- H4 betrayal window: effect size in post-switch rounds
- Save outputs to `results/reanalysis/`

### Phase 4: New Experiments [NOT STARTED]
- Create `configs/shallow_affect_confirm.json` (conditions [1,2,3,4] + lesioned preset, 100 reps)
- H5 partner selection: fresh full run
- Clinical betrayal: first run on new architecture
- Clinical phenotypes: first run on new architecture

### Phase 5: Analysis + Docs [NOT STARTED]
- Run analysis on each new experiment
- Update hypothesis scorecard in results.md
- Flag any surprising finding before updating narrative

## Experiment Status

| Experiment | Config | Status | Rows | Notes |
|---|---|---|---|---|
| H1 factorial | h1_depth_affect_factorial.json | COMPLETE | 160k | All 8 conditions, 100 reps |
| H2 lesion | h2_lesion_dissociation.json | COMPLETE | 80k | Conditions 5,6 + presets |
| H4 betrayal | h4_betrayal_recovery.json | COMPLETE | 48k | Conditions 5,6 + presets |
| H5 selection | h5_partner_selection.json | INCOMPLETE | 6.4k | 32 seeds condition 5 only — DELETE and rerun |
| Clinical betrayal | clinical_betrayal.json | NOT RUN | — | New arch, run in Phase 4 |
| Clinical phenotypes | clinical_phenotypes.json | NOT RUN | — | New arch, run in Phase 4 |
| Shallow confirm | shallow_affect_confirm.json | NOT CREATED | — | Create + run in Phase 4 |

## Auto Handoff

- **What changed:** Post-restructure experiments complete. G compression confirmed structural. Decision: fixed gamma=1.0 with full enumeration is standard AIF, no fix needed. Depth inversion is a domain finding, not a bug.
- **What is still in flight:** Phases 1-5 not started. See pending work above.
- **What next session should do:** Start at Phase 1 — cleanup then reframe then re-analyze then new experiments. Read MISSION.md fully before starting.
- **Key risk:** If shallow-depth affect effect is also weak (d<0.3 at tau=1), flag immediately — this would change the paper story fundamentally.

## Status
READY — Hand off to conductor. Start at Phase 1.
