# AGENTS.md - docs/manuscript/

This subtree owns the LaTeX manuscript, rendered PDF, source tables, and paper
figures.

- Read `docs/manuscript/README.md`, `docs/results/current.md`, and
  `docs/manuscript/notes/claims_and_evidence.md` before changing manuscript
  claims or statistics.
- Verify numbers against `docs/manuscript/source_tables/` and compact result
  summaries before changing prose, captions, or tables.
- Keep internal process language out of reader-facing manuscript text.
- Figure captions should describe plotted panels only; do not add unshown
  behavioral claims.
- After manuscript source changes, rebuild the PDF with the documented
  `pdflatex -> bibtex -> pdflatex -> pdflatex` sequence when feasible.

