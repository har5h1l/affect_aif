# Experimentation Plan: Affect as Computational Infrastructure for Social Inference

## Testing Per-Partner Affective Precision in Multi-Agent Active Inference

---

## 1. Overview

This document specifies the experimental design for testing the central claim: per-partner affective states (tracking social model precision) improve shallow-planning active inference agents by adding partner-specific confidence information, and ablating these states reproduces the behavioral signature of vmPFC damage — intact social knowledge with impaired social decision-making.

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
- Policy selection: EFE over 2-step horizon, precision-weighted by the first partner's affective signal
- Precision modulation: off by default in the primary experiments (`affect_modulates_precision=False`), so Condition 2 tests shallow-EFE weighting rather than per-partner $\gamma_k$ modulation
- Purpose: tests the core hypothesis — does affective precision weighting improve shallow planning beyond what horizon-2 evaluation can do on its own?

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

---

## 5. Hypotheses and Predictions

### Hypothesis 1: Affect Provides Value Beyond Planning Depth

**Prediction**: Condition 2 (affective, shallow) outperforms every non-affective planner, including Conditions 1, 4, 6, and 7, while using much less explicit computation than the deep planner.

**Metrics**:
- Cumulative payoff over 200 rounds (primary)
- Number of policy-tree nodes expanded per decision (computational cost)
- Per-round decision time (wall clock, if relevant)

**Expected outcome**: Under sophisticated inference, the explicit-depth curve among non-affective agents is flat in this binary-action trust game, so Condition 2 should beat the whole no-affect family rather than merely matching Condition 1. This reframes the result from "affect approximates deep lookahead" to "affect adds a partner-specific evaluation signal that depth alone does not recover here."

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

### Hypothesis 3: Precision Tracking Outperforms Reward Averaging

