# Current Hypotheses

The old H1-H5/H7 labels are replaced by hypotheses that follow directly from
the Hesp-to-multi-agent extension.

## H1: Model Fitness, Not Reward

Per-partner affect tracks how reliable the agent's model of a partner is, not
how rewarding that partner is. Reliable cooperators and reliable adversaries can
both produce high model-fitness signals. Volatile partners should produce low or
unstable signals.

## H2: Partner Factorization

Per-partner affect should preserve social structure that a global affect signal
collapses. Multi-agent environments require knowing which partner is predictable,
not merely whether the world is globally predictable.

## H3: Deployment, Not Knowledge

Lesioning affect should preserve partner inference while impairing action
deployment. The Damasio-style dissociation is: partner type or stance beliefs
remain intact, but payoff, recovery, or partner choice worsens.

## H4: Social Volatility

Affect should matter most under betrayal, stance shifts, partner volatility,
noisy observations, or changing partner pools. Stable tasks may under-express
the mechanism.

## H5: Partner Selection

Per-partner affect should guide whom the agent chooses, avoids, probes, or
returns to in agent-choice settings.

## H6: Policy-Space Regime

Affect only changes behavior when the policy posterior has room to move.
Saturated binary settings can hide the mechanism. Shallow horizons, graded
action spaces, volatile environments, and multi-partner choices should expose it
more strongly.

## H7: Clinical Perturbations

Clinical-like regimes are perturbations of affective precision dynamics: frozen
precision, volatile precision, low-baseline precision, or slow-updating
precision. They should separate by task regime, not as global traits that behave
identically everywhere.

## Engineering Objectives

### E1: Trust-Task Evaluation Arena

AIF agents versus scripted baselines are a task evaluation surface, not a
separate external benchmark.

### E2: Multi-Focal Emergent Dynamics

AIF agents interacting with each other remain descriptive until a specific
hypothesis is promoted.
