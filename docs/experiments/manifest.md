# Experiment Manifest

This manifest maps the maintained experiment surface to the current Hesp-extension hypothesis spine. Benchmark and CvC configs still under `configs/` are preserved for the later benchmark phase and are not interpreted as primary trust-task hypothesis configs here.

| Item | Question | Configs | Analysis |
|---|---|---|---|
| H1 | Model fitness, not reward | `experiments/trust/configs/h1_model_fitness_factorial.json` | `analysis.hypotheses.test_h1_model_fitness` |
| H2 | Partner factorization | pending config | `analysis.hypotheses.test_h2_partner_factorization` |
| H3 | Deployment, not knowledge | `experiments/trust/configs/h3_deployment_lesion.json` | `analysis.hypotheses.test_h3_deployment_not_knowledge` |
| H4 | Social volatility | `experiments/trust/configs/h4_betrayal_volatility.json` | `analysis.hypotheses.test_h4_social_volatility` |
| H5 | Partner selection | `experiments/trust/configs/h5_partner_selection.json` | `analysis.hypotheses.test_h5_partner_selection` |
| H6 | Policy-space regime | `experiments/trust/configs/h6_shallow_policy_regime.json`, `experiments/trust/configs/h6_graded_policy_regime.json`, `experiments/trust/configs/h6_graded_betrayal.json` | `analysis.hypotheses.test_h6_policy_space_regime` |
| H7 | Clinical perturbations | `experiments/trust/configs/h7_clinical_betrayal.json`, `experiments/trust/configs/h7_clinical_phenotypes.json`, `experiments/trust/configs/h7_sensitivity_sweep.json` | `analysis.hypotheses.test_h7_clinical_perturbations` |
| E1 | External benchmark arena | pending Phase 5 benchmark config move; current benchmark configs remain under `configs/benchmark*.json` | pending benchmark analysis |
| E2 | Multi-focal social dynamics | `experiments/multifocal/configs/e2_homogeneous.json`, `experiments/multifocal/configs/e2_clinical_mix.json`, `experiments/multifocal/configs/e2_assortative.json` | pending multi-focal analysis |

Smoke configs:

| Item | Configs |
|---|---|
| trust smoke | `experiments/trust/configs/smoke.json` |
| multi-focal smoke | `experiments/multifocal/configs/smoke.json` |
