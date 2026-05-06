# Action-Dependent Partner Dynamics: Design Specification

## 1. Motivation

The current system uses action-independent partner dynamics. The B matrix for partner type is identical across all agent actions — cooperating or defecting has no effect on hidden state transitions. Partner behavior depends on agent actions only through the A matrix (reciprocators mirror, exploiters switch at a fixed round number).

This means planning depth is structurally uninformative: looking further ahead reveals no new state transitions, just the same p_switch drift. The "depth is irrelevant" finding from the MVP is likely a structural artifact of this design, not a property of the domain.

External review (Andrew Pashea, 2026-03-30) identified this as the central architectural issue. The orthogonal augmentation claim rests on a domain where depth was never going to help.

### What Changes

This design replaces the action-independent partner model with one where partners do Bayesian inference about the agent and adapt their behavior accordingly. This creates:

- Action-dependent state transitions (the agent's behavior shapes the partner's future behavior)
- A harder inference problem (the agent must jointly infer partner type AND partner disposition)
- Meaningful planning depth (looking ahead reveals different futures depending on action sequences)
- A more defensible experimental foundation for the affect-as-orthogonal-augmentation claim

### The New Story

**Claim:** In social environments where partners adapt to your behavior, per-partner affective precision tracking provides orthogonal value beyond what planning depth alone recovers — even when deeper planning is genuinely informative.

This replaces "depth is irrelevant, affect substitutes" with "depth matters, and affect still adds something on top that more lookahead cannot substitute for."

---

## 2. Partner-Side Design (Ground Truth Environment)

Each partner has two components:

### 2.1 Fixed Type (Exogenous)

Same as before: cooperator, reciprocator, exploiter, random. Determines base behavioral tendencies. Subject to stochastic type switches (p_switch) for volatility.

### 2.2 Stance (Endogenous, New)

Three discrete states: **trusting**, **neutral**, **hostile**.

Determined by the partner's Bayesian inference about the agent. The partner maintains a posterior over agent character types:

- P(agent = cooperative)
- P(agent = exploitative)
- P(agent = unreliable)

### 2.3 Partner's Bayesian Update

After each interaction, the partner updates its posterior based on the agent's observed action:

- Agent cooperates: likelihood ratio favors cooperative agent type
- Agent defects: likelihood ratio favors exploitative agent type
- Mixed/inconsistent pattern: likelihood ratio favors unreliable agent type

The specific likelihood model:

```
P(agent_cooperates | agent_type=cooperative)   = 0.85
P(agent_cooperates | agent_type=exploitative)  = 0.15
P(agent_cooperates | agent_type=unreliable)    = 0.50
```

Partner starts with a uniform prior over agent types: [1/3, 1/3, 1/3].

### 2.4 Posterior-to-Stance Mapping

The partner's posterior over agent types maps to a discrete stance:

- P(agent = cooperative) > 0.6 --> **trusting**
- P(agent = cooperative) < 0.3 --> **hostile**
- Otherwise --> **neutral**

### 2.5 Stance-Conditioned Behavior

The partner's action probability depends on both their fixed type and their current stance:

| Type | Trusting | Neutral | Hostile |
|------|----------|---------|---------|
| Cooperator | P(C)=0.95 | P(C)=0.80 | P(C)=0.55 |
| Reciprocator | mirrors + bonus (P mirror=0.90) | mirrors exactly (P mirror=0.85) | mirrors + penalty (P mirror=0.70, bias toward defect) |
| Exploiter | exploits aggressively (high early coop, sharp betrayal) | standard exploit schedule | mutual defect (P(C)=0.10) |
| Random | P(C)=0.60 | P(C)=0.50 | P(C)=0.35 |

### 2.6 Asymmetric Dynamics

Trust builds slowly and erodes quickly:

- Trusting --> neutral: 1 defection shifts the posterior enough (single strong evidence against cooperative)
- Neutral --> trusting: requires 3-4 consecutive cooperations (gradual posterior accumulation)
- Neutral --> hostile: 2-3 defections
- Hostile --> neutral: requires 4-5 cooperations (hard to recover from)
- Trusting --> hostile: possible in 2 defections (rapid collapse)

This asymmetry emerges naturally from the Bayesian update structure — a single defection is strong evidence against a cooperative agent type, while a single cooperation is weaker evidence for it (exploitative agents also cooperate sometimes).

### 2.7 Stance-Conditioned Exploitation

The exploiter behavior is stance-conditioned:

- A trusting stance gives the exploiter more to exploit (the partner cooperates more, creating higher-stakes betrayal)
- The exploiter's behavioral shift happens when the agent's trust has been established, not at an arbitrary round number
- This is more naturalistic: real exploitation targets trust, not round counts

---

## 3. Agent-Side Design (Generative Model)

### 3.1 Hidden State Factors

- **Factor 1: Partner type** — (cooperator, reciprocator, exploiter, random). 4 states.
- **Factor 2: Partner stance** — (trusting, neutral, hostile). 3 states. **New.**
- **Factor 3: Interaction context** — (which partner). N states. Same as before.

Total hidden state space per partner: 4 types x 3 stances = 12 joint states.

### 3.2 A Matrix (Likelihood)

Observation probabilities depend on type x stance.

A[0] (partner action observation): shape (2, num_types, num_stances)
- For each type-stance combination, P(partner cooperates) and P(partner defects)
- Populated from the stance-conditioned behavior table in Section 2.5

A[1] (payoff observation): shape (num_payoff_levels, num_social_actions, 2)
- Same structure as before — deterministic mapping from (agent_action, partner_action) to payoff

### 3.3 B Matrix (Transitions)

**B[0] — Partner type transitions:** Mostly action-independent, as before. The agent's actions don't change what type someone fundamentally is. Small p_switch for environmental volatility.

Shape: (num_types, num_types, num_actions)
All action slices are identical (same as current design).

**B[1] — Partner stance transitions: ACTION-DEPENDENT.** This is the critical change.

Shape: (num_stances, num_stances, num_actions)
Different transition matrices for cooperate vs defect.

B_stance for cooperate:
```
             from_trusting  from_neutral  from_hostile
to_trusting      0.90          0.30          0.05
to_neutral       0.10          0.60          0.35
to_hostile       0.00          0.10          0.60
```

B_stance for defect:
```
             from_trusting  from_neutral  from_hostile
to_trusting      0.10          0.05          0.02
to_neutral       0.50          0.35          0.18
to_hostile       0.40          0.60          0.80
```

These encode: cooperating builds trust gradually, defecting destroys trust quickly, recovery from hostility is slow.

**B[2] — Interaction context:** Same as before (which partner is active).

### 3.4 C Matrix (Preferences)

Same structure as before. The agent prefers cooperative partner actions and high payoffs.

### 3.5 D Matrix (Priors)

- Type: uniform over 4 types
- Stance: prior centered on neutral (e.g., [0.2, 0.6, 0.2])
- Context: uniform over partners

### 3.6 Inference

The agent performs joint inference over type and stance from observations. After each round:

1. Observe partner action and payoff
2. Compute likelihood under each (type, stance) combination
3. Update joint posterior over type x stance
4. Apply B matrix to get predictive prior for next encounter (action-dependent for stance)

The inference problem is now harder than before: observing a partner defect could mean:
- "This is an exploiter" (type inference)
- "This is a reciprocator who has become hostile toward me" (stance inference)
- "This is a cooperator who is wary of me" (type + stance)

Disambiguating requires tracking the interaction history and the agent's own past actions.

### 3.7 Planning

With action-dependent B_stance, deeper planning is now informative:

- **Horizon 1:** "What should I do right now given current beliefs?"
- **Horizon 3:** "If I cooperate for 3 rounds, the stance shifts toward trusting, improving future outcomes"
- **Horizon 6:** "I can absorb short-term cost to build trust with a reciprocator, because the long-term payoff from a trusting reciprocator exceeds the investment"

The agent can now discover trust-building and trust-repair strategies through planning. This is the kind of temporal credit assignment that makes depth meaningful.

---

## 4. Why Affect Remains Orthogonal

Even with deep planning and action-dependent B, the agent faces meta-uncertainty that depth cannot resolve:

### 4.1 Type-Stance Confounding

A partner defection is ambiguous: hostile reciprocator or normal exploiter? The agent's predictions will be wrong until it resolves this ambiguity. Beta tracks "are my predictions about this partner still calibrating?" — a fast summary that complements the slower joint posterior update.

### 4.2 Stance Transition Stochasticity

The B_stance matrix is probabilistic, not deterministic. Even if the agent cooperates, the partner might not shift to trusting (the Bayesian update depends on the partner's full interaction history, not just the last action). Beta tracks whether the expected stance dynamics are actually playing out.

### 4.3 Asymmetric Damage Detection

One defection can destroy trust that took many rounds to build. The affective state provides a fast "something changed" signal — a spike in prediction error — before the agent's type-stance posterior has fully adjusted. This is especially valuable when the agent has high confidence in a wrong belief (e.g., "this partner is a trusting cooperator" right before they become hostile).

### 4.4 Multi-Partner Tracking

With 4+ partners whose stances are evolving independently (each based on their own Bayesian inference about the agent), the agent needs a quick per-partner summary of "how stable is my model of this partner right now?" Beta provides this without requiring explicit reasoning about each partner's inference process.

---

## 5. Experimental Design

### Experiment 1: Depth Matters

**Goal:** Validate that the new environment makes planning depth informative.

**Design:** Compare planning horizons tau=1, 2, 4, 8 (no affect) across 50-100 seeds, 200 rounds.

**Prediction:** Deeper planning should yield measurably better cumulative payoff when stance transitions make trust-building sequences available. The agent at tau=4+ can discover trust-building sequences; tau=1 cannot.

**Key metric:** Cumulative payoff by depth. Effect size of tau=1 vs tau=8.

### Experiment 2: Affect is Orthogonal to Depth

**Goal:** The core finding. Affect adds value on top of depth, not as a substitute.

**Design:** Full factorial: depth (tau=1, 2, 4, 8) x affect (on/off). 50-100 seeds, 200 rounds.

**Prediction:** Main effect of depth (deeper is better). Main effect of affect (affect is better). No interaction (affect benefit is roughly constant across depths). Both main effects are significant; the interaction is not.

**Key metric:** 2-way ANOVA. Effect sizes for depth, affect, and interaction.

### Experiment 3: Lesion Dissociation (Damasio Pattern)

**Goal:** Replicate the somatic marker deficit pattern in the richer environment.

**Design:** Full agent, no-affect, no-epistemic, reward-average lesions. 50-100 seeds, 200 rounds.

**Prediction:** No-affect agents have intact type-stance inference but fail to adapt quickly to stance changes. They know what's happening but can't deploy that knowledge efficiently. Same qualitative pattern as the Iowa Gambling Task dissociation.

### Experiment 4: Volatility and Betrayal

**Goal:** Test affect's value in detecting and recovering from trust violations.

**Design:** Scheduled disruptions — partner builds trust for 50 rounds, then the agent is forced to defect (or a partner type switch occurs), collapsing the stance. Test recovery dynamics.

**Prediction:** Affective agents detect the trust collapse faster (via prediction error spike in beta) and re-allocate to other partners or begin trust repair sooner.

### Experiment 5: Clinical Profiles

**Goal:** Differentiated clinical trajectories in the richer environment.

**Design:** Alexithymia (dampened beta updates), borderline (amplified beta), depression (negative beta bias). Same environment, 100 seeds, 200 rounds.

**Predictions:**
- Alexithymia: fails to detect stance shifts, continues interacting with hostile partners
- Borderline: overreacts to normal stance fluctuations, destabilizes trust through erratic behavior
- Depression: negative bias prevents recognizing when trust has been established, under-exploits trusting partners

### Experiment 6: Precision Tracking vs Reward Averaging

**Goal:** Show when precision tracking (beta) outperforms reward averaging.

**Design:** Conditions where a partner's stance shifts but payoffs haven't changed yet (e.g., a reciprocator just became wary — predictions are now wrong, but last round's payoff was still fine).

**Prediction:** Precision tracking detects the stance shift immediately (prediction error spikes). Reward averaging lags because payoffs haven't changed yet. This is the scenario where the two mechanisms dissociate most cleanly.

---

## 6. Codebase Changes

| Component | Change | Scope |
|-----------|--------|-------|
| `generative_model/partner_types.py` | Add stance-conditioned behavior tables for each type | Moderate |
| `environment/partner.py` | Add Bayesian inference over agent type, posterior-to-stance mapping, stance-conditioned action selection | Major |
| `generative_model/model.py` | New hidden factor (stance), action-dependent B_stance, updated A matrix for type x stance | Major |
| `core/rollout.py` | B matrix indexing uses action for stance factor; planning propagates stance beliefs forward | Major |
| partner bank | Stores joint inference over type + stance in PartnerBank snapshots | Major |
| `environment/trust_game.py` | Pass stance information through step results for logging | Minor |
| `configs/` | New experiment configs for all 6 experiments | Moderate |
| `analysis/hypotheses.py` | Updated hypothesis definitions | Moderate |
| `analysis/` | Updated metrics for stance inference accuracy | Moderate |
| `tests/` | New tests for stance dynamics, action-dependent transitions, joint inference | Major |

---

## 7. What We Drop

- All existing experiment results (they used action-independent B; they become development history)
- The "depth is irrelevant" framing and the flat depth curve as a finding
- Phase/round-dependent exploiter behavior (replaced by stance dynamics)
- The binary last_action conditioning in the A matrix (replaced by stance conditioning)

## 8. What We Keep

- The affective beta mechanism and its variational grounding (Hesp et al.)
- The core claim structure: orthogonal augmentation
- Clinical profile framework (alexithymia, borderline, depression)
- JAX implementation
- Most of the analysis and statistics pipeline
- The hypothesis testing framework (updated hypotheses, same statistical machinery)

## 9. Open Questions

1. **Exact transition probabilities for B_stance:** The values in Section 3.3 are illustrative. Need to calibrate so that (a) depth effects are detectable but not overwhelming, (b) stance shifts happen at a rate that interacts meaningfully with planning horizons of 2-8.

2. **Graded vs binary actions:** The current system supports both binary (cooperate/defect) and graded (investment levels) games. The stance mechanism works naturally with binary. For graded, the partner's Bayesian update would treat investment level as evidence strength (higher investment = stronger evidence for cooperative). Need to decide whether to support graded from the start or add it later.

3. **Partner's prior over agent types:** Starting at uniform [1/3, 1/3, 1/3] is the default. Could also vary this across partner types (e.g., a reciprocator starts more neutral, a cooperator starts slightly trusting). This adds another parameter to tune.

4. **Interaction between type switches and stance:** When a partner's type switches (stochastic volatility), does the stance reset? The partner's Bayesian inference about the agent is independent of the partner's own type, so the stance should persist through type switches. But this means a hostile-cooperator could exist after a type switch, which is unusual. Need to decide.

5. **Agent's model accuracy:** Should the agent's B_stance match the ground truth transition dynamics exactly, or should there be a model mismatch? Exact match is cleaner for the initial experiments. Mismatch is more realistic and could be explored later.
