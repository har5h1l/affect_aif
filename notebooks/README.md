# Notebooks

- `demo.ipynb`: Colab/local workflow demo using `configs/demo/`. It runs real
  demo experiments, runs post-hoc analysis, plots payoff/entropy readouts, and
  prints demo-scale interpretation snippets.
- `reproduce.ipynb`: Colab/local paper reproduction notebook. It dry-runs all
  `configs/paper/` specs to show the workload, then runs the full paper configs
  into `outputs/paper_full/`, materializes those fresh outputs into
  `results/paper/*/raw/`, regenerates analysis artifacts, plots paper readouts,
  and can export `results/` to Google Drive.

Both public notebooks avoid `.venv` and absolute local paths. In Colab they
clone the repo, install it into the runtime, report CPU/GPU/JAX devices, and
write scratch runs under `outputs/` before touching canonical `results/`. The
command-line scripts are the canonical execution surface; notebooks call those
scripts rather than implementing separate runners.
