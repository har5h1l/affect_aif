# Affect as Precision Augmentation for Social Inference Under Active Inference

## A Theory of Per-Partner Metacognitive Affective States as Precision Controllers in Multi-Agent Social Learning

---

## 1. Background

### 1.1 The Computational Problem of Social Inference

Social cognition presents a fundamental computational bottleneck. When agent A interacts with agent B in a repeated game, optimal decision-making requires A to maintain a probabilistic model of B's hidden states (type, strategy, beliefs about A), simulate forward through multiple rounds of interaction, evaluate expected outcomes under each candidate policy, and select the best one. The computational cost of this planning grows exponentially with the planning horizon T — each additional step multiplies the number of policy branches by the number of possible observations and state transitions.

In multi-partner environments with 3-5 social partners whose strategies may change over time, the problem compounds further. Maintaining full recursive models of multiple agents and planning deeply over joint interaction sequences quickly becomes intractable, even for approximate inference schemes. Yet humans navigate these social environments fluently, suggesting they employ some form of computational shortcut that preserves decision quality without requiring exhaustive forward planning.

### 1.2 The Somatic Marker Hypothesis

Damasio's somatic marker hypothesis (1994) proposes that emotional signals — experienced as bodily (somatic) states — provide exactly this shortcut. Through the ventromedial prefrontal cortex (vmPFC) and its connections to the amygdala and insula, the brain generates rapid affective evaluations that bias decision-making before and below the level of deliberate reasoning.

The Iowa Gambling Task (Bechara et al., 1997) provided the key evidence. Participants choose from four card decks with different risk-reward profiles. Healthy participants develop anticipatory skin conductance responses (SCRs) — somatic markers — before choosing risky decks, even before they can explicitly articulate which decks are bad. vmPFC-lesioned patients show the critical dissociation: they can verbally describe which decks are risky (explicit knowledge is intact) but fail to develop anticipatory SCRs and continue choosing disadvantageously. The knowledge is there; the capacity to deploy it efficiently in real-time decisions is not.

This dissociation — intact knowledge but impaired deployment — is the behavioral signature that our computational model aims to reproduce in a social context.

### 1.3 Active Inference and the Free Energy Principle

Active inference (Friston, 2010; Parr, Pezzulo & Friston, 2022) provides the formal framework. Agents maintain generative models of the causes of their sensory observations and act to minimize variational free energy — an upper bound on surprise. Policy selection is governed by expected free energy (EFE), which decomposes into:

- **Pragmatic value**: the degree to which a policy's expected outcomes align with the agent's prior preferences
- **Epistemic value**: the degree to which a policy is expected to reduce uncertainty about hidden states

The agent selects policies by computing a softmax distribution over expected free energies, weighted by a precision parameter γ (policy precision) that determines how deterministic vs. exploratory the agent's behavior is.

### 1.4 Affect Under Active Inference

Hesp, Smith, Parr, Allen, Friston, and Ramstead (2021) formalized affect within deep active inference in "Deeply Felt Affect" (*Neural Computation*). Their key contributions:

- **Valence as expected precision of the action model.** A higher-level hidden state encodes the agent's estimate of how well its current generative model is performing — termed "subjective fitness." Positive valence corresponds to the expectation that one's model will continue to perform well (high expected precision); negative valence corresponds to the expectation that one's model is failing (low expected precision).

- **Affective charge as signed prediction error.** Updates to the affective state are driven by signed discrepancies between expected and realized model fitness, converting unsigned prediction errors into valenced updates that modulate future policy precision.

- **Temporal depth.** The affective state operates on a slower timescale than observation-level inference, integrating over longer windows to provide a running summary of model quality.

Critically, Hesp et al.'s model operates in a single-agent T-maze context. The affective state tracks fitness of the agent's model of its environment, not of its model of social partners.

### 1.5 Multi-Agent Active Inference: The Current State

Existing multi-agent AIF work covers several dimensions of the problem:

- **Theory of Mind as inference over others' generative models.** Friston and Frith (2015) showed that mutual prediction between agents with shared generative models produces generalized synchrony. Yoshida et al. (2008) formalized recursive mentalizing in game-theoretic settings.

- **Empathy as model coupling.** Pitliya et al. (2025) and Matsumura et al. (2024) equip AIF agents with mechanisms for modeling others' internal states to improve social coordination.

- **Trust and social learning.** Work on multi-agent social learning uses trust-like parameters to modulate how much agents learn from each other's observations and demonstrations.

- **Factorized multi-agent models.** Ruiz-Serra et al. (2025) maintain separate belief distributions over each partner's internal states, enabling strategic reasoning in multi-player games.

What is absent across all of this work: a per-partner metacognitive affective state that compresses interaction history into a precision signal, provides orthogonal augmentation beyond what explicit planning depth alone recovers, and whose ablation reproduces the somatic marker deficit pattern.

---

## 2. The Proposed Idea

### 2.1 Core Claim

Affect provides orthogonal augmentation to explicit planning in social inference. Specifically, per-partner metacognitive affective states — slow-timescale hierarchical representations tracking the reliability of one's social model for each partner — function as learned precision weights that improve policy evaluation by adding partner-specific confidence information that no amount of additional explicit lookahead recovers in the current task.

### 2.2 What the Affective State Tracks

The affective state is **not** a value function over reward history. It is a **precision estimate over social model fitness**. This distinction is critical and produces different behavioral predictions.

A value function tracks: "How much reward has B given me?" → scalar summary of payoff history.

The affective state tracks: "How well have my predictions about B been calibrating?" → precision estimate over social model accuracy.

The difference manifests in three ways:

1. **Betrayal asymmetry.** If B has been reliably cooperative for 20 rounds (high affective precision) and then defects, the affective response (precision collapse) is proportional to how confident the model was, not just how bad the outcome is. Betrayal by a trusted partner produces a larger affective signal than the same defection by an unpredictable partner, even when the material loss is identical. A value function can't capture this without additional machinery; the precision-based state gets it for free.

