# Current Mission

Advance the manuscript from a diagnostic smoke-evidence draft to a
publication-quality paper grounded in confirmation-scale runs and the new
individual-differences / phenotype framing. The active evidence surface
combines core mechanism tests (H0-H6) with phenotype experiments (Exp A-D)
that fill the Section 3.6 placeholders on affective precision dynamics as
individual differences in social trust calibration.

## Scope

- Use official `inferactively-pymdp==1.0.0` as the supported active-inference
  runtime. Do not reintroduce a custom AIF engine.
- Keep trust-game model construction, affective precision tracking, experiment
  runners, logging, and analysis in project-owned task and experiment modules.
- Scripts are the canonical experiment and analysis entry points.
- Preserve the Hesp-extension behavior-card spine in
  `docs/theory/hypotheses.md`.
- Treat pre-May-27 bounded-error results as historical/provisional.
- The post-fix three-seed smoke (`results/log_surprisal_spine_smoke_postfix_20260528/`)
  is the current diagnostic baseline. Do not promote smoke numbers to
  publication claims without confirmation-scale reruns.

## Constraints

- Do not update result interpretation from new experiment outputs without user
  approval (except filling `\resultp{}` placeholders in the manuscript after
  inspecting outputs).
- Do not add orchestration or deployment scripts to this repo; use Mango for
  remote VM, sync, and merge flows.
- Do not reintroduce the removed external benchmark integration.
- Re-run the verification gate in `docs/active/progress.md` immediately before
  scheduling any further full experiment reruns.

## Current Phase: Manuscript Revision + Phenotype Experiments

The manuscript has been substantially revised (May 31, 2026):

- Abstract: replaced with new 3-paragraph version foregrounding affect as
  social metacognition, the action-sharpening dissociation, and the
  individual-differences phenotype contribution.
- Introduction: replaced with new layered framing distinguishing the
  psychological, formalisation, and emergent-dynamics levels of the claim.
- Results: rewritten as a clean publication-quality narrative. Smoke numbers
  used directly where strong (H2 entropy, H3 locality correlations, H5
  betrayal). Section 3.6 (affective precision dynamics as individual
  differences) added with `\resultp{}` placeholders throughout.
- Discussion: individual-differences subsection added; 4th limitation added;
  future directions replaced with a more focused and ambitious version.
- `\resultp{}` LaTeX command added to macros.tex for visible blue placeholders.

The four phenotype experiment scripts (Exp A-D) are running on the server.
See `docs/active/progress.md` for commands and expected outputs.

## Completion State

- Active runtime cutover to official `inferactively-pymdp==1.0.0` is complete.
- Post-fix H0-H6 smoke completed under corrected centered selector.
- Manuscript draft revised toward phenotype/individual-differences framing.
- Exp A-D scripts implemented and running on server. Exp A has written outputs;
  Exp B is still running, so phenotype outputs are not final evidence.
- Confirmation-scale runs for H5 (and H1 corrected-readout confirmation) are the next planned
  experiments after Exp A-D complete.

## Current Evidence State per Hypothesis

| Hypothesis | Smoke read | Manuscript treatment | Next step |
|---|---|---|---|
| H0 Policy Openness | flat payoff, active deployment | deployment channel established | H2 confirm if payoff language stays |
| H1 Model Fitness | corrected active-aligned read supports surprise-over-reward but smoke only | claims framed with `\resultp{}` | confirm; redesign only if confounded |
| H2 Deployment | entropy active, payoff flat | deployment interpretation | confirm if needed |
| H3 Locality | local=cleaner signal, global=higher smoke payoff | decomposition claim, not necessity | Exp D provides partial test |
| H4 Social Allocation | underpowered | allocation reorganisation claim with `\resultp{}` | confirm if language stays |
| H5 Betrayal | repaired; affect beats no-affect | primary positive anchor, full numbers | PRIORITY confirmation |
| H6 Perturbation | phenotype dynamics separate | supplemental perturbation section | Exp A-D supersede this |
| Exp A α Sweep | not yet | Section 3.6.1 all `\resultp{}` | running on server |
| Exp B Prior Factorial | not yet | Section 3.6.2 all `\resultp{}` | running on server |
| Exp C Forgiveness | not yet | Section 3.6.3 all `\resultp{}` | running on server |
| Exp D Mixed Volatility | not yet | Section 3.6.4 all `\resultp{}` | running on server |

## Current Handoff

Read this folder in order: `state.md`, `progress.md`, then `blockers.md`.
Paper-facing evidence in `docs/paper/manuscript/`. Interpreted results in
`docs/results/`.

The next active lane is:
1. Wait for Exp A-D to complete on server (`mango cloud sync fetch affect_aif`).
2. Run `scripts/analysis/analyze.py` on each `results/exp_*/` output.
3. Fill Section 3.6 `\resultp{}` placeholders with actual numbers.
4. Queue H5 confirmation run after verification gate passes.
5. Run H1 confirmation with the corrected active-aligned and partial-correlation
   readouts; if confirmation remains reward/exposure-confounded, use the
   balanced graded reliability spine and then the reward-neutral diagnostic
   before treating the model as failed.

Do not create a separate handoff document; keep the live handoff in this
`docs/active/` state/progress surface.

## Stop Conditions

- A required verification command fails in a way that suggests a design
  problem rather than a local fix.
- Exp A-D produce results qualitatively inconsistent with the phenotype
  predictions in Section 3.6 (flag to user before updating narrative).
- Confirmation-scale H5 runs reverse the betrayal advantage.
- Clinical reruns on the current architecture qualitatively invert the
  expected phenotype ordering.
