# IWAI Manuscript Packet

This folder contains the LNCS manuscript and the supporting evidence packet for
the IWAI 2026 submission. It keeps manuscript source, figure assets, source
tables, provenance, and claim boundaries together without migrating this repo
into a new project scaffold.

## Files

- `main.tex`: anonymized LNCS manuscript source using the approved title.
- `sections/`: manuscript section files included by `main.tex`.
- `manuscript_draft.pdf`: rendered PDF produced from `main.tex`.
- `references.bib`: verified bibliography entries used by the manuscript.
- `results_digest.md`: audited seed counts, promoted result roots, key numbers,
  and include/exclude decisions.
- `figures.md`: figure plan, copied figure assets, captions, and source paths.
- `future_work.md`: two-week follow-up menu and longer-term work.
- `figures/`: copied PNGs from current analysis outputs.
- `source_tables/`: compact CSVs copied from analysis outputs for the writing
  model and later manual checking.

## Evidence Contract

Use `docs/results/current.md` and this packet as the current evidence hierarchy.
Do not write a broad "affect improves reward" claim. The supported thesis is:

> Partner-specific affective precision tracks social model fitness and changes
> policy deployment when the policy space is open, but abrupt social shocks can
> turn the same precision channel into misdeployment.

Primary manuscript evidence should come from:

- 30-seed H1 confirmation: model fitness rather than reward.
- 30-seed H3 confirmation: stress boundary condition.
- 30-seed H3 precision-sensitivity follow-up: abrupt versus gradual shock shape.
- Five-seed H0/H2/H4 current-architecture queue: open-regime deployment and
  social-choice readouts.
- Five-seed H5 runs: supplemental precision-dynamics phenotypes only.
- H6 global-beta/locality smoke runs: follow-up discovery only unless promoted
  after user review.

## Writing Guardrails

- Every paragraph should have one claim tied to a result, method detail, source,
  or explicit assumption.
- Report seed counts with every headline result.
- State that H5 variants are clinical-like perturbations, not clinical models.
- State that beta is an external HESP-style precision tracker, not a POMDP
  hidden state.
- Do not add unverified citations, DOIs, venues, quotes, or BibTeX entries.
