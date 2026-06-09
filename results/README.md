# Result Summaries

This directory is the public result scaffold. Git tracks compact summaries,
manifests, and README files. Full per-round trajectories named `results.csv`
are intentionally ignored and live on the server or Drive packet.

For interpretation and provenance rules, see `docs/results/`.

## Paper Results

| Folder | Config | Tracked summary | Raw policy |
|---|---|---|---|
| `paper/model_fitness/` | `configs/paper/h1_model_fitness/reliability_vs_reward_confirm.toml` | `summary.csv` | `raw/` retained locally/server-side, ignored by git |
| `paper/betrayal_adaptation/` | `configs/paper/h5_betrayal/betrayal_reallocation_confirm.toml` | `summary.csv` | `raw/` retained locally/server-side, ignored by git |
| `paper/alpha_sweep/` | `configs/paper/alpha_sweep.toml` | `metrics.csv` | `raw/` retained locally/server-side, ignored by git |
| `paper/prior_factorial/` | `configs/paper/prior_factorial.toml` | `metrics.csv` | `raw/` retained locally/server-side, ignored by git |
| `paper/forgiveness/` | `configs/paper/forgiveness.toml` | `metrics.csv` | `raw/` retained locally/server-side, ignored by git |
| `paper/mixed_volatility/` | `configs/paper/mixed_volatility.toml` | `metrics.csv` | `raw/` retained locally/server-side, ignored by git |

## Diagnostics

`diagnostics/` contains compact summaries and manifests for informative
non-paper probes. The full diagnostic raw runs are retained on `server`; the
public configs under `configs/diagnostics/` remain runnable.

Tracked diagnostic cards:

- `diagnostics/policy_openness/`
- `diagnostics/deployment/`
- `diagnostics/locality/`

## Archive

`archive/` is ignored except for `.gitkeep`. It may exist locally or on server
for historical, incomplete, dry-run, or superseded material; it is not current
paper evidence.
