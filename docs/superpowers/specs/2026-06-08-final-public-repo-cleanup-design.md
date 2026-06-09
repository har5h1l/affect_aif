# Final Public Repo Cleanup Design

Date: 2026-06-08

## Goal

Make the repository public-readable and paper-reproducible without losing the
useful maintainer state needed before final publication. The cleaned surface
should make it obvious what the project is, how to install it, how to run a
small demo, how to reproduce the paper experiments, where analysis lives, and
where manuscript materials live.

## Principles

- The public route starts at `README.md` and points to a small set of focused
  docs. It should not require reading active agent state, historical manifests,
  or paper drafting notes.
- `scripts/experiment/run.py` is the only maintained experiment runner.
  Experiment identity comes from TOML configs, not wrapper scripts.
- Analysis code computes metrics, summaries, figures, and configured analysis
  artifacts from result files. It does not launch experiments.
- Full raw result data stays ignored. Compact summaries, manifests, and
  paper-used source tables stay tracked.
- `docs/active/` and `docs/handoffs/` remain in the repo for now, but they are
  maintainer/agent state rather than the public reading path.
- Benchmark code/config/docs are removed from the active surface. The trust-task
  benchmark arena is not used in the paper and can be restored later from the
  archive branch if needed.

## Final Top-Level Surface

```text
README.md
AGENTS.md
configs/
  paper/
  demo/
  diagnostics/
docs/
  model/
  experiments/
  results/
  manuscript/
  active/
  handoffs/
notebooks/
  demo.ipynb
  reproduce.ipynb
results/
  paper/
  diagnostics/
scripts/
  experiment/run.py
  experiment/inspect.py
  analysis/analyze.py
  analysis/phenotype_artifacts.py
analysis/
experiments/
tasks/
tests/
```

`results/archive/` may exist locally or on the server, but it should be ignored
and should not be a tracked public result surface.

## Config Layout

Use intent-based config folders:

```text
configs/
  paper/
    h1_model_fitness/reliability_vs_reward_confirm.toml
    h5_betrayal/betrayal_reallocation_confirm.toml
    alpha_sweep.toml
    prior_factorial.toml
    forgiveness.toml
    mixed_volatility.toml
  demo/
    model_fitness.toml
    betrayal_adaptation.toml
    alpha_sweep.toml
  diagnostics/
    smoke/trust_smoke.toml
    h0_policy_openness/
    h1_model_fitness/
    h2_deployment/
    h3_locality/
    h4_social_allocation/
    h5_timescale_volatility/
    h6_perturbation/
```

Rename `configs/paper_reproduce/` to `configs/paper/`. Fold
`configs/smoke/trust_smoke.toml` into `configs/diagnostics/smoke/`.
Remove `configs/benchmark/`.

## CLI Surface

Keep:

- `scripts/experiment/run.py`
- `scripts/experiment/inspect.py`
- `scripts/analysis/analyze.py`
- `scripts/analysis/phenotype_artifacts.py`

Remove:

- `scripts/benchmark/`
- historical experiment wrapper scripts
- any docs/tests/package references that present benchmark as supported

The root README and `docs/experiments/running.md` should show the supported
commands. Benchmark commands should disappear from public docs and tests.

## Docs Layout

Make docs audience-based rather than history-based:

```text
docs/
  README.md
  model/
    README.md
    pomdp.md
    affective_precision.md
    hypotheses.md
  experiments/
    README.md
    running.md
    configs.md
    paper.md
    diagnostics.md
  results/
    README.md
    current.md
    paper.md
    diagnostics.md
    cleanup/
  manuscript/
    README.md
    main.tex
    sections/
    appendix/
    figures/
    source_tables/
    references.bib
    notes/
      claims_and_evidence.md
      figures_tables.md
      limitations.md
  active/
  handoffs/
```

Consolidate old folders as follows:

- `docs/theory/pomdp_spec.md` -> `docs/model/pomdp.md`, simplified.
- `docs/theory/hypotheses.md` -> `docs/model/hypotheses.md`.
- useful parts of `docs/theory/goals.md` and `docs/theory/theory.md` ->
  `docs/model/README.md` or `docs/model/affective_precision.md`.
- useful parts of `docs/design/implementation.md` and
  `docs/design/partner_stance.md` -> `docs/model/pomdp.md` and
  `docs/experiments/running.md`.
- `docs/experiment/config_schema.md` -> `docs/experiments/configs.md`.
- `docs/experiment/design.md` -> split into `docs/experiments/paper.md` and
  `docs/experiments/diagnostics.md`.
- `docs/experiments/manifest.md` -> fold into `docs/experiments/README.md` or
  `docs/experiments/paper.md`.
- `docs/operations/cli.md` -> `docs/experiments/running.md`.
- `docs/operations/benchmark.md` -> delete with benchmark.
- `docs/decisions/*` -> fold useful decisions into `docs/model/` and
  `docs/experiments/`; delete `docs/decisions/`.
- `docs/archive/` -> ignore or leave empty; it should not be part of the
  public route.

## Manuscript Layout

Rename `docs/manuscript/` to `docs/manuscript/` and prune it to paper-adjacent
material:

```text
docs/manuscript/
  README.md
  main.tex
  sections/
  appendix/
  figures/
  source_tables/
  references.bib
  notes/
    claims_and_evidence.md
    figures_tables.md
    limitations.md
```

Remove or move:

- delete `docs/manuscript/prompts/`
- delete `docs/manuscript/REPRODUCE.md`
- move `notes/model_spec.md` into `docs/model/`
- fold `notes/experiment_manifest.md` and `notes/reproducibility.md` into
  `docs/experiments/`
