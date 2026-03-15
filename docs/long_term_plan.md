# Long-Term Plan

## Purpose

This document turns the current project priorities into an execution sequence. The main constraint is simple: use the existing single-agent codebase to get the primary empirical result before spending time on architecture work for multi-agent or N-agent extensions.

The order of work is:

1. Run the primary experiment now.
2. Diagnose the Exploiter mechanism next.
3. Tighten the theory after the result pattern is known.
4. Defer the N-agent refactor until the first paper is drafted.

## Guiding Rule

Do not refactor toward N-agent support before the single-agent affect question is answered with full runs and analysis. If the current mechanism fails on the primary hypotheses, the next step is debugging and recalibration, not architecture expansion.

## Phase 1: Primary Results

### Goal

Get the main result tables and first-pass figures from the current codebase.

### Status

Completed for the current baseline:

- `default` has been run and interpreted.
- `betrayal_stress` has been run and interpreted.
- Current headline: 4 of 5 hypotheses supported, with H3 currently an informative null.

### Runs

Historical baseline runs:

- `affect_aif/configs/default.json`
- `affect_aif/configs/betrayal_stress.json`

Target scale:

- 100 seeds / replications
- 5 conditions

Important current-code note:

- `default.json` already uses `num_replications = 100` and conditions `[1, 2, 3, 4, 5]`.
- `betrayal_stress.json` currently uses `num_replications = 50` and conditions `[1, 2, 3, 5]`.
- To match the Phase 1 target, create a full-run betrayal config or update a copy of the existing one before launching the full pass.

### Core questions

- H1: Does Condition 2 approach Condition 1?
- H2: Does Condition 3 show the knowledge-behavior dissociation?
- H3: Does Condition 2 beat Condition 5 on Exploiter detection?
- Is the derived `mu` reasonable relative to the scale of explicit EFE?

### Primary outputs to inspect

For both runs:

- `hypothesis_summary.csv`
- `hypothesis_tests.json`
- `final_round_summary.csv`
- `pairwise_payoff_tests.csv`
- `statistics_summary.txt`
- `affective_movement_summary.csv`

For betrayal-focused runs:

- `betrayal_condition_comparison.csv`
- `betrayal_post_switch_window_1_5.csv`
- `betrayal_post_switch_window_1_10.csv`
- `betrayal_detection_latency.csv`
- `betrayal_trajectories.csv`

### Stop/go criteria

- If H1 is roughly confirmed, move to Phase 2.
- If H1 fails badly, defined here as Condition 2 trailing Condition 1 by more than 15 percent on payoff, stop and debug before doing anything else.

### Debug order if H1 fails

Check these first:

1. Whether the terminal value term is on the right scale relative to explicit EFE.
2. Whether `lambda_smooth = 0.9` is too inertial for beta to meaningfully separate partners over 200 rounds.
3. Whether the derived `mu` is numerically plausible but behaviorally too weak.
4. Whether beta and terminal-signal ranges are materially moving in `affective_movement_summary.csv`.

### Current next step

Do not spend more time on A, B, C, or `cautious_prior` unless the user explicitly asks. The only remaining high-value shipped experiment is `affect_aif/configs/variant_d.json`, because correlated partners are the best available test of whether precision tracking can separate from reward averaging.

### Recommended execution record

For each Phase 1 run, save:

- the exact config used
- the CLI command used
- the derived `mu`
- the git commit hash
- the output directory
- a short note on whether H1-H3 passed, failed, or were ambiguous

## Phase 2: Exploiter Deep-Dive

### Goal

Use the betrayal-stress setup as the primary mechanism test. This is the cleanest diagnostic for whether precision tracking adds something beyond reward averaging.

### Focus

Run the betrayal-stress variant with fine-grained logging and center the analysis on the cooperation-to-defection transition of the scheduled Exploiter.

### Required analysis

- Plot beta trajectories through the switch window.
- Plot reward-average trajectories through the same window.
- Compare Condition 2 versus Condition 5 during the first 5 to 10 encounters after the switch.
- Inspect detection latency and payoff recovery latency.

### Figure target

This should become Figure 5, the centerpiece mechanism figure.

The figure should make it easy to see:

- when the scheduled betrayal occurs
- how quickly Condition 2 updates after the transition
- whether Condition 5 lags because reward history stays attractive
- whether the beta trajectory changes earlier or more cleanly than the reward-average control

## Phase 3: Theory Tightening

### Goal

Revise the paper-level theoretical framing only after the empirical pattern is known.

### Priority items

1. Empirically justify the terminal value approximation.
2. Acknowledge the difference between the current implementation and the Hesp formulation.
3. Expand the trust-versus-affect comparison into a clearer 2x2 table.

### Required empirical support

For the terminal value claim, add an analysis showing the correlation between:

- Condition 2 beta / terminal signal
- actual value-to-go estimated from Condition 1

The point of this section is not just to restate the theory. It is to show that the approximation tracks the deep-planning continuation value well enough to deserve the interpretation used in the paper.

## Phase 4: N-Agent Extension

### Goal

Treat mutual affective inference as a separate project after the first paper is drafted.

### Entry condition

Do not start this phase until:

- the single-agent paper story is stable
- the primary figures are drafted
- the Phase 1 and Phase 2 claims are either supported or clearly delimited

### Scope

1. Refactor `Partner` so it shares the agent interface cleanly.
2. Build a two-agent setup where both agents are active inference agents with affect.
3. Test whether mutual affect tracking produces cooperation dynamics that scripted partners cannot produce.

### Project boundary

This is a second-paper direction, not part of the first-paper critical path.

## Short Operational Summary

- Now: run the main experiments with the current code.
- Next: use betrayal stress as the mechanism deep-dive.
- After results: tighten the theory around what the data actually shows.
- Later: do the N-agent refactor only once the single-agent paper is in draft form.
