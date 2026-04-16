---
status: CONTINUE
next_priority: 2
pending_work:
  - "Phase 2: reframe docs/experiment/design.md and docs/experiment/results.md around H1-H5 on the action-dependent architecture"
  - "Phase 3: run targeted re-analysis for H1 shallow, H2 lesion, and H4 betrayal window into results/reanalysis/"
  - "Phase 4-5: create shallow_affect_confirm config, run smoke/full experiments, analyze outputs, then update docs cautiously"
next_session_focus: "Start Phase 2 doc reframe, then compute the three targeted re-analyses before launching new experiments"
model_hint: sonnet
mode_hint: codex
---

# Research State

## Last Updated
2026-04-16 (Session 18 — Phase 1 cleanup checkpoint)

## Session Count
18

## Current Direction
Post-restructure reframe. Action-dependent stance is the supported trust-game architecture; current work is reframing the hypothesis story around depth redundancy / G compression and then finishing the remaining experiments on that surface.

## This Session

### Phase 1 cleanup
- Updated `docs/future/roadmap.md`:
  - Decision 1 marked resolved: action-dependent stance implemented; depth redundancy now treated as a structural binary-task finding.
  - Decision 2 removed: no pymdp path remains active.
  - Decision 3 kept open; Decision 4 kept as future work.
  - CvC / CoGames moved out of active tracks into future directions.
  - Current direction updated to post-restructure reframe.
- Cleanup targets from MISSION were not present in this worktree:
  - `results/clinical_run/`
  - `results/h5_selection/h5_partner_selection/results_partial.csv`
  The local `results/` tree currently only contains `.gitkeep` and `results/README.md`.
- Ran full verification: `python -m pytest tests/ -v`
  - Result: `247 passed, 26 skipped, 1 warning in 151.07s`
  - Warning: multiprocessing `os.fork()` with JAX in `test_batch_runner_writes_per_config_subdirs_and_provenance`; suite still passed.

## Pending Work (Phases)

### Phase 2: Hypothesis Reframe [NEXT]
- Update `docs/experiment/design.md` Section 1 and hypothesis framing to the new H1-H5 definitions from MISSION.
- Update `docs/experiment/results.md` status note and scorecard framing to match the post-restructure story.
- Do not touch `docs/paper/`.

### Phase 3: Targeted Re-Analysis [NOT STARTED]
- H1 shallow reanalysis from `results/h1_factorial/h1_depth_affect_factorial/results.csv`
- H2 lesion reanalysis from `results/h2_lesion/h2_lesion_dissociation/results.csv`
- H4 betrayal-window reanalysis from `results/h4_betrayal/h4_betrayal_recovery/results.csv`
- Save outputs under `results/reanalysis/`

### Phase 4: New Experiments [NOT STARTED]
- Create `configs/shallow_affect_confirm.json`
- Run smoke + full shallow confirmation
- Rerun H5 partner selection
- Run clinical betrayal and clinical phenotypes on new architecture

### Phase 5: Analysis + Docs [NOT STARTED]
- Analyze each new run immediately after completion
- Update `docs/experiment/results.md` cautiously with scorecard outcomes
- Flag contradictions before narrative changes

## Auto Handoff

- **What changed:** Phase 1 completed. Roadmap now reflects resolved B-matrix decision, removed pymdp path, and CvC moved to future directions. Full test suite passes.
- **What is still in flight:** Phases 2-5 remain. No experiment jobs launched yet.
- **What next session should do:** Edit `docs/experiment/design.md` and `docs/experiment/results.md` for the new H1-H5 framing, then run the three targeted re-analyses before any new experiment.
- **Key risk:** If shallow-depth reanalysis still shows weak affect at tau=1 (`d < 0.3`), stop and flag; that would require a deeper story change.

DECISION: Treat depth redundancy / G compression as a structural result of the supported binary action-dependent trust-game surface, not as a pending implementation defect.
NEXT: Commit the Phase 1 checkpoint, then start Phase 2 doc reframe.