2. **Reliable adversaries.** An agent can have positive affective precision toward a partner it models as reliably selfish, as long as the model's predictions are accurate. "I feel clear about B" (high precision) is compatible with "B always defects" (negative expected reward). This dissociates affect from valence-as-reward-average.

3. **Uncertainty preservation.** If two partners yield the same average reward (0.6) but one is reliable (low variance) and the other oscillates between 0.0 and 1.2, the affective states differ — one signals safety, the other signals volatility. A reward average collapses this distinction. Precision-based affect preserves it, and this preservation matters for planning because it determines the balance between epistemic and pragmatic action.

### 2.3 Three-Level Architecture

The model has three hierarchical levels, each operating on a different timescale:

**Level 1 — Observations (fastest timescale: per-trial)**
Trial-by-trial outcomes of social interactions: partner's action (cooperate/defect), own payoff, any observable behavioral cues. Updated every round.

**Level 2 — Cognitive social model (medium timescale: parameter learning)**
Latent states encoding each partner's type/strategy (e.g., cooperator, reciprocator, exploiter, random) and potentially their beliefs about the agent. This is the standard theory-of-mind layer. Dirichlet parameters accumulate evidence about partner tendencies over many rounds. This is where the existing trust-as-learning-rate mechanism operates.

**Level 3 — Per-partner affective state (slowest timescale: metacognitive affective integration)**
A slow state for each partner summarizing the running quality of the agent's social model of that partner — operationalized as the expected precision of the level-2 action model with respect to that partner. Updated by an exponentially-weighted moving average of prediction error magnitudes from level 2, with a long time constant that makes it resistant to single-trial fluctuations.

### 2.4 Mechanism: Affect as Precision Weighting

In standard active inference, policy selection evaluates expected free energy over a planning horizon of depth T:

$$G(\pi) = \sum_{t=1}^{T} G_t(\pi)$$

The affective agent augments standard EFE evaluation with a partner-specific precision weight:

$$G(\pi) \approx \left(\sum_{t=1}^{\tau} G_t(\pi)\right) \cdot \left(1 + \mu \beta_k\right)$$

Where $\beta_k$ is derived from the level-3 affective state. A partner with high affective precision increases the effective precision of the EFE estimate, making the agent more decisive when its model of that partner is calibrating well. A partner with low affective precision leaves the rollout weakly weighted, preserving exploratory behavior when the partner model is unreliable. Under sophisticated inference with observation-branching, planning depth $\tau$ from 2 to 8 produces identical non-affective performance, so the affective weight contributes information orthogonal to depth rather than substituting for missing lookahead.

The vmPFC lesion maps to: remove the affective weighting and force the agent to rely only on explicit planning up to horizon $\tau$. Without the affective signal, the agent loses access to the partner-specific precision information that augments its policy evaluation.

### 2.5 The Three Novel Components

1. **Per-partner metacognitive affective state in multi-agent AIF.** Not a global mood, not a shared precision parameter — a learned affective state for each social partner that compresses that specific interaction history into a precision signal. No existing AIF model has this.

2. **Affect as orthogonal augmentation beyond planning depth.** Under sophisticated inference, explicit planning depth ($\tau = 2$ through $\tau = 8$) produces identical non-affective performance. The model demonstrates that partner-specific affective precision adds an evaluative signal that no amount of additional explicit lookahead recovers in the current task — the augmentation is orthogonal to depth, not a substitute for it.

3. **Computational vmPFC lesion in a social context.** The IGT literature shows the behavioral syndrome in single-agent gambling tasks. This model reproduces it computationally in a multi-agent setting by decoupling the affective state from policy selection.

---

## 3. Core Mathematical Framework

### 3.1 Generative Model Structure

The agent maintains a partially observable Markov decision process (POMDP) generative model for each social partner $k$:

$$P(o_{1:T}, s_{1:T}, \pi) = P(\pi) \prod_{t=1}^{T} P(o_t | s_t) P(s_t | s_{t-1}, \pi)$$

