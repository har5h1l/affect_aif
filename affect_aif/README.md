# Package Overview

The supported Python package lives under `affect_aif/`.

Key layers:

- `core/`: generic active-inference math, policies, and rollout helpers
- `generative_model/`: trust-game model structure, payoffs, and partner types
- `agent/`: supported agent variants used by current conditions
- `environment/`: trust-game environments and scripted partners
- `experiment/`: config loading, condition metadata, orchestration, and batching
- `analysis/`: metrics, plotting, visualization, and model comparison
- `configs/`: supported configs for the documented workflows

See the README in each subdirectory for the local entry points and responsibilities.
