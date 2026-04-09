# Agent Model Specification: Trust Game with Affective Precision

## Hidden State Factors

| Factor | Symbol | States | Controllable? | Notes |
|--------|--------|--------|---------------|-------|
| Partner type | s{type} | cooperator, reciprocator, exploiter, random (4) | No | Small stochastic drift p_switch = 0.05 |
| Partner stance | s{stance} | trusting, neutral, hostile (3) | Indirect | Partner's disposition toward agent. Agent influences via actions, cannot observe directly. |
| Interaction context | s{context} | partner_1, ..., partner_N (N) | Yes (agent_choice mode) | Which partner is currently active |
| Affective precision | s{beta} | 0.2, 0.5, 1.0, 1.5, 2.0 (5) | No | Per-partner metacognitive precision. 1.0 = baseline. |

---

## Observation Modalities

| Modality | Symbol | Outcomes | Depends on |
|----------|--------|----------|------------|
| Partner action | o{action} | cooperate, defect (2) | s{type}, s{stance} |
| Payoff | o{payoff} | e.g. {-1, 1, 3, 5} (4) | agent_action x partner_action (see note below) |
| Interoceptive | o{intero} | 5 levels of affective charge | s{beta} only |

Payoff is a deterministic function of (agent_action, partner_action), not a standard hidden-state-to-observation mapping.

---

## Control Factor

| Factor | Symbol | Actions | Controls |
|--------|--------|---------|----------|
| Social action | pi{social} | cooperate, defect (2) | s{stance} transitions via action-dependent B[1] |

In agent_choice mode the action space expands to N x 2 (choose partner x choose social action), and pi{social} also controls s{context}.

---

## A Matrices

### A[0]: P(o{action} | s{type}, s{stance})

Shape: `(2, 4, 3)` -- 2 outcomes x 4 types x 3 stances.

Values are P(cooperate | type, stance). P(defect) = 1 - P(cooperate).

|  | trusting | neutral | hostile |
|--|----------|---------|---------|
| cooperator | 0.95 | 0.80 | 0.55 |
| reciprocator | 0.90 | 0.70 | 0.30 |
| exploiter | 0.70 | 0.35 | 0.10 |
| random | 0.60 | 0.50 | 0.35 |

Optional noise: `A_noisy = (1 - noise) * A_clean + noise * 0.5`

### A[1]: Payoff

N/A

### A[2]: P(o{intero} | s{beta})

Shape: `(5, 5)` -- 5 interoceptive observations x 5 beta levels. Columns sum to 1.

Construction: for beta level `b_l` and bin center `epsilon_s`:

```
A[2][s, l] = exp(alpha * (sigma_0^2 - epsilon_s^2) * b_l)
```

Normalize each column. Parameters: `alpha=3.0`, `sigma_0^2=0.25`, `beta_levels=[0.2, 0.5, 1.0, 1.5, 2.0]`, `bin_centers=[0.0, 0.25, 0.5, 0.75, 1.0]`.

Low beta (0.2) produces a nearly uniform distribution. High beta (2.0) concentrates mass on high-valence observations.

---

## B Matrices

### B[0]: P(s{type, t+1} | s{type, t})

Shape: `(4, 4)` -- uncontrollable, replicated across actions.

```
P(stay same type)          = 0.95
P(switch to each other type) = 0.05 / 3 ~= 0.017
```

### B[1]: P(s{stance, t+1} | s{stance, t}, pi{social})

Shape: `(3, 3, 2)` -- action-dependent.

**pi{social} = cooperate (action 0):**

|  | from trusting | from neutral | from hostile |
|--|---------------|--------------|--------------|
| to trusting | 0.90 | 0.30 | 0.05 |
| to neutral  | 0.10 | 0.60 | 0.35 |
| to hostile  | 0.00 | 0.10 | 0.60 |

**pi{social} = defect (action 1):**

|  | from trusting | from neutral | from hostile |
|--|---------------|--------------|--------------|
| to trusting | 0.10 | 0.05 | 0.02 |
| to neutral  | 0.50 | 0.35 | 0.18 |
| to hostile  | 0.40 | 0.60 | 0.80 |

