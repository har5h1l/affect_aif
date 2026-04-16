---
status: CONTINUE
next_priority: 3
pending_work:
  - "Phase 3: once the detached H1/H2/H4 regenerations finish, run scripts/run_targeted_reanalysis.py and save outputs under results/reanalysis/"
  - "Phase 4-5: run shallow_affect_confirm smoke/full experiments, analyze outputs, then update docs cautiously"
  - "If shallow H1 reanalysis yields d<0.3 at tau=1, stop and flag a story-level contradiction before changing docs"
next_session_focus: "Check whether the detached H1/H2/H4 regeneration jobs finished, then run scripts/run_targeted_reanalysis.py; if Phase 3 clears, start shallow_affect_confirm smoke run with the committed config"
model_hint: haiku
mode_hint: monitor
---

# Research State

## Last Updated
2026-04-16 (Session 25 — regeneration still running)

## Session Count
25


<!-- Older entries truncated (was 166 lines) -->

    - log: `/tmp/mango-worktree-affect_aif-20260416_165841-206877/results/logs/h4_betrayal_relaunch.log`
- No additional polling performed after that single post-launch verification.

  - read `conductor/MISSION.md` and `conductor/STATE.md`
  - confirmed `conductor/INBOX.md` does not exist
  - re-checked phase docs: `docs/future/roadmap.md`, `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
- Performed one post-launch completion check for the detached Phase 3 regeneration jobs:
  - `results/h1_factorial/h1_depth_affect_factorial/results.csv` still missing
  - `results/h2_lesion/h2_lesion_dissociation/results.csv` still missing
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv` still missing
  - `pgrep -af` still shows the launched experiment processes for all three configs
- No additional polling performed after that single check.

### Config checkpoint
- Added `configs/shallow_affect_confirm.json` exactly for the Phase 4 shallow-depth confirmation run:
  - conditions `[1, 2, 3, 4]`
  - preset `lesioned`
  - 100 replications / 200 rounds
  - matches mission-specified binary random-assignment surface
- Verified it parses through `ExperimentConfig.from_json(...)`.
- Commit created:
  - `141fcbe` — `Config: add shallow affect confirmation run`

### Verification + detached regeneration launch
- Re-ran the full required test gate before any experiments:
  - `python -m pytest tests/ -v`
  - Result: `248 passed, 26 skipped, 2 warnings in 159.10s`
  - Warnings:
    - multiprocessing `os.fork()` with JAX in `test_batch_runner_writes_per_config_subdirs_and_provenance`
    - SciPy precision-loss warning in the targeted reanalysis CLI smoke test
- Confirmed the three required Phase 3 CSVs are still absent locally under `results/`.
- Confirmed the current `mango` CLI here does not provide the older result-fetch flow documented in `CLAUDE.md`; local fallback is regeneration.
- Launched detached regeneration jobs for the missing mission datasets and verified them once with `pgrep -af`:
  - `h1_factorial` → run dir `/tmp/mango-worktree-affect_aif-20260416_143926-170352/results/h1_factorial/h1_depth_affect_factorial`
    - log: `/tmp/mango-worktree-affect_aif-20260416_143926-170352/results/logs/h1_factorial.log`
    - verified process match included python PID `184351` (plus two worker processes from `--workers 2`)
  - `h2_lesion` → run dir `/tmp/mango-worktree-affect_aif-20260416_143926-170352/results/h2_lesion/h2_lesion_dissociation`
    - log: `/tmp/mango-worktree-affect_aif-20260416_143926-170352/results/logs/h2_lesion.log`
    - verified process match included python PID `184455`
  - `h4_betrayal` → run dir `/tmp/mango-worktree-affect_aif-20260416_143926-170352/results/h4_betrayal/h4_betrayal_recovery`
    - log: `/tmp/mango-worktree-affect_aif-20260416_143926-170352/results/logs/h4_betrayal.log`
    - verified process match included python PID `184456`
  - Launch pattern that survives the exec wrapper:
    - `setsid bash -lc 'cd "$PWD" && python scripts/run_experiment.py ... > results/logs/<name>.log 2>&1 < /dev/null' >/dev/null 2>&1 &`
  - Important: plain `nohup ... &` from this runner is not sufficient; the wrapper reaps normal background jobs when the command exits.

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

### Phase 2 hypothesis reframe
- Updated `docs/experiment/design.md`:
  - Rewrote Section 1 overview around the new H1-H5 framing.
  - Replaced the canonical Hypotheses 1-5 section: H1 is now G compression / depth redundancy, H2 affect augmentation, H3 lesion dissociation, H4 betrayal recovery, H5 partner selection.
  - Replaced the current empirical status scorecard so it reflects what is supported versus what still needs shallow/post-switch re-analysis.
- Updated `docs/experiment/results.md`:
  - Replaced the status note and architectural review note with the post-restructure interpretation.
  - Rewrote the top-level headline, hypothesis scorecard, and interpretation sections so they no longer anchor on the old pooled-depth story.
  - Left lower historical sections in place as archival context; the top of the file now explicitly marks them as historical unless updated.

