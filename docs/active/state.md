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
- `07b31d0` aligns the abstract, introduction, results, and discussion with the
  current evidence tier: H1 and H5 are confirmation targets, and phenotype
  profiles are pending computational targets rather than final outputs.
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
- Exp A-D scripts implemented. The original server run stopped during Exp B;
  recovery is running on server to regenerate Exp A compact outputs, finish Exp
  B, then run Exp D and Exp C with analysis between stages.
- H5 confirmation is running in parallel with the tail of Exp C after a fresh
  June 4 verification gate passed; H1 corrected-readout confirmation remains
  the next core mechanism run once server headroom is available.

## Current Evidence State per Hypothesis

| Hypothesis | Smoke read | Manuscript treatment | Next step |
|---|---|---|---|
| H0 Policy Openness | flat payoff, active deployment | diagnostic deployment-channel readout | confirm only if stronger payoff/general-performance language returns |
| H1 Model Fitness | corrected active-aligned read supports surprise-over-reward but smoke only | claims framed with `\resultp{}` | confirm; redesign only if confounded |
| H2 Deployment | entropy active, payoff flat | deployment interpretation | confirm if needed |
| H3 Locality | local=cleaner signal, global=higher smoke payoff | decomposition claim, not necessity | Exp D provides partial test |
| H4 Social Allocation | underpowered | smoke-scale allocation reorganisation readout | confirm only if this remains a core manuscript claim |
| H5 Betrayal | repaired; affect beats no-affect in smoke | primary behavioral confirmation target | PRIORITY confirmation |
| H6 Perturbation | phenotype dynamics separate | supplemental perturbation section | Exp A-D supersede this |
| Exp A α Sweep | raw complete; compact outputs regenerated operationally | Section 3.6.1 all `\resultp{}` | await Exp A-D finality + review |
| Exp B Prior Factorial | complete: 360/360 runs, compact outputs, and generic analysis | Section 3.6.2 all `\resultp{}` | await Exp A-D finality + review |
| Exp C Forgiveness | running as of June 4 21:10 PDT; partial checkpoint has 107/120 complete seed groups | Section 3.6.3 all `\resultp{}` | recovery running; not ready for interpretation |
| Exp D Mixed Volatility | complete: 80/80 runs, compact outputs, and generic analysis | Section 3.6.4 all `\resultp{}` | operationally ready, but not interpreted |
| H5 Betrayal Confirmation | running as `affect_aif_h5_confirm_20260604`; partial checkpoint has 64/120 complete groups | primary behavioral confirmation target | monitor, then analyze after finality |

## Active Read Order

Read this folder in order: `state.md`, `progress.md`, then `blockers.md`.
Paper-facing evidence in `docs/paper/manuscript/`. Interpreted results in
`docs/results/`. Task-specific handoffs, when needed, live in
`docs/handoffs/`; read them only when named, linked, newly created, or
task-matched.

The next active lane is:
1. Wait for Exp A-D to complete on server and confirm finality before reading
   metric values.
2. Run the applicable analysis on final `results/exp_*/results.csv` outputs and
   inspect the standalone Exp A-D `metrics.csv` files/source tables. Exp A/B
   compact outputs now include explicit post-betrayal P0 selection and
   high-investment commitment rates so the older `betrayal_recovery_time`
   readout does not need to carry withdrawal-language claims by itself.
3. Fill Section 3.6 `\resultp{}` placeholders with actual numbers only after
   finality and user-approved interpretation review.
4. Monitor the running H5 confirmation and analyze only after finality.
5. Run H1 confirmation with the corrected active-aligned and partial-correlation
   readouts; if confirmation remains reward/exposure-confounded, use the
   balanced graded reliability spine, then the reward-matched graded spine, and
   then the strict reward-neutral diagnostic before treating the model as
   failed.

Do not create a task-specific handoff document unless a current task needs one.
When a handoff is needed, create it under `docs/handoffs/` and keep durable
project state in this `docs/active/` state/progress/blockers surface.

## Stop Conditions

- A required verification command fails in a way that suggests a design
  problem rather than a local fix.
- Exp A-D produce results qualitatively inconsistent with the phenotype
  predictions in Section 3.6 (flag to user before updating narrative).
- Confirmation-scale H5 runs reverse the betrayal advantage.
- Clinical reruns on the current architecture qualitatively invert the
  expected phenotype ordering.
