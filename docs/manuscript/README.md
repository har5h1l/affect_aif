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
- `macros.tex`: shared LaTeX macros.
- `results_digest.md`: audited seed counts, promoted result roots, key numbers,
  and include/exclude decisions.
- `figures/`: copied PNG/PDF panels from analysis outputs.
- `source_tables/`: compact CSVs copied from analysis outputs for checking and
  figure regeneration.
- `scripts/analysis/make_paper_figures.py`: regenerates composite figures from
  `source_tables/` (see `docs/manuscript/notes/figures_tables.md`).

## Evidence Contract

Use `docs/results/current.md`, `results_digest.md`, and the manuscript notes in
`docs/manuscript/notes/` as the diagnostic evidence surface. H5 and Exp A–D use the
reviewed source tables in this folder; the post-fix three-seed smoke remains
diagnostic provenance only. Do not promote old bounded-error numbers or pre-fix
smoke numbers as current manuscript evidence.

Do not write a broad "affect improves reward" claim. The supported thesis matches
the current manuscript abstract and Discussion:

> Partner-local affective precision tracks predictability rather than partner
> value, modulates action confidence (metacognitive deployment), reorganises
> engagement under choice, and under abrupt change sharpens policy commitment
> with modest behavioral benefit. The mechanism is a temporal dependency, not a
> generic reward boost or inference gain.

Seed scales as stated in Methods:

- **20 seeds:** phenotype / Exp A–D descriptive figures (§3.6).
- **30 seeds:** central behavioural confirmations, including H1 model fitness
  and H5 abrupt betrayal.
- **3-seed smoke:** `results/diagnostics/spine_smoke/raw/`
  remains diagnostic provenance for early H-card readouts; prefer
  manuscript-embedded numbers where they supersede smoke at higher seed count.

For model and experiment background, use `docs/model/` and `docs/experiments/`.
