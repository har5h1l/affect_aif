# Current Hypotheses

The canonical hypothesis surface is organized as chronological behavior cards:
first ask whether affect can move policy, then ask what it tracks, whether it
changes deployment, and where those changes become visible.

## Mechanism Chain

Hesp et al. model affect as inferred expected precision over action-model
fitness. This project extends that idea from one global action model to multiple
partner-specific social models:

```text
partner prediction reliability
  -> partner-specific precision_k
  -> policy-posterior shift
  -> action or partner-choice behavior
  -> payoff, recovery, or reallocation
```

The affective signal is not partner liking, direct reward history, or literal
trust in the partner. It is trust in the agent's model of that partner. A
predictable exploiter can therefore produce high precision because the agent
knows how to act around them.

Implementation note: beta is the HESP-aligned rate parameter. Low beta means
high expected policy precision. Analyses should report
`precision_k = 1 / E[beta_k]` whenever possible.

Partner-specific beta is an architectural premise of the model. The H3
global-beta condition tests whether per-partner affect is behaviorally superior
to, or mechanistically cleaner than, a shared affective precision state.

Current global-beta discovery read: local beta preserves a cleaner model-fitness signal
than global beta in the focused locality probes, but global beta has higher
aggregate payoff in those same smoke runs. H3 should therefore be treated as an
open decomposition of signal quality versus behavioral allocation, not as
evidence that partner-local beta is necessary.

## H0: Openness Gate

**Mechanism claim:** Affective precision can only change behavior when the
policy posterior has room to move. If the best policy is already effectively
selected, changing precision may move beta without changing action.

**Expected behavior:** Affect effects should be weakest in saturated binary
settings and strongest in regimes with moderate policy uncertainty: shallow
horizons, graded action spaces, betrayal windows, noisy observations, and
agent-choice settings.

**Primary measures:** `q_pi_entropy`, `G_spread`, best-vs-second-best EFE gap,
and policy-posterior shifts such as `KL(q_pi_affect || q_pi_no_affect)`.

**Pass pattern:** Affect payoff, action, or partner-choice effects increase when
policy entropy is moderate or high.

**Failure pattern:** Affect shows no behavioral effect even in open policy
regimes, or effect size is unrelated to policy openness.

## H1: Model Fitness

**Mechanism claim:** Per-partner affect tracks prediction reliability, not how
rewarding the partner is.

**Expected behavior:**

| Partner case | Reward | Predictability | Expected precision |
|---|---:|---:|---:|
| Reliable cooperator | high | high | high |
| Reliable exploiter | low if cooperated with | high | high |
| Volatile ally | medium/high | low | low or unstable |
| Random partner | variable | low | low |

The reliable exploiter is the critical dissociation: high precision should
support confident avoidance, defection, or disengagement, not attraction.

**Primary measures:** `precision_k = 1 / E[beta_k]`, predictive accuracy,
predictive log score or surprise, and partner reward.

**Pass pattern:** Precision is high for reliable cooperators and reliable
exploiters, and low or unstable for volatile partners. Predictive accuracy
dominates reward in partial-correlation or regression analyses.

**Failure pattern:** Precision mostly tracks average payoff, collapsing the
mechanism into cached value.

## H2: Deployment

**Mechanism claim:** Affective precision helps the agent deploy social knowledge
in action. Lesioning the pathway should preserve partner inference while
impairing policy selection, recovery, or partner choice.

This is the computational vmPFC/somatic-marker dissociation: the model should
not claim to implement vmPFC directly, only to reproduce the knowing-versus-
using pattern associated with that literature.

**Expected behavior:** Lesioned agents should infer partner type and stance about
as well as affective agents, but should be worse at choosing actions, choosing
partners, or recovering after a shift.

**Primary measures:** type/stance belief accuracy, predictive log score,
`KL(q_s_affect || q_s_lesion)`, `KL(q_pi_affect || q_pi_lesion)`, payoff,
recovery latency, and partner-choice shift.

**Pass pattern:** Beliefs are similar, while policy distributions and behavior
diverge in an open policy regime.

**Failure pattern:** The lesion damages inference itself, or lesion and affect
behave identically when H0 says the policy space is open.

## H3: Locality / Global Precision

**Mechanism claim:** Partner-local affect should contain model-fitness evidence
to the partner whose model generated it. A shared global beta tracker should
mix reliability evidence across partners and may spread precision changes to
partners whose behavior did not change.

**Expected behavior:** Local beta should preserve the strongest
surprise-over-reward signature at the partner level. After one partner switches
stance, local beta should move mainly for that partner, while global beta should
change policy precision for all candidate partners.

**Primary measures:** global beta, partner-local beta or terminal signal,
selected-partner distribution, policy entropy conditional on selected partner,
payoff conditional on selected partner, partner-level precision-surprise versus
precision-payoff associations, and policy-posterior shifts for untouched
partners.

**Pass pattern:** Global beta produces measurable cross-partner interference
after a localized social shock, or weakens the partner-level model-fitness
signature relative to local beta.

