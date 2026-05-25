# Experiment Config Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace legacy condition/preset JSON experiment configs with hierarchical TOML experiment specs that run explicit variants, sweeps, and configured analysis outputs.

**Architecture:** Add a new TOML spec layer in `experiments/trust/spec.py` that parses hypothesis/experiment/scenario/variant/sweep/analysis sections and expands them into concrete run specs. Adapt the existing runner, batch scheduler, and factory to consume concrete variant runs while preserving the official `pymdp.Agent` runtime boundary. Keep analysis auto-generation as a thin dispatch hook in the first pass, with hypothesis-specific modules receiving saved result paths and config analysis declarations.

**Tech Stack:** Python 3.10+, `tomllib`/`tomli`, dataclasses, pandas, official `inferactively-pymdp==1.0.0`, pytest, ruff, mypy.

---

## File Structure

- Create: `experiments/trust/spec.py`
  - TOML loading, dataclasses, validation, scenario-to-runtime conversion, variant expansion, sweep expansion.
- Modify: `experiments/trust/config.py`
  - Reduce or bridge `ExperimentConfig` to runtime-only fields during migration. Keep this file as the internal runtime config adapter if that is less disruptive.
- Modify: `experiments/trust/conditions.py`
  - Remove numeric condition taxonomy from the new supported path. Keep only reusable helpers if needed for variant defaults.
- Modify: `experiments/trust/factory.py`
  - Build `NativeTrustRuntime` from explicit variant specs instead of `condition`.
- Modify: `experiments/trust/runner.py`
  - Run concrete variant replications; emit `hypothesis_id`, `experiment_id`, and `variant_id`.
- Modify: `experiments/trust/batch.py`
  - Schedule expanded variant-replication jobs instead of condition-replication jobs.
- Modify: `experiments/trust/tasks.py`
  - Worker payloads should use serialized experiment spec plus expanded run spec.
- Modify: `experiments/trust/calibration.py`
  - Remove old sensitivity helper or replace it with sweep expansion helpers if not housed in `spec.py`.
- Modify: `scripts/experiment/run.py`
  - Accept `.toml`; dry-run manifest reports experiments, variants, sweeps, and replications.
- Modify: `scripts/experiment/inspect.py`
  - Print parsed TOML experiment summary.
- Modify: `scripts/experiment/preliminary.py`
  - Use the new TOML smoke/default experiment.
- Create: `analysis/core/`
  - Shared analysis utilities moved or wrapped from existing `analysis/*.py`.
- Create: `analysis/hypotheses/<hypothesis>/`
  - First-pass hypothesis analysis modules with stable entrypoints.
- Create: `analysis/reports/`
  - Report output helpers.
- Modify: `scripts/analysis/analyze.py`
  - Add config-aware dispatch while keeping direct results analysis usable during migration.
- Create: `experiments/trust/hypotheses/**/*.toml`
  - Maintained H0-H5 experiment specs.
- Delete: old maintained `experiments/trust/configs/*.json` after equivalent TOML specs pass tests.
- Modify docs:
  - `README.md`
  - `docs/operations/cli.md`
  - `docs/experiments/manifest.md`
  - `docs/experiment/design.md`
  - `docs/experiment/config_schema.md`
  - `docs/design/implementation.md`
  - `docs/state/current/next_runs.md`
- Modify tests:
  - `tests/test_experiment_config_schema.py` or equivalent new file.
  - `tests/test_integration.py`
  - `tests/test_experiment_manifest.py`
  - `tests/test_supported_surface.py`
  - `tests/test_package_surface.py`
  - `tests/test_analysis_hypotheses.py`
  - `tests/test_analysis_semantics.py`

## Task 1: Add TOML Spec Parser And Validation

**Files:**
- Create: `experiments/trust/spec.py`
- Test: `tests/test_experiment_config_schema.py`

- [ ] **Step 1: Write failing parser tests**

