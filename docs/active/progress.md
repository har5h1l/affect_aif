# Next Runs

Re-run the verification gate below immediately before launching full
statistical experiments so queued runs carry fresh local provenance.

## Verification Gate

Run these before scheduling current-evidence experiments:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
git diff --check
```

## Current Queue Status

As of May 31, 2026, the manuscript has been substantially revised toward the
full individual-differences / phenotype framing. The canonical affect update
uses Hesp-style surprisal with neutral baseline `sigma_0_sq = (-log 0.5)^2`.

### June 2 H1 Analysis/Design Checkpoint

The current code/config checkpoint is `c5bc373`, after the H1
active-encounter alignment fix, richer H1 confound diagnostics, and the two
controlled H1 diagnostic configs. Current `master` may have docs-only
synchronization commits on top. The previous `3a36756` and `942c595` notes are
stale; later H1 handoff and controlled-diagnostic commits sit on top.

Keep long experiments on `server`. The Exp A-D tmux/Mango process
`affect_aif_exp_abcd_20260529` is still running and monitor-only. As of
June 2 01:00 PDT, Exp A has written `results/exp_a/` and manuscript source
tables, while Exp B is active in
`scripts/experiment/run_exp_b_prior_factorial.py`; its
`results/exp_b/betrayal/results_partial.csv` last updated at
June 2 00:41:42 PDT and Exp C/D have not started. Do not interpret Exp A or
partial Exp B outputs as manuscript evidence until Exp A-D complete and the
user approves result interpretation updates.

The full local pytest gate is clean as of June 2 01:00 PDT. The previous
stall was diagnosed as oversized test fixtures that imported the full H5
betrayal config for narrow integration/theory assertions. Those tests now use
tiny scheduled-switch specs; no model math, task runtime, or manuscript
experiment config changed.

On June 2, the planning/manuscript docs were synchronized with the corrected
H1 active-encounter analysis status. Historical pre-log-surprisal confirmation
notes remain as provenance, but current planning pages now treat H1 as
smoke-supported and awaiting confirmation or controlled diagnostic escalation
before manuscript use.

As of June 2 01:22 PDT, Exp B is still CPU-active in the same tmux/Mango
process; `results/exp_b/betrayal/results_partial.csv` updated at 01:20 PDT.
Continue monitor-only and do not interpret Exp A/B outputs until Exp A-D
complete.

The H1 manuscript figure/source-table path now uses the partial model-fitness
readout (`abs_partial_corr_precision_surprise_minus_reward`) alongside the
active-encounter partial correlation columns. The default paper figure builder
was verified against the current source-table packet in `/tmp` after refreshing
the H1 source tables from the post-fix smoke results.

```text
tmux: affect_aif_full_pytest_20260602_final
log: /tmp/affect_aif_full_pytest_20260602_final.log
HEAD under test: 2424211
working-tree fixture diff hash: c2695914b969ab5bd299bd32f9a78a3a7cc10fa6ada98d3f00aa78adb81b2e08
pytest: 308 passed, 7 skipped, 74 warnings in 730.13s
ruff: All checks passed
mypy: Success, no issues found in 15 source files
git diff --check: clean
```

Mango registration for the final full-pytest tmux process failed because
`mango_service` timed out, but the process ran isolated in tmux and completed.
The Exp A-D Mango entry remained visible and running. Re-run the verification
gate before scheduling any later confirmation-scale experiments if code changes
again.

The post-fix H0-H6 smoke rebaseline completed at:

```text
results/log_surprisal_spine_smoke_postfix_20260528/
```

This is the current diagnostic baseline. Four phenotype experiments (Exp A-D)
are running on the server to fill the Section 3.6 placeholders. Confirmation-
scale runs for the core hypothesis spine are the next priority after Exp A-D
complete.

## Phenotype Experiment Queue (Exp A-D)
### Status: running on server

These fill Section 3.6 of the manuscript with actual numbers. They run via
standalone scripts rather than TOML spec configs.

### Exp A — α Sweep

```bash
.venv/bin/python scripts/experiment/run_exp_a_alpha_sweep.py
```

- **α values**: `[0.05, 0.1, 0.3, 0.5, 1.0, 2.0, 4.0, 8.0]`
- **Environments**: open graded + betrayal
- **Seeds**: 20 per condition
- **Outputs**: `results/exp_a/`, figures → `docs/paper/manuscript/figures/fig_alpha_sweep.pdf`
- **Metrics**: `early_exploitation_rate`, `betrayal_recovery_time`, `selection_gini`,
  `entropy_trajectory` (early/mid/late), `beta_range`
- **Manuscript target**: Section 3.6.1 placeholders (`\resultp{Exp A: ...}`)

### Exp B — 2×2 Prior × α Factorial

```bash
.venv/bin/python scripts/experiment/run_exp_b_prior_factorial.py
```

- **Prior conditions**: naive (low-β weights), cautious (high-β weights), default
- **α conditions**: `low = 0.1`, `high = 3.0`, default reference
- **Environments**: open graded, betrayal, partner-choice
- **Seeds**: 20 per condition
- **Outputs**: `results/exp_b/`, figures → `docs/paper/manuscript/figures/fig_phenotype_quadrants.pdf`
- **Metrics**: all Exp A metrics + `trust_asymmetry`
- **Target phenotypes**: anxious-reactive, hypervigilant, naive-stubborn, avoidant-rigid
- **Manuscript target**: Section 3.6.2 placeholders

### Exp C — Forgiveness Paradigm

```bash
.venv/bin/python scripts/experiment/run_exp_c_forgiveness.py
```

- **Episode structure**: cooperative (1–80), betrayal (81–120), reversion (121–200)
- **Conditions**: all 4 phenotype conditions + default + no-affect baseline
- **Seeds**: 20 per condition
- **Outputs**: `results/exp_c/`, figures → `docs/paper/manuscript/figures/fig_forgiveness.pdf`
- **Metrics**: `reengagement_rate`, `payoff_recovery`, `beta_recovery_trajectory`,
  `reengagement_latency`
- **Manuscript target**: Section 3.6.3 placeholders

### Exp D — Mixed Volatility Environment

```bash
.venv/bin/python scripts/experiment/run_exp_d_mixed_volatility.py
```

- **Partner setup**: P0 stationary cooperator, P1 stationary exploiter,
  P2 abrupt-shift (cooperative rounds 1–99 → hostile), P3 gradual-drift (rounds 50–150)
- **Regime**: partner-choice
- **Conditions**: default, low α (0.1), high α (3.0), no-affect baseline
- **Seeds**: 20 per condition
- **Outputs**: `results/exp_d/`, figures → `docs/paper/manuscript/figures/fig_mixed_volatility.pdf`
- **Metrics**: `discrimination_index`, `concentration_toward_P0`, per-partner beta
  trajectories, `false_positive_rate`
- **Manuscript target**: Section 3.6.4 placeholders

### After Exp A-D Complete

1. Run `scripts/analysis/analyze.py` on each `results/exp_*/` output.
2. Fill `\resultp{...}` placeholders in `sections/03_results.tex` Section 3.6.
3. Check that phenotype descriptions match the actual metric values.
4. Update `docs/results/current.md` with phenotype findings (ask user before
   updating interpretation narrative).
5. Proceed to confirmation-scale runs below.

---

## Core Hypothesis Confirmation Queue

Do not launch this queue until the verification gate passes and Exp A-D are
complete or explicitly approved by user.

### Priority 1: H5 Betrayal Confirmation (most important)

H5 is the repaired positive behavioral anchor after the selector fix.

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation_confirm.toml \
  --output-dir results \
  --batch-name log_surprisal_h5_confirm_postfix_20260601 \
  --workers 1
```

