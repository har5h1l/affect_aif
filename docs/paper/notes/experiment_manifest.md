# Supplement: Experiment Manifest

This is the paper-facing subset of the maintained experiment manifest. The
operational manifest remains `docs/experiments/manifest.md`.

## Primary H0-H5 Specs

| Card | Purpose | Primary configs |
|---|---|---|
| H0 Openness Gate | Test whether policy-space openness gates affect effects. | `configs/trust/hypotheses/h0_openness/shallow_binary.toml`, `configs/trust/hypotheses/h0_openness/graded_choice.toml`, `configs/trust/hypotheses/h0_openness/graded_betrayal.toml` |
| H1 Model Fitness | Test whether precision tracks predictability rather than reward. | `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml`, `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml` |
| H2 Deployment | Test beta-to-policy lesion in an open regime. | `configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml` |
| H3 Stress Response | Test betrayal/stress windows and misdeployment. | `configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml`, `configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml`, `configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity.toml`, `configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity_gradual.toml` |
| H4 Social Choice | Test partner selection, avoidance, and probing. | `configs/trust/hypotheses/h4_social_choice/partner_choice.toml` |
| H5 Perturbation Phenotypes | Test clinical-like precision-dynamics perturbations. | `configs/trust/hypotheses/h5_perturbation/clinical_betrayal.toml`, `configs/trust/hypotheses/h5_perturbation/clinical_dynamics.toml`, `configs/trust/hypotheses/h5_perturbation/affect_sensitivity.toml` |

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
