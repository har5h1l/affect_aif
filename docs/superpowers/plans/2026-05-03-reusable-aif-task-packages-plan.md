# Reusable AIF Task Packages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-ground the repository around a reusable JAX-based `aif/` core, task packages, current Hesp-extension hypotheses, canonical script-driven experiments, docs/state steering, and high-confidence tests before rerunning experiments.

**Architecture:** Implement in behavior-preserving phases first, then harden the JAX core as a separate phase. The dependency direction is `scripts -> experiments -> tasks -> aif`; `aif/` must stay free of task/research/runtime imports. Trust-specific semantics move to `tasks/trust/`, trust baselines become a trust-task evaluation arena, and CvC moves structurally to `benchmarks/cvc/` without making CvC runtime success a blocker.

**Tech Stack:** Python 3.10, JAX/JAX NumPy for core `aif/`, pytest, ruff, mypy, pandas for analysis/logging, Mango for remote sync. No new runtime dependencies without explicit approval.

---

## Spec Reference

Approved design:

- `docs/superpowers/specs/2026-05-03-reusable-aif-task-packages-design.md`

Implementation must preserve these decisions:

- Hesp-extension hypothesis spine replaces the old drifted H# story.
- Salvage useful paper/state/archive content, then delete stale artifacts.
- Scripts produce canonical runs; notebooks are references only.
- Unit tests plus lightweight e2e tests are mandatory; no full experiments in e2e.
- Mango sync on the main MacBook Air server is part of completion and is recorded in `docs/state/`.

---

## File Structure

### Created

| path | responsibility |
|---|---|
| `docs/state/README.md` | Current context steering wheel for humans and agents. |
| `docs/state/current/mission.md` | Active mission, scope, constraints, and stop conditions. |
| `docs/state/current/next_runs.md` | Exact experiment queue and run commands after restructure. |
| `docs/state/current/blockers.md` | Open blockers and decisions that require human input. |
| `docs/state/decisions/architecture.md` | Settled architecture decisions and rationale. |
| `docs/state/decisions/experiments.md` | Settled hypothesis/config/analysis decisions. |
| `docs/state/handoffs/<date>.md` | Dated handoff snapshots replacing conductor logs. |
| `docs/theory/goals.md` | Project goal and Hesp-extension framing. |
| `docs/theory/hypotheses.md` | Current H1-H7 hypotheses. |
| `docs/theory/apashea_alignment.md` | apashea notebook alignment and deliberate deviations. |
| `docs/results/README.md` | Results documentation contract. |
| `docs/results/current.md` | Current interpreted result status. |
| `docs/results/historical_findings.md` | Salvaged historical findings clearly marked as historical. |
| `docs/results/runs/` | Per-run provenance docs. |
| `docs/design/task_packages.md` | Task package boundary contract. |
| `docs/design/benchmarks.md` | External benchmark/CvC status and trust evaluation distinction. |
| `tasks/trust/**` | Trust task package. |
| `experiments/trust/**` | Trust experiment orchestration, configs, logging, and runners. |
| `experiments/multifocal/**` | Multi-focal experiment orchestration. |
| `benchmarks/cvc/**` | CvC structure, kept non-blocking. |
| `benchmarks/shared/**` | Shared external benchmark helpers, if still needed. |
| `scripts/experiment/*.py` | Canonical experiment CLI wrappers. |
| `scripts/analysis/*.py` | Canonical analysis/summary/visualization CLI wrappers. |
| `scripts/benchmark/*.py` | Canonical external benchmark wrappers. |
| `tests/test_import_boundaries.py` | Import-boundary checks. |
| `tests/test_package_surface.py` | Package discovery and public API checks. |
| `tests/test_docs_state.py` | Docs/state inventory checks. |
| `tests/test_experiment_e2e_lightweight.py` | Tiny end-to-end wiring tests, no full experiments. |
| `tests/test_scripts_smoke.py` | CLI dry-run/smoke tests. |
| `tests/test_aif_jax_core.py` | JAX core API and PRNG tests. |

### Modified

| path | responsibility |
|---|---|
| `pyproject.toml` | Package discovery, ruff/mypy settings if needed. |
| `aif/**` | JAX-based reusable core; later JAX hardening. |
| `analysis/hypotheses.py` | Rewritten around current Hesp-extension H1-H7. |
| `analysis/metrics.py` | Current hypothesis metric helpers. |
| `scripts/run_experiment.py`, `scripts/run_analysis.py`, `scripts/run_visualization.py`, `scripts/run_benchmark.py` | Move or replace with thin wrappers under subfolders. |
| `README.md`, `AGENTS.md`, `CLAUDE.md` | Updated pointers to current docs/state and supported workflow. |
| `docs/theory/pomdp_spec.md` | Keep formal model spec, update links/alignment. |
| `docs/operations/cli.md`, `docs/operations/benchmark.md` | Update commands and benchmark semantics. |
| Existing tests | Update imports and split coverage by package boundary. |

### Deleted after salvage

| path | reason |
|---|---|
| `docs/paper/**` | Stale maintained paper surface; useful content moves into docs. |
| `conductor/**` | Replaced by `docs/state/`. |
| `archive/**` | No legacy junk drawer; useful content moves into docs or is deleted. |
| `notebooks/01_single_agent_demo.ipynb` | Stale tutorial; no notebooks except references. |
| `notebooks/02_affective_agent_demo.ipynb` | Stale tutorial; no notebooks except references. |
| `notebooks/03_full_experiment.ipynb` | Stale tutorial; no notebooks except references. |
| Unsupported configs/scripts | Delete if they do not map to current hypotheses or external benchmark needs. |

### Moved

| from | to |
|---|---|
| `notebooks/04_apashea_trust_spec.ipynb` | `notebooks/references/apashea_trust_spec.ipynb` |
| `trust/*.py` | `tasks/trust/...` |
| `env/*.py` | `tasks/trust/envs/...` |
| `experiment/*.py` | `experiments/trust/...` or `experiments/multifocal/...` |
| `benchmark/cvc_*.py`, CvC helpers | `benchmarks/cvc/...` |
| trust baseline/evaluation files | `tasks/trust/evaluation/...` |

