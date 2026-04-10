# POMDP Specification v3 — Hesp-Aligned Affect AIF

This is the merged, authoritative specification for the trust-game POMDP, superseding both `hesp-beta-spec.md` and `agent_model_spec.md`. It follows Hesp et al. (2021) "Deeply Felt Affect" and specifies the generative model in standard pymdp A/B/C/D/E format.

---

## 1. Overview

N agents interact in a repeated trust game with turn-taking. Each round, one focal agent selects an action (cooperate/defect, and optionally which partner to engage). All agents run active inference — behavioral "types" are encoded in preference structures (C), not hardcoded policies. Each agent maintains per-partner beliefs over (type, stance, beta).

The agent tracks per-partner metacognitive precision (beta_k) through an interoceptive inference channel, adapting Hesp et al.'s single-agent affective precision to the multi-partner social domain. This is the "inside-out" move: the agent tracks the reliability of its *own* social model for each partner, not the partner's internal state.

**Version history**: v1 had F=4, M=3 with non-standard payoff. v2 dropped payoff (M=2). v3 restores payoff as a proper modality via s_own factor and re-parameterizes beta to match Hesp's convention.

**Posterior factorization** (key tractability property): A[0] and A[1] are uniform over beta. A[2] depends only on beta. Therefore:

```
P(type, stance, own_action, beta | o_action, o_payoff, o_intero)
  = P(type, stance, own_action | o_action, o_payoff) * P(beta | o_intero)
```

Since own_action is deterministic given the agent's policy, it collapses out of inference. The two independent channels are:
1. **Social inference**: (type, stance) updated from o_action and o_payoff
2. **Precision inference**: beta updated from o_intero

---

## 2. Hidden State Factors (F=5)

| Factor | Symbol | States | Controllable? | Notes |
|--------|--------|--------|---------------|-------|
| Partner type | `s_type` | cooperator, reciprocator, exploiter, random (4) | No | Fixed behavioral tendency. Small stochastic drift (p_switch = 0.05). |
| Partner stance | `s_stance` | trusting, neutral, hostile (3) | **Yes** | Partner's disposition toward the agent. Evolves based on agent's actions. Agent influences via actions, cannot observe directly. |
| Interaction context | `s_context` | partner_1, ..., partner_N (N) | Depends on mode | agent_choice: controllable. random: uncontrollable. |
| Affective precision | `s_beta` | 0.5, 0.67, 1.0, 1.5, 2.0 (5) | No | **Hesp rate parameter.** E[gamma] = 1/beta. High beta = low precision = exploratory. |
| Own action | `s_own` | cooperate, defect (2) | Yes | Deterministic: tracks agent's own last action. Needed for payoff modality. |

**Key structural property**: Stance is the **partner's** disposition toward the **agent** (a hidden state the agent must infer), not the agent's own attitude. The agent influences stance through its actions (cooperating builds trust, defecting destroys it), but cannot directly observe or control it.

**Beta sign convention (Hesp-aligned)**: In Hesp (2021), beta is the rate parameter of the Gamma prior on policy precision gamma: `P(gamma) = Gamma(1, beta)`, so `E[gamma] = 1/beta`. High beta = low expected precision = more exploratory. Low beta = high expected precision = more decisive. This is the **opposite** of an intuitive "higher is better" reading. We follow Hesp's convention exactly.

Joint state space per partner: 4 types x 3 stances x 5 beta x 2 own_action = 120 states.

---

## 3. Observation Modalities (M=3)

| Modality | Symbol | Outcomes | Depends on |
|----------|--------|----------|------------|
| Partner action | `o_action` | cooperate, defect (2) | type, stance |
| Payoff | `o_payoff` | -1, 1, 3, 5 (4 discrete levels) | own_action, type, stance (partner action marginalized) |
| Interoceptive | `o_intero` | 5 levels of affective charge (0-4) | beta |

**Payoff**: Now a proper modality with A[1] conditioned on (s_own, s_type, s_stance). The partner's actual action is marginalized through the type x stance cooperation probabilities. This preserves the Prisoner's Dilemma temptation structure at horizon 1 while trust-building via stance dynamics emerges at horizon >= 2.

**Interoceptive**: This is NOT an external observation. It is the agent's readout of its own prediction error on the social channel, discretized and treated as sensory input to a higher-level Bayesian filter over beta. This is hierarchical active inference under the Seth/Friston interoceptive inference framing: the agent models its own precision state through an internal sensory channel (neuroscience hook: interoception -> insula/vmPFC).

