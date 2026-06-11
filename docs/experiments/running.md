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

## Execution Modes

Config folders and runtime profiles answer different questions. Folders such
as `paper/`, `demo/`, `diagnostics/`, and `future/` define evidence role.
`[runtime].profile` defines how heavy the execution should be.

The runner currently has these execution paths:

- `--dry-run`: validates config expansion and writes a manifest without
  simulating episodes.
- `--workers 1`: runs inline in the current process, which is the simplest
  deterministic local path and avoids process-pool startup overhead.
- `--workers N` for `N > 1`: runs expanded variant/replication tasks through a
  process pool and keeps the same per-config output and checkpoint layout.
- `profile = "data_collection"`: the default maintained-config profile; writes
  manuscript-facing per-round result rows and compact checkpoints as quickly
  as the configured model allows. This profile keeps payoff, choice,
  entropy, beta, surprise/log-evidence, inference-correctness, switch, seed,
  variant, and config metadata needed by the paper analyses, while omitting
  bulky diagnostic-only policy and belief tensors.
- `--verbose --verbosity-mode stage_stream`: emits structured per-stage
  progress for serial and single-worker inline runs, and batch-level progress
  for multi-worker runs.
- `profile = "debug"`: enables policy-trace logging and full diagnostic
  internals such as `q_pi`, `G`, policy-step costs, partner belief matrices,
  and posterior tensors. Do not use it for statistical data collection because
  these arrays can make checkpoints and CSVs very large.
- post-hoc analysis: run `scripts/analysis/*` after data collection. Keep
  `[analysis].auto = false` for maintained data-collection configs; enable it
  only for narrow local configs where immediate summaries matter more than
  throughput.

JAX persistent compilation caching is enabled by default at
`/tmp/affect_aif_jax_cache` because it is exact-preserving and speeds repeated
same-shape local checks and paper reruns. Use `--jax-cache-dir` to choose
another cache directory, or `--no-jax-cache` for a one-off uncached check:

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
Result rows and `batch_metadata.json` record config paths as resolved absolute
paths so provenance does not depend on whether a run used the serial,
single-worker inline, or multi-worker batch path.

Runner diagnostics are assembled in `experiments/trust/diagnostics.py`, while
POMDP matrices are assembled in `tasks/trust/pomdp_matrices.py` and wrapped by
`tasks/trust/pomdp.py`. These modules are structural boundaries only: changing
them should be verified by comparing fixed-seed data-collection and debug
`results.csv` hashes against the previous implementation before treating the
change as experiment-preserving.

The current runtime optimization audit is recorded in
`docs/results/runtime_optimization_audit_20260611.md`.

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
