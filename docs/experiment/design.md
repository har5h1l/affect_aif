# Experimentation Plan: Affect as Computational Infrastructure for Social Inference

## Testing Per-Partner Affective Precision in Multi-Agent Active Inference

## Current Trust-Game Status

The supported experiment surface has moved to the action-dependent stance model described in [docs/action-dependent-partner-design.md](docs/action-dependent-partner-design.md).

- Ground-truth partners now have a fixed type and an evolving stance.
- The agent jointly infers `type × stance` and plans with action-dependent stance transitions.
- The trust-game generative model now uses two observation modalities (`o_action`, `o_payoff`) over latent `type × stance`, with `own_action` tracked separately.
- The default affective path uses the discrete HESP beta filter (`DiscreteBetaState`, `initial_beta=1.0`, beta levels `[0.5, 0.67, 1.0, 1.5, 2.0]`).
- The legacy `mu`-weighted shallow-EFE path still exists in the runner; read later mentions of `mu` as current implementation notes, not as the final end-state of the v3 migration.
- The primary factorial is Conditions `1-8` = `{tau=1,2,4,8} × {no_affect, affect}`.
- Lesion, no-epistemic, and clinical runs are named presets layered on top of the `tau4_affect` base.
- Scheduled betrayal should be expressed via `scheduled_stance_switches`, not `scheduled_type_switches`, unless the experiment is explicitly about exogenous type volatility.

Older condition numbering below is retained only as historical context and should not be used for new runs.

### Removed experiment surface (future work)

The following are intentionally **not** in the runnable tree; reintroduce them only with a real implementation and tests:

- **Variational beta** — the old `variational_beta` preset and `beta_mode` experiment field are removed. A variational auxiliary state would be new code; historical context is summarized in `docs/results/historical_findings.md`.
- **CoGames policy bridge** — the unfinished AIFPolicy adapter has been removed; CvC integration should add a policy class under `benchmarks/cvc/` when that track unfreezes.

---

## 1. Overview

This document now frames the supported trust-game program around the post-restructure action-dependent stance results.

The older story treated affect as something that compensated for shallow planning. The current binary-action results point to a different structure:

- **H1 — G compression / depth redundancy:** beyond `tau=2`, the policy set grows much faster than the discriminating `G` signal, so fixed-`gamma` planning becomes computationally redundant.
- **H2 — Affect as orthogonal augmentation:** per-partner metacognitive precision still improves payoff, but the effect should be judged at calibrated shallow horizons (`tau=1,2`) where the policy posterior remains discriminating.
- **H3 — Lesion dissociation:** affective decoupling should preserve inference accuracy while impairing payoff, most clearly in that same shallow regime.
- **H4 — Betrayal recovery:** affect should help agents recover faster after a hostile switch, with the main test focused at `tau=2`.
- **H5 — Partner selection:** beta-guided precision should shape adaptive partner choice in agent-choice settings, again at `tau=2`.

So the central claim is narrower and more structural than before: in the shipped binary-action task, depth redundancy is itself a result, and affect is tested as an orthogonal augmentation that remains useful where the policy softmax has not already saturated.

---

## 2. POMDP Structure

### 2.1 State Space Factorization

The generative model is best understood as a single hidden-state inference problem plus an auxiliary affective summary:

**Level 1 — Trial State** $s^{(1)}_t$
The current-round game context is task-given:
- which partner is currently interacting
- the partner's action on this trial: {Cooperate, Defect}

This is directly observed in the main experiments (or noisily observed in later variants — see Section 3.3). It is not treated as a latent factor in the shipped binary-action setup.

**Level 2 — Partner Type** $s^{(2)}_k$
Each partner's latent strategy type, drawn from:
- **Cooperator**: cooperates with probability 0.9
- **Reciprocator**: mirrors the agent's previous action with probability 0.85
- **Exploiter**: cooperates initially (first 3-5 rounds) then defects with probability 0.85
- **Random**: cooperates with probability 0.5

Types are stable within blocks but switch at geometrically-distributed intervals (expected block length ~20 rounds). The agent does not observe type switches directly.

