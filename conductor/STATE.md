---
status: BLOCKED
next_priority: 1
pending_work:
  - "User decision needed: `shallow_confirm` still contradicts the expected H2/H3 story (`tau1 d=0.1489`, `tau2 d=0.1955`) and the shallow lesion is not a clean Damasio dissociation"
  - "Detached reruns for `h5_selection` and `clinical_post_restructure/clinical_betrayal` exited without final `results.csv`; partials are incomplete (`h5_selection`: 15 seeds x 200 rounds, `clinical_betrayal`: 26 seeds x 120 rounds)"
  - "`results/clinical_post_restructure/clinical_phenotypes` still has no partial or final output and appears never to have started in this worktree"
next_session_focus: "Wait for user direction on whether to salvage/analyze incomplete partials or relaunch H5 and clinical batches; do not rewrite interpretation docs without explicit user approval"
model_hint: opus
mode_hint: research
---

# Research State

## Last Updated
2026-04-18 (Session 106 — detached H5 and clinical betrayal runs found exited without final outputs; both partials incomplete; `clinical_phenotypes` still absent)

## Session Count
106


<!-- Older entries truncated (was 170 lines) -->

### Session 67 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/shallow_confirm/shallow_affect_confirm/results.csv` still missing; partial output present at `results/shallow_confirm/shallow_affect_confirm/results_partial.csv`
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv`
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv`
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; run directory still absent under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted Phase 4 wrappers and worker processes remain live:
    - `shallow_confirm`: wrapper/children `373967`, `374127`, `374164`, `374165`
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
  - `pgrep -af` also showed older unrelated `h1_factorial` / `h4_betrayal` relaunch processes (`209790`, `209792`, `209969`, `209973`, `209985`, `209986`, `283269`, `283274`); these were not part of this bounded check and were not touched
- DECISION: no analysis or doc updates are available in this wake cycle because none of the detached Phase 4 batches has completed yet
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

## Auto Handoff

- What changed: Session 106 found that the tracked detached reruns are no longer running. No final `results.csv` exists for `h5_selection` or `clinical_post_restructure/clinical_betrayal`, and `clinical_phenotypes` still has not emitted any file in this worktree.
- In flight: nothing active from the previously tracked Phase 4 wrappers. `h5_selection` stopped at `results_partial.csv` with 3000 rows = 15 seeds x 200 rounds (all seed-condition pairs maxed at round `199`, zero-indexed). `clinical_betrayal` stopped at `results_partial.csv` with 3120 rows = 26 seeds x 120 rounds (all seed-condition pairs maxed at round `119`, zero-indexed). No log files were found under the worktree root or result directories.
- Next session should do: wait for user direction before relaunching or salvaging these incomplete runs. The mission already had an interpretation blocker from `shallow_confirm` (`tau1 d=0.1489`, `tau2 d=0.1955`, shallow lesion not Damasio-like), and the detached H5/clinical reruns did not complete cleanly.

### Session 106 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/h5_selection/h5_partner_selection/results.csv` is still missing; partial output remains at `results/h5_selection/h5_partner_selection/results_partial.csv` (`539698176` bytes, timestamp `2026-04-18 14:47 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` is still missing; partial output remains at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`561080437` bytes, timestamp `2026-04-18 15:17 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` is still missing; no partial output exists under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af '373976|374138|373989|374151|374161'` returned no live processes; the previously tracked wrappers/workers have exited
- Performed one salvage-readiness check on the partial CSVs:
  - `h5_selection` partial contains `3000` rows = `15` seeds x `200` rounds for one condition; every seed-condition pair ends at round `199` (zero-indexed), so the run stopped after 15 completed seeds and never finalized
  - `clinical_betrayal` partial contains `3120` rows = `26` seeds x `120` rounds for one condition; every seed-condition pair ends at round `119` (zero-indexed), so the run stopped after 26 completed seeds and never finalized
  - no `.log` or `nohup.out` files were found under the worktree root or the tracked result directories
- DECISION: the monitored detached reruns are no longer in flight and cannot be analyzed as completed batches because both final artifacts are missing and the partials are incomplete
- BLOCKER: the mission-level interpretation blocker remains in force because `shallow_confirm` still shows weak affect at `tau=1,2`; user direction is needed before deciding whether to salvage partials, relaunch reruns, or reframe further
- NEXT: wait for user input on how to handle incomplete H5/clinical reruns and the shallow-confirm contradiction before starting new runs or rewriting interpretation docs

### Session 105 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`539698176` bytes, timestamp `2026-04-18 14:47 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`539500127` bytes, timestamp `2026-04-18 14:19 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; no partial output present under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted Phase 4 wrappers and worker processes remain live:
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the tracked detached Phase 4 batches has completed yet
- DECISION: `h5_selection` partial output advanced during this wake, while `clinical_betrayal` remained unchanged and `clinical_phenotypes` still has not emitted any file
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 104 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`503737288` bytes, timestamp `2026-04-18 13:06 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`539500127` bytes, timestamp `2026-04-18 14:19 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; no partial output present under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted Phase 4 wrappers and worker processes remain live:
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the tracked detached Phase 4 batches has completed yet
- DECISION: `clinical_betrayal` partial output advanced during this wake, while `h5_selection` remained unchanged and `clinical_phenotypes` still has not emitted any file
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 103 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`503737288` bytes, timestamp `2026-04-18 13:06 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`517935352` bytes, timestamp `2026-04-18 13:20 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; no partial output present under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted Phase 4 wrappers and worker processes remain live:
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the tracked detached Phase 4 batches has completed yet
- DECISION: tracked partial outputs did not advance during this wake, while `clinical_phenotypes` still has not emitted any file
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 102 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`503737288` bytes, timestamp `2026-04-18 13:06 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`517935352` bytes, timestamp `2026-04-18 13:20 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; no partial output present under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted Phase 4 wrappers and worker processes remain live:
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the tracked detached Phase 4 batches has completed yet
- DECISION: both tracked partial outputs advanced during this wake, while `clinical_phenotypes` still has not emitted any file
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 101 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`467744584` bytes, timestamp `2026-04-18 11:28 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`496371409` bytes, timestamp `2026-04-18 12:23 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; no partial output present under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted Phase 4 wrappers and worker processes remain live:
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the tracked detached Phase 4 batches has completed yet
- DECISION: `clinical_betrayal` partial output advanced during this wake, while `h5_selection` stayed at the prior size/timestamp and `clinical_phenotypes` still has not emitted any file
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs
