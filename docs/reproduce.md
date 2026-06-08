# Reproduce The Public Results

This is a short pointer to the maintained public reproduction route.

Start with:

- `docs/experiments/running.md` for the runner and output layout.
- `docs/experiments/paper.md` for the full paper suite.
- `notebooks/reproduce.ipynb` for a notebook checklist.

Smoke dry-run:

```bash
python scripts/experiment/run.py \
  --config configs/diagnostics/smoke/trust_smoke.toml \
  --batch-name smoke_dry_check \
  --dry-run
```

Paper dry-run:

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

Full per-round `results.csv` files are gitignored and retained locally/server
side. Compact public summaries and manifests live under `results/paper/` and
`results/diagnostics/`.
