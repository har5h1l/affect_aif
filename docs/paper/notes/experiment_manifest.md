# Supplement: Experiment Manifest

This is the paper-facing subset of the maintained experiment manifest. The
operational manifest remains `docs/experiments/manifest.md`.

## Primary / Exploratory H0-H8 Specs

| Card | Purpose | Primary configs |
|---|---|---|
| H0 Policy Openness | Test whether policy-space openness gates affect effects. | `configs/trust/hypotheses/h0_policy_openness/shallow_binary.toml`, `configs/trust/hypotheses/h0_policy_openness/graded_choice.toml`, `configs/trust/hypotheses/h0_policy_openness/graded_betrayal.toml` |
| H1 Model Fitness | Test whether precision tracks predictability rather than reward. | `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml`, `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml` |
| H2 Deployment | Test beta-to-policy lesion in an open regime. | `configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml` |
| H3 Locality / Global Precision | Test local beta against shared global beta. | `configs/trust/hypotheses/h3_locality/global_beta_focal_switch_probe.toml`, `configs/trust/hypotheses/h3_locality/global_beta_locality_probe.toml` |
| H4 Social Allocation | Test partner selection, avoidance, and probing. | `configs/trust/hypotheses/h4_social_allocation/partner_choice.toml` |
| H5 Timescale / Volatility | Test betrayal/stress windows and misdeployment. | `configs/trust/hypotheses/h5_timescale_volatility/betrayal_choice.toml`, `configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation_confirm.toml`, `configs/trust/hypotheses/h5_timescale_volatility/betrayal_precision_sensitivity.toml`, `configs/trust/hypotheses/h5_timescale_volatility/betrayal_precision_sensitivity_gradual.toml` |
| H6 Perturbation Phenotypes | Test clinical-like precision-dynamics perturbations. | `configs/trust/hypotheses/h6_perturbation/clinical_betrayal.toml`, `configs/trust/hypotheses/h6_perturbation/clinical_dynamics.toml`, `configs/trust/hypotheses/h6_perturbation/affect_sensitivity.toml` |
| H7 Signal Source | Compare partner-action surprisal with joint surprise. | Future-work; no active config. |
| H8 Observation Noise / Robustness | Test beta inertia under noisy observations. | Future exploratory config. |

## Evidence Batches

| Evidence tier | Batch root | Use in paper |
|---|---|---|
| Primary May H0-H5 queue | `results/updated_h0_h5_20260517_w2/`, `results/updated_h0_h5_20260518_remainder/` | Broad H0-H5 evidence and H5 dynamics. |
| H0/H1/H2/H4 local confirmation | `results/confirm_h0_h1_h2_h4_20260518/` | Open-regime, model-fitness, deployment, and social-choice summaries. |
| H1/H3 split confirmation | `results/confirm_h1_h3_split_20260519/` | Main H1 and H3 confirmation. |
| H3 precision sensitivity | `results/h3_precision_sensitivity_20260522/` | Stress boundary-condition robustness. |

## Secondary Tracks

E1 benchmark and E2 multi-focal configs remain future or descriptive tracks.
They should not carry the main manuscript claims unless promoted by a separate
analysis and result note.
