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

### June 3 Phenotype Recovery Run

The original Exp A-D tmux/Mango process `affect_aif_exp_abcd_20260529`
stopped without reaching finality: no live `run_exp_*` process, no tmux
session, no `DONE` marker in `results/exp_abcd_20260529_logs/run.log`, no
Exp C/D outputs, and no top-level final Exp B `results.csv`. Exp B had
completed `open_graded` and `betrayal`; `partner_choice` had 116/120 complete
runs, missing only no-affect replications 16--19. Those completed raw
trajectories remain valid and are being reused through the existing checkpoint
resume path in `ExperimentRunner.run_all()`.

Recovery is running in tmux/Mango:

```text
tmux: affect_aif_exp_recovery_20260603
log: results/exp_abcd_recovery_20260603_logs/run.log
HEAD: 972f13b
Mango: affect_aif_exp_recovery_20260603, monitor-only
```

Seed/round decision: keep phenotype experiments at 20 seeds x 200 rounds. This
is large enough for manuscript summaries and confidence intervals, avoids
underpowered tiny follow-ups, and avoids expanding compute beyond the already
partly completed Exp A/B design.

Recovery order is least-to-most incremental cost, with analysis between
stages:

1. Full verification gate: `pytest tests/ -q`, `ruff check .`, `mypy`,
   `git diff --check`.
2. Exp A `--analyze-only`, then generic `scripts/analysis/analyze.py` on
   `results/exp_a/results.csv`.
3. Exp B resume from checkpoints, then generic analysis on
   `results/exp_b/results.csv`.
4. Exp D full run and generic analysis (80 runs: 4 variants x 20 seeds).
5. Exp C full run and generic analysis (120 runs: 6 variants x 20 seeds).
6. `RECOVERY_DONE` marks finality for the recovery session.

Current recovery status on June 4 17:50 PDT:

- Verification gate passed in the recovery log:
  `324 passed, 7 skipped, 74 warnings in 504.08s`; ruff passed; mypy passed;
  `git diff --check` passed.
- Exp A analyze-only regeneration and generic analysis completed. Operational
  artifacts now exist at `results/exp_a/analysis/` and
  `docs/paper/manuscript/figures/fig_alpha_sweep.pdf`. Do not interpret the
  printed metric values as manuscript results until full Exp A-D finality and
  user-approved review.
- Exp B resume completed. Structural audit shows all three Exp B environments
  complete: `open_graded`, `betrayal`, and `partner_choice` each have 120
  run groups x 200 rounds, and top-level `results/exp_b/results.csv` has 360
  run groups / 72,000 data rows. Compact outputs exist at
  `results/exp_b/metrics.csv`,
  `docs/paper/manuscript/source_tables/exp_b_prior_factorial/`, and
  `docs/paper/manuscript/figures/fig_phenotype_quadrants.pdf`. Generic
  analysis completed under `results/exp_b/analysis/`.
- Exp D completed operationally. Structural audit found 80/80 complete seed
  groups x 200 rounds, with all four variants complete. Final
  `results/exp_d/results.csv`, `results/exp_d/metrics.csv`,
  `results/exp_d/manifest.json`, `results/exp_d/README.md`,
  `results/exp_d/analysis/`, `docs/paper/manuscript/source_tables/exp_d_mixed_volatility/metrics.csv`,
  and `docs/paper/manuscript/figures/fig_mixed_volatility.pdf` exist. Do not
  interpret metric values until Exp A-D finality and user-approved review.
  Preliminary user-requested Exp D review on June 4 found that the current
  compact readout is not manuscript-ready for the strong planned
  mixed-volatility claim. Raw outputs are structurally valid, but the
  whole-episode `discrimination_index` and derived time-resolved beta-drop
  diagnostic only partially match expectations. Before filling Section 3.6.4,
  either revise/soften the claim around what Exp D actually supports or add a
  clearer time-resolved discrimination/tradeoff readout from existing raw
  trajectories.
- Exp C started at 14:16 PDT and is now the active recovery stage. A
  structural-only check at 17:50 PDT found 47 complete seed groups out of the
  planned 120 groups (`naive_low_alpha` and `naive_high_alpha` complete,
  `cautious_low_alpha` in progress). Continue monitor-only unless the process
  exits, loses CPU without I/O, or logs an error.
