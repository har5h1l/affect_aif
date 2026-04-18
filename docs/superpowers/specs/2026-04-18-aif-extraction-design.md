# aif/ extraction + canonical TrustGameModel — design spec

date: 2026-04-18
status: **READY FOR USER REVIEW** — sections 1–6 drafted, multi-focal-agent compatibility appendix added, sub-project F (multi-focal runtime) added to parent scoping doc. self-review pass complete (decision log row order fixed, Section 1 callouts/tree reconciled with Section 5's verified inventory, test counts corrected from 12 → 13). decisions log at top is current.
parent: [`2026-04-18-codebase-restructure-scoping.md`](2026-04-18-codebase-restructure-scoping.md) (sub-projects B + A combined)
follow-on: implementation plan via `superpowers:writing-plans` skill, written to `docs/superpowers/plans/` after this spec is approved

---

## decisions log (locked in, in order taken)

| # | decision | resolution |
|---|---|---|
| 1 | repo layout style | flat, packages at repo root. no nested `affect_aif/` python package — repo dir name only. |
| 2 | project package name | `trust/` (renamed from `agent/` + `agent/model/` flattened in) |
| 3 | `aif.Agent` shape | thin stateful container. holds A/B/C/D/E/pA/pB/pD/pE/qs/policies/gamma. **no `step()` method**. loop runs externally in the runner via free functions. mirrors andrew pescia's pymdp pattern. |
| 4 | multi-partner architecture | `TrustGameAgent` HAS-A list of N `aif.Agent`s, one per partner. per-partner `pA`/`pB`. cross-partner action selection lives on `TrustGameAgent.choose_partner_and_action()`. `qs_per_partner` exposed as read-only derived property `np.stack([p.qs for p in self.partners])`. |
| 5 | `TrustGameModel` consolidation | merge `TrustGameModel` + `GradedTrustGameModel` + `_BaseTrustGameModel` into single `TrustGameModel` in `trust/model.py` with `payoff_mode={"binary","graded"}` constructor arg. **hard rename**, no `GradedTrustGameModel` alias, no deprecation warning. |
| 6 | `infer_joint_posterior` payoff-drop bug | **fix now** as part of the restructure. **first** intentional behavior change. `observation_likelihood` updated to multiply across both modalities `(A[0][o_action] · A[1][o_payoff, own_action])`. invalidates noisy-observation experiments — rerun required. |
| 7 | `aif/affect/` placement | move `agent/affect/beta.py` → `aif/affect/beta.py`. rename `partner` → `entity` at the public boundary. delete `agent/affect/interoception.py` (10-line stub, YAGNI). module name `aif/affect/` (parallels `aif/inference/`). |
| 8 | migration strategy | hard switch, **no shims, no codemod, no back-compat anywhere.** removed config keys (`variant`, `model_class`) raise `ValueError`. removed class names (`GradedTrustGameModel`, `_BaseTrustGameModel`, `BaseAgent`) are deleted with no aliases. work split across **two PRs** per decision #10. CI green at every commit in both PRs. |
| 9 | per-partner Dirichlet learning | each per-partner `aif.Agent` holds its **own** `A`, `B`, `pA`, `pB` (fresh copies). `C`, `D`, `E` stay shared. **second** intentional behavior change. today's code learns one shared `partner_action_prob_table` blind to which partner produced the evidence; new code accumulates per-partner. trust-specific planner takes per-partner stacks of A/B views. invalidates all configs with `learn_A=True`, `learn_B=True`, or `use_parameter_learning=True`. |
| 10 | PR split | **two PRs** at commit-1/2 boundary. PR-1 lands `aif/` skeleton as inert/dead code (passes CI, no behavioral change). PR-2 lands the rest (model + agent cutover, `agent/` directory deletion, verification). rationale: PR-1 is reviewable in <30 min and de-risks the rest; PR-2's diff is large but every change is "delete-an-old-import-or-class" which reviews fast. |

---

## section 1 — repo layout & module map (approved)

end-state directory tree at the repo root:

```
affect_aif/                         (repo root — name only, not a python package)
│
├── aif/                            ← NEW — generic active-inference package
│   ├── __init__.py                 (re-exports Agent + free functions)
│   ├── agent.py                    Agent (stateful container)
│   ├── inference.py                infer_states, infer_policies (free fns)
│   ├── policies.py                 sample_action, construct_policies, gamma_per_policy
│   ├── efe.py                      G computation (utility + info gain)
│   ├── learning.py                 update_pA, update_pB, update_pD, update_pE
│   ├── runtime.py                  rollout primitives (generate_observation_sequences)
│   ├── maths.py                    softmax, log_stable, dirichlet_expected_value, etc.
│   ├── utils.py                    obj_array, onehot, normalize, etc.
│   ├── backend.py                  numpy/jax dispatch
│   └── affect/
│       ├── __init__.py
│       └── beta.py                 DiscreteBetaState (entity-renamed)
│
├── trust/                          ← NEW — project package (renamed from agent/)
│   ├── __init__.py                 (re-exports TrustGameAgent, TrustGameModel)
│   ├── agent.py                    TrustGameAgent (composes N aif.Agent)
│   ├── affective.py                AffectiveAgent(TrustGameAgent) — uses aif.affect.beta
│   ├── lesioned.py                 LesionedAgent(TrustGameAgent)
│   ├── model.py                    TrustGameModel (canonical, payoff_mode switch)
│   ├── rollout.py                  decision_step_trust_game, _decode_action,
│   │                               _decode_policy_timestep, _partner_action_distribution,
│   │                               _rollout_policy_trust_game_*
│   ├── payoffs.py                  build_payoff_matrix, build_graded_payoff_matrix,
│   │                               decode_action, encode_env_action_factorized, etc.
│   ├── stance.py                   STANCE_ORDER, cooperation_evidence_strength,
│   │                               interpolate_stance_transition,
│   │                               get_type_stance_cooperation_table
│   └── types.py                    PARTNER_TYPE_ORDER, PartnerType,
│                                   default_partner_type_params
│
├── analysis/                       (unchanged — verified 0 imports of agent.*)
├── benchmark/                      (unchanged — verified 0 imports of agent.*; cvc stack out of scope)
├── experiment/                     (3 files: factory.py, runner.py, config.py — imports rewritten)
├── configs/                        (22 JSON files gain "payoff_mode": "binary"; 2 graded configs unchanged)
├── conductor/                      (unchanged)
├── docs/                           (sub-project E will rewrite, not this one; AGENTS.md gets a drive-by edit)
├── tests/                          (13 files updated; 1 deleted; 14 new test files added)
├── notebooks/                      (unchanged — verified 0 imports of agent.*)
└── scripts/                        (unchanged — verified 0 imports of agent.*)
```

callouts:

1. **`agent/` directory deleted entirely.** contents go to either `aif/` or `trust/`. no empty `agent/` shell, no re-export shims.
2. **`agent/inference/control.py` dissolves.** 25 lines split: `construct_policies` already belongs in `aif/policies.py`; `decision_step_trust_game` → `trust/rollout.py`; `generate_observation_sequences` → `aif/runtime.py`. file goes away.
3. **`agent/inference/rollout.py` splits.** generic helpers (`generate_observation_sequences`, `gamma_per_policy`) → `aif/runtime.py`. trust-specific (`decision_step_trust_game`, `_rollout_policy_trust_game_*`, `_decode_*`, `_partner_action_distribution`) → `trust/rollout.py`.
4. **`agent/affect/interoception.py` deleted.** 10-line stub, YAGNI.
5. **`agent/model/` flattens into `trust/`.** `payoffs.py`, `stance.py`, `types.py`, `trust_game.py` (now `model.py`) all live as flat siblings in `trust/`. no `trust/model/` subpackage.
6. **`benchmark/`, `analysis/`, `notebooks/`, `scripts/` have zero imports of `agent.*`** (verified by grep). nothing to rewrite there. only `experiment/` (3 files) and `tests/` (13 files) need import edits. (`benchmark/aif_policy.py` is a `NotImplementedError` stub — sub-project C's problem.)
7. **CvC stack untouched per MISSION.** verified that no cvc file imports `agent.*` today, so there's nothing to rewrite for compilation either. the cvc stack is genuinely a no-op for B+A.

---

## section 2 — `aif/` package public surface (drafted, pending review)

### `aif/agent.py`

```python
@dataclass
class Agent:
    """stateful container for a single-agent POMDP, pymdp-style.

    holds A/B/C/D/E plus optional Dirichlet priors and current posterior qs.
    has no `step()` method — the loop lives in the runner. all operations
    on an Agent are free functions in aif (infer_states, infer_policies,
    sample_action, update_pA/pB/pD/pE).
    """
    A: np.ndarray              # obj_array of likelihoods, one per modality
    B: np.ndarray              # obj_array of transitions, one per factor
    C: np.ndarray              # obj_array of preferences, one per modality
    D: np.ndarray              # obj_array of initial state priors, one per factor
    policies: np.ndarray       # (num_policies, horizon) or (num_policies, horizon, num_factors)
    qs: np.ndarray | None = None         # current posterior, obj_array per factor; None until first inference
    E: np.ndarray | None = None          # log-prior over policies, optional
    pA: np.ndarray | None = None         # Dirichlet hyperparams for A, optional
    pB: np.ndarray | None = None         # Dirichlet hyperparams for B, optional
    pD: np.ndarray | None = None         # Dirichlet hyperparams for D, optional
    pE: np.ndarray | None = None         # Dirichlet hyperparams for E, optional
    gamma: float = 1.0                   # policy precision
    use_utility: bool = True
    use_information_gain: bool = True
    action_sampling: str = "marginal"    # "marginal" | "full"
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(0))

    def reset(self) -> None:
        """reset qs to the prior D (or to expected value of pD if learning)."""
```

no methods beyond `reset`. mutations happen via free functions.

### `aif/inference.py`

```python
def infer_states(agent: Agent, obs: list[int], action: list[int] | None = None) -> np.ndarray:
    """single-step Bayes update: qs ← softmax(log D + log P(o|s)) factorized.

    if `action` is provided, first predicts qs forward through B[f][:,:,action[f]]
    and uses that as the prior. otherwise uses agent.qs (or D if qs is None).
    writes back to agent.qs and returns the new posterior.

    NOTE: this is a 1-step posterior update, not a fixed-point or MMP scheme.
    if the project later needs full pymdp inference, this is the extension point.
    """

def infer_policies(agent: Agent) -> tuple[np.ndarray, np.ndarray]:
    """compute G per policy and return (q_pi, G).

    q_pi = softmax(-gamma * G + (E or 0)).
    internally calls aif.efe.compute_efe_all_policies(...).
    """
```

### `aif/policies.py`

existing surface plus one signature change:

```python
def construct_policies(num_controls: list[int], planning_horizon: int,
                       max_policies: int | None = None,
                       rng: np.random.Generator | None = None) -> np.ndarray:
    """enumerate or sample policy sequences. same as today."""

def sample_action(agent: Agent, q_pi: np.ndarray, timestep: int = 0) -> int | np.ndarray:
    """sample an action from q_pi using agent.action_sampling and agent.rng.

    NOTE: signature changes — takes `agent` instead of (q_pi, policies, sampling_mode, rng).
    old free-function form becomes an internal helper."""

def gamma_per_policy(...):
    """moved verbatim from agent/inference/rollout.py."""
```

### `aif/efe.py`

existing surface, unchanged: `compute_expected_free_energy`, `compute_efe_all_policies`, `compute_efe_with_terminal_value`. imports go from `agent.inference.maths` → `aif.maths`.

### `aif/learning.py`

existing surface, unchanged signatures, plus thin Agent-aware wrappers:

```python
def update_pA(agent: Agent, obs: list[int], learning_rate: float = 1.0) -> None:
    """in-place update of agent.pA from current agent.qs and obs."""

def update_pB(agent: Agent, qs_previous: np.ndarray, action: list[int]) -> None:
    """in-place update of agent.pB from qs_previous → agent.qs over action."""

def update_pD(agent: Agent, learning_rate: float = 1.0) -> None:
    """accumulates current qs into pD (initial-state Dirichlet)."""

def update_pE(agent: Agent, q_pi: np.ndarray, learning_rate: float = 0.5) -> None:
    """accumulates q_pi into pE (policy-prior Dirichlet)."""
```

current `update_likelihood_dirichlet` / `update_transition_dirichlet` stay as lower-level building blocks called by the wrappers.

### `aif/runtime.py`

two roles:
- **JAX runtime config** (current contents): `RuntimeConfig`, `resolve_device`, `runtime_context`, `as_jax`, `to_numpy`. unchanged.
- **generic rollout primitives** moved from `agent/inference/rollout.py`: `generate_observation_sequences(planning_horizon)`. only part of `rollout.py` that is task-agnostic.

### `aif/maths.py`, `aif/utils.py`, `aif/backend.py`

verbatim moves. internal imports rewritten (`agent.inference.X` → `aif.X`). no API change.

### `aif/affect/beta.py`

`DiscreteBetaState` moved from `agent/affect/beta.py`. public API renamed at the entity boundary:

| current | new |
|---|---|
| `num_partners` | `num_entities` |
| `partner_idx` (kwarg in `update`, `get_beta`, `get_prediction_error`) | `entity_idx` |
| `get_all_betas()` | unchanged (already neutral) |
| `get_prediction_errors()` | unchanged |

internal variable names renamed to match.
`agent/affect/interoception.py` deleted.

### `aif/__init__.py`

```python
from aif.agent import Agent
from aif.inference import infer_states, infer_policies
from aif.policies import construct_policies, sample_action
from aif.learning import update_pA, update_pB, update_pD, update_pE
```

usage example:

```python
import aif
agent = aif.Agent(A=..., B=..., C=..., D=..., policies=...)
qs = aif.infer_states(agent, obs=[0, 1])
q_pi, G = aif.infer_policies(agent)
action = aif.sample_action(agent, q_pi)
aif.update_pA(agent, obs=[0, 1])
```

### implicit decisions in section 2

1. `aif.Agent` is a `@dataclass`, not a regular class. (rationale: it's a data container.) speak up if you want a regular class.
2. `infer_states` is a 1-step Bayes update, not full pymdp MMP/VMP inference. matches what `_BaseTrustGameModel.infer_joint_posterior` does today. tracked as a follow-up: "introduce optional MMP-style inference" — see follow-up tasks appendix.
3. `aif.sample_action` takes `agent` as first arg now, instead of being a fully free function. minor inconsistency with `construct_policies` — but `construct_policies` is pre-construction (no agent yet), whereas `sample_action` operates on agent.rng/agent.action_sampling.

---

## section 3 — `trust/` package public surface (drafted, pending review)

### per-partner private learning (decision #9)

**each per-partner `aif.Agent` gets its own `A`, `B`, `pA`, `pB` (fresh copies from `model.build_A/B/pA/pB`).** `C`, `D`, `E` stay shared (no per-partner divergence semantics).

today's code learns one shared `partner_action_prob_table` blind to which partner produced the evidence — that semantics is gone.

implications:
- the trust-specific planner (`decision_step_trust_game`) signature changes: takes `partner_action_prob_tables` (shape `(N, num_types, num_stances)`), per-partner `B_type` (shape `(N, num_types, num_types)`), per-partner `B_stance_by_action` (shape `(N, num_actions, num_stances, num_stances)`). uniform per-partner indexing — no special "shared" code path. when learning is off, all N slices are identical.
- behavioral-equivalence verification narrows: bit-identical results only for configs with `learn_A=False AND learn_B=False AND use_parameter_learning=False`.
- configs with learning enabled are **deliberately rerun** with new acceptance criteria (numerical drift expected; check direction and order of magnitude). add to STATE.md blockers list.

### `trust/agent.py` — `TrustGameAgent`

```python
class TrustGameAgent:
    """Active inference agent for the multi-partner trust game.

    Composes N aif.Agent instances (one per partner). Each per-partner agent
    holds its own A, B, pA, pB (per-partner Dirichlet learning). C, D, E are
    shared. Per-partner posterior qs and ephemeral state are private. Cross-
    partner action selection (agent_choice mode) lives here. The trust-specific
    planner (decision_step_trust_game) is delegated to trust.rollout.
    """

    def __init__(
        self,
        model: TrustGameModel,
        *,
        planning_horizon: int = 8,
        gamma: float = 1.0,
        lr: float = 0.1,
        action_sampling: str = "marginal",
        use_utility: bool = True,
        use_information_gain: bool = True,
        max_policies: int | None = None,
        reference_horizon: int | None = None,
        seed: int = 0,
        use_parameter_learning: bool = False,
        learn_A: bool = False,
        learn_B: bool = False,
        learn_E: bool = False,
        pA_scale: float = 1.0,
        pB_scale: float = 10.0,
        lr_E: float = 0.5,
    ):
        ...
        # construct N per-partner aif.Agents, each with its own A/B/pA/pB:
        single_partner_policies = aif.policies.construct_policies(
            model.num_controls, planning_horizon, max_policies=max_policies, rng=self.rng
        )
        self.partners: list[aif.Agent] = [
            aif.Agent(
                A=model.build_A(),                    # fresh per-partner copy
                B=model.build_B(),                    # fresh per-partner copy
                C=model.C,                            # shared by reference
                D=model.D,                            # shared by reference
                E=None,                               # populated per-partner if learn_E
                policies=single_partner_policies,
                pA=model.build_pA(pA_scale) if learn_A else None,
                pB=model.build_pB(pB_scale) if learn_B else None,
                gamma=gamma,
                use_utility=use_utility,
                use_information_gain=use_information_gain,
                action_sampling=action_sampling,
                rng=np.random.default_rng(self.seed + i),
            )
            for i in range(self.num_partners)
        ]

    # ----- public API -----

    def reset(self) -> None: ...

    def choose_partner_and_action(self, active_partner: int | None = None) -> int:
        """Plan + sample action.

        For random-assignment mode: active_partner is supplied by the env; this
        method just decides the social action. For agent_choice mode:
        active_partner=None and this method picks both (partner, social_action)
        jointly via the trust-specific planner.

        Returns the raw action index in the env action space (compatible with
        the existing experiment runner's action interface).
        """

    def observe_outcome(
        self,
        partner_idx: int,
        observation: list[int],
        action_taken: int,
        partner_action: int,
        payoff: float,
        true_partner_type: str | None = None,
        true_partner_stance: str | None = None,
    ) -> None:
        """Belief update + Dirichlet learning for the active partner only.

        Calls aif.infer_states on partners[partner_idx] for the Bayes update,
        then aif.update_pA / aif.update_pB if learning enabled (mutates THAT
        partner's pA/pB and A/B only — other partners unaffected),
        then aif.predict_state to prepare partners[partner_idx].qs for next
        round.
        """

    def get_metrics(self) -> dict:
        """Round-level metrics for analysis. Same keys as today."""

    # ----- read-only derived views -----

    @property
    def qs_per_partner(self) -> np.ndarray:
        """(N, num_types, num_stances) — joint type-stance posteriors per partner."""

    @property
    def partner_beliefs(self) -> np.ndarray:
        """(N, num_types) — type marginals."""

    @property
    def partner_stance_beliefs(self) -> np.ndarray:
        """(N, num_stances) — stance marginals."""

    @property
    def partner_action_prob_tables(self) -> np.ndarray:
        """(N, num_types, num_stances) — derived from each partner's A[0].
        Used by the planner; reflects per-partner learning."""

    # ----- subclass extension hook -----

    def precision_signal(self) -> np.ndarray:
        """(N,) — per-partner γ multiplier. TrustGameAgent returns ones.
        AffectiveAgent overrides to return betas. Called by the planner."""

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float) -> None:
        """No-op on TrustGameAgent. AffectiveAgent overrides to update beta state.
        LesionedAgent overrides to gate the update."""
```

notable changes from current `BaseAgent`:

- `model` is the only positional arg. A/B/C/D no longer passed separately.
- `plan_and_act(active_partner)` → `choose_partner_and_action(active_partner)`. better name.
- `partner_joint_beliefs` and `partner_joint_posteriors` collapse into one quantity: `qs_per_partner` (a derived view).
- `_refresh_transition_views`, `B_type`, `B_stance_by_action` → moved into `trust/rollout.py` as helpers (now per-partner).
- `_decode_raw_action` → moved to `trust/rollout.py`.
- `_apply_parameter_learning` (the "fast" non-Dirichlet learning path) stays as private method on `TrustGameAgent`. now operates per-partner.

### `trust/affective.py` — `AffectiveAgent`

```python
class AffectiveAgent(TrustGameAgent):
    """Trust-game agent with per-entity affective precision (Hesp-style)."""

    def __init__(
        self, model: TrustGameModel, *,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 1.0,
        num_levels: int = 5,
        persistence: float = 0.8,
        **kwargs,
    ):
        super().__init__(model, **kwargs)
        self.affect = aif.affect.beta.DiscreteBetaState(
            num_entities=self.num_partners,        # was num_partners
            num_levels=num_levels,
            persistence=persistence,
            alpha_charge=alpha_charge,
            sigma_0_sq=sigma_0_sq,
            initial_beta=initial_beta,
        )

    def precision_signal(self) -> np.ndarray:
        return self.affect.get_all_betas()

    def _update_auxiliary_states(self, partner_idx, partner_action, payoff):
        if self.pending_prediction_partner != partner_idx:
            return
        self.affect.update(
            entity_idx=partner_idx,                # was partner_idx
            predicted_action_probs=self.pending_prediction_probs,
            observed_action=partner_action,
        )

    def get_betas(self) -> np.ndarray: ...
    def get_prediction_errors(self) -> np.ndarray: ...
```

mostly unchanged; differences:
- inherits from `TrustGameAgent` (was `BaseAgent`)
- imports `aif.affect.beta.DiscreteBetaState`
- uses `num_entities=` and `entity_idx=` at boundary (rename from Q7)
- drops `jax.numpy` import — `precision_signal()` returns plain numpy

### `trust/lesioned.py` — `LesionedAgent`

unchanged in shape; only import paths update. `lesion_mode="freeze"` stays per scoping doc (sub-project C decides its fate).

```python
class LesionedAgent(AffectiveAgent):
    def __init__(self, *args, lesion_mode: str = "decouple", **kwargs): ...
    def precision_signal(self) -> np.ndarray:
        if self.lesion_mode in {"decouple", "freeze"}:
            return np.ones((self.num_partners,), dtype=float)   # was jnp
        return super().precision_signal()
    def _update_auxiliary_states(self, partner_idx, partner_action, payoff):
        if self.lesion_mode == "freeze":
            return
        super()._update_auxiliary_states(...)
```

### `trust/rollout.py` — public surface

```python
def decision_step_trust_game(
    beliefs: np.ndarray,                              # (N, num_types, num_stances)
    active_partner: int,                              # -1 in agent_choice mode
    policies: np.ndarray,                             # (num_policies, horizon, num_factors)
    observation_sequences: np.ndarray,
    B_type: np.ndarray,                               # (N, num_types, num_types) — per-partner
    B_stance_by_action: np.ndarray,                   # (N, num_actions, num_stances, num_stances)
    partner_action_prob_tables: np.ndarray,           # (N, num_types, num_stances) — per-partner
    payoff_index_table: np.ndarray,                   # shared (no learning on payoff structure)
    agent_payoff_table: np.ndarray,                   # shared
    payoff_preferences: np.ndarray,                   # shared (C[1])
    partner_action_preferences: np.ndarray,           # shared (C[0])
    precision_signal: np.ndarray,                     # (N,)
    assignment_mode_code: int,
    gamma: float,
    use_utility_flag: float,
    use_information_gain_flag: float,
    num_social_actions: int,
    log_policy_prior: np.ndarray,
) -> dict:
    """Per-(partner, policy) EFE evaluation. Returns dict with q_pi, G, step_costs,
    mean_abs_step_efe. Numerics preserved from agent/inference/rollout.py except
    that A/B inputs are now per-partner stacks (decision #9)."""

def _decode_action(...): ...                          # verbatim move
def _decode_policy_timestep(...): ...                 # verbatim move
def _partner_action_distribution(...): ...            # verbatim move
def _rollout_policy_trust_game_factorized(...): ...   # per-partner-aware variant
def _rollout_policy_trust_game_flat(...): ...         # per-partner-aware variant

def build_transition_views(B, num_controls, factorized_policies):
    """Returns (B_type, B_stance_by_action) for one partner's B. Called per-partner
    by TrustGameAgent to assemble the per-partner stacks the planner expects."""

def decode_raw_action_to_partner_and_social(
    raw_action, active_partner, assignment_mode_code, factorized_policies,
    num_social_actions, num_partners,
) -> tuple[int, int]: ...                             # verbatim from BaseAgent._decode_raw_action
```

`build_transition_views` returns single-partner views; `TrustGameAgent` calls it once per partner and stacks the results before passing to `decision_step_trust_game`.

### `trust/model.py`

section 4 covers in detail. surface preview:

```python
class TrustGameModel:
    """Canonical trust-game POMDP. payoff_mode={'binary','graded'}."""
    def __init__(self, config: dict | TrustGameConfig): ...
    @property
    def uses_factorized_controls(self) -> bool: ...
    def build_A(self) -> np.ndarray: ...        # returns fresh copy each call
    def build_B(self) -> np.ndarray: ...        # returns fresh copy each call
    def build_C(self) -> np.ndarray: ...
    def build_D(self) -> np.ndarray: ...
    def build_pA(self, scale: float = 1.0) -> np.ndarray: ...
    def build_pB(self, scale: float = 10.0) -> np.ndarray: ...
    def get_matrices(self) -> tuple: ...

    # belief operations (still on model — encode trust-specific belief shape):
    def as_joint_belief(self, belief): ...
    def partner_action_distribution(self, joint_belief): ...
    def joint_observation_likelihood(self, partner_action, payoff_obs, own_action): ...   # **bug fix here**
    def observation_likelihood(self, observation, own_action): ...                          # **bug fix here**
    def predict_next_joint_belief(self, joint_belief, action): ...
    def infer_joint_posterior(self, joint_belief, observation, own_action): ...             # **bug fix here**
```

`build_A` and `build_B` returning fresh copies each call (vs returning the cached `self.A`) is the small constructor change that supports per-partner copies cleanly.

### `trust/payoffs.py`, `trust/stance.py`, `trust/types.py`

verbatim moves. imports updated. no API changes.

### `trust/__init__.py`

```python
from trust.agent import TrustGameAgent
from trust.affective import AffectiveAgent
from trust.lesioned import LesionedAgent
from trust.model import TrustGameModel
```

### runner-side example

```python
import aif
from trust import TrustGameAgent, TrustGameModel

model = TrustGameModel(config)
agent = TrustGameAgent(model, planning_horizon=8, gamma=1.0)

for round_idx in range(num_rounds):
    active_partner = env.next_partner()  # int or None (agent_choice)
    raw_action = agent.choose_partner_and_action(active_partner=active_partner)

    obs, partner_action, payoff, info = env.step(raw_action)
    agent.observe_outcome(
        partner_idx=info["partner_idx"],
        observation=obs,
        action_taken=info["social_action"],
        partner_action=partner_action,
        payoff=payoff,
    )

    log(agent.get_metrics())
```

runner doesn't see `aif.*` directly; calls `TrustGameAgent`. `aif.*` calls happen inside `TrustGameAgent.observe_outcome` and `choose_partner_and_action`. runner is structurally unchanged.

### things flagged in this section

1. **per-partner private learning (decision #9)** — second intentional behavior change. updates STATE.md blockers list and behavioral-equivalence verification scope.
2. `partner_joint_beliefs` vs `partner_joint_posteriors` collapse into one (just `qs_per_partner`) — pure cleanup, no behavior change.
3. `AffectiveAgent` drops the JAX import — `precision_signal()` return type changes from `jnp.ndarray` to `np.ndarray`. confirm no downstream consumer type-checks for JAX arrays (writing-plans will add a `git grep precision_signal` audit task).
4. `TrustGameModel.observation_likelihood` and `infer_joint_posterior` carry the bug fix.

---

## section 4 — canonical `TrustGameModel` (drafted, pending review)

### final shape

single class. no `_BaseTrustGameModel`, no `GradedTrustGameModel`. lives at `trust/model.py`. constructor branches on `payoff_mode`:

```python
class TrustGameModel:
    """Canonical trust-game POMDP. Replaces TrustGameModel + GradedTrustGameModel
    + _BaseTrustGameModel (decision #5)."""

    def __init__(self, config: dict | TrustGameConfig):
        cfg = asdict(config) if is_dataclass(config) else dict(config)
        self.config = cfg

        # ----- shared knobs (all configs) -----
        self.num_partners        = int(cfg.get("num_partners", 4))
        self.partner_type_names  = tuple(cfg.get("partner_types", PARTNER_TYPE_ORDER))
        self.stance_names        = tuple(cfg.get("stance_names", STANCE_ORDER))
        self.num_types           = len(self.partner_type_names)
        self.num_stances         = len(self.stance_names)
        self.p_switch            = float(cfg.get("p_switch", 0.05))
        if "variant" in cfg:
            raise ValueError(
                "config key 'variant' was removed in the B+A restructure. "
                "rename to 'assignment_mode' and rerun. no back-compat shim is provided."
            )
        self.assignment_mode     = str(cfg["assignment_mode"]) if "assignment_mode" in cfg else "random"
        self.observation_noise   = float(cfg.get("observation_noise", 0.0))
        self.preference_temperature = float(cfg.get("preference_temperature", 1.0))
        self.partner_type_params = default_partner_type_params()
        self.partner_type_params.update(cfg.get("partner_type_params", {}))
        self.partner_types = [
            PartnerType(type_name=n, params=self.partner_type_params.get(n, {}))
            for n in self.partner_type_names
        ]

        # ----- removed legacy keys (fail loudly; no silent fallback) -----
        if "model_class" in cfg:
            raise ValueError(
                "config key 'model_class' was removed in the B+A restructure. "
                "TrustGameModel is now the only class. drop the key and add payoff_mode."
            )

        # ----- payoff branch (decision #5) -----
        if "payoff_mode" not in cfg:
            raise ValueError(
                "config must specify payoff_mode={'binary','graded'}. defaulting was "
                "removed in the B+A restructure (no back-compat). update the config."
            )
        self.payoff_mode = str(cfg["payoff_mode"])
        _BINARY_KEYS = {"mutual_coop", "sucker", "temptation", "mutual_defect"}
        _GRADED_KEYS = {"num_investment_levels", "endowment", "multiplier"}
        if self.payoff_mode == "binary":
            stray = _GRADED_KEYS & cfg.keys()
            if stray:
                raise ValueError(f"payoff_mode='binary' but graded-only keys present: {sorted(stray)}")
            self.num_social_actions = 2
            self.payoff_matrix = build_payoff_matrix(
                mutual_coop   = tuple(cfg.get("mutual_coop",   (3.0, 3.0))),
                sucker        = tuple(cfg.get("sucker",        (-1.0, 5.0))),
                temptation    = tuple(cfg.get("temptation",    (5.0, -1.0))),
                mutual_defect = tuple(cfg.get("mutual_defect", (1.0, 1.0))),
            )
        elif self.payoff_mode == "graded":
            stray = _BINARY_KEYS & cfg.keys()
            if stray:
                raise ValueError(f"payoff_mode='graded' but binary-only keys present: {sorted(stray)}")
            num_levels = int(cfg.get("num_investment_levels", 6))
            self.num_social_actions = num_levels
            self.payoff_matrix = build_graded_payoff_matrix(
                num_levels = num_levels,
                endowment  = float(cfg.get("endowment",  10.0)),
                multiplier = float(cfg.get("multiplier",  3.0)),
            )
        else:
            raise ValueError(f"unknown payoff_mode={self.payoff_mode!r}, expected 'binary' or 'graded'")

        # ----- derived structure (mode-agnostic) -----
        self.payoff_levels    = infer_payoff_levels(self.payoff_matrix)
        self.num_obs          = [2, len(self.payoff_levels)]
        self.num_controls     = factorized_num_controls(
            self.num_partners, self.assignment_mode, self.num_social_actions
        )
        self.partner_action_prob_table = self._build_partner_action_prob_table()
        self.payoff_index_table        = self._build_payoff_index_table()
        self.agent_payoff_table        = self.payoff_matrix[:, :, 0]

        # ----- cached canonical matrices -----
        # NOTE: build_A/build_B return FRESH copies on each call. these cached
        # references are kept for the model's own belief-update methods (which
        # read A directly), and as the seed for per-partner copies in
        # TrustGameAgent. mutating these would silently affect spawned agents,
        # so trust-side code never mutates them.
        self.A = self.build_A()
        self.B = self.build_B()
        self.C = self.build_C()
        self.D = self.build_D()
```

### config-key inventory

| key                       | applies to    | required? | default            | notes |
|---|---|---|---|---|
| `payoff_mode`             | all           | **yes**   | —                  | **NEW.** `"binary"` or `"graded"`. no default — every config must declare. |
| `num_partners`            | all           | no        | 4                  | unchanged |
| `partner_types`           | all           | no        | PARTNER_TYPE_ORDER | unchanged |
| `stance_names`            | all           | no        | STANCE_ORDER       | unchanged |
| `p_switch`                | all           | no        | 0.05               | unchanged |
| `assignment_mode`         | all           | no        | `"random"`         | `variant=` is **removed** — raises `ValueError` if present in config. all configs are rewritten in this PR. |
| `observation_noise`       | all           | no        | 0.0                | unchanged |
| `preference_temperature`  | all           | no        | 1.0                | unchanged |
| `partner_type_params`     | all           | no        | `{}`               | unchanged |
| `mutual_coop`             | binary only   | no        | `(3.0, 3.0)`       | raises `ValueError` if set under `payoff_mode="graded"` (no silent ignore) |
| `sucker`                  | binary only   | no        | `(-1.0, 5.0)`      | same |
| `temptation`              | binary only   | no        | `(5.0, -1.0)`      | same |
| `mutual_defect`           | binary only   | no        | `(1.0, 1.0)`       | same |
| `num_investment_levels`   | graded only   | no        | 6                  | raises `ValueError` if set under `payoff_mode="binary"` |
| `endowment`               | graded only   | no        | 10.0               | same |
| `multiplier`              | graded only   | no        | 3.0                | same |
| `model_class`             | (legacy)      | no        | —                  | **removed.** raises `ValueError` if present. runner no longer dispatches on it. |

**existing configs — actual inventory** (verified by `git grep` against `configs/`):

- 0 configs reference `variant` (the key was already renamed to `assignment_mode` upstream — nothing to do).
- 0 configs reference `model_class` (the dispatch is already `payoff_mode`-based in `experiment/factory.py:18`).
- 2 configs already declare `payoff_mode: "graded"`: `configs/graded_betrayal.json`, `configs/graded_trust_factorial.json`.
- the remaining 22 configs do NOT declare `payoff_mode` and currently rely on the implicit binary default in `experiment/factory.py`.

so the config rewrite for B+A is:
- add `"payoff_mode": "binary"` as an explicit top-level key in the 22 configs that don't already set it.
- no key removals are needed.
- `experiment/factory.py:create_model` collapses from a 4-line `if/return` into `return TrustGameModel(asdict(config))`. (the `model_class`-style guards I wrote into the constructor stay as defensive checks against future regressions.)

**enforcement principle**: contradictory or removed keys raise `ValueError`. no `warnings.warn`, no silent ignore, no graceful degradation. matches decision #8 (hard switch, no shims, no back-compat).

### the `infer_joint_posterior` payoff-drop bug fix (decision #6)

**current behavior** (`agent/model/trust_game.py:215-221`):

```python
def joint_observation_likelihood(self, partner_action, payoff_obs=None, own_action=None):
    del payoff_obs, own_action                          # ← BUG: drops o_payoff
    return np.asarray(self.A[0][int(partner_action)], dtype=float)

def observation_likelihood(self, observation, own_action=None):
    payoff_obs = int(observation[1]) if len(observation) > 1 else None
    return self.joint_observation_likelihood(
        int(observation[0]), payoff_obs=payoff_obs, own_action=own_action
    )
```

`payoff_obs` is computed but immediately discarded. the joint likelihood reduces to `A[0][o_partner_action]` only.

**new behavior**:

```python
def joint_observation_likelihood(self, partner_action: int, payoff_obs: int, own_action: int) -> np.ndarray:
    """Likelihood over joint (type, stance) given both observation modalities.

    L[t, s] = P(o_partner_action | t, s) * P(o_payoff | own_action, t, s)
            = A[0][partner_action, t, s]   *   A[1][payoff_obs, own_action, t, s]
    """
    L_action = np.asarray(self.A[0][int(partner_action)],                         dtype=float)
    L_payoff = np.asarray(self.A[1][int(payoff_obs), int(own_action)],            dtype=float)
    return L_action * L_payoff

def observation_likelihood(self, observation: list[int], own_action: int) -> np.ndarray:
    if len(observation) < 2:
        raise ValueError(
            f"observation_likelihood now requires both modalities; got {observation!r}. "
            "callers must pass [o_partner_action, o_payoff]."
        )
    if own_action is None:
        raise ValueError(
            "observation_likelihood now requires own_action to evaluate the payoff modality. "
            "pre-fix code passed None — call sites must be updated."
        )
    return self.joint_observation_likelihood(
        int(observation[0]),
        payoff_obs = int(observation[1]),
        own_action = int(own_action),
    )

def infer_joint_posterior(self, joint_belief, observation, own_action):
    """Bug-fixed: now multiplies through both modalities (decision #6).
    Spec compliance with pomdp_spec.md v4 §3 restored."""
    prior     = self.as_joint_belief(joint_belief)
    likelihood = self.observation_likelihood(observation, own_action=own_action)
    posterior  = prior * likelihood
    posterior /= max(float(posterior.sum()), 1e-16)
    return posterior
```

**signature changes**:
- `joint_observation_likelihood`: `payoff_obs` and `own_action` go from `Optional` to required.
- `observation_likelihood`: `own_action` goes from `Optional` to required. raises `ValueError` if either modality or `own_action` is missing — fail-fast, no silent fallback. forces every caller to be updated in this PR.
- `infer_joint_posterior`: signature unchanged, behavior changes.

**call-site impact**: ~4 call sites in `agent/base.py` and `agent/inference/rollout.py`. each already has `own_action` in scope; the change is wiring it through. writing-plans will list these explicitly.

**configs invalidated** (rerun required, with new acceptance criteria — direction + order-of-magnitude, not bit-identical):
- any config with `observation_noise > 0` (only configs where the payoff modality carries non-trivial likelihood signal beyond what `partner_action` alone provides — though even with `noise=0`, noisy stance dynamics produce numerical drift)
- conservative listing: ALL configs are rerun under decision #6 + decision #9, since both touch belief updates. STATE.md blockers list captures this.

### what the model class no longer does

decisions to *not* let scope creep happen:

- **no learning state on the model.** `pA`/`pB` live on per-partner `aif.Agent` instances (decision #9). `model.build_pA(scale)` returns a fresh starter, but the model does not own or track learned values.
- **no posterior state on the model.** `model.infer_joint_posterior` is a *pure* function (input belief → output belief). it does NOT mutate `self.A` or accumulate evidence. (today's code has the same property; just being explicit.)
- **no agent loop on the model.** the model is the POMDP definition; `aif.Agent` is the runtime container; `TrustGameAgent` is the trust-aware wrapper.
- **no `social_action_for_action` indirection in the public path.** that helper survives as a private method but everything in `aif/` and the per-partner `aif.Agent` constructor uses `model.num_controls` and the per-partner factorized policies directly. trust-specific decoding happens in `trust/rollout.py`.

### things flagged in this section

1. **fresh-copy semantics of `build_A()`/`build_B()`**: today they happen to construct fresh tensors each call (no caching), but this is an *implicit* property the new design relies on for per-partner copies. spec'd explicitly as part of the public contract: `build_*` always returns a fresh allocation.
2. **no back-compat anywhere** (per decision #8 + this turn's clarification): `variant=`, `model_class=`, contradictory binary/graded keys all raise `ValueError`. every config in `configs/` is rewritten in the same PR. configs that are no longer maintained get deleted (sub-project D will do a second pass; B+A only deletes configs that are *unrunnable* under the new schema and not referenced by current STATE.md).
3. **config rewrite checklist** (handed to writing-plans, real inventory):
   - the 2 graded configs already have `payoff_mode: "graded"` — leave them alone.
   - the 22 remaining configs need `"payoff_mode": "binary"` added as a top-level key.
   - no other key edits.
   - run a config-loader smoke test: every JSON in `configs/` instantiates `TrustGameModel` cleanly. cvc configs (`benchmark_cvc_*.json`) are excluded per MISSION (their loader doesn't go through `create_model`).

---

## section 5 — migration plan (drafted, pending review)

per decisions #8 + #10: hard switch across **two PRs** (split at the commit-1/2 boundary), **no shims, no codemod, no back-compat anywhere**, CI green at every commit in both PRs. this section turns that policy into an exact ordered work-plan with verified inventory.

### import-site inventory (verified)

| location | files | what's there |
|---|---|---|
| `agent/` (becomes `aif/` + `trust/`) | 18 .py files | intra-package imports — get rewritten as part of moves |
| `tests/` | 14 files importing `from agent.*` (13 updated + 1 deleted) | updated → `from aif.*` / `from trust.*`; deleted → `tests/test_interoception.py` |
| `experiment/` | 3 files (`factory.py`, `runner.py`, `config.py`) | rewritten |
| `notebooks/` | 0 files importing `agent.*` | nothing to do (verified — `04_apashea_trust_spec.ipynb` uses `pymdp` only) |
| `scripts/` | 0 files importing `agent.*` | nothing to do |
| `analysis/` | 0 files importing `agent.*` | nothing to do |
| `benchmark/` | 0 files importing `agent.*` | nothing to do (cvc stack out of scope per MISSION; nothing else there imports `agent.`) |
| `archive/` | several | **untouched** — archived code stays archived. |
| `configs/` | 22 files need `"payoff_mode": "binary"` added; 2 already declare `"graded"` | small JSON edit each |
| `docs/` | 2 files mention old class names | sub-project E rewrites; B+A only fixes if a doc is referenced from an active code path |
| `AGENTS.md` | 1 mention | drive-by edit in this PR |

**total source files touched**: 18 (moved) + 13 (tests updated) + 3 (experiment) + 22 (configs) + 1 (`AGENTS.md`) = **57 files**. plus deletes: 1 test file (`tests/test_interoception.py`), 1 source stub (`agent/affect/interoception.py`), `agent/inference/control.py`, plus the empty-by-then `agent/__init__.py`, `agent/affect/__init__.py`, `agent/inference/__init__.py`, `agent/model/__init__.py`.

### work-plan: two PRs, commit-by-commit (CI green each commit)

each commit is a self-contained green change. no commit leaves the repo in a "half-renamed" state. PR boundary is between commit 1 and commit 2.

#### PR-1 (small, lands first)

**commit 1 — `aif/` skeleton, generic moves with no API change**
- create `aif/__init__.py`, `aif/maths.py`, `aif/utils.py`, `aif/backend.py`, `aif/efe.py`, `aif/runtime.py`, `aif/policies.py`, `aif/learning.py`
- bodies: identical to `agent/inference/{maths,utils,backend,efe,runtime,policies,learning}.py`
- `agent/inference/<x>.py` → `from aif.<x> import *` re-export... NO. **per decision #8 no shims.** instead: in commit 1, `aif/` files exist but are not yet referenced. nothing imports them. they're dead code. CI green because no behavior changed.
- bonus: a single regression test `tests/test_aif_skeleton.py` confirms `import aif; aif.softmax(...) == agent.inference.maths.softmax(...)` to prove the move is value-preserving.

#### PR-2 (large, lands after PR-1 merges)

**commit 2 — `aif/agent.py`, `aif/inference.py`, `aif/affect/beta.py`**
- create `aif/agent.py` with the `Agent` dataclass.
- create `aif/inference.py` with `infer_states`, `infer_policies`.
- move `agent/affect/beta.py` → `aif/affect/beta.py` with the `partner` → `entity` rename. delete `agent/affect/beta.py`.
- update `agent/affective.py` to `from aif.affect.beta import DiscreteBetaState` (uses new `entity_idx=` kwargs internally).
- delete `agent/affect/interoception.py` (10-line stub).
- update `agent/affect/__init__.py` — at this point it can be empty or deleted entirely; the only consumer is `agent/affective.py` which is now using `aif.affect.beta` directly.
- new test `tests/test_aif_agent.py`: instantiate `aif.Agent`, run `aif.infer_states` against andrew's notebook setup, confirm equivalence to a reference numpy posterior.
- CI green: `agent/affective.py` now imports from `aif.affect.beta`; behavior unchanged because `DiscreteBetaState` semantics are unchanged (only the kwargs renamed).

**commit 3 — `trust/` skeleton (model + helpers, no agent classes yet)**
- create `trust/types.py`, `trust/stance.py`, `trust/payoffs.py` (verbatim moves from `agent/model/`). update internal imports to `aif.maths`, `aif.utils`.
- create `trust/model.py` with the canonical `TrustGameModel` (decisions #5 + #6 applied: single class, payoff_mode switch, payoff-drop bug fix wired in).
- delete `agent/model/trust_game.py`, `agent/model/types.py`, `agent/model/stance.py`, `agent/model/payoffs.py`, `agent/model/__init__.py`.
- update `experiment/factory.py:create_model` to `from trust.model import TrustGameModel; return TrustGameModel(asdict(config))`.
- update `experiment/config.py` import: `from trust.types import PARTNER_TYPE_ORDER`.
- update `experiment/runner.py` import: `from trust.model import TrustGameModel`.
- the 22 binary configs gain `"payoff_mode": "binary"` in this commit too (smallest-possible JSON edit per file).
- update tests that touch `TrustGameModel`/`GradedTrustGameModel`: `tests/test_generative_model.py`, `tests/test_action_dependent_model.py`. they swap to `from trust.model import TrustGameModel` and use `TrustGameModel({..., "payoff_mode": "graded", ...})` everywhere `GradedTrustGameModel(...)` was used.
- **CI green proof point**: `pytest tests/test_generative_model.py tests/test_action_dependent_model.py` and `pytest tests/` overall pass. one config-loader smoke test confirms every JSON in `configs/` (excluding cvc) instantiates the new model.

**commit 4 — `trust/agent.py` + `trust/affective.py` + `trust/lesioned.py` + `trust/rollout.py`**
- create `trust/rollout.py` (move trust-specific helpers + new per-partner-aware planner).
- move `agent/inference/control.py:generate_observation_sequences` → `aif/runtime.py`, then delete the file.
- create `trust/agent.py` with `TrustGameAgent` per Section 3.
- create `trust/affective.py` with `AffectiveAgent` (subclass of `TrustGameAgent`).
- create `trust/lesioned.py` with `LesionedAgent`.
- delete `agent/base.py`, `agent/affective.py`, `agent/lesioned.py`, `agent/inference/rollout.py`.
- delete `agent/__init__.py`, `agent/inference/__init__.py`, `agent/model/__init__.py`.
- delete `agent/affect/__init__.py` if it's empty by now; otherwise it goes too.
- update `experiment/factory.py` and `experiment/runner.py`: `from trust import TrustGameAgent, AffectiveAgent, LesionedAgent`.
- update all 13 `tests/*.py` files (including `tests/conftest.py`) that import `from agent.*`. mechanical: `agent.base.BaseAgent` → `trust.TrustGameAgent`, `agent.affective.AffectiveAgent` → `trust.AffectiveAgent`, `agent.lesioned.LesionedAgent` → `trust.LesionedAgent`. delete `tests/test_interoception.py`.
- update `AGENTS.md` to drop references to `BaseAgent` / `GradedTrustGameModel`.
- **at this commit, `agent/` directory ceases to exist on disk.**
- CI green proof points (now stronger):
  - full `pytest` suite passes.
  - the equivalence-test suite (see below) compares old (pre-PR base SHA) vs new numerical outputs on every config.

**commit 5 — verification artifacts**
- add `tests/test_behavioral_equivalence.py` (see below).
- add `STATE.md` blockers list update: list configs with `learn_A=True | learn_B=True | use_parameter_learning=True | observation_noise > 0` as "needs rerun under decisions #6 + #9".
- add a CHANGELOG entry summarizing decisions #6 and #9.
- no source code changes in this commit. CI green.

**why this ordering works**:
- PR-1 (commit 1) is pure addition: `aif/` skeleton exists as dead code. zero behavioral change. reviewable in <30 minutes. de-risks the abstraction by getting it on `main` before any cutover.
- if PR-1 reveals problems (naming, factoring, missing helpers), they get fixed before any cutover work begins.
- PR-2 (commits 2–5) is the actual restructure. commit 2 is pure addition; commits 3–4 are cutovers; commit 5 is verification. each commit is independently green.
- commit 3 is the "model class" cutover. uses the new `TrustGameModel` everywhere `_BaseTrustGameModel` / `TrustGameModel` / `GradedTrustGameModel` were used.
- commit 4 is the "agent class" cutover and `agent/` directory deletion. atomic — `agent/` ceases to exist on disk in this single commit.
- if PR-2 is rejected after PR-1 lands, the `aif/` skeleton is dead code on `main` (can be reverted cleanly with a one-commit revert).

### behavior-equivalence verification protocol

two-tier verification. both tiers live as ordinary pytest code; **no binary blobs in git**, **no baseline parquets**, **no on-demand regeneration scripts**. optimized for agentic coding: every "captured" value is grep-able, reviewable in PR, and points to a specific failure when it fires.

**tier 1 — hand-written per-belief assertions (~30–50 of them)**

`tests/test_behavioral_equivalence_pinpoint.py` contains ~30–50 `assert_allclose` checks against specific (config, seed, round, modality) tuples. each was captured by running the **pre-PR SHA** once, eyeballing the value, and pasting it into the test. example:

```python
def test_smoke_test_seed42_round5_partner0_type_belief():
    """Captured from pre-PR SHA <abc123> on 2026-04-18 (decision #6/#9 baseline).
    Decision #6 + #9 should not affect this config (observation_noise=0,
    learn_*=False), so the post-PR code MUST reproduce these values
    bit-identically (atol=1e-6)."""
    cfg = load_config("smoke_test.json", overrides={"random_seed": 42})
    agent, env = build(cfg)
    run_rounds(agent, env, 5)
    assert_allclose(agent.partner_beliefs[0], [0.31, 0.19, 0.27, 0.23], atol=1e-6)
```

**coverage targets** (writing-plans pins the exact list):
- `smoke_test.json` — sanity baseline, 4 assertions
- `benchmark_default.json`, `benchmark_full.json` — ~6 assertions
- `h1_depth_affect_factorial.json`, `h2_lesion_dissociation.json`, `h4_betrayal_recovery.json`, `h5_partner_selection.json` — ~4 each = 16
- `graded_betrayal.json`, `graded_trust_factorial.json` — ~3 each = 6
- one `assignment_mode="agent_choice"` config — 4 assertions (covers `decode_raw_action_to_partner_and_social` path)
- one `observation_noise > 0` config — 3 assertions, marked `xfail` (decision #6 expected to change these)
- one `learn_A=True` config — 3 assertions, marked `xfail` (decision #9 expected to change these)

total: ~45 assertions. each is one line + a comment. ~500 lines of test file.

**why hand-written assertions and not a captured parquet**:
- code, not data. greppable, diff-reviewable in PR, versioned alongside the change.
- each failure is diagnostic: `partner_beliefs[0][2]` differs at round 5 of `smoke_test.json` seed 42 → exactly localizes the bug.
- agentic friendliness: an agent doing the refactor can read the assertions to understand "what we're promising to preserve". it can also re-derive a single assertion locally if it disagrees with a captured value.
- the `xfail` markers explicitly document the two intentional behavior changes (decisions #6, #9). when the agent runs the test suite post-refactor, an `xfail` flipping to `xpass` (or vice versa) would scream loudly.

**tier 2 — aggregate sweep test**

`tests/test_behavioral_equivalence_aggregates.py` runs **every** config in `configs/` (excluding cvc) for ~50 rounds with 5 seeds, computes 5 aggregate metrics per (config, seed), and compares against `tests/data/equivalence_aggregates.json` (~10 KB, checked in, plain JSON, fully reviewable).

aggregate metrics per (config, seed):
- `mean_payoff`
- `cooperation_rate` (fraction of own-actions that were cooperative; for graded mode: mean investment level / max)
- `mean_final_partner_belief_entropy` (averaged across partners)
- `mean_final_beta` (only for affective configs; null otherwise)
- `total_partner_switches` (count of times the agent's MAP partner-type estimate flipped)

JSON shape:

```json
{
  "captured_from_sha": "abc123def",
  "captured_on": "2026-04-18",
  "configs": {
    "smoke_test.json": {
      "seed_42": {"mean_payoff": 1.83, "cooperation_rate": 0.62, "mean_final_partner_belief_entropy": 1.21, "mean_final_beta": null, "total_partner_switches": 3},
      "seed_43": {...}, "seed_44": {...}, "seed_45": {...}, "seed_46": {...}
    },
    "h1_depth_affect_factorial.json": {...},
    ...
  },
  "post_pr_acceptance": {
    "no_learning_no_noise": {"atol": 1e-6, "behavior": "must match bit-identical"},
    "with_learning_or_noise": {"cooperation_rate_atol": 0.10, "mean_payoff_rtol": 0.15, "behavior": "direction + order of magnitude"}
  }
}
```

**why per-seed and not mean-across-seeds**:
- diagnostic: if seed 44 diverges and seeds 42/43/45/46 don't, that's a clue (probably an RNG ordering issue in one branch). means-only would hide it.
- size: 5× per-config still under 10 KB total. trivially small.
- agentic: when the test fails on one seed, the failure message names the seed → the agent can rerun just that seed locally to debug.

**rerun expectations** (also captured in STATE.md blockers list):

| config bucket | tier-1 expectation | tier-2 expectation |
|---|---|---|
| no learning, no noise (≈12 of 24) | bit-identical (`atol=1e-6`) | bit-identical aggregates |
| `observation_noise > 0`           | tier-1 assertions marked `xfail` (decision #6) | direction + order-of-magnitude only |
| any `learn_*=True`                | tier-1 assertions marked `xfail` (decision #9) | direction + order-of-magnitude only |
| `use_parameter_learning=True`     | tier-1 marked `xfail` (decision #9 affects it too) | direction + order-of-magnitude only |

**capturing the baseline (one-time, before PR-2)**:
1. on the pre-PR SHA, run `pytest -q --collect-only tests/test_behavioral_equivalence_pinpoint.py` to confirm test stubs exist.
2. for each test, replace the `assert_allclose([...placeholder...])` with the actual value from running the test in "capture mode" (a small `--capture-baseline` flag the test file exposes that prints values instead of asserting).
3. run `python tests/data/regenerate_aggregates.py` (a small script committed alongside the JSON) on the pre-PR SHA. it dumps fresh aggregates → diff against the checked-in JSON → the diff IS the captured snapshot.
4. commit the populated assertions and the JSON in PR-2 commit 5.

**total artifact footprint**:
- `tests/test_behavioral_equivalence_pinpoint.py`: ~500 lines of pytest code
- `tests/test_behavioral_equivalence_aggregates.py`: ~150 lines of test code
- `tests/data/equivalence_aggregates.json`: ~10 KB plain JSON
- `tests/data/regenerate_aggregates.py`: ~80 lines of script code
- **no parquet, no h5, no binary blob.**

### notebook update plan

verified: 0 notebooks import `agent.*`. only notebook touched is `notebooks/04_apashea_trust_spec.ipynb` — but only as a **reference** notebook (it imports `pymdp` directly to teach the AIF API). nothing to update for the import rewrite.

**new notebook (optional, defer to follow-up tasks)**: a parallel `notebooks/05_aif_standalone_demo.ipynb` showing andrew's setup using our `aif.Agent` instead of `pymdp.Agent`. proves abstraction equivalence. flagged as a follow-up, not required for B+A merge.

### things flagged in this section

1. **archive/ is untouched.** `archive/legacy_discrete_beta/` and `archive/scripts/run_*_clinical.py` reference removed class names and config keys. they stay broken (they were already archived). writing-plans should add a one-line `archive/README.md` note clarifying this.
2. **commit-1 dead code**: writing-plans should explicitly call out that commit 1's `aif/` files have no inbound imports. linters might flag this; if so, add a `# noqa` or move to commit 2.
3. **no baseline parquet** (decision finalized this turn). verification artifacts are pure code + tiny JSON; total <15 KB checked into git.
4. **PR-2 is still large** (~2–3k LOC of moves/renames/deletes). most of it is mechanical (`from agent.X` → `from aif.X` or `from trust.X`). reviewers should focus on (a) `trust/model.py` constructor + bug fix, (b) `trust/agent.py` per-partner architecture, (c) `trust/rollout.py` per-partner planner signature, (d) the equivalence-test harness. the rest can be eyeballed.

---

## section 6 — testing strategy (drafted, pending review)

four buckets: (a) new tests for `aif/`, (b) ported tests for `trust/`, (c) equivalence tests (already specced in Section 5), (d) regression tests for the two intentional behavior changes (decisions #6, #9). plus one bucket for deletions.

### a — new tests for `aif/` (pure additions, no analog in current suite)

| test file | what it covers | LOC |
|---|---|---|
| `tests/test_aif_agent.py` | `aif.Agent` construction, `reset()`, dataclass field defaults, `rng` reproducibility | ~120 |
| `tests/test_aif_inference.py` | `aif.infer_states` 1-step Bayes update against a hand-computed posterior on a 2-state-1-modality toy POMDP. `aif.infer_policies` returns sane `(q_pi, G)` shapes and `q_pi` sums to 1. | ~180 |
| `tests/test_aif_policies.py` | `construct_policies` enumerates correctly under both flat and factorized control specs. `sample_action(agent, q_pi)` respects `agent.action_sampling` and `agent.rng`. | ~120 |
| `tests/test_aif_learning.py` | `update_pA`, `update_pB`, `update_pD`, `update_pE` — each in-place updates the right Dirichlet hyperparam, leaves others untouched, and the resulting expected-A/expected-B move in the right direction | ~200 |
| `tests/test_aif_efe.py` | `compute_expected_free_energy` matches a hand-computed value on a tiny POMDP. utility-only and info-gain-only branches each isolated. | ~120 |
| `tests/test_aif_runtime.py` | `generate_observation_sequences` produces correct-shape obj_array. `RuntimeConfig` resolves devices correctly. | ~80 |
| `tests/test_aif_affect_beta.py` | `DiscreteBetaState` with `entity_idx=` API. parity check against the old `partner_idx=` behavior on a recorded sequence. | ~150 |

**andrew's notebook reproducibility**: a single integration test `tests/test_aif_apashea_parity.py` (~100 LOC) uses `aif.Agent` to reproduce the first 5 timesteps of `notebooks/04_apashea_trust_spec.ipynb`'s setup. proves `aif/` is a real generic abstraction, not just a relabeled `agent/inference/`. **acceptance criterion**: posterior beliefs at each of the first 5 timesteps match the notebook's `pymdp.Agent` outputs to `atol=1e-3` (loose because we use 1-step Bayes vs pymdp's MMP — see follow-up tasks).

**totals for bucket a**: ~970 LOC of new test code, 8 new test files.

### b — ported tests for `trust/` (existing tests with import + class-name updates)

| current test file | becomes | what changes |
|---|---|---|
| `tests/test_generative_model.py` | (kept name) | `from agent.model.trust_game import GradedTrustGameModel, TrustGameModel` → `from trust.model import TrustGameModel`. all `GradedTrustGameModel(cfg)` → `TrustGameModel({**cfg, "payoff_mode": "graded"})`. otherwise identical. |
| `tests/test_action_dependent_model.py` | (kept name) | same pattern |
| `tests/test_core.py` | (kept name) | imports updated; `BaseAgent` → `TrustGameAgent` |
| `tests/test_joint_agent_and_conditions.py` | (kept name) | imports + class names updated |
| `tests/test_hesp_agents.py` | (kept name) | imports + class names. uses `AffectiveAgent` and `LesionedAgent`; assertions unchanged. |
| `tests/test_hesp_v3_model.py`, `test_hesp_precision_modulation.py` | (kept) | import updates only |
| `tests/test_theory_alignment.py` | (kept) | import updates only |
| `tests/test_supported_surface.py` | **partial rewrite** | tests assert which classes/symbols are exported. needs to assert against `aif.*` and `trust.*` rather than `agent.*`. |
| `tests/test_environment.py` | (kept) | import update only (`from agent.model.types import PARTNER_TYPE_ORDER` → `from trust.types import PARTNER_TYPE_ORDER`) |
| `tests/test_stance_dynamics.py` | (kept) | import update only |
| `tests/test_discrete_beta.py` | (kept name) | imports updated to `aif.affect.beta.DiscreteBetaState`. all `partner_idx=` kwargs → `entity_idx=`. |
| `tests/test_interoception.py` | **delete** | tests `agent/affect/interoception.py` which is being deleted (10-line YAGNI stub) |
| `tests/conftest.py` | partial rewrite | fixtures that build agents/models updated to new imports + class names |

**totals for bucket b**: 13 files updated, 1 deleted, no LOC change to speak of (mechanical edits).

### c — equivalence tests (specced in Section 5, listed here for completeness)

- `tests/test_behavioral_equivalence_pinpoint.py` — ~500 LOC, ~45 hand-written `assert_allclose` checks. pre-PR baselines captured one-time.
- `tests/test_behavioral_equivalence_aggregates.py` — ~150 LOC, runs every config in `configs/` (excluding cvc), compares aggregates to `tests/data/equivalence_aggregates.json`.
- `tests/data/equivalence_aggregates.json` — ~10 KB, per-(config, seed) aggregate metrics.
- `tests/data/regenerate_aggregates.py` — ~80 LOC, one-time capture script.

### d — regression tests for intentional behavior changes

these are **new** tests that exist *because* of the two intentional bug fixes. they will fail on the old code and pass on the new code — the opposite of equivalence tests.

**decision #6 — `infer_joint_posterior` payoff-drop fix:**

`tests/test_payoff_modality_in_likelihood.py` (~120 LOC):

```python
def test_payoff_modality_actually_contributes_to_posterior():
    """Decision #6: o_payoff must contribute to the joint posterior.
    
    Construct a config where o_partner_action is uninformative (uniform across
    types/stances) but o_payoff strongly discriminates. The posterior MUST
    diverge from the prior. Pre-fix code keeps posterior == prior here."""
    model = TrustGameModel({
        "payoff_mode": "binary",
        "observation_noise": 0.5,            # makes o_partner_action uninformative
        "mutual_coop":   (10.0, 10.0),       # makes payoffs strongly discriminate
        "sucker":        (-10.0, 10.0),
        "temptation":    (10.0, -10.0),
        "mutual_defect": (-10.0, -10.0),
    })
    prior = uniform_joint_belief(model)
    posterior = model.infer_joint_posterior(prior, observation=[0, 1], own_action=0)
    
    assert not np.allclose(posterior, prior, atol=0.05), (
        "Posterior identical to prior — payoff modality is being dropped (regression of #6)."
    )

def test_observation_likelihood_requires_own_action():
    """Decision #6 fail-fast: own_action=None must raise."""
    model = TrustGameModel({"payoff_mode": "binary"})
    with pytest.raises(ValueError, match="own_action"):
        model.observation_likelihood([0, 1], own_action=None)

def test_observation_likelihood_requires_both_modalities():
    """Decision #6 fail-fast: missing payoff modality must raise."""
    model = TrustGameModel({"payoff_mode": "binary"})
    with pytest.raises(ValueError, match="both modalities"):
        model.observation_likelihood([0], own_action=0)
```

**decision #9 — per-partner Dirichlet learning:**

`tests/test_per_partner_learning.py` (~180 LOC):

```python
def test_each_partner_has_independent_pA():
    """Decision #9: pA is per-partner, not shared."""
    cfg = {"payoff_mode": "binary", "num_partners": 3}
    agent = TrustGameAgent(TrustGameModel(cfg), learn_A=True, pA_scale=1.0)
    
    # All three partners' pA start identical (fresh copies of the same canonical):
    for i in range(1, 3):
        assert_allclose(agent.partners[0].pA[0], agent.partners[i].pA[0])
    
    # Mutating one must not affect the others:
    agent.partners[0].pA[0] += 5.0
    for i in range(1, 3):
        assert not np.allclose(agent.partners[0].pA[0], agent.partners[i].pA[0])

def test_observe_outcome_only_updates_active_partner_pA():
    """Decision #9: observe_outcome(partner_idx=k) updates only partners[k].pA/pB."""
    cfg = {"payoff_mode": "binary", "num_partners": 3, "observation_noise": 0.0}
    agent = TrustGameAgent(TrustGameModel(cfg), learn_A=True)
    
    pA_before = [p.pA[0].copy() for p in agent.partners]
    agent.observe_outcome(partner_idx=1, observation=[0, 0], action_taken=0,
                          partner_action=0, payoff=3.0)
    pA_after = [p.pA[0].copy() for p in agent.partners]
    
    assert_allclose(pA_after[0], pA_before[0])               # untouched
    assert not np.allclose(pA_after[1], pA_before[1])         # changed
    assert_allclose(pA_after[2], pA_before[2])               # untouched

def test_per_partner_A_diverges_under_asymmetric_evidence():
    """Decision #9: after running with two different partners producing different
    cooperation rates, partners[0].A and partners[1].A diverge. Pre-#9 code keeps
    them identical (single shared partner_action_prob_table)."""
    # ... 30-line scenario simulating asymmetric partners
    assert not np.allclose(agent.partners[0].A[0], agent.partners[1].A[0], atol=0.01)
```

**combined regression tests for decisions #6 + #9:**

`tests/test_decisions_combined_smoke.py` (~80 LOC): one end-to-end smoke test confirming a `learn_A=True, observation_noise=0.3, num_partners=4` config runs to completion with the new semantics, finishes without errors, and produces final beliefs that are **different from** the pre-PR baseline (proving the fix actually changed behavior, in case both `xfail`s on tier-1 silently went green by accident).

### e — tests deleted

| test file | reason |
|---|---|
| `tests/test_interoception.py` | tests `agent/affect/interoception.py`, which is deleted (10-line YAGNI stub) |
| any test asserting `_BaseTrustGameModel` is a subclass of something | `_BaseTrustGameModel` no longer exists |
| any test asserting `GradedTrustGameModel` is a separate class | `GradedTrustGameModel` no longer exists; replaced with `TrustGameModel({"payoff_mode": "graded", ...})` |

writing-plans should grep for `_BaseTrustGameModel`, `GradedTrustGameModel`, `agent.model`, `agent.base.BaseAgent` and resolve each hit explicitly.

### test-suite shape after B+A

| bucket | files | new LOC | net file delta |
|---|---|---|---|
| (a) new `aif/` tests | 8 new files | ~970 | +8 |
| (b) ported `trust/` tests | 13 updated, 1 deleted | ~0 net | -1 |
| (c) equivalence tests | 2 new files + 1 JSON + 1 script | ~730 | +4 |
| (d) regression tests | 3 new files | ~380 | +3 |
| (e) deletions | 1 (interoception) | -50 | (counted in b) |
| **total** | | **~+2080 LOC of test code** | **+14 net new files** |

`pytest tests/` runtime expected to grow from ~30s today to ~90s post-restructure (most of the added time is the aggregate sweep test running every config).

### CI integration

- pre-PR-1 (`aif/` skeleton): only the 8 new `aif/` tests need to pass. they're testing dead code; no risk of regression elsewhere.
- pre-PR-2 (real cutover): full test suite including ported `trust/` tests, equivalence tests, and regression tests must all pass.
- the two `xfail`-marked tier-1 assertions (decision #6, decision #9) flipping to `xpass` would indicate something subtle is wrong — CI should be configured to treat unexpected `xpass` as a **failure** (`pytest --runxfail` semantics or per-test `strict=True`). writing-plans pins this.

### things flagged in this section

1. **andrew's notebook parity test uses `atol=1e-3` not `1e-6`** because we run 1-step Bayes vs pymdp's MMP. acknowledged as expected. tighter tolerance is a follow-up task (introduce optional MMP inference in `aif`).
2. **aggregate sweep test runs every config including `benchmark_*.json` non-cvc ones**. some of those are slow (~5s each). total CI time grows by ~60s. acceptable; if not, drop to a representative subset and document which configs are excluded.
3. **`xfail` strictness**: this is a real pytest config decision. the spec says strict=True; writing-plans should add the corresponding `pytest.ini` or `pyproject.toml` line.
4. **decision #9 test "asymmetric evidence" scenario** (~30 lines) needs careful construction so that pre-PR code would fail it but post-PR code passes it. writing-plans should include a one-time validation step: run the test on the pre-PR SHA, confirm it fails with the right error, then check it in.

---

## known divergences from `pomdp_spec.md` v4

1. **`infer_joint_posterior` previously dropped `o_payoff` modality.** fixed in this restructure (decision #6). spec compliance restored.
2. **partner-blind Dirichlet learning** previously accumulated evidence into a single shared `partner_action_prob_table` regardless of which partner produced the observation. fixed in this restructure (decision #9). pymdp-style per-instance learning restored.
3. **factorized controls `[N,2,2]` vs spec's strict §4 `[1,2,2]`.** intentional, documented in MISSION.md. preserved.
4. **`C[1]` log-softmax instead of raw softmax.** intentional, documented. preserved.
5. **graded variant uses interpolated `cooperation_evidence_strength` for stance dynamics rather than two discrete slices.** intentional. preserved.

---

## multi-focal-agent compatibility (informative — sub-project F handles the runtime)

a follow-on sub-project (**F**) will build a runtime where M focal active-inference agents play the trust game with each other (instead of one focal AIF + scripted partners). this section *proves* the B+A design supports F by composition and pins down the contract sub-project F will rely on.

**why this matters now**: pomdp_spec.md v4 §1 explicitly describes "N agents interact in a repeated trust game with turn-taking". multi-focal is the canonical setup. it is **not** behaviorally equivalent to N separate single-focal-vs-scripted games — beliefs co-evolve, emergent dynamics arise (cooperation buildup, defection cascades), 2-level mind-modeling structure that scripted partners cannot produce. by ensuring the B+A design supports it, we don't have to retouch `aif/` or `trust/` when F lands.

**the contract that B+A guarantees for F**:

1. `trust.TrustGameAgent` is fully self-contained — no implicit assumption that there is only one focal agent in a process.
2. `TrustGameAgent.choose_partner_and_action(active_partner)` returns a `raw_action` (int) in the env action space. the F runner can decode `(partner_idx, social_action)` via `trust.rollout.decode_raw_action_to_partner_and_social`.
3. `TrustGameAgent.observe_outcome(partner_idx, observation, action_taken, partner_action, payoff)` accepts everything the F runner has after resolving a pair's joint action.
4. `num_partners` is a config-driven property of each `TrustGameAgent` and corresponds to *the agent's own model of how many partners it tracks*. for an M-focal-agent experiment, each agent has `num_partners = M-1` (no self-modeling) or `M` (with self-modeling) depending on F's convention.
5. **per-partner private Dirichlet learning** (decision #9) is what makes heterogeneous M-agent populations work cleanly: each focal agent learns about each of its partners independently. agent A's belief about agent B does not leak into agent A's belief about agent C.
6. `TrustGameModel` is shared-construction: F can give all M agents the same `TrustGameModel` instance (each `TrustGameAgent` will still build its own per-partner A/B copies internally), or different instances (e.g., heterogeneous preference temperatures).
7. `aif.Agent` carries no awareness of multi-agent or multi-focal contexts. spawning M `aif.Agent`s (or M `TrustGameAgent`s, each containing N internal `aif.Agent`s) produces M × N agents and is fine.

**what F builds (NOT in B+A)**:
- `experiment/multi_focal_runner.py` — drives M `TrustGameAgent`s per round.
- `experiment/pairing.py` — round-robin / all-pairs / random / mutual-selection.
- `experiment/joint_resolution.py` — resolves M chosen actions into per-pair payoffs and the `(partner_action, payoff)` observations each agent receives.
- new config schema for heterogeneous populations.
- tests for emergent dynamics.

**B+A action items to ensure compatibility**:
- ✅ `decode_raw_action_to_partner_and_social` is part of `trust/rollout.py`'s public surface.
- ✅ `TrustGameAgent.observe_outcome` signature accepts the pair-resolution outputs F produces.
- ✅ per-partner private Dirichlet learning (decision #9) makes heterogeneous populations work without contamination.
- ⚠️ writing-plans should add a smoke-test task: *"with the post-B+A code, manually instantiate two `TrustGameAgent`s and run a single round of mutual selection"* — to confirm composability before F starts. ~30 minutes of work.

---

## explicitly out of scope (B+A)

- **CvC / cogames / observatory stack** (`benchmark/cvc_*.py`, `benchmark/cogames_adapter.py`, `configs/benchmark_cvc_*.json`, `tests/test_cvc_*.py`, `tests/test_observatory_*.py`). per `conductor/MISSION.md`, do not touch beyond import-line rewrites necessary for compilation.
- **agent inventory cleanup** (decisions about which agents to keep, baselines, broken `AIFPolicy` stub). belongs to sub-project C.
- **experiment / config pruning** + hypothesis label cleanup. belongs to sub-project D.
- **doc rewrite** beyond the immediate spec doc. belongs to sub-project E.
- **paper updates** (`docs/paper/main.tex`). after sub-project E.
- **new MMP-style inference in `aif.infer_states`.** see follow-up tasks.

---

## follow-up tasks (post-this-spec)

these are things the brainstorming surfaced that are explicitly NOT in this spec but should be tracked:

1. **introduce optional MMP-style multi-step inference** in `aif.infer_states`. current implementation is single-step Bayes only. andrew's notebook uses `MMP` algo with `inference_horizon=3`. would let us match his protocol exactly.
2. **typed `TrustGameConfig` dataclass** to replace the dict-based constructor surface. low priority cleanup.
3. **populate `aif/examples/`** with andrew's single-partner notebook reformulated as a runnable test, demonstrating `aif/` standalone usage outside the trust project. confirms the abstraction is real.
4. **decide what to do with `aif/affect/interoception.py`** when interoception modality is actually wired up (currently deleted).

---

## handoff (per scoping doc)

on completion of this spec + its writing-plans plan:

1. commit this spec to `docs/superpowers/specs/`
2. commit implementation plan from writing-plans to `docs/superpowers/plans/`
3. append entry under "completed sub-projects" in scoping doc
4. NOT start implementation in the same session — implementation runs in a fresh executing-plans session
