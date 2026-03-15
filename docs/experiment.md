# Experimentation Plan: Affect as Computational Infrastructure for Social Inference

## Testing Per-Partner Affective Precision in Multi-Agent Active Inference

---

## 1. Overview

This document specifies the experimental design for testing the central claim: per-partner affective states (tracking social model precision) allow shallow-planning active inference agents to match deep-planning agents in multi-partner social environments, and ablating these states reproduces the behavioral signature of vmPFC damage — intact social knowledge with impaired social decision-making.

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

Types are stable within blocks but switch at geometrically-distributed intervals (expected block length ~20 rounds, minimum 10). The agent does not observe type switches directly.

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

**Policy evaluation**: standard expected free energy computation over the planning horizon. For affective agents, an affective terminal value is appended at the end of the shallow horizon.

### 2.6 Affective State Update (Level 3 Implementation)

After each trial with partner $k$, the affective state is updated:

```
# After observing partner k's action at time t:
prediction = E[o_t | current posterior over s^(2)_k]
actual = o_t
epsilon_k = actual - prediction                    # prediction error
sq_error = epsilon_k^2

# Affective charge: positive if model is accurate, negative if not
charge = alpha * (sigma_0^2 - sq_error)

# Exponential moving average update
beta_k = lambda * beta_k + (1 - lambda) * sigmoid(charge)
```

Parameters:
- $\lambda = 0.9$ — smoothing parameter (affective state is 10× slower than beliefs)
- $\alpha = 1.0$ — charge sensitivity
- $\sigma_0^2$ — baseline expected error (set to the variance of a uniform-random partner)
- sigmoid clamps the charge contribution to $[0, 1]$

The affective terminal value is then:

```
continuation_k = E[payoff | terminal_state_k, terminal_action] / max_abs_payoff
V_affect_k = -mu * beta_k * continuation_k
```

Where $\mu$ scales the influence of affect on policy selection. This keeps the terminal contribution context-sensitive rather than treating every policy involving a partner as equally good or bad.

---

## 3. Environment and Task

### 3.1 Multi-Partner Trust Game

The agent interacts with $K = 4$ partners over $N = 200$ rounds. Each round:

1. A partner is selected (either randomly assigned or agent-chosen — see Variant 3.4)
2. The agent and partner simultaneously choose Cooperate or Defect
3. Payoffs are determined by the Trust Game matrix
4. The agent observes the partner's action and updates beliefs

Partners' hidden types switch according to the geometric distribution ($p_{\text{switch}} = 0.05$ per trial). The agent must learn partner types, track changes, and choose actions to maximize cumulative payoff.

### 3.2 Why This Task

This task is chosen to satisfy several requirements:

- **Multi-partner**: forces the agent to maintain separate models (and potentially separate affective states) for each partner, stressing computational resources.
- **Sequential and volatile**: partner types change, so the agent must continuously update rather than converging to a fixed strategy. This is where planning depth matters most.
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
- Policy selection: EFE over 2-step horizon + affective terminal value $V_k(\beta_k)$
- Purpose: tests the core hypothesis — can affect compensate for reduced planning depth?