- Diagnostic Exp A/B audit at 23:41 PDT found complete raw trajectories and
  compact metrics for Exp A/B with expected run counts: Exp A has 320/320
  groups x 200 rounds, and Exp B has 360/360 groups x 200 rounds. No raw
  trajectory deletion or task rerun is indicated from this structural audit. On
  June 4, compact Exp A/B outputs were regenerated from existing raw
  trajectories after adding explicit post-betrayal P0 selection and
  high-investment commitment rates. This resolves the immediate
  analysis-language risk without changing task dynamics, model math, or raw
  trajectories.

Manuscript-critical evidence audit at 14:47 PDT:

| Evidence surface | Planned size | Current artifact state | Manuscript status |
|---|---:|---|---|
| Exp A alpha sweep | 320 runs: 2 environments x 8 alpha values x 20 seeds, 200 rounds | Final `results.csv`, `metrics.csv`, `manifest.json`, `README.md`, generic `analysis/`, source table, and `fig_alpha_sweep.pdf` exist | Operationally ready, but do not interpret until Exp A-D recovery finality and user-approved review |
| Exp B prior x alpha factorial | 360 runs: 3 environments x phenotype/default arms x 20 seeds, 200 rounds | Final `results.csv`, `metrics.csv`, `manifest.json`, `README.md`, generic `analysis/`, source table, and `fig_phenotype_quadrants.pdf` exist | Operationally ready, but do not interpret until Exp A-D recovery finality and user-approved review |
| Exp D mixed volatility | 80 runs: 4 variants x 20 seeds, 200 rounds | Final `results.csv`, `metrics.csv`, `manifest.json`, `README.md`, generic `analysis/`, source table, and `fig_mixed_volatility.pdf` exist | Operationally ready, but do not interpret until Exp A-D recovery finality and user-approved review |
| Exp C forgiveness | 120 runs: 6 variants x 20 seeds, 200 rounds | Running as active recovery stage; partial checkpoint has 47/120 complete seed groups as of June 4 17:50 PDT | Pending; critical for forgiveness/trust-repair readout |
| H5 confirmation | 120 runs in current confirm spec: 4 variants x 30 seeds, 120 rounds | Not yet queued in recovery | Top core-mechanism confirmation after Exp A-D |
| H1 confirmation | 90 runs in corrected confirm spec: 3 variants x 30 seeds, 200 rounds | Not yet queued in recovery | Required before using H1 as publication-grade model-fitness evidence |
| H1 controlled diagnostics | 20 runs each for balanced graded, reward-matched graded, and reward-neutral diagnostics | Dry-run/smoke-checked only | Escalate only if corrected H1 confirmation remains reward/exposure-confounded |

Seed/round audit: keep Exp A-D at 20 seeds x 200 rounds because these runs are
already partly complete, cover within-episode transients needed by Section 3.6,
and provide enough replication for compact CIs without expanding compute. For
core confirmation, use the existing 30-seed specs first: H5
`betrayal_reallocation_confirm.toml` is 4 variants x 30 seeds x 120 rounds, and
H1 `reliability_vs_reward_confirm.toml` is 3 variants x 30 seeds x 200 rounds.
Do not add more seeds until the first confirmation pass is analyzed; if H1 is
ambiguous, escalate to controlled diagnostics before increasing replication.

Do not read or interpret phenotype metric values until recovery finality is
confirmed and the user approves result interpretation updates.

As of May 31, 2026, the manuscript has been substantially revised toward the
full individual-differences / phenotype framing. The canonical affect update
uses Hesp-style surprisal with neutral baseline `sigma_0_sq = (-log 0.5)^2`.

### June 2 H1 Analysis/Design Checkpoint

The H1 analysis/config checkpoint is `a5161e0`, after the H1 active-encounter
alignment fix, richer H1 confound diagnostics, reward-neutral readout handling,
and the controlled H1 diagnostic configs. Later checkpoints aligned the
manuscript evidence boundary (`07b31d0`), Exp D alpha-arm separation
(`ff8c3fe`), Exp C/D pre-run metric definitions (`e66fc16`), and active
phenotype handoff (`b236bf8`). The previous `3a36756`, `942c595`, `c5bc373`,
and `f86ede4` notes are stale as current-state references.

Keep long experiments on `server`. The original Exp A-D tmux/Mango process
`affect_aif_exp_abcd_20260529` is superseded by
`affect_aif_exp_recovery_20260603`; use the recovery log and finality gate
above as the source of truth. Do not interpret Exp A/B partial outputs as
manuscript evidence until recovery completes and the user approves result
interpretation updates.

The full local pytest gate is clean as of June 2 01:00 PDT. The previous
stall was diagnosed as oversized test fixtures that imported the full H5
betrayal config for narrow integration/theory assertions. Those tests now use
tiny scheduled-switch specs; no model math, task runtime, or manuscript
experiment config changed.