**Failure pattern:** Global beta matches partner-local beta across the same
readouts, suggesting that the current partner-local implementation is
interpretable but not necessary under this task design.

**Current discovery pattern:** Local beta has the stronger
surprise-over-reward signature, but this cleaner signal has not yet produced
better allocation or payoff than global beta in five-seed locality smokes.

## H4: Social Allocation

**Mechanism claim:** Partner-specific precision should guide whom the agent
approaches, avoids, probes, or returns to in agent-choice settings.

**Expected behavior:** Partner choice should not be uniform. High precision does
not always mean approach: a reliable exploiter should be confidently avoided or
defected against, while an uncertain partner may be probed when epistemic value
is useful.

**Primary measures:** selection entropy, `P(select k)` as a function of
`precision_k x expected_payoff_k`, avoidance of reliable exploiters, probing
rate for uncertain partners, and return latency to recovered partners.

**Pass pattern:** Partner choice is systematically related to partner-specific
precision and expected value.

**Failure pattern:** Partner choice is unrelated to partner-local precision in
agent-choice settings.

## H5: Timescale / Volatility

**Mechanism claim:** Affective precision helps when partner regularities persist
long enough for partner beliefs and beta to stay aligned. It becomes risky when
social change is faster than belief recalibration.

**Expected behavior:** After a betrayal or hostile stance switch, the affective
agent should show a prediction-error spike, precision drop for the affected
partner, faster policy change, and either faster recovery/reallocation or a
measurable boundary-condition failure when precision sharpens the wrong
post-switch model. Gradual shifts should be less harmful than abrupt shifts
because belief and beta can stay better synchronized.

**Primary measures:** post-switch windows, surprise spike, partner-specific
precision reaction time, recovery latency, post-switch payoff, partner
reallocation, return latency to the switched partner, payoff conditional on
re-encounter, low-entropy wrong action/belief rates, belief recalibration, and
beta-lag relative to belief change.

**Pass pattern:** Affect effects are amplified around volatility windows, either
as better post-switch action deployment or as a boundary-condition pattern:
lower entropy but higher wrong-type, wrong-action, or low-entropy bad-outcome
rates after an abrupt switch.

**Failure pattern:** Affect effects are not amplified by volatility, and the
recovery/reallocation plus misdeployment readouts are all flat.

## H6: Perturbation Phenotypes

**Mechanism claim:** Clinical-like variants are perturbations of precision
dynamics, not validated clinical diagnoses.

**Expected behavior:**

| Variant | Parameter idea | Precision behavior | Visible behavior |
|---|---|---|---|
| Alexithymia-like | blunted update | barely moves | misses real shifts; may resist noise |
| Borderline-like | high gain or low smoothing | swings too fast | unstable choice and high action churn |
| Depression-like | pessimistic initial precision | starts low-confidence | early caution or avoidance |
| Slow-updating | high persistence | lags reality | delayed recovery after changes |

**Primary measures:** precision mean, variance, autocorrelation, reaction time to
surprise, partner-selection entropy, action-flip rate, recovery latency, and
payoff after precision dynamics are confirmed.

**Pass pattern:** Perturbations separate first in beta/precision dynamics and
become behaviorally visible mainly in open policy regimes.

**Failure pattern:** Behavior differs without the intended precision dynamics,
or precision dynamics do not differentiate.

## H7: Signal Source

**Mechanism claim:** Partner-action surprisal is the canonical affect update
because partner action is the direct social model-fitness signal. Joint
action-plus-payoff surprisal is an exploratory alternative that may mix social
predictability with reward structure.

**Expected behavior:** Partner-action surprisal should preserve the reliable
exploiter dissociation: predictable but low-payoff partners can still produce
high precision. A joint surprise signal may pull precision toward payoff or
action-outcome value and weaken the H1 model-fitness dissociation.

**Primary measures:** precision-surprise association, precision-payoff
association, reliable-exploiter precision, deployment effects, and payoff in
matched H1/H2 settings.

**Current status:** Future-work or exploratory. The supported runtime currently
uses partner-action surprisal.

## H8: Observation Noise / Robustness

**Mechanism claim:** Affective precision may stabilize behavior under noisy
observations by integrating reliability evidence more slowly than trial-level
belief updates, but the same inertia may slow adaptation when noise is confused
with real partner change.

**Expected behavior:** Under moderate observation noise, local beta should reduce
action churn and preserve partner-selection structure when the underlying
partner is stable. Under high noise or real shifts, excess inertia may delay
recalibration.

**Primary measures:** observation-noise level, beta volatility, policy entropy,
action-flip rate, predictive log score, partner-selection entropy, and payoff
conditional on stable versus switched partners.

**Current status:** Exploratory. Observation noise is supported by configs, but
the manuscript does not depend on this lane.

## Engineering Objectives

### E1: Trust-Task Evaluation Arena

AIF agents versus scripted baselines are a task evaluation surface, not a
separate external benchmark.

### E2: Multi-Focal Emergent Dynamics

AIF agents interacting with each other remain descriptive until a specific
hypothesis is promoted.
