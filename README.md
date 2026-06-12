# Partner-Specific Affective Precision in Social Active Inference

Active-inference trust-game simulations for studying partner-local affective
precision as a relationship-specific confidence signal.

**Anonymous review:** the public code mirror for double-blind review is
<https://anonymous.4open.science/r/affect_aif>.

## What This Is

`affect_aif` contains a pymdp-backed trust-game model, paper reproduction
configs, compact result summaries, and the manuscript source. The central
mechanism tracks partner-local prediction error in an external beta state and
maps that state into policy precision during action selection.

## How The Repo Works

- `tasks/trust/`: trust-game environments, POMDP construction, affect update,
  partner-local agent/runtime state, and payoff helpers. This is the core
  trust model package, even though it contains the agent machinery.
- `experiments/trust/`: TOML spec loading, variant expansion, batch execution,
  logging, and configured analysis hooks for the focal-agent paper experiments.
- `experiments/multifocal/`: tested reciprocal AIF-vs-AIF extension code. This
  is future work and is not used by the paper reproduction configs.
- `configs/`: public runnable TOML specs grouped by intent.
- `scripts/`: supported command-line entry points for running experiments and
  analyzing existing results.
- `analysis/`: post-hoc metrics, figures, and compact artifact builders.
- `docs/`: model, experiment, result, and manuscript documentation.
- `results/`: tracked compact summaries and manifests; raw CSVs are retained
  outside git and in the Drive packet.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Demo

```bash
python scripts/experiment/run.py \
  --config configs/demo/01_predictability_value.toml \
  --batch-name demo \
  --workers 1
```

Inspect a config without running it:

```bash
python scripts/experiment/inspect.py --config configs/demo/01_predictability_value.toml
```

## Reproduce The Paper

Dry-run the paper suite first:

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

Remove `--dry-run` to launch the full reproduction. Use `--workers 1` unless
you intentionally want parallel local execution.

## Analyze Results

```bash
python scripts/analysis/analyze.py \
  --results results/paper/04_betrayal_adaptation/raw/betrayal_adaptation/betrayal_adaptation/results.csv \
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
- `docs/overview/`: understand the model and hypotheses.
- `docs/experiments/`: run demos, paper configs, and diagnostics.
- `docs/results/`: inspect compact result summaries and provenance.
- `docs/manuscript/`: build and inspect the manuscript.
- `notebooks/`: demo and reproduction notebooks.