**Level 3 — Affective State** $\beta_k$ (for affective agents only)
A discrete HESP-style auxiliary state per partner representing the **rate parameter** of expected policy precision. Default levels are `[0.5, 0.67, 1.0, 1.5, 2.0]`, with `\beta_k = 1.0` as the baseline prior. Lower beta means higher expected precision and more decisive policy selection when precision modulation is enabled.

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

**Level 3 transitions (affective state)**: in the default path, beta updates via a discrete predict-then-correct filter over the HESP beta levels using interoceptive observations derived from surprise.

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

**Policy evaluation**: standard expected free energy computation over the planning horizon, using sophisticated inference rather than a mean-field rollout. For each policy, the planner enumerates all future binary partner-action observation sequences, updates partner-type beliefs after each hypothetical observation via Bayes rule, and averages the pathwise EFE under the corresponding path probabilities. For affective agents, the shallow-horizon EFE is then precision-weighted by the current partner-specific signal. In the shipped binary-action task, this makes the horizon comparison a check on explicit depth rather than a proxy for different rollout approximations.

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

Where $\mu$ scales the influence of affect on policy selection in the current runner. The weight is keyed to the first partner implicated by the policy so the affective signal changes first-action marginals rather than washing out at the end of the rollout. Full experiment runs now enforce a minimum of `3` calibration episodes rather than `10`.

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
- Beta implementation: discrete HESP beta by default; config can still select the variational beta compatibility path
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

### 4.10 Condition 9: Alexithymia (Clinical)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): active, per-partner, with blunted affective charging ($\alpha = 0.1$ vs default $\alpha = 3.0$)
- Policy selection: same as Condition 2
- Purpose: models alexithymia as reduced affective responsiveness. The low $\alpha$ dampens the surprise-to-charge conversion, producing near-frozen beta trajectories.

### 4.11 Condition 10: Borderline (Clinical)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): active, per-partner, with volatile affect via amplified charge gain ($\alpha = 12.0$ vs default $\alpha = 3.0$)
- Policy selection: same as Condition 2
- Purpose: models borderline personality as over-reactive, poorly smoothed precision dynamics. High $\alpha$ amplifies charge; low $\lambda$ reduces temporal smoothing, producing noisy beta oscillations.

### 4.12 Condition 11: Depression (Clinical)

- Planning horizon: $\tau = 2$
- Level 3 (affective state): active, per-partner, with pessimistic initial precision ($\beta_0 = 2.0$ vs default $\beta_0 = 1.0$)
- Policy selection: same as Condition 2
- Purpose: models depression as a pessimistic prior on model reliability. Unlike C9 and C10, this is an initial-condition perturbation (not a dynamical parameter change), so it self-corrects through evidence accumulation.

---

## 5. Hypotheses and Predictions

### Hypothesis 1: G Compression / Depth Redundancy

**Prediction**: Under sophisticated inference with action-dependent stance dynamics, non-affective planners separate little or not at all once horizon exceeds `tau=2`, because policy entropy grows much faster than the discriminating `G` range.

**Metrics**:
- Cumulative payoff by horizon for no-affect conditions
- Policy entropy as a function of horizon
- `G` range / spread as a function of horizon

**Expected outcome**: `tau=1` and `tau=2` remain the only materially discriminating horizons in the binary task; deeper horizons enumerate many more policies without adding enough `G` contrast for fixed `gamma=1.0` to separate them. This is a structural property of the task, not a calibration failure.

**Failure mode**: If the no-affect depth curve rises materially beyond `tau=2`, then the current depth-redundancy framing is wrong and the task still supports a standard explicit-lookahead account.

### Hypothesis 2: Affect as Orthogonal Augmentation

**Prediction**: Affect-augmented agents outperform matched no-affect agents at calibrated shallow horizons (`tau=1,2`), where the policy posterior still discriminates among actions.

**Metrics**:
- Cumulative payoff for affect vs. no-affect at each shallow horizon
- Cohen's `d` and `p`-value for `tau=1` and `tau=2`
- Comparison against pooled-across-depth effect sizes

**Expected outcome**: Affect produces a clear positive effect at `tau=1,2`, larger than the weak pooled-across-depth effect seen when saturated deep horizons are included. The mechanism claim is therefore about orthogonal augmentation in the discriminating regime, not about a uniform gain at every horizon.