**Primary readouts**: total payoff by variant; post-switch reallocation and
reencounter rate; policy entropy and joint accuracy; payoff conditional on
returned/switched partner.

**Seed target**: 30+ seeds minimum for publication-grade claim.

### Priority 2: H1 Model Fitness Corrected-Readout Confirmation

The old post-fix H1 smoke read mixed carried per-partner precision/surprise
state with active-encounter payoff. The corrected active-encounter readout
restores the surprise-over-reward diagnostic in the smoke, and the stricter
partial-correlation readout controls active payoff and encounter count. This
does not make H1 publication-grade; confirm before using model-fitness as a
manuscript claim. Redesign the task only if the corrected confirmation remains
reward/exposure-confounded.

```bash
# diagnostic first — do not add seeds before inspecting design
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml \
  --output-dir results \
  --batch-name log_surprisal_h1_diagnostic_YYYYMMDD \
  --workers 1
```

**Action items before running**:
- Use the corrected `model_fitness_correlation_summary.csv` columns:
  `alignment`, `partial_corr_precision_surprise`, and
  `partial_corr_precision_reward`.
- Use `evidence_effect_summary.csv` metric
  `abs_partial_corr_precision_surprise_minus_reward` for manuscript figure
  effect panels; the raw correlation gap remains a secondary diagnostic.
