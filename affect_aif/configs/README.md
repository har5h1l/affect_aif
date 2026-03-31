# Configs

## Responsibility

This directory stores the bundled JSON configurations used by the supported experiment and benchmark workflows.

## Public Surface

The files here are loaded through `ExperimentConfig.from_json(...)` and the benchmark config loaders used by `scripts/run_experiment.py` and `scripts/run_benchmark.py`.

## Key Groups

- `default.json`, `betrayal_stress.json`: primary experiment configs
- `graded_trust.json`, `graded_betrayal_*.json`: graded-task variants
- `benchmark_*.json`: benchmark runner configs
- `figure_*.json`, `variant_*.json`, `horizon_sweep.json`, `cautious_prior.json`, `deep_affect_test.json`: documented workflow variants

## Internal / Compatibility Notes

- These files are the supported on-disk config surface; ad hoc config edits should stay in user-owned copies unless a workflow explicitly requires a new bundled preset.
