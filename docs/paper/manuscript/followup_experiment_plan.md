# Follow-Up Experiment Plan

Last updated: 2026-06-02

## Overview

The manuscript's contribution now has two layers:
1. **Core mechanism**: partner-local affective precision as social metacognition
   (H0-H6 spine)
2. **Individual differences extension**: affective precision parameters define
   testable social trust calibration profiles (Exp A-D)

Exp A-D are running on the server. Core confirmation runs follow after Exp A-D
complete and are reviewed.

---

## Phenotype Experiments (Exp A-D)
### Status: running on server as of June 2, 2026

These experiments fill the `\resultp{}` placeholders in Section 3.6 of the
manuscript. Each script is standalone (not TOML-based) and writes outputs
directly to `results/exp_*/` plus compact metric tables to
`docs/paper/manuscript/source_tables/exp_*/` and figures to
`docs/paper/manuscript/figures/`.

### Exp A — α Sweep

**Script**: `scripts/experiment/run_exp_a_alpha_sweep.py`

**Purpose**: Test whether precision-gain values produce a systematic
behavioural profile across the planned Section 3.6 readouts. Replaces the
earlier parameter sanity check with a controlled sweep.

**Design**:
- α values: `[0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 4.0, 8.0]`
- Environments: open graded + betrayal (both required)
- Seeds: 20 per condition

**Metrics**:
- `early_exploitation_rate`: cooperation rate with exploiter-type, rounds 1–30
- `betrayal_recovery_time`: rounds post-switch until selection rate returns
  within 10% of pre-betrayal baseline
- `selection_gini`: Gini coefficient of partner selection distribution
- `entropy_trajectory`: rolling 20-round policy entropy at early/mid/late
- `beta_range`: mean per-partner beta range across episode

**Expected pattern**: monotonic relationship between α and reactive social
confidence. Low α → rigid, stable, slow-updating. High α → rapid swings, sharp
concentration but noisy. Payoff does not rank α monotonically.

**Figure A**: 5-panel. Top: exploitation rate, recovery time, selection Gini
(line plots, α on x-axis, 95% CI). Bottom: entropy trajectory (three lines per
α), beta range. Cool-to-warm color gradient. Annotate phenotype zones: Rigid
(α ≤ 0.1), Calibrated (default ± 0.3), Reactive (α ≥ 3.0).

**Output**: `docs/paper/manuscript/figures/fig_alpha_sweep.pdf`

---

### Exp B — 2×2 Prior × α Factorial

**Script**: `scripts/experiment/run_exp_b_prior_factorial.py`

**Purpose**: Test four behavioural phenotype targets from crossing prior
belief (naive vs cautious) with precision gain (low vs high).

**Design**:
- Prior conditions:
  - Naive: `q(β_k)` weights `{0.5: 0.4, 0.67: 0.4, 1.0: 0.15, 1.5: 0.04, 2.0: 0.01}`
  - Cautious: `q(β_k)` weights `{0.5: 0.01, 0.67: 0.04, 1.0: 0.15, 1.5: 0.4, 2.0: 0.4}`
  - Default: current initialisation (reference arm)
- α conditions: `low = 0.1`, `high = 3.0`, plus default reference
- Full factorial: 2 priors × 2 α levels = 4 phenotype conditions + default
- Environments: open graded, betrayal, partner-choice
- Seeds: 20 per condition

**Additional metric**: `trust_asymmetry` — ratio of (rounds to first high-
confidence approach of new partner) to (rounds to first high-confidence
withdrawal after first defection). Values > 1 mean faster to approach than to
withdraw.

**Target phenotypes**:

| Phenotype | Prior | α | Core signature |
|---|---|---|---|
| Anxious-Reactive | Naive | High | Fast to trust and distrust, high βk volatility |
| Hypervigilant | Cautious | High | Slow to trust even with evidence, fast to distrust |
| Naive-Stubborn | Naive | Low | Slow to update, high early exploitation rate |
| Avoidant-Rigid | Cautious | Low | Chronically wary, low payoff, low trust asymmetry |

**Figure B**: 2×2 radar charts, one per phenotype. Five axes: exploitation
rate, recovery time, selection Gini, trust asymmetry, mean payoff (normalised
0–1). Overlay default agent profile as dashed line on each. Label each
quadrant with phenotype name and 1-line human analogue.

**Output**: `docs/paper/manuscript/figures/fig_phenotype_quadrants.pdf`

---

### Exp C — Forgiveness Paradigm

**Script**: `scripts/experiment/run_exp_c_forgiveness.py`

**Purpose**: Test re-engagement and trust recovery after a betraying partner
reverts to cooperative behaviour. Connects to forgiveness and reconciliation
literature.

**Episode structure**:
- Rounds 1–80: cooperative baseline
- Rounds 81–120: betrayal (switch to hostile)
- Rounds 121–200: reversion to cooperative

**Conditions**: all 4 phenotype conditions from Exp B + default + no-affect
baseline.

**Seeds**: 20 per condition.

**Metrics**:
- `reengagement_rate`: mean selection rate of reverted partner, rounds 121–200
- `payoff_recovery`: payoff from reverted partner rounds 151–200 vs rounds
  50–80 (late pre-betrayal baseline)
