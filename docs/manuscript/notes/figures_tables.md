# Figures And Tables

Headline numbers and include/exclude rules: `docs/results/current.md`.

Recommended paper output plan. Use compact figures from reviewed paper source
tables rather than raw row-level dumps.

Regenerate paper panels with:

```bash
python scripts/analysis/make_paper_figures.py
```

The script reads `docs/manuscript/source_tables/` and writes PNG/PDF
figures to `docs/manuscript/figures/`.

## Main Figures

### Figure 1: Predictability-Over-Value Locality Probe

Source tables:

- `docs/manuscript/source_tables/h1_model_fitness_confirm/model_fitness_correlation_summary.csv`
- `docs/manuscript/source_tables/h1_model_fitness_confirm/final_round_summary.csv`

Output asset:
`docs/manuscript/figures/fig_model_fitness_beta_reward_divergence.pdf`

Manuscript numbers:

- Partner-local raw correlations: precision--surprisal `-0.949`,
  precision--payoff `-0.748`.
- Partner-local active-encounter partial correlations: precision--surprisal
  `-0.882`, precision--payoff `0.130`.
- Shared-$\beta$ active-encounter partial correlations: precision--surprisal
  `-0.380`, precision--payoff `0.049`.
- Payoff panel: local `483.5`, shared `517.6`, no-affect `542.1`.

Caption/readout must say the payoff panel reports payoff over the same
locality-probe analysis window, not full-episode payoff.

### Figure 2: Open-Regime Deployment Contrast

Source table:
`docs/manuscript/source_tables/h2_deployment_contrast_summary.csv`.

Output asset: `docs/manuscript/figures/fig_deployment_social_summary.pdf`

Manuscript numbers:

- Affect: payoff `1851.3`, entropy `8.59`.
- No-affect: payoff `1864.2`, entropy `8.79`.
- Tracked-only: payoff `1864.2`, entropy `8.79` (matches no-affect).

Do not claim open-regime payoff improvement from this batch.

### Partner-Choice Text Readout

Source table: `docs/manuscript/source_tables/h4_partner_choice_summary.csv`.
This is the graded paper partner-selection readout. Reviewer-control provenance
is retained outside the paper source-table set.

Manuscript numbers:

- Policy entropy: affect `3.99`, no-affect `4.83`.
- Cooperator selection: affect `36.6%`, no-affect `34.8%`.
- Exploiter selection: affect `13.8%`, no-affect `16.2%`.
- Total payoff: affect `393.6`, no-affect `393.2` (flat at this scale).

Frame as a small allocation shift consistent with sharper policy commitment,
not as cumulative-payoff separation.

### Figure 3: Betrayal Boundary Condition

Source table: `docs/manuscript/source_tables/h5_evidence_effect_summary.csv`
(regenerated from the 30-seed abrupt-betrayal confirmation).

Output asset: `docs/manuscript/figures/fig_betrayal_boundary_summary.pdf`

Current confirmation numbers (P0 stance switch at round 31):

- Affect entropy `8.36`; no-affect entropy `8.74`; interval for the difference
  is negative (`-0.62` to `-0.14`) --- lead panel.
- Affect joint accuracy `0.372`; no-affect joint accuracy `0.266`; interval for
  the difference is positive (`0.034` to `0.185`).
- Affect payoff `1185.9`; no-affect payoff `1172.1`; paired bootstrap interval
  crosses zero (`-25.2` to `53.2`).
- Figure support panel also plots post-switch P0 reencounters (affect higher
  than no-affect; CI `0.97` to `8.03`).

Caption claim: partner-local affect sharpens policy deployment under abrupt
change; joint accuracy improves; payoff remains uncertain. Frame uncertain
payoff as expected for a calibration mechanism, not a power failure.
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
