# Results Tracking

This document tracks the current empirical status of the project and the next recommended run. Update it when the user asks for a results refresh after new experiments finish.

## Current Status

As of 2026-03-15, the core sophisticated-inference experiment families have been completed and interpreted:

- `default`: 100 replications x 200 rounds, random partner assignment, conditions 1-5
- `betrayal_stress`: 50 replications x 120 rounds, agent-chosen partner, scheduled cooperator -> exploiter switch, conditions 1-3 and 5
- `horizon_sweep`: 100 replications x 200 rounds, random partner assignment, conditions 1, 2, 4, 6, and 7
- prior variants have been rerun as archive/supporting checks, but the active scorecard is now anchored to the three configs above because they isolate the current theory questions most cleanly

## Headline

The main empirical update is: under sophisticated inference, explicit planning depth is irrelevant in the shipped binary-action task.

In `horizon_sweep`, all non-affective planners are statistically identical:

- `C1 deep_no_affect = 529.26`
- `C7 intermediate_4_no_affect = 529.40`
- `C6 intermediate_3_no_affect = 529.82`
- `C4 shallow_no_affect = 530.04`
- every pairwise comparison among those four conditions has `p > 0.93`

Condition 2 remains clearly better than each non-affect condition:

- `C2 affective_shallow = 575.06`
- `C2` vs `C1`: `d = 0.64`, `p = 1.1e-5`
- `C2` vs `C4`: `p = 1.4e-5`
- `C2` vs `C6`: `p = 1.3e-5`
- `C2` vs `C7`: `p = 1.1e-5`

The defensible story is therefore no longer "affect compensates for shallow depth." It is "affect provides value beyond explicit planning depth."

## Hypothesis Scorecard

| Hypothesis | Status | Current reading |
|---|---|---|
| H1 affect > non-affect baselines | Strongly supported | `default` supports it (`d = 0.64`, `p = 1.1e-5`), `betrayal_stress` supports it more strongly (`d = 1.30`, `p = 6.8e-9`), and `horizon_sweep` shows the entire non-affect depth curve is flat. |
| H2 lesion dissociation | Strongly supported | In `default`, lesion accuracy matches deep planner accuracy (`p = 0.96`) while payoff drops relative to affect (`p = 1.4e-5`). In `betrayal_stress`, the same pattern holds (`p = 0.55` for accuracy, `p = 9.6e-7` for payoff). `C3 = C4` exactly in `default`, confirming the lesion is a clean affect-to-action decoupling. |
| H3 precision > reward average | Context-dependent support | `default` is a null (`d = 0.009`, `p = 0.95`), but `betrayal_stress` supports the mechanism (`C2 = 481.88`, `C5 = 428.32`, `d = 0.59`, `p = 0.004`). Precision tracking matters when prediction error and reward come apart. |
| H4 post-switch robustness | Supported | `default`: `C2` beats `C1` (`p = 2.8e-9`) and `C4` (`p = 5.4e-9`) in the post-switch window. `betrayal_stress`: `C2` beats `C1` (`p = 0.013`). |
| H5 partner selection | Supported | In `betrayal_stress`, beta correlates with partner selection frequency (`r = 0.51`, `p = 2.9e-9`). |

## Interpretation

The old framing was "affect compensates for shallow planning depth." The current data do not support that. Once mean-field rollouts are replaced by sophisticated inference, non-affective planning depth from `τ = 2` through `τ = 8` has no measurable marginal value in the default task.

The stronger framing is:

- affect is an augmentation, not a compensation
- the mean-field approximation was the real bottleneck, not horizon length
- the affective signal adds partner-specific precision weighting that explicit depth alone does not recover in this task

H3 also needs a narrower reading than before. It is not a universal null and not a universal win. It is a context-dependent mechanism result:

- null when predictive reliability and reward history stay aligned
- supported when betrayal creates a temporary prediction-reward dissociation

The beta dynamics remain active in both primary runs, so the results are not a frozen-signal artifact:

- `default`: mean Condition 2 beta range `= 0.164`, 100% of seeds move materially
- `betrayal_stress`: mean Condition 2 beta range `= 0.134`, 100% of seeds move materially

## Experimental Phase

The core documentation-facing experimental phase is not closed yet, but it is narrower now.

Recommended next step:

- run `affect_aif/configs/deep_affect_test.json` to compare `C8` against `C2` and `C1`

Why this is the right next run:

- if `C8 ~= C2`, that further supports the "affect value is orthogonal to depth" interpretation
- if `C8 > C2`, then affect and depth interact after all, and the current reframing needs to become more conditional

## Execution Record

2026-03-15: `default`

- config: `affect_aif/configs/default.json`
- output directory: `results/main_run/default`
- headline: H1, H2, and H4 supported; H3 null in the baseline random-assignment task
- key numbers: `C1 = 529.26`, `C2 = 575.06`, `C3 = 530.04`, `C4 = 530.04`, `C5 = 574.42`
- interpretation change: yes; `C3 = C4` exactly confirms the lesion implementation, and H3 becomes a baseline null rather than a final global read

2026-03-15: `betrayal_stress`

- config: `affect_aif/configs/betrayal_stress.json`
- output directory: `results/main_run/betrayal_stress`
- headline: H1, H2, H4, and H5 supported; H3 separates positively under scheduled betrayal
- key numbers: `C1 = 399.80`, `C2 = 481.88`, `C3 = 419.44`, `C5 = 428.32`
- interpretation change: yes; H3 is no longer a confirmed null because betrayal cleanly separates precision tracking from reward averaging

2026-03-15: `horizon_sweep`

- config: `affect_aif/configs/horizon_sweep.json`
- output directory: `results/main_run/horizon_sweep`
- headline: all non-affective horizons are tied; affect remains better than every one of them
- key numbers: `C1 = 529.26`, `C7 = 529.40`, `C6 = 529.82`, `C4 = 530.04`, `C2 = 575.06`
- interpretation change: yes; the old depth-compensation story is no longer defensible under sophisticated inference

## Execution Record Template

When the user asks to refresh this file after a run, append:

- date
- config name
- command used
- output directory
- derived `mu`
- short read on H1-H5
- whether the recommended next step changed
