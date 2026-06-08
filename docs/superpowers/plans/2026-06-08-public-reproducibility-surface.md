# Public Reproducibility Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the public demo/reproduction/results surface described in `docs/superpowers/specs/2026-06-08-public-reproducibility-surface-design.md`.

**Architecture:** Keep full trajectories out of git while tracking a reproducible `results/` scaffold, compact summaries, public configs, and docs. Split work into repo-local implementation first, then a dry-run server cleanup manifest, then gated server/Drive mutation.

**Tech Stack:** Python 3, TOML experiment specs, canonical `scripts/experiment/run.py`, pandas/matplotlib for notebook summaries, pytest/ruff/gitignore checks, Mango/ssh for server result cleanup.

---

## Pre-Flight

The branch already has uncommitted cleanup work. Do not revert unrelated edits.
The spec commit is `c945244`.

- [ ] **Step 1: Confirm branch and dirty state**

Run:

```bash
git status --short --branch
```

Expected: branch is `codex/repro-cleanup-20260608`; existing config/doc/script cleanup edits are present.

- [ ] **Step 2: Read the design spec**

Run:

```bash
sed -n '1,280p' docs/superpowers/specs/2026-06-08-public-reproducibility-surface-design.md
```

Expected: spec includes required public result directory artifacts and the server dry-run checkpoint.

- [ ] **Step 3: Verify no live server experiment before planning server mutation**

Run:

```bash
mango process list --project affect_aif 2>/dev/null || mango process list 2>/dev/null || true
ssh server 'tmux ls 2>/dev/null || true'
```

Expected: no live affect_aif experiment. If any active experiment appears, stop before server cleanup tasks.

---

## File Structure

Create or modify these files:

- Modify `.gitignore`: keep raw result data ignored while allowing public result scaffolds and compact summaries.
- Create `configs/demo/model_fitness.toml`: demo-scale model-fitness spec.
- Create `configs/demo/betrayal_adaptation.toml`: demo-scale betrayal adaptation spec.
- Create `configs/demo/alpha_sweep.toml`: demo-scale alpha sweep spec.
- Modify `configs/README.md`: document `demo/`, `paper_reproduce/`, `diagnostics/`, `smoke/`, `benchmark/`.
- Modify `scripts/README.md`: document `run.py` as the only public experiment-running CLI.
- Modify `tests/test_scripts_smoke.py`: test demo config dry-run through `run.py`.
- Modify `tests/test_supported_surface.py`: include demo configs and verify old wrapper scripts are not the public surface.
- Delete or migrate: `scripts/experiment/paper.py`, `scripts/experiment/smoke.py`,
  `scripts/experiment/preliminary.py`, and other experiment-running wrappers
  once their behavior is represented by configs plus `run.py`.
- Create `tests/test_results_surface.py`: validate public result scaffold contracts and gitignore behavior where possible.
- Create `notebooks/demo.ipynb`: runnable notebook that runs demo-scale experiments and plots compact outputs.
- Modify `README.md`: public front door.
- Create `docs/reproduce.md` as the canonical public reproduction route. Keep
  `docs/paper/REPRODUCE.md` only as a short pointer if compatibility is useful
  during the cleanup branch.
- Modify `docs/results/README.md`, `docs/results/current.md`: concise public evidence map.
- Modify `docs/paper/README.md` and selected `docs/paper/notes/*.md`: shrink paper docs to manuscript-facing notes and point general result interpretation to `docs/results/`.
- Create tracked public result directories:
  - `results/README.md`
  - `results/paper/model_fitness/`
  - `results/paper/betrayal_adaptation/`
  - `results/paper/alpha_sweep/`
  - `results/paper/prior_factorial/`
  - `results/paper/forgiveness/`
  - `results/paper/mixed_volatility/`
  - selected diagnostic directories such as `results/diagnostics/policy_openness/`,
    `results/diagnostics/deployment/`, and `results/diagnostics/locality/`
- Create `docs/results/cleanup/local_results_cleanup_manifest_20260608.md`.
- Create `docs/results/cleanup/server_results_cleanup_manifest_20260608.md` before any remote mutation.

Do not create a reusable cleanup CLI unless the implementation proves a one-off manifest is too brittle.

---

### Task 1: Make `results/` Track Scaffolds And Summaries

**Files:**
- Modify: `.gitignore`
- Create: `tests/test_results_surface.py`

- [ ] **Step 1: Write failing tests for result scaffold expectations**

Create `tests/test_results_surface.py`:

