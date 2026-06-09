# Trust POMDP

Public specification for the trust-game generative model and runtime. The
implementation uses official `inferactively-pymdp==1.0.0` `pymdp.Agent`
instances. Project code constructs matrices, manages partner-local runtime
state, and logs diagnostics.

## Scope

The reported experiments use one focal active-inference agent interacting with
environment-side scripted partners. Partners sample from type-by-stance
cooperation tables, update stance reactively from the focal agent's actions,
and support scheduled switches — but they do not run pymdp, expected free
energy, or affective precision.

Each social partner has a partner-local POMDP. In agent-choice tasks, the
runtime evaluates partner-local candidate policies and then executes the chosen
partner/action in the trust-game environment. Partner-local beta lives outside
the generative model; see `affective_precision.md`.

Reciprocal AIF-vs-AIF partners are future work (`experiments/multifocal/`).

## Hidden State Factors

| Factor | States | Controllable? | Role |
|---|---|---|---|
| `s_type` | cooperator, reciprocator, exploiter, random | no | Partner behavioral tendency. |
| `s_stance` | trusting, neutral, hostile | yes | Partner disposition toward the focal agent. |
| `s_own` | action/investment level | yes | Deterministic bookkeeping for the focal agent's own action. |

`s_own` is deterministic bookkeeping so payoff fits standard pymdp form — not a
substantive latent variable. Stance is the **partner's** disposition toward the
focal agent: influenced by the agent's actions, inferred not directly observed.

Joint state space per partner: 4 types × 3 stances × 2 own actions = 24 states
(binary games; graded games expand the own-action factor).

`B[0]` is near-identity with small type drift (`p_switch ≈ 0.05`) unless a
scenario injects scheduled type switches.

## Observation Modalities

| Modality | Outcomes | Depends on |
|---|---|---|
| `o_action` | partner response | `s_type`, `s_stance` |
| `o_payoff` | discrete payoff category | `s_own`, `s_type`, `s_stance` |

Binary games use cooperate/defect and four payoff levels `[-1, 1, 3, 5]` from
the standard trust-game table:

| | partner cooperates | partner defects |
|---|---|---|
| agent cooperates | 3 | -1 |
| agent defects | 5 | 1 |

Graded games use configured investment levels, endowment, and multiplier.

In the environment, payoff is deterministic from joint actions. In the generative
model, `A[1]` conditions payoff on own action and latent partner state while
marginalizing partner response through `A[0]` — a reduced representation that
preserves the incentive landscape, not a claim that payoff is stochastic in the
world.

### A[0]: Partner cooperation probabilities

`A[0] = P(o_action | s_type, s_stance)`. Default cooperate probabilities:

| type | trusting | neutral | hostile |
|---|---:|---:|---:|
| cooperator | 0.95 | 0.80 | 0.55 |
| reciprocator | 0.90 | 0.70 | 0.30 |
| exploiter | 0.70 | 0.35 | 0.10 |
| random | 0.60 | 0.50 | 0.35 |

`P(defect) = 1 - P(cooperate)`. Optional observation noise mixes toward 0.5.

### A[1]: Payoff likelihood

For each `(s_own, s_type, s_stance)`, marginalize partner action through `A[0]`
and map the resulting payoff to the discrete payoff modality.

## Control Factors

Partner choice is external to each partner-local POMDP. The runtime evaluates
candidate policies per partner in `select_decision(...)`, then executes the chosen
`(partner, stance_action, own_action)`.

| Control | Role |
|---|---|
| Partner choice (external) | which partner is engaged |
| Stance control | action-dependent `B[1]` transitions |
| Own action | deterministic `B[2]` update and payoff branch |

Binary control shape per partner-local agent:
`[1, num_social_actions, num_social_actions]`. Agent-choice mode compares
partner-local policy branches with centered `gamma_k`-scaled logits before
encoding the environment action.

Rollout uses the stance-control column for generative stance transitions during
planning; the environment updates observed stance from the executed own action.

## B Matrices

`B[1] = P(s_stance' | s_stance, action)` is action-dependent — this is what
makes deeper planning structurally informative.

**Cooperate / higher investment:**

| to \\ from | trusting | neutral | hostile |
|---|---:|---:|---:|
| trusting | 0.90 | 0.30 | 0.05 |
| neutral | 0.10 | 0.60 | 0.35 |
| hostile | 0.00 | 0.10 | 0.60 |

**Defect / lower investment:**

| to \\ from | trusting | neutral | hostile |
|---|---:|---:|---:|
| trusting | 0.10 | 0.05 | 0.02 |
| neutral | 0.50 | 0.35 | 0.18 |
| hostile | 0.40 | 0.60 | 0.80 |

Cooperation gradually builds trust; defection destroys it faster; recovery from
hostile is slow.

`B[2] = P(s_own' | action)` deterministically records the chosen action.

## C, D, And E

`C[0]` over partner action is zero — no direct preference over partner responses.
`C[1]` encodes ascending preference over payoff levels via scaled log preferences.

Default `D`: uniform partner type; stance prior centered on neutral
(`[0.2, 0.6, 0.2]`); uniform own-action bookkeeping.

`E` is uniform unless a config introduces an explicit policy prior.

## Multi-Partner Runtime

The focal agent maintains **K parallel partner-local pymdp agents**:

- shared A/B/C/E templates
- per-partner type/stance posteriors and beta trackers
- one shared own-action bookkeeping state
- only the engaged partner's beliefs update each round

Random assignment fixes the active partner externally; agent-choice evaluates
all partner branches before selection.

## Action-Perception Cycle

Each round:

1. Select the active partner or evaluate partner-local candidate policies.
2. Set partner-local policy precision from beta when affective precision is
   enabled.
3. Call `pymdp.Agent.infer_policies(...)` and choose an action.
4. Step the trust-game environment (`tasks/trust/envs/`).
5. Update partner-local beliefs with `infer_states(...)`.
6. Update external beta from prediction error and log diagnostics.

Policy posterior openness (`q_pi_entropy`, EFE spread) determines whether
affective precision can change behavior — the posterior must have room to move.

Partner-side implementation: `tasks/trust/envs/partners.py`, stance helpers in
`tasks/trust/stance.py` and `tasks/trust/types.py`.

## Affective Precision Boundary

Partner-local beta is external to the POMDP state space:

```text
gamma_k = gamma_base / E[beta_k]
```

The tracked-only lesion updates beta but does not feed it into `gamma_k`.
See `affective_precision.md` for the update law, modes, and lesion table.

## Implementation Pointers

- POMDP construction: `tasks/trust/pomdp.py`
- Runtime selection/update loop: `tasks/trust/runtime.py`
- Affective precision tracker: `tasks/trust/affect.py`
- Config expansion and execution: `experiments/trust/`
- Public configs: `configs/paper/`, `configs/demo/`, `configs/diagnostics/`