**Failure mode**: If affect remains weak even at `tau=1`, then the core augmentation claim needs a deeper reframing because the effect would not survive in the one regime where it should be strongest.

### Hypothesis 3: Lesion Dissociation

**Prediction**: Lesioned agents preserve partner-state inference accuracy while losing the payoff benefit provided by affective deployment, with the clearest signature expected at `tau=1,2`.

**Metrics**:
- Partner-state inference accuracy for lesioned vs. no-affect baseline
- Cumulative payoff for lesioned vs. affective baseline
- Post-switch or volatile-window payoff cost

**Expected outcome**: The Damasio-style dissociation holds, but it should be evaluated where affect still has leverage on action selection rather than in pooled deeper runs that already compress the policy posterior.

**Failure mode**: If lesion and affect remain behaviorally indistinguishable at shallow depth, then the affective deployment pathway is not doing meaningful work in the supported task.

### Hypothesis 4: Betrayal Recovery

**Prediction**: Affect-augmented agents recover faster after a hostile stance switch than matched no-affect agents, with the cleanest test at `tau=2`.

**Metrics**:
- Payoff in the post-betrayal windows (for example rounds 30-60)
- Recovery latency after the switch
- Post-switch effect size for affect vs. no-affect

**Expected outcome**: Affect helps the agent abandon an outdated trust policy faster after betrayal because beta and the partner-specific terminal signal react to the sudden prediction failure.

**Failure mode**: If post-switch payoff is flat across affect and no-affect at the calibrated horizon, then the betrayal-recovery claim is not supported in the redesigned task.

### Hypothesis 5: Partner Selection

**Prediction**: In agent-choice settings, beta-guided precision steers interaction toward well-predicted partners and away from poorly predicted ones, with the main test focused at `tau=2`.

**Metrics**:
- Correlation between beta / terminal signal and partner selection frequency
- Partner-selection entropy
- Payoff conditioned on selected partner

**Expected outcome**: Affect-augmented agents should concentrate interactions on partners whose models are stable or rapidly become stable, rather than distributing play uniformly.

**Failure mode**: If partner selection is uncorrelated with beta at `tau=2`, then the precision signal is not being deployed behaviorally in the agent-choice regime.

### Hypothesis 6 (FUTURE/PROPOSED): Predictive Model Comparison of Affective vs. Non-Affective Generative Models

**Status: Supported as a follow-up comparison; Condition 12 already provides the variational beta path.**

**Prediction**: Predictive log scores favor the affective generative model over the non-affective generative model, providing a principled basis for preferring the affect-augmented architecture beyond point-estimate performance metrics.

**Metrics**:
- Cumulative log predictive likelihood for affective vs. non-affective generative models
- Random-effects predictive score comparison across task variants

**Conceptual issues**: The comparison should stay on the same observation sequences and be interpreted as predictive scoring, not exact marginal evidence. The current trigger-based BMR approach (Section 8.2) is NOT suitable for this comparison because it conflates structure learning with model selection. A clean predictive comparison must treat the affective and non-affective models as competing generative models evaluated on the same observation sequences, without using affect-triggered structural changes as part of the score calculation.

**Failure mode**: If the non-affective model has comparable or higher predictive score despite worse behavioral performance, this would suggest the affective signal improves decisions through a mechanism that is not well-captured by the current generative model formulation — pointing toward the need for a tighter variational treatment of beta.

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

Primary implementation uses official `inferactively-pymdp==1.0.0` for active-inference policy inference. Project-owned trust-game modules construct the POMDP matrices, wrap `pymdp.Agent`, and maintain affective beta as an external per-partner precision tracker that modulates policy evaluation without becoming part of the generative model.

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
- `scripts/experiment/run.py` accepts repeated `--config` flags and a shared `--workers` pool so multiple experiment configs can be queued in one invocation.
- Outputs are written per config under `<output-dir>/<batch-id>/<config-name>/results.csv`, which keeps each experiment variant isolated while still allowing the scheduler to share workers across all queued replications.
- Current maintained configs are listed in `docs/experiments/manifest.md`. Use `experiments/trust/configs/h6_shallow_policy_regime.json` for the shallow policy-space regime and `experiments/trust/configs/h4_betrayal_volatility.json` for the betrayal volatility check.

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

