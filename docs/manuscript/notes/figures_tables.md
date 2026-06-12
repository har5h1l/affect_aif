# Figures And Tables

Headline numbers and include/exclude rules: `docs/results/current.md`.

Recommended paper output plan. Use compact figures from reviewed paper source
tables rather than raw row-level dumps.

Regenerate paper panels with:

```bash
python scripts/analysis/make_paper_figures.py --refresh-source-tables
```

The script refreshes the compact Figure 2 and Figure 3 source tables from
`results/paper/`, then reads `docs/manuscript/source_tables/` and writes
PNG/PDF figures to `docs/manuscript/figures/`.

## Main Figures

### Figure 1: Predictability-Over-Value Locality Probe

Source tables:

- `docs/manuscript/source_tables/h1_model_fitness_confirm/model_fitness_correlation_summary.csv`
- `docs/manuscript/source_tables/h1_model_fitness_confirm/final_round_summary.csv`

Output asset:
`docs/manuscript/figures/fig_model_fitness_beta_reward_divergence.pdf`

Manuscript numbers:

- Partner-local raw correlations: precision--surprisal `-0.945`,
  precision--payoff `0.367`.
- Partner-local active-encounter partial correlations: precision--surprisal
  `-0.940`, precision--payoff `0.023`.
- Shared-$\beta$ active-encounter partial correlations: precision--surprisal
  `-0.496`, precision--payoff `0.535`.
- Payoff panel: local `1977.2`, shared `1973.4`, no-affect `1905.9`.

Caption/readout must say the payoff panel reports payoff in the same
predictability-value analysis run. Do not claim this run lacks a payoff
advantage for local beta; instead, state that payoff does not identify the
precision signal because the strong partner-local precision--surprisal
relationship weakens under shared beta despite similar payoff.

### Figure 2: Open-Regime Deployment Contrast

Source tables:

- `docs/manuscript/source_tables/h2_deployment_pathway_summary.csv`
- `docs/manuscript/source_tables/h2_deployment_contrast_summary.csv`
  (retained as the broader compact summary)

Output asset: `docs/manuscript/figures/fig_deployment_social_summary.pdf`

Manuscript numbers:

- Affect: beta range `1.34`, entropy delta vs tracked-only `-0.238`,
  payoff delta vs tracked-only `+2.1`.
- Tracked-only: beta range `1.34`, entropy delta `0.0`, payoff delta `0.0`.

Do not claim open-regime payoff improvement from this batch. The figure should
show beta tracking first, entropy deployment second, and payoff non-improvement
third.

### Partner-Choice Text Readout

Source table: `docs/manuscript/source_tables/h4_partner_choice_summary.csv`.
This is the graded paper partner-selection readout. Reviewer-control provenance
is retained outside the paper source-table set.

Manuscript numbers:

- Policy entropy: affect `8.60`, no-affect `8.83`.
- Selected-type allocation, affect vs no-affect: cooperator `25.3%` vs
  `29.2%`, exploiter `25.5%` vs `21.3%`, reciprocator `23.7%` vs `22.5%`,
  random `25.5%` vs `27.1%`.
- Total payoff: affect `1868.3`, no-affect `1866.2` (nearly matched at this scale).

Frame as a small allocation reorganisation consistent with sharper policy
commitment, not as a one-type preference or cumulative-payoff separation.

### Figure 3: Betrayal Boundary Condition

Source tables:

- `docs/manuscript/source_tables/h5_betrayal_timecourse_summary.csv`
- `docs/manuscript/source_tables/h5_evidence_effect_summary.csv`
  (retained for headline effect-size prose)

Output asset: `docs/manuscript/figures/fig_betrayal_boundary_summary.pdf`

Current confirmation numbers (P0 stance switch at round 31):

- Affect entropy `8.36`; no-affect entropy `8.74`; interval for the difference
  is negative (`-0.63` to `-0.16`) --- lead panel.
- Affect joint accuracy `0.372`; no-affect joint accuracy `0.266`; interval for
  the difference is positive (`0.024` to `0.188`).
- Affect payoff `1185.9`; no-affect payoff `1172.1`; paired bootstrap interval
  crosses zero (`-21.6` to `52.0`).
- Time-course figure plots betrayed-partner/P0 selection, betrayed-partner
  inverse precision \(E_q[\beta]\), and policy entropy around the round-31
  stance switch.

Caption claim: partner-local affect maintains lower policy entropy after
abrupt change, while tracked-only shows that beta dynamics can persist without
the same deployment effect. Joint accuracy improves and payoff remains
uncertain in the prose. Frame uncertain payoff as expected for a calibration
mechanism, not a power failure.
Do not describe the abrupt-betrayal result as a payoff--accuracy tradeoff.

### Figure 4: Precision-Dynamics Perturbations

Source tables:

- `docs/manuscript/source_tables/h6_perturbation_dynamics_summary.csv`
- `docs/manuscript/source_tables/h6_perturbation_betrayal_summary.csv`

Output asset: `docs/manuscript/figures/fig_phenotype_dynamics_summary.pdf`

Use as bounded computational phenotyping evidence only. Caption must say
"computational profiles" or "computational perturbations", not clinical
validation.

### Profile Program Tables/Figures

Source tables:

- `docs/manuscript/source_tables/alpha_sweep/metrics.csv`
- `docs/manuscript/source_tables/prior_factorial/metrics.csv`
- `docs/manuscript/source_tables/forgiveness/metrics.csv`

Output assets:

- `docs/manuscript/figures/fig_alpha_sweep.pdf`
- `docs/manuscript/figures/fig_phenotype_quadrants.pdf`
- `docs/manuscript/figures/fig_forgiveness.pdf`

Use the non-monotonic profile interpretation (§3.5 rewrite):

- open with three experiments / single-axis negative;
- lead $\alpha$ sweep with non-monotonic payoff, then $\beta_k$ amplitude;
- four gain-prior profiles with equal interpretive weight;
- forgiveness profile: reengagement vs restored confidence (round 121 reversion);
- heterogeneous-volatility analyses stay future-facing, not reported evidence;
- human-data disclaimer in Discussion §4, not §3.5 opener.

## Main Tables

### Table 1: Hypothesis Scorecard

Use `docs/results/current.md` as the source of truth. Columns:

- card;
- mechanism claim;
- primary readout;
- current status;
- interpretation.

### Table 2: Experiment Specs

Use `docs/experiments/paper.md`, `docs/experiments/configs.md`, and config
paths. Columns:

- hypothesis;
- config path;
- payoff mode;
- assignment mode;
- variants;
- replications.

Paper-facing subset: `docs/manuscript/notes/experiment_manifest.md`.

### Table 3: Claims And Non-Claims

Use `docs/manuscript/notes/claims_and_evidence.md`. Useful for review and for
keeping the discussion honest.
