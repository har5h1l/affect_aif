# Configs

TOML configs are the public experiment surface. All maintained configs use the
same `ExperimentSpec` envelope and expand explicit `[[variants]]` into
seeded runs.

## Choose A Config

- `paper/`: paper evidence reproduction, including H1 model fitness, H5
  betrayal adaptation, and Exp A-D phenotype suites.
- `demo/`: fast notebook-sized configs for checking the workflow.
- `diagnostics/`: smoke checks, reviewer controls, and informative non-paper
  probes.

## Quick Checks

```bash
python scripts/experiment/run.py \
  --config configs/diagnostics/smoke/trust_smoke.toml \
  --batch-name smoke \
  --workers 1 \
  --dry-run
```

```bash
python scripts/experiment/run.py \
  --config configs/paper/alpha_sweep.toml \
  --batch-name alpha_dry \
  --workers 1 \
  --dry-run
```

## Paper Suite

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
