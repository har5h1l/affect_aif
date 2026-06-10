# Affect as Precision Augmentation for Social Inference Under Active Inference

## A Theory of Per-Partner Metacognitive Affective States as Precision Controllers in Multi-Agent Social Learning

## Current Trust-Game Status

The supported trust-family experiments now use the action-dependent stance
redesign described in `docs/overview/pomdp.md` and
`docs/overview/pomdp.md`.

For the current canonical hypothesis surface, use
`docs/overview/hypotheses.md`. That file organizes the project around H0-H8
behavior cards.

- The hidden social state is `partner type × partner stance`, not partner type plus exploiter phase.
- Stance is endogenous: partners maintain a posterior over the agent's character and map that posterior to `trusting`, `neutral`, or `hostile`.
- The agent's generative model includes an explicit stance factor and action-dependent `B_stance`, so deeper planning is now structurally informative.
- The current claim is: depth matters in action-dependent social environments,
  and per-partner affective precision adds orthogonal value beyond that depth.

Implementation note (2026-05-05): the shipped code uses official `pymdp.Agent`
instances, HESP-style discrete beta levels `[0.5, 0.67, 1.0, 1.5, 2.0]`, two
observation modalities (`o_action`, `o_payoff`), and the trust-game
hidden/control structure `type × stance` plus `own_action`. The supported
affective path follows `gamma_k = gamma_base / E[beta_k]`.

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

These approaches define three distinct computational strategies for social cognition that form a triple dissociation:

1. **Outside-in empathy** (Pitliya et al., 2025; Matsumura et al., 2024): Agents couple their generative models so that one agent's affective or perceptual states directly inform another's inference. The computational direction flows from partner to self.

2. **Cognitive theory of mind** (Yoshida et al., 2008; Friston & Frith, 2015): Agents maintain an explicit model of the partner's inference process, recursively simulating their beliefs and policies.

3. **Inside-out metacognitive monitoring** (this work): The agent tracks the reliability of its own predictive model for each partner, without modeling the partner's internal states or coupling to their generative process.

This triple dissociation — outside-in empathy, cognitive ToM, and inside-out precision monitoring — carves the space of social inference mechanisms at its computational joints. What is absent across the existing approaches: a per-partner metacognitive affective state that compresses interaction history into a precision signal, provides orthogonal augmentation beyond what explicit planning depth alone recovers, and whose ablation reproduces the somatic marker deficit pattern.

---

## 2. The Proposed Idea

### 2.1 Core Claim

Affect provides orthogonal augmentation to explicit planning in social inference. Specifically, per-partner metacognitive affective states — slow-timescale auxiliary summaries tracking the reliability of one's social model for each partner — function as learned policy-precision signals that improve decision-making by adding partner-specific confidence information that explicit lookahead alone does not recover.

### 2.2 What the Affective State Tracks

The affective state is **not** a value function over reward history. It is a **precision estimate over social model fitness**. This distinction is critical and produces different behavioral predictions.

A value function tracks: "How much reward has B given me?" → scalar summary of payoff history.

The affective state tracks: "How well have my predictions about B been calibrating?" → precision estimate over social model accuracy.

The difference manifests in three ways:

1. **Betrayal asymmetry.** If B has been reliably cooperative for 20 rounds (high affective precision) and then defects, the affective response (precision collapse) is proportional to how confident the model was, not just how bad the outcome is. Betrayal by a trusted partner produces a larger affective signal than the same defection by an unpredictable partner, even when the material loss is identical. A value function can't capture this without additional machinery; the precision-based state gets it for free.

2. **Reliable adversaries.** An agent can have positive affective precision toward a partner it models as reliably selfish, as long as the model's predictions are accurate. "I feel clear about B" (high precision) is compatible with "B always defects" (negative expected reward). This dissociates affect from valence-as-reward-average.