Create tests for:

```python
def test_loads_hierarchical_toml_spec(tmp_path):
    path = tmp_path / "betrayal_choice.toml"
    path.write_text(
        """
        [hypothesis]
        id = "h3"
        name = "stress_response"

        [experiment]
        id = "betrayal_choice"
        rounds = 120
        replications = 3
        seed = 42

        [scenario]
        payoff = "binary"
        assignment = "agent_choice"
        partners = 4
        type_volatility = 0.0

        [[variants]]
        id = "affect"
        affect = "precision"
        planning_horizon = 4
        """,
        encoding="utf-8",
    )

    spec = ExperimentSpec.from_toml(path)

    assert spec.hypothesis.id == "h3"
    assert spec.experiment.id == "betrayal_choice"
    assert spec.scenario.assignment == "agent_choice"
    assert spec.variants[0].id == "affect"
```

Also test that old public keys fail:

```python
def test_rejects_legacy_condition_keys(tmp_path):
    path = tmp_path / "legacy.toml"
    path.write_text(
        """
        [hypothesis]
        id = "h0"
        name = "openness"

        [experiment]
        id = "legacy"
        rounds = 10
        replications = 1
        seed = 1

        [scenario]
        payoff = "binary"
        assignment = "random"
        partners = 4

        conditions = [1, 2]
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="conditions"):
        ExperimentSpec.from_toml(path)
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_experiment_config_schema.py -q
```

Expected: import or assertion failures because `ExperimentSpec` does not exist.

- [ ] **Step 3: Implement spec dataclasses**

Add dataclasses:

```python
@dataclass(frozen=True)
class HypothesisSpec:
    id: str
    name: str

@dataclass(frozen=True)
class ExperimentMeta:
    id: str
    rounds: int
    replications: int
    seed: int

@dataclass(frozen=True)
class ScenarioSpec:
    payoff: str
    assignment: str
    partners: int = 4
    type_volatility: float = 0.05
    observation_noise: float = 0.0
    partner_types: tuple[str, ...] = PARTNER_TYPE_ORDER
    initial_types: tuple[str, ...] | None = None
    initial_stances: tuple[str, ...] | None = None
    stance_switches: tuple[StanceSwitchSpec, ...] = ()

@dataclass(frozen=True)
class VariantSpec:
    id: str
    affect: str
    planning_horizon: int
    gamma: float = 1.0
    epistemic_value: bool = True
    alpha_charge: float = 3.0
    sigma_0_sq: float = 0.25
    initial_beta: float = 1.0
    beta_persistence: float = 0.8
    beta_levels: tuple[float, ...] = (0.5, 0.67, 1.0, 1.5, 2.0)
    action_selection: str = "marginal"
```

Use `tomllib` with `tomli` fallback:

```python
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
```

- [ ] **Step 4: Add validation**

Reject legacy keys anywhere in parsed TOML:

```python
LEGACY_PUBLIC_KEYS = {
    "conditions",
    "presets",
    "deep_horizon",
    "shallow_horizon",
    "horizon_overrides",
    "lr",
    "use_parameter_learning",
    "learn_A",
    "learn_B",
    "learn_E",
    "pA_scale",
    "pB_scale",
    "lr_E",
    "lesion_mode",
    "run_sensitivity",
    "sensitivity_factors",
    "experiment_name",
    "verbose",
    "verbosity_mode",
    "gif_after_run",
    "gif_output_dir",
}
```

Validate allowed enum values:

```python
payoff in {"binary", "graded"}
assignment in {"random", "agent_choice"}
affect in {"none", "precision", "tracked_only"}
```

- [ ] **Step 5: Run parser tests**

Run:

