# Commands

| Script | Purpose |
|---|---|
| `experiment/run.py` | Run one or more experiment configs. |
| `experiment/inspect.py` | Show a config's expanded runs without executing them. |
| `analysis/analyze.py` | Generate summaries and plots from an existing result CSV. |
| `analysis/phenotype_artifacts.py` | Build profile metrics and figures from existing trajectories. |
| `analysis/make_paper_figures.py` | Build paper figures; add `--refresh-source-tables` to regenerate their input tables from the paper results. |

Use `python <script> --help` for available arguments.

See [Running experiments](../docs/guide/running.md) for examples,
[Configs](../docs/guide/configs.md) for settings, and
[Result provenance](../docs/results/provenance.md) for figure inputs and checks.
