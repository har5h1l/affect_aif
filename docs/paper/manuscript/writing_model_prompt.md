# Prompt For Manuscript Writing And Revision

Use when revising the LNCS draft or extending section files. The first full draft
already exists in `docs/paper/manuscript/sections/`; treat this prompt as a
framing guardrail, not a greenfield drafting brief.

Read these files first:

1. `docs/paper/manuscript/README.md`
2. `docs/paper/manuscript/sections/*.tex` (current source of truth for framing)
3. `docs/paper/notes/manuscript_outline.md`
4. `docs/paper/notes/claims_and_evidence.md`
5. `docs/paper/manuscript/results_digest.md`
6. `docs/paper/manuscript/references.bib`

Use these project docs for implementation detail if needed:

- `docs/paper/notes/model_spec.md`
- `docs/theory/pomdp_spec.md` (§12 scripted partners; §13 planned reciprocal AIF)
- `docs/design/implementation.md`

## Central Framing (already in manuscript)

- **Prediction vs commitment:** social cognition requires both inferring partners
  and deciding how decisively to act.
- **Metacognitive affect:** partner-local precision tracks model fitness for
  **behavioural** prediction, not partner mental states (contrast ToM).
- **Focal agent only** runs full active inference; partners are scripted
  parameterized policies (Discussion limitation; Methods paragraph still to add).
- **Five results claims:** predictability not value; action sharpening;
  engagement reorganisation; betrayal temporal dependency; phenotype programme.

## Drafting Rules

- Preserve the deployment claim: tracked-only dissociation is the lesion
  evidence; do not collapse affect into belief improvement.
- **Betrayal:** write payoff gain **with** lower joint accuracy as portfolio
  reallocation and temporal dependency—not "affect recovers after betrayal" and
  not "affect always misdeploys."
- Phenotypes: computational profiles from $\alpha$ and prior; not clinical
  diagnoses. Exp C forgiveness is still TODO in source.
- $\beta_k$ is an external HESP-style tracker, not a POMDP hidden state.
- Report seed counts with headline numbers (20 phenotype, 30 confirmation where
  stated; TODOs in `.tex` for final 30-seed betrayal/locality values).
- Do not invent citations, results, or reciprocal multi-AIF experiments.
- Incoming Methods edits: add explicit POMDP subsection and partner-implementation
  paragraph without contradicting Discussion limitations.

## Manuscript Spine (matches current `.tex`)

1. Intro: prediction/commitment → affect → AIF/Hesp → relational extension →
   three questions.
2. Methods: trust game → per-partner POMDP → partner-local precision → lesions
   → centred logits → simulation scale.
3. Results: five subsections aligned to claims (not H-card numbering in prose).
4. Discussion: social metacognition; phenotypes; deployment lesion; betrayal
   temporal dependency; limitations (external beta, scripted partners,
   predictive phenotypes); future work (human data, global beta, ToM).
5. Conclusion: separate prediction from confident action.

## Do Not Write

- "Affect improves payoff" without regime and boundary conditions.
- "Better partner inference after betrayal" (accuracy goes down in §3.4).
- Clinical validation or named psychiatric phenotypes as established mappings.
- All agents run active inference (partners are scripted in reported experiments).
