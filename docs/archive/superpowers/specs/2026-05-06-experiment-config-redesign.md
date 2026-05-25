# Experiment Config Redesign

## Summary

Redesign the trust experiment configuration and run surface around the current
H0-H5 hypothesis spine. The new surface should remove legacy condition
taxonomy, make planning horizon a normal knob, keep experiment files small, and
connect each experiment to its intended analysis outputs.

The central hierarchy is:

```text
hypothesis -> experiment -> scenario -> variants -> replications -> rounds
```

One experiment file defines one scenario and the variants compared within that
scenario. A replication is one full episode under one seed. An episode contains
the configured number of rounds.

Backward compatibility with the old numeric condition IDs is intentionally out
of scope.

## Goals

- Replace JSON experiment configs with human-authored TOML experiment specs.
- Use one file per experiment, grouped by hypothesis folder.
- Replace `conditions` and `presets` with explicit `variants`.
- Treat `planning_horizon` as a variant knob, not as a condition category.
- Remove legacy and DTM public knobs from maintained configs.
- Add a first-class analysis declaration so experiment runs can optionally
  generate configured raw analysis outputs.
- Update docs in the same implementation pass so the runnable workflow stays
  accurate.

## Non-Goals

- Preserve compatibility with current `conditions: [1, 2, ...]` configs.
- Keep deprecated or future-work configs in the maintained experiment tree.
- Redesign all analysis internals in the first implementation pass.
- Reinterpret result narratives from new runs.
- Add orchestration or deployment scripts; remote execution still uses Mango.

## File Layout

Maintained trust experiments should live under:

```text
experiments/trust/hypotheses/
  h0_openness/
    shallow_binary.toml
    graded_choice.toml
    graded_betrayal.toml
  h1_model_fitness/
    reliability_vs_reward.toml
  h2_deployment/
    lesion_open_regime.toml
  h3_stress_response/
    betrayal_choice.toml
  h4_social_choice/
    partner_choice.toml
  h5_perturbation/
    clinical_betrayal.toml
    clinical_dynamics.toml
    affect_sensitivity.toml
```

No deferred or speculative configs should live in this maintained tree. If a
future-work scenario is worth preserving, document it as future work rather
than as a runnable core experiment.

## Experiment Spec Shape

Use TOML because it is readable and supported by Python's standard `tomllib`
on supported modern runtimes, with `tomli` already available for older Python
versions in the dev dependency set.

Example:

```toml
[hypothesis]
id = "h3"
name = "stress_response"

[experiment]
id = "betrayal_choice"
rounds = 120
replications = 100
seed = 42

[scenario]
payoff = "binary"
assignment = "agent_choice"
partners = 4
type_volatility = 0.0
observation_noise = 0.0
partner_types = ["cooperator", "reciprocator", "exploiter", "random"]
initial_types = ["cooperator", "reciprocator", "cooperator", "random"]
initial_stances = ["trusting", "neutral", "neutral", "neutral"]

[[scenario.stance_switches]]
round = 31
partner = 0
to = "hostile"

[[variants]]
id = "no_affect"
affect = "none"
planning_horizon = 4

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 4

[[variants]]
id = "lesioned"
affect = "tracked_only"
planning_horizon = 4

[[variants]]
id = "no_epistemic"
affect = "precision"
planning_horizon = 4
epistemic_value = false

[runtime]
max_policies = 4096

[analysis]
auto = true
target = "experiment"
primary = "h3_stress_response"
compare = ["affect", "no_affect", "lesioned"]
switch_window = [1, 10]
metrics = ["payoff", "precision", "partner_choice", "stance_accuracy"]
```

## Public Config Vocabulary

### Scenario Knobs

Keep these as public scenario knobs:

- `payoff`: `binary` or `graded`
- `assignment`: `random` or `agent_choice`
- `partners`
- `rounds`
- `type_volatility`
- `observation_noise`
- `partner_types`
- `initial_types`
- `initial_stances`
- `stance_switches`

For graded payoff scenarios, keep the graded payoff knobs under `scenario`,
such as `investment_levels`, `endowment`, and `multiplier`.

For binary payoff scenarios, keep binary payoff matrix overrides only when an
experiment explicitly needs them. Defaults should cover normal runs.

### Variant Knobs

Keep these as public variant knobs:

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

Prefer explicit beta support:

```toml
beta_levels = [0.5, 0.67, 1.0, 1.5, 2.0]
```

over a derived level count. This makes the scientific support visible in the
experiment spec.

### Run And Runtime Knobs

Keep these:

- `replications`
- `seed`
- `max_policies` under `[runtime]`

Keep `workers`, verbosity, GIF generation, and dry-run behavior as CLI flags,
not config fields.

## Removed Public Knobs

Remove these from the maintained public config surface:

- `conditions`
- `presets`
- `deep_horizon`
- `shallow_horizon`
- `horizon_overrides`
- `lr`
- `use_parameter_learning`
- `learn_A`
- `learn_B`
- `learn_E`
- `pA_scale`
- `pB_scale`
- `lr_E`
- `lesion_mode`
- `run_sensitivity`
- `sensitivity_factors`
- `experiment_name`
- `verbose`
- `verbosity_mode`
- `gif_after_run`
- `gif_output_dir`

Replacement rules:

- `conditions` and `presets` become explicit `variants`.
- `lesion_mode = "decouple"` becomes `affect = "tracked_only"`.
- sensitivity runs become explicit `[[sweeps]]` blocks.
- `experiment_name` becomes `[experiment].id`.
- verbosity and GIF options stay on the CLI.

## Sweeps

Sweeps are allowed only when an experiment is explicitly about a parameter
axis. They should not replace ordinary explicit variants.

Example for H0:

```toml
[[sweeps]]
parameter = "planning_horizon"
values = [1, 2, 3, 4, 8]
applies_to = ["no_affect", "affect"]
```

Example for H5 sensitivity:

```toml
[[sweeps]]
parameter = "alpha_charge"
values = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0]
applies_to = ["affect"]
```

Expanded sweep runs should produce concrete variant IDs such as:

```text
affect__planning_horizon_1
affect__planning_horizon_2
```

This keeps result tables and plots concrete.

## Runner Design

The trust runner should expand:

```text
experiment x variants x sweeps x replications
```

Each expanded item runs one full episode. The runner should save rows with the
new identity fields:

- `hypothesis_id`
- `experiment_id`
- `variant_id`
- `replication`
- `seed`
- `round`

The old `condition` field should disappear from the new supported output
surface.

Default output layout:

```text
results/<hypothesis>/<experiment>/
  results.csv
  results_partial.csv
  config.toml
  metadata.json
```

The CLI should continue to support multiple experiment config paths and a
shared worker pool, but the unit of scheduling becomes an expanded
variant-replication run rather than a condition-replication run.

## Analysis Integration

Analysis should become a first-class configured stage while remaining separate
from simulation code.

Target package layout:

```text
analysis/
  core/
    loading.py
    summaries.py
    statistics.py
    plots.py
    windows.py
  hypotheses/
    h0_openness/
      analyze.py
      schema.py
    h1_model_fitness/
      analyze.py
      schema.py
    h2_deployment/
      analyze.py
      schema.py
    h3_stress_response/
      analyze.py
      schema.py
    h4_social_choice/
      analyze.py
      schema.py
    h5_perturbation/
      analyze.py
      schema.py
  reports/
    render.py
    manifest.py
```

Experiment specs declare what analysis to run:

```toml
[analysis]
auto = true
target = "experiment"
primary = "h3_stress_response"
compare = ["affect", "no_affect", "lesioned"]
switch_window = [1, 10]
metrics = ["payoff", "precision", "partner_choice", "stance_accuracy"]
```

When `analysis.auto = true`, the experiment runner should run the configured
analysis after results are saved.

Default analysis output:

```text
results/<hypothesis>/<experiment>/analysis/
  raw/
  figures/
  report/
```

`analysis/raw/` contains generated CSV/JSON tables. `analysis/figures/`
contains generated figures. `analysis/report/` contains generated Markdown or
summary artifacts.

The analysis runner should also be callable independently, so auto-analysis is
convenience rather than the only path.

## Documentation Updates

Update docs in the same implementation pass:

- `README.md`
- `docs/operations/cli.md`
- `docs/experiments/manifest.md`
- `docs/experiment/design.md`
- `docs/experiment/config_schema.md`
- `docs/design/implementation.md`
- `docs/state/current/next_runs.md`

Only update theory interpretation docs, such as `docs/theory/hypotheses.md`, if
the experiment wording changes the computational claim or interpretation.

## Migration Plan

1. Add TOML experiment config dataclasses and parser.
2. Add variant expansion and sweep expansion.
3. Update the trust factory to construct runtimes from explicit variants.
4. Update serial and batch runners to schedule expanded variant replications.
5. Update result row identity fields and metadata.
6. Add the maintained TOML experiment files.
7. Remove old maintained JSON trust configs from the supported tree.
8. Add the analysis configuration block and experiment-level auto-analysis hook.
9. Update docs and script examples.
10. Update tests around config parsing, expansion, runner scheduling, output
    columns, manifest entries, and analysis output paths.

## Verification

Minimum verification after implementation:

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
python scripts/experiment/run.py --config experiments/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name config_redesign_smoke --workers 1 --dry-run
```

Before full current-evidence runs, also follow the verification gate in
`docs/state/current/next_runs.md`.