```bash
python -m pytest tests/test_experiment_config_schema.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit parser**

```bash
git add experiments/trust/spec.py tests/test_experiment_config_schema.py
git commit -m "feat(trust): add experiment spec parser"
```

## Task 2: Add Variant And Sweep Expansion

**Files:**
- Modify: `experiments/trust/spec.py`
- Test: `tests/test_experiment_config_schema.py`

- [ ] **Step 1: Write failing expansion tests**

Test variant expansion without sweeps:

```python
def test_expands_variants_to_runs(example_spec):
    runs = example_spec.expand_runs()

    assert [run.variant_id for run in runs] == ["affect", "affect", "affect"]
    assert [run.seed for run in runs] == [42, 43, 44]
```

Test sweep expansion:

```python
def test_expands_planning_horizon_sweep(tmp_path):
    spec = ExperimentSpec.from_toml(make_h0_sweep_toml(tmp_path))

    runs = spec.expand_runs()
    ids = {run.variant_id for run in runs}

    assert "affect__planning_horizon_1" in ids
    assert "affect__planning_horizon_4" in ids
    assert "no_affect__planning_horizon_1" in ids
```

- [ ] **Step 2: Run tests to verify failure**

```bash
python -m pytest tests/test_experiment_config_schema.py -q
```

Expected: FAIL because `expand_runs()` does not exist.

- [ ] **Step 3: Implement `ExpandedRunSpec`**

Add:

```python
@dataclass(frozen=True)
class ExpandedRunSpec:
    hypothesis_id: str
    experiment_id: str
    variant_id: str
    replication: int
    seed: int
    scenario: ScenarioSpec
    variant: VariantSpec
    analysis: AnalysisSpec
    runtime: RuntimeSpec
```

- [ ] **Step 4: Implement sweep application**

Add `SweepSpec`:

```python
@dataclass(frozen=True)
class SweepSpec:
    parameter: str
    values: tuple[float | int | str | bool, ...]
    applies_to: tuple[str, ...]
```

Implement expansion so a sweep modifies a copy of the base variant and appends
`__{parameter}_{value}` to `variant_id`.

- [ ] **Step 5: Run expansion tests**

```bash
python -m pytest tests/test_experiment_config_schema.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit expansion**

```bash
git add experiments/trust/spec.py tests/test_experiment_config_schema.py
git commit -m "feat(trust): expand variants and sweeps"
```

## Task 3: Bridge Specs To Runtime Config

**Files:**
- Modify: `experiments/trust/spec.py`
- Modify: `experiments/trust/config.py`
- Test: `tests/test_experiment_config_schema.py`
- Test: `tests/test_environment.py`

- [ ] **Step 1: Write failing adapter test**

```python
def test_expanded_run_builds_runtime_config(example_spec):
    run = example_spec.expand_runs()[0]

    cfg = run.to_runtime_config()

    assert cfg.payoff_mode == "binary"
    assert cfg.assignment_mode == "agent_choice"
    assert cfg.num_rounds == 120
    assert cfg.p_switch == 0.0
    assert cfg.gamma == 1.0
    assert cfg.alpha_charge == 3.0
```

- [ ] **Step 2: Run failing adapter test**

```bash
python -m pytest tests/test_experiment_config_schema.py::test_expanded_run_builds_runtime_config -q
```

Expected: FAIL because adapter does not exist.

- [ ] **Step 3: Implement adapter**

Add `ExpandedRunSpec.to_runtime_config()` that returns an `ExperimentConfig`
for environment/POMDP construction. Mapping:

```text
scenario.payoff -> payoff_mode
scenario.assignment -> assignment_mode
scenario.partners -> num_partners
experiment.rounds -> num_rounds
scenario.type_volatility -> p_switch
scenario.observation_noise -> observation_noise
scenario.initial_types -> initial_partner_types
scenario.initial_stances -> initial_partner_stances
scenario.stance_switches -> scheduled_stance_switches
variant.gamma -> gamma
variant.action_selection -> action_sampling
variant.alpha_charge -> alpha_charge
variant.sigma_0_sq -> sigma_0_sq
variant.initial_beta -> initial_beta
variant.beta_persistence -> beta_persistence
runtime.max_policies -> max_policies
```

