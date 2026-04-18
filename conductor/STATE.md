---
status: CONTINUE
next_priority: 1
pending_work:
  - "Detached runs remain in flight: `results/h5_selection/h5_partner_selection` and `results/clinical_post_restructure/clinical_betrayal`; `clinical_phenotypes` still has no run directory"
  - "If `results.csv` appears for `h5_selection` or `clinical_post_restructure`, run `scripts/run_analysis.py` immediately and capture the hypothesis-relevant readout before any doc edits"
  - "Keep interpretation docs unchanged until the user explicitly wants the weak shallow-affect and non-Damasio shallow lesion results incorporated into the narrative"
next_session_focus: "Do one bounded completion check for the detached runs, analyze any newly completed batch, and keep the shallow-confirm contradictions visible in handoff"
model_hint: opus
mode_hint: hybrid
---

# Research State

## Last Updated
2026-04-18 (Session 82 — bounded completion check, no new batch completions)

## Session Count
82


<!-- Older entries truncated (was 179 lines) -->

### Session 82 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/shallow_confirm/shallow_affect_confirm/results.csv` exists (`392152888` bytes, timestamp `2026-04-17 22:31 UTC`); `figures/` is present from the recovered shallow-confirm analysis
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`251859188` bytes, timestamp `2026-04-18 01:45 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`258982927` bytes, timestamp `2026-04-18 01:58 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; run directory is still absent under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms the targeted detached wrappers/workers remain live for the unfinished runs:
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
  - `pgrep -af` also still shows older unrelated `h1_factorial` / `h4_betrayal` relaunch processes (`209790`, `209792`, `209969`, `209973`, `209985`, `209986`, `283269`, `283274`); these were not part of this bounded check and were not touched
- DECISION: no new analysis or doc updates were available in this wake cycle because neither `h5_selection` nor `clinical_post_restructure` produced a fresh `results.csv`
- DECISION: the detached Phase 4 situation is unchanged from the previous handoff except that shallow-confirm completion is now explicitly confirmed from on-disk artifacts during this wake
- NEXT: on the next wake, do one bounded completion check again; if either unfinished batch has `results.csv`, run `scripts/run_analysis.py` immediately and capture the hypothesis-relevant readout before touching interpretation docs

- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
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

- What changed: performed the single bounded completion check for this wake. No new batch completed. `shallow_confirm` remains complete on disk with `results.csv` and `figures/`, but the unfinished targets did not produce fresh `results.csv` files.
- In flight: `h5_selection` and `clinical_post_restructure` wrappers/workers were still live during this wake; `h5_selection` still only had `results_partial.csv` (`251859188` bytes, `2026-04-18 01:45 UTC`), `clinical_betrayal` still only had `results_partial.csv` (`258982927` bytes, `2026-04-18 01:58 UTC`), and `clinical_phenotypes` still had no run directory.
- Next session should do: one bounded completion check for the detached experiment runs, analyze any newly completed batch immediately, and keep two contradictions visible in handoff: shallow affect is still weak (`d≈0.20` at tau=1,2) and the shallow lesion is not a clean Damasio dissociation on stance accuracy.
