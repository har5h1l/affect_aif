# Supplement: Model Specification

## Runtime Boundary

The supported runtime is official `inferactively-pymdp==1.0.0`. Project code
constructs trust-game matrices, manages partner-local agents, updates the
external affective beta tracker, and logs analysis fields. The repository does
not provide a custom active-inference engine.

## Per-Partner POMDP

Each tracked partner has one partner-local `pymdp.Agent` built from
`tasks.trust.pomdp.build_trust_pomdp_template(...)`.

Hidden-state factors:

| Factor | States | Role |
|---|---:|---|
| Partner type | cooperator, reciprocator, exploiter, random | latent behavioral category |
| Partner stance | trusting, neutral, hostile | partner disposition toward focal agent |
| Own action | binary action or graded investment level | deterministic bookkeeping factor for payoff likelihood |

Observation modalities:

| Modality | Outcomes | Depends on |
|---|---:|---|
| Partner action | cooperate/defect | type x stance |
| Payoff | payoff levels from task matrix | own action x type x stance |

The environment realizes payoff deterministically from joint actions; the
agent's likelihood marginalizes partner action through the type-by-stance
cooperation table.

## Controls

Partner-local policies use factorized controls:

```text
[1, num_social_actions, num_social_actions]
```

The first dimension is a singleton partner-control placeholder. The second
dimension controls stance transitions during planning. The third controls the
executed own action and payoff likelihood. Binary games use
`num_social_actions = 2`; graded games use the configured investment levels.

Agent-choice runs evaluate candidate policies for each partner-local agent and
select the final environment action in `tasks.trust.runtime.select_decision`.

## Affective Precision Tracker

Beta is external to the POMDP. After observing partner action for partner `k`,
the tracker computes:

```text
surprise_k = -log(P_predicted(observed_partner_action))
charge_k = alpha_charge * (sigma_0_sq - surprise_k^2)
q(beta_k) <- normalize(likelihood(charge_k | beta_level) * T_beta q(beta_k))
gamma_k = gamma_base / E[beta_k]
```

Low beta means high expected policy precision. High beta means lower policy
precision and more diffuse policy selection.

## Lesion

The tracked-only lesion keeps beta updates but decouples beta from action by
forcing policy precision to `gamma_base`. This tests deployment: the agent can
maintain the affective state but cannot use it to sharpen or soften policy
selection.

## Alignment Notes

The model follows the reference trust notebook for factorized controls and
matrix conventions, while using official `pymdp` as the runtime dependency.
Detailed engineering notes remain in:

- `docs/theory/pomdp_spec.md`
- `docs/design/implementation.md`
- `docs/decisions/architecture.md`