On June 2, the planning/manuscript docs were synchronized with the corrected
H1 active-encounter analysis status and the manuscript prose was aligned with
the current evidence tier. Historical pre-log-surprisal confirmation notes
remain as provenance, but current planning pages now treat H1 as
smoke-supported and awaiting confirmation or controlled diagnostic escalation
before manuscript use.

Mango reports `affect_aif_exp_recovery_20260603` as running and monitor-only.
Continue monitor-only and do not interpret Exp A/B outputs until Exp A-D
complete.

June 4 monitor checks: server-side Mango still reports
`affect_aif_exp_recovery_20260603` as running and monitor-only. The old
`affect_aif_exp_abcd_20260529` Mango registration is obsolete and still points
to a missing tmux session; use the recovery process and log as source of truth.

Status classification from this monitor check:

- Exp A: final raw trajectories and regenerated compact outputs are
  structurally valid, but interpretation remains gated until full Exp A-D
  finality and user-approved review.
- Exp B: final raw trajectories and compact outputs are structurally valid,
  but the `betrayal_recovery_time` language/readout risk remains an
  analysis/manuscript issue, not a raw-rerun issue.
- Exp D: structurally complete and operationally analyzed, but not interpreted.
- Exp C: in-progress and structurally sane so far; not final, not obsolete,
  and not ready for analysis or interpretation.
- H1/H5 confirmations: not queued during recovery; next agent should not launch
  them until Exp A-D finality is established or the user explicitly changes the
  queue order.

The H1 manuscript figure/source-table path now uses the partial model-fitness
readout (`abs_partial_corr_precision_surprise_minus_reward`) alongside the
active-encounter partial correlation columns. The default paper figure builder
was verified against the current source-table packet in `/tmp` after refreshing
the H1 source tables from the post-fix smoke results.

The H1 diagnostic ladder was dry-run locally on June 2 and rechecked at
02:31 PDT: the corrected confirmation expands to 90 runs, the balanced graded,
reward-matched graded, and reward-neutral diagnostics expand to 20 runs each,
and the historical smoke `reliability_vs_reward.toml` expands to 9 runs. A
reduced-round local smoke of
`reliability_spine_graded_reward_matched_diagnostic.toml`
verified that the reward-matched graded spine executes end to end (40 rows:
4 variants x 1 seed x 10 rounds). A reduced-round local smoke of
`reliability_reward_neutral_diagnostic.toml` verified that constant payoff is
flagged as `reward_proxy_constant`, reward association is treated as zero for
the dominance diagnostic, and
`abs_partial_corr_precision_surprise_minus_reward` rows are emitted. This keeps
the strict reward-neutral diagnostic analyzable as a reliability test rather
than failing because reward variance was intentionally removed.

On June 2, before Exp C/D had started, Exp D's mixed-volatility high-gain arm
was corrected from `alpha=3.0` to `alpha=8.0`. This keeps the project default
(`alpha=3.0`) as the calibrated reference while making the high-gain arm a
distinct reactive comparison. Exp A/B outputs are not obsolete; Exp D had not
started, so no interruption or rerun was required.

Also before Exp C/D had started, Exp C's payoff-recovery metric was aligned to
the manuscript plan by using rounds 50--80 as the late pre-betrayal baseline,
and Exp D's `false_positive_rate` was aligned to the planned stable-partner
readout by measuring rolling P0 engagement drops more than 15% below its early
baseline. Exp A/B outputs are not obsolete; no interruption or rerun was
required.

Still before Exp C/D had started, the Exp C/D compact figure contracts were
aligned to the manuscript plan without changing task dynamics or the model
process. Exp C now writes partner-0 beta recovery trajectory columns for the
planned forgiveness figure and uses the planned three panels: reengagement
rate, beta recovery trajectory, and payoff recovery. Exp D now writes
per-partner beta trajectory snapshots and rolling P0-selection snapshots for
the planned mixed-volatility figure: default and high-alpha beta trajectories,
discrimination index with 95% CI, and concentration toward P0 with switch/drift
reference lines. Since Exp C/D had no outputs, no rerun or analyze-only
regeneration is required for those two experiments.