**Prediction**: Condition 2 (precision-based affect) outperforms Condition 5 (reward-average weighting), particularly in scenarios with:
- Reliable adversaries (same average reward but different model precision)
- Volatile periods (where uncertainty information matters most)
- Mixed partner populations (where some partners are predictable and others aren't)

**Metrics**:
- Cumulative payoff (overall and broken down by partner type)
- Performance in the first 10 rounds after a partner type switch (where uncertainty information is most valuable)
- Exploitation rate by Exploiter-type partners
- In the betrayal stress test, performance in the first 5-10 encounters after the forced cooperator→exploiter switch

**Expected outcome**: The result is now expected to be context-dependent rather than universal. In the default random-assignment task, Condition 2 and Condition 5 can remain effectively tied because prediction accuracy and reward history stay closely aligned. In the betrayal-stress task, the reward-average agent should be exploited more by the forced cooperator→exploiter switch because it confuses attractive recent reward with current reliability, whereas the precision-based agent reacts to the spike in surprise.
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
- Computational cost comparison (Conditions 1 vs. 2): paired t-test on nodes-expanded-per-decision
- Knowledge vs. behavior dissociation (Condition 3): correlation between level-2 posterior accuracy and behavioral optimality, plotted over time
- Precision vs. reward-average (Conditions 2 vs. 5): interaction analysis of condition × partner-type on per-partner payoff
- Noise robustness (Hypothesis 4): segmented analysis of performance in stable vs. post-switch windows
- Sensitivity analysis: sweep over $\lambda$ (0.7-0.99), $\mu$ (0.5-5.0), $p_{\text{switch}}$ (0.01-0.1) to characterize robustness of results to parameter choices

**Execution workflow note**:
- `scripts/run_experiment.py` accepts repeated `--config` flags and a shared `--workers` pool so multiple experiment configs can be queued in one invocation.
- Outputs are written per config under `<output-dir>/<batch-id>/<config-name>/results.csv`, which keeps each experiment variant isolated while still allowing the scheduler to share workers across all queued replications.
- `affect_aif/configs/horizon_sweep.json` is the reference config for Conditions 1, 2, 4, 6, and 7; analysis now emits a horizon-sweep figure so the affective shallow condition can be read directly against explicit depth.
- `affect_aif/configs/deep_affect_test.json` is the targeted follow-up for Conditions 1, 2, and 8, isolating whether affect adds anything once explicit planning is already deep.

### 6.4 Visualizations

Key figures for the paper:

1. **Cumulative payoff curves** (all 5 conditions, averaged over 100 replications with confidence bands)
2. **Affective state trajectories** for Condition 2: $\beta_k$ over time for each partner, with partner type switches marked as vertical lines. Should show slow tracking with inertial response to switches.
3. **Knowledge-behavior dissociation plot** for Condition 3: level-2 posterior accuracy on x-axis, behavioral optimality on y-axis. Healthy conditions cluster in upper-right; lesioned condition clusters in right-center (high accuracy, medium-low optimality).
4. **Planning depth × affect interaction**: 2×2 plot showing payoff as a function of planning depth (2 vs. 8) and affect (present vs. absent), demonstrating whether affective weighting creates a benefit that depth alone does not in the current binary-action task.
5. **Precision vs. reward-average response to Exploiter partner**: time series showing how $\beta_k$ (precision-based) and $\bar{R}_k$ (reward-average) diverge when an Exploiter transitions from cooperation to exploitation. Precision should drop before reward average does.
6. **Computational cost comparison**: bar chart of mean policy-tree nodes per decision for Conditions 1 vs. 2.

### 6.5 Expected Timeline

| Phase | Tasks | Duration |
|---|---|---|
| Phase 1 | Implement basic multi-partner POMDP in the repository's JAX-first stack (Conditions 1, 4) | 2 weeks |
| Phase 2 | Implement affective state and shallow-EFE weighting mechanism (Condition 2) | 1-2 weeks |
| Phase 3 | Implement lesion and reward-average conditions (Conditions 3, 5) | 1 week |
| Phase 4 | Run primary simulations (Variant A, all conditions, 100 replications) | 1 week |
| Phase 5 | Analysis and visualization of primary results | 1 week |
| Phase 6 | Run Variants B, C, D | 2 weeks |
| Phase 7 | Sensitivity analyses and parameter sweeps | 1 week |
| Phase 8 | Write-up | 2-3 weeks |

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

- The old "affect compensates for shallow depth" framing no longer fits the data. Under sophisticated inference, non-affective planners from `τ = 2` through `τ = 8` are statistically indistinguishable in the default task: `C1 = 529.26`, `C7 = 529.40`, `C6 = 529.82`, `C4 = 530.04`, with every pairwise `p > 0.93`.
- The more defensible claim is **augmentation, not compensation**. Affect adds a partner-specific terminal signal that improves policy evaluation in a way explicit lookahead depth does not recover in the shipped binary-action task.
- H3 is no longer a confirmed null. It is a boundary-condition result: null in `default`, but supported in `betrayal_stress` where the scheduled betrayal creates a temporary dissociation between recent reward and current predictive reliability (`C2 = 481.88` vs `C5 = 428.32`, `p = 0.004`, `d = 0.59`).
- `C3` and `C4` are exactly identical in the default run, confirming that `mu = 0` removes the affective contribution cleanly without perturbing belief updating or other planning logic.

For the rolling summary and next recommended run, see [docs/results_tracking.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/docs/results_tracking.md).

---

## 7. Possible Outcomes and Their Interpretations

### 7.1 Strongest Supported Read

Condition 2 beats the full non-affective family, not just the shallow baseline. Condition 3 reproduces the Damasio-style knowledge/deployment dissociation. Condition 2 and Condition 5 separate only in betrayal-style environments where reward history and predictive reliability come apart. Affective inertia also improves post-switch robustness.

**Interpretation**: affect is computational infrastructure for social inference, but the strongest supported claim is narrower than the original plan. The current evidence supports a per-partner precision-augmentation account over a pure planning-depth account. In this task family, affect changes policy evaluation in a way deeper non-affective planning does not recover.

**Next steps**: run the targeted `C8` comparison when needed, then move to richer task families if the goal is to test whether explicit depth matters again once the environment has more structural branching.

### 7.2 Empirically Realized Outcome: Affect Helps but Depth Alone Does Not

Condition 2 improves over the non-affect controls, but Conditions 1, 4, 6, and 7 remain tightly clustered because sophisticated inference removes the old mean-field bottleneck and the current binary action space gives extra explicit horizon very little marginal leverage.

**Interpretation**: affect provides genuine computational benefit, but the default task does not support a strong "depth compensation" claim because depth alone is largely irrelevant here. The defensible result is that partner-specific weighting changes evaluation in a way that shallow and deep non-affect planners both miss.

**Adjustment**: keep the benchmark claim focused on augmentation and post-switch robustness, and use richer action spaces or more structurally branching tasks if the goal is to recover a non-flat explicit-depth curve.

### 7.3 Context Dependence in Precision vs Reward Average

Conditions 2 and 5 perform comparably in `default`, but separate in `betrayal_stress`.

**Interpretation**: the precision-specific claim is not a universal win, but it is not dead either. It becomes visible when the environment creates a genuine prediction-reward dissociation, such as a scheduled betrayal where cached reward remains attractive while surprise spikes.

**Adjustment**: frame H3 as a conditional hypothesis. Default-style tasks remain a null boundary condition; betrayal-style tasks are the positive mechanism test.

### 7.4 The Lesion Doesn't Produce the Expected Dissociation

Condition 3 performs similarly to Condition 2, or its level-2 posteriors are also degraded (not just behavior).

**Interpretation**: the architecture doesn't cleanly dissociate knowledge from deployment. Possible reasons: (a) in this simple task, 2-step planning is actually sufficient and affect is redundant, (b) the lesion implementation doesn't correctly model the vmPFC disconnection, (c) the task needs to be harder (more partners, faster volatility, partial observability) to stress the planning system enough.

**Adjustment**: increase task difficulty until shallow planning clearly fails (higher $p_{\text{switch}}$, more partners, noisy observations). If the dissociation appears only at higher difficulty, this is still a meaningful result — it characterizes the boundary conditions under which affective infrastructure becomes necessary.

### 7.5 Worst Case: Affect Doesn't Help

Conditions 2, 3, 4, 5 all perform comparably and all far below Condition 1. Only deep planning works.

**Interpretation**: the affective weighting is not a good approximation of the true value-to-go in this task. The social environment may be too volatile or too adversarial for a slow affective summary to track.

**Adjustment**: this is a genuinely negative result. Consider whether (a) the affective update rule needs to be more sophisticated (perhaps a full Bayesian precision estimate rather than an EMA), (b) the timescale separation is wrong ($\lambda$ too high or too low), or (c) the theoretical framework needs revision — maybe affect helps in specific task niches rather than generally.

---

## 8. Extensions and Future Directions

### 8.1 From Simulated Affect to Fitted Behavior

Fit the model to human behavioral data from multi-partner trust games. Estimate $\lambda$ (affective timescale) and $\mu$ (affective influence) as individual-difference parameters. Test whether estimated affective parameters correlate with self-reported emotional awareness, interoceptive accuracy, or alexithymia scores.

### 8.2 Bridge to Structure Learning

Implement Bayesian Model Reduction triggered by persistent low $\beta_k$. When the affective state for partner $k$ remains below a threshold despite ongoing parameter learning, launch BMR over alternative social model structures (partner types, coalition structures, domain-specific reliability). Test whether this accelerates discovery of non-trivial social structures compared to untriggered BMR.

### 8.3 Developmental Bootstrapping

Initialize agents with no prior knowledge and simulate the full developmental trajectory: from exploration-heavy behavior (all partners are novel → low precision → high epistemic drive) through gradual affective differentiation (partners become differentially predictable) to a mature state with stable partner-specific affective profiles. Compare the learning trajectory to developmental findings on children's trust calibration.

### 8.4 Clinical Modeling

Vary model parameters to simulate psychiatric conditions:
- **Alexithymia**: reduce the gain $\alpha$ on affective charge (feelings are attenuated)
- **Borderline patterns**: increase $\alpha$ and decrease $\lambda$ (feelings are intense and volatile)
- **Depression**: bias $\beta_k$ toward low values (chronic low precision → reduced engagement)
- **Anxiety**: increase epistemic drive weighting when $\beta_k$ is low (uncertainty triggers excessive information-seeking)

Test whether these parameter variations reproduce known behavioral profiles in social decision-making tasks.
