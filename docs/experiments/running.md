# Running Experiments

The canonical runner is `scripts/experiment/run.py`.

```bash
python scripts/experiment/run.py \
  --config configs/demo/model_fitness.toml \
  --batch-name demo \
  --workers 1
```

Use `--dry-run` to validate configs and write a manifest without running
experiments:

```bash
python scripts/experiment/run.py \
  --config configs/diagnostics/smoke/trust_smoke.toml \
  --output-dir /tmp/affect_aif_smoke_check \
  --batch-name smoke_dry \
  --dry-run
```

Inspect expansion without writing outputs:

```bash
python scripts/experiment/inspect.py --config configs/paper/alpha_sweep.toml
```

Outputs are written under:

```text
<output-dir>/<batch-name>/<hypothesis-id>/<experiment-id>/
```

Each completed run directory may contain `results.csv`, copied config TOML,
metadata, and configured analysis artifacts. Raw `results.csv` files are
gitignored in the public repo but retained locally and on `server`.

Post-hoc analysis:

```bash
python scripts/analysis/analyze.py \
  --results results/paper/model_fitness/raw/h1/reliability_vs_reward_confirm/results.csv \
  --output-dir /tmp/affect_aif_analysis
```
