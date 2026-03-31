# Package Overview

The supported Python package lives under `affect_aif/`.

## Public Import Surface

- `affect_aif.ExperimentConfig`
- `affect_aif.ExperimentRunner`

Those names are re-exported from `affect_aif.experiment` for the supported top-level import path.

## Package Layout

- `core/`: generic active-inference math, control, and learning helpers
- `generative_model/`: trust-game model structure, payoffs, and partner types
- `agent/`: supported agent variants and affect-state helpers
- `environment/`: trust-game environments and scripted partners
- `experiment/`: config loading, condition metadata, orchestration, and batching
- `analysis/`: metrics, plotting, visualization, and model comparison
- `benchmark/`: backend-aware benchmark runners and comparison helpers
- `cli/`: shared helpers used by the supported scripts
- `configs/`: bundled JSON configs for supported workflows

See the README in each subdirectory for local responsibilities and compatibility notes.