Where:
- $o_t$ — observations at time t (partner's action, payoff)
- $s_t$ — hidden states at time t (partner's type, strategy, context)
- $\pi$ — policy (sequence of actions the agent takes)

For the three-level model, hidden states factor hierarchically:

$$s_t = (s_t^{(1)}, s_t^{(2)}, s_t^{(3)})$$

- $s^{(1)}$ — current trial-level state (action on this round)
- $s^{(2)}$ — partner type/strategy (stable over blocks of trials)
- $s^{(3)}_k$ — affective state for partner $k$ (stable over longer blocks)

**State inference and variational free energy.** Belief updating over partner type (level-2 hidden state) follows the variational free energy principle. For a categorical variational distribution $q(s)$ over discrete states, the VFE-minimizing posterior is the Bayesian posterior $q^*(s) \propto P(o \mid s) P(s)$. The implementation therefore uses the **analytical solution** to VFE minimization: one-step Bayes with the likelihood matrix $A$ and transition matrix $B$, i.e. posterior = normalize(likelihood × prior), then predictive next prior = $B \times$ posterior. No iterative optimization is required because the optimum is closed-form under this generative model.

### 3.2 Expected Free Energy Decomposition

For a policy $\pi$ at future timestep $t$, expected free energy decomposes as:

$$G_t(\pi) = \underbrace{-\mathbb{E}_{Q(o_t|\pi)}[\ln P(o_t)]}_{\text{pragmatic value (negative)}} - \underbrace{\mathbb{E}_{Q(s_t|\pi)}[D_{KL}[Q(s_t|o_t, \pi) \| Q(s_t|\pi)]]}_{\text{epistemic value (negative)}}$$

Pragmatic value measures expected alignment with prior preferences (preferred observations). Epistemic value measures expected information gain — how much uncertainty about hidden states the agent expects to resolve.

### 3.3 Policy Precision and the Role of γ

Policy selection follows a softmax:

$$P(\pi) = \sigma(-\gamma \cdot G(\pi))$$

Where $\gamma$ is the policy precision (inverse temperature). Higher $\gamma$ makes the agent more deterministic (commits to the policy with lowest EFE); lower $\gamma$ makes it more exploratory.

In Hesp et al.'s framework, the affective state modulates $\gamma$. We extend this to per-partner precision:

$$\gamma_k = f(\beta_k)$$

Where $\beta_k$ is the affective state for partner $k$ — the expected precision of the agent's model of partner $k$. When the agent is selecting policies involving partner $k$, the effective policy precision is $\gamma_k$, not a global $\gamma$.

In the primary experiments in this repository, that precision-modulation path is disabled by default (`affect_modulates_precision=False`). The main empirical test therefore targets the terminal-value mechanism in Section 3.5, while per-partner $\gamma_k$ modulation remains an optional implementation path rather than the default experimental manipulation.

### 3.4 Affective State Dynamics

> **Variational Grounding.** The $\beta$ update rule below extends Hesp et al.'s (2021) variational treatment of precision dynamics to the multi-partner social setting. The signed charge mechanism converts per-partner prediction errors into precision estimates, tracking expected model fitness in the same spirit as Hesp et al.'s single-agent formulation. Phase 4 (see §4.9) targets a further formalization in which $\beta$ becomes a discrete hidden state with its own likelihood and transition model.

The affective state $\beta_k$ for partner $k$ is updated from a signed affective charge derived from prediction error:

$$\beta_k^{(t+1)} = \lambda \beta_k^{(t)} + (1 - \lambda) \cdot \sigma(\phi(\epsilon_k^{(t)}))$$

Where:
- $\lambda \in (0.5, 0.9)$ — smoothing parameter (controls timescale; higher $\lambda$ = slower, more inertial updates)
- $\epsilon_k^{(t)} = 1 - P(o_t = o_t^{\mathrm{obs}} \mid s^{(2)}_k)$ — unsigned surprise from the level-2 social model
- $\phi(\epsilon)$ — a signed transformation that converts surprise magnitudes into affective charge:
  - Small $\epsilon$ → positive charge (model is calibrating well → increase $\beta_k$)
  - Large $\epsilon$ → negative charge (model is miscalibrating → decrease $\beta_k$)
- $\sigma(\cdot)$ — a logistic squash that keeps the charge contribution in $[0, 1]$ before the moving average is applied

The specific form of $\phi$ is:

$$\phi(\epsilon) = \alpha \cdot (\sigma_0^2 - \epsilon^2)$$

Where $\sigma_0^2$ is a baseline expected surprise variance and $\alpha$ is a learning rate. In the current implementation, the default `0.25` corresponds to the squared surprise of a maximally uninformative binary partner: $(1 - 0.5)^2$. Defaults of `lambda_smooth = 0.6` and `alpha_charge = 3.0` keep affect slower than belief updates while still letting partner-specific precision estimates separate over roughly 5-10 interactions. When actual squared surprise is below baseline, affect increases; when above, it decreases. This is still a precision-tracking signal — the affective state estimates how reliable the social model has been for that partner.
Within-theory sensitivity analysis therefore varies not just $\mu$, $\lambda$, and $\alpha$, but also $\sigma_0^2$. That sweep asks whether the mechanism is under-expressed because the baseline surprise scale is badly calibrated, while keeping the update law itself fixed.

This update law extends Hesp et al.'s variational precision dynamics to the per-partner social setting. The surprise term is computed from the agent's own level-2 predictive beliefs about the observed partner action, so the affective update is belief-coupled rather than externally injected or decoupled from inference. Phase 4 targets formalizing this as a discrete hidden-state inference problem (see §4.9), which would make the precision state a first-class component of the generative model subject to the same variational machinery as partner-type inference.

### 3.5 Affect as Precision Weighting of Shallow EFE

When planning with a shallow horizon τ, the affective approximation is:

$$G(\pi) \approx \left(\sum_{t=1}^{\tau} G_t(\pi)\right) \cdot \left(1 + \mu \beta_k\right)$$

The parameter $\mu$ scales how strongly partner-specific affect changes the precision of the shallow estimate. In the implementation, the weighting is keyed to the first partner implicated by the policy rather than the terminal node of the rollout. This matters because action selection samples from first-action marginals: weighting the whole shallow-horizon EFE by the first partner's affective precision lets the partner-specific signal survive marginalization, whereas an additive scalar at the terminal node can cancel across policies that share the same first action.

### 3.6 The vmPFC Lesion

The computational lesion takes one of two forms:

**Full lesion:** Set $\beta_k = \beta_0$ (a fixed neutral value) for all partners and all time. The affective state exists in the model architecture but is decoupled from experience. The agent retains its level-2 social model (it "knows" partner types) but cannot use affective precision to augment policy evaluation.

**Precision ablation:** Set $\mu = 0$, removing the shallow-EFE weighting while leaving affective state dynamics intact. The agent "feels" things about partners (the internal state updates) but these feelings have no effect on action selection. This models a disconnection between metacognitive affective representation and decision circuitry.

Both lesion types should produce the Damasio pattern: intact level-2 posteriors (correct identification of partner types) but impaired behavioral deployment (suboptimal choices, especially in volatile conditions).

### 3.7 Relationship to Trust-as-Learning-Rate

In the existing social learning framework, trust modulates how much agent A updates its world model based on agent B's demonstrations:

$$\Delta \theta_A = \eta \cdot \tau_k \cdot \delta_k$$

Where $\tau_k$ is the trust parameter for partner $k$ and $\delta_k$ is the learning signal from $k$'s behavior.

The affective state $\beta_k$ is distinct from $\tau_k$:

- **Trust ($\tau_k$)** modulates *learning rate* — how much B's information changes A's world model
- **Affect ($\beta_k$)** modulates *policy precision* — how confidently A acts on its model of B

These dissociate. A brilliant but erratic collaborator has high trust (good information source, learn from them) but low affective precision (unpredictable in cooperative interactions, don't rely on them for joint planning). A predictable adversary has low trust (don't learn from them) but potentially high affective precision (reliable model → confident policy selection, even if the policy is avoidance).

The two quantities also interact: persistently low $\beta_k$ (chronic model misfit despite learning) could serve as a trigger for structural model revision (Bayesian Model Reduction) — a signal that the current model *form* for partner $k$ is wrong, not just its parameters.

> **Positive feedback loop warning.** In the trust-as-learning-rate formulation, reducing learning rate when surprised creates self-reinforcing cycles: an agent that down-weights surprising evidence becomes increasingly surprised because its model fails to track the true state, which in turn drives further learning-rate reduction. If $\beta_k$ were to modulate $\tau_k$ directly (low affect → low trust → slow learning → persistent model error → low affect), the same pathological loop would arise. The current implementation avoids this by keeping the $\beta \to$ policy-precision and $\tau \to$ learning-rate pathways independent, but any future integration of affect into the learning-rate channel must include a floor or reset mechanism to break the cycle.

---

## 4. Theoretical Implications

### 4.1 Emotions as Evolved Computational Architecture

The model provides an account of why biological agents evolved per-partner affective states: affect supplies information that additional planning depth does not recover. In social environments where:

- Multiple partners must be tracked simultaneously,
- Partner strategies change unpredictably,
- Noise vastly exceeds signal (most behavioral variation is stochastic, not strategic), and
- The strategically relevant contingencies are already captured within a shallow planning horizon under sophisticated inference,

precision-based affective signals add an evaluative dimension orthogonal to explicit lookahead. The empirical result is that extending planning depth from $\tau = 2$ to $\tau = 8$ produces no measurable payoff gain, yet adding partner-specific affective precision consistently improves performance. Affect therefore occupies a specific niche in the computational architecture: it preserves second-order information (model reliability) that first-order summaries (average reward) discard, and that deeper explicit planning does not reconstruct. The value of affect is not that it is cheaper than depth — it is that it encodes something depth does not.

### 4.2 Why Precision, Not Value

The model predicts that the affective state tracks model fitness (prediction accuracy), not hedonic value (reward history). This generates the following dissociable predictions:

- Agents can have high affective precision toward reliably adversarial partners (accurate model of their hostility) and low affective precision toward unreliable allies (inaccurate model of their helpfulness).
- Betrayal by a highly-predicted partner produces larger affective disruption than equivalent loss from an unpredicted partner, because the prediction error is scaled by prior precision.
- Affective recovery after a partner changes strategy tracks the speed at which the social model re-calibrates, not the speed at which rewards return to previous levels.

These predictions distinguish the model from simpler accounts (affect ≈ cached value) and connect to empirical phenomena: the disproportionate psychological impact of betrayal by trusted partners, the emotional stability that comes from accurate models even of adverse environments, and the prolonged distress when one's social world model fails.

### 4.3 Bridge to Structure Learning

Persistent low affective precision despite ongoing parameter learning constitutes evidence that the model structure is wrong. This positions the affective state as a natural trigger for Bayesian Model Reduction over social model architectures — discovering that two partners are correlated (coalition), that trust is domain-specific, or that a partner's strategy has a hidden dependency on a third party.

### 4.4 Multi-Timescale Social Cognition

The three-timescale architecture (fast observation inference, medium parameter learning, slow affective integration) maps onto known neural timescale hierarchies:

- Fast inference → sensory cortex, moment-to-moment processing
- Parameter learning → hippocampal-dependent gradual updating
- Affective integration → vmPFC/insula, slow interoceptive dynamics

The model predicts that disruption at each level produces qualitatively different behavioral deficits: level-1 damage impairs perception of social cues, level-2 damage impairs learning about partners, level-3 damage impairs efficient deployment of learned knowledge — each a distinct clinical presentation.

### 4.5 Depth Irrelevance Under Sophisticated Inference

The most important empirical update is that explicit planning depth is effectively irrelevant in the shipped binary-action trust game once all conditions use the same observation-branching sophisticated inference. In the `horizon_sweep` run, the non-affective planners are flat: `C1 = 529.26`, `C7 = 529.40`, `C6 = 529.82`, `C4 = 530.04`, and every pairwise comparison among those four conditions has `p > 0.93`.

This sharply changes the theoretical reading of the earlier depth story. The old mean-field rollout was the practical bottleneck, not horizon length itself. Once hypothetical observations are integrated correctly and partner-type beliefs are updated pathwise, extending the explicit horizon from `τ = 2` to `τ = 8` yields no measurable payoff gain in this task. So the relevant comparison is no longer "can affect approximate a deep planner?" but "does affect add something that no amount of extra explicit lookahead recovers here?" The current answer is yes.

That does not imply depth is universally irrelevant in active inference. It implies that in this particular task family, with binary actions and a small partner-type state space, sophisticated inference already captures the strategically relevant contingencies within a shallow horizon. Extra depth then mostly repeats the same local ranking rather than revealing qualitatively new futures.

### 4.6 Affect as Augmentation, Not Compensation

Under that flat depth curve, Condition 2 should not be read as a cheap approximation to Condition 1. It is better read as a planner with an additional evaluative factor: partner-specific precision weighting. Affect therefore acts as **augmentation**, not **compensation**. It changes how the shallow rollout is interpreted, rather than merely filling in missing future steps.

This yields a stronger theoretical claim than the original one. If the non-affective depth curve were steep, an affective shallow planner beating a shallow baseline could still be dismissed as a crude proxy for deeper search. The new result rules that out for the shipped task: all non-affective depths are behaviorally identical, yet the affective condition still improves payoff. The added value must therefore come from the partner-specific precision signal, not from hidden effective depth.

The `deep_affect_test` result strengthens that claim further. Condition 8 adds the same affective mechanism to the deep planner and lands at essentially the same payoff as Condition 2 (`C2` vs `C8: p = 0.94`). So affect is not rescuing shallow lookahead by approximating what the deep planner would have done anyway. It is contributing an evaluative signal that survives even when explicit planning is already deep.

The lesion result reinforces this interpretation. In the `default` run, `C3` and `C4` are exactly identical in both payoff and inferred-type accuracy. That is the expected signature of a pure affect-to-action disconnection: belief updating remains intact, but removing the affective weighting collapses the agent back onto the non-affective planner.

### 4.7 When Precision Diverges From Reward

The precision-versus-reward story is now conditional rather than uniformly null. In the default random-assignment task, Condition 2 and Condition 5 remain tied (`575.06` vs `574.42`, `d = 0.009`, `p = 0.95`). There, identifying partner type quickly tells the agent how to act for reward, so predictive calibration and reward history mostly co-move.

In `betrayal_stress`, however, the environment temporarily breaks that alignment. A previously cooperative partner switches to exploiter under scheduled betrayal, so recent reward still looks attractive while prediction error spikes. Under those conditions, Condition 2 outperforms Condition 5 (`481.88` vs `428.32`, `d = 0.59`, `p = 0.004`). This is exactly the regime where a precision-tracking signal should matter.

The theoretical distinction should therefore surface when model calibration and reward decouple. Three cases matter most:

- reliable adversaries: high precision, low raw reward
- volatile benefactors: low precision, high average reward
- betrayal transitions: reward remains cached as attractive while surprise rises abruptly

The current environment family instantiates that dissociation cleanly only in the betrayal-style setup. So H3 is best read as a boundary-condition claim: precision tracking is not a universal win, but it becomes behaviorally relevant when prediction error and reward point in different directions.

### 4.8 Empirical Reframing After the Current Runs

The completed `default`, `betrayal_stress`, `horizon_sweep`, and `deep_affect_test` runs support a narrower but stronger claim than the original "depth compensation" framing. Affect is best interpreted here as **precision augmentation**: a partner-specific signal that changes policy evaluation in ways that deeper non-affective planning does not recover in the current binary-action task.

The key empirical pattern is:

- affective weighting improves payoff over every non-affect condition
- affective weighting improves payoff by the same margin at shallow and deep horizons
- the lesion preserves partner knowledge while impairing payoff, reproducing the Damasio-style dissociation
- partner selection covaries with beta in the agent-choice setup
- the precision-versus-reward comparison is null in `default` but positive in `betrayal_stress`
- raw planning depth alone is flat once sophisticated inference replaces the old mean-field approximation

So the present theory should be read as: affect adds a partner-specific precision signal orthogonal to explicit depth in this task, not as proof that affect universally substitutes for deep lookahead in every social POMDP.

### 4.9 Discrete Variational Beta Formulation

> **Status: Implemented and Validated (Phase 4).** The discrete formulation is implemented in `affect_aif/agent/affect/discrete_state.py` and wired as Condition 12.

The current $\beta$ update rule (§3.4) extends Hesp et al.'s variational precision dynamics to the multi-partner setting using a continuous EMA formulation. Phase 4 extends this further by treating $\beta_k$ as a discrete hidden state within the generative model, with its own likelihood and transition dynamics, so that its posterior update falls out of the same categorical inference machinery used for partner-type estimation.

**The discrete formulation:**

1. **Discretize $\beta$.** Replace the continuous $\beta_k \in [0, 1]$ with a categorical hidden state $\beta_k \in \{b_1, b_2, \ldots, b_L\}$ representing $L$ evenly-spaced precision levels in $(0, 1)$. Default: $L = 5$, giving levels at approximately $\{0.17, 0.33, 0.50, 0.67, 0.83\}$.

2. **Likelihood $P(\epsilon \mid \beta)$.** The charge-based likelihood directly mirrors the continuous EMA's signed charge mechanism:

$$P(\epsilon_k^{(t)} \mid \beta_k = b_l) \propto \exp\left(\alpha(\sigma_0^2 - \epsilon^2) \cdot b_l\right)$$

When $\epsilon^2 < \sigma_0^2$ (low surprise), the charge $\alpha(\sigma_0^2 - \epsilon^2)$ is positive and higher $\beta$ levels receive more likelihood. When $\epsilon^2 > \sigma_0^2$ (high surprise), the charge is negative and lower $\beta$ levels are favored. This is the same informational content as the continuous charge mechanism, expressed as a proper likelihood function.

3. **Transition dynamics $P(\beta_k^{(t+1)} \mid \beta_k^{(t)})$.** A tridiagonal persistent transition matrix with reflecting boundaries. Self-transition probability = persistence parameter $p$ (default 0.8); remaining probability $(1-p)/2$ splits between each neighbor. Boundary states fold out-of-bounds probability back to self, making them stickier (reflecting boundary). This encodes the prior belief that precision levels change slowly.

4. **Standard Bayesian update.** Given the observed prediction error $\epsilon_k^{(t)}$, the posterior over $\beta_k$ updates as:

$$q(\beta_k^{(t)}) \propto P(\epsilon_k^{(t)} \mid \beta_k) \cdot \sum_{\beta_k^{(t-1)}} P(\beta_k^{(t)} \mid \beta_k^{(t-1)}) \, q(\beta_k^{(t-1)})$$

This is the same predict-then-correct scheme used for the level-2 partner-type inference, extended to the precision state. The point estimate $\hat{\beta}_k = \mathbb{E}_{q}[b_l]$ is used as the terminal signal for EFE weighting, identical to how the continuous $\beta$ enters the policy evaluation.

**Advantages of the discrete formulation:** (a) $\beta$ becomes a first-class hidden state within the generative model, subject to the same inference machinery as every other latent variable; (b) the precision of the precision estimate is itself represented (the width of $q(\beta_k)$), enabling the agent to distinguish "I'm confident my model is good" from "I'm unsure whether my model is good"; (c) the framework naturally accommodates structure learning — Bayesian Model Reduction over the $\beta$ state space can discover whether fewer or more precision levels are needed.

**Formal correspondence to the continuous EMA.** The continuous update $\beta_k^{(t+1)} = \lambda \beta_k^{(t)} + (1 - \lambda) \sigma(\alpha(\sigma_0^2 - \epsilon^2))$ is a point-estimate analogue of the discrete posterior mean. The smoothing parameter $\lambda$ maps to the persistence of the transition matrix (both control the timescale), and the charge amplitude $\alpha$ controls the strength of a single observation's influence (the likelihood's informativeness). In the limit $L \to \infty$ with appropriate scaling, the discrete posterior mean converges to the EMA update. In practice with $L = 5$, the qualitative behavior matches exactly: low surprise increases $\beta$, high surprise decreases it, and the timescale is governed by the transition matrix rather than the smoothing parameter.

**Empirical validation (50 seeds per condition):**

| Setting | C2 (continuous) | C12 (discrete) | C4 (baseline) | C2 vs C12 |
|---------|----------------|----------------|---------------|-----------|
| Default | 574.8 ± 81.3 | 574.7 ± 81.3 | 527.3 ± 75.1 | d=0.001, p=0.99 |
| Betrayal | 481.9 ± 76.6 | 448.1 ± 88.5 | 419.4 ± 25.9 | d=0.41, p=0.04 |

In the default (stable) condition, the two formulations produce *indistinguishable* payoffs (Cohen's d = 0.001). Both significantly outperform the no-affect baseline (d ≈ 0.6). This confirms that the discrete formulation captures the same augmentation mechanism as the continuous EMA.

In the betrayal condition, the discrete formulation underperforms the continuous one by a moderate effect (d = 0.41, p = 0.04), while still outperforming the baseline (d = 0.44, p = 0.03). The divergence arises from the transition matrix's persistence: after a sudden strategy switch, the discrete posterior shifts more slowly because the tridiagonal transition matrix constrains how far the belief can move in a single step. The continuous EMA, by contrast, applies the sigmoid-squashed charge directly, allowing larger single-step jumps. This is a *feature* of the discrete formulation — it embeds a stronger prior on precision stability — but it comes at the cost of slower betrayal adaptation.

**Implication:** The continuous EMA and discrete Bayesian formulations are equivalent representations of the same mechanism in stable environments. In volatile environments, the discrete formulation's transition dynamics impose an additional constraint (one-step moves only) that slows adaptation. The choice between them is therefore a modeling decision about the prior on precision volatility, not a difference in the underlying mechanism.

### 4.10 Clinical Parameter Space

> **Status: Sensitivity Analysis, Not a Unified Clinical Framework.** This section describes how existing model parameters map onto clinically interpretable phenotypes. These are parameter-regime explorations within the current model, not a validated clinical taxonomy. Phase 5 targets systematic sensitivity analysis with clinical interpretation.

The model's parameter space admits several regimes that correspond, at a coarse-grained level, to recognized clinical phenotypes. Each regime is defined by extremal settings of parameters that already exist in the model:

**Alexithymia ($\alpha \to 0$, blunted affective charge).**
When the charge scaling parameter $\alpha$ approaches zero, prediction errors produce negligible affective updates. The agent's $\beta_k$ values remain near their initial value $\beta_0$ regardless of interaction history. Behaviorally, this resembles the vmPFC-lesion condition (§3.6): the agent "knows" partner types at level 2 but fails to develop differentiated affective responses that modulate policy evaluation. The distinction from the full lesion is that here the affective *architecture* is intact — the agent has $\beta_k$ states that could in principle be updated — but the gain on the update channel is too low to produce functional differentiation.

**Borderline-like volatility (high $\alpha$ + low $\lambda$, volatile precision).**
High affective charge gain ($\alpha \gg 1$) combined with low smoothing ($\lambda$ near 0.5) produces an agent whose precision estimates swing rapidly in response to single-trial prediction errors. A single defection by a previously cooperative partner can collapse $\beta_k$ from near-ceiling to near-floor, and a single cooperative act can restore it. This creates unstable approach-avoidance cycling: the agent alternates between high-confidence commitment and low-confidence disengagement with the same partner, driven by trial-to-trial noise rather than sustained evidence. The behavioral signature — idealization followed by rapid devaluation — parallels descriptions of interpersonal instability.

**Depressive pessimism (low $\beta_0$, persistent low precision prior).**
When the initial precision prior $\beta_0$ is set low, the agent starts with low confidence in its model of every partner. Combined with moderate $\lambda$ (high smoothing), this creates an agent that is slow to develop trust-like affective states even when partners are reliably cooperative. The agent's policy evaluation remains weakly weighted for many rounds, producing exploratory or avoidant behavior long after a non-depressive agent would have committed to cooperative reciprocation. The computational analogue of "learned helplessness" emerges: the prior is so strong that accumulating positive evidence is insufficient to shift $\beta_k$ to a functionally decisive level within the interaction window.

**Important caveats.** These phenotype labels are heuristic mappings, not diagnostic claims. The current model lacks several features that would be required for serious clinical modeling: continuous (not discrete) action spaces, richer emotional state representations, developmental trajectories, and integration with physiological variables.

### Preliminary Empirical Finding: Binary Augmentation Architecture

A systematic exploration of the clinical parameter space (see `results/clinical_sensitivity_synthesis.md`) across four experimental designs and both precision channels found that the affective mechanism operates as a **binary augmentation** in the current trust game: having mu-weighted terminal values provides ~10% payoff improvement, but the specific beta dynamics are behaviorally degenerate. Key findings:

- **Beta dynamics differentiate correctly.** Alexithymia freezes beta at 0.5 (σ=0.001), borderline creates swings from 0.08 to 0.99 (σ=0.113), depression starts at 0.01 and recovers. The parameter-to-phenotype mapping produces the intended dynamical signatures.

- **Dynamics don't translate to behavior.** The maximum clinical effect is 0.5% of total payoff (3 points out of 576). The trust game's EFE landscape has a median best-vs-second-best policy gap of 10.83, making the softmax effectively a hard argmax. Whether beta is 0.14 or 0.94, the same policy wins.

- **Softmax saturation nullifies the precision modulation channel.** `affect_modulates_precision=True` has zero measurable effect on policy selection because the logit magnitudes are too large for the (1+beta) scaling to change the argmax. 91.5% of rounds have q_π entropy < 0.01.

- **The parameter space has clinically relevant structure; the task doesn't amplify it.** This is a task-specificity finding, not a model limitation. Richer environments with more ambiguous EFE landscapes (larger action spaces, partial observability, multiple equilibria) could unlock the clinical resolution the parameter space structurally supports.

This result reframes the clinical sensitivity roadmap: Phase 5 should follow Phase 7 (richer tasks) rather than proceeding immediately, because the current environment cannot distinguish between clinical phenotypes regardless of parameter settings.

### 4.11 Graded Trust Game: Activating the Precision Channel

The binary augmentation finding (§4.10) identified the bottleneck: the binary game's EFE landscape is too steep for any terminal value signal to change policy selection. The graded investment trust game tests whether a more ambiguous decision space unlocks the channel.

The graded game replaces binary share/keep with six investment levels per partner (0%, 20%, 40%, 60%, 80%, 100% of endowment), creating 24 total actions (6 levels × 4 partners). This expands the EFE landscape from a near-deterministic argmax to a genuinely ambiguous softmax: policy entropy rises from $< 0.01$ to $\sim 5.8$, confirming that the terminal value signal now has room to influence policy selection.

**The orthogonality table across game types:**

| Condition | Binary game payoff | Binary effect size vs C4 | Graded game payoff | Graded effect size vs C4 |
|---|---|---|---|---|
| C4 (no affect, $\tau=2$) | 530.04 | — | 10.184 | — |
| C1 (no affect, $\tau=8$) | 529.26 | $d \approx 0$ | 10.184 | $d = 0$ |
| C3 (lesioned) | 530.04 | $d = 0$ | 10.184 | $d = 0$ |
| C2 (precision tracking) | 575.06 | $d = 0.64$ | 10.394 | $d = 1.14$ |
| C5 (reward averaging) | 574.42 | $d = 0.009$ | 10.468 | $d = 1.72$ |

Two results stand out. First, the augmentation effect is *stronger* in the graded game ($d = 1.14$) than in the binary game ($d = 0.64$), confirming that the ambiguous EFE landscape amplifies the terminal value signal rather than merely exposing it. Second, reward averaging now clearly outperforms precision tracking ($d = 0.43$ in favor of C5), reversing the pattern from the binary betrayal scenario where C2 dominated.

**The affect × depth orthogonality in the binary game:**

| | No Affect | Affect (C2) |
|---|---|---|
| Shallow ($\tau=2$) | C4: 530.04 | C2: 575.06 |
| Deep ($\tau=8$) | C1: 529.26 | C8: $\approx 576$ |

Depth is irrelevant (rows are statistically identical). Affect matters (columns differ by $d \approx 0.64$). The augmentation is additive and independent of planning depth.

### 4.12 Reward Averaging vs. Precision Tracking in Ambiguous Spaces

The graded game reverses the H3 result from the binary betrayal scenario. In the binary betrayal, precision tracking beat reward averaging ($d = 0.59$, $p = 0.004$) because a cooperator-to-exploiter switch creates a regime where recent reward and prediction error diverge — reward history says "this partner is good" while the precision signal says "my model is failing." In the graded game, C5 dominates throughout, including post-betrayal ($d = -0.89$, $p < 0.0001$).

Three factors explain this reversal:

1. **Reward gradient richness.** The graded game's continuous investment levels create a rich reward gradient: investing 20% vs 80% in a cooperative partner produces proportionally different returns. Reward averaging encodes this gradient directly — "partner $k$ has been generating high/low returns" maps immediately onto "invest more/less in $k$." Precision tracking only encodes "my model of $k$ is accurate/inaccurate," which must be translated through the terminal value mechanism into an investment decision. The translation adds indirection without adding information in a task where the reward gradient is monotonically informative.

2. **Betrayal signal informativeness.** In the binary game, betrayal is all-or-nothing: a partner who was cooperating now defects. Reward averaging responds slowly because the cumulative average is dominated by many rounds of cooperation. Precision tracking responds quickly because a single unexpected defection produces large prediction error, which directly collapses $\beta_k$. In the graded game, even the reward signal responds informatively because the continuous payoff drop provides a strong gradient signal that the EMA-based reward average incorporates efficiently.

3. **Terminal value encoding.** The reward-average terminal value is $0.5 \cdot (1 + \tanh(r_k / r_{\max}))$, which maps reward history monotonically to the $[0, 1]$ signal range. This encoding directly prioritizes high-reward partners for larger investments. The precision-tracking terminal value ($\beta_k$) prioritizes partners the agent *predicts well*, not necessarily partners that give the most reward. In the graded game, where investment level is the primary decision variable, knowing "who gives more reward" is more directly useful than knowing "who I predict better."

**Theoretical implication.** Precision tracking and reward averaging occupy different niches. Reward averaging provides a better *exploitation* signal when the action space offers continuous investment gradients. Precision tracking provides a better *robustness* signal when the decision is binary (trust/don't trust) and model fitness diverges from reward history. The current graded game tests exploitation; a graded game with delayed feedback, partial observability, or non-stationary reward functions would test robustness more directly.

### 4.13 Clinical Sensitivity Restored by Task Ambiguity

The binary game's softmax saturation makes clinical parameter variations behaviorally inert: maximum clinical effect is 0.5% of total payoff. The graded game restores clinical sensitivity:

| Condition | Graded payoff | vs C4 effect size |
|---|---|---|
| C4 (no affect) | 10.134 | — |
| C9 (alexithymia, $\alpha = 0.1$) | 10.324 | $d = 2.20$ |
| C10 (borderline, $\alpha = 12, \lambda = 0.5$) | 10.353 | $d = 2.20$ |
| C11 (depression, $\beta_0 = 0.2$) | 10.331 | $d = 2.17$ |

All clinical conditions massively outperform the no-affect baseline ($d > 2.1$), a $4\times$ improvement over the binary game's negligible effects. The clinical parameter space has the structure theorized in §4.10; it just required an environment with sufficient EFE ambiguity to express it.

The within-clinical differentiation remains small (10.324–10.353 range). This suggests that the specific *form* of affective impairment matters less than whether any terminal value signal is present at all — consistent with the binary augmentation finding, but now operating at a much larger effect size. Whether the affective charge is blunted (alexithymia), volatile (borderline), or pessimistic (depression), the mu-weighted terminal value still provides substantial augmentation over raw planning. Distinguishing between clinical profiles may require richer environments (multiple equilibria, deception detection, coalition formation) where the *dynamics* of the affective signal, not just its presence, determine qualitatively different behavioral strategies.

### 4.14 Beta Does Not Approximate Value-to-Go

An empirical analysis of the graded trust game tests whether the beta terminal signal correlates with actual future payoffs from the same partner. If beta were approximating a cached value function, high beta for partner $k$ should predict higher future payoffs from $k$.

The result is a null: within-round correlations between beta and average future payoff per partner are centered at $r \approx -0.01$ (median across rounds 20–180), with no round window reaching significance after correction. A beta tercile analysis confirms the pattern: agents with high beta ($\bar{\beta} = 0.616$) and low beta ($\bar{\beta} = 0.468$) for a given partner experience statistically indistinguishable future payoffs ($d = -0.03$, $p = 0.21$).

This null is *predicted* by the theory. Beta tracks prediction accuracy (§3.4), not reward quality. A cooperator who is reliably cooperative and an exploiter who is reliably exploitative can both produce high beta — the agent predicts both well. Conversely, a random partner yields mediocre beta regardless of whether random-partner payoffs happen to be above or below average.

The null therefore validates the orthogonal augmentation claim from the opposite direction. Beta contributes information orthogonal to value history, not an approximation to it. If beta correlated strongly with value-to-go, the augmentation could be dismissed as a learned value cache that duplicates what deeper planning would discover. The absence of correlation confirms that beta encodes a genuinely different signal — model fitness — that improves policy evaluation through a channel that value history alone does not access.

### 4.15 Synthesis: The Paper Story Across Both Game Types

The binary and graded trust games together tell a more complete story than either alone:

1. **Binary game establishes the core claim.** Affect provides orthogonal augmentation beyond planning depth. Under sophisticated inference, depth $\tau = 2$ through $\tau = 8$ is flat; affect adds $\sim 46$ payoff points at every depth. The lesion reproduces the Damasio dissociation. Precision tracking separates from reward averaging only under betrayal stress.

2. **Graded game tests the mechanism's generality.** Moving from 8 to 24 actions activates the precision channel that was structurally inert in the binary game. Both terminal value mechanisms (precision and reward) provide strong augmentation ($d > 1$), but reward averaging dominates because the continuous investment gradient makes reward history directly decision-relevant. This is not a failure of precision tracking — it is a task-specificity result: the graded game's monotonic reward structure favors the simpler signal.

3. **The precision tracking mechanism's value is modelability.** Its parameters ($\alpha$, $\lambda$, $\beta_0$) map naturally onto clinically interpretable constructs (alexithymia, borderline volatility, depressive pessimism) in ways that reward averaging's single EMA parameter does not. This makes precision tracking the right mechanism for clinical and neuroscientific modeling, even when reward averaging achieves higher raw performance in a specific task.

4. **The graded game unlocks the clinical sensitivity that the binary game cannot provide.** Clinical parameter variations produce effect sizes above $d = 2$ in the graded game, compared to negligible effects in the binary game. This validates the theoretical prediction that the parameter space has clinically relevant structure — it just needs an environment with sufficient decision ambiguity to express it.

---

## 5. Key References

- Bechara, A., Damasio, A. R., Damasio, H., & Anderson, S. W. (1994). Insensitivity to future consequences following damage to human prefrontal cortex. *Cognition*, 50, 7-15.
- Bechara, A., Damasio, H., Tranel, D., & Damasio, A. R. (1997). Deciding advantageously before knowing the advantageous strategy. *Science*, 275(5304), 1293-1295.
- Friston, K. J., & Frith, C. D. (2015). A Duet for one. *Consciousness and Cognition*, 36, 390-405.
- Friston, K. J., Lin, M., Frith, C. D., Pezzulo, G., Hobson, J. A., & Ondobaka, S. (2017). Active inference, curiosity and insight. *Neural Computation*, 29(10), 2633-2683.
- Hesp, C., Smith, R., Parr, T., Allen, M., Friston, K. J., & Ramstead, M. J. D. (2021). Deeply felt affect: The emergence of valence in deep active inference. *Neural Computation*, 33(2), 398-446.
- Joffily, M., & Coricelli, G. (2013). Emotional valence and the free-energy principle. *PLoS Computational Biology*, 9(6), e1003094.
- Matsumura, M., et al. (2024). Active inference with empathy mechanism for socially behaved artificial agents. *Artificial Life*, 30(2), 277-295.
- Parr, T., Pezzulo, G., & Friston, K. J. (2022). *Active Inference: The Free Energy Principle in Mind, Brain, and Behavior*. MIT Press.
- Pitliya, R., et al. (2025). Empathy modeling in active inference agents for perspective-taking and alignment. arXiv:2602.20936.
- Ruiz-Serra, J., Sweeney, K., & Harré, M. S. (2025). Factorised active inference for strategic multi-agent interactions. *AAMAS*.
- Seth, A. K. (2013). Interoceptive inference, emotion, and the embodied self. *Trends in Cognitive Sciences*, 17(11), 565-573.
- Seth, A. K., & Friston, K. J. (2016). Active interoceptive inference and the emotional brain. *Philosophical Transactions of the Royal Society B*, 371(1708), 20160007.
- Smith, R., Schwartenbeck, P., Parr, T., & Friston, K. J. (2020). An active inference approach to modeling structure learning. *Frontiers in Computational Neuroscience*, 14, 5.
- Smith, R., et al. (2021). A Bayesian computational model reveals a failure to adapt interoceptive precision estimates across depression, anxiety, eating, and substance use disorders. *PLoS Computational Biology*, 17(3), e1008484.
- Yoshida, W., Dolan, R. J., & Friston, K. J. (2008). Game theory of mind. *PLoS Computational Biology*, 4(12), e1000254.
