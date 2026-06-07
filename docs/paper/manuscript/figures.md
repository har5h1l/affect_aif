# Figure Plan

Regenerate paper panels with:

```bash
python scripts/analysis/make_paper_figures.py
```

The script reads `docs/paper/manuscript/source_tables/` and writes PNG/PDF
figures to `docs/paper/manuscript/figures/`.

## Main Figure 1: Model Schematic

Status: create manually for final paper.

Content:

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

## Main Figure 2: Model Fitness / Locality

Source table: `source_tables/h1_model_fitness_confirm/`.

Output asset: `figures/fig_model_fitness_beta_reward_divergence.pdf`

Manuscript numbers:

- Local beta active-encounter partials: surprise `0.882`, payoff `0.130`.
- Shared/global beta partials: surprise `0.380`, payoff `0.049`.
- Payoff: local `483.5`, global `517.6`, no-affect `542.1`.

H1 confirmation has replaced the older focal-switch smoke values for the
manuscript panel.

## Main Figure 3: Open-Regime Deployment Dissociation

Source table: `source_tables/h2_deployment_dissociation_summary.csv`.

Output asset: `figures/fig_deployment_social_summary.pdf`

Manuscript numbers:

- Affect: payoff `1851.3`, entropy `8.6`.
- No-affect: payoff `1864.2`, entropy `8.8`.
- Tracked-only: payoff `1864.2`, entropy `8.8`.

Do not claim open-regime payoff improvement from this diagnostic batch.

## Main Figure 4: Betrayal Boundary Condition

Source table: `source_tables/h5_evidence_effect_summary.csv`, regenerated from
the 30-seed H5 confirmation.

Output asset: `figures/fig_betrayal_boundary_summary.pdf`

Current confirmation numbers:

- Affect payoff `1185.9`; no-affect payoff `1172.1`; paired bootstrap interval
  crosses zero.
- Affect entropy `8.36`; no-affect entropy `8.74`; interval for the difference
  is negative.
- Affect joint accuracy `0.372`; no-affect joint accuracy `0.266`; interval for
  the difference is positive.

Caption claim: partner-local affect sharpens policy deployment under abrupt
change and modestly improves behavioral readouts, but the payoff effect is
uncertain. Do not describe H5 as a payoff--accuracy tradeoff.

## Main Figure 5: Precision-Dynamics Perturbations

Source tables:

- `source_tables/h6_perturbation_dynamics_summary.csv`
- `source_tables/h6_perturbation_betrayal_summary.csv`

Output asset: `figures/fig_phenotype_dynamics_summary.pdf`

Use as bounded computational phenotyping evidence only. The caption must say
"computational profiles" or "computational perturbations", not clinical
validation.

## Main Figure 6: Phenotype Program

Source tables:

- `source_tables/exp_a_alpha_sweep/metrics.csv`
- `source_tables/exp_b_prior_factorial/metrics.csv`
- `source_tables/exp_c_forgiveness/metrics.csv`
- `source_tables/exp_d_mixed_volatility/metrics.csv`

Output assets:

- `figures/fig_alpha_sweep.pdf`
- `figures/fig_phenotype_quadrants.pdf`
- `figures/fig_forgiveness.pdf`
- `figures/fig_mixed_volatility.pdf`

Use the non-monotonic profile interpretation:

- higher alpha expands beta movement but does not monotonically improve payoff;
- Exp C forgiveness separates reengagement from restored model-fitness
  confidence;
- Exp D supports a boundary condition, not the older strong
  sensitivity-specificity claim.
