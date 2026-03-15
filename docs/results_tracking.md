# Results Tracking

This document tracks the current empirical status of the project and the next recommended run. Update it when the user asks for a results refresh after new experiments finish.

## Current Status

As of 2026-03-15, the planned experiment families have been completed and interpreted:

- `default`: 100 replications x 200 rounds, random partner assignment, conditions 1-5
- `betrayal_stress`: 50 replications x 120 rounds, agent-chosen partner, scheduled cooperator -> exploiter switch, conditions 1-3 and 5
- `variant_d`: 100 replications x 200 rounds, random partner assignment with partners 1 and 2 correlated at `correlation_strength = 0.9`, conditions 1-5

## Hypothesis Scorecard

| Hypothesis | Status | Current reading |
|---|---|---|
| H1 affect > baseline | Strongly supported | Condition 2 beats the non-affect controls in all three completed runs, with medium-to-large effects (`default` `d = 0.63`, `betrayal_stress` `d = 1.11`, `variant_d` `d = 0.52`). |
| H2 lesion dissociation | Strongly supported | Condition 3 preserves partner knowledge while losing payoff relative to Condition 2 in all completed runs, matching the Damasio-style pattern. |
| H3 precision > reward average | Confirmed null | Condition 2 and Condition 5 are effectively identical across `default`, `betrayal_stress`, and `variant_d`; even the correlated-partner test left payoff and exploitation nearly unchanged. |
| H4 post-switch robustness | Supported | Condition 2 shows better post-switch recovery than the non-affect baseline in all completed runs, including scheduled betrayal and the correlated-partner variant. |
| H5 partner selection | Supported | In agent-choice mode, beta correlates positively with partner selection frequency. |

## Interpretation

The current story is "4 of 5 hypotheses supported, with 1 confirmed null." H3 is now the main boundary-condition result: in the existing trust-game environments, model calibration and reward history remain too aligned for precision-based affect to cleanly diverge from reward averaging.

This means the theory should be framed as **precision augmentation** rather than pure **depth compensation**. Affect improves shallow evaluation by adding partner-specific confidence information, but the current task does not show that deeper lookahead alone would otherwise solve the problem.

`variant_d` was the last mechanism test worth running in the shipped environment family. It did not rescue H3:

- H1: supported (`C2 = 651.52` vs `C1 = 600.04`, ratio `= 1.086`, `d = 0.52`, `p = 3.0e-4`)
- H2: supported (`C3` accuracy identical to `C1` at `0.4508`, while `C3` payoff stayed below `C2`, `p = 3.0e-4`)
- H3: null (`C2 = 651.52` vs `C5 = 651.64`, `d = -0.001`, `p = 0.99`; exploitation rates both `0.481`)
- H4: supported (`C2` post-switch payoff exceeded `C1`, `p = 1.7e-6`)
- H5: not applicable (`assignment_mode = "random"`)

Beta dynamics were still active in `variant_d` (`mu = 9.09`; mean Condition 2 beta range `= 0.163`, 100 of 100 seeds moved materially), so the H3 null is not a frozen-signal failure. The more defensible interpretation is structural: the current partner-type set does not generate stable cases where prediction accuracy and reward come apart.

## Experimental Phase

The experimental phase is complete. No additional runs are recommended in the current environment family.

Active next step:

- tighten the paper framing around **precision augmentation**
- write up H3 as a confirmed null and theory boundary condition
- use `default`, `betrayal_stress`, and `variant_d` as the final empirical scorecard

## Execution Record

2026-03-15: `variant_d`

- config: `affect_aif/configs/variant_d.json`
- output directory: `results/main_run/variant_d`
- derived `mu`: `9.093529994755983`
- H1: supported
- H2: supported
- H3: confirmed null
- H4: supported
- H5: not applicable
- next-step change: yes; experimental phase complete, shift to theory tightening and write-up

## Execution Record Template

When the user asks to refresh this file after a run, append:

- date
- config name
- command used
- output directory
- derived `mu`
- short read on H1-H5
- whether the recommended next step changed
