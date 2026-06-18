# Configs

Experiment configs are TOML files under `configs/`. Every maintained config
maps to a result card or canonical raw path in `docs/results/config_map.md`.

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
- optional `[runtime]`: execution profile and runtime limits such as
  `max_policies`.
- optional `[analysis]`: configured analysis contract.

## Runtime Profiles

Runtime profiles organize execution weight without changing the config family:

| Profile | Use | Logging behavior |
|---|---|---|
| `data_collection` | Default for paper, demo, diagnostics, and future configs that collect trajectories | Writes the manuscript-facing row contract: payoff, choices, entropy, beta/precision traces, prediction error, log evidence, inference correctness, switch markers, and provenance metadata. Omits diagnostic-only policy and belief tensors. |
| `debug` | Narrow local debugging configs only | Enables `debug_mode`, policy traces, full `q_pi`/`G` vectors, policy-step costs, partner belief matrices, and posterior tensors; avoid for statistical batches. |

Post-hoc analysis remains separate under `[analysis]`. For fastest full data
collection, keep `profile = "data_collection"` and run heavy analysis after
the trajectories are written.

The Exp A-C paper configs use a suite form with `[suite]`, `[defaults.*]`,
`[[variants]]`, and one or more `[[experiments]]`. `run.py` supports both
forms.

## Paper Configs

| Config | Claim role | Workload | What it does |
|---|---|---:|---|
| `configs/paper/01_predictability_value.toml` | Section 3.1 predictability over value | 3 variants x 30 seeds x 200 rounds | Paper-facing copy of the corrected model-fitness readout; reviewer ladder remains under diagnostics. |
| `configs/paper/02_deployment_ablation.toml` | Section 3.2 deployment ablation | 4 variants x 30 seeds x 200 rounds | Tests whether tracked-only precision loses behavioral effect when beta cannot modulate gamma. |
| `configs/paper/03_partner_selection.toml` | Section 3.3 partner selection | 3 variants x 30 seeds x 200 rounds | Tests whether precision modulation reshapes graded partner choice before payoff separates. |
| `configs/paper/04_betrayal_adaptation.toml` | Section 3.4 betrayal adaptation | 4 variants x 30 seeds x 120 rounds | Tests abrupt stance change under graded agent-choice play. Compares partner-local affect, tracked-only lesion, shared beta, and no-affect. |
| `configs/paper/05a_alpha_sweep.toml` | Section 3.5 profile gain | 2 scenarios x 8 alpha values x 20 seeds x 200 rounds | Sweeps affective gain from `0.05` to `8.0` in open and betrayal settings to show non-monotonic precision dynamics. |
| `configs/paper/05b_prior_factorial.toml` | Section 3.5 prior x gain profiles | 3 scenarios x 6 variants x 20 seeds x 200 rounds | Crosses naive/cautious beta priors with low/high gain, plus default and no-affect references. |
| `configs/paper/05c_forgiveness.toml` | Section 3.5 trust repair | 6 variants x 20 seeds x 200 rounds | Switches one partner from cooperative to exploitative and back, separating reengagement from confidence restoration. |

## Future Configs

These configs are implemented follow-up surfaces, not diagnostics and not
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
| `configs/diagnostics/h1_model_fitness/` | `reliability_vs_reward.toml`, `reliability_vs_reward_confirm.toml`, `reliability_spine_graded_diagnostic.toml`, `reliability_spine_graded_reward_matched_diagnostic.toml`, `reliability_reward_neutral_diagnostic.toml` | Binary model-fitness diagnostics and reviewer ladder for reward/exposure controls around H1. |
| `configs/diagnostics/h2_deployment/` | `lesion_open_regime.toml`, `lesion_open_regime_confirm.toml` | Tests tracked-only deployment dissociation. |
| `configs/diagnostics/h3_locality/` | `global_beta_*.toml`, `lesion_family_probe.toml` | Tests partner-local versus shared precision routing and lesion families. |
| `configs/diagnostics/h4_social_allocation/` | `partner_choice.toml`, `partner_choice_confirm.toml` | Binary agent-choice allocation probes retained as diagnostics only. |
| `configs/diagnostics/h5_timescale_volatility/` | `betrayal_choice.toml`, `betrayal_reallocation.toml`, `betrayal_precision_sensitivity*.toml` | Volatility and precision-sensitivity probes beyond the final paper H5 config. |
| `configs/diagnostics/h6_perturbation/` | `affect_sensitivity.toml`, `perturbation_betrayal.toml`, `perturbation_dynamics.toml` | Earlier profile-style perturbation probes retained as diagnostic provenance. |
