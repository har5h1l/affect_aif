# Config To Result Map

Every maintained TOML config under `configs/` has a documented result destination.
Tracked public summaries live under `results/paper/`, `results/diagnostics/`, and
`results/future/`. Full per-round `results.csv` files are gitignored under each
card's `raw/` subtree when materialized locally.

When you run a config through `scripts/experiment/run.py` **without**
`--output-dir` or `--batch-name`, the runner uses the **canonical family layout**
implemented in `experiments/trust/output_layout.py`:

| Config family | Default write root |
|---|---|
| `configs/paper/` | `results/paper/<config-stem>/raw/` |
| `configs/diagnostics/` | `results/diagnostics/...` (promoted card or `results/diagnostics/raw/...`) |
| `configs/future/` | `results/future/<config-stem>/raw/` |
| `configs/demo/` | `outputs/demo/<config-stem>/<hypothesis>/<experiment>/` |

Paper suite configs with multiple `[[experiments]]` blocks write under
`results/paper/<config-stem>/raw/<experiment_id>/`.

Legacy batch layout is still available when you pass explicit paths:

```text
--output-dir <root> --batch-name <batch>
  -> <root>/<batch>/<hypothesis_id>/<experiment_id>/results.csv
```

The **canonical raw path** column below matches the default runner layout for
each config.

## Paper Configs

| Config | Result card | Canonical raw path |
|---|---|---|
| `configs/paper/01_predictability_value.toml` | `results/paper/01_predictability_value/` | `results/paper/01_predictability_value/raw/results.csv` |
| `configs/paper/02_deployment_ablation.toml` | `results/paper/02_deployment_ablation/` | `results/paper/02_deployment_ablation/raw/results.csv` |
| `configs/paper/03_partner_selection.toml` | `results/paper/03_partner_selection/` | `results/paper/03_partner_selection/raw/results.csv` |
| `configs/paper/04_betrayal_adaptation.toml` | `results/paper/04_betrayal_adaptation/` | `results/paper/04_betrayal_adaptation/raw/results.csv` |
| `configs/paper/05a_alpha_sweep.toml` | `results/paper/05a_alpha_sweep/` | `results/paper/05a_alpha_sweep/raw/open_graded/results.csv`; `results/paper/05a_alpha_sweep/raw/betrayal/results.csv` |
| `configs/paper/05b_prior_factorial.toml` | `results/paper/05b_prior_factorial/` | `results/paper/05b_prior_factorial/raw/open_graded/results.csv`; `results/paper/05b_prior_factorial/raw/betrayal/results.csv`; `results/paper/05b_prior_factorial/raw/partner_choice/results.csv` |
| `configs/paper/05c_forgiveness.toml` | `results/paper/05c_forgiveness/` | `results/paper/05c_forgiveness/raw/results.csv` |

Suite index: `results/paper/manifest.json`.

## Future Configs

| Config | Result card | Canonical raw path |
|---|---|---|
| `configs/future/mixed_volatility.toml` | `results/future/mixed_volatility/` | `results/future/mixed_volatility/raw/results.csv` |

## Demo Configs

Demo configs mirror the numbered paper suite at reduced scale. They do not have
tracked result cards; default outputs are ephemeral under `outputs/demo/`.

| Config | Paper analogue | On-run path pattern |
|---|---|---|
| `configs/demo/01_predictability_value.toml` | `configs/paper/01_predictability_value.toml` | `outputs/demo/01_predictability_value/predictability_value_demo/predictability_value_demo/results.csv` |
| `configs/demo/02_deployment_ablation.toml` | `configs/paper/02_deployment_ablation.toml` | `outputs/demo/02_deployment_ablation/deployment_ablation_demo/deployment_ablation_demo/results.csv` |
| `configs/demo/03_partner_selection.toml` | `configs/paper/03_partner_selection.toml` | `outputs/demo/03_partner_selection/partner_selection_demo/partner_selection_demo/results.csv` |
| `configs/demo/04_betrayal_adaptation.toml` | `configs/paper/04_betrayal_adaptation.toml` | `outputs/demo/04_betrayal_adaptation/betrayal_adaptation_demo/betrayal_adaptation_demo/results.csv` |
| `configs/demo/05a_alpha_sweep.toml` | `configs/paper/05a_alpha_sweep.toml` | `outputs/demo/05a_alpha_sweep/exp_a_demo/{experiment_id}/results.csv` |
| `configs/demo/05b_prior_factorial.toml` | `configs/paper/05b_prior_factorial.toml` | `outputs/demo/05b_prior_factorial/exp_b_demo/{experiment_id}/results.csv` |
| `configs/demo/05c_forgiveness.toml` | `configs/paper/05c_forgiveness.toml` | `outputs/demo/05c_forgiveness/exp_c_demo/forgiveness/results.csv` |

## Diagnostic Configs With Promoted Result Cards

