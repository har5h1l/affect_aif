# Figures And Tables

This is the recommended paper artifact plan. Use compact figures from reviewed
paper source tables rather than raw row-level dumps.

## Main Figures

### Figure 1: Model Schematic

Show the mechanism chain:

```text
partner prediction reliability
  -> partner-specific precision_k
  -> policy posterior shift
  -> action / partner choice
  -> payoff, reallocation, or boundary-condition effects
```

Include the architectural split:

- focal agent: partner-local `pymdp.Agent` over `type x stance x own_action`;
- environment: scripted parameterized partners (cooperation-table sampling);
- external beta tracker on focal side only;
- beta-to-gamma modulation;
- tracked-only lesion.

Source docs: `docs/theory/pomdp_spec.md`, `docs/design/implementation.md`.

### Figure 2: Model Fitness / Locality

Show partner-local precision-surprise versus precision-payoff association and
the shared-beta attenuation from the final H1 confirmation.

Primary source:

- `docs/paper/manuscript/source_tables/h1_model_fitness_confirm/`

### Figure 3: Open-Regime Deployment

Compare affect, no-affect, and tracked-only variants in the graded-choice/open
regime:

- total payoff;
- mean policy entropy;
- belief accuracy or joint accuracy.

Primary source:

- `docs/paper/manuscript/source_tables/h2_deployment_dissociation_summary.csv`

### Figure 4: Betrayal Boundary

Use the 30-seed H5 confirmation source table, not the three-seed smoke table.

Primary source:

- `docs/paper/manuscript/source_tables/h5_evidence_effect_summary.csv`

Current caption claim: lower policy entropy and higher joint accuracy under
partner-local affect, with small/uncertain payoff advantage. Do not describe
the confirmation as a payoff--accuracy tradeoff.

### Figure 5: Perturbation Dynamics

Use beta range, payoff, and entropy for bounded computational perturbations.

Primary sources:

- `docs/paper/manuscript/source_tables/h6_perturbation_dynamics_summary.csv`
- `docs/paper/manuscript/source_tables/h6_perturbation_betrayal_summary.csv`

### Figure 6: Phenotype Program

Use reviewed Exp A-D source tables:

- `docs/paper/manuscript/source_tables/exp_a_alpha_sweep/metrics.csv`
- `docs/paper/manuscript/source_tables/exp_b_prior_factorial/metrics.csv`
- `docs/paper/manuscript/source_tables/exp_c_forgiveness/metrics.csv`
- `docs/paper/manuscript/source_tables/exp_d_mixed_volatility/metrics.csv`

Caption language should emphasize non-monotonic profiles, not clinical
validation or broad payoff improvement.

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

Use `docs/paper/notes/claims_and_evidence.md`. This table is useful for review
and for keeping the discussion honest.
