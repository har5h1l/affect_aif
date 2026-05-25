# Native pymdp Trust Design

## Decision

Move from a `pymdp`-backed custom agent architecture to a native `pymdp`
architecture.

This is a hard transition. The post-transition codebase should not preserve
the current custom agent/model architecture as a supported surface, fallback
path, compatibility layer, or "just in case" abstraction. If code exists mainly
to make the new architecture look like the old one, remove it.

The end state is:

```text
trust POMDP template -> official pymdp.Agent -> experiment loop
```

not:

```text
trust POMDP template -> TrustGameModel -> TrustGameAgent -> pymdp.Agent -> experiment loop
```

The only custom logic around `pymdp.Agent` should be:

- constructing the trust-game A/B/C/D/E/policy template
- maintaining one `pymdp.Agent` per partner
- tracking external affective precision per partner
- mapping trust-environment results to `pymdp` observations
- producing experiment logs

No custom object should pretend to be the active-inference agent. The agent is
official `pymdp.Agent`.

## Hard Transition Rules

The migration should be performed as a replacement, not as an adapter.

Required:

- Replace custom agent classes with direct `pymdp.Agent` construction and a
  procedural experiment loop.
- Replace `TrustGameModel` as the runtime model object with a native POMDP
  template dataclass or pure template functions.
- Replace `agent.plan_and_act(...)`, `agent.observe_outcome(...)`, and
  `agent.get_metrics()` with explicit runner calls to `pymdp.Agent` and
  snapshot helpers.
- Move or delete every runtime dependency on `tasks.trust.agents.*`.
- Make affect and multi-partner state the only remaining wrappers around
  `pymdp.Agent`.
- Update tests and docs to target the new native surface.

Forbidden:

- no dual architecture
- no backend flag
- no old-class wrappers that delegate to the new procedural implementation
- no compatibility aliases in the documented API
- no import fallbacks from native modules to old agent/model modules
- no tests that require `TrustGameAgent`/`AffectiveAgent`/`LesionedAgent` as
  first-class runtime objects
- no custom state inference, policy inference, expected-free-energy, rollout,
  or policy-sampling logic

Temporary aliases are allowed only inside a single mechanical transition patch
if needed to keep imports resolving while files are moved. They must be removed
before the native migration is considered complete.

## Goals

- Make the trust task feel like idiomatic `pymdp`, similar in spirit to the
  Apashea reference notebook.
- Preserve the scientific logic of the original task exactly unless explicitly
  changed later.
- Keep arrays JAX-native at the `pymdp` boundary.
- Remove legacy-shaped classes that duplicate model, belief, policy, action,
  and diagnostic responsibilities already owned by `pymdp`.
- Keep affect as a small external precision tracker, not as a second agent
  framework.
- Keep multi-partner tracking as a table/list of per-partner `pymdp.Agent`
  instances plus per-partner snapshots.

## Non-goals

- Reinterpret experiment results.
- Change payoff semantics.
- Change stance-transition semantics.
- Change partner-type likelihoods.
- Change HESP beta dynamics.
- Reintroduce custom active-inference inference/planning code.
- Preserve `TrustGameAgent`, `AffectiveAgent`, or `LesionedAgent` as substantive
  agent implementations.

Compatibility aliases may exist for one transition patch only if needed to
avoid breaking imports during the refactor, but the final state should not
require users to instantiate those classes.

## Logic That Must Be Preserved

The native implementation must preserve these existing mechanisms:

- Hidden factors:
  - partner type
  - partner stance
  - own action
- Observation modalities:
  - partner action
  - payoff
- Binary trust-game payoff table:
  - cooperate/cooperate -> 3
  - cooperate/defect -> -1
  - defect/cooperate -> 5
  - defect/defect -> 1
- Payoff observation remains a POMDP modality conditioned on own action,
  partner type, and stance, with partner action marginalized through the
  cooperation table.
- Factorized controls remain:
  - partner choice where applicable
  - stance control
  - own action
- For each local partner `pymdp.Agent`, controls are the single-partner pymdp
  factors needed for stance and own-action planning.
- In agent-choice mode, the runner/orchestrator evaluates partner-local agents
  and chooses a partner plus first-step action without creating a giant global
  product-state POMDP.
- Stance transitions are action-dependent and use the same cooperation evidence
  interpolation as the current implementation.
- Type transitions use the same `p_switch` semantics.
- Initial priors remain:
  - type uniform
  - stance `[0.2, 0.6, 0.2]`
  - own action uniform