| Config | Result card | Canonical raw path |
|---|---|---|
| `configs/diagnostics/h0_policy_openness/graded_choice.toml` | `results/diagnostics/policy_openness/` | `results/diagnostics/policy_openness/raw/h0/graded_choice/results.csv` |
| `configs/diagnostics/h2_deployment/lesion_open_regime.toml` | `results/diagnostics/deployment/` | `results/diagnostics/deployment/raw/h2/lesion_open_regime/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_locality_probe.toml` | `results/diagnostics/locality/` | `results/diagnostics/locality/raw/h3/global_beta_locality_probe/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_focal_switch_probe.toml` | `results/diagnostics/locality/` | `results/diagnostics/locality/raw/h3/global_beta_focal_switch_probe/results.csv` |
| `configs/diagnostics/h1_model_fitness/reliability_vs_reward_confirm.toml` | `results/diagnostics/model_fitness/` | `results/diagnostics/model_fitness/raw/h1/reliability_vs_reward_confirm/results.csv` |
| `configs/diagnostics/h4_social_allocation/partner_choice_confirm.toml` | `results/diagnostics/social_allocation/` | `results/diagnostics/social_allocation/raw/partner_choice_confirm_20260609/h4/partner_choice_confirm/results.csv` |

Interpretation for promoted diagnostic cards lives in `docs/results/diagnostics.md`.

## Other Diagnostic Configs

These configs are runnable reviewer or mechanism probes. They do not have
tracked compact summaries in git. Use the canonical raw path when you need to
retain outputs outside a one-off batch directory.

| Config | Canonical raw path |
|---|---|
| `configs/diagnostics/smoke/trust_smoke.toml` | `results/diagnostics/raw/smoke/smoke/results.csv` |
| `configs/diagnostics/h0_policy_openness/shallow_binary.toml` | `results/diagnostics/raw/h0/shallow_binary/results.csv` |
| `configs/diagnostics/h0_policy_openness/graded_choice_confirm.toml` | `results/diagnostics/raw/h0/graded_choice_confirm/results.csv` |
| `configs/diagnostics/h0_policy_openness/graded_betrayal.toml` | `results/diagnostics/raw/h0/graded_betrayal/results.csv` |
| `configs/diagnostics/h1_model_fitness/reliability_vs_reward.toml` | `results/diagnostics/raw/h1/reliability_vs_reward/results.csv` |
| `configs/diagnostics/h1_model_fitness/reliability_spine_graded_diagnostic.toml` | `results/diagnostics/raw/h1/reliability_spine_graded_diagnostic/results.csv` |
| `configs/diagnostics/h1_model_fitness/reliability_spine_graded_reward_matched_diagnostic.toml` | `results/diagnostics/raw/h1/reliability_spine_graded_reward_matched_diagnostic/results.csv` |
| `configs/diagnostics/h1_model_fitness/reliability_reward_neutral_diagnostic.toml` | `results/diagnostics/raw/h1/reliability_reward_neutral_diagnostic/results.csv` |
| `configs/diagnostics/h2_deployment/lesion_open_regime_confirm.toml` | `results/diagnostics/raw/h2/lesion_open_regime_confirm/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_smoke.toml` | `results/diagnostics/raw/h3/global_beta_smoke/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_betrayal_probe.toml` | `results/diagnostics/raw/h3/global_beta_betrayal_probe/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_deployment_probe.toml` | `results/diagnostics/raw/h3/global_beta_deployment_probe/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_model_fitness_probe.toml` | `results/diagnostics/raw/h3/global_beta_model_fitness_probe/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_partner_choice_probe.toml` | `results/diagnostics/raw/h3/global_beta_partner_choice_probe/results.csv` |
| `configs/diagnostics/h3_locality/lesion_family_probe.toml` | `results/diagnostics/raw/h3/lesion_family_probe/results.csv` |
| `configs/diagnostics/h4_social_allocation/partner_choice.toml` | `results/diagnostics/raw/h4/partner_choice/results.csv` |
| `configs/diagnostics/h5_timescale_volatility/betrayal_choice.toml` | `results/diagnostics/raw/h5/betrayal_choice/results.csv` |
| `configs/diagnostics/h5_timescale_volatility/betrayal_reallocation.toml` | `results/diagnostics/raw/h5/betrayal_reallocation/results.csv` |
| `configs/diagnostics/h5_timescale_volatility/betrayal_precision_sensitivity.toml` | `results/diagnostics/raw/h5/betrayal_precision_sensitivity/results.csv` |
| `configs/diagnostics/h5_timescale_volatility/betrayal_precision_sensitivity_gradual.toml` | `results/diagnostics/raw/h5/betrayal_precision_sensitivity_gradual/results.csv` |
| `configs/diagnostics/h6_perturbation/affect_sensitivity.toml` | `results/diagnostics/raw/h6/affect_sensitivity/results.csv` |
| `configs/diagnostics/h6_perturbation/perturbation_betrayal.toml` | `results/diagnostics/raw/h6/perturbation_betrayal/results.csv` |
| `configs/diagnostics/h6_perturbation/perturbation_dynamics.toml` | `results/diagnostics/raw/h6/perturbation_dynamics/results.csv` |

H6 perturbation outputs also feed appendix figure builders documented in
`docs/results/provenance.md`.

## Hygiene Rules

- Do not keep local result trees whose experiment ids do not match a maintained
  config. Legacy probes such as `clinical_dynamics` and `log_surprise_*_smoke`
  were removed with their configs.
- Do not add a suite-level rollup such as `results/paper/metrics.csv`; profile
  metrics belong under `results/paper/05a_alpha_sweep/`,
  `results/paper/05b_prior_factorial/`, and `results/paper/05c_forgiveness/`.
- Promoted cards own tracked summaries (`summary.csv`, `source_tables/*.csv`,
  or section `metrics.csv`) plus `manifest.json` and `README.md`.
