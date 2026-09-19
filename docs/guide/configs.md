# Configs

Experiment configs are TOML files under `configs/`. This guide covers their
schema, model controls, and output destinations.

## Families

- `configs/paper/`: paper evidence reproduction.
- `configs/demo/`: fast demos used by `notebooks/demo.ipynb`.
- `configs/diagnostics/`: smoke checks, reviewer controls, and informative
  non-paper probes.
- `configs/future/`: implemented exploratory extensions that are not paper
  evidence.

## Config Schema

Most trust configs use this envelope:

- `[hypothesis]`: hypothesis id/name.
- `[experiment]`: id, family, rounds, replications, seed.
- `[scenario]`: payoff mode, assignment mode, partners, switches, and payoff
  parameters.
- `[[variants]]`: explicit affect/planning/precision variants.
- optional `[[sweeps]]`: parameter expansion over selected variants.
- optional `[runtime]`: execution profile and diagnostic logging controls.
- optional `[analysis]`: analysis settings.

For affect-enabled variants, `charge_transform = "linear"` explicitly selects
the paper's charge formula, `alpha * (log(2) - surprise)`. The runtime default
is also linear; `"squared"` is retained only as an explicit diagnostic
override. Variants with `affect = "none"` must not declare a charge transform.

## What The Main Parameters Control

The paper uses one focal `pymdp.Agent` workflow with scripted social partners.
A partner's type and stance are inferred; the focal agent's investment is the
shared action that drives stance transitions, own-action bookkeeping, and payoff.
Longer planning horizons consider more action sequences and increase runtime.

`beta` is an auxiliary confidence tracker, not a POMDP hidden-state factor.
Partner-response surprisal is evaluated using the pre-update prediction. With
the default baseline, linear charge is `alpha_charge * (log(2) - surprisal)`.
Lower expected beta means higher confidence; deployed precision is
`gamma / E[beta]`. Precision scales policy-score deviations within each partner
without shifting that partner's mean score. See the manuscript Methods and
appendices for the complete model.

| Setting | Effect |
|---|---|
| `alpha_charge` | Gain on the signed evidence signal. |
| `initial_beta` / `beta_prior` | Initial confidence state or distribution. |
| `beta_levels` | Discrete support for the confidence tracker. |
| `beta_persistence` | Persistence in the tracker transition. |
| `gamma` | Base policy precision before beta modulation. |
| `sigma_0_sq` | Legacy stored squared baseline; linear charge uses its square root. |

| `affect` mode | Tracker | Policy precision |
|---|---|---|
| `none` | Off | Base gamma |
| `precision` | Partner-local | Gamma divided by that partner's expected beta |
| `tracked_only` | Partner-local | Base gamma; tracker is disconnected from deployment |
| `global_beta` | Shared | Gamma divided by shared expected beta |

These are configuration meanings, not predictions that any setting improves
payoff. Use `docs/results/findings.md` for measured comparisons.

## Runtime Profiles

Runtime profiles organize execution weight without changing the config family:

| Profile | Use | Logging behavior |
|---|---|---|
| `data_collection` | Default for paper, demo, diagnostics, and future configs that collect trajectories | Records payoff, choices, entropy, beta/precision traces, prediction error, log evidence, inference correctness, switch markers, and provenance metadata. Omits diagnostic-only policy and belief tensors. |
| `debug` | Narrow local debugging configs only | Enables `debug_mode`, policy traces, full `q_pi`/`G` vectors, policy-step costs, partner belief matrices, and posterior tensors; avoid for statistical batches. |

Post-hoc analysis remains separate under `[analysis]`. For fastest full data
collection, keep `profile = "data_collection"` and run heavy analysis after
the trajectories are written.

Policy enumeration is exhaustive. Runtime configs do not expose a policy cap
or subsampling option; the policy count is determined exactly by the social
action count and planning horizon.

The Exp A-C paper configs use a suite form with `[suite]`, `[defaults.*]`,
`[[variants]]`, and one or more `[[experiments]]`. `run.py` supports both
forms.

## Paper Configs

