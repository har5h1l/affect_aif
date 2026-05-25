# Unified Experiment Config Families

## Summary

Extend the TOML experiment-spec system so benchmarks become another experiment
family inside the same public config structure rather than a separate JSON
configuration world.

The trust hypothesis redesign already established the right shape:

```text
hypothesis -> experiment -> scenario -> variants -> sweeps -> replications -> rounds
```

This follow-up keeps that shape. Benchmark-specific settings are nested add-on
knobs inside the normal `ExperimentSpec`, not a separate public schema that
users must learn.

## Goals

- Use one public config root: `configs/`.
- Use one public file format for runnable experiments: TOML.
- Keep the existing clean hypothesis TOML structure and extend it, rather than
  undoing it.
- Treat benchmark as `experiment.family = "benchmark"`.
- Keep benchmark knobs explicit and hierarchical under `[benchmark]`.
- Remove root-level benchmark JSON configs after equivalent TOML specs pass.
- Preserve internal adapters where useful, but do not expose benchmark as a
  separate public config system.

## Non-Goals

- Do not bring back numeric trust conditions, presets, or flat legacy knobs.
- Do not collapse every family into identical semantics when the runtime needs
  family-specific fields.
- Do not reinterpret results or update evidence narratives from new runs.
- Do not add Mango/orchestration scripts.

## Config Layout

All runnable experiment configs should live under `configs/`:

```text
configs/
  trust/
    hypotheses/
      h0_openness/
      h1_model_fitness/
      h2_deployment/
      h3_stress_response/
      h4_social_choice/
      h5_perturbation/
    smoke/
      smoke.toml
  benchmark/
    e1_arena/
      default.toml
      betrayal.toml
      full.toml
    cvc/
      local_smoke.toml
      comparison.toml
      full.toml
    smoke/
      smoke.toml
  multifocal/
    e2_descriptive/
    smoke/
      smoke.toml
```

The exact benchmark filenames can be adjusted during implementation, but the
principle is fixed: no primary runnable configs should remain as loose files at
repo-root `configs/`.

## Shared Spec Envelope

Every runnable config uses the same top-level spine:

```toml
[hypothesis]
id = "e1"
name = "benchmark_arena"

[experiment]
id = "trust_arena_default"
family = "benchmark"
rounds = 100
replications = 10
seed = 42

[scenario]
payoff = "binary"
assignment = "agent_choice"

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 4

[analysis]
auto = true
primary = "e1_benchmark_arena"
```

`family` controls which runner adapter executes the expanded runs. Trust-family
configs continue to work like the current TOML hypothesis specs, except their
path moves under `configs/trust/`.

## Benchmark Add-On Section

Benchmark settings live inside the same `ExperimentSpec` as a namespaced
section:

```toml
[benchmark]
backends = ["trust"]
agents = ["affect", "no_affect", "random", "tit_for_tat"]

[benchmark.trust]
scenario = "resource_sharing"

[benchmark.cvc_local]
mission = "machina_1"
num_agents = 8
max_steps = 1000
python_bin = "python3.12"

[benchmark.observatory]
season = "default"
pool = "default"
```

Implementation may represent this as a nested dataclass or typed section for
validation, but conceptually it is not a separate public config. It is just the
benchmark add-on inside `ExperimentSpec`.

## Data Flow

```text
ExperimentSpec.from_toml(path)
  -> parse shared envelope
  -> parse optional family add-ons
  -> expand variants/sweeps/replications
  -> dispatch by experiment.family
       trust      -> ExperimentRunner
       benchmark  -> BenchmarkRunner adapter
       multifocal -> future MultiFocal adapter
```

Benchmark execution can keep internal `BenchmarkConfig`-like adapters if that
keeps existing benchmark code simple. Those adapters should be constructed from
the unified TOML spec and should not remain the public authored config surface.

## Validation Rules

- Trust configs reject legacy keys already rejected by the current spec parser.
- Benchmark configs reject old JSON-only public shapes once TOML equivalents
  exist.
- `[benchmark]` is required when `experiment.family = "benchmark"`.
- `[benchmark]` is invalid for trust-family specs unless explicitly allowed by
  a future design.
- Benchmark agents must be explicit strings or structured agent declarations.
- CvC knobs stay under `[benchmark.cvc_local]`; trust benchmark knobs stay under
  `[benchmark.trust]`.

## Migration Plan

1. Move current trust TOMLs from `experiments/trust/hypotheses/` to
   `configs/trust/hypotheses/` and update docs/tests/CLI paths.
2. Add `family = "trust"` to trust specs, or default missing family to `trust`
   for one migration window.
3. Add optional benchmark section parsing to `ExperimentSpec`.
4. Convert root `configs/benchmark*.json` files to hierarchical TOML under
   `configs/benchmark/`.
5. Update benchmark CLI to load unified TOML specs and build internal benchmark
   runtime adapters.
6. Delete root benchmark JSON configs after TOML equivalents pass tests.
7. Update manifests and docs so every runnable config is discoverable under
   `configs/`.

## Testing

- Parser tests for `family = "benchmark"` with `[benchmark]`.
- Validation tests that benchmark family requires benchmark settings.
- Manifest tests that no runnable benchmark JSON remains in root `configs/`.
- CLI dry-run tests for both trust and benchmark TOML specs.
- Smoke benchmark run using `configs/benchmark/smoke/smoke.toml`.
- Full test suite plus `ruff`, `mypy`, and `git diff --check`.

## Open Questions

- Should `family` be required immediately for trust specs, or should missing
  family default to `trust` during migration?
- Should benchmark variants reuse trust `[[variants]]` exactly, or should agent
  comparisons live only under `[benchmark.agents]` when they are non-AIF
  policies?
- Should multifocal be included in this implementation pass, or left as a
  documented next family after trust and benchmark are unified?