### 4.3 Condition 3: Lesioned Affective Agent (vmPFC Analog)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): present in architecture but **decoupled** from policy selection
  - Option 3a: $\beta_k$ fixed at 0.5 (neutral) for all partners, all time
  - Option 3b: $\beta_k$ updates normally but $\mu = 0$ (affect doesn't influence EFE)
- Level 2 (social model): fully intact, updates normally
- Policy selection: EFE over 2-step horizon, no terminal value
- Purpose: reproduces the Damasio pattern — the agent can correctly identify partner types (inspect level-2 posteriors) but cannot efficiently use this knowledge for decision-making.

Both lesion variants (3a, 3b) should be tested. 3b is the cleaner analog — the agent "feels" things but feelings don't influence decisions, modeling the vmPFC disconnection from action selection rather than destruction of the representation itself.

### 4.4 Condition 4: Shallow Planner, No Affect (Minimal Baseline)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): absent
- Policy selection: EFE over 2-step horizon only
- Purpose: confirms that shallow planning alone (without affect) genuinely fails, establishing that it is affect specifically (not just additional computation of any kind) doing the work.

### 4.5 Condition 5: Reward-Average Agent (Value Function Control)

- Planning horizon: $\tau = 2$
- Instead of precision-based affect: a simple exponential moving average of reward per partner, used as terminal value
- $\bar{R}_k^{(t+1)} = \lambda \bar{R}_k^{(t)} + (1 - \lambda) \cdot r_t$
- Terminal signal: $\tilde{R}_k = 0.5 \cdot (1 + \tanh(\bar{R}_k / \max |r|))$
- Terminal value: $V_k = -\mu \cdot \tilde{R}_k \cdot \frac{\mathbb{E}[r \mid s^{\mathrm{terminal}}_k, a^{\mathrm{terminal}}]}{\max |r|}$
- Purpose: distinguishes the precision-tracking account from a simpler "cached value" account. If Condition 2 outperforms Condition 5, it demonstrates that tracking model precision provides information that reward averaging does not (the uncertainty preservation argument).

---

## 5. Hypotheses and Predictions

### Hypothesis 1: Affect Compensates for Planning Depth

**Prediction**: Condition 2 (affective, shallow) achieves cumulative payoff within 5% of Condition 1 (deep, no affect), while using significantly fewer computational resources.

**Metrics**:
- Cumulative payoff over 200 rounds (primary)
- Number of policy-tree nodes expanded per decision (computational cost)
- Per-round decision time (wall clock, if relevant)

**Expected outcome**: Affective agents achieve ~95% of deep-planner performance at ~25% of computational cost (2-step horizon vs. 8-step = exponentially fewer branches).

**Failure mode**: If Condition 2 significantly underperforms Condition 1 (>10% payoff gap), it means the affective terminal value is not a good enough approximation of deep planning. This would require either (a) increasing τ to 3-4, or (b) enriching the affective state representation.

### Hypothesis 2: Lesion Reproduces Damasio Pattern

**Prediction**: Condition 3 (lesioned) shows:
- Level-2 posteriors correctly identify partner types (comparable accuracy to Condition 1)
- Behavioral performance is significantly worse than Condition 2 (and comparable to Condition 4)
- The deficit is largest during volatile periods (after partner type switches)

**Metrics**:
- Partner type identification accuracy (inspecting argmax of level-2 posterior)
- Cumulative payoff (should be near Condition 4 level)
- Performance gap between stable periods and post-switch periods

**Expected outcome**: Lesioned agents "know" partner types but "can't use" that knowledge. During stable periods (types not switching), the lesion effect is moderate — shallow planning is adequate when nothing changes. During volatile periods, the lesion effect is large — without affective inertia to buffer noise and without terminal value to extend planning, the agent makes myopic, exploitable decisions.

**Failure mode**: If the lesioned agent performs as well as Condition 2, then affect isn't doing computational work — the architecture itself (having a level-3 state, even decoupled) provides some benefit, or the task is too easy for 2-step planning alone.

### Hypothesis 3: Precision Tracking Outperforms Reward Averaging

**Prediction**: Condition 2 (precision-based affect) outperforms Condition 5 (reward-average terminal value), particularly in scenarios with:
- Reliable adversaries (same average reward but different model precision)
- Volatile periods (where uncertainty information matters most)
- Mixed partner populations (where some partners are predictable and others aren't)

**Metrics**:
- Cumulative payoff (overall and broken down by partner type)
- Performance in the first 10 rounds after a partner type switch (where uncertainty information is most valuable)
- Exploitation rate by Exploiter-type partners

**Expected outcome**: The reward-average agent is exploited more by Exploiter types (who provide good initial rewards but then defect) because it confuses high past reward with high future reliability. The precision-based agent detects increasing prediction errors from the Exploiter earlier, even before average reward drops, because the Exploiter's transition from cooperation to defection produces model misfit that precision tracking catches but reward averaging misses.

**Failure mode**: If Conditions 2 and 5 perform comparably, then the simpler reward-average account is sufficient and the precision interpretation isn't necessary. This would weaken the theoretical contribution but not destroy the planning-depth result.

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

Primary implementation in **pymdp** (Python library for active inference POMDPs). The basic POMDP structure (levels 1-2) uses standard pymdp machinery. The affective state (level 3) is implemented as an auxiliary variable outside the core POMDP loop, modulating the EFE computation through the terminal value mechanism.

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
| Affective smoothing ($\lambda$) | 0.9 | 10× slower than belief updates |
| Affective scaling ($\mu$) | Tuned via grid search | Should be calibrated so affect meaningfully shifts policy selection |
| Replications per condition | 100 | Sufficient for reliable statistics |

### 6.3 Analysis Plan

**Primary analysis**: mixed-effects ANOVA on cumulative payoff with Condition as fixed factor and replication as random factor. Post-hoc pairwise comparisons with Bonferroni correction.

**Secondary analyses**:
- Computational cost comparison (Conditions 1 vs. 2): paired t-test on nodes-expanded-per-decision
- Knowledge vs. behavior dissociation (Condition 3): correlation between level-2 posterior accuracy and behavioral optimality, plotted over time
- Precision vs. reward-average (Conditions 2 vs. 5): interaction analysis of condition × partner-type on per-partner payoff
- Noise robustness (Hypothesis 4): segmented analysis of performance in stable vs. post-switch windows
- Sensitivity analysis: sweep over $\lambda$ (0.7-0.99), $\mu$ (0.5-5.0), $p_{\text{switch}}$ (0.01-0.1) to characterize robustness of results to parameter choices

### 6.4 Visualizations

Key figures for the paper:

1. **Cumulative payoff curves** (all 5 conditions, averaged over 100 replications with confidence bands)
2. **Affective state trajectories** for Condition 2: $\beta_k$ over time for each partner, with partner type switches marked as vertical lines. Should show slow tracking with inertial response to switches.
3. **Knowledge-behavior dissociation plot** for Condition 3: level-2 posterior accuracy on x-axis, behavioral optimality on y-axis. Healthy conditions cluster in upper-right; lesioned condition clusters in right-center (high accuracy, medium-low optimality).
4. **Planning depth × affect interaction**: 2×2 plot showing payoff as a function of planning depth (2 vs. 8) and affect (present vs. absent), demonstrating the interaction — affect helps shallow planners dramatically but helps deep planners only marginally.
5. **Precision vs. reward-average response to Exploiter partner**: time series showing how $\beta_k$ (precision-based) and $\bar{R}_k$ (reward-average) diverge when an Exploiter transitions from cooperation to exploitation. Precision should drop before reward average does.
6. **Computational cost comparison**: bar chart of mean policy-tree nodes per decision for Conditions 1 vs. 2.

### 6.5 Expected Timeline

| Phase | Tasks | Duration |
|---|---|---|
| Phase 1 | Implement basic multi-partner POMDP in pymdp (Conditions 1, 4) | 2 weeks |
| Phase 2 | Implement affective state and terminal value mechanism (Condition 2) | 1-2 weeks |
| Phase 3 | Implement lesion and reward-average conditions (Conditions 3, 5) | 1 week |
| Phase 4 | Run primary simulations (Variant A, all conditions, 100 replications) | 1 week |
| Phase 5 | Analysis and visualization of primary results | 1 week |
| Phase 6 | Run Variants B, C, D | 2 weeks |
| Phase 7 | Sensitivity analyses and parameter sweeps | 1 week |
| Phase 8 | Write-up | 2-3 weeks |

---

## 7. Possible Outcomes and Their Interpretations

### 7.1 Best Case: All Hypotheses Confirmed

Condition 2 matches Condition 1 at a fraction of the computational cost. Condition 3 reproduces the Damasio pattern. Condition 2 > Condition 5 on Exploiter detection. Affective inertia provides noise robustness.

**Interpretation**: affect is computational infrastructure for social inference. The per-partner precision-tracking account is supported over simpler alternatives. The model provides the first computational demonstration of the somatic marker hypothesis in a multi-agent setting.

**Next steps**: extend to more complex social scenarios (larger groups, more partner types, partial observability of actions), test whether affective states can trigger structural model revision (BMR bridge), explore developmental trajectories (how affective states bootstrap from scratch).

### 7.2 Partial Success: Affect Helps but Doesn't Fully Compensate

Condition 2 improves over Condition 4 but falls short of Condition 1 (e.g., 80% of deep-planner performance rather than 95%).

**Interpretation**: affect provides genuine computational benefit but is not sufficient to fully replace deep planning. The agent needs some minimal planning depth plus affect.

**Adjustment**: test intermediate planning depths ($\tau = 3, 4$) and find the depth at which affect bridges the remaining gap. The story becomes: "affect reduces the *required* planning depth from 8 to 3-4, providing a 2-4× computational savings." Less dramatic but still meaningful and publishable.

### 7.3 Precision ≈ Reward Average (Hypothesis 3 Fails)

Conditions 2 and 5 perform comparably. The simpler reward-average account is sufficient.

**Interpretation**: the planning-depth compensation result still holds, but the mechanism is simpler than proposed — any slow terminal value function works, not specifically precision-based. The precision interpretation loses support.

**Adjustment**: pivot framing from "precision is the right compression" to "slow affective summarization enables depth compensation" and present the precision vs. reward-average as an open question. Look for specific scenarios (e.g., novel partner types, mixed cooperative/adversarial interactions) where precision tracking's advantage might emerge.

### 7.4 The Lesion Doesn't Produce the Expected Dissociation

Condition 3 performs similarly to Condition 2, or its level-2 posteriors are also degraded (not just behavior).

**Interpretation**: the architecture doesn't cleanly dissociate knowledge from deployment. Possible reasons: (a) in this simple task, 2-step planning is actually sufficient and affect is redundant, (b) the lesion implementation doesn't correctly model the vmPFC disconnection, (c) the task needs to be harder (more partners, faster volatility, partial observability) to stress the planning system enough.

**Adjustment**: increase task difficulty until shallow planning clearly fails (higher $p_{\text{switch}}$, more partners, noisy observations). If the dissociation appears only at higher difficulty, this is still a meaningful result — it characterizes the boundary conditions under which affective infrastructure becomes necessary.

### 7.5 Worst Case: Affect Doesn't Help

Conditions 2, 3, 4, 5 all perform comparably and all far below Condition 1. Only deep planning works.

**Interpretation**: the affective terminal value is not a good approximation of the true value-to-go in this task. The social environment may be too volatile or too adversarial for a slow affective summary to track.

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
