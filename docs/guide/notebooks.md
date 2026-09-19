# Notebooks

- `demo.ipynb`: guided public walkthrough using `configs/demo/`. It explains
  the mechanism before each run, executes the four core demo configs by default,
  and displays mechanism snapshots, timecourses, compact analysis tables, and
  short explanations of the results. Use this first when the goal is to understand
  what the model is doing. The default core route is 21 expanded runs; the
  opt-in appendix/profile route brings the full demo notebook to 42 expanded
  runs.
- `reproduce.ipynb`: Colab/local paper reproduction notebook. It dry-runs each
  numbered `configs/paper/` spec before running it, and walks through
  Sections 3.1--3.5 one paper section at a time. Each section runs the relevant
  config into `outputs/`, copies the output into
  `results/paper/*/raw/`, regenerates analysis artifacts, and plots the local
  readout before moving on.

Both public notebooks avoid `.venv` and absolute local paths. In Colab they
clone the repo, install it into the runtime, report CPU/GPU/JAX devices, and
write scratch runs under `outputs/` before copying paper runs into `results/`. The
notebooks use the same runner as the command-line scripts.

## Which Notebook To Use

Use `demo.ipynb` when you want a fast, readable proof that the project installs,
runs experiments, runs analysis, and produces plots. It is the better notebook
for first-time readers. Set `DEMO_ROUTE = "profiles"` in the route-control cell
when you also want appendix-level intuition about gain, priors, and forgiveness
dynamics.

Use `reproduce.ipynb` when you want to regenerate the paper suite. It is more
expensive because each paper experiment is executed before its analysis cells;
the full paper route is 1220 expanded runs.

## Colab Notes

- Runtime: CPU is enough for the small demo; GPU/JAX devices are detected and
  reported when present but are not required for correctness.
- Outputs: scratch runs go under `outputs/`; paper results go
  under `results/paper/*/raw/`.
- Data policy: row-level `results.csv` files are ignored by git. The notebook
  can still write them locally or export them to Drive.
- Published data: [results ZIP](../../paper_results.zip) and [checksum](../../paper_results.zip.sha256).
- Source of truth: if a notebook cell and a CLI doc differ, prefer the CLI doc
  in `docs/guide/running.md` and update the notebook.
- Scope: paper sections use `configs/paper/01_*` through `05c_*`; fast
  workflow checks stay under `configs/demo/`; additional checks and comparisons stay under `configs/diagnostics/`; future extensions stay under
  `configs/future/`.

## Public Checkout And Fresh Readouts

Both notebooks default to `https://github.com/har5h1l/affect_aif.git`, branch
`master`. Set `AFFECT_AIF_BRANCH` before the bootstrap cell to use another
branch, such as `pub-ready` before its merge. Local launches find the existing
checkout from either the repository root or `notebooks/` and preserve it.
Colab buttons target `master`, so they show the released notebook after merge.

The reproduction notebook runs the current configs and validates each core
result's settings and completeness before building summaries. Core tables are generated alongside the raw
results in `analysis/`. Profile figures and source tables go to
`outputs/notebook_paper_artifacts/`. It does not use the frozen manuscript
source tables as if they were freshly regenerated.

`RUN_EXPERIMENTS = False` reuses existing notebook batch outputs; it does not
fetch the public archive automatically. `MATERIALIZE_RESULTS = True` replaces
the corresponding local `results/paper/*/raw/` folders with those batch outputs.
Keep a separate checkout if you need to preserve another local run. Set
`RUN_ANALYSIS = False` only when the generated analysis files already exist.

The demo uses reduced configs and the same CLI/runtime; its plots do not verify
the paper's effect sizes. All seven paper configs expand to 1,220 runs; these
are substantial computations, not a quick notebook check.
