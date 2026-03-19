# Experimentation Plan: Affect as Computational Infrastructure for Social Inference

## Testing Per-Partner Affective Precision in Multi-Agent Active Inference

---

## 1. Overview

This document specifies the experimental design for testing the central claim: per-partner metacognitive precision tracking provides an orthogonal augmentation to active inference policy evaluation — one that improves social decision-making in ways that increasing planning depth alone does not recover. Under sophisticated inference with binary actions, non-affective planners from horizon 2 through horizon 8 are statistically indistinguishable, yet adding a per-partner affective signal yields a measurable benefit at every depth. Ablating this signal reproduces the behavioral signature of vmPFC damage — intact social knowledge with impaired social decision-making.

---

## 2. POMDP Structure

### 2.1 State Space Factorization

The generative model factorizes hidden states into three hierarchical levels per partner $k$:

**Level 1 — Trial State** $s^{(1)}_t$
The current-round game state, including:
- Partner $k$'s action on this trial: {Cooperate, Defect}
- Context: {which partner is currently interacting}

This is directly observed (or noisily observed, depending on the variant — see Section 3.3).

**Level 2 — Partner Type** $s^{(2)}_k$
Each partner's latent strategy type, drawn from:
- **Cooperator**: cooperates with probability 0.9
- **Reciprocator**: mirrors the agent's previous action with probability 0.85
- **Exploiter**: cooperates initially (first 3-5 rounds) then defects with probability 0.85
- **Random**: cooperates with probability 0.5

Types are stable within blocks but switch at geometrically-distributed intervals (expected block length ~20 rounds). The agent does not observe type switches directly.

**Level 3 — Affective State** $\beta_k$ (for affective agents only)
A continuous-valued state per partner, bounded in $[0, 1]$, representing the agent's running estimate of social model precision for partner $k$. Initialized at $\beta_k = 0.5$ (neutral).

### 2.2 Observation Model (A matrix)

Observations consist of:
- **Partner action**: Cooperate or Defect (observed directly)
- **Own payoff**: determined by the game payoff matrix (observed directly)

For the basic version, observations are noise-free — the agent sees exactly what the partner did. A later variant can add observational noise (misreading partner actions) to test whether affective precision also aids robustness to sensory uncertainty.

The A matrix maps hidden states (partner type × context) to observations (partner action × payoff):

$$P(o_t | s^{(1)}_t, s^{(2)}_k) = \text{determined by type-specific cooperation probabilities}$$

### 2.3 Transition Model (B matrix)

**Level 1 transitions**: depend on the agent's action and partner's type.

**Level 2 transitions**: partner types are mostly stable (identity transition with probability 0.95) but switch with probability 0.05 per trial to a uniformly random new type. This creates the volatility that makes the task nontrivial.

