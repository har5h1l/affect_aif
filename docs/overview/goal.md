# Hypotheses

## Project Goal

This project extends Hesp et al.'s affect-as-expected-action-precision account
into multi-partner social active inference by factorizing model-fitness estimates
over partners. The central question is when partner-specific precision signals
help a focal agent deploy otherwise available social knowledge, choose partners,
and recover under social uncertainty — not whether affect simply replaces
planning or monotonically improves reward.

Affect is partner-specific model fitness updated from partner-action surprisal
and deployed as inverse-beta policy precision. The trust task is a testbed for
social inference under volatility with a focal AIF agent against scripted
partners. Clinical-like variants perturb precision dynamics; they are not
validated diagnoses.

## Mechanism Chain

Behavior cards are ordered mechanistically: can affect move policy (H0), what
does it track (H1), does it change deployment (H2), is the signal
partner-local (H3), where does it reorganize behavior (H4–H5), and how do
parameter profiles vary (H6).

```text
partner-action predictability
  -> partner-local q(beta_k)
  -> policy precision gamma_k
  -> policy posterior / action / partner choice
  -> payoff, recovery, or reallocation (downstream)
```

The affective signal is trust in the agent's **model of a partner**, not partner
liking or cached reward. A predictable exploiter can carry high precision because
the agent knows how to act around them.

Payoff is downstream of calibration interacting with task structure. Report
`precision_k = 1 / E[beta_k]` in analyses (lower beta = higher precision).

## Spine Table

| ID | Role | Primary measures |
|---|---|---|
| H0 | Policy openness: precision matters only when the policy posterior can move. | `q_pi_entropy`, EFE spread, `KL(q_pi)` shifts |
| H1 | Model fitness: beta tracks predictability over partner value or reward. | surprise vs payoff partials, `precision_k` |
| H2 | Deployment: tracked-only separates inference from action confidence. | belief match, policy/entropy divergence |
| H3 | Locality: partner-local beta gives cleaner signals than shared beta. | partner-level surprise-over-payoff |
| H4 | Social allocation: precision reorganizes partner choice. | selection entropy, cooperator/exploiter mix |
| H5 | Volatility: abrupt change tests deployment under temporal shift. | post-switch entropy, accuracy, payoff |
| H6 | Profile-style variation: gain and prior shape computational profiles. | beta dynamics, reengagement, payoff |

Exploratory lanes H7 (signal source) and H8 (observation noise), plus reciprocal
AIF and benchmark extensions, are listed in `docs/future.md`. The supported
runtime uses partner-action surprisal only.

## H0: Openness Gate

**Claim:** Affective precision can change behavior only when the policy posterior
has room to move. Saturated binary settings may update beta without changing action.

**Regimes:** graded action spaces, agent-choice, betrayal windows, moderate
horizon — not hard-argmax binary games.

**Pass:** affect effects scale with policy openness. **Fail:** no effect in open
regimes, or effect unrelated to entropy/EFE spread.

## H1: Model Fitness

**Claim:** Per-partner affect tracks prediction reliability, not partner reward.

| Partner case | Reward | Predictability | Expected precision |
|---|---:|---:|---:|
| Reliable cooperator | high | high | high |
| Reliable exploiter | low if cooperated with | high | high |
| Volatile ally | medium/high | low | low or unstable |
| Random partner | variable | low | low |

The reliable exploiter is the critical dissociation: high precision should support
confident avoidance or defection, not attraction.

**Pass:** surprise dominates reward in partial/regression readouts. **Fail:**
precision tracks average payoff alone.

## H2: Deployment

**Claim:** Affect helps deploy social knowledge in action. Tracked-only should
preserve partner inference while impairing policy selection or recovery.

**Pass:** similar beliefs, divergent `q_pi` and behavior in open regimes.
**Fail:** lesion damages inference, or matches full affect when H0 says policy
space is open.

## H3: Locality

**Claim:** Partner-local beta preserves model-fitness evidence at the partner
who generated it; shared beta mixes reliability across partners.

**Pass:** global beta weakens partner-level surprise-over-payoff signature or
produces cross-partner interference after localized shocks. **Fail:** global
matches local on all readouts.

Treat as signal-quality and interpretability evidence unless a dedicated
behavioral necessity comparison is run.

## H4: Social Allocation

**Claim:** Partner-specific precision guides approach, avoidance, probing, and
return in agent-choice settings. High precision does not always mean approach.

**Pass:** partner choice relates to `precision_k` and expected value.
**Fail:** choice unrelated to partner-local precision.

## H5: Volatility

**Claim:** Abrupt social change activates the deployment channel — prediction-error
spike, precision drop, faster policy change — with payoff effects regime-dependent.

**Pass:** amplified post-switch entropy/accuracy/reallocation readouts.
**Fail:** flat volatility-window effects across deployment metrics.

## H6: Profile-Style Variation

**Claim:** Clinical-like variants are precision-dynamics perturbations, not
diagnoses.

| Profile | Parameter idea | Precision behavior |
|---|---|---|
| Alexithymia-like | low `alpha_charge` | barely moves |
| Borderline-like | high gain / low smoothing | swings too fast |
| Depression-like | high `initial_beta` | starts low-confidence |
| Slow-updating | high `beta_persistence` | lags reality |

**Pass:** profiles separate in beta dynamics first, then behavior in open regimes.
**Fail:** behavioral differences without intended precision dynamics.
