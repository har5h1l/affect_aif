# AGENTS.md - analysis/

This subtree owns post-hoc analysis over existing result tables.

- Read `docs/results/README.md` and the relevant experiment docs before
  changing metrics, summaries, figures, source-table builders, or report
  rendering.
- Analysis modules should operate on data frames and artifact paths, not run
  experiments.
- If a metric definition changes, update the matching result/manuscript notes
  and source-table documentation in the same change.
- Do not reinterpret new outputs in `docs/results/` without user approval.
- Keep future-extension analysis separate from paper evidence paths.

