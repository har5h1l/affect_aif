# IWAI Manuscript Source

LNCS manuscript source, rendered PDF, promoted source tables, and figure assets
for the IWAI 2026 submission.

## Build

From this directory:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Output: `main.pdf`.

## Files

- `main.tex`: anonymized LNCS manuscript source using the approved title.
- `sections/`: manuscript section files included by `main.tex`.
- `appendix/`: appendix section files.
- `main.pdf`: rendered PDF produced from `main.tex`.
- `references.bib`: verified bibliography entries used by the manuscript.
- `macros.tex`: shared LaTeX macros. The default build uses the anonymous
  supplementary Drive packet for review. After de-anonymization, set
  `\anonsupprepofalse` to print the public GitHub repository URL instead. The
  supplementary statement appears once at the start of the appendix
  (`appendix/appendix_00_supplementary.tex`).
- `figures/`: copied PNG/PDF panels from analysis outputs.
- `source_tables/`: compact CSVs copied from paper analysis outputs for
  checking and figure regeneration.
- `scripts/analysis/make_paper_figures.py`: refreshes figure-specific compact
  tables from `results/paper` when requested and regenerates composite figures
  from `source_tables/`.

## Evidence Contract

Use `docs/results/current.md` as the paper evidence surface. Abrupt-betrayal and
profile results use the reviewed source tables in this folder. Do not promote
old bounded-error numbers or pre-fix smoke numbers as current main-text
evidence.

Do not write a broad "affect improves reward" claim. The supported thesis matches
the current manuscript abstract and Discussion:

> Partner-local affective precision modulates policy confidence
> (metacognitive deployment), reorganises engagement under choice, and under
> abrupt change sharpens policy commitment with uncertain payoff consequences.
> The mechanism is a temporal calibration process, not a generic reward boost
> or inference gain.

Seed scales as stated in Methods:

- **20 seeds:** profile descriptive figures (§3.6).
- **30 seeds:** central behavioural confirmations: deployment ablation, graded
  partner selection, and abrupt betrayal.

For model and experiment background, use `docs/overview/` and
`docs/experiments/`.