### B[2]: P(s{context, t+1} | s{context, t}, pi{social})

Shape: `(N, N, U)`. Deterministic partner selection in agent_choice mode. Uniform 1/N in random assignment mode.

### B[3]: P(s{beta, t+1} | s{beta, t})

Shape: `(5, 5)` -- uncontrollable, tridiagonal with persistence 0.80 and reflecting boundaries.

|  | from VL | from L | from M | from H | from VH |
|--|---------|--------|--------|--------|---------|
| to VL | 0.90 | 0.10 | 0.00 | 0.00 | 0.00 |
| to L  | 0.10 | 0.80 | 0.10 | 0.00 | 0.00 |
| to M  | 0.00 | 0.10 | 0.80 | 0.10 | 0.00 |
| to H  | 0.00 | 0.00 | 0.10 | 0.80 | 0.10 |
| to VH | 0.00 | 0.00 | 0.00 | 0.10 | 0.90 |

---

## C Vectors

### C[0]: Preferences over o{action}

```
C[0] = [0.0, 0.0]
```

No preference over partner actions.

### C[1]: Preferences over o{payoff}

```
C[1] = log_softmax(payoff_levels / temperature)
```

Ascending preference for higher payoffs.

### C[2]: Preferences over o{intero}

```
C[2] = [0.0, 0.25, 0.5, 0.75, 1.0]  (scaled by preference temperature)
```

Ascending preference for high-precision interoceptive observations.

In the factorized implementation, C[2] does not directly enter EFE for action selection since beta dynamics are action-independent during rollout. The effect of beta on behavior runs through gamma modulation. C[2] is included for a fully joint EFE implementation.

---

## D Vectors

### D[0]: Prior over s{type}

```
D[0] = [0.25, 0.25, 0.25, 0.25]
```

### D[1]: Prior over s{stance}

```
D[1] = [0.2, 0.6, 0.2]  (trusting, neutral, hostile)
```

### D[2]: Prior over s{context}

```
D[2] = [1/N, ..., 1/N]
```

### D[3]: Prior over s{beta}

```
D[3] = [0.05, 0.15, 0.60, 0.15, 0.05]
```

Concentrated at beta = 1.0 (baseline precision, index 2).

---

## E Vector

Uniform. No policy restrictions.

```
Single-step: E = [0.5, 0.5]  (cooperate, defect)
```

For multi-step horizons: enumerate all length-tau sequences over {cooperate, defect}.

---

## Affective Charge and Gamma Modulation

After each trial observation, before next policy selection. Per partner k:

**Step 1 - Prediction error:**

```
eps_k = 1 - P_predicted(observed_action_k)
```

P_predicted comes from the pre-observation belief over (type, stance).

**Step 2 - Affective charge:**

```
phi_k = alpha * (sigma_0^2 - eps_k^2)
```

With alpha=3.0, sigma_0^2=0.25:

```
eps = 0.0  (perfect prediction)  ->  phi = +0.75
eps = 0.5  (baseline)            ->  phi =  0.00
eps = 1.0  (total surprise)      ->  phi = -2.25
```

**Step 3 - Interoceptive observation:**

```
p = sigmoid(phi_k)
o_intero_k = floor(p * 5)    # clipped to [0, 4]
```

**Step 4 - Bayesian update on beta:**

```
prior_k      = B[3] @ posterior_k_prev
likelihood_k = A[2][o_intero_k, :]
posterior_k  = normalize(likelihood_k * prior_k)
```

**Step 5 - Gamma modulation:**

```
E[beta_k] = dot(posterior_k, [0.2, 0.5, 1.0, 1.5, 2.0])
gamma_k   = gamma_base * E[beta_k]
q(pi)     = softmax(-gamma_k * G(pi))
```

In agent_choice mode, gamma is keyed to the first partner implicated by the policy.

---

## Multi-Partner Handling

Rather than a joint factor expansion (4^N x 3^N x 5^N), each partner k maintains separate belief vectors:

```
Posterior over (type, stance): shape (4, 3)
Posterior over beta:           shape (5,)
```

Only the active partner's beliefs update each round.
