# Benchmark Layer

## Responsibility

This package provides benchmark backends, baseline agents, and cross-environment comparison helpers.

## Public Surface

The package-level import surface is `affect_aif.benchmark`. It re-exports:

- backend availability checks: `cogames_available`, `mettagrid_available`
- baseline agents: `RandomAgent`, `TitForTatAgent`, `WinStayLoseShiftAgent`, `PavlovAgent`, `GrimTriggerAgent`, `QLearningAgent`
- common metrics: `cooperation_rate`, `cumulative_payoff`, `type_identification_accuracy`, `adaptation_speed`, `partner_discrimination`

## Key Modules

- `backend.py`: benchmark backend contract and shared context
- `benchmark_config.py`: benchmark configuration schema
- `benchmark_runner.py`: benchmark execution orchestration
- `baselines.py`: supported baseline agents
- `common_metrics.py`: environment-agnostic comparison metrics
- `compat.py`: optional dependency guards
- `comparison.py`: trust-vs-gridworld comparison helpers
- `trust_backend.py`: supported trust benchmark backend
- `cvc_*`: local CvC proof-of-concept and packaging helpers
- `toy_gridworld_backend.py`: legacy scripted gridworld shim

## Internal / Compatibility Notes

- The trust backend is the supported benchmark path.
- The local CvC backend is intentionally isolated so it can mature independently.
- The scripted gridworld adapter remains for backward compatibility only and is not treated as a first-class CoGames integration.
