# affect_aif

Active-inference trust-game simulations for studying partner-local affective
precision as a relationship-specific confidence signal.

## What This Is

`affect_aif` contains a pymdp-backed trust-game model, paper reproduction
configs, compact result summaries, and the manuscript source. The central
mechanism tracks partner-local prediction error in an external beta state and
maps that state into policy precision during action selection.

## How The Repo Works

- `tasks/trust/`: trust-game environments, POMDP construction, affect update,
  partner-local runtime state, and payoff helpers.
- `experiments/trust/`: TOML spec loading, variant expansion, batch execution,
  logging, and configured analysis hooks.
- `configs/`: public runnable TOML specs grouped by intent.
- `scripts/`: supported command-line entry points for running experiments and
  analyzing existing results.
- `analysis/`: post-hoc metrics, figures, and compact artifact builders.
- `docs/`: model, experiment, result, and manuscript documentation.
- `results/`: tracked compact summaries and manifests; raw CSVs are retained
  locally/server-side and gitignored.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Demo

```bash
python scripts/experiment/run.py \
  --config configs/demo/model_fitness.toml \
  --batch-name demo \
  --workers 1
```

Inspect a config without running it:

```bash
python scripts/experiment/inspect.py --config configs/demo/model_fitness.toml
```

## Reproduce The Paper

Dry-run the paper suite first:

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

Remove `--dry-run` to launch the full reproduction. Use `--workers 1` unless
you intentionally want parallel local execution.

## Analyze Results

```bash
python scripts/analysis/analyze.py \
  --results results/paper/model_fitness/raw/h1/reliability_vs_reward_confirm/results.csv \
  --output-dir /tmp/affect_aif_analysis
```

Phenotype compact tables and manuscript figures are regenerated from existing
raw trajectories with:

```bash
python scripts/analysis/phenotype_artifacts.py --help
python scripts/analysis/make_paper_figures.py --help
```

## Where To Go Next

- `configs/README.md`: choose a config.
- `docs/model/`: understand the model and hypotheses.
- `docs/experiments/`: run demos, paper configs, and diagnostics.
- `docs/results/`: inspect compact result summaries and provenance.
- `docs/manuscript/`: build and inspect the manuscript.
- `notebooks/`: demo and reproduction notebooks.

## Maintainer State

`docs/active/` and `docs/handoffs/` are maintainer/agent state surfaces. They
are useful for ongoing work, but public readers should start with the routes
above.
