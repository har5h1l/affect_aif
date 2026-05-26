# Implementation Notes

## Code/Doc Alignment

- `docs/theory/theory.md` is the mechanism-level description.
- `docs/experiment/design.md` is the task and hypothesis-level description.
- This file records implementation-specific choices that are easy to misread from the theory alone.
- When code changes any of these behaviors, update the docs in the same patch.

## Current Trust-Game Status

The shipped trust-game path now uses the action-dependent stance redesign.

- `switch_round`, exploiter early/late phases, and `last_action × phase` likelihood conditioning are no longer part of the supported trust-game semantics.
- `tasks.trust.pomdp.build_trust_pomdp_template(...)` is the canonical trust-game matrix surface for both binary and graded payoffs (`payoff_mode={"binary","graded"}`).
- The shipped trust-game matrices expose two observation modalities (`o_action`, `o_payoff`) and three hidden/control factors (`type`, `stance`, `own_action`).
- Experiments instantiate one official `pymdp.Agent` per tracked partner and hold them in a `PartnerBank`, with project-owned trust-game `A/B/C/D/E` construction and logging of per-partner joint beliefs over `4 types × 3 stances`.
- The affective helper path now defaults to a discrete HESP beta state with levels `[0.5, 0.67, 1.0, 1.5, 2.0]` and baseline `initial_beta = 1.0`.
- TOML `ExperimentSpec` files under `configs/` are the maintained public experiment surface. Trust specs use `experiment.family = "trust"` under `configs/trust/`; benchmark specs use `experiment.family = "benchmark"` under `configs/benchmark/`. `ExperimentConfig` remains the internal trust runtime adapter for environment and POMDP construction.

## Switching Semantics

- `p_switch` in the environment is the stochastic probability that a partner changes **latent type** after an interaction.
- `scheduled_stance_switches` is the supported way to induce betrayal-like disruptions in the redesigned task.
- Stance persists across type switches because stance tracks the partner's posterior over the agent, not the exogenous fixed type.

## Partner Environment Interface

- Scripted `Partner` instances remain environment-owned stochastic policies with latent type switching.
- Their small environment-facing protocol is separate from the active-inference runtime. Official `pymdp.Agent` objects are used only on the focal experiment side.

## Precision Modulation

- Affective native runtimes use the HESP inverse-beta mapping `gamma_k = gamma_base / E[beta_k]`.
- That means low beta (high expected precision) sharpens the policy posterior, while high beta (low expected precision) softens it below the base `gamma`.
- Lesioned runtimes use `affect_mode="decouple"` to leave beta updates intact while forcing `gamma_k = gamma_base`.
- In `agent_choice` mode, the final candidate selector applies the selected
  partner's `gamma_k` to each candidate policy score before the global softmax,
  so partner-choice policies use the same precision channel as assigned-partner
  action policies.

## Belief updating (state inference)

- Partner social beliefs are updated by the **analytical solution** to variational free energy minimization: for a categorical $q(s)$, the VFE-minimizing posterior equals the Bayesian posterior.
- The current trust-game posterior now conditions on both the observed partner action and the realized payoff, with the payoff likelihood keyed by the agent's own action.
- No gradient descent or iterative VFE minimization is used; the matrix-based update is the closed-form optimum.

## Sophisticated rollout inference

- The trust-game planner now uses observation-branching sophisticated inference for **all** variants and horizons.
- Implementation-wise, the supported control surface is official `pymdp.Agent` plus procedural task helpers. `tasks.trust.pomdp` builds the task-specific A/B/C/D/E matrices, `tasks.trust.runtime` evaluates partner-local agents, updates the acted-on partner belief after each observation, and records snapshots for logging.
- The internal rollout comparison path used by tests is not the default decision rule. That path uses observation-weighted expected information gain on non-terminal steps rather than negative ambiguity alone.
- This keeps the planning-method axis controlled across variants, so horizon comparisons are not confounded with different rollout approximations.

## Trust vs Affect

- `use_parameter_learning=True` enables standard Dirichlet updates to the likelihood model after each observed interaction.
- This is an implementation of ordinary parameter learning over the observation model, not a separate trust variable matching older archived $\tau_k$ notation.
- In other words:
  - learned likelihood parameters capture how the agent updates beliefs from evidence
  - affective `beta_k` captures the slow per-partner summary used for partner-local policy precision