For `beta_levels`, either add explicit support to `ExperimentConfig` or keep it
on `ExpandedRunSpec` and pass it directly to runtime construction in Task 4.
Prefer explicit support if it keeps the factory simpler.

- [ ] **Step 4: Run adapter tests**

```bash
python -m pytest tests/test_experiment_config_schema.py tests/test_environment.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit adapter**

```bash
git add experiments/trust/spec.py experiments/trust/config.py tests/test_experiment_config_schema.py tests/test_environment.py
git commit -m "feat(trust): map experiment specs to runtime config"
```

## Task 4: Build Runtime From Explicit Variants

**Files:**
- Modify: `experiments/trust/factory.py`
- Modify: `experiments/trust/conditions.py`
- Test: `tests/test_supported_surface.py`
- Test: `tests/test_hesp_agents.py`
- Test: `tests/test_agents.py`

- [ ] **Step 1: Write failing factory tests**

```python
def test_factory_uses_variant_affect_mode(example_run):
    runtime = create_native_runtime_from_run(example_run)

    assert runtime.variant_id == "affect"
    assert runtime.agent_kind == "affective"
    assert runtime.affect_mode == "normal"
    assert runtime.planning_horizon == 4
```

```python
def test_factory_uses_tracked_only_lesion(example_run):
    lesioned = replace(example_run, variant=replace(example_run.variant, id="lesioned", affect="tracked_only"))

    runtime = create_native_runtime_from_run(lesioned)

    assert runtime.affect_mode == "decouple"
```

- [ ] **Step 2: Run failing factory tests**

```bash
python -m pytest tests/test_supported_surface.py tests/test_hesp_agents.py -q
```

Expected: FAIL until new factory function exists.

- [ ] **Step 3: Add `create_native_runtime_from_run`**

Implement a new factory function:

```python
def create_native_runtime_from_run(run: ExpandedRunSpec) -> NativeTrustRuntime:
    config = run.to_runtime_config()
    planning_horizon = int(run.variant.planning_horizon)
    ...
```

Map affect:

```text
none -> agent_kind="base", affect_mode="none", no beta
precision -> agent_kind="affective", affect_mode="normal", beta enabled
tracked_only -> agent_kind="lesioned", affect_mode="decouple", beta enabled
```

Set information gain from `variant.epistemic_value`.

- [ ] **Step 4: Keep old factory temporarily private if needed**

If existing tests still use `create_native_runtime(config, condition, seed)`,
either update those tests immediately or keep the old helper only as a private
test bridge. Do not document numeric conditions as supported.

- [ ] **Step 5: Run factory tests**

```bash
python -m pytest tests/test_supported_surface.py tests/test_hesp_agents.py tests/test_agents.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit factory changes**

```bash
git add experiments/trust/factory.py experiments/trust/conditions.py tests/test_supported_surface.py tests/test_hesp_agents.py tests/test_agents.py
git commit -m "refactor(trust): build runtimes from variants"
```

## Task 5: Update Runner To Variant Runs

**Files:**
- Modify: `experiments/trust/runner.py`
- Modify: `experiments/trust/logger.py`
- Test: `tests/test_integration.py`
- Test: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Write failing runner output test**

```python
def test_runner_outputs_variant_identity(example_spec):
    runner = ExperimentRunner.from_spec(example_spec)
    results = runner.run_all()

    assert {"hypothesis_id", "experiment_id", "variant_id", "replication", "seed", "round"} <= set(results.columns)
    assert "condition" not in results.columns
```

- [ ] **Step 2: Run failing runner test**

```bash
python -m pytest tests/test_integration.py::test_runner_outputs_variant_identity -q
```

Expected: FAIL because runner still schedules conditions.

- [ ] **Step 3: Add spec-aware runner constructor**

