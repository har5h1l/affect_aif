# Unified Experiment Config Families Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move trust, benchmark, and eventually multifocal runnable configs into one TOML-first `ExperimentSpec` family system rooted under `configs/`.

**Architecture:** Keep the current trust TOML schema as the canonical shared envelope. Add `experiment.family` and optional family add-on sections, starting with `[benchmark]`, so benchmark configs become normal experiment specs rather than a separate public JSON config surface. Existing benchmark code may keep internal adapter dataclasses, but authored configs and CLI entrypoints should load unified TOML specs.

**Tech Stack:** Python 3.10+, `tomllib`/`tomli`, dataclasses, pandas, pytest, ruff, mypy, official `inferactively-pymdp==1.0.0`.

---

## Starting Point

This plan assumes the current `codex/experiment-config-redesign` worktree already has:

- `experiments/trust/spec.py` parsing trust TOML specs.
- Trust specs under `experiments/trust/hypotheses/**/*.toml`.
- Old maintained trust JSON configs deleted from `experiments/trust/configs/`.
- Benchmark configs still authored as root `configs/benchmark*.json`.
- Benchmark runtime still using `benchmarks.core.benchmark_config.BenchmarkConfig` internally.

Do not undo the trust cleanup. This plan brings benchmark into the same public config discipline.

## File Structure

- Modify: `experiments/trust/spec.py`
  - Add `ExperimentMeta.family`.
  - Add nested `BenchmarkSettings` / benchmark section fields inside `ExperimentSpec`.
  - Validate family-specific section presence.
- Modify: `benchmarks/core/benchmark_config.py`
  - Keep as internal adapter only.
  - Add construction from unified `ExperimentSpec`.
- Modify: `scripts/experiment/run.py`
  - Load config paths from new `configs/trust/...` paths.
  - Dispatch by `spec.experiment.family`.
- Modify: `scripts/benchmark/run_cvc.py`
  - Load unified TOML `ExperimentSpec`.
  - Build internal benchmark adapter from `spec.benchmark`.
- Modify: `scripts/experiment/inspect.py`
  - Print family and benchmark add-on summary.
- Modify: `scripts/experiment/preliminary.py`
  - Point default trust config to `configs/trust/...`.
- Modify: `scripts/experiment/smoke.py`
  - Point default trust smoke config to `configs/trust/smoke/smoke.toml`.
- Create/move: `configs/trust/hypotheses/**/*.toml`
  - Move existing trust TOMLs here.
- Create: `configs/trust/smoke/smoke.toml`
  - Move existing trust smoke TOML here.
- Create: `configs/benchmark/**/*.toml`
  - Convert root benchmark JSON configs to unified TOML specs.
- Delete: `configs/benchmark*.json`
  - Only after TOML equivalents parse and benchmark smoke passes.
- Modify: `docs/experiment/config_schema.md`
- Modify: `docs/operations/cli.md`
- Modify: `docs/operations/benchmark.md`
- Modify: `docs/experiments/manifest.md`
- Modify: `docs/state/current/next_runs.md`
- Modify: `README.md`
- Test: `tests/test_experiment_config_schema.py`
- Test: `tests/test_experiment_manifest.py`
- Test: `tests/test_benchmark_config.py`
- Test: `tests/test_supported_surface.py`
- Test: `tests/test_scripts_smoke.py`
- Test: `tests/test_benchmark_runner.py`

## Task 1: Add Family And Benchmark Parsing Tests

**Files:**
- Modify: `tests/test_experiment_config_schema.py`
- Modify: `tests/experiment_spec_helpers.py`

- [ ] **Step 1: Write failing test for `experiment.family`**

Add a test that writes a minimal trust spec with:

```toml
[experiment]
id = "family_trust"
family = "trust"
rounds = 2
replications = 1
seed = 1
```

Expected assertion:

```python
spec = ExperimentSpec.from_toml(path)
assert spec.experiment.family == "trust"
```

- [ ] **Step 2: Write failing test for benchmark add-on parsing**

Add a TOML fixture:

```toml
[hypothesis]
id = "e1"
name = "benchmark_arena"

[experiment]
id = "benchmark_smoke"
family = "benchmark"
rounds = 2
replications = 1
seed = 7

[scenario]
payoff = "binary"
assignment = "random"
partners = 2

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 1

[benchmark]
backends = ["trust"]
agents = ["affect", "random"]

[benchmark.trust]
scenario = "resource_sharing"
```

Expected assertions:

```python
spec = ExperimentSpec.from_toml(path)
assert spec.experiment.family == "benchmark"
assert spec.benchmark is not None
assert spec.benchmark.backends == ("trust",)
assert spec.benchmark.agents == ("affect", "random")
assert spec.benchmark.trust["scenario"] == "resource_sharing"
```

- [ ] **Step 3: Write failing validation tests**

Add tests:

```python
def test_benchmark_family_requires_benchmark_section(tmp_path):
    path = write_benchmark_toml(tmp_path / "missing.toml", include_benchmark=False)
    with pytest.raises(ValueError, match="benchmark"):
        ExperimentSpec.from_toml(path)
```

```python
def test_trust_family_rejects_benchmark_section(tmp_path):
    path = write_trust_toml(tmp_path / "trust.toml", benchmark_section=True)
    with pytest.raises(ValueError, match="benchmark"):
        ExperimentSpec.from_toml(path)
```

- [ ] **Step 4: Run tests to verify RED**

Run:

```bash
python -m pytest tests/test_experiment_config_schema.py -q
```

Expected: FAIL because `ExperimentMeta.family` and `ExperimentSpec.benchmark` do not exist yet.

- [ ] **Step 5: Commit tests**

Do not commit yet if the repo policy requires green commits. Otherwise, defer commit until Task 2 green.

## Task 2: Implement Family And Benchmark Section In `ExperimentSpec`

**Files:**
- Modify: `experiments/trust/spec.py`
- Test: `tests/test_experiment_config_schema.py`

- [ ] **Step 1: Add family field**

Modify `ExperimentMeta`:

```python
@dataclass(frozen=True)
class ExperimentMeta:
    id: str
    rounds: int
    replications: int
    seed: int
    family: str = "trust"
```

Allowed values:

```python
FAMILY_VALUES = {"trust", "benchmark", "multifocal"}
```

- [ ] **Step 2: Add benchmark section dataclass inside spec module**

Add:

```python
@dataclass(frozen=True)
class BenchmarkSettings:
    backends: tuple[str, ...]
    agents: tuple[str | dict[str, Any], ...]
    trust: dict[str, Any]
    cvc_local: dict[str, Any]
    observatory: dict[str, Any] | None = None
```

This is not a separate public config system. It is a typed nested section on `ExperimentSpec`.

- [ ] **Step 3: Add field to `ExperimentSpec`**

```python
benchmark: BenchmarkSettings | None = None
```

- [ ] **Step 4: Parse benchmark section**

Implement:

```python
def _parse_benchmark(data: dict[str, Any] | None) -> BenchmarkSettings | None:
    if data is None:
        return None
    raw = dict(data)
    return BenchmarkSettings(
        backends=tuple(str(item) for item in raw.get("backends", ())),
        agents=tuple(raw.get("agents", ())),
        trust=dict(raw.get("trust", {})),
        cvc_local=dict(raw.get("cvc_local", {})),
        observatory=None if raw.get("observatory") is None else dict(raw["observatory"]),
    )
```

- [ ] **Step 5: Add validation**

Rules:

```python
if experiment.family not in FAMILY_VALUES:
    raise ValueError(...)
if experiment.family == "benchmark" and benchmark is None:
    raise ValueError("benchmark family requires [benchmark]")
if experiment.family == "trust" and benchmark is not None:
    raise ValueError("trust family does not accept [benchmark]")
```

- [ ] **Step 6: Update payload serialization**

Update `to_payload()` / `from_payload()` to preserve `family` and nested benchmark settings.

- [ ] **Step 7: Run parser tests**

Run:

```bash
python -m pytest tests/test_experiment_config_schema.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit parser changes**

```bash
git add experiments/trust/spec.py tests/test_experiment_config_schema.py tests/experiment_spec_helpers.py
git commit -m "feat(config): add experiment families"
```

## Task 3: Move Trust Specs Under Unified `configs/`

**Files:**
- Move: `experiments/trust/hypotheses/**/*.toml` -> `configs/trust/hypotheses/**/*.toml`
- Move: `experiments/trust/hypotheses/smoke/smoke.toml` -> `configs/trust/smoke/smoke.toml`
- Modify: `tests/test_experiment_manifest.py`
- Modify: `tests/test_supported_surface.py`
- Modify: `tests/test_scripts_smoke.py`
- Modify: `tests/conftest.py`
- Modify: `tests/experiment_spec_helpers.py`

- [ ] **Step 1: Write failing path tests**

Update manifest tests to assert expected trust specs under:

```python
expected = [
    "configs/trust/hypotheses/h0_openness/shallow_binary.toml",
    "configs/trust/hypotheses/h0_openness/graded_choice.toml",
    "configs/trust/hypotheses/h0_openness/graded_betrayal.toml",
    ...
    "configs/trust/smoke/smoke.toml",
]
```

Also assert old path is gone:

```python
assert not Path("experiments/trust/hypotheses").exists()
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
python -m pytest tests/test_experiment_manifest.py tests/test_supported_surface.py tests/test_scripts_smoke.py -q
```

Expected: FAIL because files still live under `experiments/trust/hypotheses/`.

- [ ] **Step 3: Move files**

Use `git mv`:

```bash
mkdir -p configs/trust
git mv experiments/trust/hypotheses configs/trust/hypotheses
mkdir -p configs/trust/smoke
git mv configs/trust/hypotheses/smoke/smoke.toml configs/trust/smoke/smoke.toml
rmdir configs/trust/hypotheses/smoke
```

- [ ] **Step 4: Add `family = "trust"` to trust specs**

For every trust TOML, add:

```toml
[experiment]
id = "..."
family = "trust"
rounds = ...
```

If implementation chooses a migration default instead, still prefer writing `family = "trust"` explicitly in maintained configs.

- [ ] **Step 5: Update tests and fixtures**

Replace old paths:

```text
experiments/trust/hypotheses/
```

with:

```text
configs/trust/hypotheses/
```

and:

```text
experiments/trust/hypotheses/smoke/smoke.toml
```

with:

```text
configs/trust/smoke/smoke.toml
```

- [ ] **Step 6: Run path tests**

Run:

```bash
python -m pytest tests/test_experiment_manifest.py tests/test_supported_surface.py tests/test_scripts_smoke.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit trust config move**

```bash
git add configs/trust tests
git rm -r experiments/trust/hypotheses
git commit -m "refactor(config): move trust specs under configs"
```

## Task 4: Convert Benchmark JSONs To Unified TOML Specs

**Files:**
- Create: `configs/benchmark/e1_arena/default.toml`
- Create: `configs/benchmark/e1_arena/betrayal.toml`
- Create: `configs/benchmark/e1_arena/full.toml`
- Create: `configs/benchmark/cvc/local_smoke.toml`
- Create: `configs/benchmark/cvc/comparison.toml`
- Create: `configs/benchmark/cvc/full.toml`
- Create: any remaining TOML equivalents needed for current `configs/benchmark*.json`
- Modify: `tests/test_benchmark_config.py`
- Modify: `tests/test_experiment_manifest.py`

- [ ] **Step 1: Write failing benchmark manifest test**

Add:

```python
def test_benchmark_configs_are_unified_toml_specs():
    paths = sorted(Path("configs/benchmark").glob("**/*.toml"))
    assert paths
    for path in paths:
        spec = ExperimentSpec.from_toml(path)
        assert spec.experiment.family == "benchmark"
        assert spec.benchmark is not None
```

Add:

```python
def test_no_root_benchmark_json_configs_remain():
    assert not sorted(Path("configs").glob("benchmark*.json"))
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
python -m pytest tests/test_benchmark_config.py tests/test_experiment_manifest.py -q
```

Expected: FAIL because TOML benchmark specs do not exist and root JSONs still exist.

- [ ] **Step 3: Convert each JSON to unified TOML**

For each root JSON, create a TOML with shared envelope plus `[benchmark]`.

Example for default trust arena:

```toml
[hypothesis]
id = "e1"
name = "benchmark_arena"

[experiment]
id = "benchmark_default"
family = "benchmark"
rounds = 100
replications = 10
seed = 42

[scenario]
payoff = "binary"
assignment = "random"
partners = 4

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 4

[analysis]
auto = false
primary = "e1_benchmark_arena"

[benchmark]
backends = ["trust"]
agents = ["affect", "no_affect", "random", "tit_for_tat"]

[benchmark.trust]
scenario = "resource_sharing"
```

For CvC configs, use:

```toml
[benchmark]
backends = ["cvc_local"]
agents = [
  "teammate_reliability",
  "starter",
]

[benchmark.cvc_local]
mission = "machina_1"
num_agents = 8
max_steps = 1000
python_bin = "python3.12"
```

- [ ] **Step 4: Keep agent declaration shape explicit where needed**

If a JSON config uses structured agents, represent them as array tables:

```toml
[[benchmark.agent_specs]]
name = "teammate_reliability"
backend = "cvc_local"
kind = "policy_spec"
policy_spec = "class=benchmarks.cvc.policy.TeammateReliabilityPolicy"
```

If this is added, update `BenchmarkSettings` parsing from Task 2 to include `agent_specs`.

- [ ] **Step 5: Delete old root JSON benchmark configs**

Use:

```bash
git rm configs/benchmark*.json
```

- [ ] **Step 6: Run benchmark config tests**

Run:

```bash
python -m pytest tests/test_benchmark_config.py tests/test_experiment_manifest.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit benchmark config conversion**

```bash
git add configs/benchmark tests/test_benchmark_config.py tests/test_experiment_manifest.py
git commit -m "refactor(config): convert benchmark configs to unified TOML"
```

## Task 5: Build Benchmark Internal Adapter From `ExperimentSpec`

**Files:**
- Modify: `benchmarks/core/benchmark_config.py`
- Modify: `tests/test_benchmark_config.py`

- [ ] **Step 1: Write failing adapter test**

Add:

```python
def test_benchmark_config_builds_from_experiment_spec():
    spec = ExperimentSpec.from_toml("configs/benchmark/e1_arena/default.toml")

    config = BenchmarkConfig.from_experiment_spec(spec)

    assert config.backends == ["trust"]
    assert [agent.name for agent in config.agents]
    assert config.num_rounds == spec.experiment.rounds
    assert config.num_replications == spec.experiment.replications
    assert config.random_seed == spec.experiment.seed
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
python -m pytest tests/test_benchmark_config.py::test_benchmark_config_builds_from_experiment_spec -q
```

Expected: FAIL because `from_experiment_spec` does not exist.

- [ ] **Step 3: Implement adapter**

Add:

```python
@classmethod
def from_experiment_spec(cls, spec: ExperimentSpec) -> BenchmarkConfig:
    if spec.experiment.family != "benchmark" or spec.benchmark is None:
        raise ValueError("BenchmarkConfig requires a benchmark ExperimentSpec")
    payload = {
        "backends": list(spec.benchmark.backends),
        "agents": list(spec.benchmark.agent_specs or spec.benchmark.agents),
        "num_replications": spec.experiment.replications,
        "num_rounds": spec.experiment.rounds,
        "output_dir": f"results/{spec.hypothesis.id}/{spec.experiment.id}",
        "random_seed": spec.experiment.seed,
        "backend_configs": {},
    }
    if spec.benchmark.trust:
        payload["backend_configs"]["trust"] = spec.benchmark.trust
    if spec.benchmark.cvc_local:
        payload["backend_configs"]["cvc_local"] = spec.benchmark.cvc_local
    if spec.benchmark.observatory:
        payload["observatory"] = spec.benchmark.observatory
    return cls.from_dict(payload)
```

Adjust exact field names to match Task 2.

- [ ] **Step 4: Keep JSON compatibility only if needed by tests during transition**

After Task 4 deletes root JSON configs, remove public `from_json` / `to_json` if no supported caller uses them.

- [ ] **Step 5: Run benchmark adapter tests**

Run:

```bash
python -m pytest tests/test_benchmark_config.py tests/test_benchmark_runner.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit adapter**