- The current code therefore keeps trust-like evidence accumulation and affective deployment distinct, rather than instantiating a dedicated trust scalar alongside `beta_k`.

## Native Precision Surface

- Policy differentiation in the current trust runtime is carried by native pymdp policy inference plus inverse-beta precision modulation for affective runtimes (`gamma_k = gamma_base / E[beta_k]`), not by a separate reward-average control path.

## TOML Experiment Expansion

- `experiments.trust.spec.ExperimentSpec` parses the hierarchy
  `hypothesis -> experiment -> scenario -> variants -> sweeps`.
- `ExperimentSpec.expand_runs()` schedules
  `experiment x variants x sweeps x replications`.
- Each expanded run adapts to `ExperimentConfig` immediately before environment
  and `pymdp.Agent` construction.
- Planning horizon is a normal variant knob (`planning_horizon`) rather than a
  numeric condition category.
- `affect = "none"` builds a base runtime, `affect = "precision"` builds the
  normal partner-local beta-to-gamma runtime, `affect = "tracked_only"` builds
  the beta tracker while decoupling it from policy precision, and
  `affect = "global_beta"` builds one shared beta tracker that modulates every
  partner's policy precision.

## Affective Update Signal

- The current code tracks unsigned surprise, not signed residual error.
- Concretely, it uses `1 - P(observed action)` under the current predictive distribution for that partner.
- The `prediction_errors` logging field records surprise magnitude.
- Affective variants use task-local precision tracking around `pymdp.Agent` policy inference; beta is external to the POMDP state space and remains owned by trust-task modules.
- In that default path, beta is the **rate parameter** of precision: low surprise decreases beta toward `{0.5, 0.67}`, high surprise increases beta toward `{1.5, 2.0}`, and `initial_beta` defaults to `1.0`.
- The `global_beta` ablation uses the same update law but routes every
  interaction through beta entity `0`. Partner-local POMDP beliefs remain
  separate; only the beta precision signal is shared across partners.

## Supported Surface

- The supported CLI wrappers are:
  - `scripts/experiment/run.py`
  - `scripts/experiment/smoke.py`
  - `scripts/experiment/inspect.py`
  - `scripts/experiment/preliminary.py`
  - `scripts/analysis/analyze.py`
  - `scripts/analysis/summarize.py`
  - `scripts/analysis/visualize.py`
  - `scripts/analysis/model_comparison.py`
  - `scripts/benchmark/run.py`
  - ``
  Use the grouped paths above for all supported CLI work.

## Verbose Execution Tracing

- Execution-only controls for live tracing and post-run GIF generation are owned by CLI flags, not by TOML `ExperimentSpec` or runtime `ExperimentConfig`.
- `scripts/experiment/run.py --verbose --verbosity-mode stage_stream` emits structured stage lines from `ExperimentRunner` rather than ad hoc prints on supported serial paths.
- The current stage stream reports:
  - variant start/end
  - replication start/end
  - round start
  - planning start/end
  - environment step start/end
  - belief update start/end
  - metric logging end
- These progress events are observational only. They do not change experiment dynamics, result rows, or analysis semantics.

## GIF Generation

- `affect_aif.analysis.visualization.build_run_gifs(...)` generates one GIF per `(variant_id, seed)` run from an in-memory or reloaded results table.
- `scripts/experiment/run.py --make-gifs` calls that helper after writing the results file. `scripts/analysis/visualize.py` provides the same capability for an existing CSV/parquet file.
- The animation dashboard is intentionally task-facing rather than publication-facing. Each frame shows the current round, partner roster, selected/observed actions, payoff, inferred vs true type, cumulative payoff trajectory, and the per-partner beta signal when that signal exists.
- Non-affective variants render a disabled signal panel instead of fabricating beta values.

## Parallelism

- `scripts/experiment/run.py` accepts multiple TOML `--config` paths and a `--workers` count. With more than one config or `workers > 1`, it uses `BatchExperimentRunner` and a `ProcessPoolExecutor` from the standard library.
- Work is parallelized at expanded-run granularity. Each worker receives a serialized experiment spec plus a serialized `ExpandedRunSpec`; results are collected in the main process and written under `<output-dir>/<batch_name>/<hypothesis_id>/<experiment_id>/results.csv`.
- Batch and serial trust runs checkpoint after each completed expanded run.
  `results_partial.csv` stores row-level progress, while
  `checkpoint_manifest.json` records completed `variant_id`, `seed`, and
  `replication` keys. Reusing the same `--batch-name` resumes from these files
  and schedules only missing expanded runs.