- fold `notes/result_provenance.md` into `docs/results/`
- fold or delete `notes/literature_positioning.md` depending on current value

Appendix stays inside the manuscript folder because it is part of the paper
source, not a top-level docs concept.

## Results Layout

The results tree is the bridge between runnable configs, ignored full data, and
tracked public summaries. The repo should be cloneable with the directory
scaffold and compact summaries present, while full per-round CSVs stay outside
git on local/server/Drive.

Keep this canonical structure locally and on `server`:

```text
results/
  README.md
  paper/
    model_fitness/
      README.md
      manifest.json
      summary.csv
      source_tables/
      raw/
    betrayal_adaptation/
      README.md
      manifest.json
      summary.csv
      source_tables/
      raw/
    alpha_sweep/
      README.md
      manifest.json
      metrics.csv
      raw/
    prior_factorial/
      README.md
      manifest.json
      metrics.csv
      raw/
    forgiveness/
      README.md
      manifest.json
      metrics.csv
      raw/
    mixed_volatility/
      README.md
      manifest.json
      metrics.csv
      raw/
  diagnostics/
    policy_openness/
      README.md
      manifest.json
      summary.csv
    deployment/
      README.md
      manifest.json
      summary.csv
    locality/
      README.md
      manifest.json
      summary.csv
    smoke/
      README.md
      manifest.json
      summary.csv
      raw/
    precision_sensitivity/
      README.md
      manifest.json
      summary.csv
      raw/
    social_allocation/
      README.md
      manifest.json
      summary.csv
      raw/
  archive/
```

Track:

- `README.md`
- `manifest.json`
- compact `summary.csv` and `metrics.csv`
- paper-used source-table CSVs

Ignore:

- `raw/`
- full per-round `results.csv`
- `results/archive/`
- checkpoints, partial CSVs, and logs

Do not delete completed full experiment data during cleanup. Moves and renames
should preserve final raw CSVs and analysis artifacts unless the run is clearly
incomplete, corrupt, or explicitly obsolete. For incomplete/corrupt runs,
delete checkpoints and partial CSVs, and document the archival decision in
`docs/results/cleanup/`.

### Result-to-Config Hook

Every tracked result folder needs a `manifest.json` that connects it back to
the config(s) that produce it:

```json
{
  "name": "alpha_sweep",
  "category": "paper",
  "status": "complete",
  "config_paths": ["configs/paper/alpha_sweep.toml"],
  "source_run_paths": ["results/paper/alpha_sweep/raw/results.csv"],
  "raw_results_policy": "gitignored_retained_locally_and_on_server",
  "tracked_summary_files": ["metrics.csv"],
  "paper_use": "Section 3.6.1 alpha sweep profile readout"
}
```

For diagnostics, the same contract applies, but `paper_use` should make clear
that the run is informative or reviewer-facing rather than primary manuscript
evidence.

### Local, Server, and Drive Policy

- Local repo: keep full paper raw data and useful diagnostic raw data under the
  same canonical `results/` layout. Raw files are gitignored.
- Server repo: keep the same canonical layout plus fuller `results/archive/`
  for extensive historical, dry-run, log, and incomplete material. The server
  can retain more than local, but not under confusing top-level names.
- Drive handoff: the user should be able to copy the local `results/` folder
  into Drive. Therefore local `results/` must be clean enough to share:
  paper raw data under `results/paper/*/raw/`, compact diagnostics under
  `results/diagnostics/`, no checkpoints, no partial CSVs, no stale
  `exp_a`/`exp_b`/`log_surprisal_*` top-level folders.

### Naming Rules

- Use semantic result folder names (`alpha_sweep`, `model_fitness`,
  `betrayal_adaptation`) rather than historical batch IDs (`exp_a`,
  `log_surprisal_h5_confirm_postfix_20260604`).
- Keep seeds, timestamps, and run-recovery details inside manifests/logs, not
  in the public folder name.
- The top-level result categories are `paper`, `diagnostics`, and local/server
  `archive` only.

## Notebooks

Keep two public notebooks:

- `notebooks/demo.ipynb`: runs small demo configs through
  `scripts/experiment/run.py`, loads generated outputs, and plots compact
  summaries.
- `notebooks/reproduce.ipynb`: full paper reproduction route using
  `configs/paper/*`, with an explicit dry-run cell and runtime warnings before
  the full command.

## README Contract

The root `README.md` should be the public front door and answer, in order:

1. What this repo is: a trust-task active-inference model using official
   `inferactively-pymdp`, studying partner-local affective precision as a
   confidence/model-fitness signal in social trust.
2. How the repo works: `tasks/trust`, `experiments/trust`, `configs`,
   `analysis`, `results`, and `docs`.
3. Setup:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

4. Quick demo command.
5. Paper reproduction command and pointer to `docs/experiments/paper.md`.
6. Analysis commands and note that analysis never launches experiments.
7. Where to go next:
   - model details: `docs/model/`
   - running experiments: `docs/experiments/`
   - current evidence: `docs/results/`
   - manuscript source: `docs/manuscript/`
   - maintainer state: `docs/active/`, `docs/handoffs/`

Subfolder READMEs should be practical route maps, not historical inventories.

## Verification

After implementation:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
python scripts/experiment/run.py --config configs/diagnostics/smoke/trust_smoke.toml --dry-run
python scripts/experiment/run.py --config configs/paper/alpha_sweep.toml --dry-run
```

Also verify:

- no references to deleted benchmark paths in public docs/tests/package config
- no references to `configs/paper_reproduce/`
- no references to top-level `configs/smoke/`
- no public docs route through `docs/active/` or `docs/handoffs/` by default
- no generated caches, checkpoint manifests, partial CSVs, or raw result files
  are tracked
