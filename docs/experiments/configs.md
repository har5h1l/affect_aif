# Configs

Experiment configs are TOML files under `configs/`.

## Families

- `configs/paper/`: paper evidence reproduction.
- `configs/demo/`: fast demos used by `notebooks/demo.ipynb`.
- `configs/diagnostics/`: smoke checks, reviewer controls, and informative
  non-paper probes.

## Config Schema

Most trust configs use this envelope:

- `[hypothesis]`: hypothesis id/name.
- `[experiment]`: id, family, rounds, replications, seed.
- `[scenario]`: payoff mode, assignment mode, partners, switches, and payoff
  parameters.
- `[[variants]]`: explicit affect/planning/precision variants.
- optional `[[sweeps]]`: parameter expansion over selected variants.
- optional `[runtime]`: runtime limits such as `max_policies`.
- optional `[analysis]`: configured analysis contract.

The Exp A-D paper configs use a suite form with `[suite]`, `[defaults.*]`,
`[[variants]]`, and one or more `[[experiments]]`. `run.py` supports both
forms.

## Paper Configs

| Config | Claim role | Workload | What it does |
|---|---|---:|---|
| `configs/paper/h1_model_fitness/reliability_vs_reward_confirm.toml` | H1 model fitness | 3 variants x 30 seeds x 200 rounds | Tests whether partner-local precision tracks predictability more strongly than reward after active-encounter controls. Includes no-affect, partner-local affect, and shared beta. |
| `configs/paper/h5_betrayal/betrayal_reallocation_confirm.toml` | H5 betrayal adaptation | 4 variants x 30 seeds x 120 rounds | Tests abrupt stance change under graded agent-choice play. Compares partner-local affect, tracked-only lesion, shared beta, and no-affect. |
| `configs/paper/alpha_sweep.toml` | Exp A profile gain | 2 scenarios x 8 alpha values x 20 seeds x 200 rounds | Sweeps affective gain from `0.05` to `8.0` in open and betrayal settings to show non-monotonic precision dynamics. |
| `configs/paper/prior_factorial.toml` | Exp B prior x gain profiles | 3 scenarios x 6 variants x 20 seeds x 200 rounds | Crosses naive/cautious beta priors with low/high gain, plus default and no-affect references. |
| `configs/paper/forgiveness.toml` | Exp C trust repair | 6 variants x 20 seeds x 200 rounds | Switches one partner from cooperative to exploitative and back, separating reengagement from confidence restoration. |
| `configs/paper/mixed_volatility.toml` | Exp D mixed volatility | 4 variants x 20 seeds x 200 rounds | Tests a stable exploiter alongside partners with staged volatility to expose payoff/calibration boundary conditions. |

## Demo Configs

| Config | Runtime scale | Purpose |
|---|---:|---|
| `configs/demo/model_fitness.toml` | 3 variants x 2 seeds x 40 rounds | Fast H1-style workflow check for model-fitness plots and summaries. |
| `configs/demo/betrayal_adaptation.toml` | 4 variants x 2 seeds x 50 rounds | Fast H5-style workflow check with abrupt change and lesion/global controls. |
| `configs/demo/alpha_sweep.toml` | 3 variants x 2 seeds x 60 rounds | Small profile-gain sweep for notebook exploration. |

## Diagnostic Configs

Diagnostics are retained because they are informative, not because they are
paper evidence. Use them for smoke tests, reviewer controls, and mechanism
probes that are not part of the current manuscript reproduction claim.

| Folder | Configs | Purpose |
|---|---|---|
| `configs/diagnostics/smoke/` | `trust_smoke.toml` | One-seed runner sanity check. |
| `configs/diagnostics/h0_policy_openness/` | `shallow_binary.toml`, `graded_choice.toml`, `graded_choice_confirm.toml`, `graded_betrayal.toml` | Checks whether affective precision can matter only when policy posteriors are open enough to move. |
| `configs/diagnostics/h1_model_fitness/` | `reliability_vs_reward.toml`, `reliability_spine_graded_diagnostic.toml`, `reliability_spine_graded_reward_matched_diagnostic.toml`, `reliability_reward_neutral_diagnostic.toml` | Reviewer ladder for reward/exposure controls around H1. |
| `configs/diagnostics/h2_deployment/` | `lesion_open_regime.toml`, `lesion_open_regime_confirm.toml` | Tests tracked-only deployment dissociation. |
| `configs/diagnostics/h3_locality/` | `global_beta_*.toml`, `lesion_family_probe.toml` | Tests partner-local versus shared precision routing and lesion families. |
| `configs/diagnostics/h4_social_allocation/` | `partner_choice.toml`, `partner_choice_confirm.toml` | Agent-choice allocation probes. |
| `configs/diagnostics/h5_timescale_volatility/` | `betrayal_choice.toml`, `betrayal_reallocation.toml`, `betrayal_precision_sensitivity*.toml` | Volatility and precision-sensitivity probes beyond the final paper H5 config. |
| `configs/diagnostics/h6_perturbation/` | `affect_sensitivity.toml`, `perturbation_betrayal.toml`, `perturbation_dynamics.toml` | Earlier profile-style perturbation probes retained as diagnostic provenance. |
