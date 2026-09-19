# Analysis Code

This layer reads existing trajectories and produces summaries and plots.
It does not launch experiments. Use [scripts/analysis/](../scripts/README.md)
for supported command-line entry points.

| Area | What to read here |
|---|---|
| [metrics.py](metrics.py) | Paper readouts, paired contrasts, and bootstrap summaries. |
| [core/](core/) | Loading, parsing, windows, summaries, and statistical helpers. |
| [phenotypes/](phenotypes/) | Alpha-sweep, prior-factorial, forgiveness, and future mixed-volatility metrics. |
| [configured.py](configured.py) and [hypotheses/](hypotheses/) | Config-driven analysis dispatch and hypothesis-specific reports. |
| [plots.py](plots.py), [visualization.py](visualization.py), [figure_style.py](figure_style.py) | Plot construction and styling. |
| [reports/](reports/) | Report rendering. |

The paper-specific source-table and figure builders live in
[make_paper_figures.py](../scripts/analysis/make_paper_figures.py);
profile artifact export lives in
[phenotype_artifacts.py](../scripts/analysis/phenotype_artifacts.py).
Use [result provenance](../docs/results/provenance.md) to find the exact builder
and input for a figure. [Findings](../docs/results/findings.md) owns the
interpretation; analysis output alone does not update those claims.

`analysis.auto = false` disables configured dispatch. For an explicit generic
post-hoc run, use `scripts/analysis/analyze.py` without `--config`; the paper
notebook instead calls the paper analysis functions for each completed core run.