The current repo state is no longer pre-results. The first post-restructure experiment families have been run, but several headline claims now need shallow-depth or post-switch re-analysis before they should be treated as settled:

- `h1_depth_affect_factorial`: 100 replications x 200 rounds, conditions spanning `tau={1,2,4,8}` with and without affect
- `h2_lesion_dissociation`: 100 replications x 200 rounds, lesion comparison family centered on the tau-4 base
- `h4_betrayal_recovery`: 100 replications x 120 rounds, agent-choice betrayal family on the redesigned architecture

Current scorecard:

| Hypothesis | Current evidence | Current reading | Status |
|---|---|---|---|
| H1 G compression / depth redundancy | Policy entropy rises sharply with depth while discriminating `G` spread grows slowly; deep pooled runs underperform shallow ones | Depth beyond `tau=2` is currently read as structurally redundant in the binary task | Supported |
| H2 affect as orthogonal augmentation | Pooled-across-depth affect effect is weak; targeted shallow re-analysis is pending | Judge the mechanism at `tau=1,2`, not from pooled saturated deep horizons | Needs shallow re-analysis |
| H3 lesion dissociation | Tau-4 lesion family shows a weak pooled dissociation | Expected to sharpen at `tau=1,2` where affect still influences action selection | Needs shallow re-analysis |
| H4 betrayal recovery | Tau-4 betrayal family shows a modest pooled post-switch effect | Main readout should be the post-betrayal recovery window at calibrated horizon | Needs targeted betrayal-window analysis |
| H5 partner selection | Prior partner-choice evidence exists, but the redesigned architecture needs a clean rerun | Test should focus on `tau=2` agent-choice dynamics | Needs rerun |

Interpretation:

- The old depth-compensation framing is retired. In the redesigned binary task, depth redundancy is itself a structural result that must be explained.
- The affective story is now horizon-specific: evaluate it where the policy posterior remains discriminating (`tau=1,2`), not where deep enumeration already compresses the softmax.
- Lesion and betrayal claims remain live, but the headline versions should come from shallow-depth and post-switch analyses rather than pooled tau-4 summaries.

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

**Critical analysis warning**: The trigger-based BMR formulation needs reformulation before it can be used for predictive comparison (see H6). Using affect thresholds to trigger structural changes conflates the affective signal with the model selection process, making it impossible to cleanly evaluate whether affect improves predictive score. A cleaner approach would separate the BMR machinery from the affective trigger and compare triggered vs. untriggered BMR as competing model-selection strategies, rather than embedding the trigger in the generative model itself.

### 8.3 Developmental Bootstrapping (Phase 7: Richer Tasks)

Initialize agents with no prior knowledge and simulate the full developmental trajectory: from exploration-heavy behavior (all partners are novel → low precision → high epistemic drive) through gradual affective differentiation (partners become differentially predictable) to a mature state with stable partner-specific affective profiles. Compare the learning trajectory to developmental findings on children's trust calibration.

**Critical analysis warning**: Learning rate modulation based on $\beta$ (e.g., increasing learning rate when precision is low) creates a positive feedback loop risk: low $\beta$ increases learning rate, which increases belief volatility, which increases surprise, which further lowers $\beta$. Any extension that couples $\beta$ to the learning dynamics must include stability analysis or damping to prevent runaway oscillation. The supported variational beta path is safer than a raw feedback loop because it keeps the precision signal in a bounded posterior update rather than feeding directly into learning-rate control.

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
| Phase 4 | Variational beta: supported auxiliary posterior path in Condition 12; broader formalization remains | Phase 3 | Supported |
| Phase 5 | Clinical sensitivity: revisit in richer environments | Phase 7 | **Completed** (graded game enables d>2.1 clinical effects) |
| Phase 6 | Model comparison: predictive log score comparison (H6) | Phase 4 | Planned |
| Phase 7 | Richer tasks: test whether depth curve remains flat in larger action spaces, structure learning | Phase 3 | **Completed** (graded investment trust game) |
| Phase 8 | Human data: fit to behavioral data, estimate individual-difference parameters | Phases 5-7 | Planned |
