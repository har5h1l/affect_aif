# POMDP Specification v4 — External Precision Tracking

Specifies the generative model in standard pymdp A/B/C/D/E format.

---

## 1. Overview

N agents interact in a repeated trust game with turn-taking. Each round, one focal agent selects an action (cooperate/defect, and optionally which partner to engage). All agents run active inference — behavioral "types" are inferred social categories in the focal agent's model; in simulations, partner behavior is shaped by internal parameterizations including preference temperature, planning horizon, and policy noise. Each agent maintains per-partner beliefs over (type, stance) via the POMDP, plus a per-partner precision tracker (beta) that operates outside the generative model.

Precision tracking reads social prediction errors and modulates policy precision, without being part of the POMDP state space. This matches Hesp et al.'s hierarchical approach where precision is inferred from inference dynamics rather than from a dedicated sensory channel.

**Version history**: v1 had F=4, M=3 with non-standard payoff. v2 dropped payoff (M=2). v3 restores payoff as a proper modality via s_own factor and re-parameterizes beta to match Hesp's convention. v4 removes beta from POMDP state space and intero from observations; precision tracking becomes an external module operating on inference dynamics. The current implementation also follows the factorized-control convention from the reference trust notebook.

---

## 2. Hidden State Factors (F=3)

| Factor | Symbol | States | Controllable? | Notes |
|--------|--------|--------|---------------|-------|
| Partner type | `s_type` | cooperator, reciprocator, exploiter, random (4) | No | Fixed behavioral tendency. Small stochastic drift (p_switch = 0.05). |
| Partner stance | `s_stance` | trusting, neutral, hostile (3) | **Yes** | Partner's disposition toward the agent. Evolves based on agent's actions. Agent influences via actions, cannot observe directly. |
| Own action | `s_own` | cooperate, defect (2) | Yes | Deterministic: tracks agent's own last action. Needed for payoff modality. |

**Note on s_own**: This is not a substantive latent variable. It is a deterministic bookkeeping state included so that payoff can be represented as a standard factorized A-matrix dependency: A[1] = P(o_payoff | s_own, s_type, s_stance). The agent always knows its own action; s_own simply makes this knowledge available to the observation model in pymdp-standard form.

**Key structural property**: Stance is the **partner's** disposition toward the **agent** (a hidden state the agent must infer), not the agent's own attitude. The agent influences stance through its actions (cooperating builds trust, defecting destroys it), but cannot directly observe or control it.

Joint state space per partner: 4 types x 3 stances x 2 own_action = 24 states.

---

## 3. Observation Modalities (M=2)

| Modality | Symbol | Outcomes | Depends on |
|----------|--------|----------|------------|
| Partner action | `o_action` | cooperate, defect (2) | type, stance |
| Payoff | `o_payoff` | -1, 1, 3, 5 (4 discrete levels) | own_action, type, stance (partner action marginalized) |

**Payoff**: A proper modality with A[1] conditioned on (s_own, s_type, s_stance). The partner's actual action is marginalized through the type x stance cooperation probabilities. This preserves the Prisoner's Dilemma temptation structure at horizon 1 while trust-building via stance dynamics emerges at horizon >= 2.

**Note on payoff representation**: In the environment, realized payoff is deterministically derived from joint actions. In the agent's generative model, payoff is instead treated as a modality conditionally generated from own action and latent partner disposition, with partner action marginalized through the cooperation table. This is a reduced generative representation that preserves standard factorized pymdp structure while retaining the expected incentive landscape. It is not a claim that payoff is stochastic in the real game.

---

## 4. Control Factors

The current trust-game implementation uses factorized controls
inside each partner-local `pymdp.Agent`. Partner choice is handled outside the
partner-local POMDP by evaluating candidate policies for each partner in
`tasks.trust.runtime.select_decision(...)`.

| Factor | Symbol | Actions | Controls |
|--------|--------|---------|----------|
| Partner choice | external selector | current partner in random mode; N partners in agent-choice mode | which partner receives the executed interaction |
| Stance control | `pi_stance` | action/investment levels | `s_stance` transitions via action-dependent B |
| Own action | `pi_own` | action/investment levels | `s_own` deterministic update and realized payoff |

For both random and agent-choice runs, the partner-local instantaneous control
shape is `[1, num_social_actions, num_social_actions]`. Binary games have
`num_social_actions = 2`; graded games use the configured number of investment
levels. In agent-choice mode, the runtime loops over partners, applies the
candidate partner's `gamma_k`, and then encodes the executed environment action
as `(partner, stance_action, own_action)`.

Payoff and outcome updates use the executed `own` action. Rollout uses the
stance-control column for generative stance transitions during planning, while
partner-observed stance dynamics use the executed own action. This keeps the
POMDP matrices compatible with the reference notebook while using official
`pymdp` as the runtime dependency.