| Config | Claim role | Workload | What it does |
|---|---|---:|---|
| `configs/paper/01_predictability_value.toml` | Section 3.1 predictability over value | 3 variants x 30 seeds x 200 rounds | Compares partner predictability and reward. |
| `configs/paper/02_deployment_ablation.toml` | Section 3.2 deployment ablation | 4 variants x 30 seeds x 200 rounds | Tests whether tracked-only precision loses behavioral effect when beta cannot modulate gamma. |
| `configs/paper/03_partner_selection.toml` | Section 3.3 partner selection | 3 variants x 30 seeds x 200 rounds | Tests whether precision modulation reshapes graded partner choice before payoff separates. |
| `configs/paper/04_betrayal_adaptation.toml` | Section 3.4 betrayal adaptation | 4 variants x 30 seeds x 120 rounds | Tests abrupt stance change under graded agent-choice play. Compares partner-local affect, tracked-only lesion, shared beta, and no-affect. |
| `configs/paper/05a_alpha_sweep.toml` | Section 3.5 profile gain | 2 scenarios x 8 alpha values x 20 seeds x 200 rounds | Sweeps affective gain from `0.05` to `8.0` in open and betrayal settings to show non-monotonic precision dynamics. |
| `configs/paper/05b_prior_factorial.toml` | Section 3.5 prior x gain profiles | 3 scenarios x 6 variants x 20 seeds x 200 rounds | Crosses naive/cautious beta priors with low/high gain, plus default and no-affect references. |
| `configs/paper/05c_forgiveness.toml` | Section 3.5 trust repair | 6 variants x 20 seeds x 200 rounds | Switches one partner from cooperative to exploitative and back, separating reengagement from confidence restoration. |

## Future Configs

These configs are exploratory experiments, not diagnostics and not
paper evidence.

| Config | Role | Workload | What it does |
|---|---|---:|---|
| `configs/future/mixed_volatility.toml` | heterogeneous-volatility extension | 4 variants x 20 seeds x 200 rounds | Tests stable and shifting partners in the same episode; reserved for future change-detection and volatility-learning work. |

## Demo Configs

| Config | Runtime scale | Purpose |
|---|---:|---|
| `configs/demo/01_predictability_value.toml` | 3 variants x 2 seeds x 40 rounds | Fast analogue of paper Section 3.1. |
| `configs/demo/02_deployment_ablation.toml` | 4 variants x 1 seed x 40 rounds | Fast analogue of paper Section 3.2. |
| `configs/demo/03_partner_selection.toml` | 3 variants x 1 seed x 40 rounds | Fast analogue of paper Section 3.3. |
| `configs/demo/04_betrayal_adaptation.toml` | 4 variants x 2 seeds x 50 rounds | Fast analogue of paper Section 3.4 with an earlier switch. |
| `configs/demo/05a_alpha_sweep.toml` | opt-in: 2 scenarios x 3 alpha values x 1 seed x 60 rounds | Fast analogue of paper Exp A. |
| `configs/demo/05b_prior_factorial.toml` | optional: 3 scenarios x 4 variants x 1 seed x 60 rounds | Reduced analogue of paper Exp B. |
| `configs/demo/05c_forgiveness.toml` | optional: 3 variants x 1 seed x 60 rounds | Reduced analogue of paper Exp C. |

## Diagnostic Configs

Diagnostics are retained because they are informative, not because they are
paper evidence. Use them for smoke tests, reviewer controls, and mechanism
probes that are not part of the current manuscript reproduction claim.

| Folder | Configs | Purpose |
|---|---|---|
| `configs/diagnostics/smoke/` | `trust_smoke.toml` | One-seed runner sanity check. |
| `configs/diagnostics/h0_policy_openness/` | `shallow_binary.toml`, `graded_choice.toml`, `graded_choice_confirm.toml`, `graded_betrayal.toml` | Checks whether affective precision can matter only when policy posteriors are open enough to move. |
| `configs/diagnostics/h1_model_fitness/` | `reliability_vs_reward.toml`, `reliability_vs_reward_confirm.toml`, `reliability_spine_graded_diagnostic.toml`, `reliability_spine_graded_reward_matched_diagnostic.toml`, `reliability_reward_neutral_diagnostic.toml` | Binary model-fitness diagnostics and additional checks for reward/exposure controls around H1. |
| `configs/diagnostics/h2_deployment/` | `lesion_open_regime.toml`, `lesion_open_regime_confirm.toml` | Tests tracked-only deployment dissociation. |
| `configs/diagnostics/h3_locality/` | `global_beta_*.toml`, `lesion_family_probe.toml` | Tests partner-local versus shared precision routing and lesion families. |
| `configs/diagnostics/h4_social_allocation/` | `partner_choice.toml`, `partner_choice_confirm.toml` | Binary agent-choice allocation probes retained as diagnostics only. |
| `configs/diagnostics/h5_timescale_volatility/` | `betrayal_choice.toml`, `betrayal_reallocation.toml`, `betrayal_precision_sensitivity*.toml` | Volatility and precision-sensitivity probes beyond the final paper H5 config. |
| `configs/diagnostics/h6_perturbation/` | `affect_sensitivity.toml`, `perturbation_betrayal.toml`, `perturbation_dynamics.toml` | Earlier profile-style perturbation probes retained as additional comparisons. |

## Output Destinations

Every TOML config under `configs/` has a documented result destination.
Tracked public summaries live under `results/paper/`, `results/diagnostics/`, and
`results/future/`. Full per-round `results.csv` files are gitignored under each
card's `raw/` subtree when materialized locally.

