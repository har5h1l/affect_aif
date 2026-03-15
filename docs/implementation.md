# Implementation Notes

## Code/Doc Alignment

- `docs/theory.md` is the mechanism-level description.
- `docs/experiment.md` is the task and hypothesis-level description.
- This file records implementation-specific choices that are easy to misread from the theory alone.
- When code changes any of these behaviors, update the docs in the same patch.

## Switching Semantics

- `p_switch` in the environment is the stochastic probability that a partner changes **latent type** after an interaction.
- `switch_round` in the generative model is not that process. It is the exploiter-type partner's internal phase boundary: after enough interactions, an exploiter switches from `p_coop_early` to `p_coop_late`.
- These are intentionally separate:
  - stochastic type switching controls volatility across partner identities
  - exploiter phase switching controls a specific within-type betrayal profile

## Partner Interface Seam

- Scripted `Partner` instances now expose the same minimal lifecycle as agent implementations:
  - `plan_and_act(...)`
  - `observe_outcome(...)`
- This does not change current experiment semantics. Partners are still environment-owned stochastic policies with latent type switching.
- The purpose is architectural: `TrustGameEnv` no longer depends on partner-specific helper names, which makes a later swap to agent-like peers much cleaner.

## Precision Modulation

- `affect_modulates_precision=False` by default.
- When enabled, the current implementation multiplies policy precision by `1 + precision_signal`.
- That means the optional precision path only boosts decisiveness above the base `gamma`; it does not suppress precision below baseline.

## Trust vs Affect

- `use_parameter_learning=True` enables standard Dirichlet updates to the likelihood model after each observed interaction.
- This is an implementation of ordinary parameter learning over the observation model, not a separate trust variable matching the $\tau_k$ notation in [docs/theory.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/docs/theory.md).
- In other words:
  - learned likelihood parameters capture how the agent updates beliefs from evidence
  - affective `beta_k` captures the slow per-partner summary used for terminal values (and optionally precision modulation)
- The current code therefore keeps trust-like evidence accumulation and affective deployment distinct, rather than instantiating a dedicated trust scalar alongside `beta_k`.

## Terminal Values

- Affective and reward-average agents now both emit terminal signals on a comparable `[0, 1]` scale.
- Affective agents use raw `beta_k`.
- Reward-average agents use `0.5 * (1 + tanh(reward_avg / max_abs_payoff))`, which is centered at `0.5` when reward history is neutral.
- Full experiment runs enforce a minimum of `10` calibration episodes when deriving `mu`, even if the config requests fewer.
- This guard exists because `mu` is shared across all affective and control conditions in a run, so calibrating from only `2-3` episodes makes downstream comparisons noisier than intended.
- Direct calls to `ExperimentRunner.calibrate_mu()` can still use fewer episodes for fast unit tests or notebook demos.
- The terminal value actually used in planning is context-sensitive:

```text
V = -mu * signal_k * normalized_continuation_payoff
```

- `RewardAvgAgent` intentionally inherits the base `precision_signal()` implementation, which returns zeros for every partner.
- That means the reward-average control only contributes through terminal values; it does not modulate policy precision even if precision modulation is enabled globally.

## Affective Update Signal

- The current code tracks unsigned surprise, not signed residual error.
- Concretely, it uses `1 - P(observed action)` under the current predictive distribution for that partner.
- The existing `prediction_errors` logging field is kept for backward compatibility, but its semantics are surprise magnitude.

## Verbose Execution Tracing

- `ExperimentConfig` now includes execution-only controls for live tracing and post-run GIF generation:
  - `verbose`
  - `verbosity_mode`
  - `verbosity_include_calibration`
  - `gif_after_run`
  - `gif_output_dir`
- `scripts/run_experiment.py --verbose --verbosity-mode stage_stream` emits structured stage lines from `ExperimentRunner` rather than ad hoc prints.
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
- `scripts/run_experiment.py --make-gifs` calls that helper after writing the results file. `scripts/run_visualization.py` provides the same capability for an existing CSV/parquet file.
- The animation dashboard is intentionally task-facing rather than publication-facing. Each frame shows the current round, partner roster, selected/observed actions, payoff, inferred vs true type, cumulative payoff trajectory, and the per-partner beta or reward-average signal when that signal exists.
- Non-affective conditions render a disabled signal panel instead of fabricating beta values.

## Betrayal Stress Experiment

- The environment supports `initial_partner_types` to seed a specific partner roster.
- It also supports `scheduled_type_switches`, a list of `{round, partner_idx, to_type}` events.
- Scheduled switches are applied at the start of the specified 1-based round, before the selected partner acts, so the agent experiences the switch as an unexpected behavioral change.
- See `affect_aif/configs/betrayal_stress.json` for the reference setup.
- `scripts/run_analysis.py` now detects switch events automatically and writes betrayal-specific artifacts without extra CLI flags:
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
