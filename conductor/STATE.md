---
status: CONTINUE
next_priority: 1
pending_work:
  - "Detached runs remain in flight: `results/h5_selection/h5_partner_selection` and `results/clinical_post_restructure/clinical_betrayal`; `clinical_phenotypes` still has no run directory"
  - "If `results.csv` appears for `h5_selection` or `clinical_post_restructure`, run `scripts/run_analysis.py` immediately and capture the hypothesis-relevant readout before any doc edits"
  - "Keep interpretation docs unchanged until the user explicitly wants the weak shallow-affect and non-Damasio shallow lesion results incorporated into the narrative"
next_session_focus: "Do one bounded completion check for `h5_selection` and `clinical_post_restructure`, analyze any newly completed batch immediately, and keep the shallow-confirm contradictions visible in handoff"
model_hint: opus
mode_hint: hybrid
---

# Research State

## Last Updated
2026-04-18 (Session 85 — shallow_confirm completion confirmed and readout captured)

## Session Count
85


<!-- Older entries truncated (was 171 lines) -->

### Session 85 status check
- Read `CLAUDE.md`, `conductor/MISSION.md`, and `conductor/STATE.md`
- Confirmed `conductor/INBOX.md` does not exist
- Re-checked phase docs:
  - `docs/future/roadmap.md`
  - `docs/experiment/results.md`
- Checked branch state:
  - `git status --short --branch` → `## analysis/post-restructure-reframe`
  - working tree was dirty only from `conductor/STATE.md`
- Performed one bounded completion check for the detached Phase 4 runs:
  - `results/shallow_confirm/shallow_affect_confirm/results.csv` now exists (`392152888` bytes, `2026-04-17 22:31 UTC`); no live `shallow_confirm` wrapper/worker remained
  - `results/h5_selection/h5_partner_selection/results.csv` still missing; partial output present at `results/h5_selection/h5_partner_selection/results_partial.csv` (`287823598` bytes, `2026-04-18 03:24 UTC`)
  - `results/clinical_post_restructure/clinical_betrayal/results.csv` still missing; partial output present at `results/clinical_post_restructure/clinical_betrayal/results_partial.csv` (`302145037` bytes, `2026-04-18 03:52 UTC`)
  - `results/clinical_post_restructure/clinical_phenotypes/results.csv` still missing; no run directory or partial file under `results/clinical_post_restructure/clinical_phenotypes`
  - `pgrep -af` confirms only the targeted `h5_selection` and `clinical_post_restructure` wrappers/workers remain live:
    - `h5_selection`: wrapper/child `373976`, `374138`
    - `clinical_post_restructure`: wrapper/children `373989`, `374151`, `374161`
- Confirmed `shallow_confirm` analysis artifacts already exist under `results/shallow_confirm/shallow_affect_confirm/figures`
- Captured `shallow_confirm` readout from `final_round_summary.csv`:
  - payoff means: `tau1_no_affect=406.28`, `tau1_affect=416.66`, `tau2_no_affect=390.34`, `tau2_affect=398.58`, `lesioned=375.54`
  - shallow affect remains weak: `tau1_affect` vs `tau1_no_affect` `d=0.207`, `p=0.144`; `tau2_affect` vs `tau2_no_affect` `d=0.196`, `p=0.168`
  - lesion payoff drop is clear against shallow affect: `tau2_affect` vs `lesioned` payoff `d=0.545`, `p=1.58e-4`
  - lesion does not preserve inference cleanly enough for a Damasio story: `lesioned` vs `tau2_no_affect` joint accuracy `d=-0.136`, `p=0.339`, but stance accuracy is materially worse `d=-1.050`, `p=3.55e-12`
- DECISION: `shallow_confirm` is complete, but it does not rescue the shallow-affect story; the effect remains weak at both `tau=1` and `tau=2`
- DECISION: the shallow lesion result is mixed rather than a clean dissociation because payoff drops versus affect while stance accuracy also degrades materially
- NEXT: on the next wake, do one bounded completion check for `h5_selection` and `clinical_post_restructure`; if either `results.csv` exists, analyze immediately and capture the hypothesis-relevant readout before any doc edits

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

- What changed: `shallow_confirm` completion was confirmed and its existing analysis artifacts were read. The shallow readout stays contradictory to the hoped-for reframe: affect remains weak at `tau=1` (`d=0.207`, `p=0.144`) and `tau=2` (`d=0.196`, `p=0.168`).
- In flight: `h5_selection` and `clinical_post_restructure` wrappers/workers were still live during this wake; `clinical_betrayal` partial output advanced to `302145037` bytes (`2026-04-18 03:52 UTC`); `clinical_phenotypes` still had no run directory.
- Next session should do: one bounded completion check for `h5_selection` and `clinical_post_restructure`, analyze any newly completed batch immediately, and keep two contradictions visible in handoff: shallow affect is still weak and the shallow lesion is not a clean Damasio dissociation because stance accuracy degrades strongly.
