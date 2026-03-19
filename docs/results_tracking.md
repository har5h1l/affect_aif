# Results Tracking

This document tracks the current empirical status of the project and the next recommended run. Update it when the user asks for a results refresh after new experiments finish.

## Current Status

As of 2026-03-15, the core sophisticated-inference experiment families have been completed and interpreted:

- `default`: 100 replications x 200 rounds, random partner assignment, conditions 1-5
- `betrayal_stress`: 50 replications x 120 rounds, agent-chosen partner, scheduled cooperator -> exploiter switch, conditions 1-3 and 5
- `horizon_sweep`: 100 replications x 200 rounds, random partner assignment, conditions 1, 2, 4, 6, and 7
- `deep_affect_test`: follow-up comparison of conditions 1, 2, and 8, confirming that affect's payoff gain is depth-independent in the shipped task
- prior variants have been rerun as archive/supporting checks, but the active scorecard is now anchored to these four configs because they isolate the current theory questions most cleanly

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

The defensible story is therefore no longer "affect compensates for shallow depth." It is "affect provides orthogonal augmentation beyond explicit planning depth."

`deep_affect_test` closes the loop on that interpretation:

- `C8 deep_affective ≈ 576`
- `C2` vs `C8`: `p = 0.94`
- affect adds roughly `+46` payoff points whether planning depth is `τ = 2` or `τ = 8`

So the current evidence is stronger than "affect beats shallow non-affect." It is that affect and depth are orthogonal in the shipped binary-action task: affect matters, depth does not.

## Hypothesis Scorecard

| Hypothesis | Status | Current reading |
|---|---|---|
| H1 affect > non-affect baselines | Strongly supported | `default` supports it (`d = 0.64`, `p = 1.1e-5`), `betrayal_stress` supports it more strongly (`d = 1.30`, `p = 6.8e-9`), and `horizon_sweep` shows the entire non-affect depth curve is flat. |
| H2 lesion dissociation | Strongly supported | In `default`, lesion accuracy matches deep planner accuracy (`p = 0.96`) while payoff drops relative to affect (`p = 1.4e-5`). In `betrayal_stress`, the same pattern holds (`p = 0.55` for accuracy, `p = 9.6e-7` for payoff). `C3 = C4` exactly in `default`, confirming the lesion is a clean affect-to-action decoupling. |
| H3 precision > reward average | Task-dependent | Binary default: null (`d = 0.009`). Binary betrayal: C2 wins (`d = 0.59`, `p = 0.004`). Graded default: C5 wins (`d = 0.43`). Graded betrayal: C5 wins (`d = −0.89`). Precision tracking helps when decisions are binary and model fitness diverges from reward; reward averaging dominates in continuous-investment settings where the reward gradient is directly decision-relevant. |
| H4 post-switch robustness | Supported | `default`: `C2` beats `C1` (`p = 2.8e-9`) and `C4` (`p = 5.4e-9`) in the post-switch window. `betrayal_stress`: `C2` beats `C1` (`p = 0.013`). |
| H5 partner selection | Supported | In `betrayal_stress`, beta correlates with partner selection frequency (`r = 0.51`, `p = 2.9e-9`). |

## Interpretation

The old framing was "affect compensates for shallow planning depth." The current data do not support that framing. Once mean-field rollouts are replaced by sophisticated inference, non-affective planning depth from `τ = 2` through `τ = 8` has no measurable marginal value in the default task.

The stronger framing is:

- affect is an orthogonal augmentation, not a depth compensation
- the mean-field approximation was the real bottleneck, not horizon length
- the affective signal adds partner-specific precision weighting that explicit depth alone does not recover in this task
- adding affect at depth `τ = 8` reproduces the same payoff lift as adding affect at depth `τ = 2`, so the gain is not a hidden depth substitute

H3 also needs a narrower reading than before. It is not a universal null and not a universal win. It is a context-dependent mechanism result:

- null when predictive reliability and reward history stay aligned
- supported when betrayal creates a temporary prediction-reward dissociation

The beta dynamics remain active in both primary runs, so the results are not a frozen-signal artifact:

- `default`: mean Condition 2 beta range `= 0.164`, 100% of seeds move materially
- `betrayal_stress`: mean Condition 2 beta range `= 0.134`, 100% of seeds move materially
- `deep_affect_test`: mean beta range is effectively identical for `C2` and `C8` (`0.1636` vs `0.1640`), consistent with the same affective mechanism operating at both depths

## Terminal Value Approximation Analysis

Within-C2 analysis in the graded game: does beta predict future payoffs from the same partner?

- Within-round correlation between beta and average future payoff: median $r = -0.01$ across rounds 20–180, none significant after correction
- Beta tercile analysis: high-beta ($\bar{\beta} = 0.616$) vs low-beta ($\bar{\beta} = 0.468$) partners show indistinguishable future payoffs ($d = -0.03$, $p = 0.21$)
- Per-partner-type partial correlations (controlling for round): all $|r| < 0.1$

This null is predicted by the theory: beta tracks prediction accuracy, not reward quality. A cooperator and an exploiter can both produce high beta if the agent predicts them well. The null validates that beta contributes orthogonal information rather than approximating a value cache.

## Experimental Phase

Phase 3 (theory tightening) is complete. All tasks done including the terminal value analysis, graded game integration, and C5 > C2 explanation.

Current read:

- Binary game establishes the core orthogonal augmentation claim
- Graded game activates the precision channel, reveals C5 > C2 as a task-specificity result, and restores clinical sensitivity
- Beta does not approximate value-to-go, confirming orthogonality
- Phase 4 (variational beta) is the next step

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
- interpretation change: yes; the old depth-compensation story is replaced by orthogonal augmentation under sophisticated inference

2026-03-15: `deep_affect_test`

- config: `affect_aif/configs/deep_affect_test.json`
- output directory: `results/main_run/deep_affect_test`
- headline: `C8` and `C2` are statistically identical, confirming that affect's value is independent of explicit planning depth in the shipped task
- key numbers: `C1 = 529.26`, `C2 = 575.06`, `C8 ≈ 576`, `C2 vs C8: p = 0.94`
- interpretation change: yes; the augmentation story is now directly supported rather than inferred only from the flat non-affect depth curve

## Graded Investment Trust Game Results

### Context

The binary trust game produced strong results for the core claim (affect provides orthogonal augmentation), but clinical sensitivity analysis showed the binary game is too unambiguous — EFE gaps of ~10.83 make softmax a hard argmax, so clinical parameter variations produce <0.5% behavioral effects. The graded investment trust game (6 investment levels × 4 partners = 24 actions) was designed to create a more ambiguous decision landscape where precision modulation can differentiate conditions.

**Key fix**: the mu calibration formula returned 0 when `deep_horizon == shallow_horizon` (both must be 2 in the graded game due to combinatorial explosion). Fixed by using `max(1, horizon_gap)` so mu scales by 1× mean EFE magnitude when horizons are equal.

### Graded Default (agent_choice, all horizons = 2)

- config: `affect_aif/configs/graded_trust.json`
- output: `results/graded_trust_default.csv`
- 5 conditions × 100 replications × 200 rounds
- calibrated mu: ~2.36

| Condition | Mean payoff | q_pi_entropy | vs C4 diff | Cohen's d | p |
|---|---|---|---|---|---|
| C1 deep (h=2) | 10.184 | 5.80 | — | — | — |
| C4 shallow | 10.184 | 5.80 | — | — | — |
| C3 lesioned | 10.184 | 5.80 | — | — | — |
| C2 affective | 10.394 | 4.51 | +0.21 | 1.14 | <0.0001 |
| C5 reward avg | 10.468 | 4.16 | +0.28 | 1.72 | <0.0001 |

