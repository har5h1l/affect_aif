# Running Experiments

The canonical runner is `scripts/experiment/run.py`.

```bash
python scripts/experiment/run.py \
  --config configs/demo/01_predictability_value.toml \
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
python scripts/experiment/inspect.py --config configs/paper/05a_alpha_sweep.toml
```

For repeated same-shape local runs, opt into JAX's persistent compilation cache:

```bash
python scripts/experiment/run.py \
  --config configs/demo/05c_forgiveness.toml \
  --output-dir outputs \
  --batch-name forgiveness_cached \
  --workers 1 \
  --jax-cache-dir /tmp/affect_aif_jax_cache
```

The cache changes compilation reuse only; it must not change seeds, expanded
variants, model parameters, observations, actions, or result rows.

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
  --results results/paper/04_betrayal_adaptation/raw/betrayal_adaptation/betrayal_adaptation/results.csv \
  --output-dir /tmp/affect_aif_analysis
```

## Notebook Route

Use `notebooks/demo.ipynb` for a small run-and-analyze workflow. Use
`notebooks/reproduce.ipynb` for the full paper suite. Both notebooks are
Colab-compatible and call the same CLI scripts shown here.

## Choosing An Output Directory

For throwaway local checks, write under `/tmp` or `outputs/`:

```bash
python scripts/experiment/run.py \
  --config configs/demo/01_predictability_value.toml \
  --output-dir outputs \
  --batch-name demo_model_fitness
```

For canonical paper materialization, use the `results/paper/.../raw/` layout
documented in `docs/results/paper.md`. Binary model-fitness probes use
`results/diagnostics/model_fitness/` instead. Raw files are gitignored, while
the compact `summary.csv`, `metrics.csv`, `manifest.json`, and README files are
tracked.

## What The Runner Does Not Run

`scripts/experiment/run.py` intentionally executes only the maintained
focal-agent trust TOML surface (`family = "trust"`). The
`experiments/multifocal/` package contains a tested reciprocal AIF-vs-AIF
prototype with JSON configs under `experiments/multifocal/configs/`, but that
code is future work. It is not part of the paper reproduction command, demo
notebooks, or canonical result layout yet.