```python
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


PUBLIC_RESULT_DIRS = [
    REPO_ROOT / "results/paper/model_fitness",
    REPO_ROOT / "results/paper/betrayal_adaptation",
    REPO_ROOT / "results/paper/alpha_sweep",
    REPO_ROOT / "results/paper/prior_factorial",
    REPO_ROOT / "results/paper/forgiveness",
    REPO_ROOT / "results/paper/mixed_volatility",
]


REQUIRED_MANIFEST_FIELDS = {
    "name",
    "category",
    "status",
    "config_paths",
    "source_run_paths",
    "raw_results_policy",
    "tracked_summary_files",
    "paper_use",
}


def test_public_paper_result_directories_have_required_artifacts():
    for result_dir in PUBLIC_RESULT_DIRS:
        assert (result_dir / "README.md").exists(), result_dir
        manifest_path = result_dir / "manifest.json"
        assert manifest_path.exists(), result_dir
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert REQUIRED_MANIFEST_FIELDS <= set(manifest), result_dir
        assert manifest["category"] == "paper"
        assert manifest["tracked_summary_files"], result_dir
        for relative_path in manifest["tracked_summary_files"]:
            assert (result_dir / relative_path).exists(), result_dir / relative_path


def test_raw_result_files_are_not_tracked_in_public_scaffold():
    for result_dir in PUBLIC_RESULT_DIRS:
        assert not (result_dir / "results.csv").exists(), result_dir
        assert not (result_dir / "results_partial.csv").exists(), result_dir
        assert not (result_dir / "checkpoint_manifest.json").exists(), result_dir
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_results_surface.py -q
```

Expected: FAIL because `results/paper/*` scaffold does not exist yet.

- [ ] **Step 3: Update `.gitignore` to allow scaffold files**

Modify the results block to:

```gitignore
# Local experiment outputs
results/**
!results/
!results/.gitkeep
!results/README.md
!results/paper/
!results/paper/**/
!results/diagnostics/
!results/diagnostics/**/
!results/**/README.md
!results/**/manifest.json
!results/**/metrics.csv
!results/**/summary.csv
!results/**/*.summary.csv
!results/**/*summary*.csv
!results/**/source_tables/
!results/**/source_tables/*.csv
!results/**/.gitkeep
results/**/results.csv
results/**/results_partial.csv
results/**/checkpoint_manifest.json
results/**/*checkpoint*
results/**/*.log
outputs/
artifacts/
```

- [ ] **Step 4: Verify gitignore behavior manually**

Run:

```bash
mkdir -p /tmp/affect_aif_ignore_check/results/paper/model_fitness
git check-ignore -v results/paper/model_fitness/results.csv
git check-ignore -v results/paper/model_fitness/results_partial.csv
git check-ignore -v results/paper/model_fitness/metrics.csv || true
```

Expected: `results.csv` and `results_partial.csv` are ignored; `metrics.csv` is not ignored.

- [ ] **Step 5: Commit task**

Commit after Task 2 passes, not now, because the test needs the scaffold.

---

### Task 2: Build The Public Paper Result Scaffold

**Files:**
- Create: `results/README.md`
- Create: `results/paper/*/README.md`
- Create: `results/paper/*/manifest.json`
- Create/copy: `results/paper/*/metrics.csv` or `summary.csv`
- Create: `docs/results/cleanup/local_results_cleanup_manifest_20260608.md`
- Test: `tests/test_results_surface.py`

- [ ] **Step 1: Map paper result sources**

Use this mapping:

| Public path | Source raw result | Compact source |
|---|---|---|
| `results/paper/model_fitness/` | `results/log_surprisal_h1_confirm_postfix_20260606/h1/reliability_vs_reward_confirm/results.csv` | `docs/paper/manuscript/source_tables/h1_*` |
| `results/paper/betrayal_adaptation/` | `results/log_surprisal_h5_confirm_postfix_20260604/h5/betrayal_reallocation_confirm/results.csv` | `docs/paper/manuscript/source_tables/h5_evidence_effect_summary.csv` plus H5 tables |
| `results/paper/alpha_sweep/` | `results/exp_a/results.csv` | `results/exp_a/metrics.csv` |
| `results/paper/prior_factorial/` | `results/exp_b/results.csv` | `results/exp_b/metrics.csv` |
| `results/paper/forgiveness/` | `results/exp_c/results.csv` | `results/exp_c/metrics.csv` |
| `results/paper/mixed_volatility/` | `results/exp_d/results.csv` | `results/exp_d/metrics.csv` |

- [ ] **Step 2: Create `results/README.md`**

Include:

```markdown
# Result Summaries

This directory is the public result scaffold. Git tracks compact summaries,
manifests, and README files. Full per-round trajectories named `results.csv`
are intentionally ignored and live on the server or Drive packet.

## Paper Results

- `paper/model_fitness/`
- `paper/betrayal_adaptation/`
- `paper/alpha_sweep/`
- `paper/prior_factorial/`
- `paper/forgiveness/`
- `paper/mixed_volatility/`

## Diagnostics

`diagnostics/` contains complete informative non-paper runs that remain
runnable from public configs.
```

- [ ] **Step 3: Create each paper directory README**

Each `README.md` must state the same fields. Example for
`results/paper/model_fitness/README.md`:

