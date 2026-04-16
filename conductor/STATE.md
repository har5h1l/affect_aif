---
status: CONTINUE
next_priority: 1
pending_work:
  - "Phase 3: let the detached H1/H2/H4 single-worker regenerations finish, then run scripts/run_targeted_reanalysis.py against the new results.csv files"
  - "Phase 4-5: run shallow_affect_confirm smoke/full experiments, analyze outputs, then update docs cautiously"
  - "If shallow H1 reanalysis yields d<0.3 at tau=1, stop and flag a story-level contradiction before changing docs"
next_session_focus: "Check whether the new setsid-backed Phase 3 runs finished, then run targeted reanalysis on their results.csv outputs"
model_hint: haiku
mode_hint: monitor
---

# Research State

## Last Updated
2026-04-16 (Session 34 — relaunched Phase 3 regenerations with working detach pattern)

## Session Count
34


<!-- Older entries truncated (was 168 lines) -->

### Session 34 relaunch pass
- Read `CLAUDE.md`, `conductor/MISSION.md`, `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Verified current branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree dirty only from `conductor/STATE.md`
- Inspected the failed regeneration artifacts once:
  - prior relaunched outputs had only partial checkpoints:
    - `results/h1_factorial/h1_depth_affect_factorial/results_partial.csv` → `28,864` rows
    - `results/h2_lesion/h2_lesion_dissociation/results_partial.csv` → `49,113` rows
    - `results/h4_betrayal/h4_betrayal_recovery/results_partial.csv` → `720` rows
  - no final `results.csv` files existed for any of those three runs
  - the runner has checkpointing but no resume path; partial files cannot be resumed in place
- Ran the required full test suite before relaunching experiments:
  - `python -m pytest tests/ -v`
  - result: `248 passed, 26 skipped, 2 warnings in 371.48s (0:06:11)`
  - DECISION: the relevant warning is from `tests/test_integration.py::test_batch_runner_writes_per_config_subdirs_and_provenance`:
    - `RuntimeWarning: os.fork() was called. os.fork() is incompatible with multithreaded code, and JAX is multithreaded, so this will likely lead to a deadlock.`
  - DECISION: this explains the failed detached reruns that used the batch-style worker pool; relaunches should avoid forked worker pools and use `--workers 1`
- Attempted plain `nohup` detached relaunches and observed that they died immediately under this tool runner with empty logs
- DECISION: `setsid -f` is the working detach pattern in this environment; it leaves long-lived experiment processes visible via `pgrep`
- Relaunched fresh single-worker regeneration jobs into new batch directories:
  - H1:
    - PID `283269`
    - run dir `results/h1_factorial_setsid_20260416/h1_depth_affect_factorial`
    - log `results/logs/h1_factorial_setsid_20260416.log`
  - H2:
    - PID `283271`
    - run dir `results/h2_lesion_setsid_20260416/h2_lesion_dissociation`
    - log `results/logs/h2_lesion_setsid_20260416.log`
  - H4:
    - PID `283274`
    - run dir `results/h4_betrayal_setsid_20260416/h4_betrayal_recovery`
    - log `results/logs/h4_betrayal_setsid_20260416.log`
- Performed exactly one post-launch verification:
  - `pgrep -af 'h1_factorial_setsid_20260416|h2_lesion_setsid_20260416|h4_betrayal_setsid_20260416'`
  - live processes observed:
    - `283269 python scripts/run_experiment.py --config configs/h1_depth_affect_factorial.json --output-dir results --batch-name h1_factorial_setsid_20260416 --workers 1`
    - `283271 python scripts/run_experiment.py --config configs/h2_lesion_dissociation.json --output-dir results --batch-name h2_lesion_setsid_20260416 --workers 1`
    - `283274 python scripts/run_experiment.py --config configs/h4_betrayal_recovery.json --output-dir results --batch-name h4_betrayal_setsid_20260416 --workers 1`
- NEXT: do not poll further in this wake cycle; next session should check whether these three runs produced final `results.csv` files and, if so, run `scripts/run_targeted_reanalysis.py` against the new result paths
- Auto Handoff:
  - What changed: identified the likely failure root cause (`os.fork`/JAX warning in batch worker mode), confirmed the old reruns were incomplete, and relaunched H1/H2/H4 with `setsid -f` plus `--workers 1`
  - Still in flight: detached runs `283269`, `283271`, `283274`
  - Next session: verify completion of the three new run dirs, then execute targeted reanalysis and inspect whether tau=1 affect is still weak

  - `results/h2_lesion/h2_lesion_dissociation/results.csv` still missing
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv` still missing
  - `results/h1_factorial/h1_depth_affect_factorial/results_partial.csv` is present
  - `pgrep -af` still shows the launched wrapper processes:
    - `209790` for `h1_factorial`
    - `209791` for `h2_lesion`
    - `209792` for `h4_betrayal`
  - `pgrep -af` still shows live python children:
    - `209969`, `209985`, `209986` for `h1_factorial`
    - `209972` for `h2_lesion`
    - `209973` for `h4_betrayal`
