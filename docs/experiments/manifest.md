# Experiment Manifest

This manifest maps maintained TOML experiment specs under `configs/` to the
canonical behavior-card spine in `docs/theory/hypotheses.md`. Trust-family specs
drive the active H0-H6 runs and documented H7-H8 exploratory lanes; benchmark-family specs use the same `ExperimentSpec`
envelope with `experiment.family = "benchmark"` and benchmark add-on sections.

Trust-task batches write TOML outputs under:

```text
results/<batch_name>/<hypothesis_id>/<experiment_id>/
```

Configured auto-analysis, when enabled, writes under the experiment directory:

```text
analysis/raw/
analysis/figures/
analysis/report/
```

Experiment directories also contain resumability artifacts. `results_partial.csv`
and `checkpoint_manifest.json` are updated after each completed expanded run, so
rerunning the same command with the same `--batch-name` skips completed
`variant_id` × `seed` × `replication` tasks and fills in only missing work.

| Card | Result root | Question | Specs | Configured analysis |
|---|---|---|---|---|
| H0 Policy Openness | `results/<batch>/h0/` | Is the policy space open enough for precision to change behavior? | `configs/trust/hypotheses/h0_policy_openness/shallow_binary.toml`, `configs/trust/hypotheses/h0_policy_openness/graded_choice.toml`, `configs/trust/hypotheses/h0_policy_openness/graded_choice_confirm.toml`, `configs/trust/hypotheses/h0_policy_openness/graded_betrayal.toml` | `analysis.configured` |
| H1 Model Fitness | `results/<batch>/h1/` | Does precision track predictive reliability rather than reward? | `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml`, `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml`, `configs/trust/hypotheses/h1_model_fitness/reliability_spine_graded_diagnostic.toml`, `configs/trust/hypotheses/h1_model_fitness/reliability_spine_graded_reward_matched_diagnostic.toml`, `configs/trust/hypotheses/h1_model_fitness/reliability_reward_neutral_diagnostic.toml` | `analysis.configured` |
| H2 Deployment | `results/h2_deployment/` | Are beliefs intact while behavior changes when beta is decoupled from policy precision? | `configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml`, `configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml` | `analysis.configured` |
| H3 Locality / Global Precision | `results/<batch>/h3/` | Does partner-local beta preserve cleaner partner-specific model-fitness signals than a shared global tracker? | `configs/trust/hypotheses/h3_locality/global_beta_smoke.toml`, `configs/trust/hypotheses/h3_locality/global_beta_model_fitness_probe.toml`, `configs/trust/hypotheses/h3_locality/global_beta_deployment_probe.toml`, `configs/trust/hypotheses/h3_locality/global_beta_partner_choice_probe.toml`, `configs/trust/hypotheses/h3_locality/global_beta_betrayal_probe.toml`, `configs/trust/hypotheses/h3_locality/global_beta_focal_switch_probe.toml`, `configs/trust/hypotheses/h3_locality/global_beta_locality_probe.toml`, `configs/trust/hypotheses/h3_locality/lesion_family_probe.toml` | standalone `scripts/analysis/analyze.py` |
| H4 Social Allocation | `results/<batch>/h4/` | Does partner-specific precision guide approach, avoidance, probing, and return? | `configs/trust/hypotheses/h4_social_allocation/partner_choice.toml`, `configs/trust/hypotheses/h4_social_allocation/partner_choice_confirm.toml` | `analysis.configured` |
| H5 Timescale / Volatility | `results/<batch>/h5/` | Does affect help or harm when social change outruns belief recalibration? | `configs/trust/hypotheses/h5_timescale_volatility/betrayal_choice.toml`, `configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation.toml`, `configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation_confirm.toml`, `configs/trust/hypotheses/h5_timescale_volatility/betrayal_precision_sensitivity.toml`, `configs/trust/hypotheses/h5_timescale_volatility/betrayal_precision_sensitivity_gradual.toml` | `analysis.configured` |
| H6 Perturbation Phenotypes | `results/<batch>/h6/` | Do clinical-like parameter variants separate first in precision dynamics, then behavior? | `configs/trust/hypotheses/h6_perturbation/clinical_betrayal.toml`, `configs/trust/hypotheses/h6_perturbation/clinical_dynamics.toml`, `configs/trust/hypotheses/h6_perturbation/affect_sensitivity.toml` | `analysis.configured` |
| H7 Signal Source | future | Does partner-action surprisal remain cleaner than joint action-plus-payoff surprisal? | Future-work; no active TOML until runtime support exists. | pending |
| H8 Observation Noise / Robustness | future | Does beta inertia stabilize or slow behavior under noisy social observations? | Future exploratory TOML under `configs/trust/hypotheses/h8_observation_noise/` when promoted. | pending |
| E1 Trust benchmark arena | `results/e1_benchmarks/` | How do trust-task agents compare with trust-task baselines? | `configs/benchmark/e1_arena/default.toml`, `configs/benchmark/e1_arena/betrayal.toml`, `configs/benchmark/e1_arena/full.toml` | pending benchmark analysis |
| E2 Multi-focal social dynamics | `results/e2_multifocal_descriptive/` | What descriptive dynamics emerge when AIF agents interact with each other? | `experiments/multifocal/configs/e2_homogeneous.json`, `experiments/multifocal/configs/e2_clinical_mix.json`, `experiments/multifocal/configs/e2_assortative.json` | pending multi-focal analysis |

Smoke configs:

| Item | Configs |
|---|---|
| trust smoke | `configs/trust/smoke/smoke.toml` |
| benchmark smoke | `configs/benchmark/smoke/smoke.toml` |
| multi-focal smoke | `experiments/multifocal/configs/smoke.json` |

## Standard Analysis Outputs

For TOML specs with `analysis.auto = true`, the run command writes first-pass
configured outputs under `analysis/raw`, `analysis/figures`, and
`analysis/report`.

Stable raw tables include:

- `final_round_summary.csv`
- `hypothesis_tests.json`
- `affective_movement_summary.csv`
- `deployment_dissociation_summary.csv`
- `partner_choice_summary.csv`
- `phenotype_validation_summary.csv`
- `evidence_effect_summary.csv`
- `betrayal_phase_summary.csv`,
  `betrayal_misdeployment_summary.csv`, and
  `betrayal_reallocation_summary.csv` when switch events are present
- `cross_partner_interference_summary.csv`,
  `partner_phase_delta_summary.csv`, and `global_vs_local_beta_summary.csv`
  from the standalone analysis path when switch-event runs include the H6
  global-beta condition

The standalone post-hoc analysis remains available:

```bash
python scripts/analysis/analyze.py --results results/<batch>/<hypothesis>/<experiment>/results.csv --output-dir results/<batch>/<hypothesis>/<experiment>/analysis
```

Optional follow-up artifacts:

```bash
python scripts/analysis/visualize.py --results results/<batch>/<hypothesis>/<experiment>/results.csv --output-dir results/<batch>/<hypothesis>/<experiment>/gifs
python scripts/analysis/model_comparison.py --results results/<batch>/<hypothesis>/<experiment>/results.csv --output-dir results/<batch>/<hypothesis>/<experiment>/model_comparison
```
