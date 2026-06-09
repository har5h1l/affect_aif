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

## Paper Suite Map

| Paper section | Config | Result folder | Summary files |
|---|---|---|---|
| Model fitness / predictability over reward | `configs/paper/h1_model_fitness/reliability_vs_reward_confirm.toml` | `results/paper/model_fitness/` | `summary.csv`, `manifest.json` |
| Betrayal adaptation | `configs/paper/h5_betrayal/betrayal_reallocation_confirm.toml` | `results/paper/betrayal_adaptation/` | `summary.csv`, `manifest.json` |
| Precision-gain profiles | `configs/paper/alpha_sweep.toml` | `results/paper/alpha_sweep/` | `metrics.csv`, `manifest.json` |
| Prior x gain profiles | `configs/paper/prior_factorial.toml` | `results/paper/prior_factorial/` | `metrics.csv`, `manifest.json` |
| Forgiveness / trust repair | `configs/paper/forgiveness.toml` | `results/paper/forgiveness/` | `metrics.csv`, `manifest.json` |
| Mixed volatility | `configs/paper/mixed_volatility.toml` | `results/paper/mixed_volatility/` | `metrics.csv`, `manifest.json` |

The exact manuscript source tables and final paper figures live under
`docs/manuscript/source_tables/` and `docs/manuscript/figures/`.

## Analysis Route

For H1 and H5, the config `[analysis]` block names the primary analysis
contract used by `run.py`. For Exp A-D, raw trajectories are converted into
compact profile metrics and manuscript figures with:

```bash
python scripts/analysis/phenotype_artifacts.py --help
python scripts/analysis/make_paper_figures.py --help
```

Use `docs/results/paper.md` for the result-card interpretation boundary: these
folders contain compact tracked summaries; full `raw/results.csv` files are
ignored by git and retained locally/server-side.