Key findings:
- **q_pi_entropy ~5.8** (vs <0.01 in binary) — the graded game IS ambiguous, activating the precision modulation channel
- **C2 >> C4** (d=1.14) — affect provides strong augmentation in the graded game
- **C1 = C3 = C4** — same horizon, lesion strips affect, all collapse to identical behavior
- **C5 > C2** (d=0.43) — reward averaging outperforms precision tracking in the default task

### Graded Betrayal Stress (agent_choice, scheduled cooperator→exploiter switch at round 31)

- config: `affect_aif/configs/graded_betrayal_stress.json`
- output: `results/graded_betrayal_stress.csv`
- 4 conditions × 50 replications × 120 rounds

| Window | C1/C3 | C2 (affect) | C5 (reward avg) |
|---|---|---|---|
| Pre (20-29) | 10.54 | 10.46 | 11.01 |
| Betrayal (30-39) | 10.39 | 10.28 | 10.55 |
| Impact (40-49) | 9.83 | 9.97 | 10.24 |
| Recovery (60-69) | 10.25 | 10.43 | 11.05 |
| Late (100-109) | 10.59 | 10.79 | 11.02 |

Post-betrayal C2 vs C5: t=−6.20, p<0.0001, d=−0.89. C5 dominates throughout. Both C2 and C5 recover from betrayal (payoffs increase post-dip), while C1/C3 suffer more and recover more slowly.

### Graded Clinical Sensitivity (random assignment, horizons = 2)

All three clinical conditions use `random` assignment and compare against C4 (no affect).

| Condition | Parameters | Mean payoff | vs C4 diff | Cohen's d | p |
|---|---|---|---|---|---|
| C4 (no affect) | baseline | 10.134 | — | — | — |
| C9 (alexithymia) | α=0.1 | 10.324 | +0.190 | 2.20 | <0.0001 |
| C10 (borderline) | α=12, λ=0.5 | 10.353 | +0.218 | 2.20 | <0.0001 |
| C11 (depression) | β₀=0.2 | 10.331 | +0.196 | 2.17 | <0.0001 |

All three clinical conditions massively outperform C4 (d ≈ 2.2). However, the between-clinical differentiation is small (10.324–10.353 range). The clinical conditions differ from no-affect but not much from each other.

Contrast with binary game: clinical conditions showed <0.5% behavioral effects in the binary game. In the graded game, the effect is ~1.9% — a ~4× improvement in sensitivity.

### Revised Hypothesis Scorecard (Graded Game)

| Hypothesis | Binary game | Graded game |
|---|---|---|
| H1 affect > non-affect | d=0.64 | d=1.14 (stronger) |
| H2 lesion dissociation | C3=C4 | C3=C4 (confirmed) |
| H3 precision > reward avg | null in default, d=0.59 in betrayal | **C5 > C2 in both default and betrayal** |
| H4 post-switch robustness | C2 beats C1/C4 post-switch | C2 recovers faster than C1/C3 (confirmed, but C5 recovers faster still) |
| Clinical sensitivity | <0.5% effects | ~1.9% effects, all d>2.1 vs C4 |

### Interpretation

The graded game confirms that the precision modulation channel was structurally inert in the binary game due to softmax saturation, and is now active (q_pi_entropy ~5.8 vs <0.01). Both terminal value mechanisms (precision tracking and reward averaging) provide substantial augmentation over base planning.

The unexpected result is that C5 (reward averaging) consistently outperforms C2 (precision tracking), including in the betrayal scenario where precision tracking was expected to shine. This suggests that in the current architecture, direct reward encoding provides more focused guidance than precision-weighted terminal values.

The paper story becomes:
1. **Binary game**: affect provides orthogonal augmentation beyond planning depth (H1, H2 strong; H3 context-dependent)
2. **Graded game**: the ambiguous action space activates the terminal value channel; both mechanisms help, but simple reward averaging is more effective than precision tracking
3. **Clinical differentiation**: the graded game enables measurable behavioral differences for clinical parameter variations, which the binary game could not produce

