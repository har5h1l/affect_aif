---
status: CONTINUE
next_priority: 1
pending_work:
  - "Detached runs remain in flight: `results/h5_selection/h5_partner_selection/results_partial.csv` and `results/clinical_post_restructure/clinical_betrayal/results_partial.csv`; `clinical_phenotypes` still has no partial or final output"
  - "If `results.csv` appears for `h5_selection` or `clinical_post_restructure`, run `scripts/run_analysis.py` immediately and capture the hypothesis-relevant readout; do not rewrite interpretation docs without explicit user approval"
  - "Interpretation blocker remains: `shallow_confirm` is finalized and still shows weak affect at `tau=1,2` (`tau1 d=0.1489`, `tau2 d=0.1955`) and the shallow lesion is not a clean Damasio dissociation"
next_session_focus: "Do one bounded completion check for `h5_selection` and `clinical_post_restructure`; analyze immediately if a final `results.csv` appears, otherwise leave the detached runs alone"
model_hint: opus
mode_hint: hybrid
---

# Research State

## Last Updated
2026-04-18 (Session 101 — bounded completion check only; detached runs still partial)

## Session Count
100


<!-- Older entries truncated (was 169 lines) -->

- DECISION: no analysis or doc updates are available in this wake cycle because none of the detached Phase 4 batches has completed yet
- DECISION: `h5_selection` and `clinical_betrayal` partial outputs both advanced since the prior handoff; `clinical_phenotypes` still has not created any output path
- NEXT: on the next wake, wait for explicit user direction if possible; otherwise do one bounded completion check again and analyze immediately if a final `results.csv` appears
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/shallow_confirm/shallow_affect_confirm/results.csv` still missing; partial output present at `results/shallow_confirm/shallow_affect_confirm/results_partial.csv` (`22091568` bytes, timestamp `2026-04-17 19:23 UTC`)
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`107908931` bytes, timestamp `2026-04-17 17:58 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`129518364` bytes, timestamp `2026-04-17 19:12 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; run directory still absent under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted Phase 4 wrappers and worker processes remain live:
    - `shallow_confirm`: wrapper/children `373967`, `374127`, `374164`, `374165`
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the detached Phase 4 batches has completed yet
- DECISION: `shallow_confirm` partial output appears to have restarted from a smaller file while remaining live; `clinical_betrayal` partial output advanced materially since Session 70; `h5_selection` remains unchanged and `clinical_phenotypes` has not created a run directory
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 63 status check
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
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; run directory not created yet under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the launched wrappers and worker processes remain live:
    - `shallow_confirm`: wrapper `373967`; python `374127`, `374164`, `374165`
    - `h5_selection`: wrapper `373976`; python `374138`
    - `clinical_post_restructure`: wrapper `373989`; python `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the detached Phase 4 batches has completed yet
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 64 status check
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
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; run directory still absent and no partial file present under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the launched wrappers and worker processes remain live:
    - `shallow_confirm`: wrappers/children `373967`, `374127`, `374164`, `374165`
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrappers/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the detached Phase 4 batches has completed yet
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 66 status check
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
  - `pgrep -af` confirms the launched wrappers and worker processes remain live:
    - `shallow_confirm`: wrappers/children `373967`, `374127`, `374164`, `374165`
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrappers/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the detached Phase 4 batches has completed yet
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

### Session 65 status check
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
  - `pgrep -af` confirms the launched wrappers and worker processes remain live:
    - `shallow_confirm`: wrappers/children `373967`, `374127`, `374164`, `374165`
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrappers/children `373989`, `374151`, `374161`
- DECISION: no analysis or doc updates are available in this wake cycle because none of the detached Phase 4 batches has completed yet
- NEXT: on the next wake, do one bounded completion check again; if any `results.csv` exists, run `scripts/run_analysis.py` for that batch and capture the hypothesis readout before touching interpretation docs

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

- What changed: Session 101 performed the required bounded completion check only. No new final `results.csv` appeared. `clinical_betrayal` partial output advanced again; `h5_selection` did not advance during this wake.
- In flight: targeted wrappers/workers are still live for `h5_selection` (`373976`, `374138`) and `clinical_post_restructure` (`373989`, `374151`, `374161`); `h5_selection` partial output remains `467744584` bytes at `2026-04-18 11:28 UTC`; `clinical_betrayal` partial output is now `496371409` bytes at `2026-04-18 12:23 UTC`; `clinical_phenotypes` still has no partial or final file.
- Next session should do: do only one bounded completion check for `h5_selection` / `clinical_post_restructure`; if a final `results.csv` appears, run `scripts/run_analysis.py` immediately and capture the hypothesis-relevant readout. Otherwise leave the detached runs alone and wait for user direction because `shallow_confirm` still contradicts the expected H2/H3 story (`tau1 d=0.1489`, `tau2 d=0.1955`, shallow lesion not Damasio-like).

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
