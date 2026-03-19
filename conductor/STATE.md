# Research State

## Last Updated
2026-03-19

## Session Count
4

## Current Findings

### Phase 6 (COMPLETE)
Bayesian model comparison. Per-round log-evidence computed for all agent variants, pairwise Bayes factors and RFX-BMS (Stephan et al. 2009) implemented.

- **Default (PD, 50 seeds):** C5 wins RFX-BMS (exceedance 1.000). C2/C5 substantially better than non-affect (log10 BF ≈ 0.7–0.9).
- **Betrayal (PD, 50 seeds):** C2 wins **decisively** — log10 BF = 3.00 vs C1, 2.70 vs C5. Exceedance 0.998.

### Phase 7 (COMPLETE)
Cross-game generalization tested with Stag Hunt and Chicken (zero code changes, config-only).

**Default conditions:**
| Game | H1 d | H1 p | RFX-BMS winner |
|---|---|---|---|
| PD | 0.62 | 0.003 | C5 (exc=1.000) |
| Stag Hunt | 0.50 | 0.015 | C2 (exc=0.992) |
| Chicken | 0.05 | 0.795 | C2 (exc=0.710) |

**Betrayal conditions:**
| Game | H1 d | H1 p | C2 vs C5 BF | RFX-BMS winner |
|---|---|---|---|---|
| PD | 1.30 | <0.001 | +2.70 decisive C2 | C2 (0.998) |
| Stag Hunt | 1.60 | <0.001 | +1.08 strong C2 | C2 (0.954) |
| Chicken | 1.12 | <0.001 | -1.07 strong C5 | C5 (0.931) |

**Key insights:**
1. Augmentation generalizes under volatility (d > 1.0 in ALL games)
2. Game-dependent in stable conditions (PD/SH strong, Chicken negligible)
3. Stag Hunt uniquely favors precision tracking (C2 wins both conditions)
4. Chicken favors reward averaging under betrayal
5. Precision tracking excels where miscoordination penalty is severe

### Implementation Delivered This Session
1. `BaseAgent._compute_round_log_evidence()` — per-round log p(partner_action | model)
2. `affect_aif/analysis/model_comparison.py` — BFs, RFX-BMS, protected exceedance
3. `scripts/run_model_comparison.py`, `scripts/run_cross_game_comparison.py` — CLIs
4. 8 new tests (77 total pass)
5. Stag Hunt + Chicken configs (default + betrayal, 4 configs)
6. Theory: §4.16 (Bayesian model comparison), §4.17 (cross-game generalization)
7. Full documentation in results_tracking.md and long_term_plan.md

## Auto Handoff
- **What changed:** Phases 6 and 7 complete in a single session. All code, experiments, analysis, and documentation delivered.
- **What is still in flight:** Nothing.
- **What next session should do:** Phase 5 (clinical sensitivity) could be revisited using the graded game or Stag Hunt (both have more ambiguous EFE landscapes). Phase 8 (human data) requires user decision. No other autonomous work remains.

Model-Hint: opus

## Status
DONE — Phases 6 and 7 complete. Phase 5 blocked, Phase 8 requires user. Awaiting user decision.
