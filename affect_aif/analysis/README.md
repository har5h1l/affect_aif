# Analysis Layer

## Responsibility

This layer operates on saved experiment outputs and produces summary tables, figures, and comparison artifacts.

## Public Surface

The package-level import surface is `affect_aif.analysis`. It re-exports:

- `build_run_gifs`
- `load_results`

## Key Modules

- `metrics.py`: summary metrics and switch-aware analysis helpers
- `statistics.py`: ANOVA and pairwise tests
- `hypotheses.py`: H1-H5 battery
- `plots.py`: figure generation
- `visualization.py`: GIF generation and result loading
- `model_comparison.py`: Bayesian model comparison

## Internal / Compatibility Notes

- This package is intentionally post-processing only; it does not own experiment execution.
- The supported scripts consume these helpers directly rather than through a larger analysis framework.
