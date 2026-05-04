# Implementation Notes

## Code/Doc Alignment

- `docs/theory.md` is the mechanism-level description.
- `docs/experiment.md` is the task and hypothesis-level description.
- This file records implementation-specific choices that are easy to misread from the theory alone.
- When code changes any of these behaviors, update the docs in the same patch.

## Current Trust-Game Status

The shipped trust-game path now uses the action-dependent stance redesign.

- `switch_round`, exploiter early/late phases, and `last_action × phase` likelihood conditioning are no longer part of the supported trust-game semantics.
- `TrustGameModel` is the canonical trust-game model for both binary and graded payoffs (`payoff_mode={"binary","graded"}`).
- The shipped trust-game matrices expose two observation modalities (`o_action`, `o_payoff`) and three hidden/control factors (`type`, `stance`, `own_action`).
- `TrustGameAgent` composes one `aif.Agent` per tracked partner, each with its own `A/B/pA/pB`, while logging shared per-partner joint beliefs over `4 types × 3 stances`.
- The affective helper path now defaults to a discrete HESP beta state with levels `[0.5, 0.67, 1.0, 1.5, 2.0]` and baseline `initial_beta = 1.0`.
- `ExperimentConfig` supports `initial_partner_stances`, `scheduled_stance_switches`, and named `presets`.
- The enforced minimum full-run `mu` calibration count is now `3`, and calibration uses the deepest relevant no-affect condition for the current config rather than always forcing tau-8.

## Switching Semantics

- `p_switch` in the environment is the stochastic probability that a partner changes **latent type** after an interaction.
- `scheduled_stance_switches` is the supported way to induce betrayal-like disruptions in the redesigned task.
- Stance persists across type switches because stance tracks the partner's posterior over the agent, not the exogenous fixed type.

## Partner Interface Seam

- Scripted `Partner` instances now expose the same minimal lifecycle as agent implementations:
  - `plan_and_act(...)`
  - `observe_outcome(...)`
- This does not change current experiment semantics. Partners are still environment-owned stochastic policies with latent type switching.
- The purpose is architectural: `TrustGameEnv` no longer depends on partner-specific helper names, which makes a later swap to agent-like peers much cleaner.

## Precision Modulation

- `affect_modulates_precision=False` by default.
- When enabled, the current implementation uses the HESP inverse-beta mapping `gamma_k = gamma_base / E[beta_k]`.
- That means low beta (high expected precision) sharpens the policy posterior, while high beta (low expected precision) softens it below the base `gamma`.

## Belief updating (state inference)

- Partner social beliefs are updated by the **analytical solution** to variational free energy minimization: for a categorical $q(s)$, the VFE-minimizing posterior equals the Bayesian posterior.
- The current trust-game posterior now conditions on both the observed partner action and the realized payoff, with the payoff likelihood keyed by the agent's own action.
- No gradient descent or iterative VFE minimization is used; the matrix-based update is the closed-form optimum.

## Sophisticated rollout inference

- The trust-game planner now uses observation-branching sophisticated inference for **all** conditions and horizons.
- Implementation-wise, the supported control surface is split across `aif/policies.py`, `aif/efe.py`, `aif/runtime.py`, and `trust/rollout.py`. The rollout path precomputes all binary observation sequences of length `planning_horizon - 1`, evaluates each `(policy, observation-sequence)` path, updates the acted-on partner belief after each hypothetical observation by Bayes rule, and then sums the pathwise EFE under the path probabilities.
- The old mean-field rollout is retained only as an internal comparison path for tests; it is no longer the default decision rule. That retained path now uses observation-weighted expected information gain on non-terminal steps rather than negative ambiguity alone.
- This keeps the planning-method axis controlled across Conditions 1-8, so horizon comparisons are not confounded with different rollout approximations.

## Trust vs Affect

- `use_parameter_learning=True` enables standard Dirichlet updates to the likelihood model after each observed interaction.
- This is an implementation of ordinary parameter learning over the observation model, not a separate trust variable matching the $\tau_k$ notation in [docs/theory.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/docs/theory.md).
- In other words:
  - learned likelihood parameters capture how the agent updates beliefs from evidence
  - affective `beta_k` captures the slow per-partner summary used for shallow-EFE weighting (and optionally precision modulation)
- The current code therefore keeps trust-like evidence accumulation and affective deployment distinct, rather than instantiating a dedicated trust scalar alongside `beta_k`.

## Policy Weighting and Calibration

- Full experiment runs still enforce a minimum of `3` calibration episodes when deriving shared calibration terms such as `mu`, even if the config requests fewer.
- `ExperimentRunner.calibrate_mu()` can still be called directly with fewer episodes for fast unit tests or notebooks.
- The shipped affective runtime no longer exposes a supported `RewardAvgAgent`; the `reward_avgs` metric key remains in the logged schema as a placeholder (`NaN`) for compatibility with historical analysis surfaces.
- Policy differentiation in the current trust runtime is carried by sophisticated rollout plus optional inverse-beta precision modulation (`gamma_k = gamma_base / E[beta_k]`), not by a separate reward-average control path.

## Condition-specific horizons

- `ExperimentConfig.horizon_overrides` can target either numeric core conditions or named presets.
- The supported core sweep is Conditions `1-8` = `{tau=1,2,4,8} × {no_affect, affect}`.
- Named presets (`lesioned`, `no_epistemic`, `alexithymia`, `borderline`, `depression`) default to the tau-4 base unless overridden.

## Affective Update Signal

