# Results Tracking

This document tracks the current empirical status of the project and the next recommended run. Update it when the user asks for a results refresh after new experiments finish.

## Current Status

As of 2026-03-15, two experiment families have been completed and interpreted:

- `default`: 100 replications x 200 rounds, random partner assignment, conditions 1-5
- `betrayal_stress`: 50 replications x 120 rounds, agent-chosen partner, scheduled cooperator -> exploiter switch, conditions 1-3 and 5

## Hypothesis Scorecard

| Hypothesis | Status | Current reading |
|---|---|---|
| H1 affect > baseline | Supported | Condition 2 beats the non-affect controls in both completed runs; effect size is medium in `default` and large in `betrayal_stress`. |
| H2 lesion dissociation | Supported | Condition 3 preserves partner knowledge but loses payoff relative to Condition 2, matching the Damasio-style pattern. |
| H3 precision > reward average | Informative null | Condition 2 and Condition 5 are effectively equivalent in the completed tasks; this is a task-structure null, not an analysis failure. |
| H4 post-switch robustness | Supported | Condition 2 shows better post-switch recovery than the non-affect baseline, including under betrayal stress. |
| H5 partner selection | Supported | In agent-choice mode, beta correlates positively with partner selection frequency. |

## Interpretation

The current story is "4 of 5 hypotheses supported, with 1 informative null." The informative null is H3: in the existing trust-game environments, model calibration and reward history are too aligned for precision-based affect to cleanly diverge from reward averaging.

This means the theory should be framed as **precision augmentation** rather than pure **depth compensation**. Affect improves shallow evaluation by adding partner-specific confidence information, but the current task does not show that deeper lookahead alone would otherwise solve the problem.

## Recommended Next Run

Run `affect_aif/configs/variant_d.json` next and only if you want one more mechanism test before write-up.

Why `variant_d`:

- It is the only shipped variant that introduces hidden correlation structure between partners.
- Correlated partners create indirect information that prediction-error tracking can exploit even when reward averaging cannot.
- Variants A, B, C, and `cautious_prior` are now mostly redundant with completed results or weaker robustness checks.

## What To Inspect After `variant_d`

Primary files:

- `results/<batch_name>/variant_d/results.csv`
- `results/<batch_name>/variant_d/figures/hypothesis_summary.csv`
- `results/<batch_name>/variant_d/figures/hypothesis_tests.json`
- `results/<batch_name>/variant_d/figures/final_round_summary.csv`
- `results/<batch_name>/variant_d/figures/pairwise_payoff_tests.csv`
- `results/<batch_name>/variant_d/figures/affective_movement_summary.csv`

Decision rule:

- If Condition 2 now separates from Condition 5, H3 survives in a structure-learning setting.
- If Condition 2 still matches Condition 5, stop running variants and write up the null as a real boundary condition on the theory.

## Execution Record Template

When the user asks to refresh this file after a run, append:

- date
- config name
- command used
- output directory
- derived `mu`
- short read on H1-H5
- whether the recommended next step changed