```markdown
# Model Fitness

- Category: paper
- Role: model-fitness readout for predictability-over-reward evidence.
- Config: `configs/paper_reproduce/h1_model_fitness/reliability_vs_reward_confirm.toml`
- Full raw source: `results/log_surprisal_h1_confirm_postfix_20260606/h1/reliability_vs_reward_confirm/results.csv`
- Tracked summaries: `summary.csv` and `source_tables/*.csv`
- Raw policy: full per-round `results.csv` is ignored in git and retained on server/Drive.
```

- [ ] **Step 4: Create each `manifest.json`**

Use this schema:

```json
{
  "name": "model_fitness",
  "category": "paper",
  "status": "complete",
  "config_paths": [
    "configs/paper_reproduce/h1_model_fitness/reliability_vs_reward_confirm.toml"
  ],
  "source_run_paths": [
    "results/log_surprisal_h1_confirm_postfix_20260606/h1/reliability_vs_reward_confirm/results.csv"
  ],
  "raw_results_policy": "ignored_in_git_retained_on_server_and_drive",
  "tracked_summary_files": [
    "summary.csv"
  ],
  "paper_use": "Section 3.1 model-fitness readout"
}
```

Adjust `name`, paths, summaries, and `paper_use` per directory.

- [ ] **Step 5: Copy compact summaries**

Rules:

- If `results/exp_*/metrics.csv` exists, copy it to the matching public directory as `metrics.csv`.
- If only source-table CSVs exist, copy the relevant paper-used CSVs into `source_tables/` and add a short `summary.csv` with one row per copied source table.
- Do not copy raw `results.csv`.
- Do not copy `results_partial.csv` or checkpoint files.

- [ ] **Step 6: Write local cleanup manifest**

Create `docs/results/cleanup/local_results_cleanup_manifest_20260608.md` with sections:

- `Kept paper`
- `Kept diagnostics`
- `Archived on server only`
- `Deleted locally`
- `Not found locally`

For local deletion candidates, list partial/checkpoint/corrupt/dry-run files before deleting them.

- [ ] **Step 7: Run scaffold tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_results_surface.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

Run:

```bash
git add .gitignore tests/test_results_surface.py results/README.md results/paper docs/results/cleanup/local_results_cleanup_manifest_20260608.md
git commit -m "docs: add public result scaffold"
```

---

### Task 3: Build The Public Diagnostic Result Scaffold

**Files:**
- Create: `results/diagnostics/policy_openness/README.md`
- Create: `results/diagnostics/policy_openness/manifest.json`
- Create: `results/diagnostics/policy_openness/summary.csv`
- Create: `results/diagnostics/deployment/README.md`
- Create: `results/diagnostics/deployment/manifest.json`
- Create: `results/diagnostics/deployment/summary.csv`
- Create: `results/diagnostics/locality/README.md`
- Create: `results/diagnostics/locality/manifest.json`
- Create: `results/diagnostics/locality/summary.csv`
- Optional create: `results/diagnostics/social_allocation/`
- Optional create: `results/diagnostics/precision_profiles/`
- Modify: `tests/test_results_surface.py`
- Modify: `docs/results/cleanup/local_results_cleanup_manifest_20260608.md`

- [ ] **Step 1: Extend result-surface tests for diagnostics**

Modify `tests/test_results_surface.py`:

```python
PUBLIC_DIAGNOSTIC_DIRS = [
    REPO_ROOT / "results/diagnostics/policy_openness",
    REPO_ROOT / "results/diagnostics/deployment",
    REPO_ROOT / "results/diagnostics/locality",
]


def test_public_diagnostic_result_directories_have_required_artifacts():
    for result_dir in PUBLIC_DIAGNOSTIC_DIRS:
        assert (result_dir / "README.md").exists(), result_dir
        manifest_path = result_dir / "manifest.json"
        assert manifest_path.exists(), result_dir
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert REQUIRED_MANIFEST_FIELDS <= set(manifest), result_dir
        assert manifest["category"] == "diagnostic"
        assert manifest["tracked_summary_files"], result_dir
        for relative_path in manifest["tracked_summary_files"]:
            assert (result_dir / relative_path).exists(), result_dir / relative_path
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_results_surface.py::test_public_diagnostic_result_directories_have_required_artifacts -q
```

Expected: FAIL because diagnostic scaffolds do not exist yet.

- [ ] **Step 3: Map diagnostic sources**

Use this initial public diagnostic mapping:

| Public path | Source raw result | Config path | Role |
|---|---|---|---|
| `results/diagnostics/policy_openness/` | `results/log_surprisal_spine_smoke_postfix_20260528/h0/graded_choice/results.csv` | `configs/diagnostics/h0_policy_openness/graded_choice.toml` | policy openness and deployment-channel provenance |
| `results/diagnostics/deployment/` | `results/log_surprisal_spine_smoke_postfix_20260528/h2/lesion_open_regime/results.csv` | `configs/diagnostics/h2_deployment/lesion_open_regime.toml` | tracked-only deployment diagnostic |
| `results/diagnostics/locality/` | `results/h6_global_beta_locality_probe_20260526/h6/global_beta_locality_probe/results.csv` and `results/h6_global_beta_focal_switch_probe_20260526/h6/global_beta_focal_switch_probe/results.csv` | `configs/diagnostics/h3_locality/global_beta_locality_probe.toml`, `configs/diagnostics/h3_locality/global_beta_focal_switch_probe.toml` | local-vs-shared precision diagnostic |

Add `social_allocation` and `precision_profiles` only if compact source tables
are already available and can be documented without new interpretation.

- [ ] **Step 4: Create diagnostic README files**

Each README must include the same fields. Example:

```markdown
# Policy Openness