- `beta_recovery_trajectory`: βk for reverted partner, rounds 80–200
- `reengagement_latency`: rounds after reversion before first re-approach

**Key dissociation**: low-gain → slow forgiveness but complete recovery once
started (α effect). Cautious-prior → faster initial re-approach but lower
payoff recovery ceiling (prior effect). Maps onto: forgiveness = dynamic
re-engagement (α-driven) vs trust repair = structural confidence restoration
(prior-driven).

**Figure C**: 3-panel. Left: reengagement rate as bar chart by condition.
Middle: beta recovery trajectory lines (rounds 80–200) with vertical dashed
lines at betrayal onset and reversion. Right: payoff recovery ratio bar chart
with reference line at 1.0.

**Output**: `docs/paper/manuscript/figures/fig_forgiveness.pdf`

---

### Exp D — Mixed Volatility Environment

**Script**: `scripts/experiment/run_exp_d_mixed_volatility.py`

**Purpose**: Test whether partner-local affective precision correctly
discriminates between stationary and shifting partners within the same episode.
Critical test of behavioral necessity of partner-local vs global precision.

**Environment**:
- P0: stationary cooperator (never changes)
- P1: stationary exploiter (never changes)
- P2: abrupt-shift (cooperative 1–99, hostile 100–200)
- P3: gradual-drift (transitioning 50–150)

**Regime**: partner-choice.

**Conditions**: default α (3.0), low α (0.1), high α (8.0), no-affect
baseline. The high-α arm is deliberately distinct from the project default so
the mixed-volatility tradeoff can compare calibrated and reactive gain.

**Seeds**: 20 per condition.

**Metrics**:
- `discrimination_index`: Pearson correlation between per-partner βk trajectory
  and per-partner behavioural stability score
- `concentration_toward_P0`: rolling 20-round selection rate of P0
- `per_partner_beta_trajectories`: βk over time for each P0–P3
- `false_positive_rate`: rate where agent reduces engagement with P0 below 15%
  of baseline (P0 never changes, so all reductions are false alarms)

**Expected tradeoff**: high-α → better discrimination of P2/P3, higher
false-positive rate for P0. Low-α → poor P2/P3 discrimination, lower false
positives. Default → best tradeoff. This is the sensitivity-specificity
tradeoff in signal detection theory, applied to social confidence.

**Figure D**: 4-panel. Top left: per-partner βk trajectories, default agent.
Top right: same, high-α agent. Bottom left: discrimination index by agent type
(bar chart, 95% CI). Bottom right: concentration-toward-P0 line plot for all
agent types, with reference lines at P2 switch and P3 drift onset/end.

**Output**: `docs/paper/manuscript/figures/fig_mixed_volatility.pdf`

---

## After Exp A-D Complete

### Inspection Checklist (do before filling placeholders)

1. Confirm finality before reading metric values: the tmux/Mango process has
   ended, `results/exp_abcd_20260529_logs/run.log` contains `DONE`, and
   `results/exp_a/` through `results/exp_d/` each contain a final `results.csv`,
   `metrics.csv`, `manifest.json`, and `README.md`.
2. `mango cloud sync fetch affect_aif` — pull results from server if working
   from a local checkout.
3. Run `scripts/analysis/analyze.py` on each `results/exp_*/results.csv` where
   the generic analysis is applicable; the standalone Exp A-D scripts also
   write their own compact `metrics.csv` files and manuscript source tables.
4. Read the phenotype metric values only after finality is established; verify
   direction of effects against Section 3.6 narrative before filling any
   placeholders.
5. Check that `fig_alpha_sweep.pdf`, `fig_phenotype_quadrants.pdf`,
   `fig_forgiveness.pdf`, `fig_mixed_volatility.pdf` exist and are readable
6. Ask user before updating any interpretation narrative in `docs/results/`

### Placeholder Fill Checklist

After inspection is approved:
- Section 3.6.1: fill `\resultp{Exp A: ...}` with actual metric values and CIs
- Section 3.6.2: fill `\resultp{Exp B: ...}` per phenotype condition
- Section 3.6.3: fill `\resultp{Exp C: ...}` per condition
- Section 3.6.4: fill `\resultp{Exp D: ...}` per agent type

---

## Core Mechanism Confirmation Queue

See `docs/active/progress.md` for full commands and ordering. Priority:

1. **H5 betrayal** (30+ seeds) — primary behavioral confirmation target
2. **H1 redesign diagnostic** — must inspect before adding seeds
3. **H0/H2/H4 support** — only if diagnostic deployment/allocation language
   needs confirmation-scale support
4. **H3 global-beta ablation** — Exp D provides partial answer; dedicated run
   optional

---

## Stop Conditions

Pause before changing manuscript claims if:

- Exp A-D phenotype direction contradicts Section 3.6 predictions (flag to
  user; do not silently rewrite)
- Global beta matches local beta in Exp D interference/discrimination readouts
  (would weaken the locality claim)
- H5 confirmation run reverses the betrayal advantage (catastrophic for the
  paper; stop and redesign)
- Any design issue surfaces where affect inadvertently changes belief updating
  rather than only beta/precision deployment
