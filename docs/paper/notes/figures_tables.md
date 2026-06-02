# Figures And Tables

This is the recommended paper artifact plan. Use compact figures from current
analysis outputs rather than raw row-level dumps.

## Main Figures

### Figure 1: Model Schematic

Show the mechanism chain:

```text
partner prediction reliability
  -> partner-specific precision_k
  -> policy posterior shift
  -> action / partner choice
  -> payoff, reallocation, or misdeployment
```

Include the architectural split:

- partner-local `pymdp.Agent` over `type x stance x own_action`;
- external beta tracker;
- beta-to-gamma modulation;
- tracked-only lesion.

Source docs: `docs/theory/pomdp_spec.md`, `docs/design/implementation.md`.

### Figure 2: H0/H2 Open-Regime Deployment

Compare affect, no-affect, and lesioned variants in the graded-choice/open
regime:

- total payoff;
- mean policy entropy;
- belief accuracy or joint accuracy.

Source artifacts:

- `results/confirm_h0_h1_h2_h4_20260518/h0/graded_choice/analysis/final_round_summary.csv`
- `results/confirm_h0_h1_h2_h4_20260518/h2/lesion_open_regime/analysis/deployment_dissociation_summary.csv`

### Figure 3: H1 Model Fitness

Show precision-surprise versus precision-reward association as a post-fix
target diagnostic, not as final evidence.

Primary source:

- `docs/paper/manuscript/source_tables/postfix_smoke_20260528/h1_model_fitness_correlation_summary.csv`
- `docs/paper/manuscript/source_tables/postfix_smoke_20260528/h1_evidence_effect_summary.csv`

Current corrected post-fix smoke: local affect has
`|corr(precision, surprise)| = 0.976` and
`|corr(precision, payoff)| = 0.721`; the partial readout controlling active
payoff and encounter count is `0.951` versus `0.172`. Treat this as a
confirmation target, not final manuscript evidence.

### Figure 4: H5 Betrayal Anchor

Show post-fix abrupt betrayal effects:

- total payoff;
- policy entropy;
- reencounters/return behavior;
- misdeployment rates.

Primary source:

- `docs/paper/manuscript/source_tables/postfix_smoke_20260528/h5_final_round_summary.csv`
- `docs/paper/manuscript/source_tables/postfix_smoke_20260528/h5_betrayal_reallocation_summary.csv`
- `docs/paper/manuscript/source_tables/postfix_smoke_20260528/h5_betrayal_misdeployment_summary.csv`

### Figure 5: H3 Shock-Shape / Sensitivity

Compare abrupt and gradual betrayal:

- no-affect/lesioned baseline;
- default affect;
- cautious variants.

Primary source:

- `results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/analysis/final_round_summary.csv`
- `results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/analysis/final_round_summary.csv`
- paired `pairwise_payoff_tests.csv` and `betrayal_reallocation_summary.csv`

## Secondary Figures

### H4 Social Choice

Use partner-selection rate and entropy to show behavior moves even when payoff
is flat.

Source:

- `results/confirm_h0_h1_h2_h4_20260518/h4/partner_choice/analysis/partner_choice_summary.csv`

### H5 Perturbation Dynamics

Use beta range, beta autocorrelation, action-flip rate, and selection entropy.
Keep in supplement unless the manuscript centers perturbation phenotypes.

Source:

- `results/updated_h0_h5_20260517_w2/h5/clinical_dynamics/analysis/phenotype_validation_summary.csv`
- `results/updated_h0_h5_20260517_w2/h5/clinical_betrayal/analysis/phenotype_validation_summary.csv`
- `results/updated_h0_h5_20260518_remainder/h5/affect_sensitivity/analysis/affective_movement_summary.csv`

## Main Tables

### Table 1: Hypothesis Scorecard

Use `docs/results/current.md` as the source of truth. Columns:

- card;
- mechanism claim;
- primary readout;
- current status;
- interpretation.

### Table 2: Experiment Specs

Use `docs/experiments/manifest.md` and config paths. Columns:

- hypothesis;
- config path;
- payoff mode;
- assignment mode;
- variants;
- replications.

### Table 3: Claims And Non-Claims

Use `docs/paper/claims_and_evidence.md`. This table is useful for review and
for keeping the discussion honest.
