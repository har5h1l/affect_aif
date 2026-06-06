# Paper Packet

This directory collects the paper-facing narrative for `affect_aif`. It is the
best entry point when deciding what the manuscript can claim.

## Files

- `notes/manuscript_outline.md`: section-by-section skeleton synced to current
  manuscript `.tex`.
- `notes/claims_and_evidence.md`: what the current results support, fail to
  support, and leave incomplete.
- `notes/literature_positioning.md`: novelty and related-work positioning.
- `notes/figures_tables.md`: recommended figures, tables, and source artifacts.
- `notes/limitations_followups.md`: limitations, reviewer risks, and narrow
  follow-up experiments.
- `notes/model_spec.md`: concise computational model description (focal AIF +
  scripted partners).
- `notes/experiment_manifest.md`: manuscript-facing experiment/config map.
- `notes/reproducibility.md`: commands, environment, and provenance rules.
- `notes/result_provenance.md`: promoted result roots and interpretation notes.
- `manuscript/`: LNCS manuscript source, rendered PDF, result digest, figure
  assets, source CSVs, future-work menu, and writing-model handoff.

## One-Sentence Thesis

Partner-local affective precision is a metacognitive model-fitness signal: it
tracks predictability rather than partner value and gates how decisively the
focal agent deploys existing social beliefs into action when the policy space is
open.

## Current Read

The manuscript draft has a coherent mechanism-and-boundary story aligned with
the five linked results claims in `sections/03_results.tex`.

- **Core mechanism:** predictability tracking, metacognitive (not epistemic)
  deployment via tracked-only dissociation, partner-choice reorganisation.
- **Boundary / stress:** abrupt betrayal can raise payoff while lowering joint
  accuracy—temporal dependency on portfolio structure, not a simple recovery
  or failure story.
- **Individual differences:** phenotype programme ($\alpha$, prior) is in the
  manuscript at 20-seed descriptive scale; not clinical validation.
- **Limitations already in Discussion:** external $\beta_k$, scripted partners,
  predictive phenotypes.
- **Still incoming in `.tex`:** explicit partner-implementation paragraph and
  fuller POMDP subsection in Methods.
- **Still TODO in numbers:** 30-seed confirmation values for betrayal and
  locality probe (marked in source).

Do not overclaim: human data, reciprocal AIF partners, or clinical diagnosis.
