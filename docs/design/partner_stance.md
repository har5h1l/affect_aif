# Action-Dependent Partner Dynamics

This document records the action-dependent stance redesign that is now part of
the supported trust-task architecture. Older design notes that argued for this
change are historical; the implemented surface is summarized here.

## Current Design

Each partner has:

- a latent behavioral `type`: cooperator, reciprocator, exploiter, or random
- a latent `stance`: trusting, neutral, or hostile

Partners are implemented as **environment-side parameterized policies**, not as
active-inference agents. They sample cooperate/defect from
`P(action | type, stance)` and update stance reactively from the focal agent's
actions. The focal agent maintains partner-local beliefs over `type x stance`
via `pymdp.Agent`. Stance is the partner's disposition toward the agent, not
the agent's own attitude. The agent influences stance through its actions, but
does not observe stance directly.

## Generative Model

The supported POMDP template is `tasks.trust.pomdp.build_trust_pomdp_template`.
The canonical matrix specification is `docs/theory/pomdp_spec.md`.

Hidden/control factors:

- `s_type`: partner type, slowly drifting
- `s_stance`: partner stance, action-dependent
- `s_own`: deterministic bookkeeping for the agent's executed own action

Observation modalities:

- `o_action`: observed partner action
- `o_payoff`: observed payoff

Binary trust games use factorized controls:

- partner choice, when `assignment_mode = "agent_choice"`
- stance-directed social control
- own action

Environment action encoding follows `partner * 4 + stance * 2 + own`.

## Stance Dynamics

Cooperation tends to move the partner toward trusting; defection tends to move
the partner toward hostile. The transition matrices are intentionally
asymmetric: trust builds gradually and erodes quickly.

Scheduled betrayal-style disruptions should use `scheduled_stance_switches`,
not old round-count exploiter phases or `scheduled_type_switches`, unless the
experiment is explicitly about exogenous type volatility.

## Why This Matters

The redesign makes social planning structurally meaningful: action sequences can
change future partner stance, so policy horizon and stance dynamics are part of
the task rather than incidental implementation details.

It also clarifies the affect claim. Affective precision does not replace
planning depth. It provides partner-local model-fitness information that changes
how strongly the agent deploys its current social model into policy selection.

## Current Evidence

Current results should be read through `docs/results/current.md`:

- H0: openness gates whether precision can move behavior
- H1: precision tracks predictive reliability more than reward
- H2: affect changes deployment while preserving much of partner inference
- H3: stress exposes a misdeployment boundary condition
- H4: partner-local precision changes social choice
- H5: perturbation variants separate first in precision dynamics

Older claims about "depth is irrelevant," reward-average C-condition
comparisons, or pre-cutover JAX/custom-engine implementation plans are archive
material only.