3. **Uncertainty preservation.** If two partners yield the same average reward (0.6) but one is reliable (low variance) and the other oscillates between 0.0 and 1.2, the affective states differ — one signals safety, the other signals volatility. A reward average collapses this distinction. Precision-based affect preserves it, and this preservation matters for planning because it determines the balance between epistemic and pragmatic action.

### 2.3 Three-Level Architecture

The current shipped experiments are best read as a single hidden-state inference problem plus an auxiliary affective summary:

**Level 1 — Directly observed task context (fastest timescale: per-trial)**
Partner identity / interaction context and trial outcome are task-given. The agent observes which partner is being played and what happened on that round; context is not a latent factor in the main experiments.

**Level 2 — Cognitive social model (medium timescale: partner inference)**
The main hidden state is each partner's `type x stance`: a strategy-like
partner type (cooperator, reciprocator, exploiter, random) and the partner's
hidden disposition toward the focal agent (trusting, neutral, hostile).
Optional Dirichlet learning hooks can accumulate evidence about likelihoods,
but the shipped trust runtime does not maintain a separate trust scalar.

**Level 3 — Per-partner affective summary (slowest timescale: metacognitive affective integration)**
A slow auxiliary state for each partner summarizes the running quality of the agent's social model of that partner — operationalized as an expected precision-like signal tied to level-2 prediction error. It modulates policy evaluation, but it is not treated as a fully symmetric hidden-state factor in the main generative model.

### 2.4 Mechanism: Affect as Precision Weighting

In standard active inference, policy selection evaluates expected free energy over a planning horizon of depth T:

$$G(\pi) = \sum_{t=1}^{T} G_t(\pi)$$

The affective runtime augments standard policy inference with a partner-specific precision:

$$P(\pi \mid k) = \sigma(-\gamma_k G(\pi)), \qquad \gamma_k = \frac{\gamma_{\mathrm{base}}}{\mathbb{E}[\beta_k]}$$

Where $\beta_k$ is derived from the level-3 affective state. In the HESP inverse-beta convention used here, lower expected beta raises policy precision and makes the agent more decisive; higher expected beta lowers precision and preserves exploratory behavior. The key point is that the partner-specific signal changes the native pymdp policy posterior without becoming another hidden-state factor in the trust POMDP.

The vmPFC lesion maps to: keep the beta tracker available but decouple it from policy precision. Without that deployment pathway, the agent loses access to the partner-specific precision information that augments its policy evaluation.

### 2.5 The Three Novel Components

1. **Per-partner metacognitive affective state in multi-agent AIF.** Not a global mood, not a shared precision parameter — a learned affective state for each social partner that compresses that specific interaction history into a precision signal. No existing AIF model has this.

2. **Affect as precision-weighted deployment.** Partner-specific affective
   precision adds an evaluative signal to policy selection. Its effect is gated
   by policy-space openness: when the policy posterior is saturated, beta can
   move without changing behavior; when several policies remain live, precision
   can change action or partner choice.

3. **Computational vmPFC lesion in a social context.** The IGT literature shows the behavioral syndrome in single-agent gambling tasks. This model reproduces it computationally in a multi-agent setting by decoupling the affective state from policy selection.

---

## 3. Core Mathematical Framework

### 3.1 Generative Model Structure

The agent maintains a partially observable Markov decision process (POMDP) generative model for each social partner $k$:

$$P(o_{1:T}, s_{1:T}, \pi) = P(\pi) \prod_{t=1}^{T} P(o_t | s_t) P(s_t | s_{t-1}, \pi)$$

