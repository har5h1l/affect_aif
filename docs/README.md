# Documentation

The public documentation has two routes:

- [Guide](guide/README.md): install, configure, run notebooks or scripts,
  reproduce experiments, and build the manuscript.
- [Results](results/README.md): findings, uncertainty, evidence boundaries,
  source tables, and provenance.

`manuscript/` contains the paper source, PDF, bibliography, figures, and compact
source tables. Its Methods and appendices provide the formal model description.

## Maintenance

Keep instructions in `guide/` and interpreted evidence in `results/`.
`results/findings.md` owns current claims; `results/provenance.md` maps them to
artifacts. Check those sources before changing paper numbers or interpretation.
Update affected guide docs when config or script behavior changes. Avoid
parallel summaries of the same findings.

Agent context lives in local `active/`; historical material lives in local
`archive/`. These are excluded from Git and are not the public documentation.
Raw result CSVs are also ignored at their working paths; the tracked
`paper_results.zip` provides the frozen paper data. See the root README.
