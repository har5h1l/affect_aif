# Public Reproducibility Surface Design

## Purpose

Turn the repository from an internal research cockpit into a public,
paper-facing reproducibility surface while preserving informative diagnostics
and full server-side provenance.

The public route should make it obvious how to run a small demo, reproduce the
paper experiments, find the compact result summaries used by the manuscript,
and understand which non-paper experiments remain informative.

## Context

The current repo has the correct scientific ingredients but too many overlapping
navigation layers:

- Paper-used results are mixed with diagnostics, historical runs, partial CSVs,
  checkpoints, dry-run output, and log folders.
- `docs/paper/notes/` mixes manuscript guardrails, result interpretation,
  provenance, and operational notes.
- Public configs are being split into `paper_reproduce`, `smoke`, and
  `diagnostics`, but the final demo/reproduction path is not yet fully
  documented.
- Full raw trajectories should remain out of git, while compact result
  summaries and directory scaffolds should be tracked so a clone has the same
  public shape as the server and Drive packet.

No new result interpretation should be invented during this cleanup. Move,
summarize, and label already-reviewed evidence; do not reinterpret fresh outputs
without user approval.

## Public Repository Surface

The top-level public route should be:

- `README.md`: short setup, demo notebook, reproduction route, result layout,
  and pointers to scripts/configs.
- `notebooks/demo.ipynb`: fast runnable notebook for demo-scale versions of
  core paper claims.
- `configs/demo/`: small notebook-friendly configs.
- `configs/paper_reproduce/`: full manuscript reproduction configs.
- `configs/diagnostics/`: complete informative non-paper experiments that
  remain publicly runnable.
- `configs/archive/` or documented archive notes for superseded configs that
  are no longer on the public run path.
- `scripts/experiment/run.py`: the single public experiment-running CLI.
  Demo, smoke, diagnostic, and paper workflows should be config sets and
  documented command examples, not separate wrapper scripts.
- `docs/results/`: public result interpretation, run maps, and compact evidence
  summaries.
- `docs/paper/`: manuscript source, figure/table provenance, and
  manuscript-specific claim guardrails.
- `docs/active/`: internal current-state and agent continuation surface; it
  should not be the public front door.

## Results Layout

`results/` remains the public result scaffold. Heavy raw data stay gitignored,
but lightweight summaries and directory structure are tracked.

Paper result directories should use human-readable names rather than seed counts
or hypothesis IDs:

```text
results/paper/model_fitness/
results/paper/betrayal_adaptation/
results/paper/alpha_sweep/
results/paper/prior_factorial/
results/paper/forgiveness/
results/paper/mixed_volatility/
```

Informative non-paper runs should live under:

```text
results/diagnostics/<human_name>/
```

Server-only historical material may live under:

```text
results/archive/<human_name>/
```

Tracked compact files may include:

- `README.md`
- `manifest.json`
- `metrics.csv`
- `summary.csv`
- named source-table or evidence-summary CSVs when one table is not enough
- `.gitkeep` only where a directory would otherwise be empty

Ignored heavy files include raw per-round trajectories such as `results.csv`,
partial CSVs, checkpoint manifests, logs, and generated run debris.

Each public result directory must include, at minimum:

- `README.md` with the public label, evidence role, config path, source raw run,
  and whether the directory is paper evidence, diagnostic evidence, or
  historical provenance.
- `manifest.json` with `name`, `category`, `status`, `config_paths`,
  `source_run_paths`, `raw_results_policy`, `tracked_summary_files`, and
  `paper_use` fields.
- At least one tracked compact evidence file:
  - `metrics.csv` when the experiment has a compact metric table.
  - `summary.csv` when no existing compact metric table exists.
  - named evidence/source-table CSVs when the manuscript uses multiple
    distinct tables for one result.

Every public result directory must allow an ignored raw `results.csv` to appear
after a local or server rerun without changing git status.

## Server And Drive Layout

The server should mirror the public result scaffold, but it may retain full raw
data:

- `results/paper/`: full paper-used raw trajectories plus compact summaries.
- `results/diagnostics/`: complete informative non-paper runs plus compact
  summaries.
- `results/archive/`: complete but superseded historical runs with short
  explanations.

The Google Drive packet should be produced from the cleaned server layout. It
can include full paper data and selected diagnostic summaries or full data,
depending on size and sharing need. The packet README should state that git
tracks compact summaries and scaffolds, while server/Drive hold full raw
trajectories.

Implementation should use an explicit safety checkpoint:

1. Build the repo result scaffold, config layout, notebook/CLI docs, and local
   cleanup manifest first.
2. Produce a server dry-run cleanup manifest that lists every folder to keep,
   move to `results/paper`, move to `results/diagnostics`, move to
   `results/archive`, or delete.
3. Mutate the server results tree only after the manifest has been reviewed in
   the implementation turn or explicitly approved by the user.
4. Build the Drive packet from the cleaned server tree after server cleanup is
   complete.

## Cleanup Rules

Keep:

- complete paper-used experiments
- complete informative diagnostics that still clarify boundaries, reviewer
  controls, or rejected stronger claims
- compact tracked summaries and manifests
- configs for every public runnable paper, demo, or diagnostic experiment

Archive on server:

- complete but superseded historical runs
- complete runs whose interpretation changed because the model or config was
  superseded
- log folders retained only for finality/provenance