Add:

```python
@classmethod
def from_spec(cls, spec: ExperimentSpec) -> ExperimentRunner:
    return cls(spec=spec)
```

If retaining `ExperimentConfig` initialization temporarily, make the constructor
accept exactly one of `config` or `spec`.

- [ ] **Step 4: Replace condition scheduling**

Change `run_all()` to iterate:

```python
for run in self.spec.expand_runs():
    records.extend(self.run_replication(run=run))
```

Change `run_replication()` to accept `run: ExpandedRunSpec` and use
`create_native_runtime_from_run(run)`.

- [ ] **Step 5: Rename row annotations**

Replace `condition_name`, `condition`, and `run_mode` primary assumptions with:

```text
hypothesis_id
experiment_id
variant_id
replication
seed
config_path
batch_id
```

Keep `run_mode` only if sweep/analysis code still needs it; otherwise remove.

- [ ] **Step 6: Run runner tests**

```bash
python -m pytest tests/test_integration.py tests/test_analysis_semantics.py -q
```

Expected: PASS after tests are updated to new vocabulary.

- [ ] **Step 7: Commit runner changes**

```bash
git add experiments/trust/runner.py experiments/trust/logger.py tests/test_integration.py tests/test_analysis_semantics.py
git commit -m "refactor(trust): run variant experiment specs"
```

## Task 6: Update Batch Worker Scheduling

**Files:**
- Modify: `experiments/trust/batch.py`
- Modify: `experiments/trust/tasks.py`
- Modify: `experiments/trust/calibration.py`
- Test: `tests/test_integration.py`

- [ ] **Step 1: Write failing batch dry-run/scheduling test**

```python
def test_batch_schedules_expanded_variant_runs(tmp_path, example_toml_path):
    runner = BatchExperimentRunner(
        config_paths=[str(example_toml_path)],
        output_root=str(tmp_path),
        batch_id="batch",
        workers=1,
    )

    states = runner._load_states()

    assert states[0].spec.experiment.id == "betrayal_choice"
    assert len(states[0].expanded_runs) == 3
```

- [ ] **Step 2: Run failing batch test**

```bash
python -m pytest tests/test_integration.py::test_batch_schedules_expanded_variant_runs -q
```

Expected: FAIL because batch state still loads `ExperimentConfig`.

- [ ] **Step 3: Update batch state**

Replace config-specific fields with:

```python
spec: ExperimentSpec
spec_payload: dict[str, Any]
expanded_runs: list[ExpandedRunSpec]
```

- [ ] **Step 4: Update worker tasks**

Replace `run_primary_replication_task(... condition=...)` with:

```python
def run_variant_replication_task(spec_payload, run_payload, *, config_path, batch_id):
    spec = deserialize_spec(spec_payload)
    run = deserialize_run(run_payload)
    rows = ExperimentRunner.from_spec(spec).run_replication(run=run, ...)
```

- [ ] **Step 5: Remove old sensitivity worker path**

Delete `run_sensitivity_replication_task` from the supported path. Sweeps are
already expanded into normal variant runs.

- [ ] **Step 6: Run batch tests**

