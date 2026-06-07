# IWAI Manuscript Packet

This folder contains the LNCS manuscript and the supporting evidence packet for
the IWAI 2026 submission. It keeps manuscript source, figure assets, source
tables, provenance, and claim boundaries together without migrating this repo
into a new project scaffold.

## Files

- `main.tex`: anonymized LNCS manuscript source using the approved title.
- `sections/`: manuscript section files included by `main.tex`.
- `main.pdf`: rendered PDF produced from `main.tex`.
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
this packet as the current diagnostic evidence surface. H5 and Exp A--D now use
the reviewed source tables in this packet; the post-fix three-seed smoke remains
diagnostic provenance only. Do not promote old bounded-error numbers or pre-fix
smoke numbers as current manuscript evidence.
Do not write a broad "affect improves reward" claim. The supported thesis matches
the current manuscript abstract and Discussion:

> Partner-local affective precision tracks predictability rather than partner
> value, modulates action confidence (metacognitive deployment), reorganises
> engagement under choice, and under abrupt change sharpens policy commitment
> with modest behavioral benefit. The mechanism is a temporal dependency, not a
> generic reward boost or inference gain.

Current manuscript evidence uses mixed seed scales as stated in Methods:

- **20 seeds:** phenotype / Exp A–D descriptive figures (§3.5–3.6).
- **30 seeds:** central behavioural confirmations, including H1 model fitness
  and H5 abrupt betrayal.
- **3-seed smoke:** `results/log_surprisal_spine_smoke_postfix_20260528/`
  remains diagnostic provenance for early H-card readouts; prefer
  manuscript-embedded numbers where they supersede smoke at higher seed count.

Incoming `.tex` edits (not yet required in this packet): explicit partner-
implementation paragraph and fuller POMDP Methods subsection.

Publication-ready tightening no longer has a numeric experiment placeholder;
remaining work is manuscript polish and any reviewer-driven follow-up decision.

## Writing Guardrails

- Every paragraph should have one claim tied to a result, method detail, source,
  or explicit assumption.
- Report seed counts with every headline result.
- State that H6 variants are phenotype-inspired computational perturbations,
  not clinical models.
- State that beta is an external HESP-style precision tracker, not a POMDP
  hidden state.
- State that reported experiments use a focal active-inference agent against
  scripted parameterized partner policies (Discussion limitation).
- Frame betrayal as temporal dependency in deployment: lower entropy and higher
  joint accuracy at confirmation scale, with uncertain payoff size.
- Do not add unverified citations, DOIs, venues, quotes, or BibTeX entries.
