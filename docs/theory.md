# Affect as Computational Infrastructure for Social Inference Under Active Inference

## A Theory of Per-Partner Interoceptive States as Precision Controllers in Multi-Agent Social Learning

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

What is absent across all of this work: a per-partner interoceptive/affective state that compresses interaction history into a precision signal, enables planning-depth reduction, and whose ablation reproduces the somatic marker deficit pattern.

---

## 2. The Proposed Idea

### 2.1 Core Claim

Affect is computational infrastructure that makes tractable social inference possible under realistic resource constraints. Specifically, per-partner interoceptive states — slow-timescale hierarchical representations tracking the reliability of one's social model for each partner — function as learned terminal value approximations that allow shallow explicit planning to achieve the performance of deep explicit planning.

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

**Level 3 — Per-partner affective state (slowest timescale: interoceptive integration)**
A slow state for each partner summarizing the running quality of the agent's social model of that partner — operationalized as the expected precision of the level-2 action model with respect to that partner. Updated by an exponentially-weighted moving average of prediction error magnitudes from level 2, with a long time constant that makes it resistant to single-trial fluctuations.

### 2.4 Mechanism: Affect as Terminal Value Function

In standard active inference, policy selection evaluates expected free energy over a planning horizon of depth T:

$$G(\pi) = \sum_{t=1}^{T} G_t(\pi)$$

The affective agent replaces depth-T planning with depth-τ planning (τ << T) plus an affective terminal value:

$$G(\pi) \approx \sum_{t=1}^{\tau} G_t(\pi) + V_{\text{affect}}(s_\tau, \text{partner})$$

Where $V_{\text{affect}}$ is derived from the level-3 affective state. A partner with high affective precision contributes a favorable terminal value (policies engaging with this partner are expected to go well beyond the planning horizon). A partner with low affective precision contributes either an unfavorable terminal value (avoid) or a high epistemic term (investigate).

The vmPFC lesion maps to: remove $V_{\text{affect}}$ and force the agent to rely only on explicit planning up to horizon τ. With τ = 2 and no affective compensation, the agent can only see 2 steps ahead and has no summary of what lies beyond.

### 2.5 The Three Novel Components

1. **Per-partner interoceptive state in multi-agent AIF.** Not a global mood, not a shared precision parameter — a learned affective state for each social partner that compresses that specific interaction history into a precision signal. No existing AIF model has this.

2. **Explicit planning-depth vs. performance tradeoff.** The model demonstrates that affect is the specific mechanism that shifts the cost-performance curve — allowing a 1-2 step planner to match a 5-10 step planner. Existing planning-depth optimization literature does not use affect as the mechanism.

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

### 3.4 Affective State Dynamics

The affective state $\beta_k$ for partner $k$ is updated from a signed affective charge derived from prediction error:

$$\beta_k^{(t+1)} = \lambda \beta_k^{(t)} + (1 - \lambda) \cdot \sigma(\phi(\epsilon_k^{(t)}))$$

Where:
- $\lambda \in (0.8, 0.99)$ — smoothing parameter (controls timescale; high $\lambda$ = slow, inertial updates)
- $\epsilon_k^{(t)} = o_t - \mathbb{E}[o_t | s^{(2)}_k]$ — prediction error from the level-2 social model
- $\phi(\epsilon)$ — a signed transformation that converts prediction error magnitudes into affective charge:
  - Small $|\epsilon|$ → positive charge (model is calibrating well → increase $\beta_k$)
  - Large $|\epsilon|$ → negative charge (model is miscalibrating → decrease $\beta_k$)
- $\sigma(\cdot)$ — a logistic squash that keeps the charge contribution in $[0, 1]$ before the moving average is applied

The specific form of $\phi$ could be:

$$\phi(\epsilon) = \alpha \cdot (\sigma_0^2 - \epsilon^2)$$

Where $\sigma_0^2$ is a baseline expected prediction error variance and $\alpha$ is a learning rate. When actual squared error is below baseline, affect increases; when above, it decreases. This is a precision-tracking signal — the affective state literally estimates the inverse variance of the social model's prediction errors.

### 3.5 Affect as Terminal Value

When planning with a shallow horizon τ, the affective terminal value approximation is:

$$G(\pi) \approx \sum_{t=1}^{\tau} G_t(\pi) + V_k(\beta_k)$$

Where:

$$V_k(\beta_k) = -\mu \cdot \beta_k \cdot \frac{\mathbb{E}[r \mid s^{\mathrm{terminal}}_k, a^{\mathrm{terminal}}]}{\max |r|}$$

The negative sign ensures that high affective precision reduces expected free energy only when the predicted continuation is favorable. The parameter $\mu$ scales the influence of affect relative to explicit planning, while the normalized continuation payoff keeps the terminal contribution on the same scale as the pragmatic terms accumulated within the explicit horizon.

This context-sensitive form is preferable to a flat scalar $-\mu \beta_k$ because the same partner-level affect should not blindly favor every policy involving that partner. In the implementation, affect gates the expected continuation value of the terminal action under the current belief state. High $\beta_k$ therefore amplifies credible good continuations, while low $\beta_k$ dampens them and leaves shallow planning closer to its explicit-horizon evidence.

### 3.6 The vmPFC Lesion

The computational lesion takes one of two forms:

**Full lesion:** Set $\beta_k = \beta_0$ (a fixed neutral value) for all partners and all time. The affective state exists in the model architecture but is decoupled from experience. The agent retains its level-2 social model (it "knows" partner types) but cannot use affective precision to modulate policy selection or extend its effective planning horizon.

**Precision ablation:** Set $\mu = 0$, removing the terminal value function while leaving affective state dynamics intact. The agent "feels" things about partners (the internal state updates) but these feelings have no effect on action selection. This models a disconnection between interoceptive representation and decision circuitry.

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

---

## 4. Theoretical Implications

### 4.1 Emotions as Evolved Computational Architecture

The model provides a resource-rational account of why biological agents evolved per-partner affective states rather than simply deeper planning capacity. In social environments where:

- Multiple partners must be tracked simultaneously,
- Partner strategies change unpredictably,
- Noise vastly exceeds signal (most behavioral variation is stochastic, not strategic), and
- Metabolic resources for neural computation are limited,

precision-based affective compression outperforms both (a) deep planning (too expensive to scale to many partners) and (b) simple reward averaging (discards the uncertainty information needed for efficient exploration-exploitation balancing). Affect occupies a specific niche in the computational architecture: it preserves second-order information (model reliability) that first-order summaries (average reward) discard, at a fraction of the cost of explicit deep planning.

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
