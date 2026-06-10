# Scripts

Supported command-line entry points:

- `experiment/run.py`: run one or more trust experiment TOML configs.
- `experiment/inspect.py`: inspect config expansion without running.
- `analysis/analyze.py`: compute generic post-hoc summaries and figures from
  an existing `results.csv`.
- `analysis/phenotype_artifacts.py`: regenerate compact profile metrics,
  source tables, and figures from existing paper or future-extension raw
  trajectories.
- `analysis/make_paper_figures.py`: rebuild manuscript composite figures from
  source tables.

Use `python <script> --help` for script-specific arguments.
