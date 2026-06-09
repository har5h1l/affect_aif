# Reproduce The Public Results

This is the maintained public reproduction route. Start with the demo if you
want to verify installation quickly; use the paper suite when you want the full
set of paper-facing experiments.

Start with:

- `docs/experiments/running.md` for the runner and output layout.
- `docs/experiments/paper.md` for the full paper suite.
- `notebooks/README.md` for notebook choices.
- `notebooks/demo.ipynb` for a small run-and-analyze notebook.
- `notebooks/reproduce.ipynb` for the full reproduction notebook.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Smoke Dry-Run

```bash
python scripts/experiment/run.py \
  --config configs/diagnostics/smoke/trust_smoke.toml \
  --batch-name smoke_dry_check \
  --dry-run
```

## Demo Run

```bash
python scripts/experiment/run.py \
  --config configs/demo/model_fitness.toml \
  --batch-name demo_model_fitness \
  --workers 1
```

## Paper Dry-Run

```bash
python scripts/experiment/run.py \
  --config configs/paper/h1_model_fitness/reliability_vs_reward_confirm.toml \
  --config configs/paper/h5_betrayal/betrayal_reallocation_confirm.toml \
  --config configs/paper/alpha_sweep.toml \
  --config configs/paper/prior_factorial.toml \
  --config configs/paper/forgiveness.toml \
  --config configs/paper/mixed_volatility.toml \
  --batch-name paper \
  --workers 1 \
  --dry-run
```

Remove `--dry-run` for the full paper execution. The paper suite is larger
than the demo notebooks; use `--workers 1` unless you intentionally want local
parallel execution.

Full per-round `results.csv` files are gitignored and retained locally/server
side. Compact public summaries and manifests live under `results/paper/` and
`results/diagnostics/`.

## Colab Route

Open `notebooks/demo.ipynb` or `notebooks/reproduce.ipynb` in Google Colab,
clone the repo in the first setup cell, and run cells top to bottom. The
notebooks write scratch outputs under `outputs/` before materializing canonical
paper paths.