On June 2, while Exp B was still running, the Exp B compact analysis and figure
contract was aligned to the manuscript plan without changing task dynamics or
the model process. `metrics.csv` now reports `trust_approach_latency`,
`trust_withdrawal_latency`, and `trust_asymmetry =
trust_withdrawal_latency / trust_approach_latency`; the phenotype radar figure
uses the planned five axes: early exploitation rate, betrayal recovery time,
selection Gini, trust asymmetry, and mean payoff, with a dashed default-agent
overlay. The live Exp B raw trajectories remain valid, but the currently
running Python process loaded the older analysis code; after Exp A-D finality,
rerun Exp B with `--analyze-only` so `results/exp_b/metrics.csv`, source
tables, and `fig_phenotype_quadrants.pdf` use the updated readout.

Also while Exp B was still running, the Exp A compact analysis and figure
contract was aligned to the manuscript plan without changing task dynamics or
the model process. `early_exploitation_rate` now uses rounds 1--30 as written,
and `fig_alpha_sweep.pdf` now plots the planned early/mid/late entropy
trajectory with 95% confidence intervals on the sweep panels. Exp A raw
trajectories remain valid, but the already-written Exp A compact outputs were
produced by the older analysis code; after Exp A-D finality, rerun Exp A with
`--analyze-only` so `results/exp_a/metrics.csv`, source tables, and
`fig_alpha_sweep.pdf` use the updated readout.

Decision tree for H1:

1. Run `reliability_vs_reward_confirm.toml` first, because it confirms the
   corrected active-encounter analysis on the manuscript's current H1 surface.
2. If it passes the partial surprise-over-reward readout with tolerable active-
   encounter imbalance, keep H1 framed as model-fitness sensitivity and treat
   whole-run payoff as secondary.
3. If it fails mainly through reward/exposure coupling, classify the problem as
   analysis/task-design ambiguity and run the balanced graded reliability spine
   before adding seeds.
4. If the normal graded spine remains reward-coupled, run the reward-matched
   graded spine. It keeps the graded investment task but sets the multiplier to
   zero so own payoff is independent of partner action at each investment level.
5. If the reward-matched graded spine still cannot separate predictive
   reliability from reward or exposure, run the strict reward-neutral
   diagnostic.
6. Treat H1 as a model-level failure only if the strict reward-neutral
   diagnostic also fails to produce a precision-surprise association. A pass on
   reward-neutral H1 after a graded-spine failure means the earlier failure was
   caused by task or analysis confounding, not the core affective precision
   mechanism.

On June 2, the benchmark trust backend was moved out of
`tasks.trust.evaluation` into `benchmarks.trust_backend`, leaving task-local
evaluation to hold only baseline agents. The import-boundary guard now checks
that `tasks/` does not import `experiments`, `analysis`, or `benchmarks`,
preserving the intended `scripts -> experiments -> tasks -> pymdp` direction.

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
- **Conditions**: default α (3.0), low α (0.1), high α (8.0), no-affect baseline
- **Seeds**: 20 per condition
- **Outputs**: `results/exp_d/`, figures → `docs/paper/manuscript/figures/fig_mixed_volatility.pdf`
- **Metrics**: `discrimination_index`, `concentration_toward_P0`, per-partner beta
  trajectories, `false_positive_rate` (rolling rate where stable-P0 engagement
  drops more than 15% below its early baseline)
- **Manuscript target**: Section 3.6.4 placeholders

### After Exp A-D Recovery Complete

1. Confirm finality before reading metric values: the tmux/Mango process has
   ended, `results/exp_abcd_recovery_20260603_logs/run.log` contains
   `RECOVERY_DONE`, and `results/exp_a/` through `results/exp_d/` each contain
   final `results.csv`, `metrics.csv`, `manifest.json`, and `README.md`.
2. Confirm generic analysis directories exist for Exp A-D where applicable:
   `results/exp_*/analysis/`.
3. Fill `\resultp{...}` placeholders in `sections/03_results.tex` Section 3.6
   only after finality is established and the metric directions are checked
   against the planned readouts.
4. Update `docs/results/current.md` with phenotype findings only after asking
   the user before interpretation narrative updates.
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
- In the strict reward-neutral diagnostic, expect `reward_proxy_constant =
  True`; this means reward has no variance by design, so the partial dominance
  readout compares precision-surprise association against zero reward
  association rather than an undefined payoff correlation.
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

- If the normal graded spine still cannot separate reward/exposure from
  predictive reliability, run the reward-matched graded spine:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_spine_graded_reward_matched_diagnostic.toml \
  --output-dir results \
  --batch-name log_surprisal_h1_graded_reward_matched_diagnostic_YYYYMMDD \
  --workers 1
```

- If the reward-matched graded spine still cannot separate reward/exposure from
  predictive reliability, run the strict reward-neutral diagnostic:

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