---

## Global Verification Commands

Run at the end of every phase:

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

When doc validators exist, include:

```bash
python -m pytest tests/test_docs_state.py tests/test_import_boundaries.py -q
```

Expected final state: all commands pass. Slow statistical experiments are not part of the implementation verification gate.

---

## Phase 0 - Merge-Readiness Patch

Goal: make the current branch shippable before large moves.

### Task 0.1: Protect worktree state and scope

**Files:**
- Inspect only: all currently dirty files

- [ ] **Step 1: Inspect current status**

```bash
git status --short --branch
```

Expected: existing deletions under `archive/` and `docs/paper/` may be present. Do not stage or revert them unless this phase explicitly handles deletion.

- [ ] **Step 2: Record scope in a scratch note**

Write in the implementation PR notes: "Phase 0 only touches package/lint/type/link readiness; it does not perform the large topology move."

- [ ] **Step 3: Commit nothing**

This is an audit task only.

### Task 0.2: Add package discovery coverage

**Files:**
- Modify: `pyproject.toml`
- Create/modify: `tests/test_package_surface.py`

- [ ] **Step 1: Write failing package discovery test**

```python
from pathlib import Path
import tomllib

from setuptools import find_packages


ROOT = Path(__file__).resolve().parents[1]


def test_current_runtime_packages_are_discovered_by_pyproject():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    include = pyproject["tool"]["setuptools"]["packages"]["find"]["include"]
    assert "aif*" in include
    assert "trust*" in include
    packages = set(find_packages(where=str(ROOT), include=include))
    assert "aif" in packages
    assert "aif.affect" in packages
    assert "trust" in packages
```

- [ ] **Step 2: Run the test and verify it fails if `pyproject.toml` omits packages**

```bash
python -m pytest tests/test_package_surface.py::test_current_runtime_packages_are_discovered_by_pyproject -v
```

Expected: FAIL until package discovery includes `aif*` and `trust*`, or PASS if already fixed by concurrent work.

- [ ] **Step 3: Update package discovery**

In `pyproject.toml`, change package discovery from:

```toml
include = ["agent*", "env*", "experiment*", "analysis*", "benchmark*", "cli*"]
```

to:

```toml
include = ["aif*", "trust*", "env*", "experiment*", "analysis*", "benchmark*", "cli*"]
```

Do not add future `tasks*`/`experiments*` packages until those packages exist.

- [ ] **Step 4: Run targeted test**

```bash
python -m pytest tests/test_package_surface.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tests/test_package_surface.py
git commit -m "fix(package): include current aif and trust packages"
```

### Task 0.3: Fix lint/type/diff readiness without behavior changes

**Files:**
- Modify as needed: `aif/**`, `trust/**`, `analysis/**`, `benchmark/**`, `experiment/**`, `scripts/**`, `tests/**`, `pyproject.toml`

- [ ] **Step 1: Run lint**

```bash
python -m ruff check .
```

Expected currently: FAIL with mechanical import ordering, unused imports, long lines, and modernization issues.

- [ ] **Step 2: Apply safe auto-fixes**

```bash
python -m ruff check . --fix
```

Expected: only safe mechanical changes. Review the diff before committing.

- [ ] **Step 3: Manually fix remaining lint issues**

Examples to handle manually:

```python
# Before
for c, n in zip(controls, num_controls):
    ...

# After
for c, n in zip(controls, num_controls, strict=True):
    ...
```

For long fixture dictionaries, split across lines instead of disabling line length globally.

- [ ] **Step 4: Run mypy**

```bash
python -m mypy
```

Expected currently: FAIL with a small number of type errors. Fix by narrowing unions or adding local typed variables, not by silencing whole modules.

- [ ] **Step 5: Run diff check**

```bash
git diff --check
```

Expected currently: FAIL on trailing whitespace in docs. Remove trailing whitespace.

