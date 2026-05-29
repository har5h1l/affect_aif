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

- one official `pymdp.Agent` per partner;
- hidden factors `type x stance x own_action`;
- observations `partner action` and `payoff`;
- external beta tracker outside the POMDP;
- tracked-only lesion where beta updates but gamma is decoupled.

## Main Figure 2: Open-Regime Deployment And Social Choice

Current asset: stale carryover; regenerate before submission.

Current smoke numbers:

- Affect payoff `1851.3`, entropy `8.59`.
- No-affect / lesioned payoff `1864.2`, entropy `8.79`.
- Global beta payoff `1851.3`, entropy `8.64`.
- Belief readouts do not support a local-affect payoff win at smoke scale.

Caption claim: In the open graded regime, affective precision changes policy
deployment, but the reduced log-surprisal smoke does not establish a local
affect payoff advantage.

## Main Figure 3: Model Fitness Versus Reward

Draft asset: stale carryover; regenerate before submission.

Source tables:

- `source_tables/postfix_smoke_20260528/h1_evidence_effect_summary.csv`
- `source_tables/postfix_smoke_20260528/h1_model_fitness_correlation_summary.csv`

Current smoke numbers:

- Local beta: `|corr(precision, surprise)| = 0.226`
- Local beta: `|corr(precision, payoff)| = 0.615`
- Global beta: `0.115` versus `0.103`
- no payoff advantage for affect: `492.7` versus `552.0`

Caption claim: The current post-fix H1 smoke does not yet establish the
surprise-over-reward model-fitness dissociation; treat this panel as a target
for confirmation/rework rather than final evidence.

## Main Figure 4: Betrayal Boundary Condition

Draft assets: stale carryover; regenerate before submission.

- `figures/fig_betrayal_confirm_cumulative_payoff.png`
- `figures/fig_betrayal_signal_trajectories.png`

Current smoke numbers:

- Affect payoff `1322.3`.
- No-affect / lesioned payoff `1225.0`.
- Global beta payoff `1216.2`.
- Affect entropy `7.47` versus no-affect / lesioned `8.68`.

Caption claim: under the corrected selector, abrupt betrayal is the strongest
candidate positive behavioral anchor, but the three-seed smoke must be replaced
before submission.

Source tables:

- `source_tables/h3_evidence_effect_summary.csv`
- `source_tables/h3_betrayal_reallocation_summary.csv`
- `source_tables/h3_betrayal_misdeployment_summary.csv`

Current smoke numbers:

- Affect payoff `1127.0` versus no-affect/lesion `1225.0`.
- Affect entropy `8.37` versus no-affect/lesion `8.68`.
- Affect joint accuracy `0.067` versus no-affect/lesion `0.425`.
- Affect reencounters the switched partner less often (`0.037` selection rate
  versus `0.322`) but appears to reallocate poorly.

Caption claim: Abrupt betrayal reveals an active but risky precision channel:
policy sharpening is not equivalent to safer recovery.

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