- Treat whole-run payoff as secondary; H1 is about model fitness, not reward
  advantage.
- If corrected confirmation remains confounded, run the balanced-exposure
  graded reliability spine before adding more seeds:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_spine_graded_diagnostic.toml \
  --output-dir results \
  --batch-name log_surprisal_h1_graded_spine_diagnostic_YYYYMMDD \
  --workers 1
```

- If the graded spine still cannot separate reward/exposure from predictive
  reliability, run the strict reward-neutral diagnostic:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_reward_neutral_diagnostic.toml \
  --output-dir results \
  --batch-name log_surprisal_h1_reward_neutral_diagnostic_YYYYMMDD \
  --workers 1
```

Interpretation rule: a pass on reward-neutral H1 with a failure on graded H1 is
an analysis/task-design confound, not a model-level failure. A failure on both
would justify reframing H1 before more confirmation-scale seeds.

### Priority 3: H0/H2/H4 Manuscript Support (run if language stays in draft)

Only launch if the manuscript keeps deployment/entropy and partner-choice
language and needs higher-seed confirmation for those claims.

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h0_policy_openness/graded_choice_confirm.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml \
  --config configs/trust/hypotheses/h4_social_allocation/partner_choice_confirm.toml \
  --output-dir results \
  --batch-name manuscript_open_social_confirm_YYYYMMDD \
  --workers 1
```

### Priority 4: H3 Global-Beta Ablation

Whether partner-local precision is necessary or whether a shared tracker
produces comparable stable-regime gains is now a stated question in the
manuscript (Discussion, Future Directions) and Section 3.3. The mixed-
volatility paradigm (Exp D) provides a partial answer; a dedicated H3 confirm
run at higher seeds will strengthen the locality claim if Exp D shows the
expected interference pattern.

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h3_locality/global_beta_locality_probe.toml \
  --output-dir results \
  --batch-name h3_global_beta_confirm_YYYYMMDD \
  --workers 1
```

---

## Post-Fix Smoke Evidence Summary

Results from `results/log_surprisal_spine_smoke_postfix_20260528/` — current
diagnostic baseline, not final publication evidence.

```text
H0: no stable payoff advantage; affect/global beta/no-affect are close.
H1: corrected active-aligned read preserves surprise-over-reward in smoke;
requires confirmation before manuscript use.
H2: deployment path is active (entropy 8.59 vs 8.79); payoff flat.
H3: global beta has the best smoke payoff; local beta = cleaner signal.
H4: partner-choice payoff noisy and flat at three seeds.
H5: repaired under centered selector; affect beats no-affect/lesioned.
H6: perturbation dynamics separate; clinical claims remain supplemental only.
```

Numbers used in manuscript:
- H2: policy entropy 8.59 (local affect) vs 8.79 (no-affect)
- H3: local corr(precision,surprise)=0.943 vs 0.110 (payoff); payoffs: global
  976.2, local 946.8, no-affect 950.7
- H5: payoff 1322.3 (local affect) vs 1225.0 (no-affect); entropy 7.47 vs
  8.68; joint accuracy 0.319 vs 0.425
- H6: alexithymia beta range 0.180, borderline 1.412, depression 1.464

---

## Result Interpretation Rules

- Do not treat partial detached rerun outputs as current evidence.
- Do not promote new outputs into manuscript-level claims without user review.
- Keep H7 signal-source and H8 observation-noise lanes exploratory.
- Ask user before updating interpretation narrative in `docs/results/current.md`.

## Historical Provenance

Pre-log-surprisal and pre-fix diagnostic outputs remain in `docs/results/`.
They should not be used as current manuscript evidence.