We adapt Hesp's affective charge to the social domain. Rather than computing AC from the gap between prior and posterior policy beliefs (`AC = (pi - pi_bar) * G`, which is global), we compute per-partner prediction error from the social observation channel. This gives per-partner resolution that Hesp's formulation does not naturally provide — enabling between-partner comparison, per-partner precision-weighted learning, and persistent high-beta as a BMR trigger.

---

## 4. Control Factors (U=1)

| Factor | Symbol | Actions | Controls |
|--------|--------|---------|----------|
| Social action | `pi_social` | cooperate, defect (2) | `s_stance` transitions (via action-dependent B), `s_own` (deterministic) |

In agent_choice mode, the action space expands to N x 2 (choose partner x choose social action), and `pi_social` also controls `s_context`.

---

## 5. A Matrices (Observation Likelihoods)

### A[0]: P(o_action | s_type, s_stance)

Shape: `(2, 4, 3)` — uniform over s_beta, s_context, s_own.

Each entry is the probability that the partner cooperates given their type and stance:

|  | trusting | neutral | hostile |
|---|---|---|---|
| cooperator | 0.95 | 0.80 | 0.55 |
| reciprocator | 0.90 | 0.70 | 0.30 |
| exploiter | 0.70 | 0.35 | 0.10 |
| random | 0.60 | 0.50 | 0.35 |

The row for P(defect) is 1 minus the above. Optional observation noise: `A_noisy = (1-eps) * A_clean + eps * 0.5`.

### A[1]: P(o_payoff | s_own, s_type, s_stance)

Shape: `(4, 2, 4, 3)` — 4 payoff outcomes x 2 own_action x 4 types x 3 stances. Uniform over s_beta, s_context.

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

### A[2]: P(o_intero | s_beta)

Shape: `(5, 5)` — 5 interoceptive outcomes x 5 beta levels. Uniform over all other factors.

Construction: for beta level `b_l` and interoceptive bin center `eps_s`, use **effective precision** = 1/beta:

```
A[2][s, l] = exp(alpha * (sigma_0^2 - eps_s^2) * (1 / b_l))
```

Then normalize each column. With `alpha=3.0`, `sigma_0^2=0.25`, `beta_levels=[0.5, 0.67, 1.0, 1.5, 2.0]`, `bin_centers=[0.0, 0.25, 0.5, 0.75, 1.0]`:

- **Low beta (0.5)** = high precision: concentrated on high-valence interoceptive observations (clear positive interoception — "my model works well")
- **High beta (2.0)** = low precision: nearly uniform across interoceptive observations (noisy interoception — "unclear how my model is doing")

This encodes the Hesp relationship: agents in states of high effective precision (low beta) reliably experience positive interoceptive observations, while agents in states of low effective precision (high beta) have diffuse/uncertain interoception.

---

## 6. B Matrices (Transition Dynamics)

### B[0]: P(s_type' | s_type)

Shape: `(4, 4, 2)` — replicated identically across actions (uncontrollable).

Near-identity with small stochastic drift:
```
P(stay same type) = 1 - p_switch = 0.95
P(switch to each other type) = p_switch / 3 ~ 0.017
```

### B[1]: P(s_stance' | s_stance, pi_social)

Shape: `(3, 3, 2)` — **action-dependent.** This is the core mechanism that makes planning depth structurally informative.

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

### B[2]: P(s_context' | s_context, pi_social)

Shape: `(N, N, 2)`.

- Agent_choice mode: deterministic partner selection based on action encoding.
- Random assignment: uniform `1/N` regardless of action.

### B[3]: P(s_beta' | s_beta)

Shape: `(5, 5, 2)` — replicated identically across actions (uncontrollable).

Tridiagonal with persistence and reflecting boundaries:
```
             from_0.5  from_0.67  from_1.0  from_1.5  from_2.0
to_0.5        0.90      0.10       0.00      0.00      0.00
to_0.67       0.10      0.80       0.10      0.00      0.00
to_1.0        0.00      0.10       0.80      0.10      0.00
to_1.5        0.00      0.00       0.10      0.80      0.10
to_2.0        0.00      0.00       0.00      0.10      0.90
```

(Persistence = 0.8. Boundary states get reflected leak probability added to self-transition, hence 0.90 at edges.)

This is the agent's generative model of how precision evolves: slowly, persistently, with small random fluctuations. The **actual** precision updates are driven by the interoceptive observation — the gap between what B[3] predicts and what `o_intero` shows is what drives inference.

