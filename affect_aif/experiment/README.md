# Experiment Layer

This layer is the supported orchestration surface.

- `config.py`: canonical experiment config schema and compatibility loading
- `conditions.py`: condition metadata and stable names
- `constants.py`: stable condition sets used by calibration and sensitivity
- `factory.py`: model/environment/agent factories
- `runner.py`: public `ExperimentRunner` facade
- `batch.py`: multi-config batch execution
- `tasks.py`: process-safe worker tasks
- `persistence.py`: result annotation and persistence helpers
- `progress.py`: structured progress reporting