When you run a config through `scripts/experiment/run.py` **without**
`--output-dir` or `--batch-name`, the runner uses the **default output layout**
implemented in `experiments/trust/output_layout.py`:

| Config family | Default write root |
|---|---|
| `configs/paper/` | `results/paper/<config-stem>/raw/` |
| `configs/diagnostics/` | `results/diagnostics/...` (documented result folder or `results/diagnostics/raw/...`) |
| `configs/future/` | `results/future/<config-stem>/raw/` |
| `configs/demo/` | `outputs/demo/<config-stem>/<hypothesis>/<experiment>/` |

Paper suite configs with multiple `[[experiments]]` blocks write under
`results/paper/<config-stem>/raw/<experiment_id>/`.

An explicit custom batch layout is available when you pass output paths:

```text
--output-dir <root> --batch-name <batch>
  -> <root>/<batch>/<hypothesis_id>/<experiment_id>/results.csv
```

The **default raw path** column below matches the default runner layout for
each config.

### Paper Configs — Output Paths

| Config | Result card | Raw result path |
|---|---|---|
| `configs/paper/01_predictability_value.toml` | `results/paper/01_predictability_value/` | `results/paper/01_predictability_value/raw/results.csv` |
| `configs/paper/02_deployment_ablation.toml` | `results/paper/02_deployment_ablation/` | `results/paper/02_deployment_ablation/raw/results.csv` |
| `configs/paper/03_partner_selection.toml` | `results/paper/03_partner_selection/` | `results/paper/03_partner_selection/raw/results.csv` |
| `configs/paper/04_betrayal_adaptation.toml` | `results/paper/04_betrayal_adaptation/` | `results/paper/04_betrayal_adaptation/raw/results.csv` |
| `configs/paper/05a_alpha_sweep.toml` | `results/paper/05a_alpha_sweep/` | `results/paper/05a_alpha_sweep/raw/open_graded/results.csv`; `results/paper/05a_alpha_sweep/raw/betrayal/results.csv` |
| `configs/paper/05b_prior_factorial.toml` | `results/paper/05b_prior_factorial/` | `results/paper/05b_prior_factorial/raw/open_graded/results.csv`; `results/paper/05b_prior_factorial/raw/betrayal/results.csv`; `results/paper/05b_prior_factorial/raw/partner_choice/results.csv` |
| `configs/paper/05c_forgiveness.toml` | `results/paper/05c_forgiveness/` | `results/paper/05c_forgiveness/raw/results.csv` |

Suite index: `results/paper/manifest.json`.

### Future Configs — Output Paths

| Config | Result card | Raw result path |
|---|---|---|
| `configs/future/mixed_volatility.toml` | `results/future/mixed_volatility/` | `results/future/mixed_volatility/raw/results.csv` |

### Demo Configs — Output Paths

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

### Diagnostics With Saved Summaries — Output Paths

| Config | Result card | Raw result path |
|---|---|---|
| `configs/diagnostics/h0_policy_openness/graded_choice.toml` | `results/diagnostics/policy_openness/` | `results/diagnostics/policy_openness/raw/h0/graded_choice/results.csv` |
| `configs/diagnostics/h2_deployment/lesion_open_regime.toml` | `results/diagnostics/deployment/` | `results/diagnostics/deployment/raw/h2/lesion_open_regime/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_locality_probe.toml` | `results/diagnostics/locality/` | `results/diagnostics/locality/raw/h3/global_beta_locality_probe/results.csv` |
| `configs/diagnostics/h3_locality/global_beta_focal_switch_probe.toml` | `results/diagnostics/locality/` | `results/diagnostics/locality/raw/h3/global_beta_focal_switch_probe/results.csv` |
| `configs/diagnostics/h1_model_fitness/reliability_vs_reward_confirm.toml` | `results/diagnostics/model_fitness/` | `results/diagnostics/model_fitness/raw/h1/reliability_vs_reward_confirm/results.csv` |
| `configs/diagnostics/h4_social_allocation/partner_choice_confirm.toml` | `results/diagnostics/social_allocation/` | `results/diagnostics/social_allocation/raw/partner_choice_confirm_20260609/h4/partner_choice_confirm/results.csv` |

Interpretation for documented diagnostics lives in `docs/results/diagnostics.md`.

### Other Diagnostic Configs — Output Paths

These configs are additional diagnostic experiments. They do not have
tracked compact summaries in git. Use the default raw path when you need to
retain outputs outside a one-off batch directory.

| Config | Raw result path |
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

H6 diagnostic outputs are separate from the current paper profile sources
listed in `docs/results/provenance.md`.

### Saved Results

Each result folder contains its summaries and a `manifest.json` describing the
run. Profile metrics are saved under their individual experiment folders.
Raw trajectories stay in `raw/`; see the [results guide](../results/README.md)
for the downloadable paper data.