### B[4]: P(s_own' | s_own, pi_social)

Shape: `(2, 2, 2)` — **deterministic on the control.**

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

### C[2]: Preferences over o_intero

Shape: `(5,)`

`[0.0, 0.25, 0.5, 0.75, 1.0]` scaled by preference temperature — **ascending preference for high-valence interoceptive observations.**

This is the Hesp move: the agent has a prior preference for states where its model is performing well (low beta = high effective precision = positive interoceptive observations). This makes "having accurate social models" intrinsically preferred, which grounds the inside-out metacognitive framing.

**Note on planning**: In the factorized implementation, C[2] does not directly enter the EFE computation for action selection (since beta dynamics are action-independent). The indirect causal chain (action -> stance -> prediction error -> intero obs -> beta) is a second-order effect. C[2] is declared for theoretical completeness and for the fully joint (non-factorized) pymdp implementation.

---

## 8. D Vectors (Initial State Priors)

### D[0]: Prior over s_type

Shape: `(4,)` — `[0.25, 0.25, 0.25, 0.25]` — no initial bias toward any partner type.

### D[1]: Prior over s_stance

Shape: `(3,)` — `[0.2, 0.6, 0.2]` — centered on neutral. Partners expected to start neutral.

### D[2]: Prior over s_context

Shape: `(N,)` — `[1/N, ..., 1/N]` — uniform over partners.

### D[3]: Prior over s_beta

Shape: `(5,)` — concentrated near the baseline rate beta = 1.0:

`[0.05, 0.15, 0.60, 0.15, 0.05]`

This encodes: "at the start, I expect baseline precision for each partner" (E[gamma] = 1/1.0 = gamma_base).

### D[4]: Prior over s_own

Shape: `(2,)` — `[0.5, 0.5]` — uniform. (The first action overwrites this deterministically.)

---

## 9. E Vector (Policy Prior / Habits)

Uniform — no policy restrictions. All action sequences are equally likely a priori.

For single-step horizon: `[0.5, 0.5]` for {cooperate, defect}.
For multi-step horizons: all length-tau sequences over {cooperate, defect} are enumerated.

---

## 10. Affective Charge and Gamma Modulation

This function runs after each trial observation, before the next policy selection. It implements the Hesp-style affective inference loop and the per-partner gamma modulation.

**Per partner k, after observing partner action:**

### Step 1: Prediction Error

```
eps_k = 1 - P_predicted(observed_action_k)
```

Where `P_predicted` comes from the agent's belief over type x stance before the observation. This is a functional of the agent's own inference — not an external signal.

**Adaptation from Hesp**: Hesp's affective charge is `AC = (pi - pi_bar) * G` — the gap between posterior and prior policy beliefs weighted by EFE (global policy surprise). We instead compute per-partner prediction error from the social observation channel. This gives per-partner resolution that Hesp's formulation does not naturally provide, enabling between-partner comparison and per-partner precision-weighted learning.

### Step 2: Affective Charge

```
phi_k = alpha * (sigma_0^2 - eps_k^2)
```

With `alpha = 3.0`, `sigma_0^2 = 0.25`:
- `eps = 0` (perfect prediction): `phi = 0.75` (positive charge — things going better than expected)
- `eps = 0.5` (baseline): `phi = 0.0` (neutral)
- `eps = 1.0` (total surprise): `phi = -2.25` (strong negative charge — things going worse than expected)

### Step 3: Interoceptive Observation

Discretize phi to one of 5 levels via sigmoid-then-quantize:

```
p = sigmoid(phi_k)
o_intero_k = floor(p * 5)   # clipped to [0, 4]
```

Mapping:
- phi << 0 (high surprise) -> o_intero = 0 (low valence)
- phi ~ 0 (baseline) -> o_intero = 2 (neutral)
- phi >> 0 (low surprise) -> o_intero = 3-4 (high valence)

### Step 4: Bayesian Update on Beta

Standard predict-then-correct using A[2] and B[3]:

```
prior_k = B[3] @ posterior_k_prev
likelihood_k = A[2][o_intero_k, :]    # row of A[2] for this observation
posterior_k = normalize(likelihood_k * prior_k)
```

### Step 5: Gamma Modulation (Hesp-Aligned)

```
E[beta_k] = dot(posterior_k, beta_levels)
gamma_k = gamma_base / E[beta_k]
```

Where `beta_levels = [0.5, 0.67, 1.0, 1.5, 2.0]`. This replaces the global gamma for policies involving partner k.

