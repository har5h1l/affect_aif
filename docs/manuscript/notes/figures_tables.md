# Figures And Tables

Recommended paper artifact plan. Use compact figures from reviewed paper source
tables rather than raw row-level dumps.

Regenerate paper panels with:

```bash
python scripts/analysis/make_paper_figures.py
```

The script reads `docs/manuscript/source_tables/` and writes PNG/PDF
figures to `docs/manuscript/figures/`.

## Main Figures

### Figure 1: Model Schematic

Status: create manually for final paper.

Show the mechanism chain:

```text
partner action prediction error
  -> partner-specific beta_k / precision_k
  -> partner-local gamma_k = gamma_base / E[beta_k]
  -> pymdp policy posterior shift
  -> action or partner-choice deployment
  -> payoff, reallocation, or boundary-condition effects
```

Must show:

- focal agent only runs official `pymdp.Agent`; partners are scripted
  parameterized policies;
- one official `pymdp.Agent` per tracked partner;
- hidden factors `type x stance x own_action`;
- observations `partner action` and `payoff`;
- external beta tracker outside the POMDP;
- tracked-only lesion where beta updates but gamma is decoupled.

Source docs: `docs/overview/pomdp.md` and
`docs/overview/affective_precision.md`.

### Figure 2: Model Fitness / Locality

Source table: `docs/manuscript/source_tables/h1_model_fitness_confirm/`.

Output asset: `docs/manuscript/figures/fig_model_fitness_beta_reward_divergence.pdf`

Manuscript numbers:

- Local beta active-encounter partials: surprise `0.882`, payoff `0.130`.
- Shared/global beta partials: surprise `0.380`, payoff `0.049`.
- Payoff: local `483.5`, global `517.6`, no-affect `542.1`.

H1 confirmation has replaced the older focal-switch smoke values for the
manuscript panel.

### Figure 3: Open-Regime Deployment Dissociation

Source table:
`docs/manuscript/source_tables/h2_deployment_dissociation_summary.csv`.

Output asset: `docs/manuscript/figures/fig_deployment_social_summary.pdf`

Manuscript numbers:

- Affect: payoff `1851.3`, entropy `8.59`.
- No-affect: payoff `1864.2`, entropy `8.79`.
- Tracked-only: payoff `1864.2`, entropy `8.79` (matches no-affect).

Do not claim open-regime payoff improvement from this diagnostic batch.

### Figure 3b: Partner-Choice Sharpening (H4)

Source table:
`docs/manuscript/source_tables/h4_partner_choice_summary.csv` (5 seeds;
30-seed confirmation per appendix protocols not yet in manuscript).

Manuscript numbers:

- Policy entropy: affect `3.99`, no-affect `4.83`.
- Cooperator selection: affect `36.6%`, no-affect `34.8%`.
- Exploiter selection: affect `13.8%`, no-affect `16.2%`.
- Total payoff: affect `393.6`, no-affect `393.2` (flat at this scale).

Frame as directional allocation shift toward predictable partners without
cumulative-payoff separation, consistent with the Section 3.1 dissociation.

### Figure 4: Betrayal Boundary Condition

Source table: `docs/manuscript/source_tables/h5_evidence_effect_summary.csv`
(regenerated from the 30-seed H5 confirmation).

Output asset: `docs/manuscript/figures/fig_betrayal_boundary_summary.pdf`

Current confirmation numbers (P0 stance switch at round 31):

- Affect entropy `8.36`; no-affect entropy `8.74`; interval for the difference
  is negative (`-0.62` to `-0.14`) --- lead panel.
- Affect joint accuracy `0.372`; no-affect joint accuracy `0.266`; interval for
  the difference is positive (`0.034` to `0.185`).
- Affect payoff `1185.9`; no-affect payoff `1172.1`; paired bootstrap interval
  crosses zero (`-25.2` to `53.2`).
- Figure diagnostic panel also plots post-switch P0 reencounters (affect higher
  than no-affect; CI `0.97` to `8.03`).

Caption claim: partner-local affect sharpens policy deployment under abrupt
change; joint accuracy improves; payoff is positive but uncertain. Frame
uncertain payoff as expected for a calibration mechanism, not a power failure.
Do not describe H5 as a payoff--accuracy tradeoff.

### Figure 5: Precision-Dynamics Perturbations

Source tables:

- `docs/manuscript/source_tables/h6_perturbation_dynamics_summary.csv`
- `docs/manuscript/source_tables/h6_perturbation_betrayal_summary.csv`

Output asset: `docs/manuscript/figures/fig_phenotype_dynamics_summary.pdf`

Use as bounded computational phenotyping evidence only. Caption must say
"computational profiles" or "computational perturbations", not clinical
validation.

### Figure 6: Phenotype Program

Source tables:

- `docs/manuscript/source_tables/exp_a_alpha_sweep/metrics.csv`
- `docs/manuscript/source_tables/exp_b_prior_factorial/metrics.csv`
- `docs/manuscript/source_tables/exp_c_forgiveness/metrics.csv`
- `docs/manuscript/source_tables/exp_d_mixed_volatility/metrics.csv`

Output assets:

- `docs/manuscript/figures/fig_alpha_sweep.pdf`
- `docs/manuscript/figures/fig_phenotype_quadrants.pdf`
- `docs/manuscript/figures/fig_forgiveness.pdf`
- `docs/manuscript/figures/fig_mixed_volatility.pdf`

Use the non-monotonic profile interpretation (§3.6 rewrite):

- open with four experiments / single-axis negative;
- lead $\alpha$ sweep with non-monotonic payoff, then $\beta_k$ amplitude;
- four gain-prior profiles with equal interpretive weight;
- Exp C: reengagement vs restored confidence (round 121 reversion);
- Exp D: payoff--discrimination dissociation at high gain;
- cite `Figure~\ref{fig:mixed_volatility}` in main text (not hardcoded figure number);
- human-data disclaimer in Discussion §4, not §3.6 opener.

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
