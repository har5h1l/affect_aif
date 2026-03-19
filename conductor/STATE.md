# Research State

## Last Updated
2026-03-19

## Session Count
4

## Current Findings

### Phase 6 (COMPLETE)
Bayesian model comparison implemented and run. Key findings:

- **Default (50 seeds):** C2/C5 substantially preferred over non-affect (log10 BF ≈ 0.7–0.9). RFX-BMS: C5 wins (exceedance 1.000), C2 second.
- **Betrayal (50 seeds):** C2 **decisively** best — log10 BF = 3.00 vs C1, 2.70 vs C5. RFX-BMS: C2 wins (exceedance 0.998).
- Precision tracking is the best predictive model under volatility; reward averaging wins in stable conditions.

### Phase 7 (IN PROGRESS)
Testing generalization across game types. Two new games implemented via config-only changes (zero code changes):

- **Stag Hunt** — coordination game: mutual_coop=[5,5], sucker=[0,2], temptation=[2,0], mutual_defect=[2,2]
- **Chicken** — anti-coordination game: mutual_coop=[3,3], sucker=[1,5], temptation=[5,1], mutual_defect=[0,0]

**Smoke results (5 seeds):**
- Stag Hunt: C2=601.4, C5=603.8, C1=579.8, C3=C4=575.6 — same affect augmentation pattern as PD
- Chicken: C2=482.8, C5=482.0, C1=468.8, C3=C4=470.6 — augmentation present
- Chicken shows interesting dissociation: C2 higher payoff but C1 better log-evidence (needs confirmation with 50 seeds)

**Confirmation experiments (50 seeds) RUNNING:**
- Stag Hunt default + betrayal: task b42v6f240
- Chicken default + betrayal: task b8h66w0z4
- Results will be in `results/phase7_full/`

## What's Been Implemented This Session

### Phase 6
1. `BaseAgent._compute_round_log_evidence()` — per-round log p(partner_action | model)
2. `cumulative_log_evidence` tracking in agent metrics and CSV output
3. `affect_aif/analysis/model_comparison.py` — log-evidence summaries, pairwise BFs, RFX-BMS
4. `scripts/run_model_comparison.py` — CLI
5. 8 new tests (77 total pass)
6. `docs/theory.md` §4.16 — theory section on Bayesian model comparison
7. `docs/results_tracking.md` — Phase 6 results section with full tables
8. `docs/long_term_plan.md` — Phase 6 marked complete

### Phase 7
1. 4 new configs: stag_hunt_default, stag_hunt_betrayal, chicken_default, chicken_betrayal
2. `scripts/run_cross_game_comparison.py` — cross-game analysis
3. Smoke experiments completed (5 seeds)
4. 50-seed confirmation experiments launched (still running)

## Auto Handoff
- **What changed:** Phase 6 fully complete. Phase 7 started with Stag Hunt and Chicken games.
- **What is still in flight:** Two experiment batches running (stag hunt 50-seed, chicken 50-seed). Check `results/phase7_full/` for output CSVs.
- **What next session should do:**
  1. Check if experiments finished (look for results CSVs in `results/phase7_full/`)
  2. If finished: run analysis (`scripts/run_analysis.py` and `scripts/run_model_comparison.py`) on each game
  3. Run cross-game comparison (`scripts/run_cross_game_comparison.py`)
  4. If experiments crashed or stalled: rerun with the same configs
  5. Document findings in `docs/results_tracking.md` and `docs/theory.md`
  6. Update `docs/long_term_plan.md` with Phase 7 status
  7. If results are clean, mark Phase 7 as complete and update MISSION status

Model-Hint: opus

## Status
CONTINUE — Phase 7 experiments running. Next session should analyze results.