Each archived run should have a short note explaining what happened and why it
is not front-door evidence.

Delete from local and server when safe:

- `results_partial.csv` when a final `results.csv` exists
- `checkpoint_manifest.json` when resume is no longer needed
- corrupt checkpoint directories
- `.DS_Store`
- dry-run output folders
- aborted or incomplete folders with no valid final result
- empty batch/log junk not referenced by provenance docs

## Notebook Plan

Create `notebooks/demo.ipynb` as the main presentation and transparency
artifact. It should actually run experiments, not only analyze included
results.

The notebook should run demo-scale versions of a few core claims with reduced
seeds and rounds:

- model fitness: affect tracks predictability more than reward
- betrayal adaptation: affect changes deployment under abrupt partner change
- alpha sweep: affect gain changes trust dynamics

The notebook should generate compact plots and tables directly in the notebook.
It should point to full paper configs and results for production-scale
reproduction, but it does not need to compare generated demo output against the
paper summaries.

A future `notebooks/full_reproduction.ipynb` is optional. Full reproduction can
remain CLI-first unless the notebook can stay clear and computationally honest.

## CLI And Config Design

Consolidate experiment execution into `scripts/experiment/run.py`. Delete or
migrate other experiment-running wrappers once their behavior is represented by
TOML configs, documented `run.py` commands, or notebook cells.

The public experiment CLI should be:

```bash
python scripts/experiment/run.py --config configs/smoke/trust_smoke.toml --dry-run
python scripts/experiment/run.py --config configs/demo/model_fitness.toml --config configs/demo/betrayal_adaptation.toml --config configs/demo/alpha_sweep.toml --batch-name demo --workers 1
python scripts/experiment/run.py --config configs/paper_reproduce/h1_model_fitness/reliability_vs_reward_confirm.toml --config configs/paper_reproduce/h5_betrayal/betrayal_reallocation_confirm.toml --batch-name paper_core_confirm --workers 1 --dry-run
python scripts/experiment/run.py --config configs/diagnostics/<path>.toml
python scripts/analysis/analyze.py --results <path>/results.csv --output-dir <path>/analysis
```

Public config groups:

- `configs/demo/`: fast demo-scale configs used by `notebooks/demo.ipynb` and
  direct `scripts/experiment/run.py` commands.
- `configs/paper_reproduce/`: full paper configs.
- `configs/diagnostics/`: complete informative non-paper configs.
- `configs/smoke/`: minimal development sanity checks.
- `configs/benchmark/`: benchmark arena configs.
- `configs/archive/` or archive documentation: superseded configs not meant as
  public runnable surfaces.

Do not keep compatibility aliases for old config paths or old wrapper script
entry points. If a legacy script contains unique experiment-generation logic,
move that logic into TOML configs, analysis code, or documented `run.py`
invocations before deleting it.

## Documentation Design

Simplify public docs around four questions:

1. How do I run the demo?
2. How do I reproduce the paper?
3. Where are the result summaries?
4. Which diagnostics are informative but not paper evidence?

Recommended structure:

- `README.md`: short public front door.
- `docs/reproduce.md` or `docs/paper/REPRODUCE.md`: canonical reproduction
  route, including demo, full paper CLI, server/Drive artifact expectations,
  and tracked-vs-ignored results.
- `docs/results/README.md`: result-map index.
- `docs/results/current.md`: concise claim-oriented evidence summary.
- `docs/results/runs/`: provenance for retained historical or diagnostic runs.
- `docs/paper/`: manuscript source, figures/tables, and paper-specific
  guardrails only.
- `docs/active/`: internal agent/current-state surface.

Move general result interpretation out of `docs/paper/notes/` into
`docs/results/`. Keep paper notes only when they directly guide manuscript
writing, claim wording, figures, or tables.

## Error Handling And Safety

- Do not delete raw data until the final CSV or compact summary has been
  verified.
- Before server cleanup, confirm there are no live affect_aif experiments via
  Mango/tmux/process checks.
- Prefer dry-run cleanup manifests before deletion.
- Record every archived or deleted top-level run in a cleanup manifest.
- Keep cleanup scripts local or one-off unless a reusable public maintenance
  command is clearly justified.

## Verification

Before implementation is considered complete:

```bash
.venv/bin/python scripts/experiment/run.py --config configs/demo/model_fitness.toml --config configs/demo/betrayal_adaptation.toml --config configs/demo/alpha_sweep.toml --batch-name demo_dry_check --dry-run
.venv/bin/python scripts/experiment/run.py --config configs/paper_reproduce/h1_model_fitness/reliability_vs_reward_confirm.toml --config configs/paper_reproduce/h5_betrayal/betrayal_reallocation_confirm.toml --batch-name paper_dry_check --workers 1 --dry-run
.venv/bin/python scripts/experiment/run.py --config configs/smoke/trust_smoke.toml --batch-name smoke_dry_check --dry-run
.venv/bin/python -m pytest tests/test_scripts_smoke.py tests/test_supported_surface.py -q
.venv/bin/python -m ruff check scripts/experiment tests
git diff --check
```

If result scaffolds or gitignore rules change, also verify:

```bash
git check-ignore -v results/paper/model_fitness/results.csv
git check-ignore -v results/paper/model_fitness/metrics.csv || true
git status --short --ignored results | sed -n '1,120p'
```