$$P(s^{(2)}_{k,t+1} | s^{(2)}_{k,t}) = (1 - p_{\text{switch}}) \cdot \mathbb{I}[s' = s] + p_{\text{switch}} \cdot \text{Uniform}(S^{(2)})$$

Important implementation note: this stochastic type switching is separate from the exploiter's internal `switch_round`. `p_switch` governs when a partner changes latent type altogether; `switch_round` only governs when an **exploiter-type** partner changes from its early cooperative phase to its later exploitative phase after repeated interactions.

**Level 3 transitions (affective state)**: governed by the exponential moving average update described in the theory document. Not a standard discrete POMDP transition — implemented as a continuous auxiliary variable updated outside the core POMDP loop (see Section 2.6).

### 2.4 Preference Model (C matrix)

The agent has prior preferences over observations defined by the payoff matrix of a Trust Game variant:

|  | Partner Cooperates | Partner Defects |
|---|---|---|
| **Agent Cooperates** | +3 / +3 (mutual cooperation) | -1 / +5 (sucker's payoff) |
| **Agent Defects** | +5 / -1 (temptation) | +1 / +1 (mutual defection) |

Prior preferences are specified as a log-probability vector over observations:

$$\ln P(o) \propto \text{payoff}(o)$$

This creates the standard tension: mutual cooperation is collectively optimal but unilateral cooperation is individually risky. The agent prefers high payoffs, so cooperation is preferred *when the partner is expected to cooperate* and defection is preferred otherwise.

### 2.5 Policy Space and Planning Horizon

**Actions**: {Cooperate, Defect} per round, for each partner interaction.

**Planning horizon**: varies by condition (this is the key manipulation).
- Deep planner: $T = 8$ steps ahead
- Shallow planner: $\tau = 2$ steps ahead

**Policy evaluation**: standard expected free energy computation over the planning horizon, using sophisticated inference rather than a mean-field rollout. For each policy, the planner enumerates all future binary partner-action observation sequences, updates partner-type beliefs after each hypothetical observation via Bayes rule, and averages the pathwise EFE under the corresponding path probabilities. For affective agents, the shallow-horizon EFE is then precision-weighted by the current partner-specific signal. This is now the implemented planning method for all conditions, so horizon comparisons isolate explicit depth rather than mixing depth with different rollout approximations.

### 2.6 Affective State Update (Level 3 Implementation)

After each trial with partner $k$, the affective state is updated:

```
# After observing partner k's action at time t:
prediction = E[o_t | current posterior over s^(2)_k]
actual = o_t
surprise_k = 1 - prediction[actual]               # unsigned surprise of what happened
sq_surprise = surprise_k^2

# Affective charge: positive if model is accurate, negative if not
charge = alpha * (sigma_0^2 - sq_surprise)

# Exponential moving average update
beta_k = lambda * beta_k + (1 - lambda) * sigmoid(charge)
```

Parameters:
- $\lambda = 0.6$ — smoothing parameter; slower than belief updates but responsive within 5-10 interactions
- $\alpha = 3.0$ — charge sensitivity; expands the sigmoid operating range so correct vs. incorrect predictions separate betas materially
- $\sigma_0^2$ — baseline expected squared surprise; default `0.25` matches a random binary partner because $(1 - 0.5)^2 = 0.25$
- sigmoid clamps the charge contribution to $[0, 1]$

The affective precision weight is then:

```
precision_weight_k = 1 + mu * beta_k
G_shallow(pi) = sum_t G_t(pi) * precision_weight_k
```

Where $\mu$ scales the influence of affect on policy selection. The weight is keyed to the first partner implicated by the policy so the affective signal changes first-action marginals rather than washing out at the end of the rollout. For full experiment runs, `mu` calibration should average over at least `10` deep-planner episodes; shorter calibrations are acceptable only for smoke tests and fast debugging.

---

## 3. Environment and Task

### 3.1 Multi-Partner Trust Game

The agent interacts with $K = 4$ partners over $N = 200$ rounds. Each round:

1. A partner is selected (either randomly assigned or agent-chosen — see Variant 3.4)
2. The agent and partner choose Cooperate or Defect (the implementation evaluates the agent's action first inside the simulation loop, but because both actions are resolved against the same round payoff matrix with no within-round reaction term, this is strategically equivalent to simultaneous choice)
3. Payoffs are determined by the Trust Game matrix
4. The agent observes the partner's action and updates beliefs

Partners' hidden types switch according to the geometric distribution ($p_{\text{switch}} = 0.05$ per trial). The agent must learn partner types, track changes, and choose actions to maximize cumulative payoff.

### 3.2 Why This Task

This task is chosen to satisfy several requirements:

- **Multi-partner**: forces the agent to maintain separate models (and potentially separate affective states) for each partner, stressing computational resources.
- **Sequential and volatile**: partner types change, so the agent must continuously update rather than converging to a fixed strategy. This is where partner-specific confidence signals and post-switch adaptation should matter most.
- **Social structure**: the Trust Game payoff matrix creates a genuine social dilemma where understanding partner types is essential for good decisions.
- **Minimal**: 2 actions, 4 partner types, 4 partners — small enough for exact or near-exact POMDP solutions at depth 8, providing a gold-standard deep planner to compare against.

### 3.3 Task Variants

**Variant A: Fixed partner assignment (baseline)**
Each round, the partner is randomly assigned. The agent has no choice over who to interact with — only what action to take. This isolates the cooperate/defect decision from partner selection.

**Variant B: Partner selection**
Each round, the agent chooses which of the 4 partners to interact with, then chooses cooperate/defect. This adds a second action dimension and tests whether affective states also guide partner selection (approach trustworthy partners, avoid or probe untrustworthy ones). Partner selection is where affect should have the strongest effect — choosing who to engage with is a higher-level decision that benefits most from compressed interaction summaries.

**Variant C: Noisy observations**
Partner actions are observed with 10% noise (cooperation misread as defection and vice versa). This tests whether affective inertia provides robustness to observational noise — the slow affective state should smooth over misperceptions that would destabilize a fast belief-only system.

**Variant D: Correlated partners (for structure learning extension)**
Two of the four partners are secretly correlated — partner C copies partner B's action with 90% probability. This tests whether affective signals can detect structural relationships: the agent should notice that its model of C is suspiciously well-predicted by its model of B, signaling coalition structure. This variant connects to the BMR/structure learning direction.

**Variant E: Betrayal stress test**
Use agent-chosen partners, disable stochastic type switches (`p_switch = 0`), seed a clearly cooperative partner at the start of the episode, then force a scheduled switch from `cooperator` to `exploiter` mid-episode. The key readout is payoff, action choice, and inferred-type accuracy in the first 5-10 encounters after the betrayal event. This is the cleanest way to separate precision tracking from reward averaging, because the partner's past reward history remains attractive while the predictive model becomes sharply wrong.
The repository now treats this as the primary diagnostic benchmark for condition comparison because it is the most direct test of whether per-partner beta dynamics do computational work beyond cached value.

---

## 4. Experimental Conditions

### 4.1 Condition 1: Deep Planner, No Affect (Gold Standard)

- Planning horizon: $T = 8$
- Level 3 (affective state): absent
- Policy selection: full EFE computation over 8-step horizon
- Purpose: establishes the performance ceiling — the best the agent can do with unlimited computation. All other conditions are compared against this.

### 4.2 Condition 2: Affective Agent, Shallow Planner (Target)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): active, per-partner, updated on slow timescale
- Beta implementation: continuous EMA by default; config can instead select a discrete variational beta state
- Policy selection: EFE over 2-step horizon, precision-weighted by the first partner's affective signal
- Precision modulation: off by default in the primary experiments (`affect_modulates_precision=False`), so Condition 2 tests shallow-EFE weighting rather than per-partner $\gamma_k$ modulation
- Purpose: tests the core hypothesis — does per-partner metacognitive precision tracking provide orthogonal value that planning depth alone does not recover? Under sophisticated inference the non-affective depth curve is flat, so the comparison is not "shallow + affect vs. deep" but "affect vs. no-affect at any depth."

### 4.3 Condition 3: Lesioned Affective Agent (vmPFC Analog)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): present in architecture but **decoupled** from policy selection
  - Option 3a: $\beta_k$ fixed at 0.5 (neutral) for all partners, all time
  - Option 3b: $\beta_k$ updates normally but $\mu = 0$ (affect doesn't weight EFE)
- Level 2 (social model): fully intact, updates normally
- Policy selection: EFE over 2-step horizon, no affective weighting
- Purpose: reproduces the Damasio pattern — the agent can correctly identify partner types (inspect level-2 posteriors) but cannot efficiently use this knowledge for decision-making.

Both lesion variants (3a, 3b) should be tested. 3b is the cleaner analog — the agent "feels" things but feelings don't influence decisions, modeling the vmPFC disconnection from action selection rather than destruction of the representation itself.

### 4.4 Condition 4: Shallow Planner, No Affect (Minimal Baseline)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): absent
- Policy selection: EFE over 2-step horizon only
- Purpose: confirms that shallow planning alone (without affect) genuinely fails, establishing that it is affect specifically (not just additional computation of any kind) doing the work.

### 4.5 Condition 5: Reward-Average Agent (Value Function Control)

- Planning horizon: $\tau = 2$
- Instead of precision-based affect: a simple exponential moving average of reward per partner, used as the shallow-EFE weight
- $\bar{R}_k^{(t+1)} = \lambda \bar{R}_k^{(t)} + (1 - \lambda) \cdot r_t$
- Terminal signal: $\tilde{R}_k = 0.5 \cdot (1 + \tanh(\bar{R}_k / \max |r|))$
- Weighted objective: $G(\pi) \approx \left(\sum_{t=1}^{\tau} G_t(\pi)\right) \cdot \left(1 + \mu \tilde{R}_k\right)$
- Purpose: distinguishes the precision-tracking account from a simpler "cached value" account. If Condition 2 outperforms Condition 5, it demonstrates that tracking model precision provides information that reward averaging does not (the uncertainty preservation argument).

### 4.6 Condition 6: Intermediate Planner, No Affect ($\tau = 3$)

- Planning horizon: $3$
- Level 3 (affective state): absent
- Policy selection: sophisticated-inference EFE over 3-step horizon
- Purpose: fills in the explicit-depth curve between Conditions 4 and 1.

### 4.7 Condition 7: Intermediate Planner, No Affect ($\tau = 4$)

- Planning horizon: $4$
- Level 3 (affective state): absent
- Policy selection: sophisticated-inference EFE over 4-step horizon
- Purpose: tests whether the affective shallow agent matches one or two extra steps of explicit lookahead.

### 4.8 Condition 8: Deep Planner With Affect

- Planning horizon: $T = 8$
- Level 3 (affective state): active
- Policy selection: sophisticated-inference EFE over 8-step horizon, weighted by the first partner's affective signal
- Purpose: tests whether affect adds anything once explicit planning is already deep.

### 4.9 Condition 12: Variational Affective Agent

- Planning horizon: $\tau = 2$
- Level 3 (affective state): active, per-partner, represented as a discrete variational posterior over beta levels
- Policy selection: same shallow EFE weighting as Condition 2
- Purpose: isolates the effect of switching from the default continuous beta update to the discrete variational beta formulation.

---

## 5. Hypotheses and Predictions

### Hypothesis 1: Affect Provides Orthogonal Augmentation Beyond Planning Depth

**Prediction**: Condition 2 (affective, shallow) outperforms every non-affective planner, including Conditions 1, 4, 6, and 7, while using much less explicit computation than the deep planner.

**Metrics**:
- Cumulative payoff over 200 rounds (primary)
- Number of policy-tree nodes expanded per decision (secondary/supplementary)
- Per-round decision time (wall clock, if relevant)

**Expected outcome**: Under sophisticated inference, the explicit-depth curve among non-affective agents is flat in this binary-action trust game, so Condition 2 should beat the whole no-affect family rather than merely matching Condition 1. The result is best understood as orthogonal augmentation: affect adds a partner-specific evaluation signal that depth alone does not recover, rather than approximating deeper lookahead.

**Failure mode**: If Conditions 1, 4, 6, and 7 form a rising depth-performance curve and Condition 2 only matches the shallow baseline, then the affective weighting is not adding information beyond explicit lookahead. That would push the interpretation back toward a standard planning-depth story.

### Hypothesis 2: Lesion Reproduces Damasio Pattern

**Prediction**: Condition 3 (lesioned) shows:
- Level-2 posteriors correctly identify partner types (comparable accuracy to Condition 1)
- Behavioral performance is significantly worse than Condition 2 (and comparable to Condition 4)
- The deficit is largest during volatile periods (after partner type switches)

**Metrics**:
- Partner type identification accuracy (inspecting argmax of level-2 posterior)
- Cumulative payoff (should be near Condition 4 level)
- Performance gap between stable periods and post-switch periods

**Expected outcome**: Lesioned agents "know" partner types but "can't use" that knowledge. During stable periods (types not switching), the lesion effect is moderate — shallow planning is adequate when nothing changes. During volatile periods, the lesion effect is large — without affective inertia to buffer noise and without affective weighting to extend shallow evaluation, the agent makes myopic, exploitable decisions.

**Failure mode**: If the lesioned agent performs as well as Condition 2, then affect isn't doing computational work — the architecture itself (having a level-3 state, even decoupled) provides some benefit, or the task is too easy for 2-step planning alone.

### Hypothesis 3: Precision Tracking Outperforms Reward Averaging (Boundary-Condition Result)

This is now understood as a boundary-condition result rather than a universal separation. When planning depth is equalized under sophisticated inference, affect still provides measurable benefit — but the precision-vs-reward-average distinction surfaces only in environments that create a genuine dissociation between recent reward and current predictive reliability.

**Prediction**: Condition 2 (precision-based affect) outperforms Condition 5 (reward-average weighting) specifically in scenarios where prediction error and reward dissociate:
- Betrayal-style environments (scheduled cooperator→exploiter switch)
- Volatile periods immediately following type switches
- Mixed partner populations where some partners are predictable and others aren't

In default random-assignment tasks, Condition 2 and Condition 5 may remain effectively tied because prediction accuracy and reward history stay closely aligned.

**Metrics**:
- Cumulative payoff (overall and broken down by partner type)
- Performance in the first 10 rounds after a partner type switch (where uncertainty information is most valuable)
- Exploitation rate by Exploiter-type partners
- In the betrayal stress test, performance in the first 5-10 encounters after the forced cooperator→exploiter switch

**Expected outcome**: Context-dependent. In the default task, the two conditions remain tied (null boundary condition). In the betrayal-stress task, the reward-average agent is exploited more by the forced cooperator→exploiter switch because it confuses attractive recent reward with current reliability, whereas the precision-based agent reacts to the spike in surprise (positive mechanism test).
Operationally, inspect `betrayal_post_switch_window_1_5.csv`, `betrayal_post_switch_window_1_10.csv`, and `betrayal_condition_comparison.csv`. A successful mechanism result means Condition 2 beats Condition 5 on post-switch payoff and/or accuracy while `affective_movement_summary.csv` shows non-flat beta and terminal-signal ranges. If both the comparison tables and movement summary are flat, interpret the outcome as a null mechanism result rather than a broken analysis pipeline.

**Failure mode**: If Conditions 2 and 5 perform comparably even in betrayal stress, then the simpler reward-average account is sufficient in the shipped environment family. That would weaken the precision-specific claim while leaving the broader affect-versus-no-affect result intact.

### Hypothesis 4: Affective Inertia Provides Noise Robustness

**Prediction**: Condition 2 is more robust to single-trial noise (partner occasionally deviates from type by 1 trial) but slower to detect genuine type switches (sustained deviation) compared to Condition 1.

**Metrics**:
- False alarm rate: how often the agent changes strategy toward a partner after a single noisy trial
- Detection latency: how many trials after a genuine type switch before the agent's behavior changes
- Payoff during noisy vs. stable stretches

**Expected outcome**: Condition 1 (deep planner) detects type switches fastest but also has more false alarms during noisy stretches. Condition 2 (affective) has fewer false alarms (affective inertia smooths over noise) but slightly slower detection (the slow timescale acts as a low-pass filter). The net effect is positive because in realistic social environments, noise frequency far exceeds signal (type switch) frequency.

**Failure mode**: If Condition 2 is both slower to detect and no more robust to noise, then the slow timescale is a pure cost. This would suggest $\lambda$ is too high and the smoothing parameter needs recalibration.

### Hypothesis 5: Affect Enables Adaptive Partner Selection (Variant B only)

**Prediction**: In Variant B (agent chooses which partner to interact with), Condition 2 shows more adaptive partner selection than Conditions 3, 4, and 5:
- Preferentially selects high-precision partners (where model is reliable, regardless of type)
- Probes low-precision partners epistemically (interacts to reduce uncertainty, then either commits or avoids)
- Rapidly shifts away from partners whose precision drops (type switch detected through affect)

**Metrics**:
- Partner selection entropy (how evenly the agent distributes interactions)
- Correlation between affective precision $\beta_k$ and selection frequency
- Payoff-per-interaction for selected vs. available partners

**Expected outcome**: Affective agents develop clear partner preferences early and update them after type switches. Non-affective agents either exploit myopically (Condition 4) or distribute interactions more evenly (Condition 1 can reason about information value but at high computational cost).

### Hypothesis 6 (FUTURE/PROPOSED): Bayesian Model Comparison of Affective vs. Non-Affective Generative Models

**Status: Proposed, requires Phase 4 (variational beta) and Phase 6 (model comparison).**

**Prediction**: Formal model evidence (marginal likelihood) favors the affective generative model over the non-affective generative model, providing a principled basis for preferring the affect-augmented architecture beyond point-estimate performance metrics.

**Metrics**:
- Log model evidence (marginal likelihood) for affective vs. non-affective generative models
- Bayes factor across task variants

**Conceptual issues**: This hypothesis requires Phase 4 (variational beta — formalizing the current EMA-based precision update as a discrete hidden state with explicit likelihood) before the model evidence computation is cleanly defined. The current trigger-based BMR approach (Section 8.2) is NOT suitable for this comparison because it conflates structure learning with model selection. A clean Bayesian model comparison must treat the affective and non-affective models as competing generative models evaluated on the same observation sequences, without using affect-triggered structural changes as part of the evidence calculation.

**Failure mode**: If the non-affective model has comparable or higher evidence despite worse behavioral performance, this would suggest the affective signal improves decisions through a mechanism that is not well-captured by the current generative model formulation — pointing toward the need for a tighter variational treatment of beta.

### Hypothesis 7 (PRELIMINARY): Clinical Parameter Sensitivity Analysis

**Status: Preliminary results available. The failure mode has been realized — parameter variations produce indistinguishable behavioral profiles in the current trust game, due to the task's unambiguous EFE landscape rather than a deficiency in the parameter space itself.**

**Original prediction**: Specific parameter configurations produce predictable behavioral signatures that qualitatively match known clinical profiles:
- **Alexithymia** ($\alpha \to 0$): attenuated affective charge leads to near-flat beta trajectories, reducing the agent to effectively non-affective behavior (performance approaches Condition 4)
- **Borderline patterns** (high $\alpha$ + low $\lambda$): intense, volatile affective states produce erratic partner-specific precision weights, leading to unstable cooperation patterns and high behavioral variance
- **Depression** (low $\beta_0$): chronically low precision estimates reduce engagement and bias toward defection even with cooperative partners

**Empirical result**: The beta dynamics differentiate as predicted — alexithymia freezes beta, borderline creates wide swings, depression starts low and recovers. However, none of these dynamical differences translate into measurable behavioral deficits relative to the default affective agent (Condition 2). Across four experimental designs (current params, precision modulation, short 50-round horizon, extreme params) and both precision channels (terminal values only, terminal values + gamma scaling), the maximum clinical effect is 3.0 points out of 576 total payoff (0.5%). Only 2 of 18 comparisons reach nominal p<0.05, neither survives correction for multiple comparisons, and both have Cohen's d < 0.05.

**Root cause**: The trust game's EFE landscape is too unambiguous. The median gap between the best and second-best policy is 10.83, making the softmax effectively a hard argmax. Whether beta is 0.14 or 0.94, the same policy wins. The affective mechanism provides a binary augmentation (have mu-weighted terminal values vs. don't) rather than a graded one. Within the "affect ON" regime, the parameter space is behaviorally degenerate in this task.

**Metrics** (confirmed):
- Beta trajectory statistics do differentiate: alexithymia σ=0.001, borderline σ=0.113, depression σ=0.062
- Cumulative payoff does NOT differentiate: all clinical variants within 0.5% of default C2
- Behavioral signature match: dynamics are qualitatively correct but don't translate to behavioral output

**Revised interpretation**: The parameter space has the right structure (clinically meaningful dynamical regimes exist), but the current task environment doesn't amplify these differences into behavioral consequences. This is a task-specificity limitation, not a model limitation. Clinical sensitivity analysis should be revisited in Phase 7 (richer tasks) with environments that have more ambiguous EFE landscapes — larger action spaces, partial observability, or multiple equilibria where precision differences can flip policy selection.

**Failure mode (realized)**: Parameter variations produce indistinguishable behavioral profiles. The model's parameter space lacks clinical resolution *in this task*. The question for future work is whether richer environments unlock the resolution the parameter space structurally supports.

---

## 6. Implementation Plan

### 6.1 Framework

Primary implementation is a custom **JAX-first** active inference stack in this repository. Generic active inference math and control live under `affect_aif/core`, trust-game-specific matrices and payoffs live under `affect_aif/generative_model`, and the affective state (level 3) is implemented as an auxiliary per-partner summary outside the core belief update loop, modulating policy evaluation through shallow-EFE weighting.

Reference implementation: Hesp et al.'s "Deeply Felt Affect" code (https://github.com/CasperHesp/deeplyfeltaffect) for the single-agent affective architecture. This will be extended to the multi-partner setting.

### 6.2 Simulation Parameters

| Parameter | Value | Justification |
|---|---|---|
| Partners ($K$) | 4 | Large enough for meaningful partner selection, small enough for tractable computation |
| Rounds ($N$) | 200 | Long enough for multiple type switches and learning |
| Type switch probability ($p_{\text{switch}}$) | 0.05/trial | Expected block length ~20 rounds |
| Partner types | 4 (Cooperator, Reciprocator, Exploiter, Random) | Covers key strategic diversity |
| Deep planning horizon ($T$) | 8 | Sufficient for ~optimal play in this game |
| Shallow planning horizon ($\tau$) | 2 | Minimal deliberation |
| Intermediate planning horizons | 3, 4 | Additional depth-comparison points for Conditions 6 and 7 |
| Affective smoothing ($\lambda$) | 0.6 | Slower than belief updates while still moving over 5-10 interactions |
| Affective scaling ($\mu$) | Derived from deep-planner mean absolute EFE per step | Calibrated from the explicit planning mass omitted by the shallow horizon, rather than tuned by grid search |
| Replications per condition | 100 | Sufficient for reliable statistics |

### 6.3 Analysis Plan

**Primary analysis**: mixed-effects ANOVA on cumulative payoff with Condition as fixed factor and replication as random factor. Post-hoc pairwise comparisons with Bonferroni correction.

**Secondary analyses**:
- Knowledge vs. behavior dissociation (Condition 3): correlation between level-2 posterior accuracy and behavioral optimality, plotted over time
- Precision vs. reward-average (Conditions 2 vs. 5): interaction analysis of condition × partner-type on per-partner payoff
- Noise robustness (Hypothesis 4): segmented analysis of performance in stable vs. post-switch windows
- Sensitivity analysis: sweep over $\lambda$ (0.7-0.99), $\mu$ (0.5-5.0), $p_{\text{switch}}$ (0.01-0.1) to characterize robustness of results to parameter choices

**Supplementary analyses**:
- Computational cost comparison (Conditions 1 vs. 2): paired t-test on nodes-expanded-per-decision. Under sophisticated inference the depth curve is flat in the current binary-action task, so cost differences between depths are less interpretively central than the affect/no-affect comparison. Retained for completeness but no longer a primary or secondary analysis.

**Execution workflow note**:
- `scripts/run_experiment.py` accepts repeated `--config` flags and a shared `--workers` pool so multiple experiment configs can be queued in one invocation.
- Outputs are written per config under `<output-dir>/<batch-id>/<config-name>/results.csv`, which keeps each experiment variant isolated while still allowing the scheduler to share workers across all queued replications.
- `affect_aif/configs/horizon_sweep.json` is the reference config for Conditions 1, 2, 4, 6, and 7; analysis now emits a horizon-sweep figure so the affective shallow condition can be read directly against explicit depth.
- `affect_aif/configs/deep_affect_test.json` is the completed Conditions 1, 2, and 8 comparison; it isolates whether affect adds anything once explicit planning is already deep and supports the orthogonal-augmentation interpretation because `C2` and `C8` are statistically indistinguishable.

### 6.4 Visualizations

Key figures for the paper:

1. **Cumulative payoff curves** (all 5 conditions, averaged over 100 replications with confidence bands)
2. **Affective state trajectories** for Condition 2: $\beta_k$ over time for each partner, with partner type switches marked as vertical lines. Should show slow tracking with inertial response to switches.
3. **Knowledge-behavior dissociation plot** for Condition 3: level-2 posterior accuracy on x-axis, behavioral optimality on y-axis. Healthy conditions cluster in upper-right; lesioned condition clusters in right-center (high accuracy, medium-low optimality).
4. **Planning depth × affect interaction**: 2×2 plot showing payoff as a function of planning depth (2 vs. 8) and affect (present vs. absent), demonstrating whether affective weighting creates a benefit that depth alone does not in the current binary-action task.
5. **Precision vs. reward-average response to Exploiter partner**: time series showing how $\beta_k$ (precision-based) and $\bar{R}_k$ (reward-average) diverge when an Exploiter transitions from cooperation to exploitation. Precision should drop before reward average does.

Supplementary figures:

6. **Computational cost comparison** (supplementary): bar chart of mean policy-tree nodes per decision for Conditions 1 vs. 2. Demoted from key figures because the flat depth curve under sophisticated inference makes cost comparison less interpretively central than the affect/no-affect behavioral separation.

### 6.5 Implementation Timeline (Completed)

These phases describe the original build sequence. For future research phases (theory tightening, variational beta, clinical sensitivity, model comparison, richer tasks, human data), see the Phase Roadmap in Section 8.5.

| Phase | Tasks | Duration | Status |
|---|---|---|---|
| Build 1 | Implement basic multi-partner POMDP in the repository's JAX-first stack (Conditions 1, 4) | 2 weeks | Done |
| Build 2 | Implement affective state and shallow-EFE weighting mechanism (Condition 2) | 1-2 weeks | Done |
| Build 3 | Implement lesion and reward-average conditions (Conditions 3, 5) | 1 week | Done |
| Build 4 | Run primary simulations (Variant A, all conditions, 100 replications) | 1 week | Done |
| Build 5 | Analysis and visualization of primary results | 1 week | Done |
| Build 6 | Run Variants B, C, D | 2 weeks | Partial (B, E done) |
| Build 7 | Sensitivity analyses and parameter sweeps | 1 week | Partial (horizon sweep done) |
| Build 8 | Write-up | 2-3 weeks | In progress |

### 6.6 Current Empirical Status

The current repo state is no longer pre-results. The core sophisticated-inference experiment families have been run and interpreted:

- `default`: 100 replications x 200 rounds, random partner assignment, conditions 1-5
- `betrayal_stress`: 50 replications x 120 rounds, agent-choice with a scheduled betrayal switch, conditions 1-3 and 5
- `horizon_sweep`: 100 replications x 200 rounds, random partner assignment, conditions 1, 2, 4, 6, and 7

Current scorecard:

| Hypothesis | Default | Betrayal Stress | Horizon Sweep / cross-run read | Final reading |
|---|---|---|---|---|
| H1 affect > baseline | Supported (`d = 0.64`, `p = 1.1e-5`) | Supported (`d = 1.30`, `p = 6.8e-9`) | Supported: all non-affective horizons are tied (`p > 0.93` pairwise) while `C2` exceeds each one (`p < 2e-5`) | Affect adds value orthogonal to explicit depth |
| H2 lesion dissociation | Supported: accuracy match `p = 0.96`, payoff gap `p = 1.4e-5` | Supported: accuracy match `p = 0.55`, payoff gap `p = 9.6e-7` | `C3 = C4` exactly in `default`, confirming the lesion is a pure affect-to-action decoupling | Strongly supported |
| H3 precision > reward average | Null (`d = 0.009`, `p = 0.95`) | Supported (`d = 0.59`, `p = 0.004`) | Context-dependent: default remains tied, betrayal stress separates them | Supported when prediction error and reward dissociate |
| H4 post-switch robustness | Supported (`p = 2.8e-9` vs `C1`, `p = 5.4e-9` vs `C4`) | Supported (`p = 0.013` vs `C1`) | Consistent with affective inertia helping after switches | Supported |
| H5 partner selection | N/A | Supported (`r = 0.51`, `p = 2.9e-9`) | N/A | Supported |

Interpretation:

- The old depth-compensation framing no longer fits the data. Under sophisticated inference, non-affective planners from `τ = 2` through `τ = 8` are statistically indistinguishable in the default task: `C1 = 529.26`, `C7 = 529.40`, `C6 = 529.82`, `C4 = 530.04`, with every pairwise `p > 0.93`.
- The defensible claim is **orthogonal augmentation**. Affect adds a partner-specific terminal signal that improves policy evaluation in a way explicit lookahead depth does not recover in the shipped binary-action task.
- H3 is no longer a confirmed null. It is a boundary-condition result: null in `default`, but supported in `betrayal_stress` where the scheduled betrayal creates a temporary dissociation between recent reward and current predictive reliability (`C2 = 481.88` vs `C5 = 428.32`, `p = 0.004`, `d = 0.59`).
- `C3` and `C4` are exactly identical in the default run, confirming that `mu = 0` removes the affective contribution cleanly without perturbing belief updating or other planning logic.

For the rolling summary and next recommended run, see [docs/results_tracking.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/docs/results_tracking.md).

---

## 7. Outcomes and Their Interpretations

### 7.1 Realized Outcome: Orthogonal Augmentation (RESOLVED)

Condition 2 beats the full non-affective family, not just the shallow baseline. Conditions 1, 4, 6, and 7 remain tightly clustered because sophisticated inference removes the old mean-field bottleneck and the current binary action space gives extra explicit horizon very little marginal leverage. Condition 3 reproduces the Damasio-style knowledge/deployment dissociation. Condition 2 and Condition 5 separate only in betrayal-style environments where reward history and predictive reliability come apart. Affective inertia also improves post-switch robustness.

**Interpretation**: Affect provides genuine computational benefit as orthogonal augmentation — per-partner metacognitive precision tracking changes policy evaluation in a way deeper non-affective planning does not recover in this task family. The strongest supported claim is narrower than the original plan: a per-partner precision-augmentation account, not a planning-depth account.

**Status**: This is the empirically realized outcome across `default`, `betrayal_stress`, and `horizon_sweep` runs. The `deep_affect_test` (C8) comparison further supports this: C2 and C8 are statistically indistinguishable, confirming affect provides the same benefit regardless of the explicit planning depth it is paired with.

### 7.2 Realized Outcome: Context-Dependent Precision vs. Reward Average (RESOLVED)

Conditions 2 and 5 perform comparably in `default`, but separate in `betrayal_stress`.

**Interpretation**: The precision-specific claim is a boundary-condition result. It becomes visible when the environment creates a genuine prediction-reward dissociation. Default-style tasks are the null boundary condition; betrayal-style tasks are the positive mechanism test. H3 is framed accordingly as a conditional hypothesis.

### 7.3 Remaining Risk: Task-Specificity of the Flat Depth Curve

The flat non-affective depth curve is a property of the current binary-action trust game under sophisticated inference. In richer action spaces or more structurally branching tasks, explicit depth may regain marginal value, potentially reshaping the affect-vs-depth relationship.

**Implication**: The augmentation claim is well-supported in the shipped task family. Generalization to richer environments requires further experimentation (see Phase 7 in Section 8).

### 7.4 Unrealized Scenario: Lesion Failure (NOT OBSERVED)

Condition 3 performing similarly to Condition 2 was not observed. C3 = C4 exactly in the default run, confirming the lesion cleanly removes the affective contribution. Retained for reference only.

### 7.5 Unrealized Scenario: Affect Doesn't Help (NOT OBSERVED)

All conditions performing comparably far below Condition 1 was not observed. Affect reliably helps across all tested task variants. Retained for reference only.

---

## 8. Extensions and Future Directions

### 8.1 From Simulated Affect to Fitted Behavior (Phase 8: Human Data)

Fit the model to human behavioral data from multi-partner trust games. Estimate $\lambda$ (affective timescale) and $\mu$ (affective influence) as individual-difference parameters. Test whether estimated affective parameters correlate with self-reported emotional awareness, interoceptive accuracy, or alexithymia scores.

### 8.2 Bridge to Structure Learning (Phase 7: Richer Tasks)

Implement Bayesian Model Reduction triggered by persistent low $\beta_k$. When the affective state for partner $k$ remains below a threshold despite ongoing parameter learning, launch BMR over alternative social model structures (partner types, coalition structures, domain-specific reliability). Test whether this accelerates discovery of non-trivial social structures compared to untriggered BMR.

**Critical analysis warning**: The trigger-based BMR formulation needs reformulation before it can be used for formal model comparison (see H6). Using affect thresholds to trigger structural changes conflates the affective signal with the model selection process, making it impossible to cleanly evaluate whether affect improves model evidence. A cleaner approach would separate the BMR machinery from the affective trigger and compare triggered vs. untriggered BMR as competing model selection strategies, rather than embedding the trigger in the generative model itself.

### 8.3 Developmental Bootstrapping (Phase 7: Richer Tasks)

Initialize agents with no prior knowledge and simulate the full developmental trajectory: from exploration-heavy behavior (all partners are novel → low precision → high epistemic drive) through gradual affective differentiation (partners become differentially predictable) to a mature state with stable partner-specific affective profiles. Compare the learning trajectory to developmental findings on children's trust calibration.

**Critical analysis warning**: Learning rate modulation based on $\beta$ (e.g., increasing learning rate when precision is low) creates a positive feedback loop risk: low $\beta$ increases learning rate, which increases belief volatility, which increases surprise, which further lowers $\beta$. Any extension that couples $\beta$ to the learning dynamics must include stability analysis or damping to prevent runaway oscillation. Phase 4 (discrete hidden-state $\beta$) would help by replacing the continuous EMA with a categorical inference scheme that has natural self-regularization through the transition prior.

### 8.4 Clinical Parameter Sensitivity Analysis (Phase 5)

Vary model parameters to probe clinically relevant behavioral signatures:
- **Alexithymia** ($\alpha \to 0$): attenuated affective charge, near-flat beta trajectories
- **Borderline patterns** (high $\alpha$ + low $\lambda$): intense, volatile affective states
- **Depression** (low $\beta_0$): chronically low precision estimates, reduced engagement
- **Anxiety**: increased epistemic drive weighting when $\beta_k$ is low (uncertainty triggers excessive information-seeking)

**Critical analysis warning**: These are sensitivity analyses, not a unified clinical framework. The parameter-to-phenotype mappings are illustrative and should not be interpreted as validated clinical models. The configs exist (see H7) but moving from sensitivity analysis to clinical modeling requires: (a) fitting to human behavioral data, (b) formal model comparison showing the affective model outperforms simpler alternatives on clinical populations, and (c) demonstrating that the parameter variations are identifiable from behavioral data alone rather than being degenerate with other model parameters.

**Preliminary result (binary game)**: A systematic exploration found that the binary trust game's EFE landscape is too unambiguous for clinical parameter perturbations to produce behavioral differentiation (<0.5% effects). The dynamics differentiate correctly (beta trajectories match clinical predictions) but don't translate into payoff or action differences.

**Updated result (graded game)**: The graded investment trust game (Section 8.5) resolves this. With q_pi_entropy ~5.8 (vs <0.01 in binary), all three clinical conditions produce d>2.1 effects vs C4 (no affect). However, between-clinical differentiation remains small (10.324–10.353 payoff range across alexithymia, borderline, and depression). The graded game activates the terminal value channel but does not produce large between-clinical differences.

### 8.5 Graded Investment Trust Game (Phase 7 — Completed)

The graded investment trust game replaces the binary cooperate/defect action with 6 investment levels (0%, 20%, 40%, 60%, 80%, 100% of endowment), creating 24 actions per step (6 levels × 4 partners). This produces q_pi_entropy ~5.8 (vs <0.01 in binary), activating the precision modulation channel that was structurally inert in the binary game due to softmax saturation.

**Mu calibration fix**: when `deep_horizon == shallow_horizon` (necessary in the graded game due to combinatorial explosion), mu is computed as `mean_abs_efe × max(1, horizon_gap)` instead of returning 0. This gives mu ≈ 2.36.

**Results summary** (see `docs/results_tracking.md` for full details):

- **H1 strengthened**: C2 >> C4 with d=1.14 (vs d=0.64 in binary)
- **H2 confirmed**: C3 = C4 exactly (lesion strips affect)
- **H3 reversed**: C5 > C2 in both default (d=0.43) and betrayal (d=0.89) — reward averaging outperforms precision tracking
- **Clinical sensitivity activated**: parameter variations produce d>2.1 effects vs C4 (vs <0.5% in binary)

The C5 > C2 result is the key finding. In the graded game's ambiguous landscape, direct reward encoding provides more focused terminal value guidance than precision-weighted affect. The precision tracking mechanism's advantage is modelability (clinical parameter mappings), not raw performance.

### 8.6 Phase Roadmap

| Phase | Description | Dependencies | Status |
|---|---|---|---|
| Phase 3 | Theory tightening: formalize the augmentation claim, present the variational grounding of beta via Hesp et al. | Current results | In progress |
| Phase 4 | Variational beta: replace EMA with proper variational inference over precision | Phase 3 | Planned |
| Phase 5 | Clinical sensitivity: revisit in richer environments | Phase 7 | **Completed** (graded game enables d>2.1 clinical effects) |
| Phase 6 | Model comparison: formal Bayesian model evidence comparison (H6) | Phase 4 | Planned |
| Phase 7 | Richer tasks: test whether depth curve remains flat in larger action spaces, structure learning | Phase 3 | **Completed** (graded investment trust game) |
| Phase 8 | Human data: fit to behavioral data, estimate individual-difference parameters | Phases 5-7 | Planned |