- Category: diagnostic
- Role: informative non-paper diagnostic for policy openness.
- Config: `configs/diagnostics/h0_policy_openness/graded_choice.toml`
- Full raw source: `results/log_surprisal_spine_smoke_postfix_20260528/h0/graded_choice/results.csv`
- Tracked summaries: `summary.csv`
- Raw policy: full per-round `results.csv` is ignored in git and retained on server/Drive when available.
```

- [ ] **Step 5: Create diagnostic manifests**

Use the same manifest schema as paper results with `category = "diagnostic"`
and `paper_use = "not_paper_evidence"`.

- [ ] **Step 6: Create diagnostic `summary.csv` files**

If no compact metric table exists, create a structural summary CSV with columns:

```text
label,source_run_path,config_path,rows,run_groups,variants,rounds,status,note
```

Populate `rows`, `run_groups`, `variants`, and `rounds` by reading the source
CSV. Do not add interpretive metrics unless they already exist in reviewed
source tables.

- [ ] **Step 7: Update local cleanup manifest**

List diagnostic runs under `Kept diagnostics` and note whether their full raw
trajectories remain local, server-only, or Drive-only.

- [ ] **Step 8: Run result-surface tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_results_surface.py -q
```

Expected: PASS.

- [ ] **Step 9: Commit**

Run:

```bash
git add results/diagnostics tests/test_results_surface.py docs/results/cleanup/local_results_cleanup_manifest_20260608.md
git commit -m "docs: add diagnostic result scaffold"
```

---

### Task 4: Add Demo Configs And Consolidate Run CLI

**Files:**
- Create: `configs/demo/model_fitness.toml`
- Create: `configs/demo/betrayal_adaptation.toml`
- Create: `configs/demo/alpha_sweep.toml`
- Modify: `configs/README.md`
- Modify: `scripts/README.md`
- Modify: `tests/test_scripts_smoke.py`
- Modify: `tests/test_supported_surface.py`

- [ ] **Step 1: Write failing demo config dry-run test**

Add to `tests/test_scripts_smoke.py`:

```python
def test_demo_configs_dry_run_through_run_py_writes_manifest(tmp_path):
    out = tmp_path / "results"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/experiment/run.py",
            "--config",
            "configs/demo/model_fitness.toml",
            "--config",
            "configs/demo/betrayal_adaptation.toml",
            "--config",
            "configs/demo/alpha_sweep.toml",
            "--output-dir",
            str(out),
            "--batch-name",
            "demo_dry",
            "--workers",
            "1",
            "--dry-run",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "demo_dry" / "manifest.json").read_text())
    assert manifest["batch_name"] == "demo_dry"
    assert [entry["experiment_id"] for entry in manifest["configs"]] == [
        "model_fitness_demo",
        "betrayal_adaptation_demo",
        "alpha_sweep_demo",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_scripts_smoke.py::test_demo_configs_dry_run_through_run_py_writes_manifest -q
```

Expected: FAIL because `configs/demo/*.toml` do not exist yet.

- [ ] **Step 3: Create demo configs**

Use reduced demo-scale specs:

- `model_fitness.toml`: copy from `configs/paper_reproduce/h1_model_fitness/reliability_vs_reward_confirm.toml`, set:
  - `[experiment].id = "model_fitness_demo"`
  - `[experiment].rounds = 40`
  - `[experiment].replications = 2`
  - `[experiment].seed = 101`
- `betrayal_adaptation.toml`: copy from `configs/paper_reproduce/h5_betrayal/betrayal_reallocation_confirm.toml`, set:
  - `[experiment].id = "betrayal_adaptation_demo"`
  - `[experiment].rounds = 50`
  - `[experiment].replications = 2`
  - `[experiment].seed = 202`
  - switch round to `16` if needed so the shock occurs inside the shortened run
- `alpha_sweep.toml`: create a compact graded trust spec using the same scenario as Exp A where possible, set:
  - `[experiment].id = "alpha_sweep_demo"`
  - `[experiment].rounds = 50`
  - `[experiment].replications = 2`
  - variants for `alpha_charge = 0.5`, `3.0`, and `8.0`

Keep `analysis.auto = true` only when the configured analysis supports the config at demo scale.

- [ ] **Step 4: Keep `scripts/experiment/run.py` as the only demo runner**

Do not create a new demo wrapper. If `scripts/experiment/run.py` cannot dry-run all three demo configs with repeated `--config`, extend `run.py` directly while preserving its existing repeated-config behavior.

Run command to preserve as the public demo route:

```bash
python scripts/experiment/run.py \
  --config configs/demo/model_fitness.toml \
  --config configs/demo/betrayal_adaptation.toml \
  --config configs/demo/alpha_sweep.toml \
  --output-dir results \
  --batch-name demo \
  --workers 1 \
  --dry-run
```

- [ ] **Step 5: Update supported-surface tests**

In `tests/test_supported_surface.py`, add expectations that:

- `configs/demo/model_fitness.toml` exists and expands.
- `configs/demo/betrayal_adaptation.toml` exists and expands.
- `configs/demo/alpha_sweep.toml` exists and expands.
- `scripts/experiment/run.py --help` remains the public experiment-running help surface.

- [ ] **Step 6: Update docs**

Update `configs/README.md` and `scripts/README.md` to describe the demo route as public and fast.

- [ ] **Step 7: Delete or migrate legacy experiment-running wrappers**

Audit `scripts/experiment/` and remove public runner wrappers after docs/tests
use `run.py` directly:

```bash
find scripts/experiment -maxdepth 1 -type f -name '*.py' -print | sort
rg -n "scripts/experiment/(paper|smoke|preliminary|run_exp_|followup)" README.md docs scripts tests configs || true
```

Rules:

- Delete thin wrappers whose behavior is now a documented `run.py --config ...`
  command.
- For specialized Exp A-D runner scripts, first identify whether they only run
  experiments or also generate compact paper metrics/figures. Move reusable
  analysis/table generation into `scripts/analysis/` or documented artifact
  generation before deleting the runner entry point.
- Do not keep compatibility aliases.

Expected deletion candidates after migration:

```bash
git rm scripts/experiment/paper.py scripts/experiment/smoke.py scripts/experiment/preliminary.py
```

Only delete `scripts/experiment/run_exp_a_alpha_sweep.py`,
`scripts/experiment/run_exp_b_prior_factorial.py`,
`scripts/experiment/run_exp_c_forgiveness.py`,
`scripts/experiment/run_exp_d_mixed_volatility.py`, or
`scripts/experiment/followup_phenotypes.py` after their unique output logic has
a new home or is proven unnecessary for public reproduction.

- [ ] **Step 8: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_scripts_smoke.py tests/test_supported_surface.py -q
.venv/bin/python scripts/experiment/run.py --config configs/demo/model_fitness.toml --config configs/demo/betrayal_adaptation.toml --config configs/demo/alpha_sweep.toml --output-dir /tmp/affect_aif_demo_check --batch-name demo_dry_check --workers 1 --dry-run
```

Expected: tests pass; dry-run manifest is written.

- [ ] **Step 9: Commit**

Run:

```bash
git add configs/demo configs/README.md scripts/README.md tests/test_scripts_smoke.py tests/test_supported_surface.py scripts/experiment
git commit -m "feat: consolidate experiment running into run cli"
```

---

### Task 5: Create The Demo Notebook

**Files:**
- Create: `notebooks/demo.ipynb`
- Optional create: `notebooks/README.md`
- Test: `tests/test_notebook_surface.py` if lightweight notebook validation is needed.

- [ ] **Step 1: Create notebook outline**

Use sections:

1. Setup and install
2. Demo configs
3. Run demo experiments
4. Load generated outputs
5. Plot model-fitness, betrayal adaptation, and alpha-sweep summaries
6. Where to find full paper reproduction

- [ ] **Step 2: Notebook setup cell**

Include:

```python
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
if not (ROOT / "scripts" / "experiment" / "run.py").exists():
    raise RuntimeError("Run this notebook from the affect_aif repository root.")
```

- [ ] **Step 3: Notebook run cell**

Use:

```python
DEMO_OUT = ROOT / "results" / "notebook_demo"
cmd = [
    sys.executable,
    "scripts/experiment/run.py",
    "--config",
    "configs/demo/model_fitness.toml",
    "--config",
    "configs/demo/betrayal_adaptation.toml",
    "--config",
    "configs/demo/alpha_sweep.toml",
    "--output-dir",
    "results",
    "--batch-name",
    "notebook_demo",
    "--workers",
    "1",
]
subprocess.run(cmd, check=True)
```

- [ ] **Step 4: Notebook analysis cell**

Load all demo CSVs found under `results/notebook_demo/**/results.csv`, concatenate with pandas, and compute compact summary tables. Do not rely on full paper data.

- [ ] **Step 5: Notebook plotting cells**

Use matplotlib. Keep plots simple:

- line plot of mean precision/confidence signal by round for model fitness
- line plot of `q_pi_entropy` or partner choice behavior before/after betrayal
- line plot or bar plot of alpha variant summary metrics

- [ ] **Step 6: Validate notebook JSON**

Run:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
json.loads(Path("notebooks/demo.ipynb").read_text())
print("notebook json ok")
PY
```

Expected: prints `notebook json ok`.

- [ ] **Step 7: Optionally execute a smoke-sized notebook run**

Only run this if demo configs are known to finish quickly:

```bash
.venv/bin/python scripts/experiment/run.py --config configs/demo/model_fitness.toml --config configs/demo/betrayal_adaptation.toml --config configs/demo/alpha_sweep.toml --output-dir /tmp/affect_aif_notebook_demo --batch-name notebook_demo_check --workers 1
```

Expected: completes and writes three demo result groups.

- [ ] **Step 8: Commit**

Run:

```bash
git add notebooks/demo.ipynb notebooks/README.md
git commit -m "docs: add runnable demo notebook"
```

---

### Task 6: Streamline Public Docs

