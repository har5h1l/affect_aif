# Hesp-Native Beta Specification

## Full POMDP for the Trust Game with Affective Precision

This document specifies the generative model in standard pymdp A/B/C/D/E format, following Hesp et al. (2021). The model has 4 hidden state factors and 3 observation modalities.

---

## 1. Overview

An agent interacts with N partners in a repeated trust game. Each round, the agent is paired with one partner and chooses to cooperate or defect. The partner's response depends on their fixed type and their evolving stance toward the agent. The agent tracks per-partner model quality via an affective precision state (beta), inferred through an interoceptive observation channel.

**Important clarification**: Stance is the **partner's** disposition toward the **agent** (a hidden state the agent must infer), not the agent's own attitude. The agent can influence the partner's stance through its actions (cooperating builds trust, defecting destroys it), but cannot directly observe or control it.

---

## 2. Hidden State Factors (F=4)

| Factor | Symbol | States | Controllable? | Notes |
|--------|--------|--------|---------------|-------|
| Partner type | `s{type}` | cooperator, reciprocator, exploiter, random (4) | No | Fixed behavioral tendency. Small stochastic drift (p_switch). |
| Partner stance | `s{stance}` | trusting, neutral, hostile (3) | **Yes** | Partner's Bayesian inference about agent character → discrete stance. Evolves based on agent's actions. |
| Interaction context | `s{context}` | partner_1, ..., partner_N (N) | Depends on mode | In agent_choice mode: controllable. In random assignment: uncontrollable. |
| Affective precision | `s{beta}` | 0.2, 0.5, 1.0, 1.5, 2.0 (5) | No | Per-partner metacognitive precision. Levels are precision multipliers: 1.0 = baseline. |

Joint state space per partner: 4 types x 3 stances x 5 beta levels = 60 states (manageable).

**Key structural property**: Because `A[partner_action]` does not depend on `s{beta}`, and `B[beta]` does not depend on `s{type}` or `s{stance}`, the posterior factorizes exactly:

```
P(type, stance, beta | o_action, o_intero) = P(type, stance | o_action) * P(beta | o_intero)
```

Inference over (type, stance) and inference over beta are independent. This is the central simplification: the model is tractable because the two inference channels don't interact at the posterior level — they interact only through gamma modulation at policy selection time.

---

## 3. Observation Modalities (M=3)

| Modality | Symbol | Outcomes | Depends on |
|----------|--------|----------|------------|
| Partner action | `o{action}` | cooperate, defect (2) | type, stance |
| Payoff | `o{payoff}` | discretized levels, e.g. {-1, 1, 3, 5} (4) | agent_action, partner_action (see note) |
| Interoceptive | `o{intero}` | 5 levels of affective charge | beta |

**Note on payoff**: The payoff observation is a deterministic function of (agent_action, partner_action), not a standard A-matrix mapping from hidden states. In the implementation, expected payoff is computed by marginalizing over partner actions given beliefs, combined with the candidate agent action. For a pymdp implementation, either: (a) handle payoff via a custom EFE function, (b) drop the payoff modality and encode preferences solely through C[action], or (c) add agent_action as a deterministic hidden state factor. Option (a) is recommended for simplicity.

---

## 4. Control Factors (U=1)

| Factor | Symbol | Actions | Controls |
|--------|--------|---------|----------|
| Social action | `pi{social}` | cooperate, defect (2) | `s{stance}` transitions (via action-dependent B) |

In agent_choice mode, the action space expands to N x 2 (choose partner x choose social action), and `pi{social}` also controls `s{context}`.

---

## 5. A Matrices (Observation Likelihoods)

### A[0]: P(o{action} | s{type}, s{stance})

Shape: `(2, 4, 3)` — 2 observations x 4 types x 3 stances.

This is uniform over `s{beta}` (beta does not change what the partner does). The full theoretical shape would be `(2, 4, 3, N, 5)`, but the beta and context dimensions are uniform and can be marginalized out.

Each entry is the probability that the partner cooperates given their type and stance:

|  | trusting | neutral | hostile |
|---|---|---|---|
| cooperator | 0.95 | 0.80 | 0.55 |
| reciprocator | 0.90 | 0.70 | 0.30 |
| exploiter | 0.70 | 0.35 | 0.10 |
| random | 0.60 | 0.50 | 0.35 |

The row for P(defect) is 1 minus the above. Optional observation noise can be added: `A_noisy = (1-noise) * A_clean + noise * 0.5`.

### A[1]: P(o{payoff} | ...)

Non-standard — see note in Section 3. Not a pure hidden-state-to-observation mapping.

For the pymdp spec, this can be omitted and payoff preferences encoded entirely through C[0] and a custom EFE function. If needed as a matrix, add `s{agent_action}` as a deterministic hidden state factor and define `A[1]` as shape `(K, 2)` mapping (agent_action, partner_action) to payoff.

### A[2]: P(o{intero} | s{beta})

Shape: `(5, 5)` — 5 interoceptive observations x 5 beta levels.

Each column is the probability of observing each interoceptive level given a beta state. Columns sum to 1. Higher beta states assign more probability to high-valence interoceptive observations.

Construction: For beta level `b_l` and interoceptive bin center `epsilon_s`:
```
A[2][s, l] = exp(alpha * (sigma_0^2 - epsilon_s^2) * b_l)
```
Then normalize each column. With `alpha=3.0`, `sigma_0^2=0.25`, `beta_levels=[0.2, 0.5, 1.0, 1.5, 2.0]`, and `bin_centers=[0.0, 0.25, 0.5, 0.75, 1.0]`, this gives a matrix where:

- Low beta (0.2): nearly uniform across interoceptive observations (poor precision → noisy interoception)
- High beta (2.0): concentrated on high-valence interoceptive observations (good precision → clear positive interoception)

This is uniform over `s{type}`, `s{stance}`, `s{context}` — interoception depends only on beta.

---

## 6. B Matrices (Transition Dynamics)

### B[0]: P(s{type, t+1} | s{type, t})

Shape: `(4, 4)` — replicated identically across all actions (uncontrollable).

Near-identity with small stochastic drift:
```
P(stay same type) = 1 - p_switch = 0.95
P(switch to each other type) = p_switch / 3 ≈ 0.017
```

### B[1]: P(s{stance, t+1} | s{stance, t}, pi{social})

Shape: `(3, 3, 2)` — **action-dependent**. This is the core mechanism that makes planning depth informative.

**For pi{social} = cooperate** (action index 0):
```
             from_trust  from_neutral  from_hostile
to_trust       0.90        0.30          0.05
to_neutral     0.10        0.60          0.35
to_hostile     0.00        0.10          0.60
```

**For pi{social} = defect** (action index 1):
```
             from_trust  from_neutral  from_hostile
to_trust       0.10        0.05          0.02
to_neutral     0.50        0.35          0.18
to_hostile     0.40        0.60          0.80
```

Key dynamics:
- Cooperating gradually builds trust (neutral → trusting takes ~3-4 cooperations)
- Defecting rapidly destroys trust (trusting → hostile possible in ~2 defections)
- Recovery from hostile is slow (hostile → neutral takes ~4-5 cooperations)
- This asymmetry is what makes deeper planning (horizon 4+) discover trust-building strategies

### B[2]: P(s{context, t+1} | s{context, t}, pi{social})

Shape: `(N, N, U)` where U is the number of actions.

- Agent_choice mode: deterministic partner selection based on action.
- Random assignment: uniform `1/N` regardless of action.

### B[3]: P(s{beta, t+1} | s{beta, t})

Shape: `(5, 5)` — replicated identically across all actions (uncontrollable).

Tridiagonal with persistence and reflecting boundaries:
```
             from_VL  from_L   from_M   from_H   from_VH
to_VeryLow    0.90    0.10     0.00     0.00     0.00
to_Low        0.10    0.80     0.10     0.00     0.00
to_Medium     0.00    0.10     0.80     0.10     0.00
to_High       0.00    0.00     0.10     0.80     0.10
to_VeryHigh   0.00    0.00     0.00     0.10     0.90
```

