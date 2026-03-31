# Experiment Layer

## Responsibility

This layer is the supported orchestration surface for experiment configuration, condition lookup, and batch execution.

## Public Surface

The package-level import surface is `affect_aif.experiment`. It re-exports:

- `ExperimentConfig`
- `ExperimentRunner`
- `BatchExperimentRunner`

## Key Modules

- `config.py`: canonical experiment config schema and compatibility loading
- `conditions.py`: condition metadata and stable names
- `constants.py`: stable condition sets used by calibration and sensitivity
- `factory.py`: model, environment, and agent factories
- `runner.py`: public `ExperimentRunner` facade
- `batch.py`: multi-config batch execution
- `tasks.py`: process-safe worker tasks
- `persistence.py`: result annotation and persistence helpers
- `progress.py`: structured progress reporting
- `logger.py`: per-round metric logging
- `calibration.py`: `mu` calibration helpers

## Internal / Compatibility Notes

- `config.py` is the canonical schema source; compatibility aliases are handled there rather than in callers.
- Batch and runner code share the same config model so the supported scripts can stay thin.