- [ ] **Step 6: Run full verification**

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "chore: make post-restructure branch verification clean"
```

### Task 0.4: Fix highest-risk broken links only

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `scripts/README.md`
- Modify: `docs/operations/cli.md`

- [ ] **Step 1: Write a tiny broken-link scan test for known top-level files**

Create or extend `tests/test_docs_state.py`:

```python
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_top_level_doc_links_exist():
    checked = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "scripts" / "README.md"]
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+\.md)(?:#[^)]+)?\)")
    missing = []
    for path in checked:
        text = path.read_text()
        for match in pattern.finditer(text):
            target = match.group(1)
            if target.startswith("http"):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    assert missing == []
```

- [ ] **Step 2: Run targeted test**

```bash
python -m pytest tests/test_docs_state.py::test_top_level_doc_links_exist -v
```

Expected: FAIL on stale links such as `docs/cli.md` and old doc paths.

- [ ] **Step 3: Fix only obvious links**

Examples:

```text
docs/cli.md -> docs/operations/cli.md
docs/theory.md -> docs/theory/theory.md
docs/experiment.md -> docs/experiment/design.md
docs/implementation.md -> docs/design/implementation.md
docs/results_tracking.md -> docs/experiment/results.md
```

Do not rewrite the whole docs surface in Phase 0.

- [ ] **Step 4: Run targeted test and full verification**

```bash
python -m pytest tests/test_docs_state.py::test_top_level_doc_links_exist -v
python -m pytest tests/ -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md AGENTS.md scripts/README.md docs/operations/cli.md tests/test_docs_state.py
git commit -m "docs: fix merge-blocking workflow links"
```

### Task 0.5: Merge to primary branch

**Files:**
- Git only

- [ ] **Step 1: Verify branch relation**

```bash
git fetch --prune
git status --short --branch
git merge-base --is-ancestor master HEAD
```

Expected: command exits `0`, meaning `master` is ancestor of current branch.

- [ ] **Step 2: Switch primary branch**

```bash
git switch master
```

- [ ] **Step 3: Fast-forward merge**

```bash
git merge --ff-only analysis/post-restructure-reframe
```

Expected: fast-forward succeeds.

- [ ] **Step 4: Run verification on primary branch**

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

Expected: PASS.

- [ ] **Step 5: Commit**

No commit expected; fast-forward merge reuses branch commits.

---

## Phase 1 - Context Reset and Docs State

Goal: make docs/state the context steering wheel and delete stale paper/archive/conductor surfaces after salvage.

### Task 1.1: Create docs/state inventory tests

**Files:**
- Create/modify: `tests/test_docs_state.py`

- [ ] **Step 1: Write failing docs/state inventory test**

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docs_state_steering_wheel_exists():
    required = [
        "docs/state/README.md",
        "docs/state/current/mission.md",
        "docs/state/current/next_runs.md",
        "docs/state/current/blockers.md",
        "docs/state/decisions/architecture.md",
        "docs/state/decisions/experiments.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert missing == []
```

- [ ] **Step 2: Run test and verify it fails**

```bash
python -m pytest tests/test_docs_state.py::test_docs_state_steering_wheel_exists -v
```

Expected: FAIL because docs/state does not exist.

- [ ] **Step 3: Commit failing test**

```bash
git add tests/test_docs_state.py
git commit -m "test(docs): require docs state steering wheel"
```

### Task 1.2: Create docs/state from conductor content

**Files:**
- Create: `docs/state/README.md`
- Create: `docs/state/current/mission.md`
- Create: `docs/state/current/next_runs.md`
- Create: `docs/state/current/blockers.md`
- Create: `docs/state/decisions/architecture.md`
- Create: `docs/state/decisions/experiments.md`
- Create: `docs/state/handoffs/2026-05-03.md`
- Read/salvage: `conductor/MISSION.md`, `conductor/STATE.md`

- [ ] **Step 1: Read source state**

```bash
sed -n '1,260p' conductor/MISSION.md
sed -n '1,260p' conductor/STATE.md
```

- [ ] **Step 2: Create docs/state directories**

```bash
mkdir -p docs/state/current docs/state/decisions docs/state/handoffs
```

- [ ] **Step 3: Write `docs/state/README.md`**

Minimum content:

```markdown
# Project State

This directory is the context steering wheel for humans and agents.

- `current/mission.md`: active mission and constraints
- `current/next_runs.md`: exact experiment queue
- `current/blockers.md`: unresolved blockers and stop conditions
- `decisions/`: settled architecture and experiment decisions
- `handoffs/`: dated handoff snapshots
```

- [ ] **Step 4: Write current mission/blockers/next runs**

Use the approved spec and conductor salvage. Include:

```markdown
# Current Mission

Re-ground affect_aif around a reusable JAX-based `aif/` core, task packages,
current Hesp-extension hypotheses, canonical script-driven experiments, and
docs/state steering.
```

For next runs, do not schedule full experiments until restructure verification passes.

- [ ] **Step 5: Run docs/state test**

```bash
python -m pytest tests/test_docs_state.py::test_docs_state_steering_wheel_exists -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/state tests/test_docs_state.py
git commit -m "docs(state): create project steering wheel"
```

### Task 1.3: Salvage paper and historical results, then delete stale sources

**Files:**
- Create: `docs/results/README.md`
- Create: `docs/results/current.md`
- Create: `docs/results/historical_findings.md`
- Modify: `docs/theory/goals.md` (created in Task 1.4 if not present)
- Delete: `docs/paper/**`
- Delete: `archive/**`
- Delete: `conductor/**` after state salvage

- [ ] **Step 1: Search for useful paper content**

```bash
rg "Hesp|Damasio|vmPFC|clinical|betrayal|precision|affect" docs/paper conductor archive -n
```

- [ ] **Step 2: Write historical results doc**

Mark content as historical:

```markdown
# Historical Findings

These findings are preserved as historical context only. They may predate the
apashea-aligned factorized-control model and should not be compared as current
evidence unless explicitly rerun on the current architecture.
```

- [ ] **Step 3: Delete stale sources**

```bash
git rm -r docs/paper archive conductor
```

If a directory is already deleted in the worktree, stage those deletions intentionally in this task.

- [ ] **Step 4: Run docs/state and full test suite**

```bash
python -m pytest tests/test_docs_state.py -q
python -m pytest tests/ -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/results docs/theory/goals.md docs/state
git commit -m "docs: salvage historical context and remove stale artifacts"
```

### Task 1.4: Rewrite theory goal and hypotheses docs

**Files:**
- Create: `docs/theory/goals.md`
- Create: `docs/theory/hypotheses.md`
- Create: `docs/theory/apashea_alignment.md`
- Modify: `docs/theory/pomdp_spec.md`
- Modify: `README.md`, `AGENTS.md`

- [ ] **Step 1: Write failing stale-label test**

Add to `tests/test_docs_state.py`:

```python
def test_current_docs_do_not_use_old_hypothesis_story():
    paths = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs/theory/goals.md",
        ROOT / "docs/theory/hypotheses.md",
    ]
    forbidden = ["affect compensates for shallow planning", "deep planner as gold standard"]
    offenders = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text().lower()
        for phrase in forbidden:
            if phrase in text:
                offenders.append(f"{path.relative_to(ROOT)}: {phrase}")
    assert offenders == []
```

- [ ] **Step 2: Run test**

```bash
python -m pytest tests/test_docs_state.py::test_current_docs_do_not_use_old_hypothesis_story -v
```

Expected: may FAIL until docs are written.

- [ ] **Step 3: Write `docs/theory/goals.md`**

Include the approved goal:

```markdown
# Project Goal

This project extends Hesp et al.'s single-agent affect-as-expected-action-precision account into multi-agent active inference by factorizing affective model-fitness estimates over social partners.
```

- [ ] **Step 4: Write `docs/theory/hypotheses.md`**

Include H1-H7 exactly from the approved spec: model fitness not reward, partner factorization, deployment not knowledge, social volatility, partner selection, policy-space regime, clinical perturbations.

- [ ] **Step 5: Write `docs/theory/apashea_alignment.md`**

Document:

- apashea notebook is reference
- factorized controls
- `log_policy_prior`
- deliberate deviations
- JAX-based core commitment

- [ ] **Step 6: Run tests and commit**

```bash
python -m pytest tests/test_docs_state.py -q
git add docs/theory README.md AGENTS.md tests/test_docs_state.py
git commit -m "docs(theory): reset project goal and hypotheses"
```

---

## Phase 2 - Experiment Surface Cleanup

Goal: make configs and analysis map to current hypotheses.

### Task 2.1: Add experiment manifest test

**Files:**
- Create: `docs/experiments/manifest.md`
- Create/modify: `tests/test_experiment_manifest.py`

- [ ] **Step 1: Write failing manifest consistency test**

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_experiment_manifest_lists_current_hypotheses():
    manifest = ROOT / "docs/experiments/manifest.md"
    assert manifest.exists()
    text = manifest.read_text()
    for label in ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "E1", "E2"]:
        assert f"| {label} " in text or f"## {label}" in text
