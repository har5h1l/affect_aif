# Current Mission

Rebaseline the H0-H8 evidence narrative on the official
`inferactively-pymdp==1.0.0` runtime after shifting the affect update to
Hesp-style partner-action surprisal. The active follow-up surface now combines
the main mechanism tests with global-beta controls, so partner-local and shared
affective precision can be compared in the same rerun pass.

## Scope

- Use official `inferactively-pymdp==1.0.0` as the supported active-inference runtime.
- Keep trust-game model construction, affective precision tracking, experiment
  runners, logging, and analysis in project-owned task and experiment modules.
- Do not reintroduce a custom active-inference engine or supported `aif/` runtime.
- Keep scripts as the canonical experiment and analysis entry points.
- Preserve the Hesp-extension behavior-card spine in
  `docs/theory/hypotheses.md`.
- Keep current docs aligned with the supported H0-H8 experiment surface.
- Treat pre-May-27 bounded-error results as historical/provisional. The first
  three-seed log-surprisal smoke is pre-fix diagnostic evidence after an
  agent-choice aggregation bug was found in the beta-to-gamma path. The
  post-fix three-seed smoke is complete and should be treated as current smoke
  evidence, not publication-grade confirmation.

## Constraints

- Do not treat partial detached rerun outputs as current evidence.
- Do not update result interpretation from new experiment outputs without user
  approval.
- Do not add orchestration or deployment scripts to this repo; use Mango for
  remote VM, sync, and merge flows.
- Do not reintroduce the removed external benchmark integration.
- Re-run the verification gate in `docs/active/progress.md` immediately
  before scheduling any further full experiment reruns.

## Completion State

- The active runtime cutover is complete for official
  `inferactively-pymdp==1.0.0` plus project-owned trust-task wrappers and
  external affective precision tracking.
- The May 18 H0-H5 queue is complete but now historical/provisional because the
  affect update has changed to log-surprisal.
- The manuscript draft has been revised toward a traditional results/discussion
  structure, with clearer game and generative-model descriptions.
- H3 `global_beta` support, a locality/interference smoke config, and generic
  analysis outputs for cross-partner interference have been added.
- A two-seed global-beta smoke run completed at `--workers 1`; it verifies the new
  condition and analysis path but should not yet be treated as manuscript
  evidence.
- The global-beta discovery batch completed at
  `results/h6_global_beta_discovery_20260525/` and standalone analysis outputs
  exist under each `h6/<experiment_id>/analysis/` directory. Treat these as
  documented discovery outputs, not promoted manuscript evidence.
- The focused locality/interference probe completed at
  `results/h6_global_beta_locality_probe_20260526/` with five seeds and
  `--workers 1`. It is mixed discovery evidence: local beta preserves a cleaner
  model-fitness signal, but global beta has higher aggregate payoff in this
  small probe. Do not promote locality to a necessity claim without a revised design.
- The focal-switch follow-up completed at
  `results/h6_global_beta_focal_switch_probe_20260526/` with five seeds and
  `--workers 1`. It replicated the mixed locality pattern: local beta preserved the
  cleaner model-fitness signal, while global beta had higher aggregate payoff.
- The core H0/H1/H2/H4/H5 configs now include `global_beta` variants where
  relevant, so the next rerun can evaluate locality alongside the main
  mechanism spine.
- The reduced pre-fix log-surprisal H0-H6 smoke completed at
  `results/log_surprisal_spine_smoke_20260527/` and analysis outputs exist for
  all seven queued configs. Follow-up tracing found an agent-choice candidate
  aggregation bug where low-precision negative-score branches could become
  overly selectable. The runtime now uses centered precision logits for
  cross-partner candidate comparison, so the smoke must be rerun before
  publication claims.
- The post-fix H0-H6 smoke completed at
  `results/log_surprisal_spine_smoke_postfix_20260528/` and analysis outputs
  exist for all seven queued configs. At three seeds, the H5 betrayal-choice
  read flips from a warning to a repaired smoke-scale advantage for local
  affect (`1322.3` mean payoff versus `1225.0` for no-affect/lesioned), while
  H0/H1/H2/H4 remain flat-to-negative on payoff, H1 does not preserve the old
  surprise-over-reward model-fitness readout, and H3 still favors global beta in
  aggregate reward.
- The manuscript results section has been reframed around smoke-scale
  log-surprisal evidence. It should not be treated as figure-complete or final
  publication evidence until confirmation-scale reruns replace the diagnostic
  numbers.

## Current Handoff

Read this folder in order: `state.md`, `progress.md`, then `blockers.md`.
Paper-facing evidence remains in `docs/paper/manuscript/` and interpreted
results remain in `docs/results/`.

The next active lane is to convert the post-fix smoke into a publication plan:
run the verification gate, then queue confirmation-scale reruns only for the
claims that survive smoke inspection. H5 is the repaired positive anchor; H1
needs confirmation or redesign before carrying the model-fitness claim;
H0/H2/H4 require either confirmation or softened manuscript language. H7 and H8
are exploratory lanes, not first-queue requirements.

Do not create a separate handoff document; keep the live handoff in this
`docs/active/` state/progress surface.

## Stop Conditions

- A required verification command fails in a way that suggests a design problem
  rather than a local fix.
- Shallow reruns on the current architecture contradict H0 by showing no affect
  benefit in any policy-space regime.
- Clinical reruns on the current architecture qualitatively invert the expected
  phenotype ordering.