The older single-flat-action graded control path is no longer the supported
trust-game semantics.

---

## 5. A Matrices (Observation Likelihoods)

### A[0]: P(o_action | s_type, s_stance)

Shape: `(2, 4, 3)` — uniform over s_own.

Each entry is the probability that the partner cooperates given their type and stance:

|  | trusting | neutral | hostile |
|---|---|---|---|
| cooperator | 0.95 | 0.80 | 0.55 |
| reciprocator | 0.90 | 0.70 | 0.30 |
| exploiter | 0.70 | 0.35 | 0.10 |
| random | 0.60 | 0.50 | 0.35 |

The row for P(defect) is 1 minus the above. Optional observation noise: `A_noisy = (1-eps) * A_clean + eps * 0.5`.

### A[1]: P(o_payoff | s_own, s_type, s_stance)

Shape: `(4, 2, 4, 3)` — 4 payoff outcomes x 2 own_action x 4 types x 3 stances.

Construction: for each (own_action, type, stance), marginalize over partner_action:

```
P(o_payoff=k | own, type, stance) = sum_{partner_action}
    I(payoff_table[own, partner_action] == payoff_levels[k]) * P(partner_action | type, stance)
```

Where the payoff table is:

| | partner cooperates | partner defects |
|---|---|---|
| agent cooperates | 3 | -1 |
| agent defects | 5 | 1 |

And P(partner_action | type, stance) comes from A[0].

Example: P(o_payoff=5 | own=defect, type=cooperator, stance=trusting) = P(partner_cooperates | cooperator, trusting) = 0.95. Because defect + partner_cooperates = payoff 5.

---

## 6. B Matrices (Transition Dynamics)

### B[0]: P(s_type' | s_type)

Shape: `(4, 4, 1)` in the current factorized template. Type is uncontrollable.

Near-identity with small stochastic drift:
```
P(stay same type) = 1 - p_switch = 0.95
P(switch to each other type) = p_switch / 3 ~ 0.017
```

