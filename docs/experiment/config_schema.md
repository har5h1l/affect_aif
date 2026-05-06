# Unified Experiment TOML Schema

Maintained runnable experiments use one TOML file per experiment under
`configs/`. Trust-family specs live under `configs/trust/`; benchmark-family
specs live under `configs/benchmark/`.

The hierarchy is:

```text
hypothesis -> experiment -> scenario -> variants -> sweeps -> replications -> rounds
```

Current public layout:

```text
configs/
  trust/
    hypotheses/
    smoke/
  benchmark/
    e1_arena/
    cvc/
    smoke/
```

## Sections

`[hypothesis]`

- `id`: behavior-card id such as `h3`
- `name`: stable machine-readable label such as `stress_response`

`[experiment]`

- `id`: experiment id used in result paths
- `family`: `trust`, `benchmark`, or a future family such as `multifocal`
- `rounds`: episode length
- `replications`: number of seeds per expanded variant
- `seed`: base seed; replication `r` uses `seed + r`

`[scenario]`

- `payoff`: `binary` or `graded`
- `assignment`: `random` or `agent_choice`
- `partners`
- `type_volatility`
- `observation_noise`
- `partner_types`
- `initial_types`
- `initial_stances`
- `[[scenario.stance_switches]]` with `round`, `partner`, and `to`
- graded payoff knobs: `investment_levels`, `endowment`, `multiplier`

`[[variants]]`

- `id`
- `affect`: `none`, `precision`, or `tracked_only`
- `planning_horizon`
- `gamma`
- `epistemic_value`
- `alpha_charge`
- `sigma_0_sq`
- `initial_beta`
- `beta_persistence`
- `beta_levels`
- `action_selection`

`[[sweeps]]`

- `parameter`: variant field to replace
- `values`: explicit values
- `applies_to`: variant ids

Sweep expansion produces concrete `variant_id` values such as
`affect__planning_horizon_4`.

`[runtime]`

- `max_policies`

`[analysis]`

- `auto`: whether the experiment runner writes configured analysis outputs
- `target`: usually `experiment`
- `primary`: configured analysis module id such as `h3_stress_response`
- `compare`: variants to compare
- `switch_window`
- `metrics`

`[benchmark]`

Required when `experiment.family = "benchmark"` and rejected for
`experiment.family = "trust"`.

- `backends`: backend ids such as `trust` or `cvc_local`
- `agents`: simple registry/policy names when strings are sufficient
- `[[benchmark.agent_specs]]`: structured agent declarations with `name`,
  `backend`, `kind`, `implementation`, and/or `policy_spec`

Family-specific benchmark knobs stay namespaced:

- `[benchmark.trust]`: trust benchmark scenario and trust backend overrides
- `[benchmark.cvc_local]`: CvC mission, worker, and step settings
- `[benchmark.observatory]`: optional Observatory season/pool metadata

## Removed Public Keys

The TOML surface rejects legacy condition and DTM-era public keys, including
`conditions`, `presets`, `deep_horizon`, `shallow_horizon`,
`horizon_overrides`, parameter-learning knobs, `lesion_mode`,
`run_sensitivity`, `sensitivity_factors`, `experiment_name`, verbosity fields,
and GIF fields.

Replacements:

- numeric `conditions` and named `presets` become explicit `[[variants]]`
- `lesion_mode = "decouple"` becomes `affect = "tracked_only"`
- sensitivity runs become explicit `[[sweeps]]`
- `experiment_name` becomes `[experiment].id`
- verbosity and GIF behavior stay on the CLI

## Minimal Examples

Trust-family smoke:

```toml
[hypothesis]
id = "smoke"
name = "smoke"

[experiment]
id = "smoke"
family = "trust"
rounds = 2
replications = 1
seed = 0

[scenario]
payoff = "binary"
assignment = "random"
partners = 2

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 1
```

Benchmark-family smoke:

```toml
[hypothesis]
id = "e1"
name = "benchmark_arena"

[experiment]
id = "benchmark_smoke"
family = "benchmark"
rounds = 1
replications = 1
seed = 7

[scenario]
payoff = "binary"
assignment = "random"
partners = 2

[[variants]]
id = "benchmark"
affect = "none"
planning_horizon = 1

[benchmark]
backends = ["trust"]
agents = ["random"]

[benchmark.trust]
scenario = "resource_sharing"
```
