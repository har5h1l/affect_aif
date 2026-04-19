---
status: ACTIVE
next_priority: 1
pending_work:
  - "Re-run `shallow_affect_confirm` (and other primary batches) on the new generative model — prior `shallow_confirm` effect sizes are not comparable"
  - "Detached reruns for `h5_selection` and `clinical_post_restructure/clinical_betrayal` exited without final `results.csv`; partials incomplete — decide salvage vs relaunch"
  - "`results/clinical_post_restructure/clinical_phenotypes` still absent in this worktree"
next_session_focus: "Smoke then full `shallow_affect_confirm` with conditions [1-4,9,10]; then H5/clinical relaunch if user wants; do not rewrite results.md narrative until new CSVs exist"
model_hint: opus
mode_hint: research
---

# Research State

## Last Updated
2026-04-19 (Session 108 — multi-focal runtime F: runner + configs + tests; full pytest green; slow emergent gated)

## Session Count
108


<!-- Older entries truncated (was 170 lines) -->

### Session 108 — multi-focal-runtime (F) implementation
- Added `experiment/multi_focal_runner.py`, `multi_focal_config.py`, `joint_resolution.py`, and `create_agents_from_multi_focal_config` on `experiment/factory.py`. Four configs under `configs/multifocal_*.json`.
- Strict pomdp_spec §12 turn-taking (single focal per round). `RoundProtocol` extension seam for future all-pairs. Simultaneous-moves resolution (deviation from pomdp_spec §12 step 4 documented as decision F4).
- Default `pytest` runs unit + deterministic tests; N1/N2/N3 emergent statistical tests are `pytest.mark.slow` unless `RUN_SLOW_TESTS=1`.
- Spec `docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md`; plan `docs/superpowers/plans/2026-04-18-multi-focal-runtime-plan.md`. Sub-project D should inventory the four new configs.

### Session 107 — apashea spec integration (implementation)
- Implemented factorized `num_controls` for binary trust game (`[1,2,2]` random; `[P,2,2]` agent_choice), 4 planning policies per timestep, env decode via `decode_env_agent_action`
- `decision_step_trust_game`: `log_policy_prior` on logits; `BaseAgent.log_policy_prior` + `learn_E` EMA from `last_q_pi`
- Dirichlet `learn_A` / `learn_B` wired (`pA_scale`, `pB_scale`, `lr_E` on config); `learn_A` takes precedence over `use_parameter_learning` for A updates
- Conditions **9** (`tau3_no_affect`) and **10** (`tau3_affect`); `configs/shallow_affect_confirm.json` includes `9, 10`
- Tests: `test_hesp_v3_model`, `test_action_dependent_model`, `test_theory_alignment` betrayal assertion relaxed; 250 passed
- Reference: `notebooks/04_apashea_trust_spec.ipynb`

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