```bash
python -m pytest tests/test_integration.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit batch changes**

```bash
git add experiments/trust/batch.py experiments/trust/tasks.py experiments/trust/calibration.py tests/test_integration.py
git commit -m "refactor(trust): schedule expanded variant runs"
```

## Task 7: Update CLI Scripts

**Files:**
- Modify: `scripts/experiment/run.py`
- Modify: `scripts/experiment/inspect.py`
- Modify: `scripts/experiment/preliminary.py`
- Modify: `scripts/experiment/smoke.py`
- Test: `tests/test_supported_surface.py`

- [ ] **Step 1: Write failing CLI dry-run test**

Add or update a test that invokes:

```bash
python scripts/experiment/run.py --config experiments/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir <tmp> --batch-name dry --dry-run
```

Expected manifest fields:

```json
{
  "configs": [
    {
      "hypothesis_id": "h3",
      "experiment_id": "betrayal_choice",
      "variants": ["no_affect", "affect", "lesioned"]
    }
  ]
}
```

- [ ] **Step 2: Run failing CLI test**

```bash
python -m pytest tests/test_supported_surface.py -q
```

Expected: FAIL until CLI loads TOML specs.

- [ ] **Step 3: Update `run.py`**

Replace `ExperimentConfig.from_json` with `ExperimentSpec.from_toml`.

Dry-run manifest should include:

```text
hypothesis_id
experiment_id
rounds
replications
variants
expanded_runs
analysis_auto
```

- [ ] **Step 4: Update `inspect.py`**

Print compact JSON summary:

```text
config
hypothesis
experiment
scenario
variants
sweeps
replications
expanded_runs
analysis
```

- [ ] **Step 5: Update preliminary/smoke defaults**

Point smoke/preliminary scripts to a new TOML smoke experiment, not old JSON.

- [ ] **Step 6: Run CLI tests**

```bash
python -m pytest tests/test_supported_surface.py -q
python scripts/experiment/run.py --config experiments/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name config_redesign_dry --dry-run
```

Expected: PASS and dry-run manifest written.

- [ ] **Step 7: Commit CLI changes**

```bash
git add scripts/experiment/run.py scripts/experiment/inspect.py scripts/experiment/preliminary.py scripts/experiment/smoke.py tests/test_supported_surface.py
git commit -m "refactor(cli): load TOML experiment specs"
```

## Task 8: Add Maintained TOML Experiments

**Files:**
- Create: `experiments/trust/hypotheses/h0_openness/shallow_binary.toml`
- Create: `experiments/trust/hypotheses/h0_openness/graded_choice.toml`
- Create: `experiments/trust/hypotheses/h0_openness/graded_betrayal.toml`
- Create: `experiments/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml`
- Create: `experiments/trust/hypotheses/h2_deployment/lesion_open_regime.toml`
- Create: `experiments/trust/hypotheses/h3_stress_response/betrayal_choice.toml`
- Create: `experiments/trust/hypotheses/h4_social_choice/partner_choice.toml`
- Create: `experiments/trust/hypotheses/h5_perturbation/clinical_betrayal.toml`
- Create: `experiments/trust/hypotheses/h5_perturbation/clinical_dynamics.toml`
- Create: `experiments/trust/hypotheses/h5_perturbation/affect_sensitivity.toml`
- Create: `experiments/trust/hypotheses/smoke/smoke.toml`
- Delete: old maintained `experiments/trust/configs/*.json`
- Test: `tests/test_experiment_manifest.py`

- [ ] **Step 1: Write manifest/config presence tests**

```python
def test_core_hypothesis_experiments_exist():
    expected = [
        "experiments/trust/hypotheses/h0_openness/shallow_binary.toml",
        ...
    ]
    for path in expected:
        assert Path(path).exists()
        ExperimentSpec.from_toml(path)
```

- [ ] **Step 2: Run failing manifest test**

```bash
python -m pytest tests/test_experiment_manifest.py -q
```

Expected: FAIL until TOML files exist.

- [ ] **Step 3: Create TOML files**

Use the old maintained JSON configs as source material, but remove legacy keys.
Use explicit variants. For H0 horizon tests, use a sweep:

```toml
[[variants]]
id = "no_affect"
affect = "none"
planning_horizon = 1

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 1

[[sweeps]]
parameter = "planning_horizon"
values = [1, 2, 3]
applies_to = ["no_affect", "affect"]
```

- [ ] **Step 4: Delete old maintained JSON configs**

Remove only supported trust experiment JSON configs after TOML equivalents pass.
Do not delete benchmark JSON configs under root `configs/`.

- [ ] **Step 5: Run manifest tests**

```bash
python -m pytest tests/test_experiment_manifest.py tests/test_experiment_config_schema.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit TOML configs**

```bash
git add experiments/trust/hypotheses tests/test_experiment_manifest.py
git rm experiments/trust/configs/*.json
git commit -m "refactor(experiments): replace trust JSON configs"
```

## Task 9: Add Configured Analysis Dispatch

**Files:**
- Create: `analysis/core/__init__.py`
- Create: `analysis/core/loading.py`
- Create: `analysis/core/windows.py`
- Create: `analysis/hypotheses/h0_openness/analyze.py`
- Create: `analysis/hypotheses/h1_model_fitness/analyze.py`
- Create: `analysis/hypotheses/h2_deployment/analyze.py`
- Create: `analysis/hypotheses/h3_stress_response/analyze.py`
- Create: `analysis/hypotheses/h4_social_choice/analyze.py`
- Create: `analysis/hypotheses/h5_perturbation/analyze.py`
- Create: `analysis/reports/render.py`
- Modify: `scripts/analysis/analyze.py`
- Modify: `experiments/trust/runner.py` or `scripts/experiment/run.py`
- Test: `tests/test_analysis_hypotheses.py`
- Test: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Write failing analysis dispatch test**

```python
def test_auto_analysis_writes_raw_outputs(tmp_path, example_results, example_spec):
    output_dir = tmp_path / "results" / "h3" / "betrayal_choice"
    output_dir.mkdir(parents=True)
    results_path = output_dir / "results.csv"
    example_results.to_csv(results_path, index=False)

    run_configured_analysis(example_spec, results_path, output_dir)

    assert (output_dir / "analysis" / "raw").exists()
    assert (output_dir / "analysis" / "figures").exists()
    assert (output_dir / "analysis" / "report").exists()
```

- [ ] **Step 2: Run failing analysis test**

```bash
python -m pytest tests/test_analysis_hypotheses.py::test_auto_analysis_writes_raw_outputs -q
```

Expected: FAIL because dispatcher does not exist.

- [ ] **Step 3: Add analysis dispatcher**

Implement a small dispatcher:

```python
def run_configured_analysis(spec: ExperimentSpec, results_path: Path, output_dir: Path) -> None:
    if not spec.analysis.auto:
        return
    module = importlib.import_module(f"analysis.hypotheses.{spec.analysis.primary}.analyze")
    module.run(results_path=results_path, output_dir=output_dir / "analysis", analysis=spec.analysis)
```

If `primary` names include `h3_stress_response`, ensure folders match that
string.

- [ ] **Step 4: Add first-pass hypothesis modules**

Each module can initially call shared existing analysis helpers and write at
least:

```text
analysis/raw/final_round_summary.csv
analysis/raw/hypothesis_tests.json
analysis/report/summary.md
```

Keep figure generation if existing helpers make it straightforward; otherwise
create directories and leave figure generation to a follow-up analysis refactor.

- [ ] **Step 5: Hook auto-analysis after save**

After `results.csv` is saved in CLI or runner, if `spec.analysis.auto` is true,
invoke `run_configured_analysis`.

- [ ] **Step 6: Run analysis tests**

```bash
python -m pytest tests/test_analysis_hypotheses.py tests/test_analysis_semantics.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit analysis dispatch**

```bash
git add analysis scripts/analysis/analyze.py experiments/trust/runner.py tests/test_analysis_hypotheses.py tests/test_analysis_semantics.py
git commit -m "feat(analysis): dispatch configured analyses"
```

## Task 10: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/operations/cli.md`
- Modify: `docs/experiments/manifest.md`
- Modify: `docs/experiment/design.md`
- Create: `docs/experiment/config_schema.md`
- Modify: `docs/design/implementation.md`
- Modify: `docs/state/current/next_runs.md`
- Test: `tests/test_supported_surface.py`
- Test: `tests/test_experiment_manifest.py`

- [ ] **Step 1: Update README commands**

Replace old JSON examples with TOML examples:

```bash
python scripts/experiment/run.py --config experiments/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --workers 12
```

- [ ] **Step 2: Update CLI contract**

Document:

```text
--config accepts TOML experiment specs
one config = one experiment
output path = results/<hypothesis>/<experiment>/
analysis.auto behavior
```

- [ ] **Step 3: Update manifest**

Map H0-H5 to the ten maintained TOML files.

- [ ] **Step 4: Add config schema doc**

Create `docs/experiment/config_schema.md` with:

```text
hypothesis
experiment
scenario
variants
sweeps
runtime
analysis
replication
episode
round
```

- [ ] **Step 5: Update implementation docs**

Document runner expansion:

```text
experiment x variants x sweeps x replications
```

Document analysis output folders.

- [ ] **Step 6: Update next runs**

Replace all old JSON paths with TOML paths and remove old condition framing.

- [ ] **Step 7: Run docs-related tests**

```bash
python -m pytest tests/test_supported_surface.py tests/test_experiment_manifest.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit docs**

```bash
git add README.md docs tests/test_supported_surface.py tests/test_experiment_manifest.py
git commit -m "docs: document TOML experiment workflow"
```

## Task 11: Final Verification And Cleanup

**Files:**
- Any files touched above.

- [ ] **Step 1: Run focused tests**

```bash
python -m pytest tests/test_experiment_config_schema.py tests/test_integration.py tests/test_experiment_manifest.py tests/test_analysis_hypotheses.py -q
```

Expected: PASS.

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest tests/ -q
```

Expected: PASS.

- [ ] **Step 3: Run lint/type checks**

```bash
python -m ruff check .
python -m mypy
git diff --check
```

Expected: all pass.

- [ ] **Step 4: Run CLI dry run**

```bash
python scripts/experiment/run.py --config experiments/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name config_redesign_smoke --workers 1 --dry-run
```

Expected: manifest written with `hypothesis_id`, `experiment_id`, variants,
expanded run count, and `analysis_auto`.

- [ ] **Step 5: Run tiny smoke experiment**

```bash
python scripts/experiment/run.py --config experiments/trust/hypotheses/smoke/smoke.toml --output-dir results --batch-name config_redesign_smoke --workers 1
```

Expected:

```text
results/config_redesign_smoke/smoke/results.csv
results/config_redesign_smoke/smoke/config.toml
results/config_redesign_smoke/smoke/metadata.json
results/config_redesign_smoke/smoke/analysis/
```

If the finalized output layout chooses `results/<hypothesis>/<experiment>/`
without `batch_name`, update this expected path before executing the task.

- [ ] **Step 6: Inspect output columns**

Run:

```bash
python - <<'PY'
import pandas as pd
path = "results/config_redesign_smoke/smoke/results.csv"
df = pd.read_csv(path, nrows=1)
print(df.columns.tolist())
PY
```

Expected columns include:

```text
hypothesis_id
experiment_id
variant_id
replication
seed
round
```

Expected columns do not include:

```text
condition
condition_name
```

- [ ] **Step 7: Commit final cleanup if needed**

```bash
git status --short
git add <remaining intended files>
git commit -m "chore: finalize experiment config redesign"
```

Only commit if there are intended cleanup changes left after the task commits.

## Risk Notes

- The existing worktree may contain unrelated changes. Do not revert or stage
  files outside this plan unless they are intentionally part of the refactor.
- Analysis currently expects `condition` in several places. Update analysis
  tests early when changing result identity fields.
- Batch scheduling uses process-safe serialized payloads. Keep payloads plain
  dictionaries or JSON/TOML-compatible values.
- Result interpretation docs must not be updated from new experiment outputs
  without explicit user approval.
- Do not add orchestration scripts. Remote execution remains Mango-owned.
