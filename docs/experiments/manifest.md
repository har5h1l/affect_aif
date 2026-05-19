# Experiment Manifest

This manifest maps maintained TOML experiment specs under `configs/` to the
canonical behavior-card spine in `docs/theory/hypotheses.md`. Trust-family specs
drive the H0-H5 runs; benchmark-family specs use the same `ExperimentSpec`
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
| H0 Openness Gate | `results/h0_openness/` | Is the policy space open enough for precision to change behavior? | `configs/trust/hypotheses/h0_openness/shallow_binary.toml`, `configs/trust/hypotheses/h0_openness/graded_choice.toml`, `configs/trust/hypotheses/h0_openness/graded_betrayal.toml` | `analysis.configured` |
| H1 Model Fitness | `results/h1_model_fitness/` | Does precision track predictive reliability rather than reward? | `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml`, `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml` | `analysis.configured` |
| H2 Deployment | `results/h2_deployment/` | Are beliefs intact while behavior changes when beta is decoupled from policy precision? | `configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml` | `analysis.configured` |
| H3 Stress Response | `results/h3_stress_response/` | Does affect help most around betrayal, stance shifts, or other volatility windows? | `configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml`, `configs/trust/hypotheses/h3_stress_response/betrayal_reallocation.toml`, `configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml` | `analysis.configured` |
| H4 Social Choice | `results/h4_social_choice/` | Does partner-specific precision guide approach, avoidance, probing, and return? | `configs/trust/hypotheses/h4_social_choice/partner_choice.toml` | `analysis.configured` |
| H5 Perturbation Phenotypes | `results/h5_perturbation/` | Do clinical-like parameter variants separate first in precision dynamics, then behavior? | `configs/trust/hypotheses/h5_perturbation/clinical_betrayal.toml`, `configs/trust/hypotheses/h5_perturbation/clinical_dynamics.toml`, `configs/trust/hypotheses/h5_perturbation/affect_sensitivity.toml` | `analysis.configured` |
| E1 External benchmark arena | `results/e1_benchmarks/` | How do trust-task agents compare with benchmark surfaces? | `configs/benchmark/e1_arena/default.toml`, `configs/benchmark/e1_arena/betrayal.toml`, `configs/benchmark/e1_arena/full.toml`, `configs/benchmark/cvc/local_smoke.toml` | pending benchmark analysis |
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

The standalone post-hoc analysis remains available:

```bash
python scripts/analysis/analyze.py --results results/<batch>/<hypothesis>/<experiment>/results.csv --output-dir results/<batch>/<hypothesis>/<experiment>/analysis
```

Optional follow-up artifacts:

```bash
python scripts/analysis/visualize.py --results results/<batch>/<hypothesis>/<experiment>/results.csv --output-dir results/<batch>/<hypothesis>/<experiment>/gifs
python scripts/analysis/model_comparison.py --results results/<batch>/<hypothesis>/<experiment>/results.csv --output-dir results/<batch>/<hypothesis>/<experiment>/model_comparison
```
