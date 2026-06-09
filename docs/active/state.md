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
- Preserve the behavior-card spine in `docs/overview/hypotheses.md`.
- Treat pre-May-27 bounded-error results as historical/provisional.
- The post-fix three-seed smoke (`results/diagnostics/spine_smoke/raw/`)
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

The manuscript has been substantially revised (May 31, 2026) and evidence
claims were softened on June 2 so smoke-scale findings are not presented as
publication-grade results:

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
- `07b31d0` aligned the abstract, introduction, results, and discussion with an
  earlier evidence tier where H1/H5 and phenotype profiles were still pending;
  June 6 docs now supersede that state for H5 and Exp A-D.
- `e66fc16` aligns pre-run Exp C/D phenotype metrics with their manuscript
  readouts: Exp C payoff recovery uses the late pre-betrayal baseline, and Exp
  D false positives measure stable-P0 engagement drops rather than generic
  non-P0 allocation.

The original four-script phenotype run stopped before finality and has been
superseded by the recovery tmux/Mango process documented in
`docs/active/progress.md`. Do not interpret phenotype outputs until the
recovery process reaches finality.

## Completion State

- Active runtime cutover to official `inferactively-pymdp==1.0.0` is complete.
- Post-fix H0-H6 smoke completed under corrected centered selector.
- Manuscript draft revised toward phenotype/individual-differences framing and
  current smoke-vs-confirmation evidence boundaries.
- Exp A-D scripts implemented and interpreted for manuscript use after user
  approval on June 6. Exp C forgiveness now has compact source tables and
  `fig_forgiveness.pdf`; the paper readout is a reengagement/confidence
  dissociation, not monotonic affective forgiveness.
- H5 confirmation reached structural finality and has been interpreted for the
  manuscript. The 30-seed read is lower entropy and higher joint accuracy under
  partner-local affect, with a small/uncertain payoff advantage.
- H1 confirmation reached structural finality and has been interpreted for the
  manuscript. The 30-seed read supports model-fitness tracking after
  active-encounter controls, but not reward improvement.

## Current Evidence State per Hypothesis

| Hypothesis | Smoke read | Manuscript treatment | Next step |
|---|---|---|---|
| H0 Policy Openness | flat payoff, active deployment | diagnostic deployment-channel readout | confirm only if stronger payoff/general-performance language returns |
| H1 Model Fitness | 30-seed confirmation supports surprise-over-reward after active-encounter controls; payoff favors no-affect | interpreted as model-fitness tracking, not reward gain | reviewer diagnostics only if requested |
| H2 Deployment | entropy active, payoff flat | deployment interpretation | confirm if needed |
| H3 Locality | local=cleaner signal, global=higher smoke payoff | decomposition claim, not necessity | Exp D provides partial test |
| H4 Social Allocation | underpowered | smoke-scale allocation reorganisation readout | confirm only if this remains a core manuscript claim |
| H5 Betrayal | confirmation complete | primary behavioral confirmation: entropy/accuracy improve; payoff uncertain | interpreted in paper |
| H6 Perturbation | phenotype dynamics separate | supplemental perturbation section | Exp A-D supersede this |
| Exp A α Sweep | complete; compact outputs regenerated | Section 3.6.1 interpreted | no rerun pending |
| Exp B Prior Factorial | complete: 360/360 runs, compact outputs, and generic analysis | Section 3.6.2 interpreted | no rerun pending |
| Exp C Forgiveness | structurally complete: 120/120 groups x 200 rounds; final `results.csv`, compact `metrics.csv`, analysis, source table, and `fig_forgiveness.pdf` exist | Section 3.6.3 interpreted as reengagement/confidence dissociation | no rerun pending |
| Exp D Mixed Volatility | complete: 80/80 runs, compact outputs, and generic analysis | Section 3.6.4 interpreted narrowly | no rerun pending |
| H5 Betrayal Confirmation | structurally complete: 120/120 groups x 120 rounds; final `results.csv`, checkpoint, and configured analysis artifacts exist | lower entropy/higher joint accuracy; payoff CI crosses zero | interpreted in paper |
| H1 Confirmation | structurally complete: 90/90 groups x 200 rounds, final `results.csv`, configured analysis artifacts, and source tables exist | interpreted in Section 3.1 | no rerun pending |

## Active Read Order

Read this folder in order: `state.md`, `progress.md`, then `blockers.md`.
Paper-facing evidence in `docs/manuscript/`. Interpreted results in
`docs/results/`. Task-specific handoffs, when needed, live in
`docs/handoffs/`; read them only when named, linked, newly created, or
task-matched.

The next active lane is:
1. Keep paper/docs aligned to the reviewed H1, H5, and Exp A-D interpretations.
   Exp A/B compact outputs now include explicit post-betrayal P0 selection and
   high-investment commitment rates so the older `betrayal_recovery_time`
   readout does not need to carry withdrawal-language claims by itself.
2. If reviewer pressure requires a stronger H1 reward/exposure control, use the
   balanced graded reliability spine, then the reward-matched graded spine, and
   then the strict reward-neutral diagnostic before changing the mechanism
   claim.

Do not create a task-specific handoff document unless a current task needs one.
When a handoff is needed, create it under `docs/handoffs/` and keep durable
project state in this `docs/active/` state/progress/blockers surface.

## Stop Conditions

- A required verification command fails in a way that suggests a design
  problem rather than a local fix.
- H1 confirmation remains reward/exposure-confounded after the bounded
  diagnostic ladder.
- Clinical reruns on the current architecture qualitatively invert the
  expected phenotype ordering.
