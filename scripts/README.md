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
  source tables; use `--refresh-source-tables` to refresh figure-specific
  compact tables from `results/paper` raw CSVs before plotting.

Use `python <script> --help` for script-specific arguments.

`experiment/run.py` honors each config's `[runtime].profile`. Use
`data_collection` for paper/demo/diagnostic trajectory collection: it writes
the manuscript-facing row contract and keeps diagnostic tensors out of raw
CSVs. Use `debug` only for narrow local inspection when full policy traces,
belief matrices, and posterior tensors are needed. The runner records resolved
absolute config paths in result provenance and supports
`--verbose --verbosity-mode stage_stream` for serial and single-worker inline
inspection.
