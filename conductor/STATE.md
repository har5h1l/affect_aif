---
status: CONTINUE
next_priority: 2
pending_work:
  - "Track 2.4: Full benchmark comparison running (scoring_loop + affect_cvc + starter, 10 seeds)"
  - "Track 1.2: Awaiting user decision on precision modulation (test or cut)"
  - "Track 3.3: Add CvC results to paper — now have data"
  - "Track 2.3: Spatial beta dynamics need parameter recalibration for meaningful modulation"
next_session_focus: "Analyze benchmark results, write CvC paper section, present Track 1.2 to user"
model_hint: opus
---

# Research State

## Last Updated
2026-03-27 (Session 12)

## Session Count
12

## Current Findings

### Trust-Game Results (Phases 1-7: COMPLETE)

All trust-game phases are complete with publication-quality results. Full results in docs/results_tracking.md.

### Session 12: CvC Breakthrough — Non-Zero Scores + Diagnostic Discovery (2026-03-27)

**Branch:** `mango/affect_aif/20260326-211344` — 3 commits this session

#### Environment Setup

Created conda env `cvc` with Python 3.12 + cogames 0.21.1 + mettagrid 0.21.1 on server machine. The `affect_aif` conda env only has Python 3.11 which can't run cogames.

#### DECISION: Wall Detection — aoe_mask, Not Feature Names

The mettagrid observation encodes walkable cells via `aoe_mask=1` tokens. Walls and out-of-view cells simply LACK this feature — they are never explicitly encoded as wall tokens. The previous approach guessed feature names ("wall", "obstacle", "blocked") that never matched, making every cell appear walkable (hence 80%+ wall collisions).

Fix: `_build_local_walkability` now starts with all cells unwalkable, then marks cells WITH `aoe_mask` as passable. Combined with movement-failure wall learning (expiry=15 steps), this achieves **84-91% movement success rate**.

#### DECISION: Teammate Detection — agent_id Feature, Not Tag Exclusion

Observation tag values use `object_type_names` indices (hub=7, junction=8, extractor=5) but `_structure_tag_ids` was built from PEI tag indices (hub=15, junction=16, extractor=13). This mismatch caused structures to be misidentified as teammates, producing frozen beta values for non-moving "teammates."

Fix: detect teammates via the `agent_id` feature instead. Each agent in the observation has an `agent_id` token at their location, providing reliable teammate identification.

#### CvC Diagnostic Results

| Finding | Value |
|---------|-------|
| Observation grid | 13x13 diamond centered on agent |
| Walkable cells | 121 per observation (aoe_mask=1) |
| Wall/OOV cells | 48 per observation (no aoe_mask) |
| Wall tag exists | Yes (tag=12), but walls also lack aoe_mask |
| Object types visible | hub, junction, extractors, agents, wall, ship |
| Available missions | 28 total; key: machina_1 (98x98), arena (60x60), tutorial (45x45) |
| API | Simulation class (not MettaGridEnv), set_action(string), step() |

#### CvC Benchmark Results — NON-ZERO SCORES

**Smoke test (5 seeds, 1000 steps, machina_1):**

| Metric | ScoringLoopPolicy | AffectCvCPolicy |
|--------|-------------------|-----------------|
| Mean reward | 0.132 | 0.132 |
| Aligned junctions | 4.4 | 4.4 |
| Hearts withdrawn | 5.0 | 5.0 |
| Ore deposited | 264 | 264 |
| Move success rate | 84.2% | 84.2% |

Results are identical because beta dynamics don't create behavioral differentiation in this setting (see below).

#### DECISION: Beta Dynamics in Spatial Domain

Key finding: trust-game beta parameters don't differentiate policies in spatial CvC.

**Why identical results:** team_beta_ema stabilizes at ~0.65 (consistently above COOPERATE_THRESHOLD=0.6). Even with random teammates, beta stays 0.57-0.68 because:
1. Position prediction errors are small relative to normalization range (max_obs_distance=26)
2. Random movement has low surprise (equiprobable directions → mean velocity ≈ 0)
3. Sigmoid squashing + EMA smoothing (λ=0.6) dampen fluctuations
4. Ore comes in bursts of 10+, so cargo-threshold modulation (5 vs 8) never triggers at different steps

NEXT: The architecture transfers successfully (beta tracking works, 7 real teammates identified, per-partner values are sensible). For behavioral differentiation, need either:
- Heterogeneous teams (some agents use different strategies)
- Domain-specific parameter calibration (larger alpha, lower sigma_0_sq)
- Or simply frame as "correct architectural transfer with homogeneous-team baseline"

### Track 2: CvC Benchmark — Status

| Step | Status | Details |
|------|--------|---------|
| 2.1 | **COMPLETE** | aoe_mask-based wall detection, 84-91% move success |
| 2.2 | **COMPLETE** | ScoringLoopPolicy scores non-zero (mean reward 0.13) |
| 2.3 | **COMPLETE** (tracking works; modulation needs calibration) | AffectCvCPolicy: agent_id detection, beta ~0.65, same scores as baseline |
| 2.4 | **IN PROGRESS** | Full benchmark running (10 seeds, 3 policies: scoring_loop, affect_cvc, starter) |
| 2.5 | **COMPLETE** | 28 missions discovered; tutorial (45x45) and arena (60x60) available |

### Track 1: Paper Theory Gaps

All complete from session 9 except Track 1.2 (precision modulation: test or cut) — still awaits user decision.

### Track 3: Paper Preparation

3.1-3.2 complete. 3.4 partially done. **3.3 can now proceed** — we have CvC results data.

## Auto Handoff
- **What changed:** Session 12 set up Python 3.12 + cogames env, discovered wall encoding (aoe_mask), fixed wall detection and teammate detection, achieved non-zero CvC scores. Both ScoringLoopPolicy and AffectCvCPolicy produce identical results (mean reward 0.13, 4.4 aligned junctions) because beta dynamics are too stable in homogeneous teams for modulation to trigger.
- **What is still in flight:** Full benchmark comparison (3 policies × 10 seeds) running in background. Track 1.2 awaits user. Track 3.3 ready to write.
- **What next session should do:**
  1. Check benchmark results — analyze scoring_loop vs affect_cvc vs starter
  2. Write CvC results section for paper (Track 3.3)
  3. Present Track 1.2 decision to user
  4. Consider beta parameter recalibration for spatial domain (optional — current results sufficient for "architectural generality" claim)

## Status
CONTINUE — Benchmark running, CvC paper section ready to write, Track 1.2 awaits user