**Files:**
- Modify: `README.md`
- Create: `docs/reproduce.md`
- Modify: `docs/paper/REPRODUCE.md`
- Modify: `docs/README.md`
- Modify: `docs/results/README.md`
- Modify: `docs/results/current.md`
- Modify: `docs/paper/README.md`
- Modify: selected `docs/paper/notes/*.md`
- Modify: `docs/operations/cli.md`

- [ ] **Step 1: Create canonical reproduction doc**

Create `docs/reproduce.md` as the public canonical route, then make
`docs/paper/REPRODUCE.md` point to it or remove duplication.

- [ ] **Step 2: Update `README.md`**

Keep front door sections:

- Setup
- Run demo notebook
- Run demo configs through `run.py`
- Reproduce paper
- Result summaries
- Repository layout

Remove agent-facing prose from README unless it is required for public users.

- [ ] **Step 3: Update `docs/reproduce.md`**

Include commands:

```bash
python scripts/experiment/run.py --config configs/smoke/trust_smoke.toml --dry-run
python scripts/experiment/run.py --config configs/demo/model_fitness.toml --config configs/demo/betrayal_adaptation.toml --config configs/demo/alpha_sweep.toml --batch-name demo --workers 1
python scripts/experiment/run.py --config configs/paper_reproduce/h1_model_fitness/reliability_vs_reward_confirm.toml --config configs/paper_reproduce/h5_betrayal/betrayal_reallocation_confirm.toml --batch-name paper_core_confirm --workers 1 --dry-run
python scripts/analysis/analyze.py --results results/notebook_demo/h5/betrayal_adaptation_demo/results.csv --output-dir results/notebook_demo/h5/betrayal_adaptation_demo/analysis
```

Explain that full runs are expensive and should run on `server` under tmux/Mango.

- [ ] **Step 4: Move general result interpretation to `docs/results/`**

Do not change interpretations. Move or summarize existing reviewed paper notes into:

- `docs/results/README.md`
- `docs/results/current.md`
- `docs/results/runs/*.md`

Keep `docs/paper/notes/claims_and_evidence.md` if it remains useful for manuscript wording, but make it point to `docs/results/current.md` for general evidence status.

- [ ] **Step 5: Trim `docs/paper/README.md`**

Make it manuscript-specific:

- manuscript source
- figures and source tables
- claim wording guardrails
- build instructions

Remove broad repo-navigation and operational cleanup notes.

- [ ] **Step 6: Update stale references**

Run:

```bash
rg -n "configs/trust|docs/future|CLAUDE\\.md|experiment_manifest|post-fix|smoke" README.md docs scripts tests configs
```

Patch public docs to use:

- `configs/demo/`
- `configs/paper_reproduce/`
- `configs/diagnostics/`
- `docs/reproduce.md`
- `docs/results/`
- `AGENTS.md`

Keep `smoke` wording only for development sanity checks, not reader-facing manuscript claims.

- [ ] **Step 7: Run docs/status tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_docs_state.py tests/test_experiment_manifest.py tests/test_supported_surface.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

Run:

```bash
git add README.md docs configs scripts tests
git commit -m "docs: streamline public reproduction docs"
```

---

### Task 7: Clean Local Result Junk

**Files/Directories:**
- Modify ignored local files under `results/`
- Modify: `docs/results/cleanup/local_results_cleanup_manifest_20260608.md`

- [ ] **Step 1: Generate local cleanup candidate list**

Run:

```bash
find results -type f \( \
  -name 'results_partial.csv' -o \
  -name 'checkpoint_manifest.json' -o \
  -name '*.checkpoint.csv' -o \
  -name '.DS_Store' \
\) | sort > /tmp/affect_aif_local_result_junk.txt
find results -type d -name 'corrupt_checkpoint*' | sort >> /tmp/affect_aif_local_result_junk.txt
sed -n '1,240p' /tmp/affect_aif_local_result_junk.txt
```

Expected: only partial/checkpoint/corrupt/OS files are listed.

- [ ] **Step 2: Verify final CSV exists before deleting resume artifacts**

For each `results_partial.csv`, `checkpoint_manifest.json`, or
`*.checkpoint.csv`, check that the same result directory has a final
`results.csv` before deletion. `.DS_Store` and corrupt checkpoint directories
do not need a sibling final CSV.

```bash
while IFS= read -r path; do
  case "$path" in
    *results_partial.csv|*checkpoint_manifest.json|*.checkpoint.csv)
      dir="$(dirname "$path")"
      test -f "$dir/results.csv" || echo "RETAIN RESUME ARTIFACT, FINAL MISSING: $path"
      ;;
  esac
done < /tmp/affect_aif_local_result_junk.txt
```

Expected: no `RETAIN RESUME ARTIFACT` lines for files being deleted. If any
line appears, leave that file in place and document it.

- [ ] **Step 3: Update local cleanup manifest**

Append exact paths under `Deleted locally` and `Retained because final missing`.
For checkpoint files, record whether deletion is justified by a sibling final
`results.csv` or by an explicit dry-run/aborted/useless classification.

- [ ] **Step 4: Delete safe local junk**

Run only after Step 2:

```bash
while IFS= read -r path; do
  test -e "$path" || continue
  case "$path" in
    *results_partial.csv|*checkpoint_manifest.json|*.checkpoint.csv)
      dir="$(dirname "$path")"
      test -f "$dir/results.csv" && rm -f "$path"
      ;;
    *.DS_Store)
      rm -f "$path"
      ;;
    *corrupt_checkpoint*)
      rm -rf "$path"
      ;;
  esac
done < /tmp/affect_aif_local_result_junk.txt
```

- [ ] **Step 5: Verify local cleanup**

Run:

```bash
find results -type f \( -name 'results_partial.csv' -o -name 'checkpoint_manifest.json' -o -name '.DS_Store' \) | sort
find results -type d -name 'corrupt_checkpoint*' | sort
git status --short --ignored results | sed -n '1,180p'
```

Expected: no safe junk remains; raw `results.csv` files may still appear ignored.

- [ ] **Step 6: Commit tracked manifest updates**

Run:

```bash
git add docs/results/cleanup/local_results_cleanup_manifest_20260608.md
git commit -m "docs: record local result cleanup"
```

---

### Task 8: Produce Server Dry-Run Cleanup Manifest

**Files:**
- Create/modify: `docs/results/cleanup/server_results_cleanup_manifest_20260608.md`

- [ ] **Step 1: Confirm server state**

Run:

```bash
ssh server 'cd /Users/server/repos/affect_aif && git status --short --branch'
ssh server 'cd /Users/server/repos/affect_aif && find results -maxdepth 3 -type d | sort' > /tmp/affect_aif_server_result_dirs.txt
ssh server 'cd /Users/server/repos/affect_aif && find results -type f \( -name results_partial.csv -o -name checkpoint_manifest.json -o -name ".DS_Store" \) | sort' > /tmp/affect_aif_server_junk.txt
```

- [ ] **Step 2: Write server manifest**

Create `docs/results/cleanup/server_results_cleanup_manifest_20260608.md` with:

- `Keep as paper`
- `Keep as diagnostics`
- `Move to archive`
- `Delete junk`
- `Retain for finality logs`
- `Needs user review`

Seed it from known mapping:

- Paper: H1, H5, Exp A-D.
- Diagnostics: log-surprisal spine smoke, H3 precision sensitivity, H4 social choice paircheck, H6 locality/focal switch probes, reviewer controls if complete.
- Archive: pre-fix/superseded confirmation batches, aborted manuscript open social confirm, dry-run/check folders, old batch timestamp dirs if not informative.
- Delete junk: partials/checkpoints/corrupt/.DS_Store where final exists.

- [ ] **Step 3: Include exact proposed server commands but do not run them**

For each category, include draft commands in fenced blocks:

```bash
mkdir -p results/paper results/diagnostics results/archive
mv results/log_surprisal_h1_confirm_postfix_20260606 results/paper/model_fitness
mv results/log_surprisal_spine_smoke_postfix_20260528 results/diagnostics/spine_smoke
mv results/confirm_h0_h1_h2_h4_20260518 results/archive/pre_fix_confirmation_20260518
rm -f results/paper/model_fitness/h1/reliability_vs_reward_confirm/results_partial.csv
rm -rf results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/corrupt_checkpoint_20260522_093135
```

- [ ] **Step 4: Review manifest with user or implementation lead**

Stop here unless the user explicitly approves server mutation in the same turn.

- [ ] **Step 5: Commit manifest**

Run:

```bash
git add docs/results/cleanup/server_results_cleanup_manifest_20260608.md
git commit -m "docs: plan server result cleanup"
```

---

### Task 9: Apply Server Cleanup After Manifest Approval

**Files/Systems:**
- Remote: `/Users/server/repos/affect_aif/results/`
- Local: `docs/results/cleanup/server_results_cleanup_manifest_20260608.md`

- [ ] **Step 1: Re-check live server process state**

Run:

```bash
mango process list --project affect_aif 2>/dev/null || mango process list 2>/dev/null || true
ssh server 'tmux ls 2>/dev/null || true'
```

Expected: no live affect_aif experiments.

- [ ] **Step 2: Apply approved server moves/deletions**

Run only commands approved in Task 8. Prefer a single SSH script with `set -euo pipefail` and explicit paths.

- [ ] **Step 3: Verify server layout**

Run:

```bash
ssh server 'cd /Users/server/repos/affect_aif && find results -maxdepth 3 -type d | sort | sed -n "1,240p"'
ssh server 'cd /Users/server/repos/affect_aif && find results -type f \( -name results_partial.csv -o -name checkpoint_manifest.json -o -name ".DS_Store" \) | sort'
```

Expected: paper/diagnostics/archive layout exists; safe junk is gone.

- [ ] **Step 4: Update server cleanup manifest final section**

Record:

- commands executed
- timestamp
- verification output summary
- any retained exceptions

- [ ] **Step 5: Commit manifest update**

Run:

```bash
git add docs/results/cleanup/server_results_cleanup_manifest_20260608.md
git commit -m "docs: record server result cleanup"
```

---

### Task 10: Rebuild Drive Packet From Clean Server Layout

