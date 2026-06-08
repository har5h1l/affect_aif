# Paper Packet

This directory collects the paper-facing narrative for `affect_aif`. It is the
best entry point when deciding what the manuscript can claim.

## Directory Layout

```text
docs/paper/
├── README.md                 # this index
├── prompts/
│   └── writing_model_prompt.md   # agent/human guardrails for .tex revision
├── notes/                    # narrative, claims, and supporting supplements
│   ├── manuscript_outline.md
│   ├── claims_and_evidence.md
│   ├── literature_positioning.md
│   ├── figures_tables.md
│   ├── limitations_and_followups.md
│   ├── model_spec.md
│   ├── experiment_manifest.md
│   ├── reproducibility.md
│   └── result_provenance.md
└── manuscript/               # LNCS source, PDF, digest, figures, source CSVs
    ├── README.md
    ├── main.tex, sections/, appendix/
    ├── results_digest.md
    ├── source_tables/
    └── figures/
```

## Where To Start

| Task | Read first |
|---|---|
| Revise manuscript prose | `prompts/writing_model_prompt.md`, then `manuscript/sections/*.tex` |
| Check what we can claim | `notes/claims_and_evidence.md`, `manuscript/results_digest.md` |
| Section structure / spine | `notes/manuscript_outline.md` |
| Figure or table plan | `notes/figures_tables.md` |
| Limitations and reviewer follow-ups | `notes/limitations_and_followups.md` |
| Model / runtime boundary | `notes/model_spec.md` |
| Config paths for cited experiments | `notes/experiment_manifest.md` |
| Run commands and provenance | `notes/reproducibility.md`, `notes/result_provenance.md` |
| Build PDF | `manuscript/README.md` |

Interpreted hypothesis status outside the paper packet remains in
`docs/results/current.md`. Do not treat paper notes as a substitute for that
scorecard.

## One-Sentence Thesis

Partner-local affective precision is a metacognitive model-fitness signal: it
tracks predictability rather than partner value and gates how decisively the
focal agent deploys existing social beliefs into action when the policy space is
open.

## Current Read

The manuscript draft has a coherent mechanism-and-boundary story aligned with
the five linked results claims in `manuscript/sections/03_results.tex`.

- **Core mechanism:** predictability tracking, metacognitive (not epistemic)
  deployment via tracked-only dissociation, partner-choice reorganisation.
- **Boundary / stress:** abrupt betrayal lowers policy entropy and raises joint
  accuracy at confirmation scale, with only a small/uncertain payoff advantage.
  Treat it as temporal dependency in action-confidence deployment, not a broad
  reward-improvement claim.
- **Individual differences:** phenotype programme ($\alpha$, prior) is in the
  manuscript at 20-seed descriptive scale; not clinical validation.
- **Limitations already in Discussion:** external $\beta_k$, scripted partners,
  predictive phenotypes.
- **Still incoming in `.tex`:** explicit partner-implementation paragraph and
  fuller POMDP subsection in Methods.
- **Final result gate:** H1 reached structural finality on June 6 and is now
  interpreted as model-fitness tracking rather than reward gain.

Do not overclaim: human data, reciprocal AIF partners, or clinical diagnosis.
