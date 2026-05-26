# Figure Plan

Use generated composite figures from current source tables where possible.
Regenerate the current paper panels with:

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
  -> payoff, reallocation, or misdeployment
```

Must show:

- one official `pymdp.Agent` per partner;
- hidden factors `type x stance x own_action`;
- observations `partner action` and `payoff`;
- external beta tracker outside the POMDP;
- tracked-only lesion where beta updates but gamma is decoupled.

## Main Figure 2: Open-Regime Deployment And Social Choice

Current asset: `figures/fig_deployment_social_summary.png`

Primary numbers:

- Affect payoff `1884.6`, entropy `7.94`.
- Lesioned/no-affect payoff `1859.4`, entropy `8.80`.
- Belief readouts remain similar or slightly favor lesion.

Caption claim: In the open graded regime, affective precision changes policy
deployment and payoff without improving belief accuracy; partner-selection
rates also move before whole-run payoff separates.

## Main Figure 3: Model Fitness Versus Reward

Draft asset: `figures/fig_model_fitness_beta_reward_divergence.png`

Source tables:

- `source_tables/h1_evidence_effect_summary.csv`
- `source_tables/h1_model_fitness_correlation_summary.csv`

Primary numbers:

- `|corr(precision, surprise)| = 0.701`
- `|corr(precision, payoff)| = 0.419`
- reliability-over-reward effect `+0.096`, CI `[0.027, 0.164]`
- no payoff advantage for affect: `534.6` versus `542.1`

Caption claim: Precision follows predictive reliability more strongly than
realized payoff, consistent with model fitness rather than cached value.

## Main Figure 4: Betrayal Boundary Condition

Draft assets:

- `figures/fig_betrayal_confirm_cumulative_payoff.png`
- `figures/fig_betrayal_signal_trajectories.png`

Source tables:

- `source_tables/h3_evidence_effect_summary.csv`
- `source_tables/h3_betrayal_reallocation_summary.csv`
- `source_tables/h3_betrayal_misdeployment_summary.csv`

Primary numbers:

- Affect payoff `1136.1` versus no-affect/lesion `1172.1`, `p = 0.0169`.
- Affect entropy `8.38` versus no-affect `8.74`.
- Affect reencounters switched partner less often (`4.4` versus `6.1`) but does
  not improve payoff conditional on return (`8.76` versus `8.91`).

Caption claim: Abrupt betrayal reveals an active but risky precision channel:
policy sharpening is not equivalent to safer recovery.

## Main Figure 5: Shock Shape And Sensitivity

Current asset: `figures/fig_shock_shape_summary.png`

Source tables:

- `source_tables/h3_abrupt_sensitivity_final_round_summary.csv`
- `source_tables/h3_abrupt_sensitivity_pairwise_payoff_tests.csv`
- `source_tables/h3_gradual_sensitivity_final_round_summary.csv`
- `source_tables/h3_gradual_sensitivity_pairwise_payoff_tests.csv`

Primary numbers:

- Abrupt default affect: `1140.4` versus no-affect `1153.6`, `p = 0.370`.
- Abrupt combined caution: `1115.0` versus no-affect, `p = 0.003`.
- Gradual default affect: `1147.6` versus no-affect `1148.9`, `p = 0.906`.
- Gradual combined caution: `1118.3` versus no-affect, `p = 0.005`.

Caption claim: Generic caution does not rescue abrupt betrayal; gradual shock
mostly removes the default affect payoff penalty.

## Main Figure 6: Perturbation Dynamics

Current asset: `figures/fig_phenotype_dynamics_summary.png`

Source tables:

- `source_tables/h5_clinical_dynamics_phenotype_validation_summary.csv`
- `source_tables/h5_clinical_betrayal_phenotype_validation_summary.csv`

Use as a bounded computational phenotyping result. The caption must say
"computational perturbations", not "clinical validation".