(With persistence = 0.8. Boundary states get the reflected leak probability added to self-transition, hence 0.90 at edges.)

This is the agent's generative model of how precision evolves: slowly, persistently, with small random fluctuations. The **actual** precision updates are driven by the interoceptive observation — the gap between what B[3] predicts and what `o{intero}` shows is what drives inference.

---

## 7. C Vectors (Observation Preferences)

### C[0]: Preferences over o{action}

Shape: `(2,)`

`[0.0, 0.0]` — no direct preference over partner actions. Payoff preferences are handled separately.

### C[1]: Preferences over o{payoff}

Shape: `(K,)` where K is the number of payoff levels.

`log_softmax([-1, 1, 3, 5] / temperature)` — ascending preference for higher payoffs. The temperature parameter controls how sharply the agent prefers high payoffs.

### C[2]: Preferences over o{intero}

Shape: `(5,)`

`[0.0, 0.25, 0.5, 0.75, 1.0]` scaled by preference temperature — **ascending preference for high-precision interoceptive observations**.

This is the Hesp move: the agent has a prior preference for states where its model is performing well. This makes "having accurate social models" intrinsically preferred, which is what grounds the inside-out metacognitive framing. The agent doesn't just track model quality — it *cares* about model quality.

**Note on planning**: In the factorized implementation, C[2] does not directly enter the EFE computation for action selection (since beta dynamics are action-independent from the rollout's perspective). The indirect causal chain (action → stance → prediction error → intero obs → beta) is a second-order effect that would only appear in a fully joint (non-factorized) EFE computation. C[2] is declared for theoretical completeness and for the fully joint pymdp implementation.

---

## 8. D Vectors (Initial State Priors)

### D[0]: Prior over s{type}

Shape: `(4,)`

`[0.25, 0.25, 0.25, 0.25]` — uniform, no initial bias toward any partner type.

### D[1]: Prior over s{stance}

Shape: `(3,)`

`[0.2, 0.6, 0.2]` — centered on neutral. The agent expects partners to start with a neutral disposition.

### D[2]: Prior over s{context}

Shape: `(N,)`

`[1/N, ..., 1/N]` — uniform over partners.

### D[3]: Prior over s{beta}

Shape: `(5,)`

Concentrated near the level where beta = 1.0 (the baseline precision multiplier). For example, with `beta_levels = [0.2, 0.5, 1.0, 1.5, 2.0]`, the prior is concentrated at index 2:

`[0.05, 0.15, 0.60, 0.15, 0.05]`

This encodes: "at the start, I expect my model to be at baseline precision for each partner."

---

## 9. E Vector (Policy Prior / Habits)

Uniform — no policy restrictions. All action sequences are equally likely a priori.

For a single-step horizon: `[0.5, 0.5]` for {cooperate, defect}.

For multi-step horizons: all length-tau sequences over {cooperate, defect} are enumerated.

---

## 10. Custom Function: Affective Charge and Gamma Modulation

This function runs after each trial observation, before the next policy selection. It implements the Hesp-style affective inference loop and the per-partner gamma modulation.

**Per partner k, after observing partner action:**

### Step 1: Prediction Error

```
eps_k = 1 - P_predicted(observed_action_k)
```

Where `P_predicted` comes from the agent's belief over type x stance before the observation.

### Step 2: Affective Charge

```
phi_k = alpha * (sigma_0^2 - eps_k^2)
```

With `alpha = 3.0`, `sigma_0^2 = 0.25`:
- `eps = 0` (perfect prediction): `phi = 0.75` (positive charge)
- `eps = 0.5` (baseline): `phi = 0.0` (neutral)
- `eps = 1.0` (total surprise): `phi = -2.25` (strong negative charge)

### Step 3: Interoceptive Observation

Discretize phi to one of 5 levels via sigmoid-then-quantize:

```
p = sigmoid(phi_k)
o_intero_k = floor(p * 5)   # clipped to [0, 4]
```

Mapping:
- phi << 0 (high surprise) → o_intero = 0 (low valence)
- phi ≈ 0 (baseline) → o_intero = 2 (neutral)
- phi >> 0 (low surprise) → o_intero = 3-4 (high valence)

### Step 4: Bayesian Update on Beta

Standard predict-then-correct using A[2] and B[3]:

```
prior_k = B[3] @ posterior_k_prev
likelihood_k = A[2][o_intero_k, :]    # row of A[2] for this observation
posterior_k = normalize(likelihood_k * prior_k)
```

### Step 5: Gamma Modulation

```
E[beta_k] = dot(posterior_k, beta_levels)
gamma_k = gamma_base * E[beta_k]
```

Where `beta_levels = [0.2, 0.5, 1.0, 1.5, 2.0]`. This replaces the global gamma for policies involving partner k.

- `E[beta_k] ≈ 1.0` (baseline): `gamma_k ≈ gamma_base` (normal decisiveness)
- `E[beta_k] < 1.0` (model failing): `gamma_k < gamma_base` (more exploratory)
- `E[beta_k] > 1.0` (model accurate): `gamma_k > gamma_base` (more decisive)

Policy selection: `q(pi) = softmax(-gamma_k * G(pi))` where G(pi) is the expected free energy for policy pi.

---

## 11. Multi-Partner Handling

Rather than separate hidden state factors per partner (which would give a joint space of 4^N x 3^N x 5^N), we maintain separate belief vectors per partner:

- Each partner k has its own posterior over `(type, stance)`: shape `(4, 3)` 
- Each partner k has its own posterior over `beta`: shape `(5,)`
- Each round, only the active partner's beliefs are updated

In agent_choice mode, the context factor `s{context}` selects which partner is active, and the action space is `N x 2` (choose partner x choose social action).

---

## 12. Lesion Conditions

| Condition | What changes | Behavioral prediction |
|-----------|-------------|----------------------|
| **No affect (decouple)** | gamma_k = gamma_base for all k (beta still updates internally but doesn't influence decisions) | Intact type/stance inference, but fails to adapt decision confidence to model quality changes |
| **Frozen affect** | Beta frozen at initial value, no updates. gamma_k = gamma_base * 1.0 | No metacognitive adaptation at all |
| **Alexithymia** | Dampened alpha_charge (e.g., 0.5 instead of 3.0) → intero observations cluster near neutral | Slow to detect stance shifts |
| **Borderline** | Amplified alpha_charge (e.g., 8.0) → intero observations swing to extremes | Overreacts to normal fluctuations, destabilizes trust |
| **Depression** | Negative bias in initial D[3] (prior concentrated on low beta) | Under-exploits trusting partners, excessive caution |

---

## 13. Comparison: Precision Tracking vs Reward Averaging

An alternative to the Hesp-style beta is a simple reward average:

- **Reward average**: `signal_k = running_mean(payoff_k)` → maps to gamma via tanh
- **Precision tracking**: `beta_k = Bayesian posterior over model quality` → maps to gamma via E[beta]

These dissociate when a partner's stance shifts but payoffs haven't changed yet (e.g., a reciprocator just became wary — predictions are wrong but last round's payoff was fine). Precision tracking detects this immediately (prediction error spike → low intero obs → beta drops). Reward averaging lags because payoffs haven't changed.

---

## 14. Summary of What Andrew Needs to Build

1. **Standard pymdp model**: A[0] (2x4x3), A[2] (5x5), B[0] (4x4), B[1] (3x3x2), B[2] (NxNxU), B[3] (5x5), C[0-2], D[0-3], E.
2. **Custom function**: The 5-step affective charge → intero obs → beta update → gamma modulation procedure (Section 10). This is the same logic from his legacy Hesp implementation, now per-partner.
3. **Factorized inference**: Type x stance inference via A[0], beta inference via A[2], running in parallel (exact factorization, not approximation).
4. **Per-partner gamma**: Replace global gamma with gamma_k = gamma_base * E[beta_k] in the policy softmax.
