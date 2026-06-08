# Paper Reproduction

Paper configs live under `configs/paper/`.

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

Remove `--dry-run` to run the full suite. These runs are intentionally larger
than the demos; keep `--workers 1` unless parallel local execution is intended.

Compact public summaries and manifests are tracked under `results/paper/`.
Raw trajectories are gitignored but retained locally and on `server`.