**Why drift?** Type is modeled as slowly drifting rather than perfectly fixed, to (a) capture behavioral nonstationarity in partners, (b) prevent pathological certainty that locks the agent into a wrong type inference, and (c) accommodate regime shifts (e.g., betrayal scenarios where a partner's behavior fundamentally changes).

### B[1]: P(s_stance' | s_stance, pi_social)

Shape: `(3, 3, num_social_actions)` — **action-dependent.** This is the core mechanism that makes planning depth structurally informative.

**For pi_social = cooperate** (action index 0):
```
             from_trust  from_neutral  from_hostile
to_trust       0.90        0.30          0.05
to_neutral     0.10        0.60          0.35
to_hostile     0.00        0.10          0.60
```

**For pi_social = defect** (action index 1):
```
             from_trust  from_neutral  from_hostile
to_trust       0.10        0.05          0.02
to_neutral     0.50        0.35          0.18
to_hostile     0.40        0.60          0.80
```

Key dynamics:
- Cooperating gradually builds trust (neutral -> trusting takes ~3-4 cooperations)
- Defecting rapidly destroys trust (trusting -> hostile possible in ~2 defections)
- Recovery from hostile is slow (hostile -> neutral takes ~4-5 cooperations)
- This asymmetry is what makes deeper planning (horizon 4+) discover trust-building strategies

### B[2]: P(s_own' | s_own, pi_social)

Shape: `(num_social_actions, num_social_actions, num_social_actions)` — **deterministic on the control.**

**For pi_social = cooperate** (action index 0):
```
to_cooperate    1.0    1.0
to_defect       0.0    0.0
```

**For pi_social = defect** (action index 1):
```
to_cooperate    0.0    0.0
to_defect       1.0    1.0
```

Regardless of previous s_own, the new s_own equals the chosen action. This factor exists solely to condition A[1] (payoff) on the agent's own action in a pymdp-standard way.

---

## 7. C Vectors (Observation Preferences)

### C[0]: Preferences over o_action

Shape: `(2,)`

`[0.0, 0.0]` — no direct preference over partner actions. All instrumental motivation comes from payoff preferences (C[1]) and planning depth.

### C[1]: Preferences over o_payoff

Shape: `(4,)` corresponding to payoff levels [-1, 1, 3, 5].

`log_softmax([-1, 1, 3, 5] / temperature)` — ascending preference for higher payoffs. The temperature parameter controls how sharply the agent prefers high payoffs. This is where the PD temptation lives: the agent prefers payoff 5 (defect + partner cooperates) over 3 (mutual cooperation) over 1 (mutual defection) over -1 (cooperate + partner defects).

---

## 8. D Vectors (Initial State Priors)

### D[0]: Prior over s_type

Shape: `(4,)` — `[0.25, 0.25, 0.25, 0.25]` — no initial bias toward any partner type.

### D[1]: Prior over s_stance

Shape: `(3,)` — `[0.2, 0.6, 0.2]` — centered on neutral. Partners expected to start neutral.

### D[2]: Prior over s_own

Shape: `(2,)` — `[0.5, 0.5]` — uniform. (The first action overwrites this deterministically.)

---

## 9. E Vector (Policy Prior / Habits)

Uniform — no policy restrictions. All action sequences are equally likely a priori.

For single-step horizon: `[0.5, 0.5]` for {cooperate, defect}.
For multi-step horizons: all length-tau sequences over {cooperate, defect} are enumerated.

---

## 10. Affective Precision Tracking (External to POMDP)

This module runs after each trial observation, before the next policy selection. It implements Hesp-style affective precision modulation as a standalone tracker that reads social prediction errors.

**Key design decision**: Beta is NOT a POMDP hidden state. It lives outside the generative model as a per-partner precision variable. This matches Hesp et al.'s hierarchical approach where precision is inferred from inference dynamics, not from a dedicated sensory channel.

**Beta convention (Hesp-aligned)**: Beta is the rate parameter of a Gamma prior on policy precision: `E[gamma] = 1/beta`. High beta = low precision = exploratory. Low beta = high precision = decisive.

**Beta levels**: [0.5, 0.67, 1.0, 1.5, 2.0] — discrete categorical distribution per partner.

**Per partner k, after observing partner action:**

### Step 1: Prediction Error

```
eps_k = 1 - P_predicted(observed_action_k)
```

Where `P_predicted` comes from the agent's belief over type × stance before the observation.

**Design choice**: Prediction error is computed from partner action only, not from the joint (action, payoff) observation. Partner action is the most direct social signal of partner model mismatch — it reflects type and stance directly. Payoff adds information about the game outcome but is downstream of partner action (marginalized through the cooperation table). A richer alternative would define eps_k from the joint negative log-likelihood of both observations; this is a straightforward extension if needed.

**Terminology**: This is a bounded prediction error proxy (range [0, 1]), not standard surprisal (-log P). It linearizes surprise for computational simplicity and ensures the affective charge has a natural zero-crossing at eps = sigma_0.

### Step 2: Affective Charge

```
phi_k = alpha * (sigma_0^2 - eps_k^2)
```

With `alpha = 3.0`, `sigma_0^2 = 0.25`:
- `eps = 0` (perfect prediction): `phi = 0.75` (positive — model accurate)
- `eps = 0.5` (baseline): `phi = 0.0` (neutral)
- `eps = 1.0` (total surprise): `phi = -2.25` (negative — model failing)

### Step 3: Persistence Prediction

Apply a tridiagonal transition matrix for temporal smoothing:

```
prior_k = T @ posterior_k_prev
```

Where T is a (5×5) tridiagonal matrix with persistence 0.8 and reflecting boundaries. This encodes the prior expectation that precision evolves slowly.

### Step 4: Pseudo-Likelihood and Bayesian Update

Construct a pseudo-likelihood directly from the affective charge:

This is not a standard observation likelihood in the POMDP sense. It is a hand-designed Bayesian update rule chosen to satisfy three monotonicity properties: (1) positive affective charge should favor low beta (high precision), (2) negative charge should favor high beta (low precision), (3) the strength of evidence should scale with effective precision at each level. The specific functional form `log_lik[l] = phi * (1/beta_l)` is a normative design choice, not a derived theorem:

```
effective_precision_l = 1 / beta_levels[l]
log_lik[l] = phi_k * effective_precision_l
lik = softmax(log_lik)
posterior_k = normalize(lik * prior_k)
```

Positive charge (accurate model) → high likelihood at low beta → posterior shifts toward high precision.
Negative charge (surprise) → high likelihood at high beta → posterior shifts toward low precision.

### Step 5: Gamma Modulation

```
E[beta_k] = dot(posterior_k, beta_levels)
gamma_k = gamma_base / E[beta_k]
```

Policy selection: `q(pi) = softmax(-gamma_k * G(pi))`.

**Per-partner routing in agent-choice mode**: When the action space includes partner selection (N × 2 actions), each policy's first action determines which partner it engages. The policy inherits gamma from that partner: `gamma(pi) = gamma_base / E[beta_{first_partner(pi)}]`. This means policies targeting a well-modeled partner (low beta) are evaluated more decisively than policies targeting an uncertain partner (high beta). The effect is branchwise: different branches of the policy tree may have different effective precision, creating an implicit exploration-exploitation dynamic across partners.

**Framing**: The POMDP handles social inference (type, stance). The precision tracker is a separate Bayesian module that reads prediction errors from social inference and modulates policy precision. This is a hierarchical architecture: the precision tracker operates on the *dynamics* of belief updating, not on a dedicated observation channel.

---

## 11. Per-Partner Inference (Multi-Partner Handling)

The implementation maintains **K parallel instances** of the generative model, one per partner:

- Each partner k has its own posterior over `(type_k, stance_k)`: shape `(4, 3)`
- Each partner k has a corresponding precision tracker maintaining a categorical posterior over `beta_k`: shape `(5,)`. This operates outside the POMDP.
- `s_own` is shared (the agent has one own-action state)
- Each round, only the active partner's beliefs are updated
- A/B matrices are shared across all instances
- D (initial beliefs) are per-partner (all start at the same prior, diverge through observation)

Partner selection is handled outside the POMDP:
- **Random assignment**: environment selects the active partner each round
- **Agent choice**: the agent evaluates expected outcomes for each partner instance and selects which to engage

The POMDP is a purely social inference model: type and stance posteriors are updated from partner action and payoff observations only.

---

## 12. Multi-Agent Extension

All agents (including "partners") run active inference with the same model structure. In simulations, behavioral differences arise from **parameter regimes** — combinations of preference sharpness, planning horizon, and action noise — rather than from temperature alone. Type labels are latent social categories inferred by the focal agent; the simulation instantiates them as follows:

| Type | C[1] temp | Horizon | Notes |
|------|-----------|---------|-------|
| Cooperator | 0.5 (sharp) | 4+ | Strong payoff preference + deep planning → discovers trust-building |
| Exploiter | 2.0 (flat) | 1-2 | Weak preference + shallow planning → greedy, opportunistic |
| Reciprocator | 1.0 (moderate) | 4+ | Moderate preference + deep planning → reciprocates via stance dynamics |
| Random | 5.0 (very flat) | 1 | Nearly indifferent + myopic → near-random behavior |

These are example parameterizations, not a claim that temperature alone generates each phenotype.

### Turn-Taking Protocol

Each round:
1. Focal agent selected (round-robin or random)
2. If agent_choice mode: focal agent selects partner
3. Focal agent: `infer_states → compute G(pi) → retrieve gamma_k from precision tracker → form q(pi) = softmax(-gamma_k · G) → sample action → u_focal`
4. Engaged partner: observes u_focal, runs `infer_states → compute G(pi) → retrieve gamma_k → form q(pi) = softmax(-gamma_k · G) → sample action → u_partner`
5. Both observe: o_action (each sees the other's action), o_payoff (from joint actions)
6. Both update: type x stance posteriors via POMDP inference + beta posteriors via precision tracker

---

## 13. Lesion Conditions

| Condition | What changes | Behavioral prediction |
|-----------|-------------|----------------------|
| **No affect (decouple)** | gamma_k = gamma_base for all k (beta still updates but doesn't influence decisions) | Intact inference, no metacognitive modulation |
| **Frozen affect** | Beta frozen at initial prior, no updates. gamma_k = gamma_base | No metacognitive adaptation at all |
| **Alexithymia** | Dampened alpha_charge (e.g., 0.5 instead of 3.0) -> charge signal is dampened, precision updates are weak | Slow to detect stance shifts |
| **Borderline** | Amplified alpha_charge (e.g., 8.0) -> charge signal is amplified, precision swings wildly | Overreacts to normal fluctuations, destabilizes trust |
| **Depression** | Initial precision tracker prior biased toward high beta (prior expects low precision) | Excessive caution, under-exploits trusting partners |

---

## 14. Summary: What to Build

1. **Standard pymdp model**: A[0] (2x4x3xN), A[1] (payoff_levels x 4 x 3 x N), B[0] (4x4x1), B[1] (3x3xN), B[2] (NxNxN), C[0-1], D[0-2], E, where `N = num_social_actions`.
2. **External precision tracker**: Per-partner categorical over 5 beta levels, updated via affective charge pseudo-likelihood (Section 10). Runs after each trial observation, before policy selection.
3. **Separated inference channels**: Type × stance inference via A[0]+A[1] in the POMDP. Beta inference via external tracker. Beta is not a POMDP factor and does not enter A/B; computationally the tracker is downstream of belief updates (reads prediction errors) and upstream of policy selection (modulates gamma).
4. **Per-partner gamma**: `gamma_k = gamma_base / E[beta_k]` in the policy softmax.
5. **Multi-agent**: All agents run AIF with shared architecture. Partner phenotypes emerge from different internal parameterizations (preference temperature, planning depth, noise).