- Sweeps are expanded into concrete variant runs, so the old sensitivity worker path is no longer part of maintained TOML execution.
- Serial mode (exactly one config and `--workers 1`) runs in the main process and supports `--verbose` stage streaming and `--make-gifs`; batch mode disables per-round verbosity but can still use `--verbose` for completion messages and `--make-gifs` to build GIFs per config after all replications finish.

## Betrayal Stress Experiment

- The environment supports `initial_partner_types` to seed a specific partner roster.
- It also supports `initial_partner_stances` and `scheduled_stance_switches`, a list of `{round, partner_idx, to_stance}` events.
- Scheduled stance switches are applied at the start of the specified 1-based round, before the selected partner acts, so the agent experiences the disruption as an unexpected trust violation.
- See `configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml`
  for the reference setup.
- Sensitivity-style studies should use explicit `[[sweeps]]` blocks in TOML.
  Expanded sweep runs are ordinary variant runs with concrete `variant_id`
  values.
- `scripts/analysis/analyze.py` now detects switch events automatically and writes betrayal-specific artifacts without extra CLI flags:
  - `betrayal_post_switch_window_1_5.csv`
  - `betrayal_post_switch_window_1_10.csv`
  - `betrayal_phase_summary.csv`
  - `betrayal_variant_comparison.csv`
  - `betrayal_detection_latency.csv`
  - `betrayal_trajectories.csv`
  - `betrayal_misdeployment_summary.csv`
  - `betrayal_reallocation_summary.csv`
  - `affective_movement_summary.csv`
- Generic analysis also writes `deployment_dissociation_summary.csv`,
  `partner_choice_summary.csv`, and `phenotype_validation_summary.csv` so H2,
  H4, and H5 can be read without relying on whole-run payoff alone.
- `betrayal_phase_summary.csv` separates each scheduled or observed switch into
  `pre_switch`, `acute_post_switch`, and `post_acute_tail` encounters for the
  switched partner. This is the primary diagnostic for cases where whole-run
  payoff and immediate recovery move in different directions.
- The round-level schema now logs the raw per-partner `terminal_signal` used for planning, plus `switch_kind`, `current_partner_switched`, `current_partner_scheduled_switch`, `current_partner_scheduled_stance_switch`, `scheduled_switch_partner_ids`, `scheduled_stance_switch_partner_ids`, `active_partner`, `selected_partner`, `selected_action`, `best_policy_idx`, `partner_beliefs`, and `partner_posteriors`.
- Detection latency is defined as encounters after the switch until inferred type becomes correct.
- Payoff recovery latency is defined as encounters after the switch until payoff reaches at least `1.0`, meaning the agent is no longer taking sucker-level losses under the default matrix.
- Reallocation summaries are one row per switch event and report post-switch
  decisions, whether the agent returned to the switched partner,
  decisions/rounds to first re-encounter, selection rate after the switch, and
  payoff/entropy conditional on re-encounter.
- Misdeployment summaries report post-switch wrong-type, bad-payoff,
  low-entropy, and overconfident-wrong rates so H3 can distinguish recovery
  wins from precision-sharpened wrong deployment.
- In agent-choice runs, post-switch window summaries retain scheduled switch
  events even when the agent does not re-encounter the switched partner in the
  requested window. Those rows use `encounters = 0` and NaN outcome metrics so
  avoidance/no-return remains visible instead of being silently dropped.
- If betrayal outputs remain flat in future variants, treat that as a mechanism
  null for that stress regime: beta and policy dynamics did not move enough to
  separate affective deployment from the no-affect or lesioned baseline under
  the current task and hyperparameters.

## Global-Beta Locality Ablation

- `configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml`
  is a discovery smoke config, not a final statistical run.
- It compares `none`, `precision`, `tracked_only`, and `global_beta` in an
  agent-choice task with one scheduled stance switch.
- The key diagnostic is cross-partner interference: whether a beta update caused
  by the switched partner spreads precision changes to untouched partners.

## Future Directions

- A stricter variational-beta implementation remains future work; the current shipped path keeps beta as an auxiliary discrete summary state rather than a full hidden-state factor.
- Clinical personality variants (e.g., high-anxiety, low-interoceptive-precision profiles) are config-level parameter changes to the existing affective hyperparameters; no new agent classes are needed.