### Phase 3 analysis tooling
- Added `scripts/run_targeted_reanalysis.py`.
  - Inputs default to the mission paths for H1, H2, and H4 result CSVs.
  - Writes the requested outputs:
    - `results/reanalysis/h1_shallow_reanalysis.txt`
    - `results/reanalysis/h2_lesion_reanalysis.txt`
    - `results/reanalysis/h4_betrayal_window_reanalysis.txt`
  - Computes the exact targeted summaries needed for Phase 3 once the CSVs exist locally.
- Added a smoke test in `tests/test_supported_surface.py` for the new CLI.
- Verified with `python -m pytest tests/test_supported_surface.py -v`
  - Result: `6 passed, 1 warning`

### Phase 3 blocker
- The required existing result CSVs were absent from this worktree at session start:
  - `results/h1_factorial/h1_depth_affect_factorial/results.csv`
  - `results/h2_lesion/h2_lesion_dissociation/results.csv`
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv`
- Local regeneration is again in flight in detached jobs, now relaunched from the current live worktree after recovering from a deleted-worktree detach failure.

## Pending Work (Phases)

### Phase 2: Hypothesis Reframe [DONE]
- `docs/experiment/design.md` and `docs/experiment/results.md` now use the post-restructure H1-H5 framing at their canonical top sections.

### Phase 3: Targeted Re-Analysis [NEXT]
- Wait for the detached H1/H2/H4 regenerations to finish
- Run `python scripts/run_targeted_reanalysis.py`
- Save outputs under `results/reanalysis/`

### Phase 4: New Experiments [NOT STARTED]
- Run smoke + full shallow confirmation
- Rerun H5 partner selection
- Run clinical betrayal and clinical phenotypes on new architecture

### Phase 5: Analysis + Docs [NOT STARTED]
- Analyze each new run immediately after completion
- Update `docs/experiment/results.md` cautiously with scorecard outcomes
- Flag contradictions before narrative changes

## Auto Handoff

- **What changed:** Session 25 completed the required startup sequence again and performed exactly one completion check against the current-worktree Phase 3 regeneration outputs.
- **What changed:** All three required CSVs are still missing locally, while the relaunched regeneration processes remain live under wrapper PIDs `209790`, `209791`, `209792` and python PIDs `209969`, `209972`, `209973` (plus H1 worker PIDs `209985`, `209986`).
- **What changed:** No code, docs, configs, or experiment launches were added this wake; this was a monitor-only pass to avoid unnecessary polling.
- **What is still in flight:** The detached regenerations for `h1_factorial`, `h2_lesion`, and `h4_betrayal` are still running; `results/reanalysis/` has not been produced yet. Phase 4 remains blocked on those inputs.
- **What next session should do:** Perform one completion check again. If the three `results.csv` files now exist, run `python scripts/run_targeted_reanalysis.py`, inspect the tau-1 affect effect size, save the Phase 3 outputs, and checkpoint them. If the jobs are still running, stop again after that one check.
- **Key risk:** If shallow-depth reanalysis still shows weak affect at tau=1 (`d < 0.3`), stop and flag; that would require a deeper story change.

DECISION: Treat depth redundancy / G compression as a structural result of the supported binary action-dependent trust-game surface, not as a pending implementation defect.
DECISION: Use local regeneration rather than result sync because the required CSVs are absent and this `mango` install does not expose the old fetch workflow documented in repo notes.
DECISION: Treat deleted-worktree detached runs as invalid for continuation; relaunch from the live worktree rather than continuing to monitor orphaned processes.
DECISION: `scripts/run_experiment.py` already writes per-replication checkpoints (`checkpoint_interval=1`) and partial CSVs by default for each run, so the new shallow config does not need extra unsupported save keys.
NEXT: Do not poll the relaunched detached jobs repeatedly. On the next wake, check completion once against the new PIDs / run dirs above, then run the targeted reanalysis script as soon as the three CSVs exist.
NEXT: If the regeneration jobs are still running on the next wake, perform only one completion check again and then stop; do not tail logs or watch file growth.

### Session 25 monitor pass
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
- Performed one completion check for the detached Phase 3 regeneration jobs:
  - `results/h1_factorial/h1_depth_affect_factorial/results.csv` still missing
  - `results/h2_lesion/h2_lesion_dissociation/results.csv` still missing
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv` still missing
  - `pgrep -af` still shows the launched wrapper processes:
    - `209790` for `h1_factorial`
    - `209791` for `h2_lesion`
    - `209792` for `h4_betrayal`
  - `pgrep -af` also still shows live python children:
    - `209969`, `209985`, `209986` for `h1_factorial`
    - `209972` for `h2_lesion`
    - `209973` for `h4_betrayal`
- No additional polling performed after that single check.