**Files/Directories:**
- Local/Drive packet: `/Users/harshilshah/Desktop/affect_aif_paper_results_for_andrew_20260608`
- Remote source: `/Users/server/repos/affect_aif/results/paper`
- Optional remote source: `/Users/server/repos/affect_aif/results/diagnostics`

- [ ] **Step 1: Re-sync paper results from server**

Use rsync from server to Desktop packet:

```bash
mkdir -p /Users/harshilshah/Desktop/affect_aif_paper_results_for_andrew_20260608/results
rsync -av --delete server:/Users/server/repos/affect_aif/results/paper/ \
  /Users/harshilshah/Desktop/affect_aif_paper_results_for_andrew_20260608/results/paper/
```

- [ ] **Step 2: Decide diagnostic payload size**

Measure diagnostics before choosing full-data versus summary-only sync:

```bash
ssh server 'cd /Users/server/repos/affect_aif && du -sh results/diagnostics 2>/dev/null || true'
```

If diagnostics full data are small enough, sync selected diagnostics. Otherwise sync only summaries:

```bash
rsync -av --include='*/' --include='README.md' --include='manifest.json' --include='metrics.csv' --include='summary*.csv' --include='*.summary.csv' --exclude='*' \
  server:/Users/server/repos/affect_aif/results/diagnostics/ \
  /Users/harshilshah/Desktop/affect_aif_paper_results_for_andrew_20260608/results/diagnostics/
```

- [ ] **Step 3: Update packet README**

Explain:

- `results/paper/` has full paper data.
- `results/diagnostics/` has selected informative diagnostics or summaries.
- Git tracks compact summaries/scaffolds; server/Drive hold full raw trajectories.

- [ ] **Step 4: Audit packet**

Run:

```bash
du -sh /Users/harshilshah/Desktop/affect_aif_paper_results_for_andrew_20260608
find /Users/harshilshah/Desktop/affect_aif_paper_results_for_andrew_20260608/results -maxdepth 3 -type d | sort
find /Users/harshilshah/Desktop/affect_aif_paper_results_for_andrew_20260608 -name '.DS_Store' -o -name 'results_partial.csv' -o -name 'checkpoint_manifest.json'
```

Expected: no junk files; size is reasonable for Drive.

---

### Task 11: Final Verification

**Files:**
- All touched repo files

- [ ] **Step 1: Run public dry-runs**

Run:

```bash
.venv/bin/python scripts/experiment/run.py --config configs/smoke/trust_smoke.toml --output-dir /tmp/affect_aif_public_check --batch-name smoke_dry --dry-run
.venv/bin/python scripts/experiment/run.py --config configs/demo/model_fitness.toml --config configs/demo/betrayal_adaptation.toml --config configs/demo/alpha_sweep.toml --output-dir /tmp/affect_aif_public_check --batch-name demo_dry --workers 1 --dry-run
.venv/bin/python scripts/experiment/run.py --config configs/paper_reproduce/h1_model_fitness/reliability_vs_reward_confirm.toml --config configs/paper_reproduce/h5_betrayal/betrayal_reallocation_confirm.toml --output-dir /tmp/affect_aif_public_check --batch-name paper_dry --workers 1 --dry-run
```

Expected: all return 0 and write manifests.

- [ ] **Step 2: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_scripts_smoke.py \
  tests/test_supported_surface.py \
  tests/test_results_surface.py \
  tests/test_docs_state.py \
  tests/test_experiment_manifest.py \
  -q
```

Expected: PASS.

- [ ] **Step 3: Run lint and diff checks**

Run:

```bash
.venv/bin/python -m ruff check scripts/experiment tests
git diff --check
```

Expected: PASS.

- [ ] **Step 4: Verify ignored raw result policy**

Run:

```bash
git check-ignore -v results/paper/model_fitness/results.csv
git check-ignore -v results/paper/model_fitness/results_partial.csv
git check-ignore -v results/paper/model_fitness/metrics.csv || true
git check-ignore -v results/diagnostics/policy_openness/results.csv
git check-ignore -v results/diagnostics/policy_openness/summary.csv || true
git status --short --ignored results | sed -n '1,160p'
```

Expected: raw result files ignored; compact summaries visible/tracked.

- [ ] **Step 5: Review changed files**

Run:

```bash
git status --short --branch
git log --oneline -5
```

Expected: intended cleanup commits only; no raw `results.csv` staged.

- [ ] **Step 6: Final commit if needed**

If previous tasks left uncommitted verification/doc updates:

```bash
git add README.md docs configs scripts tests results notebooks .gitignore
git commit -m "chore: finalize public reproduction cleanup"
```

---

## Execution Notes

- Use @superpowers:subagent-driven-development for implementation if parallelizing tasks.
- Keep workers on disjoint write sets:
  - Worker A: results scaffold and gitignore.
  - Worker B: demo configs, `run.py` consolidation, and CLI tests.
  - Worker C: docs cleanup.
  - Worker D: server dry-run manifest only.
- Do not let any worker mutate server results until the dry-run manifest is reviewed.
- Do not reinterpret scientific results. Move existing reviewed summaries and labels only.
- Do not restore old config path aliases.
- Do not stage raw `results.csv`, partial files, checkpoints, or logs.
