# IWAI Manuscript Packet

This folder contains the LNCS manuscript and the supporting evidence packet for
the IWAI 2026 submission. It keeps manuscript source, figure assets, source
tables, provenance, and claim boundaries together without migrating this repo
into a new project scaffold.

## Files

- `main.tex`: anonymized LNCS manuscript source using the approved title.
- `sections/`: manuscript section files included by `main.tex`.
- `manuscript.pdf`: rendered PDF produced from `main.tex`.
- `references.bib`: verified bibliography entries used by the manuscript.
- `results_digest.md`: audited seed counts, promoted result roots, key numbers,
  and include/exclude decisions.
- `figures.md`: figure plan, copied figure assets, captions, and source paths.
- `future_work.md`: two-week follow-up menu and longer-term work.
- `followup_experiment_plan.md`: evidence-gated phenotype extension plan and
  A-D experiment commands.
- `figures/`: copied PNGs from current analysis outputs.
- `source_tables/`: compact CSVs copied from analysis outputs for the writing
  model and later manual checking.
- `scripts/analysis/make_paper_figures.py`: regenerates larger manuscript
  composite figures from `source_tables/`.

## Evidence Contract

Use `docs/results/current.md`, `docs/paper/manuscript/results_digest.md`, and
this packet as the current diagnostic evidence surface. The completed post-fix
log-surprisal smoke is current smoke evidence, but not publication-grade
confirmation. Do not promote old bounded-error numbers or pre-fix smoke numbers
as current manuscript evidence.
Do not write a broad "affect improves reward" claim. The supported thesis is:

> Partner-specific affective precision changes social policy deployment when
> the policy space is open, and under the corrected selector it can improve
> abrupt-betrayal behavior at smoke scale. The model-fitness interpretation
> remains a target claim that requires post-fix confirmation.

Current manuscript evidence should be written as diagnostic/provisional until
confirmation-scale post-fix reruns exist:

- Three-seed H1 smoke: the corrected active-encounter and
  partial-correlation readouts restore the surprise-over-reward diagnostic at
  smoke scale, but H1 is not yet a publication-grade model-fitness claim.
- Three-seed H0/H2 smoke: beta-to-gamma coupling changes deployment, but local
  affect does not yet have a payoff advantage.
- Three-seed H3 smoke: locality improves signal quality, not demonstrated
  aggregate behavior.
- Three-seed H5 smoke: abrupt betrayal is repaired under the centered selector
  and is now the strongest candidate positive behavioral anchor.
- Three-seed H4/H6 smoke: supplemental only.

Publication-ready evidence requires confirmation-scale reruns of the post-fix
claim spine.

The Exp A-D phenotype scripts are not current evidence until their server-side
20-seed outputs have completed and been analyzed. Their compact outputs should
enter this folder as `source_tables/exp_*` and `figures/fig_alpha_sweep.pdf`,
`figures/fig_phenotype_quadrants.pdf`, `figures/fig_forgiveness.pdf`, and
`figures/fig_mixed_volatility.pdf`.

## Writing Guardrails

- Every paragraph should have one claim tied to a result, method detail, source,
  or explicit assumption.
- Report seed counts with every headline result.
- State that H6 variants are clinical-like perturbations, not clinical models.
- State that beta is an external HESP-style precision tracker, not a POMDP
  hidden state.
- Do not add unverified citations, DOIs, venues, quotes, or BibTeX entries.