- C preferences remain log-softmaxed payoff preferences.
- Beta remains external to the POMDP.
- Beta convention remains HESP inverse-beta:
  - low beta = high expected policy precision
  - high beta = low expected policy precision
  - `gamma_k = gamma_base / E[beta_k]`
- Surprise signal remains:
  - `surprise = 1 - P_predicted(observed_partner_action)`
- Lesion semantics remain:
  - `decouple`: beta updates but does not modulate precision
  - `fixed`: beta does not update and does not modulate precision

## JAX Requirement

The POMDP template should emit JAX arrays at the `pymdp.Agent` boundary:

```python
import jax.numpy as jnp

A: list[jnp.ndarray]
B: list[jnp.ndarray]
C: list[jnp.ndarray]
D: list[jnp.ndarray]
E: jnp.ndarray
policies: jnp.ndarray | np.ndarray accepted by pymdp
```

Use NumPy where it is naturally task-side:

- config parsing
- environment random draws
- payoff tables
- pandas/logging compatibility
- converting logged snapshots to lists

But do not rebuild inference/planning using NumPy.

## Target Code Shape

Recommended structure:

```text
tasks/trust/
├── pomdp.py                 # pure POMDP template construction
├── affect.py                # external beta tracker only
├── partner_state.py         # tiny multi-partner table/snapshot helpers
├── actions.py               # small action encode/decode helpers if payoffs.py is too broad
├── envs/                    # environment remains task-side
├── payoffs.py
├── stance.py
└── types.py

experiments/trust/
├── factory.py               # builds template, agents, env, beta tracker
├── runner.py                # procedural pymdp loop
├── logger.py                # logs snapshots
└── config.py
```

Potentially remove or collapse:

```text
tasks/trust/models/trust_game.py
tasks/trust/agents/base.py
tasks/trust/agents/affective.py
tasks/trust/agents/lesioned.py
tasks/trust/pymdp_helpers.py
```

If `TrustGameModel` survives at all, it should become a thin immutable
`TrustPomdpTemplate` dataclass returned by pure construction functions. It
should not have inference, posterior, transition-update, or prediction methods
that duplicate `pymdp.Agent`.

## POMDP Template API

Create a native template module with a small API:

```python
@dataclass(frozen=True)
class TrustPomdpTemplate:
    A: list[jnp.ndarray]
    B: list[jnp.ndarray]
    C: list[jnp.ndarray]
    D: list[jnp.ndarray]
    E: jnp.ndarray
    policies: jnp.ndarray
    control_fac_idx: tuple[int, ...]
    labels: TrustPomdpLabels
    payoff_values: tuple[float, ...]
    num_obs: tuple[int, ...]
    num_states: tuple[int, ...]
    num_controls: tuple[int, ...]


def build_trust_pomdp_template(
    config: ExperimentConfig | Mapping[str, Any],
    *,
    planning_horizon: int,
    max_policies: int | None = None,
    rng: np.random.Generator | None = None,
) -> TrustPomdpTemplate:
    ...


def create_pymdp_agent(
    template: TrustPomdpTemplate,
    *,
    gamma: float,
) -> pymdp.Agent:
    ...


def create_partner_agents(
    template: TrustPomdpTemplate,
    *,
    num_partners: int,
    gamma: float,
) -> list[pymdp.Agent]:
    ...
```

The template owns static POMDP arrays and labels only. Runtime posterior state
lives in `pymdp.Agent`.

## Multi-Partner Tracking API

Multi-partner state should be a small orchestration object or pure dataclass,
not an agent implementation.

Recommended:

```python
@dataclass
class PartnerBank:
    agents: list[pymdp.Agent]
    latest_qs: list[Any]
    beta: DiscreteBetaState | None
    prior_snapshots: list[Any]
    posterior_snapshots: list[Any]
```

Responsibilities:

- hold the list of `pymdp.Agent` instances
- hold per-partner beta state if affect is enabled
- expose snapshot extraction for logging
- reset per-partner priors between trials if official `pymdp` requires explicit
  empirical prior handling

Non-responsibilities:

- no `act`
- no `observe`
- no custom policy inference
- no custom posterior update
- no custom EFE

The runner can call procedural functions:

```python
plan_partner_action(agent, template, beta_value, action_selection, rng)
update_partner_after_observation(agent, template, obs, own_action)
snapshot_partner_bank(bank, template)
```

These functions should be thin, explicit, and easy to delete if official
`pymdp` makes them unnecessary.

## Experiment Loop Shape

The runner should look like an ordinary `pymdp` loop:

```python
template = build_trust_pomdp_template(config, planning_horizon=condition_horizon)
partner_agents = create_partner_agents(template, num_partners=config.num_partners, gamma=config.gamma)
beta = maybe_create_beta_tracker(condition)
env = create_env(config, seed)

context = env.reset()
for round_idx in range(config.num_rounds):
    active_partner = context["active_partner"]

    decision = select_decision(
        partner_agents=partner_agents,
        template=template,
        beta=beta,
        active_partner=active_partner,
        assignment_mode=config.assignment_mode,
        rng=rng,
    )

    env_result = env.step(decision.raw_action)

    obs = env_result["observation"]
    update_pymdp_agent(
        partner_agents[env_result["partner_idx"]],
        template=template,
        obs=obs,
        own_action=env_result["agent_action"],
    )

    update_beta_if_enabled(
        beta=beta,
        partner_idx=env_result["partner_idx"],
        predicted_partner_action_probability=decision.predicted_partner_action_probability,
        observed_partner_action=env_result["partner_action"],
        lesion_mode=condition.lesion_mode,
    )

    logger.log_round(...)
    context = {"active_partner": env_result["active_partner"]}
```

This loop is allowed to be procedural. That is the point.

## Decision Selection

Random-assignment mode:

- Use the active partner's `pymdp.Agent`.
- Apply beta precision modulation by setting or passing `gamma_k` for that
  planning call only.
- Call official `pymdp` policy inference.
- Select the first-step action from the chosen policy.
- Encode the environment raw action.

Agent-choice mode:

- Evaluate each partner-local `pymdp.Agent`.
- For each partner, obtain policy posterior/scores from official `pymdp`.
- Choose a partner-policy pair using the same scoring convention as the current
  implementation.
- Encode:
  - partner index
  - stance-control action
  - own action
- Do not create a custom global active-inference model over all partners unless
  that becomes an explicit future science change.

## Affect Modulation

Affect remains external and small:

```python
def gamma_for_partner(base_gamma: float, beta: DiscreteBetaState | None, partner_idx: int, mode: AffectMode) -> float:
    if beta is None or mode in {"none", "decouple", "fixed"}:
        return base_gamma
    return base_gamma / float(beta.expected_beta()[partner_idx])
```

The beta tracker should not know about `pymdp.Agent`.

The decision function may temporarily use partner-specific gamma by either:

- passing gamma through official `pymdp` API if supported, or
- creating/replacing the immutable JAX agent state in the smallest official way
  available.

Avoid mutable monkey-patching where official `pymdp` provides a native
constructor/update path.

## Logging

The logger should consume a simple `TrialSnapshot`, not a custom agent object:

```python
@dataclass
class TrialSnapshot:
    q_pi: np.ndarray
    policy_scores: np.ndarray
    selected_partner: int
    selected_action: int
    raw_action: int
    partner_type_beliefs: np.ndarray
    partner_stance_beliefs: np.ndarray
    partner_joint_beliefs: np.ndarray
    partner_joint_posteriors: np.ndarray
    beta: np.ndarray | None
    surprise: np.ndarray | None
    predictive_log_lik: float
```

This removes the need for `agent.get_metrics()` and dozens of mirrored fields
on an agent wrapper.

## Documentation Updates

Update docs to say:

- official `pymdp.Agent` is the only active-inference agent
- task code provides a trust POMDP template
- affective precision is an external modulation layer
- multi-partner tracking is orchestration over multiple `pymdp.Agent` instances
- former `TrustGameAgent`/`AffectiveAgent` classes were migration scaffolding
  and are no longer the native surface

Update:

- `README.md`
- `docs/design/implementation.md`
- `docs/theory/apashea_alignment.md`
- `docs/theory/pomdp_spec.md`
- `docs/experiment/design.md`
- `docs/state/current/mission.md`
- `docs/state/decisions/architecture.md`
- `AGENTS.md`

## Acceptance Criteria

- Experiment runtime instantiates official `pymdp.Agent` directly from a trust
  POMDP template.
- There is no custom class whose primary job is to behave like an active
  inference agent.
- `TrustGameAgent`, `AffectiveAgent`, and `LesionedAgent` are removed or reduced
  to temporary import aliases that are not part of the documented native API.
- The runner performs the infer-plan-step-update loop procedurally using
  `pymdp.Agent`.
- Multi-partner support is represented as a list/table of `pymdp.Agent`
  instances plus snapshots.
- Affect modulation is the only scientifically meaningful wrapper around
  policy precision.
- Static POMDP arrays passed into `pymdp.Agent` are JAX arrays.
- The current trust-game logic is preserved: payoff mapping, factorized
  controls, stance dynamics, type drift, observation modalities, beta update,
  lesion behavior, and condition meanings.
- No old custom active-inference inference, EFE, rollout, or policy code is
  reintroduced.