Where:
- $o_t$ — observations at time t (partner's action, payoff)
- $s_t$ — hidden states at time t (partner's type, strategy)
- $\pi$ — policy (sequence of actions the agent takes)

For the current experiments, each partner-local POMDP uses the factorization
specified in `docs/overview/pomdp.md`:

$$s_t = (s_{\mathrm{type}}, s_{\mathrm{stance}}, s_{\mathrm{own}})$$

- $s_{\mathrm{type}}$ — partner behavioral type
- $s_{\mathrm{stance}}$ — the partner's disposition toward the agent
- $s_{\mathrm{own}}$ — deterministic bookkeeping for the agent's own executed action

**Simulation boundary.** The focal agent runs this POMDP via official
`pymdp.Agent`. Ground-truth partners are environment-side parameterized policies
that sample from the same type-by-stance cooperation tables and update stance
reactively from the focal agent's actions; they do not run reciprocal active
inference or partner-local affective precision. Reciprocal multi-agent AIF is
planned future work (`pomdp_spec.md` §13).

Partner identity / interaction context is directly observed, and the affective
state $\beta_k$ is tracked as an auxiliary per-partner summary that influences
policy evaluation without becoming a POMDP hidden-state factor.

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

$$\gamma_k = \frac{\gamma_{\mathrm{base}}}{\mathbb{E}[\beta_k]}$$

Where $\beta_k$ is the HESP-style rate parameter for partner $k$. Lower
$\beta_k$ means higher expected policy precision, and higher $\beta_k$ means
lower expected policy precision. When the agent is selecting policies involving
partner $k$, the effective policy precision is partner-local rather than purely
global.

In the supported native runtime, this precision-modulation path is the
affective deployment mechanism.

### 3.4 Affective State Dynamics

> **Variational grounding (theory).** The $\beta$ update rule below extends Hesp et al.'s (2021) variational treatment of precision dynamics to the multi-partner social setting. The signed charge mechanism converts per-partner prediction errors into precision estimates, tracking expected model fitness in the same spirit as Hesp et al.'s single-agent formulation. The **shipped** code path uses the discrete filter in task-local external precision tracker only; a separate variational auxiliary-state implementation is future work.

The affective state $\beta_k$ for partner $k$ is updated from a signed
affective charge derived from prediction error. The supported implementation is
the discrete predict-then-correct filter described below; older continuous EMA
equations are archived prototype intuition only.

The current update uses:

- $\epsilon_k^{(t)} = -\log P(o_t = o_t^{\mathrm{obs}} \mid s_k)$ —
  surprisal from the partner-local social model
- $\phi(\epsilon)$ — a signed transformation that converts surprise magnitudes
  into affective charge:
  - small $\epsilon$ -> positive charge, favoring lower beta and higher policy
    precision
  - large $\epsilon$ -> negative charge, favoring higher beta and lower policy
    precision

The specific form of $\phi$ is:

$$\phi(\epsilon) = \alpha \cdot (\sigma_0^2 - \epsilon^2)$$

Where $\sigma_0^2$ is a baseline expected surprise variance and $\alpha$ is a learning rate. The default `sigma_0_sq = (-\log 0.5)^2` corresponds to the squared surprisal of a maximally uninformative binary prediction. Defaults of `beta_persistence = 0.8` and `alpha_charge = 3.0` keep affect slower than belief updates while still letting partner-specific precision estimates separate over repeated interactions. When actual squared surprise is below baseline, expected policy precision increases through lower beta; when above, expected policy precision decreases through higher beta. This is still a precision-tracking signal — the affective state estimates how reliable the social model has been for that partner.
Within-theory sensitivity analysis therefore varies `alpha_charge`, `sigma_0_sq`, `beta_persistence`, and `initial_beta`. That sweep asks whether the mechanism is under-expressed because the surprise scale or beta dynamics are badly matched to the task.

This update law extends Hesp et al.'s variational precision dynamics to the
per-partner social setting. The surprise term is computed from the agent's own
partner-local `type x stance` predictive beliefs about the observed partner
action, so the affective update is belief-coupled rather than externally
injected or decoupled from inference. The supported discrete beta tracker
formalizes this auxiliary state with explicit posterior updates, but beta
remains outside the POMDP hidden-state factors.

### 3.5 Affect as Partner-Local Policy Precision

When planning for partner $k$, the native runtime sets the partner-local `pymdp.Agent` precision before policy inference:

$$\gamma_k = \frac{\gamma_{\mathrm{base}}}{\mathbb{E}_{q(\beta_k)}[\beta_k]}$$

The trust task owns the beta posterior and the partner bank; official pymdp owns `infer_policies(...)` and `infer_states(...)`. This keeps affect outside the generative-model hidden-state factors while still letting partner-specific model fitness shape the policy posterior.

### 3.6 The vmPFC Lesion

The computational lesion takes one of two forms:

**Full lesion:** Set $\beta_k = \beta_0$ (a fixed neutral value) for all partners and all time. The affective state exists in the model architecture but is decoupled from experience. The agent retains its partner-local social model (it can infer type and stance) but cannot use affective precision to augment policy evaluation.

**Precision ablation:** Use lesion mode `decouple`, leaving affective state dynamics intact while forcing `gamma_k = gamma_base` at policy selection. The agent "feels" things about partners (the internal state updates) but these feelings have no effect on action selection. This models a disconnection between metacognitive affective representation and decision circuitry.

Both lesion types should produce the Damasio pattern: intact or broadly similar
partner-local posteriors, but impaired behavioral deployment in regimes where
H0 says precision can move policy.

### 3.7 Relationship to Trust-as-Learning-Rate

Trust-as-learning-rate is useful theoretical contrast, but it is not a current
implemented scalar in the supported trust-game runtime. In that broader social
learning formulation, trust would modulate how much agent A updates its world
model based on agent B's demonstrations:

$$\Delta \theta_A = \eta \cdot \tau_k \cdot \delta_k$$

Where $\tau_k$ is the trust parameter for partner $k$ and $\delta_k$ is the learning signal from $k$'s behavior.

The affective state $\beta_k$ should be kept distinct from such a future
$\tau_k$:

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

### 4.5 Policy Openness as the First Gate

The current evidence supports a gate claim rather than a global reward claim.
Affective precision can only become behaviorally visible when the policy
posterior has room to move. In saturated binary settings, beta can update while
the chosen action remains effectively fixed. In graded, volatile, noisy, or
agent-choice regimes, multiple policies remain live enough for
`gamma_k = gamma_base / E[beta_k]` to change the policy posterior.

This is the H0 result. Openness is necessary, but not sufficient: the graded
choice regime shows lower entropy and better payoff with affect, while the
graded betrayal regime shows lower entropy and worse payoff. Precision can guide
deployment when the model is useful; it can also sharpen a bad deployment state
when the model is wrong.

### 4.6 Affect as Deployment, Not Reward

The current H1/H2 evidence supports the deployment interpretation, but with
different evidential strength across the two cards:

- H1: the corrected post-fix smoke readout shows partner-specific precision
  tracking predictive reliability more strongly than realized payoff, including
  active-encounter and partial-correlation diagnostics. This is the current
  model-fitness diagnostic, but it still requires confirmation-scale evidence
  before carrying a manuscript-level claim.
- H2: lesion/no-affect preserves much of the partner inference surface while
  changing policy entropy and behavior in the open graded-choice regime.

The clean theoretical claim is therefore not "affect makes the agent richer."
It is: affect estimates how reliable the agent's model of a partner currently
is, then changes how strongly that model is deployed into policy selection.
This explains why predictable exploiters can yield high precision without
becoming attractive partners.

### 4.7 Stress as a Boundary Condition

The betrayal/stress results are not a clean affective recovery win. They show
that volatility exposes both the power and risk of the precision pathway.

In the 30-seed H3 confirmation, affect lowered policy entropy and reduced
returns to the switched partner, but it also produced worse whole-run payoff and
did not show a confirmed conditional-return payoff advantage. The proper H3
read is therefore a boundary condition: stress can reveal precision-driven
misdeployment, especially when the agent confidently acts on an outdated or
incorrect post-switch model.

This result strengthens the mechanism claim in a different way than originally
expected. A null policy channel would leave entropy, reallocation, and wrong
deployment flat. Instead, the channel moves behavior, but not always in the
payoff-improving direction.

### 4.8 Social Choice and Perturbation Dynamics

Partner-specific precision also changes social choice. In H4, partner-selection
distributions and policy entropy shift while whole-run payoff remains nearly
flat. That is expected: approach, avoidance, probing, and return behavior are
more direct readouts of partner-local precision than total reward.

H5 should be read as perturbation dynamics rather than clinical validation.
Clinical-like parameter variants separate in beta range, entropy,
partner-selection behavior, and payoff ordering, but the current payoff tests
are underpowered. The labels are shorthand for computational regimes:
blunted updating, volatile updating, pessimistic initial precision, and slow
updating. They are not diagnostic claims.

### 4.9 Discrete Beta Formulation

> **Status.** A separate variational-state runtime is future work. The discrete formulation below is implemented by the native affective runtime through `DiscreteBetaState`.

The narrative in §3.4 above described the charge signal. The **implemented**
$\beta$ dynamics are the discrete categorical update in the following bullets;
partner type and stance remain the primary hidden-state factors.

**The discrete formulation:**

1. **Discretize $\beta$.** Replace the continuous $\beta_k$ with a categorical auxiliary state $\beta_k \in \{b_1, b_2, \ldots, b_L\}$ outside the POMDP hidden-state factors. Default: `L = 5`, with support `[0.5, 0.67, 1.0, 1.5, 2.0]`.

2. **Likelihood $P(\epsilon \mid \beta)$.** The charge-based likelihood directly mirrors the continuous EMA's signed charge mechanism:

$$P(\epsilon_k^{(t)} \mid \beta_k = b_l) \propto \exp\left(\alpha(\sigma_0^2 - \epsilon^2) / b_l\right)$$

When $\epsilon^2 < \sigma_0^2$ (low surprise), the charge $\alpha(\sigma_0^2 - \epsilon^2)$ is positive and lower $\beta$ levels receive more likelihood, sharpening policy precision through `gamma_base / E[beta_k]`. When $\epsilon^2 > \sigma_0^2$ (high surprise), the charge is negative and higher $\beta$ levels are favored, softening policy precision. This is the same informational content as the continuous charge mechanism, expressed as a proper likelihood function.

3. **Transition dynamics $P(\beta_k^{(t+1)} \mid \beta_k^{(t)})$.** A tridiagonal persistent transition matrix with reflecting boundaries. Self-transition probability = persistence parameter $p$ (default 0.8); remaining probability $(1-p)/2$ splits between each neighbor. Boundary states fold out-of-bounds probability back to self, making them stickier (reflecting boundary). This encodes the prior belief that precision levels change slowly.

4. **Standard Bayesian update.** Given the observed prediction error $\epsilon_k^{(t)}$, the posterior over $\beta_k$ updates as:

$$q(\beta_k^{(t)}) \propto P(\epsilon_k^{(t)} \mid \beta_k) \cdot \sum_{\beta_k^{(t-1)}} P(\beta_k^{(t)} \mid \beta_k^{(t-1)}) \, q(\beta_k^{(t-1)})$$

This is the same predict-then-correct scheme used for partner-local state
inference, extended to the precision state. The point estimate
$\hat{\beta}_k = \mathbb{E}_{q}[b_l]$ sets partner-local policy precision
through `gamma_k = gamma_base / hat(beta)_k`.

**Advantages of the discrete formulation:** (a) $\beta$ has an explicit posterior rather than a pure point estimate; (b) the precision of the precision estimate is itself represented (the width of $q(\beta_k)$), enabling the agent to distinguish "I'm confident my model is good" from "I'm unsure whether my model is good"; (c) the framework naturally accommodates structure learning — Bayesian Model Reduction over the $\beta$ state space can discover whether fewer or more precision levels are needed.

**Relation to archived EMA prototypes.** Older prototype docs used a continuous
moving-average beta update. The supported runtime instead uses the categorical
posterior above. Low surprise shifts mass toward lower beta levels; high
surprise shifts mass toward higher beta levels. The transition matrix controls
timescale through `beta_persistence`.

Archived continuous-EMA and standalone variational-beta comparisons are
historical context only. The supported current path is the discrete beta tracker
inside the trust runtime, deployed around official `pymdp.Agent` policy
inference.

### 4.10 Clinical Parameter Space

> **Status: Sensitivity Analysis, Not a Unified Clinical Framework.** This section describes how existing model parameters map onto clinically interpretable phenotypes. These are parameter-regime explorations within the current model, not a validated clinical taxonomy. Phase 5 targets systematic sensitivity analysis with clinical interpretation.

The model's parameter space admits several regimes that correspond, at a coarse-grained level, to recognized clinical phenotypes. Each regime is defined by extremal settings of parameters that already exist in the model:

**Alexithymia ($\alpha \to 0$, blunted affective charge).**
When the charge scaling parameter $\alpha$ approaches zero, prediction errors produce negligible affective updates. The agent's $\beta_k$ values remain near their initial value $\beta_0$ regardless of interaction history. Behaviorally, this resembles the vmPFC-lesion condition (§3.6): the agent "knows" partner types at level 2 but fails to develop differentiated affective responses that modulate policy evaluation. The distinction from the full lesion is that here the affective *architecture* is intact — the agent has $\beta_k$ states that could in principle be updated — but the gain on the update channel is too low to produce functional differentiation.

**Borderline-like volatility (high $\alpha$, volatile precision).**
High affective charge gain ($\alpha \gg 1$) produces an agent whose precision
estimates swing rapidly in response to single-trial prediction errors. This can
create unstable approach-avoidance cycling: the agent alternates between
high-confidence commitment and low-confidence disengagement with the same
partner, driven by trial-to-trial evidence rather than sustained calibration.

**Depressive pessimism (high initial beta, persistent low precision prior).**
When the initial beta prior is high, the agent starts with low policy precision
for every partner. Combined with high beta persistence, this creates an agent
that is slow to develop confident partner-local deployment even when partners
are reliably cooperative. Current H6 configs instantiate this with
`initial_beta = 2.0`.

**Important caveats.** These phenotype labels are heuristic mappings, not diagnostic claims. The current model lacks several features that would be required for serious clinical modeling: continuous (not discrete) action spaces, richer emotional state representations, developmental trajectories, and integration with physiological variables.

### 4.11 Predictive and Comparative Extensions

Predictive model comparison remains useful future work, but it is separate from
the active H0-H8 evidence spine. A clean comparison should score matched
observation sequences and avoid mixing reward optimization with predictive
fitness. Global beta is now the maintained H3 locality ablation. Non-AIF
control-policy comparisons and richer model-selection variants remain future
work unless rerun and documented under the current architecture.

### 4.12 Task Generalization and Perturbation Tests

Cross-game and phenotype-inspired perturbation tests remain useful future extensions,
but the active spine now evaluates them through the H0-H8 behavior cards:
openness first, model fitness second, deployment third, then locality/global
precision, social allocation, timescale/volatility, perturbation dynamics,
signal-source alternatives, and observation-noise robustness. Any
phenotype-inspired interpretation must first
show the intended beta/precision dynamics and then show behavior only in regimes
where H0 confirms policy-space openness.

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
- Kass, R. E., & Raftery, A. E. (1995). Bayes factors. *Journal of the American Statistical Association*, 90(430), 773-795.
- Stephan, K. E., Penny, W. D., Daunizeau, J., Moran, R. J., & Friston, K. J. (2009). Bayesian model selection for group studies. *NeuroImage*, 46(4), 1004-1017.
- Rigoux, L., Stephan, K. E., Friston, K. J., & Daunizeau, J. (2014). Bayesian model selection for group studies—revisited. *NeuroImage*, 84, 971-985.
