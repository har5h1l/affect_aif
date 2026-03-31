# Script Inventory

## Responsibility

This directory contains the supported CLI wrappers around the package code.

## Core Supported Workflow

These wrappers define the stable end-user workflow documented in `docs/cli.md`:

- `run_experiment.py`
- `run_preliminary.py`
- `run_analysis.py`
- `run_visualization.py`
- `run_model_comparison.py`

## Additional Utilities

These scripts remain in the active tree because they support benchmark, paper, clinical, or CvC-specific workflows, but they are not part of the small core CLI contract above:

- `run_benchmark.py`
- `analyze_benchmark.py`
- `analyze_benchmark_paper.py`
- `analyze_clinical_results.py`
- `run_clinical_sensitivity.py`
- `generate_paper_figures.py`
- `cvc_list_missions.py`
- `cvc_obs_diagnostic.py`

## Internal / Compatibility Notes

- These wrappers are intentionally thin and defer real work to the package modules.
- Historical one-off scripts were moved to `archive/scripts/`.