The precision tracking mechanism's advantage is *modelability* — its parameters map naturally to clinical constructs (alexithymia, borderline, depression) in ways that simple reward averaging does not. The performance advantage, however, lies with C5.

## Phase 6: Bayesian Model Comparison

### Approach

Each agent condition is treated as a generative model. Per-round log-evidence is computed as `log p(partner_action | agent's predictive distribution)`. Cumulative log-evidence across all rounds gives the total model evidence per seed. Pairwise Bayes factors and random-effects BMS (Stephan et al., 2009) with protected exceedance probabilities (Rigoux et al., 2014) are used for formal comparison.

### Default Condition (50 seeds × 200 rounds × 5 conditions)

| Condition | Mean log-evidence | SE |
|---|---|---|
| C1 deep_no_affect | -117.69 | 1.55 |
| C2 affective_shallow | -115.89 | 1.56 |
| C3 lesioned_shallow | -117.55 | 1.56 |
| C4 shallow_no_affect | -117.55 | 1.56 |
| C5 reward_avg_shallow | -115.62 | 1.53 |

**Pairwise Bayes factors (log10 scale):**

| Comparison | log10 BF | Interpretation |
|---|---|---|
| C2 vs C1 | +0.78 | substantial, favors C2 |
| C5 vs C1 | +0.90 | substantial, favors C5 |
| C2 vs C4 | +0.72 | substantial, favors C2 |
| C5 vs C4 | +0.84 | substantial, favors C5 |
| C2 vs C5 | -0.12 | negligible |
| C3 vs C4 | 0.00 | identical |

**RFX-BMS:** C5 wins decisively — expected frequency 0.623, protected exceedance probability **1.000**. C2 second at 0.177. BOR ≈ 0. The data strongly discriminate: affect-augmented models (C2 and C5) are better predictors of the environment than non-affect models, and at the population level C5 is the most frequent best model.

### Betrayal Stress Condition (50 seeds × 120 rounds × 4 conditions)

| Condition | Mean log-evidence | SE |
|---|---|---|
| C1 deep_no_affect | -63.91 | 1.33 |
| C2 affective_shallow | -57.01 | 2.04 |
| C3 lesioned_shallow | -62.80 | 1.04 |
| C5 reward_avg_shallow | -63.23 | 2.24 |

**Pairwise Bayes factors (log10 scale):**

| Comparison | log10 BF | Interpretation |
|---|---|---|
| C2 vs C1 | +3.00 | **decisive**, favors C2 |
| C2 vs C3 | +2.51 | **decisive**, favors C2 |
| C2 vs C5 | +2.70 | **decisive**, favors C2 |
| C1 vs C3 | -0.48 | negligible |
| C1 vs C5 | -0.30 | negligible |
| C3 vs C5 | +0.18 | negligible |

**RFX-BMS:** C2 wins decisively — expected frequency 0.566, protected exceedance probability **0.998**. BOR ≈ 0. Under betrayal stress, the affective model is overwhelmingly the best predictor of partner behavior.

### Interpretation

The Bayesian model comparison adds a qualitatively new layer to the existing frequentist results:

1. **Default condition:** Both affect-augmented models (C2, C5) are substantially better predictors than non-affect models, confirming H1 with Bayesian evidence. C5 slightly edges C2 at the population level, consistent with the frequentist finding that reward averaging performs as well or slightly better in the default task.

2. **Betrayal condition:** This is the strongest finding. C2 (precision tracking) is **decisively** the best predictive model — not just higher payoff, but fundamentally better at predicting what partners will do. The log10 BF of 3.0 against C1 and 2.7 against C5 are far above the "decisive" threshold. This means:
   - Precision tracking produces systematically better partner predictions under volatility
   - The affective signal is not just a terminal value hack that improves action selection — it genuinely improves the agent's world model
   - Reward averaging (C5) provides no predictive advantage over non-affect models under betrayal, despite performing better on payoff. This dissociation between predictive accuracy and payoff suggests C5's payoff advantage comes from action selection, not from better environmental modeling