```

- [ ] **Step 2: Run and verify failure**

```bash
python -m pytest tests/test_experiment_manifest.py -v
```

Expected: FAIL until manifest exists.

- [ ] **Step 3: Commit failing test**

```bash
git add tests/test_experiment_manifest.py
git commit -m "test(experiments): require current hypothesis manifest"
```

### Task 2.2: Move and rename supported configs

**Files:**
- Create: `experiments/trust/configs/*.json`
- Create: `experiments/multifocal/configs/*.json`
- Delete/rename: `configs/*.json`
- Modify: `docs/experiments/manifest.md`

- [ ] **Step 1: Create config directories**

```bash
mkdir -p experiments/trust/configs experiments/multifocal/configs docs/experiments
```

- [ ] **Step 2: Move/rename supported configs**

Use `git mv` for configs that survive. Initial mapping:

```bash
git mv configs/smoke_test.json experiments/trust/configs/smoke.json
git mv configs/shallow_affect_confirm.json experiments/trust/configs/h6_shallow_policy_regime.json
git mv configs/h5_partner_selection.json experiments/trust/configs/h5_partner_selection.json
git mv configs/h4_betrayal_recovery.json experiments/trust/configs/h4_betrayal_volatility.json
git mv configs/clinical_betrayal.json experiments/trust/configs/h7_clinical_betrayal.json
git mv configs/clinical_phenotypes.json experiments/trust/configs/h7_clinical_phenotypes.json
git mv configs/graded_trust_factorial.json experiments/trust/configs/h6_graded_policy_regime.json
git mv configs/multifocal_smoke.json experiments/multifocal/configs/smoke.json
git mv configs/multifocal_homogeneous_affective.json experiments/multifocal/configs/e2_homogeneous.json
git mv configs/multifocal_clinical_mix.json experiments/multifocal/configs/e2_clinical_mix.json
git mv configs/multifocal_assortative_choice.json experiments/multifocal/configs/e2_assortative.json
```

For configs not listed, decide in this task whether they map to H1-H7/E1/E2. Delete unsupported ones instead of archiving.

- [ ] **Step 3: Write manifest**

Minimum table:

```markdown
# Experiment Manifest

| Item | Question | Configs | Analysis |
|---|---|---|---|
| H1 | Model fitness, not reward | `experiments/trust/configs/h1_model_fitness.json` | `analysis.hypotheses.test_h1_model_fitness` |
| H2 | Partner factorization | `experiments/trust/configs/h2_partner_factorization.json` | `analysis.hypotheses.test_h2_partner_factorization` |
```

Use `pending config` where a hypothesis has no config yet, but make that explicit.

- [ ] **Step 4: Run manifest test**

```bash
python -m pytest tests/test_experiment_manifest.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add configs experiments docs/experiments tests/test_experiment_manifest.py
git commit -m "experiments: map configs to current hypotheses"
```

### Task 2.3: Rewrite analysis hypotheses around H1-H7

**Files:**
- Modify: `analysis/hypotheses.py`
- Modify: `analysis/metrics.py`
- Modify: `scripts/run_analysis.py` or later `scripts/analysis/analyze.py`
- Modify/create: `tests/test_analysis_hypotheses.py`

- [ ] **Step 1: Write tests for new analysis API**

```python
import pandas as pd

from analysis.hypotheses import run_all_hypothesis_tests


def test_run_all_hypothesis_tests_returns_current_h_labels():
    df = pd.DataFrame(
        [
            {"condition_name": "tau1_no_affect", "seed": 1, "round": 0, "payoff": 1.0},
            {"condition_name": "tau1_affect", "seed": 1, "round": 0, "payoff": 2.0},
        ]
    )
    result = run_all_hypothesis_tests(df)
    assert set(result) == {"h1", "h2", "h3", "h4", "h5", "h6", "h7"}
```

- [ ] **Step 2: Run and verify failure**

```bash
python -m pytest tests/test_analysis_hypotheses.py -v
```

Expected: FAIL until `analysis/hypotheses.py` is rewritten.

- [ ] **Step 3: Implement new API minimally**

Keep the file name `analysis/hypotheses.py`. Replace old semantics with functions:

```python
def test_h1_model_fitness(results: pd.DataFrame) -> dict: ...
def test_h2_partner_factorization(results: pd.DataFrame) -> dict: ...
def test_h3_deployment_not_knowledge(results: pd.DataFrame) -> dict: ...
def test_h4_social_volatility(results: pd.DataFrame) -> dict: ...
def test_h5_partner_selection(results: pd.DataFrame) -> dict: ...
def test_h6_policy_space_regime(results: pd.DataFrame) -> dict: ...
def test_h7_clinical_perturbations(results: pd.DataFrame) -> dict: ...
```

Each function must return JSON-safe dictionaries with `available`, `hypothesis`, `summary`, and `evidence` keys.

- [ ] **Step 4: Run analysis tests**

```bash
python -m pytest tests/test_analysis_hypotheses.py tests/test_analysis_semantics.py -q
```

Expected: PASS after updating legacy tests.

- [ ] **Step 5: Commit**

```bash
git add analysis tests scripts docs/experiments/manifest.md
git commit -m "analysis: align hypotheses with hesp extension"
```

---

## Phase 3 - Behavior-Preserving Task Topology

Goal: move code into `tasks/` and `experiments/` without changing numerical behavior.

### Task 3.1: Add import-boundary tests

**Files:**
- Create: `tests/test_import_boundaries.py`

- [ ] **Step 1: Write boundary test**

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_aif_does_not_import_higher_layers():
    forbidden = ("tasks.", "experiments.", "analysis.", "benchmarks.", "trust.", "env.", "experiment.", "benchmark.")
    offenders = []
    for path in (ROOT / "aif").rglob("*.py"):
        text = path.read_text()
        for token in forbidden:
            if f"import {token}" in text or f"from {token}" in text:
                offenders.append(f"{path.relative_to(ROOT)} imports {token}")
    assert offenders == []
```

- [ ] **Step 2: Run targeted test**

```bash
python -m pytest tests/test_import_boundaries.py -v
```

Expected: PASS before moves and after moves.

- [ ] **Step 3: Commit**

```bash
git add tests/test_import_boundaries.py
git commit -m "test: guard aif import boundaries"
```

### Task 3.2: Move trust and env into task package

**Files:**
- Move: `trust/**` -> `tasks/trust/**`
- Move: `env/**` -> `tasks/trust/envs/**`
- Modify: imports across `experiments`, `scripts`, `analysis`, `tests`
- Modify: `pyproject.toml`

- [ ] **Step 1: Create directories**

```bash
mkdir -p tasks/trust/agents tasks/trust/envs tasks/trust/models
```

- [ ] **Step 2: Move files with `git mv`**

```bash
git mv trust/agent.py tasks/trust/agents/base.py
git mv trust/affective.py tasks/trust/agents/affective.py
git mv trust/lesioned.py tasks/trust/agents/lesioned.py
git mv trust/model.py tasks/trust/models/trust_game.py
git mv trust/payoffs.py tasks/trust/payoffs.py
git mv trust/rollout.py tasks/trust/rollout.py
git mv trust/stance.py tasks/trust/stance.py
git mv trust/types.py tasks/trust/types.py
git mv env/trust_game.py tasks/trust/envs/binary.py
git mv env/graded_trust_game.py tasks/trust/envs/graded.py
git mv env/partner.py tasks/trust/envs/partners.py
```

Create `tasks/__init__.py`, `tasks/trust/__init__.py`, `tasks/trust/agents/__init__.py`, `tasks/trust/models/__init__.py`, and `tasks/trust/envs/__init__.py`.

- [ ] **Step 3: Update imports mechanically**

Examples:

```python
# Before
from trust.model import TrustGameModel
from env.trust_game import TrustGameEnv

# After
from tasks.trust.models import TrustGameModel
from tasks.trust.envs import TrustGameEnv
```

- [ ] **Step 4: Update package discovery**

In `pyproject.toml`, include:

```toml
include = ["aif*", "tasks*", "experiments*", "analysis*", "benchmarks*", "cli*"]
```

Only do this after `tasks/` and `experiments/` exist.

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_import_boundaries.py tests/test_package_surface.py -q
python -m pytest tests/ -q
```

Expected: PASS.

- [ ] **Step 6: Delete old package dirs if empty**

```bash
rmdir trust env
```

If temporary shims were needed, add a deletion ticket in `docs/state/current/blockers.md` and delete before Phase 3 is considered complete.

- [ ] **Step 7: Commit**

```bash
git add tasks pyproject.toml tests
git add -u trust env experiment benchmark scripts
git commit -m "refactor(tasks): move trust domain into task package"
```

### Task 3.3: Move experiment orchestration

**Files:**
- Move: `experiment/runner.py` -> `experiments/trust/runner.py`
- Move: `experiment/batch.py` -> `experiments/trust/batch.py`
- Move: `experiment/config.py` -> `experiments/trust/config.py`
- Move: `experiment/logger.py` -> `experiments/trust/logger.py`
- Move: `experiment/factory.py` -> `experiments/trust/factory.py`
- Move: `experiment/conditions.py` -> `experiments/trust/conditions.py`
- Move: `experiment/multi_focal_*.py`, `experiment/joint_resolution.py` -> `experiments/multifocal/`
- Modify imports/tests/scripts

- [ ] **Step 1: Create directories**

```bash
mkdir -p experiments/trust experiments/multifocal
```

- [ ] **Step 2: Move files with `git mv`**

Use `git mv` for each file. Keep `calibration.py`, `progress.py`, `persistence.py`, and `tasks.py` with trust runner unless a clearer shared home emerges.

- [ ] **Step 3: Update imports**

Examples:

```python
# Before
from experiment.config import ExperimentConfig

# After
from experiments.trust.config import ExperimentConfig
```

- [ ] **Step 4: Run construction tests**

```bash
python -m pytest tests/test_integration.py tests/test_multi_focal_runner_construction.py tests/test_multi_focal_round_loop.py -q
```

Expected: PASS.

- [ ] **Step 5: Run full tests and commit**

```bash
python -m pytest tests/ -q
git add experiments tests scripts pyproject.toml
git add -u experiment
git commit -m "refactor(experiments): split trust and multifocal orchestration"
```

### Task 3.4: Move trust evaluation out of benchmark

**Files:**
- Move: `benchmark/baselines.py` -> `tasks/trust/evaluation/baselines.py`
- Move/adapt: `benchmark/trust_backend.py` -> `tasks/trust/evaluation/arena.py`
- Modify: `benchmark/benchmark_config.py`, `benchmark/benchmark_runner.py`, tests

- [ ] **Step 1: Write failing semantic test**

```python
def test_trust_baselines_live_under_task_evaluation():
    from tasks.trust.evaluation.baselines import RandomAgent

    assert RandomAgent is not None
```

- [ ] **Step 2: Move files**

```bash
mkdir -p tasks/trust/evaluation
git mv benchmark/baselines.py tasks/trust/evaluation/baselines.py
git mv benchmark/trust_backend.py tasks/trust/evaluation/arena.py
```

- [ ] **Step 3: Update naming in docs**

Replace "trust benchmark" with "trust-task evaluation arena" in current docs.

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_benchmark_baselines.py tests/test_benchmark_betrayal.py tests/test_joint_agent_and_conditions.py -q
```

Expected: PASS after imports update.

- [ ] **Step 5: Commit**

```bash
git add tasks benchmark tests docs
git commit -m "refactor(trust): move baselines into task evaluation arena"
```

---

## Phase 4 - JAX Core Hardening

Goal: make the reusable `aif/` core explicitly JAX-based after topology is stable.

### Task 4.1: Add JAX core tests

**Files:**
- Create: `tests/test_aif_jax_core.py`

- [ ] **Step 1: Write JAX array compatibility tests**

```python
import jax
import jax.numpy as jnp

import aif


def test_softmax_accepts_jax_array():
    values = jnp.array([1.0, 2.0, 3.0])
    result = aif.softmax(values)
    assert hasattr(result, "shape")
    assert result.shape == (3,)
    assert jnp.isclose(result.sum(), 1.0)


def test_sample_action_requires_explicit_key():
    q_pi = jnp.array([0.25, 0.75])
    key = jax.random.PRNGKey(0)
    action = aif.sample_action(q_pi, rng=key)
    assert int(action) in {0, 1}
```

- [ ] **Step 2: Run and verify failures where APIs are not explicit yet**

```bash
python -m pytest tests/test_aif_jax_core.py -v
```

Expected: FAIL until public APIs accept JAX arrays and explicit PRNG keys.

- [ ] **Step 3: Commit failing tests**

```bash
git add tests/test_aif_jax_core.py
git commit -m "test(aif): define jax core contract"
```

### Task 4.2: Convert public `aif/` numerical surfaces

**Files:**
- Modify: `aif/maths.py`
- Modify: `aif/policies.py`
- Modify: `aif/inference.py`
- Modify: `aif/efe.py`
- Modify: `aif/learning.py`
- Modify: `aif/affect/beta.py`
- Modify: task callers as needed

- [ ] **Step 1: Replace public core NumPy operations with JAX-compatible operations**

Example pattern:

```python
import jax.numpy as jnp


def softmax(x, axis: int = -1):
    values = jnp.asarray(x)
    shifted = values - jnp.max(values, axis=axis, keepdims=True)
    exp_values = jnp.exp(shifted)
    return exp_values / jnp.sum(exp_values, axis=axis, keepdims=True)
```

Keep NumPy conversion at analysis/logging/task boundaries where needed.

- [ ] **Step 2: Make policy sampling explicit**

Example public API:

```python
def sample_action(q_pi, rng):
    if rng is None:
        raise ValueError("sample_action requires an explicit JAX PRNG key.")
    return int(jax.random.categorical(rng, jnp.log(jnp.asarray(q_pi))))
```

Update task callers to pass PRNG keys or use task-local compatibility wrappers if task behavior still uses NumPy RNG.

- [ ] **Step 3: Add parity tests**

```python
def test_softmax_numpy_and_jax_parity():
    import numpy as np
    import jax.numpy as jnp

    values = np.array([0.1, 0.2, 0.3])
    np_result = np.asarray(aif.softmax(values))
    jax_result = np.asarray(aif.softmax(jnp.asarray(values)))
    assert np.allclose(np_result, jax_result)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_aif_jax_core.py tests/test_aif_inference.py tests/test_aif_policies.py tests/test_aif_learning.py -q
```

Expected: PASS.

- [ ] **Step 5: Run task behavior tests with tolerances**

```bash
python -m pytest tests/test_hesp_agents.py tests/test_integration.py tests/test_theory_alignment.py -q
```

Expected: PASS, with explicit numerical tolerances if needed.

- [ ] **Step 6: Commit**

```bash
git add aif tasks tests
git commit -m "refactor(aif): harden jax-based core APIs"
```

---

## Phase 5 - Scripts, Canonical Runs, and CvC Structure

Goal: scripts are canonical, notebooks are references only, CvC follows structure but does not block trust/AIF cleanup.

### Task 5.1: Split scripts by execution role

**Files:**
- Move/create: `scripts/experiment/run.py`
- Move/create: `scripts/experiment/smoke.py`
- Move/create: `scripts/experiment/inspect.py`
- Move/create: `scripts/analysis/analyze.py`
- Move/create: `scripts/analysis/summarize.py`
- Move/create: `scripts/analysis/visualize.py`
- Move/create: `scripts/benchmark/run_cvc.py`
- Move/create: `scripts/benchmark/package_cvc.py`
- Modify: `scripts/README.md`, `docs/operations/cli.md`

- [ ] **Step 1: Write script smoke tests**

Create `tests/test_scripts_smoke.py`:

```python
import subprocess
import sys


def test_experiment_run_help():
    result = subprocess.run(
        [sys.executable, "scripts/experiment/run.py", "--help"],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "--config" in result.stdout
```

- [ ] **Step 2: Run and verify failure until script exists**

```bash
python -m pytest tests/test_scripts_smoke.py::test_experiment_run_help -v
```

Expected: FAIL until scripts are moved/created.

- [ ] **Step 3: Move/create thin wrappers**

Wrappers should call package APIs only. Keep old top-level scripts only if needed as short-lived compatibility wrappers with deprecation messages.

- [ ] **Step 4: Run script tests**

```bash
python -m pytest tests/test_scripts_smoke.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts tests docs/operations/cli.md
git add -u scripts
git commit -m "cli: organize canonical experiment and analysis scripts"
```

### Task 5.2: Add provenance and dry-run behavior

**Files:**
- Modify: `scripts/experiment/run.py`
- Modify: `scripts/analysis/analyze.py`
- Modify: experiment persistence helpers
- Test: `tests/test_scripts_smoke.py`, `tests/test_experiment_e2e_lightweight.py`

- [ ] **Step 1: Write dry-run provenance test**

```python
import json
import subprocess
import sys


def test_experiment_run_dry_run_writes_manifest(tmp_path):
    out = tmp_path / "results"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/experiment/run.py",
            "--config",
            "experiments/trust/configs/smoke.json",
            "--output-dir",
            str(out),
            "--batch-name",
            "dry_run",
            "--dry-run",
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    manifest = json.loads((out / "dry_run" / "manifest.json").read_text())
    assert manifest["batch_name"] == "dry_run"
    assert "git_commit" in manifest
```

- [ ] **Step 2: Implement dry-run**

Dry-run should parse configs, resolve paths, write manifest/provenance, and exit without running full experiments.

- [ ] **Step 3: Run targeted tests**

```bash
python -m pytest tests/test_scripts_smoke.py::test_experiment_run_dry_run_writes_manifest -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add scripts experiments tests
git commit -m "cli: add dry-run provenance manifests"
```

### Task 5.3: Move CvC structurally

**Files:**
- Move: `benchmark/cvc_*.py` -> `benchmarks/cvc/*.py`
- Move: `benchmark/observatory.py`, `benchmark/cvc_packaging.py`, etc. as appropriate
- Modify: imports/tests/docs

- [ ] **Step 1: Write import-only CvC structure test**

```python
def test_cvc_package_imports_without_runtime_execution():
    import importlib

    module = importlib.import_module("benchmarks.cvc.packaging")
    assert module is not None
```

- [ ] **Step 2: Move CvC files with `git mv`**

Use names without repeated `cvc_` prefix inside the package:

```bash
mkdir -p benchmarks/cvc
git mv benchmark/cvc_packaging.py benchmarks/cvc/packaging.py
git mv benchmark/cvc_navigation.py benchmarks/cvc/navigation.py
git mv benchmark/cvc_beta.py benchmarks/cvc/beta.py
```

Continue for remaining CvC files that are still kept.

- [ ] **Step 3: Isolate runtime-dependent tests**

If CvC runtime dependencies are unavailable, mark runtime tests with explicit skip/marker. Import and packaging tests should still pass.

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_cvc_packaging.py tests/test_cvc_navigation.py -q
```

Expected: import/packaging tests pass; runtime tests skip if dependency is unavailable.

- [ ] **Step 5: Commit**

```bash
git add benchmarks tests docs
git add -u benchmark
git commit -m "refactor(benchmarks): move cvc into external benchmark package"
```

### Task 5.4: Reduce notebooks to references

**Files:**
- Move: `notebooks/04_apashea_trust_spec.ipynb` -> `notebooks/references/apashea_trust_spec.ipynb`
- Delete: `notebooks/01_single_agent_demo.ipynb`
- Delete: `notebooks/02_affective_agent_demo.ipynb`
- Delete: `notebooks/03_full_experiment.ipynb`
- Modify: `notebooks/README.md`

- [ ] **Step 1: Move reference notebook**

```bash
mkdir -p notebooks/references
git mv notebooks/04_apashea_trust_spec.ipynb notebooks/references/apashea_trust_spec.ipynb
```

- [ ] **Step 2: Delete stale demos**

```bash
git rm notebooks/01_single_agent_demo.ipynb notebooks/02_affective_agent_demo.ipynb notebooks/03_full_experiment.ipynb
```

- [ ] **Step 3: Rewrite notebook README**

Minimum:

```markdown
# Notebooks

Notebooks are references only. They are not the canonical way to produce results.

- `references/apashea_trust_spec.ipynb`: reference math notebook for the apashea-aligned trust model.
```

- [ ] **Step 4: Commit**

```bash
git add notebooks
git commit -m "docs(notebooks): keep only apashea reference"
```

---

## Phase 6 - Lightweight End-to-End Tests

Goal: prove wiring works without full experiment runs.

### Task 6.1: Add tiny trust construction e2e

**Files:**
- Create/modify: `tests/test_experiment_e2e_lightweight.py`

- [ ] **Step 1: Write tiny config construction test**

```python
from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_agent, create_env, create_model


def test_tiny_trust_config_constructs_and_runs_one_round():
    config = ExperimentConfig(num_rounds=1, num_replications=1, conditions=[1], random_seed=0)
    model = create_model(config)
    env = create_env(config, seed=0)
    agent = create_agent(1, model, seed=0, config=config)
    context = env.reset()
    action = agent.plan_and_act(context.get("active_partner"))
    result = env.step(action)
    agent.observe_outcome(
        partner_idx=result["partner_idx"],
        observation=result["observation"],
        action_taken=result["agent_action"],
        partner_action=result["partner_action"],
        payoff=result["agent_payoff"],
        true_partner_type=result.get("true_partner_type"),
        true_partner_stance=result.get("true_partner_stance"),
    )
    assert "agent_payoff" in result
```

- [ ] **Step 2: Run targeted test**

```bash
python -m pytest tests/test_experiment_e2e_lightweight.py::test_tiny_trust_config_constructs_and_runs_one_round -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_experiment_e2e_lightweight.py
git commit -m "test(e2e): cover tiny trust round wiring"
```

### Task 6.2: Add tiny multi-focal e2e

**Files:**
- Modify: `tests/test_experiment_e2e_lightweight.py`

- [ ] **Step 1: Write tiny multi-focal test**

Use the existing multi-focal config constructors after they move. Test one round only and assert returned rows include `round`, `agent_idx`, and payoff fields.

- [ ] **Step 2: Run targeted test**

```bash
python -m pytest tests/test_experiment_e2e_lightweight.py::test_tiny_multifocal_round_loop_schema -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_experiment_e2e_lightweight.py
git commit -m "test(e2e): cover tiny multifocal round loop"
```

### Task 6.3: Add analysis-on-tiny-results e2e

**Files:**
- Modify: `tests/test_experiment_e2e_lightweight.py`
- Modify: `analysis/hypotheses.py` if needed

- [ ] **Step 1: Write tiny analysis test**

```python
import pandas as pd

from analysis.hypotheses import run_all_hypothesis_tests


def test_analysis_runs_on_tiny_results():
    frame = pd.DataFrame(
        [
            {"condition": 1, "condition_name": "tau1_no_affect", "seed": 0, "round": 0, "payoff": 1.0},
            {"condition": 2, "condition_name": "tau1_affect", "seed": 0, "round": 0, "payoff": 2.0},
        ]
    )
    results = run_all_hypothesis_tests(frame)
    assert "h1" in results
    assert all("available" in payload for payload in results.values())
```

- [ ] **Step 2: Run targeted test**

```bash
python -m pytest tests/test_experiment_e2e_lightweight.py::test_analysis_runs_on_tiny_results -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_experiment_e2e_lightweight.py analysis/hypotheses.py
git commit -m "test(e2e): cover tiny analysis wiring"
```

---

## Phase 7 - Final Verification, Mango Sync, and Experiment Queue

Goal: verify locally, merge/sync, record state, then prepare experiment reruns.

### Task 7.1: Final local verification

**Files:**
- Inspect/modify only if tests fail

- [ ] **Step 1: Run full verification**

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

Expected: PASS.

- [ ] **Step 2: Fix any failures with systematic debugging**

Use @superpowers:systematic-debugging before changing implementation for a failure.

- [ ] **Step 3: Commit any fixes**

```bash
git add <fixed-files>
git commit -m "test: complete restructure verification"
```

### Task 7.2: Merge cleaned branch to primary

**Files:**
- Git only

- [ ] **Step 1: Fetch/prune**

```bash
git fetch --prune
```

- [ ] **Step 2: Verify primary branch name**

```bash
git branch -vv --all
```

Expected: primary is `master` unless repository has changed.

- [ ] **Step 3: Merge**

```bash
git switch master
git merge --ff-only <restructure-branch>
```

Expected: fast-forward or clean merge. If not fast-forward, stop and inspect.

### Task 7.3: Sync on Mango main MacBook Air server

**Files:**
- Modify: `docs/state/current/mission.md`
- Modify: `docs/state/handoffs/<date>.md`

- [ ] **Step 1: Push/sync via Mango external workflow**

Use the project Mango flow. Starting command from project docs:

```bash
mango cloud sync push affect_aif
```

If the main MacBook Air server requires a fetch from that side, use the corresponding Mango fetch flow:

```bash
mango cloud sync fetch affect_aif
```

Do not add Mango orchestration scripts to this repo.

- [ ] **Step 2: Record sync status**

In `docs/state/handoffs/<date>.md`, record:

- command run
- timestamp
- branch/commit
- whether sync succeeded
- any remote follow-up needed

- [ ] **Step 3: Commit state update**

```bash
git add docs/state
git commit -m "state: record mango sync after restructure"
```

### Task 7.4: Record post-restructure experiment queue

**Files:**
- Modify: `docs/state/current/next_runs.md`
- Modify: `docs/results/README.md`

- [ ] **Step 1: Write rerun queue**

Order:

1. shallow affect / tau 1-3
2. partner selection
3. betrayal / stance switch
4. clinical perturbations
5. graded precision-channel tests
6. multi-focal descriptive runs

- [ ] **Step 2: Include exact script commands**

Use the new canonical scripts, for example:

```bash
python scripts/experiment/smoke.py --config experiments/trust/configs/h6_shallow_policy_regime.json
python scripts/experiment/run.py --config experiments/trust/configs/h6_shallow_policy_regime.json --output-dir results --batch-name h6_shallow_policy_regime
python scripts/analysis/analyze.py --results results/h6_shallow_policy_regime/h6_shallow_policy_regime/results.csv --output-dir results/h6_shallow_policy_regime/h6_shallow_policy_regime/analysis
```

- [ ] **Step 3: Commit**

```bash
git add docs/state/current/next_runs.md docs/results/README.md
git commit -m "state: record post-restructure experiment queue"
```

---

## Final Acceptance Checklist

- [ ] `aif/` is reusable, JAX-based, and free of task imports.
- [ ] `tasks/trust/` owns trust semantics, envs, agents, rollout, and evaluation.
- [ ] `experiments/` owns orchestration and configs.
- [ ] Old root `trust/`, `env/`, and `experiment/` packages are gone or documented temporary shims with deletion commits.
- [ ] Trust evaluation is not described as a separate trust benchmark.
- [ ] `docs/state/` replaces conductor state and contains mission, blockers, next runs, decisions, and handoffs.
- [ ] `docs/paper/`, `archive/`, and stale notebooks are deleted after salvage.
- [ ] Only the apashea reference notebook remains.
- [ ] Current H1-H7 hypotheses are documented and mapped to configs/analysis.
- [ ] Scripts are organized by execution role and write provenance.
- [ ] Unit tests cover moved public surfaces and import boundaries.
- [ ] Lightweight e2e tests cover tiny trust run, tiny multi-focal run, tiny analysis, script dry-run, and provenance.
- [ ] CvC follows `benchmarks/cvc/` structure and does not block trust/AIF verification.
- [ ] `pytest`, `ruff`, `mypy`, and `git diff --check` pass.
- [ ] Cleaned primary branch/workspace is synced via Mango on the main MacBook Air server.
- [ ] `docs/state/current/next_runs.md` lists the post-restructure experiment queue.