- No additional polling performed after that single check.

### Session 29 monitor pass
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree remains dirty only from `conductor/STATE.md`
- Performed one completion check for the detached Phase 3 regeneration jobs:
  - `results/h1_factorial/h1_depth_affect_factorial/results.csv` still missing
  - `results/h2_lesion/h2_lesion_dissociation/results.csv` still missing
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv` still missing
  - `results/h1_factorial/h1_depth_affect_factorial/results_partial.csv` is present
  - `pgrep -af` still shows the launched wrapper processes:
    - `209790` for `h1_factorial`
    - `209791` for `h2_lesion`
    - `209792` for `h4_betrayal`
  - `pgrep -af` still shows live python children:
    - `209969`, `209985`, `209986` for `h1_factorial`
    - `209972` for `h2_lesion`
    - `209973` for `h4_betrayal`
- No additional polling performed after that single check.

### Session 28 monitor pass
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree remains dirty only from `conductor/STATE.md`
- Performed one completion check for the detached Phase 3 regeneration jobs:
  - `results/h1_factorial/h1_depth_affect_factorial/results.csv` still missing
  - `results/h2_lesion/h2_lesion_dissociation/results.csv` still missing
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv` still missing
  - `results/h1_factorial/h1_depth_affect_factorial/results_partial.csv` is present
  - `pgrep -af` still shows the launched wrapper processes:
    - `209790` for `h1_factorial`
    - `209791` for `h2_lesion`
    - `209792` for `h4_betrayal`
  - `pgrep -af` still shows live python children:
    - `209969`, `209985`, `209986` for `h1_factorial`
    - `209972` for `h2_lesion`
    - `209973` for `h4_betrayal`
- No additional polling performed after that single check.

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

### Session 26 monitor pass
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree remains dirty only from `conductor/STATE.md`
- Performed one completion check for the detached Phase 3 regeneration jobs:
  - `results/h1_factorial/h1_depth_affect_factorial/results.csv` still missing
  - `results/h2_lesion/h2_lesion_dissociation/results.csv` still missing
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv` still missing
  - `pgrep -af` still shows the launched wrapper processes:
    - `209790` for `h1_factorial`
    - `209791` for `h2_lesion`
    - `209792` for `h4_betrayal`
  - `pgrep -af` still shows live python children:
    - `209969`, `209985`, `209986` for `h1_factorial`
    - `209972` for `h2_lesion`
    - `209973` for `h4_betrayal`
- No additional polling performed after that single check.

### Session 27 monitor pass
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree remains dirty only from `conductor/STATE.md`
- Performed one completion check for the detached Phase 3 regeneration jobs:
  - `results/h1_factorial/h1_depth_affect_factorial/results.csv` still missing
  - `results/h2_lesion/h2_lesion_dissociation/results.csv` still missing
  - `results/h4_betrayal/h4_betrayal_recovery/results.csv` still missing
  - `results/h1_factorial/h1_depth_affect_factorial/results_partial.csv` is present
  - `pgrep -af 'h1_factorial'` still shows the launched wrapper and python processes:
    - wrapper `209790`
    - python `209969`, `209985`, `209986`
  - `pgrep -af 'scripts/run_experiment.py --config configs/(h1_factorial|h2_lesion_dissociation|h4_betrayal_recovery)\\.json'` shows:
    - wrappers `209791`, `209792`
    - python `209972`, `209973`
- No additional polling performed after that single completion check and one H1-specific liveness clarification.
