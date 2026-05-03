# Script Inventory

## Responsibility

This directory contains the supported CLI wrappers around the package code.

## Core Supported Workflow

These wrappers define the stable end-user workflow documented in `docs/operations/cli.md`:

- `experiment/run.py`
- `experiment/smoke.py`
- `experiment/inspect.py`
- `run_preliminary.py`
- `analysis/analyze.py`
- `analysis/summarize.py`
- `analysis/visualize.py`
- `run_model_comparison.py`
- `benchmark/run_cvc.py`
- `benchmark/package_cvc.py`

Top-level `run_experiment.py`, `run_analysis.py`, `run_visualization.py`, and
`run_benchmark.py` remain as thin compatibility wrappers.

## Additional Utilities

These scripts remain in the active tree because they support benchmark, paper, clinical, or CvC-specific workflows, but they are not part of the small core CLI contract above:

- `analyze_benchmark.py`
- `analyze_benchmark_paper.py`
- `analyze_clinical_results.py`
- `run_clinical_sensitivity.py`
- `run_targeted_reanalysis.py` — can auto-fall back to the best available checkpoint CSVs when final `results.csv` files are not present yet
- `generate_paper_figures.py`
- `cvc_list_missions.py`
- `cvc_obs_diagnostic.py`

## Internal / Compatibility Notes

- These wrappers are intentionally thin and defer real work to the package modules.
- Historical one-off scripts were removed after salvage into `docs/results/historical_findings.md`.