```bash
git add benchmarks/core/benchmark_config.py tests/test_benchmark_config.py tests/test_benchmark_runner.py
git commit -m "refactor(benchmark): adapt unified experiment specs"
```

## Task 6: Update Benchmark CLI To Unified TOML

**Files:**
- Modify: `scripts/benchmark/run_cvc.py`
- Modify: `tests/test_supported_surface.py`
- Modify: `tests/test_scripts_smoke.py`

- [ ] **Step 1: Write failing CLI test**

Update benchmark CLI test to call:

```bash
python scripts/benchmark/run_cvc.py --config configs/benchmark/smoke/smoke.toml
```

Expected resolved output:

```text
benchmark_results.csv
benchmark_config.resolved.toml
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
python -m pytest tests/test_supported_surface.py::test_benchmark_cli_uses_unified_toml_configs -q
```

Expected: FAIL because CLI still accepts JSON/TOML via old `BenchmarkConfig`.

- [ ] **Step 3: Update CLI load path**

Change:

```python
config = BenchmarkConfig.from_json(...) or BenchmarkConfig.from_toml(...)
```

to:

```python
spec = ExperimentSpec.from_toml(args.config)
config = BenchmarkConfig.from_experiment_spec(spec)
```

Validate:

```python
if spec.experiment.family != "benchmark":
    parser.error("--config must point to a benchmark-family TOML spec")
```

- [ ] **Step 4: Write resolved TOML**

After run, write:

```python
resolved_path = Path(config.output_dir) / "benchmark_config.resolved.toml"
Path(resolved_path).write_text(Path(args.config).read_text(encoding="utf-8"), encoding="utf-8")
```

If a fully resolved dump is preferable, add `ExperimentSpec.to_toml()` in a later task. Do not hand-roll complex serialization unless necessary.

- [ ] **Step 5: Run CLI tests**

Run:

```bash
python -m pytest tests/test_supported_surface.py tests/test_scripts_smoke.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit CLI changes**

```bash
git add scripts/benchmark/run_cvc.py tests/test_supported_surface.py tests/test_scripts_smoke.py
git commit -m "refactor(cli): run benchmarks from experiment specs"
```

## Task 7: Dispatch Experiment CLI By Family

**Files:**
- Modify: `scripts/experiment/run.py`
- Modify: `scripts/experiment/inspect.py`
- Modify: `experiments/trust/batch.py`
- Test: `tests/test_supported_surface.py`
- Test: `tests/test_integration.py`

- [ ] **Step 1: Write failing dry-run test for mixed families**

Add test invoking:

```bash
python scripts/experiment/run.py \
  --config configs/trust/smoke/smoke.toml \
  --config configs/benchmark/smoke/smoke.toml \
  --output-dir <tmp> \
  --batch-name dry \
  --dry-run
```

Expected manifest entries include:

```json
{"family": "trust", "experiment_id": "smoke"}
{"family": "benchmark", "experiment_id": "benchmark_smoke"}
```

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
python -m pytest tests/test_supported_surface.py::test_experiment_run_dry_run_reports_families -q
```

Expected: FAIL until manifest includes `family`.

- [ ] **Step 3: Update dry-run manifest**

Add:

```python
"family": spec.experiment.family
```

to each config entry.

- [ ] **Step 4: Decide execution dispatch boundary**

For this implementation pass, keep actual benchmark execution in `scripts/benchmark/run_cvc.py` unless user approves full unified execution. `scripts/experiment/run.py` may accept benchmark configs for dry-run/inspect only and raise a clear error for execution:

```python
if spec.experiment.family != "trust":
    parser.error("Only trust-family specs are executable through scripts/experiment/run.py; use scripts/benchmark/run_cvc.py for benchmark-family specs.")
```

This keeps scope small while unifying schema and placement.

- [ ] **Step 5: Update inspect output**

Print:

```json
{
  "family": "benchmark",
  "benchmark": {
    "backends": [...],
    "agents": [...]
  }
}
```

- [ ] **Step 6: Run CLI tests**

Run:

```bash
python -m pytest tests/test_supported_surface.py tests/test_integration.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit family-aware experiment CLI**

```bash
git add scripts/experiment/run.py scripts/experiment/inspect.py tests/test_supported_surface.py tests/test_integration.py
git commit -m "refactor(cli): report experiment families"
```

## Task 8: Update Documentation And Manifest

**Files:**
- Modify: `README.md`
- Modify: `docs/operations/cli.md`
- Modify: `docs/operations/benchmark.md`
- Modify: `docs/experiments/manifest.md`
- Modify: `docs/experiment/config_schema.md`
- Modify: `docs/design/implementation.md`
- Modify: `docs/state/current/next_runs.md`
- Modify: `scripts/README.md`

- [ ] **Step 1: Update README examples**

Replace trust paths with:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name h3_stress_response --workers 12
```

Replace benchmark paths with:

```bash
python scripts/benchmark/run_cvc.py --config configs/benchmark/e1_arena/default.toml
```

- [ ] **Step 2: Update CLI docs**

Document:

```text
configs/trust/...      trust-family experiment specs
configs/benchmark/...  benchmark-family experiment specs
configs/multifocal/... reserved future family
```

- [ ] **Step 3: Update schema doc**

Add:

```toml
[experiment]
family = "trust" # trust | benchmark | multifocal

[benchmark]
backends = [...]
agents = [...]
```

- [ ] **Step 4: Update manifest**

List trust specs and benchmark specs under the unified `configs/` tree.

- [ ] **Step 5: Update next runs**

Replace old paths:

```text
experiments/trust/hypotheses/
configs/benchmark*.json
```

with unified TOML paths.

- [ ] **Step 6: Run docs-related tests**

Run:

```bash
python -m pytest tests/test_experiment_manifest.py tests/test_supported_surface.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit docs**

```bash
git add README.md docs scripts/README.md tests/test_experiment_manifest.py tests/test_supported_surface.py
git commit -m "docs: document unified experiment config families"
```

## Task 9: Final Verification And Cleanup

**Files:**
- Any files touched above.

- [ ] **Step 1: Run focused tests**

Run:

```bash
python -m pytest \
  tests/test_experiment_config_schema.py \
  tests/test_experiment_manifest.py \
  tests/test_benchmark_config.py \
  tests/test_supported_surface.py \
  tests/test_scripts_smoke.py \
  -q
```

Expected: PASS.

- [ ] **Step 2: Run trust CLI dry-run**

Run:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml --output-dir results --batch-name unified_config_dry --workers 1 --dry-run
```

Expected manifest includes:

```text
family = trust
hypothesis_id = h3
experiment_id = betrayal_choice
expanded_runs = 300
```

- [ ] **Step 3: Run benchmark smoke**

Run:

```bash
python scripts/benchmark/run_cvc.py --config configs/benchmark/smoke/smoke.toml
```

Expected:

```text
benchmark_results.csv
benchmark_config.resolved.toml
```

- [ ] **Step 4: Run full test suite**

Run:

```bash
python -m pytest tests/ -q
```

Expected: PASS.

- [ ] **Step 5: Run static checks**

Run:

```bash
python -m ruff check .
python -m mypy
git diff --check
```

Expected: PASS.

- [ ] **Step 6: Confirm no root benchmark JSONs**

Run:

```bash
python - <<'PY'
from pathlib import Path
print(sorted(str(path) for path in Path("configs").glob("benchmark*.json")))
PY
```

Expected:

```text
[]
```

- [ ] **Step 7: Commit final cleanup if needed**

Only if intended changes remain unstaged after prior commits:

```bash
git status --short
git add <remaining intended files>
git commit -m "chore(config): finalize unified config families"
```

## Risk Notes

- Do not reintroduce old trust condition IDs or presets as public authored config.
- Do not delete benchmark semantics; migrate them into `[benchmark]`.
- Keep CvC-specific knobs under `[benchmark.cvc_local]` so trust benchmark configs remain readable.
- If a benchmark JSON cannot be represented cleanly in the shared envelope, stop and revise the schema rather than smuggling ad hoc keys into TOML.
- Do not update result interpretation docs from new experiment outputs without explicit user approval.
- Do not add orchestration or deployment scripts; Mango remains external.
