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
  --config configs/demo/01_predictability_value.toml \
  --batch-name demo_model_fitness \
  --workers 1
```

## Paper Dry-Run

```bash
python scripts/experiment/run.py \
  --config configs/paper/01_predictability_value.toml \
  --config configs/paper/02_deployment_ablation.toml \
  --config configs/paper/03_partner_selection.toml \
  --config configs/paper/04_betrayal_adaptation.toml \
  --config configs/paper/05a_alpha_sweep.toml \
  --config configs/paper/05b_prior_factorial.toml \
  --config configs/paper/05c_forgiveness.toml \
  --batch-name paper \
  --workers 1 \
  --dry-run
```

Remove `--dry-run` for the full paper execution. The paper suite is larger
than the demo notebooks; use `--workers 1` unless you intentionally want local
parallel execution.

Full per-round `results.csv` files are gitignored and retained outside git.
Compact public summaries and manifests live under `results/paper/` and
`results/diagnostics/`. Reviewer ladders, older H-card probes, and retained
non-paper controls are available under `configs/diagnostics/`; implemented
follow-up surfaces that moved out of the paper live under `configs/future/`.

## Result Data Packet

The full paper result packet is available at `ANONYMOUS_DATA_PACKET_URL`.

Use the tracked compact summaries for quick inspection and the anonymous data
packet when you need row-level `results.csv` files that are intentionally
omitted from git.

## Colab Route

Open `notebooks/demo.ipynb` or `notebooks/reproduce.ipynb` in Google Colab,
clone the repo in the first setup cell, and run cells top to bottom. The
notebooks write scratch outputs under `outputs/` before materializing canonical
paper paths.