3. **The modelability argument is strengthened.** Not only does precision tracking have interpretable clinical parameters, it also produces the best generative model of volatile social environments. C5 may win on payoff in stable conditions, but C2 wins on model quality when it matters most — under betrayal stress.

### Updated Hypothesis Scorecard (Bayesian)

| Hypothesis | Frequentist | Bayesian model comparison |
|---|---|---|
| H1 affect > non-affect | d=0.64, p<0.001 | Substantial BF (default), decisive BF (betrayal) |
| H2 lesion dissociation | C3=C4 | C3=C4 (identical log-evidence, BF=1.00) |
| H3 precision > reward avg | Task-dependent | C5 ≈ C2 in default; C2 **decisively** > C5 in betrayal (log10 BF=2.70) |
| H4 post-switch robustness | C2 > C1 post-switch | C2 best predictor overall in betrayal (log10 BF=3.00 vs C1) |

## Phase 7: Cross-Game Generalization

### Design

Three 2×2 symmetric games tested with zero code changes (payoff matrix is configurable):

| Game | Mutual Coop | Sucker | Temptation | Mutual Defect | Strategic character |
|---|---|---|---|---|---|
| Prisoner's Dilemma | (3,3) | (-1,5) | (5,-1) | (1,1) | Defection-dominated |
| Stag Hunt | (5,5) | (0,2) | (2,0) | (2,2) | Coordination game |
| Chicken | (3,3) | (1,5) | (5,1) | (0,0) | Anti-coordination |

Each game run with 50 seeds in both default (random assignment, p_switch=0.05) and betrayal stress (agent_choice, scheduled cooperator→exploiter switch at round 31).

### Default Condition Results (50 seeds × 200 rounds)

| Game | C1 (deep) | C2 (affect) | C3 (lesion) | C4 (shallow) | C5 (reward) | H1 d | H1 p |
|---|---|---|---|---|---|---|---|
| PD | 526.2 | 574.8 | 575.5¹ | 575.5¹ | 575.5 | 0.62 | 0.003 |
| Stag Hunt | 607.5 | 639.8 | 605.4 | 605.4 | 640.3 | 0.50 | 0.015 |
| Chicken | 510.5 | 513.8 | 511.5 | 511.5 | 514.7 | 0.05 | 0.795 |

¹ C3=C4 holds exactly across all three games.

**Key finding 1:** Affect augmentation (H1) generalizes to Stag Hunt (d=0.50, p=0.015) but is negligible in Chicken (d=0.05, p=0.795). The coordination structure of the Stag Hunt rewards accurate partner prediction; the anti-coordination structure of Chicken does not.

**RFX-BMS (default):**

| Game | Winner | Expected freq | Exceedance |
|---|---|---|---|
| PD | C5 | 0.623 | 1.000 |
| Stag Hunt | C2 | 0.566 | 0.992 |
| Chicken | C2 | 0.381 | 0.710 |

**Key finding 2:** In the Stag Hunt, C2 (precision tracking) wins RFX-BMS decisively — the ONLY default condition where precision tracking is the best predictive model. This makes theoretical sense: the Stag Hunt penalizes miscoordination severely (sucker=0), so accurate partner prediction (which precision tracking provides) is more valuable than simple reward tracking.

### Betrayal Stress Results (50 seeds × 120 rounds)