- `E[beta_k] ~ 0.5` (low rate = high precision, model accurate): `gamma_k ~ 2 * gamma_base` (very decisive)
- `E[beta_k] ~ 1.0` (baseline): `gamma_k ~ gamma_base` (normal)
- `E[beta_k] ~ 2.0` (high rate = low precision, model failing): `gamma_k ~ 0.5 * gamma_base` (exploratory)

Policy selection: `q(pi) = softmax(-gamma_k * G(pi))` where G(pi) is the expected free energy for policy pi.

**Framing**: The beta factor is a vanilla POMDP hidden state updated by Bayesian inference on interoceptive observations. The affect mechanism is a per-partner precision modulation layer sitting between infer_policies and sample_action that reads beta's posterior expectation and scales gamma before the softmax. This is where pymdp-vanilla ends and our extension begins.

---

## 11. Per-Partner Inference (Multi-Partner Handling)

The spec above describes a single POMDP with factors (type, stance, context, beta, own_action). But a single shared posterior over type and stance does not make sense with K partners who have different types. The implementation runs **K parallel instances** of the generative model:

- Each partner k has its own posterior over `(type_k, stance_k)`: shape `(4, 3)`
- Each partner k has its own posterior over `beta_k`: shape `(5,)`
- `s_own` is shared (the agent has one own-action state)
- Each round, only the active partner's beliefs are updated
- A/B matrices are shared across all instances
- D (initial beliefs) are per-partner (all start at the same prior, diverge through observation)

In agent_choice mode, the context factor `s_context` selects which partner is active, and the action space is `N x 2` (choose partner x choose social action).

This is NOT an approximation — the factorization in Section 1 means per-partner inference is exact.

---

## 12. Multi-Agent Extension

All agents (including "partners") run active inference with the same model structure. Behavioral types are encoded in **C preference temperature**, not hardcoded policies:

| Type | C[1] temperature | Effect |
|------|-----------------|--------|
| Cooperator | 0.5 (sharp) | Strong payoff preference, naturally cooperates for trust |
| Exploiter | 2.0 (flat) | Weak payoff preference, opportunistic |
| Reciprocator | 1.0 (moderate) | Moderate, reciprocates via planning depth |
| Random | 5.0 (very flat) | Nearly indifferent, near-random |

### Turn-Taking Protocol

Each round:
1. Focal agent selected (round-robin or random)
2. If agent_choice mode: focal agent selects partner
3. Focal agent: `infer_states -> infer_policies -> modulate_precision -> sample_action -> u_focal`
4. Engaged partner: observes u_focal, runs `infer_states -> infer_policies -> modulate_precision -> sample_action -> u_partner`
5. Both observe: o_action (each sees the other's action), o_payoff (from joint actions), o_intero (from own prediction error)
6. Both update: type x stance posteriors + beta posteriors via custom function

---

## 13. Lesion Conditions

| Condition | What changes | Behavioral prediction |
|-----------|-------------|----------------------|
| **No affect (decouple)** | gamma_k = gamma_base for all k (beta still updates but doesn't influence decisions) | Intact inference, no metacognitive modulation |
| **Frozen affect** | Beta frozen at D[3], no updates. gamma_k = gamma_base | No metacognitive adaptation at all |
| **Alexithymia** | Dampened alpha_charge (e.g., 0.5 instead of 3.0) -> intero observations cluster near neutral | Slow to detect stance shifts |
| **Borderline** | Amplified alpha_charge (e.g., 8.0) -> intero observations swing to extremes | Overreacts to normal fluctuations, destabilizes trust |
| **Depression** | D[3] biased toward high beta (prior expects low precision) | Excessive caution, under-exploits trusting partners |

---

## 14. Summary: What to Build

1. **Standard pymdp model**: A[0] (2x4x3), A[1] (4x2x4x3), A[2] (5x5), B[0] (4x4x2), B[1] (3x3x2), B[2] (NxNx2), B[3] (5x5x2), B[4] (2x2x2), C[0-2], D[0-4], E.
2. **Custom function**: The 5-step affective charge -> intero obs -> beta update -> gamma modulation procedure (Section 10). Per-partner, runs after each trial observation.
3. **Factorized inference**: Type x stance inference via A[0]+A[1], beta inference via A[2], running independently (exact factorization, not approximation).
4. **Per-partner gamma**: Replace global gamma with `gamma_k = gamma_base / E[beta_k]` in the policy softmax.
5. **Multi-agent**: All agents run AIF. Turn-taking. Types from C temperature.