- The current code tracks unsigned surprise, not signed residual error.
- Concretely, it uses `1 - P(observed action)` under the current predictive distribution for that partner.
- The existing `prediction_errors` logging field is kept for backward compatibility, but its semantics are surprise magnitude.
- Affective agents use `aif.affect.beta.DiscreteBetaState` (HESP-aligned discrete beta filter).
- In that default path, beta is the **rate parameter** of precision: low surprise decreases beta toward `{0.5, 0.67}`, high surprise increases beta toward `{1.5, 2.0}`, and `initial_beta` defaults to `1.0`.
- `num_beta_levels` is accepted only as a legacy config input alias; serialized configs now emit `beta_num_levels`.

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
  - `scripts/benchmark/run_cvc.py`
  - `scripts/benchmark/package_cvc.py`
  Top-level script compatibility wrappers have been removed; use the grouped paths above.
- Historical one-off scripts, archived configs, paper-era claims, and the earlier standalone discrete-beta prototype were salvaged into `docs/results/historical_findings.md` or deleted. They are not runnable workflow surfaces.

## Verbose Execution Tracing

- `ExperimentConfig` now includes execution-only controls for live tracing and post-run GIF generation:
  - `verbose`
  - `verbosity_mode`
  - `verbosity_include_calibration`
  - `gif_after_run`
  - `gif_output_dir`
- `scripts/experiment/run.py --verbose --verbosity-mode stage_stream` emits structured stage lines from `ExperimentRunner` rather than ad hoc prints.
- The current stage stream reports:
  - calibration episode start/end
  - condition start/end
  - replication start/end
  - round start
  - planning start/end
  - environment step start/end
  - belief update start/end
  - metric logging end
- These progress events are observational only. They do not change experiment dynamics, result rows, or analysis semantics.

## GIF Generation

- `affect_aif.analysis.visualization.build_run_gifs(...)` generates one GIF per primary `(condition, seed)` run from an in-memory or reloaded results table.
- `scripts/experiment/run.py --make-gifs` calls that helper after writing the results file. `scripts/analysis/visualize.py` provides the same capability for an existing CSV/parquet file.
- The animation dashboard is intentionally task-facing rather than publication-facing. Each frame shows the current round, partner roster, selected/observed actions, payoff, inferred vs true type, cumulative payoff trajectory, and the per-partner beta or reward-average signal when that signal exists.
- Non-affective conditions render a disabled signal panel instead of fabricating beta values.

## Parallelism

- `scripts/experiment/run.py` accepts multiple `--config` paths and a `--workers` count. With more than one config or `workers > 1`, it uses `BatchExperimentRunner` and a `ProcessPoolExecutor` from the standard library.
- Work is parallelized at replication granularity: calibration episodes, then primary replications (and when `run_sensitivity` is true, sensitivity replications) are submitted to the pool. Each task runs a single replication in a worker process; config and calibration summaries are serialized and passed in. Results are collected in the main process and written per config under `<output-dir>/<batch_id>/<config_slug>/results.csv`.
- Serial mode (exactly one config and `--workers 1`) runs in the main process and supports `--verbose` stage streaming and `--make-gifs`; batch mode disables per-round verbosity but can still use `--verbose` for completion messages and `--make-gifs` to build GIFs per config after all replications finish.

## Betrayal Stress Experiment

- The environment supports `initial_partner_types` to seed a specific partner roster.
- It also supports `initial_partner_stances` and `scheduled_stance_switches`, a list of `{round, partner_idx, to_stance}` events.
- Scheduled stance switches are applied at the start of the specified 1-based round, before the selected partner acts, so the agent experiences the disruption as an unexpected trust violation.
- See `experiments/trust/configs/h4_betrayal_volatility.json` for the reference setup.
- When a config enables `run_sensitivity`, `results.csv` contains both `run_mode="primary"` rows and sensitivity rows. `scripts/analysis/analyze.py` filters to `run_mode == "primary"` before aggregating so post-hoc summaries do not double-count sensitivity sweeps that reuse the same `(condition, seed)` identifiers.
- `scripts/analysis/analyze.py` now detects switch events automatically and writes betrayal-specific artifacts without extra CLI flags:
  - `betrayal_post_switch_window_1_5.csv`
  - `betrayal_post_switch_window_1_10.csv`
  - `betrayal_condition_comparison.csv`
  - `betrayal_detection_latency.csv`
  - `betrayal_trajectories.csv`
  - `affective_movement_summary.csv`
- The round-level schema now logs the raw per-partner `terminal_signal` used for planning, plus `switch_kind`, `current_partner_switched`, `current_partner_scheduled_switch`, `scheduled_switch_partner_ids`, `active_partner`, `selected_partner`, `selected_action`, `best_policy_idx`, `partner_beliefs`, and `partner_posteriors`.
- Detection latency is defined as encounters after the switch until inferred type becomes correct.
- Payoff recovery latency is defined as encounters after the switch until payoff reaches at least `1.0`, meaning the agent is no longer taking sucker-level losses under the default matrix.
- If the betrayal outputs remain flat, treat that as a mechanism null result: beta and terminal-signal dynamics did not move enough to separate precision tracking from reward averaging under the current task and hyperparameters.

## Future Directions

- A stricter variational-beta implementation remains future work; the current shipped path keeps beta as an auxiliary discrete summary state rather than a full hidden-state factor.
- Clinical personality variants (e.g., high-anxiety, low-interoceptive-precision profiles) are config-level parameter changes to the existing affective hyperparameters; no new agent classes are needed.
