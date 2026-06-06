# Figure Plan

The current source tables and figure assets are historical bounded-error
carryover unless explicitly regenerated from
`results/log_surprisal_spine_smoke_postfix_20260528/`. Do not use the old
panels as final current-evidence figures.

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
  -> payoff, reallocation, or misdeployment
```

Must show:

- **focal agent only** runs official `pymdp.Agent`; partners are scripted
  parameterized policies (same type×stance tables in world and likelihood);
- one official `pymdp.Agent` per tracked partner;
- hidden factors `type x stance x own_action`;
- observations `partner action` and `payoff`;
- external beta tracker outside the POMDP;
- tracked-only lesion where beta updates but gamma is decoupled.

## Main Figure 2: Model Fitness (H3 Focal-Switch Locality Probe)

Source table: `source_tables/h3_locality_probe_summary.csv` (manuscript-aligned;
correlations from postfix H3 smoke, payoffs from
`postfix_smoke_20260528/h3_final_round_summary.csv`).

Do **not** use `h1_evidence_effect_summary.csv` or
`h1_model_fitness_correlation_summary.csv` for this panel; those reflect a
different experiment (H1 reliability-vs-reward).

Output asset: `figures/fig_model_fitness_beta_reward_divergence.pdf`

Manuscript numbers (Section 3.1):

- Local beta: `|corr(precision, surprise)| = 0.943`, payoff `0.110`.
- Shared/global beta: surprise `0.149`, payoff `0.043`.
- Payoff: local `946.8`, global `976.2`, no-affect `950.7`.

## Main Figure 3: Open-Regime Deployment Dissociation

Source table: `source_tables/h2_deployment_dissociation_summary.csv`
(manuscript-aligned variant ids: `affect`, `no_affect`, `tracked_only`).

Output asset: `figures/fig_deployment_social_summary.pdf`

Manuscript numbers (Section 3.3; `postfix_smoke_20260528/h2` + `h0`):

- Affect: payoff `1851.3`, entropy `8.6`.
- No-affect: payoff `1864.2`, entropy `8.8`.
- Tracked-only: payoff `1864.2`, entropy `8.8`.

Do not claim open-regime payoff improvement from this smoke batch.

## Main Figure 4: Betrayal Boundary Condition

Source table: `source_tables/h5_evidence_effect_summary.csv` (built from
`postfix_smoke_20260528/h5_*` summaries). Do **not** use
`h3_evidence_effect_summary.csv`; that file reflects the pre-fix failure
direction (affect payoff below no-affect).

Output asset:

- `figures/fig_betrayal_boundary_summary.pdf`

Current smoke numbers (3 seeds):

- Affect payoff `1322.3`.
- No-affect / lesioned payoff `1225.0`.
- Affect entropy `7.47` versus no-affect `8.68`.
- Affect joint accuracy `0.319` versus no-affect `0.425`.

Caption claim: partner-local affect achieves higher payoff with lower joint
accuracy, consistent with portfolio reallocation rather than superior inference
about the changed partner. Replace three-seed smoke before submission.

## Main Figure 5: Shock Shape And Sensitivity

Current asset: historical carryover. Shock-shape sensitivity has not yet been
rerun under the current log-surprisal spine.

Source tables:

- `source_tables/h3_abrupt_sensitivity_final_round_summary.csv`
- `source_tables/h3_abrupt_sensitivity_pairwise_payoff_tests.csv`
- `source_tables/h3_gradual_sensitivity_final_round_summary.csv`
- `source_tables/h3_gradual_sensitivity_pairwise_payoff_tests.csv`

Historical bounded-error numbers:

- Abrupt default affect: `1140.4` versus no-affect `1153.6`, `p = 0.370`.
- Abrupt combined caution: `1115.0` versus no-affect, `p = 0.003`.
- Gradual default affect: `1147.6` versus no-affect `1148.9`, `p = 0.906`.
- Gradual combined caution: `1118.3` versus no-affect, `p = 0.005`.

Caption claim: Hold until the abrupt/gradual sensitivity sweep is rerun under
log-surprisal.

## Main Figure 6: Perturbation Dynamics

Current asset: stale carryover; regenerate before submission.

Source tables:

- `source_tables/h5_clinical_dynamics_phenotype_validation_summary.csv`
- `source_tables/h5_clinical_betrayal_phenotype_validation_summary.csv`

Current smoke beta ranges: alexithymia-like `0.180`, affect `1.126`,
borderline-like `1.412`, depression-like `1.464`.

Use as a bounded computational phenotyping result only. The caption must say
"computational perturbations", not "clinical validation".