| Game | C1 (deep) | C2 (affect) | C3 (lesion) | C5 (reward) | H1 d | H1 p | C2 vs C5 d | C2 vs C5 p |
|---|---|---|---|---|---|---|---|---|
| PD | 399.8 | 481.9 | 419.4 | 428.3 | 1.30 | <0.001 | 0.59 | 0.004 |
| Stag Hunt | 421.9 | 489.7 | 402.7 | 466.1 | 1.60 | <0.001 | 0.39 | 0.057 |
| Chicken | 378.1 | 448.2 | 390.9 | 414.6 | 1.12 | <0.001 | 0.38 | 0.062 |

**Key finding 3:** Affect augmentation under betrayal is **strong across ALL three game types** (d > 1.0 everywhere). This is the main generalization result: when partners become unreliable, affect provides robust augmentation regardless of game structure.

**Key finding 4:** C2 outperforms C5 in all three betrayal conditions, though the advantage is strongest in PD (d=0.59, significant) and marginal in Stag Hunt and Chicken (d≈0.38, p≈0.06).

**RFX-BMS (betrayal):**

| Game | Winner | Expected freq | Exceedance | C2 vs C5 log10 BF |
|---|---|---|---|---|
| PD | C2 | 0.566 | 0.998 | +2.70 (decisive) |
| Stag Hunt | C2 | 0.565 | 0.954 | +1.08 (strong) |
| Chicken | C5 | 0.511 | 0.931 | -1.07 (strong, favors C5) |

**Key finding 5:** The C2 vs C5 competition is game-dependent under betrayal:
- PD: C2 wins decisively (precision tracking best for detecting betrayal in defection-dominated games)
- Stag Hunt: C2 wins strongly (precision helps detect coordination failures)
- Chicken: C5 wins strongly (reward averaging better for anti-coordination under volatility)

### Interpretation

The cross-game analysis reveals a richer picture than any single game could provide:

1. **Affect augmentation generalizes broadly under volatility.** H1 (d > 1.0) holds across PD, Stag Hunt, and Chicken in betrayal conditions. This is not a trust-game-specific result.

2. **Affect augmentation is game-dependent in stable conditions.** Strong in PD and Stag Hunt (d=0.5-0.6), negligible in Chicken (d=0.05). Games where cooperation requires trust (PD, Stag Hunt) benefit from precision tracking; games where anti-coordination dominates (Chicken) do not.

3. **The C2 vs C5 winner depends on game structure.** Precision tracking excels in games with severe miscoordination penalties (PD, Stag Hunt). Reward averaging excels in games where the reward gradient is more directly informative (Chicken). This is consistent with the theoretical prediction: precision tracking helps when *prediction accuracy* matters more than *reward history*.

4. **The Stag Hunt is the strongest game for precision tracking.** It is the only game where C2 wins RFX-BMS in BOTH default and betrayal conditions. The high cost of miscoordination (sucker=0 vs mutual defect=2) makes partner prediction accuracy the critical factor.

5. **C3=C4 invariant holds universally.** The lesion correctly decouples affect from decisions across all game types, confirming the implementation.

### Updated Cross-Game Hypothesis Scorecard

| Hypothesis | PD | Stag Hunt | Chicken |
|---|---|---|---|
| H1 augmentation (default) | d=0.62, p=0.003 | d=0.50, p=0.015 | d=0.05, p=0.795 |
| H1 augmentation (betrayal) | d=1.30, p<0.001 | d=1.60, p<0.001 | d=1.12, p<0.001 |
| H2 C3=C4 | Yes | Yes | Yes |
| H3 C2 vs C5 (default) | C2≈C5 | C2≈C5 | C2≈C5 |
| H3 C2 vs C5 (betrayal) | C2>C5 (d=0.59) | C2>C5 (d=0.39) | C5>C2 (d=-0.38) |
| RFX-BMS default | C5 wins | **C2 wins** | C2 wins (weak) |
| RFX-BMS betrayal | **C2 wins** | **C2 wins** | C5 wins |

## Execution Record Template

When the user asks to refresh this file after a run, append:

- date
- config name
- command used
- output directory
- derived `mu`
- short read on H1-H5
- whether the recommended next step changed
