# Notebooks

- `demo.ipynb`: guided public walkthrough using `configs/demo/`. It explains
  the mechanism before each run, executes all seven demo configs by default,
  and displays mechanism snapshots, timecourses, compact analysis tables, and
  appendix-level profile readouts. Use this first when the goal is to
  understand what the model is doing.
- `reproduce.ipynb`: Colab/local paper reproduction notebook. It dry-runs all
  numbered `configs/paper/` specs to show the workload, then walks through
  Sections 3.1--3.5 one paper section at a time. Each section runs the relevant
  config into `outputs/`, materializes the fresh output into
  `results/paper/*/raw/`, regenerates analysis artifacts, and plots the local
  readout before moving on.

Both public notebooks avoid `.venv` and absolute local paths. In Colab they
clone the repo, install it into the runtime, report CPU/GPU/JAX devices, and
write scratch runs under `outputs/` before touching canonical `results/`. The
command-line scripts are the canonical execution surface; notebooks call those
scripts rather than implementing separate runners.

## Which Notebook To Use

Use `demo.ipynb` when you want a fast, readable proof that the project installs,
runs experiments, runs analysis, and produces plots. It is the better notebook
for first-time readers and for appendix-level intuition about gain, priors, and
forgiveness dynamics.

Use `reproduce.ipynb` when you want to regenerate the paper suite. It is more
expensive because each paper experiment is executed before its analysis cells.

## Colab Notes

- Runtime: CPU is enough for the small demo; GPU/JAX devices are detected and
  reported when present but are not required for correctness.
- Outputs: scratch runs go under `outputs/`; canonical materialized outputs go
  under `results/paper/*/raw/`.
- Data policy: row-level `results.csv` files are ignored by git. The notebook
  can still write them locally or export them to Drive.
- Public data packet: see root `README.md` (**Paper Result Data**).
- Source of truth: if a notebook cell and a CLI doc differ, prefer the CLI doc
  in `docs/experiments/running.md` and update the notebook.
- Scope: paper sections use `configs/paper/01_*` through `05c_*`; fast
  workflow checks stay under `configs/demo/`; reviewer controls and older
  H-card probes stay under `configs/diagnostics/`; future extensions stay under
  `configs/future/`.
