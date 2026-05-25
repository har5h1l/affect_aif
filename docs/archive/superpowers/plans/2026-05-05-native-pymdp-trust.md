# Native pymdp Trust Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current `pymdp`-backed custom agent/model architecture with a native `pymdp` runtime where the experiment loop directly constructs and uses official `pymdp.Agent` instances from a trust POMDP template.

**Architecture:** This is a hard transition, not an adapter refactor. The final runtime shape is `trust POMDP template -> official pymdp.Agent -> procedural experiment loop`, with only affect tracking and multi-partner bookkeeping around `pymdp.Agent`. Old custom agent classes, old model-wrapper responsibilities, `plan_and_act`, `observe_outcome`, and `get_metrics` are removed from the documented runtime surface.

**Tech Stack:** Python, JAX/JAX NumPy arrays at the `pymdp` boundary, official `inferactively-pymdp==1.0.0`, NumPy for task/env/logging glue, pytest.

---

## Source Design

Use the approved design spec:

- `docs/superpowers/specs/2026-05-05-native-pymdp-trust-design.md`

This plan supersedes the earlier hard-cutover plan where it conflicts. The earlier plan moved the engine to `pymdp`; this plan removes the remaining legacy-shaped custom agent/model layer.

## Hard Transition Invariants

Do not implement this as a compatibility adapter.

- No backend flags.
- No old class wrappers that delegate to the new procedural implementation.
- No documented `TrustGameAgent`, `AffectiveAgent`, or `LesionedAgent` runtime API.
- No `agent.plan_and_act(...)`.
- No `agent.observe_outcome(...)`.
- No `agent.get_metrics()`.
- No custom inference, EFE, rollout, or policy-sampling logic.
- No import fallbacks to old agent/model modules.
- No tests that assert old custom agent classes are first-class runtime objects.

Allowed custom code:

- POMDP template construction.
- Multi-partner list/table of official `pymdp.Agent` instances.
- External beta/affective precision tracking.
- Environment action/observation mapping.
- Experiment snapshots/logging.

## Task 1: Add native POMDP template surface

**Files:**

- Create: `tasks/trust/pomdp.py`
- Create: `tests/test_native_pymdp_template.py`
- Modify later: `tasks/trust/__init__.py`

- [ ] **Step 1: Write failing native template tests**

Create `tests/test_native_pymdp_template.py`:

```python
from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents, create_pymdp_agent


def test_template_exports_jax_arrays_and_expected_shapes() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=4),
        planning_horizon=2,
    )

    assert len(template.A) == 2
    assert len(template.B) == 3
    assert template.A[0].shape == (2, 4, 3, 2)
    assert template.A[1].shape == (4, 4, 3, 2)
    assert template.B[0].shape == (4, 4, 1)
    assert template.B[1].shape == (3, 3, 2)
    assert template.B[2].shape == (2, 2, 2)
    assert template.control_fac_idx == (1, 2)
    assert all(isinstance(array, jnp.ndarray) for array in template.A)
    assert all(isinstance(array, jnp.ndarray) for array in template.B)
    assert all(isinstance(array, jnp.ndarray) for array in template.C)
    assert all(isinstance(array, jnp.ndarray) for array in template.D)
    assert isinstance(template.E, jnp.ndarray)


def test_template_preserves_probability_normalization() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=4),
        planning_horizon=2,
    )

    for A_m in template.A:
        np.testing.assert_allclose(np.asarray(A_m).sum(axis=0), 1.0)
    for B_f in template.B:
        np.testing.assert_allclose(np.asarray(B_f).sum(axis=0), 1.0)
    np.testing.assert_allclose(np.asarray(template.E).sum(), 1.0)


def test_template_can_create_official_pymdp_agents() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=3),
        planning_horizon=1,
    )

    agent = create_pymdp_agent(template, gamma=1.0)
    partner_agents = create_partner_agents(template, num_partners=3, gamma=1.0)

    assert agent.__class__.__module__.startswith("pymdp.")
    assert len(partner_agents) == 3
    assert all(partner.__class__.__module__.startswith("pymdp.") for partner in partner_agents)
```

- [ ] **Step 2: Run test and confirm failure**

Run:

```bash
python -m pytest tests/test_native_pymdp_template.py -q
```

Expected:

```text
ERROR because tasks.trust.pomdp does not exist
```

- [ ] **Step 3: Implement `TrustPomdpTemplate` dataclass**

Create `tasks/trust/pomdp.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import jax.numpy as jnp
import numpy as np


@dataclass(frozen=True)
class TrustPomdpLabels:
    observation_modalities: tuple[str, ...]
    hidden_factors: tuple[str, ...]
    control_factors: tuple[str, ...]
    partner_types: tuple[str, ...]
    stances: tuple[str, ...]
    own_actions: tuple[str, ...]


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
```

- [ ] **Step 4: Move static POMDP construction into pure functions**

Move the static construction logic currently in `TrustGameModel` into pure functions in `tasks/trust/pomdp.py`.

Required functions:

```python
def build_trust_pomdp_template(
    config: Any | Mapping[str, Any],
    *,
    planning_horizon: int,
    max_policies: int | None = None,
    rng: np.random.Generator | None = None,
) -> TrustPomdpTemplate:
    ...
```

Implementation requirements:

- Preserve the current A/B/C/D/E values and shapes.
- Preserve hidden factor order: `type`, `stance`, `own_action`.
- Preserve observation modality order: `partner_action`, `payoff`.
- Preserve `control_fac_idx=(1, 2)`.
- Emit JAX arrays for `A`, `B`, `C`, `D`, `E`, and `policies`.
- Do not instantiate or depend on `TrustGameModel`.
- Reuse domain helpers from `payoffs.py`, `stance.py`, and `types.py`.

- [ ] **Step 5: Implement direct agent constructors**

Add:

```python
def create_pymdp_agent(template: TrustPomdpTemplate, *, gamma: float):
    from pymdp.agent import Agent

    return Agent(
        A=template.A,
        B=template.B,
        C=template.C,
        D=template.D,
        E=template.E,
        policies=template.policies,
        control_fac_idx=list(template.control_fac_idx),
        gamma=gamma,
    )


def create_partner_agents(template: TrustPomdpTemplate, *, num_partners: int, gamma: float):
    return [create_pymdp_agent(template, gamma=gamma) for _ in range(int(num_partners))]
```

If official `pymdp==1.0.0` needs a slightly different constructor signature, adapt here only.

- [ ] **Step 6: Run template tests**

Run:

```bash
python -m pytest tests/test_native_pymdp_template.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 7: Commit**

```bash
git add tasks/trust/pomdp.py tests/test_native_pymdp_template.py
git commit -m "feat: add native pymdp trust template"
```

## Task 2: Add tiny procedural runtime functions

**Files:**

- Create: `tasks/trust/runtime.py`
- Create: `tests/test_native_pymdp_runtime.py`

- [ ] **Step 1: Write failing runtime tests**

Create `tests/test_native_pymdp_runtime.py`:

```python
from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents
from tasks.trust.runtime import (
    PartnerBank,
    select_decision,
    snapshot_partner_bank,
    update_partner_after_observation,
)


def test_partner_bank_is_not_an_agent_wrapper() -> None:
    template = build_trust_pomdp_template(
        ExperimentConfig(payoff_mode="binary", num_partners=2),
        planning_horizon=1,
    )
    bank = PartnerBank(agents=create_partner_agents(template, num_partners=2, gamma=1.0))

    assert not hasattr(bank, "plan_and_act")
    assert not hasattr(bank, "observe_outcome")
    assert not hasattr(bank, "get_metrics")


def test_select_decision_returns_raw_environment_action() -> None:
    config = ExperimentConfig(payoff_mode="binary", num_partners=2)
    template = build_trust_pomdp_template(config, planning_horizon=1)
    bank = PartnerBank(agents=create_partner_agents(template, num_partners=2, gamma=1.0))

    decision = select_decision(
        bank=bank,
        template=template,
        active_partner=0,
        assignment_mode="random",
        base_gamma=1.0,
        action_selection="deterministic",
        rng=np.random.default_rng(0),
    )

    assert isinstance(decision.raw_action, int)
    assert decision.selected_partner == 0
    assert decision.q_pi.ndim == 1


def test_update_partner_after_observation_updates_snapshots() -> None:
    config = ExperimentConfig(payoff_mode="binary", num_partners=1)
    template = build_trust_pomdp_template(config, planning_horizon=1)
    bank = PartnerBank(agents=create_partner_agents(template, num_partners=1, gamma=1.0))

    update_partner_after_observation(
        bank=bank,
        template=template,
        partner_idx=0,
        obs=[0, 2],
        own_action=0,
    )
    snapshot = snapshot_partner_bank(bank=bank, template=template)

    assert snapshot.partner_joint_beliefs.shape == (1, 4, 3)
    np.testing.assert_allclose(snapshot.partner_joint_beliefs[0].sum(), 1.0)
```

- [ ] **Step 2: Run runtime tests and confirm failure**

Run:

```bash
python -m pytest tests/test_native_pymdp_runtime.py -q
```

Expected:

```text
ERROR because tasks.trust.runtime does not exist
```

- [ ] **Step 3: Implement runtime dataclasses**

Create `tasks/trust/runtime.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class PartnerBank:
    agents: list[Any]
    latest_qs: list[Any | None] = field(default_factory=list)
    posterior_qs: list[Any | None] = field(default_factory=list)
    beta: Any | None = None
    latest_surprise: np.ndarray | None = None

    def __post_init__(self) -> None:
        if not self.latest_qs:
            self.latest_qs = [None for _ in self.agents]
        if not self.posterior_qs:
            self.posterior_qs = [None for _ in self.agents]


@dataclass(frozen=True)
class Decision:
    raw_action: int
    selected_partner: int
    selected_action: int
    stance_action: int
    own_action: int
    q_pi: np.ndarray
    policy_scores: np.ndarray
    best_policy_idx: int
    predicted_partner_action_probs: np.ndarray
    predictive_log_lik: float


@dataclass(frozen=True)
class PartnerSnapshot:
    partner_type_beliefs: np.ndarray
    partner_stance_beliefs: np.ndarray
    partner_joint_beliefs: np.ndarray
    partner_joint_posteriors: np.ndarray
```

- [ ] **Step 4: Implement procedural planning**

Implement:

```python
def select_decision(
    *,
    bank: PartnerBank,
    template,
    active_partner: int | None,
    assignment_mode: str,
    base_gamma: float,
    action_selection: str,
    rng: np.random.Generator,
    affect_mode: str = "none",
) -> Decision:
    ...
```

Requirements:

- Use the selected partner's official `pymdp.Agent`.
- Use official `agent.infer_policies(...)`.
- Select from `template.policies`.
- For random assignment, force `selected_partner=active_partner`.
- For agent-choice, evaluate each local partner agent and choose a partner-policy pair.
- Do not call old `TrustGameAgent`.
- Do not create custom EFE.

- [ ] **Step 5: Implement procedural observation update**

Implement:

```python
def update_partner_after_observation(
    *,
    bank: PartnerBank,
    template,
    partner_idx: int,
    obs: list[int],
    own_action: int,
) -> Any:
    ...
```

Requirements:

- Update empirical prior for `s_own` to the executed own action if official `pymdp` requires it.
- Call official `agent.infer_states(...)`.
- Store returned `qs` in `bank.posterior_qs[partner_idx]`.
- Compute and store predictive/prior `latest_qs` for the next round using official `pymdp` transition behavior where available.
- Do not reimplement posterior inference.

- [ ] **Step 6: Implement snapshot extraction**

Implement:

```python
def snapshot_partner_bank(*, bank: PartnerBank, template) -> PartnerSnapshot:
    ...
```

This may convert factorized `qs` into type x stance snapshots for logs. Snapshot extraction is allowed; inference is not.

- [ ] **Step 7: Run runtime tests**

Run:

```bash
python -m pytest tests/test_native_pymdp_runtime.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 8: Commit**

```bash
git add tasks/trust/runtime.py tests/test_native_pymdp_runtime.py
git commit -m "feat: add native pymdp runtime functions"
```

## Task 3: Integrate affect as the only wrapper

**Files:**

- Modify: `tasks/trust/affect.py`
- Modify: `tasks/trust/runtime.py`
- Create: `tests/test_native_pymdp_affect.py`

- [ ] **Step 1: Write affect integration tests**

Create `tests/test_native_pymdp_affect.py`:

```python
from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.affect import DiscreteBetaState
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents
from tasks.trust.runtime import PartnerBank, gamma_for_partner, update_beta_after_observation


def test_gamma_for_partner_uses_hesp_inverse_beta() -> None:
    beta = DiscreteBetaState(num_entities=1, initial_beta=2.0)

    gamma = gamma_for_partner(base_gamma=4.0, beta=beta, partner_idx=0, affect_mode="normal")

    assert np.isclose(gamma, 2.0)


def test_decouple_mode_does_not_modulate_gamma() -> None:
    beta = DiscreteBetaState(num_entities=1, initial_beta=2.0)

    gamma = gamma_for_partner(base_gamma=4.0, beta=beta, partner_idx=0, affect_mode="decouple")

    assert np.isclose(gamma, 4.0)


def test_beta_update_uses_prediction_probability() -> None:
    template = build_trust_pomdp_template(ExperimentConfig(payoff_mode="binary", num_partners=1), planning_horizon=1)
    bank = PartnerBank(
        agents=create_partner_agents(template, num_partners=1, gamma=1.0),
        beta=DiscreteBetaState(num_entities=1, initial_beta=1.0),
    )

    before = bank.beta.expected_beta()[0]
    update_beta_after_observation(
        bank=bank,
        partner_idx=0,
        predicted_partner_action_probs=np.array([0.1, 0.9]),
        observed_partner_action=0,
        affect_mode="normal",
    )
    after = bank.beta.expected_beta()[0]

    assert after > before
```

- [ ] **Step 2: Run affect integration tests and confirm failure**

Run:

```bash
python -m pytest tests/test_native_pymdp_affect.py -q
```

Expected:

```text
FAIL because runtime affect helpers do not exist yet
```

- [ ] **Step 3: Add gamma helper**

In `tasks/trust/runtime.py`, add:

```python
def gamma_for_partner(*, base_gamma: float, beta, partner_idx: int, affect_mode: str) -> float:
    if beta is None or affect_mode in {"none", "decouple", "fixed"}:
        return float(base_gamma)
    expected_beta = float(np.asarray(beta.expected_beta(), dtype=float)[int(partner_idx)])
    return float(base_gamma) / max(expected_beta, 1e-16)
```

- [ ] **Step 4: Add beta update helper**

Add:

```python
def update_beta_after_observation(
    *,
    bank: PartnerBank,
    partner_idx: int,
    predicted_partner_action_probs: np.ndarray,
    observed_partner_action: int,
    affect_mode: str,
) -> float:
    if bank.beta is None or affect_mode in {"none", "fixed"}:
        return float("nan")
    probability = float(np.asarray(predicted_partner_action_probs, dtype=float)[int(observed_partner_action)])
    surprise = 1.0 - probability
    bank.beta.update(entity=int(partner_idx), surprise=surprise)
    if bank.latest_surprise is None:
        bank.latest_surprise = np.full((len(bank.agents),), np.nan, dtype=float)
    bank.latest_surprise[int(partner_idx)] = surprise
    return surprise
```

- [ ] **Step 5: Wire gamma helper into `select_decision`**

`select_decision` should compute partner-specific gamma through `gamma_for_partner(...)` before policy inference.

Use official `pymdp` update/replacement mechanics where possible. If the pinned official `pymdp.Agent` is frozen, centralize the minimal object update in one private helper and document that it is only setting official agent precision, not custom inference.

- [ ] **Step 6: Run affect integration tests**

Run:

```bash
python -m pytest tests/test_native_pymdp_affect.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 7: Commit**

```bash
git add tasks/trust/affect.py tasks/trust/runtime.py tests/test_native_pymdp_affect.py
git commit -m "feat: integrate affect with native pymdp runtime"
```

## Task 4: Rewrite experiment factory and runner around native runtime

**Files:**

- Modify: `experiments/trust/factory.py`
- Modify: `experiments/trust/runner.py`
- Modify: `experiments/trust/logger.py`
- Modify: `tests/test_experiment_e2e_lightweight.py`
- Create: `tests/test_native_runner_surface.py`

- [ ] **Step 1: Write native runner surface test**

Create `tests/test_native_runner_surface.py`:

```python
from __future__ import annotations

from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_native_runtime
from tasks.trust.runtime import PartnerBank


def test_factory_returns_native_runtime_without_custom_agent() -> None:
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_partners=2),
        condition=1,
        seed=0,
    )

    assert hasattr(runtime, "template")
    assert isinstance(runtime.partner_bank, PartnerBank)
    assert not hasattr(runtime, "plan_and_act")
    assert not hasattr(runtime, "observe_outcome")
```

- [ ] **Step 2: Run native runner surface test and confirm failure**

Run:

```bash
python -m pytest tests/test_native_runner_surface.py -q
```

Expected:

```text
FAIL because create_native_runtime does not exist
```

- [ ] **Step 3: Add native runtime factory**

In `experiments/trust/factory.py`, add:

```python
@dataclass
class NativeTrustRuntime:
    template: TrustPomdpTemplate
    partner_bank: PartnerBank
    affect_mode: str
    base_gamma: float
    action_selection: str
    rng: np.random.Generator
```

Add:

```python
def create_native_runtime(config: ExperimentConfig, condition: int | str, seed: int) -> NativeTrustRuntime:
    ...
```

Requirements:

- Resolve condition horizon and affect mode.
- Build `TrustPomdpTemplate`.
- Build partner agents directly with `create_partner_agents`.
- Attach `DiscreteBetaState` only for affective/lesioned conditions.
- Do not instantiate `TrustGameAgent`, `AffectiveAgent`, or `LesionedAgent`.

- [ ] **Step 4: Rewrite `_run_episode` in `ExperimentRunner`**

Replace:

```python
agent.plan_and_act(...)
agent.observe_outcome(...)
agent.get_metrics()
```

with:

```python
decision = select_decision(...)
result = env.step(decision.raw_action)
update_partner_after_observation(...)
update_beta_after_observation(...)
snapshot = snapshot_partner_bank(...)
logger.log_round(...)
```

The runner becomes the explicit procedural loop.

- [ ] **Step 5: Update logger input**

Update `MetricLogger.log_round(...)` to accept native inputs:

```python
decision: Decision
snapshot: PartnerSnapshot
beta_values: np.ndarray | None
surprise_values: np.ndarray | None
env_result: dict
```

If backwards compatibility with old `agent_metrics` is kept during the patch, remove it before Task 6 completion.

- [ ] **Step 6: Run runner tests**

Run:

```bash
python -m pytest tests/test_native_runner_surface.py tests/test_experiment_e2e_lightweight.py -q
```

Expected:

```text
all tests pass
```

- [ ] **Step 7: Commit**

```bash
git add experiments/trust/factory.py experiments/trust/runner.py experiments/trust/logger.py tests/test_native_runner_surface.py tests/test_experiment_e2e_lightweight.py
git commit -m "refactor: run experiments directly on pymdp agents"
```

## Task 5: Remove old custom agent/model runtime surface

**Files:**

- Delete: `tasks/trust/agents/base.py`
- Delete: `tasks/trust/agents/affective.py`
- Delete: `tasks/trust/agents/lesioned.py`
- Delete or empty/remove package export: `tasks/trust/agents/__init__.py`
- Delete or collapse: `tasks/trust/models/trust_game.py`
- Delete or collapse: `tasks/trust/models/__init__.py`
- Delete: `tasks/trust/pymdp_helpers.py`
- Modify: `tasks/trust/__init__.py`
- Modify/delete old tests asserting class surface:
  - `tests/test_hesp_agents.py`
  - `tests/test_joint_agent_and_conditions.py`
  - `tests/test_supported_surface.py`
  - `tests/test_theory_alignment.py`
  - `tests/test_pymdp_trust_agent.py`
  - `tests/test_trust_pymdp_model.py`
  - `tests/test_trust_pymdp_helpers.py`

- [ ] **Step 1: Search for old runtime imports**

Run:

```bash
rg -n "TrustGameAgent|AffectiveAgent|LesionedAgent|TrustGameModel|tasks\\.trust\\.agents|tasks\\.trust\\.models|pymdp_helpers|plan_and_act|observe_outcome|get_metrics" --glob '!archive/**' --glob '!results/**' --glob '!notebooks/**'
```

Expected:

```text
Matches show old runtime surface that must be removed or rewritten
```

- [ ] **Step 2: Rewrite tests to native surface**

Replace old class assertions with native assertions:

```python
from tasks.trust.pomdp import build_trust_pomdp_template, create_partner_agents
from tasks.trust.runtime import PartnerBank, select_decision, update_partner_after_observation
```

Remove tests whose only purpose is proving old classes exist.

- [ ] **Step 3: Delete old agent files**

Run:

```bash
rm tasks/trust/agents/base.py
rm tasks/trust/agents/affective.py
rm tasks/trust/agents/lesioned.py
rm tasks/trust/pymdp_helpers.py
```

Remove package exports from `tasks/trust/agents/__init__.py`, or delete the package if nothing imports it.

- [ ] **Step 4: Collapse old model module**

If no runtime imports need `TrustGameModel`, remove `tasks/trust/models/trust_game.py` and `tasks/trust/models/__init__.py`.

If a short transition is needed, replace `tasks/trust/models/trust_game.py` with a clear non-runtime error:

```python
raise ImportError("TrustGameModel was removed. Use tasks.trust.pomdp.build_trust_pomdp_template.")
```

Do not leave a class wrapper.

- [ ] **Step 5: Update package exports**

In `tasks/trust/__init__.py`, export only native surfaces:

```python
from tasks.trust.affect import DiscreteBetaState
from tasks.trust.pomdp import TrustPomdpTemplate, build_trust_pomdp_template, create_partner_agents, create_pymdp_agent
from tasks.trust.runtime import PartnerBank, select_decision, update_partner_after_observation
```

- [ ] **Step 6: Search again**

Run:

```bash
rg -n "TrustGameAgent|AffectiveAgent|LesionedAgent|TrustGameModel|tasks\\.trust\\.agents|tasks\\.trust\\.models|pymdp_helpers|plan_and_act|observe_outcome|get_metrics" --glob '!archive/**' --glob '!results/**' --glob '!notebooks/**'
```

Expected:

```text
No supported runtime or tests depend on old classes/methods
```

Historical docs may mention removed names only if explicitly marked historical.

- [ ] **Step 7: Run native tests**

Run:

```bash
python -m pytest \
  tests/test_native_pymdp_template.py \
  tests/test_native_pymdp_runtime.py \
  tests/test_native_pymdp_affect.py \
  tests/test_native_runner_surface.py \
  tests/test_experiment_e2e_lightweight.py \
  -q
```

Expected:

```text
all tests pass
```

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: remove custom trust agent runtime"
```

## Task 6: Update multifocal runtime or mark it out of scope

**Files:**

- Modify: `experiments/multifocal/runner.py`
- Modify: `experiments/multifocal/config.py`
- Modify: `tests/test_multi_focal_round_loop.py`
- Modify or skip: `tests/test_multi_focal_deterministic.py`
- Modify or skip: `tests/test_multi_focal_emergent.py`

- [ ] **Step 1: Decide scope**

If multifocal is required for current supported tests, port it to native runtime.

If multifocal is not part of the immediate supported surface, mark tests skipped with an explicit reason:

```python
pytestmark = pytest.mark.skip(reason="multifocal native pymdp migration is tracked separately")
```

Prefer porting if the changes are small.

- [ ] **Step 2: Port multifocal if in scope**

Replace focal-agent calls:

```python
focal.choose_partner_and_action(...)
focal.observe_outcome(...)
```

with native procedural calls:

```python
select_decision(...)
update_partner_after_observation(...)
update_beta_after_observation(...)
snapshot_partner_bank(...)
```

- [ ] **Step 3: Run multifocal tests**

Run:

```bash
python -m pytest tests/test_multi_focal_round_loop.py -q
```

Expected:

```text
pass or explicit skip with native migration reason
```

- [ ] **Step 4: Commit**

```bash
git add experiments/multifocal tests/test_multi_focal_round_loop.py tests/test_multi_focal_deterministic.py tests/test_multi_focal_emergent.py
git commit -m "refactor: align multifocal surface with native pymdp"
```

## Task 7: Update docs for native hard transition

**Files:**

- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/design/implementation.md`
- Modify: `docs/theory/apashea_alignment.md`
- Modify: `docs/theory/pomdp_spec.md`
- Modify: `docs/experiment/design.md`
- Modify: `docs/state/current/mission.md`
- Modify: `docs/state/decisions/architecture.md`
- Modify: `notebooks/README.md`

- [ ] **Step 1: Search stale docs**

Run:

```bash
rg -n "TrustGameAgent|AffectiveAgent|LesionedAgent|TrustGameModel|plan_and_act|observe_outcome|get_metrics|pymdp-backed|custom agent|tasks/trust/agents|tasks/trust/models" README.md AGENTS.md docs notebooks/README.md
```

Expected:

```text
Matches identify docs that still describe old runtime
```

- [ ] **Step 2: Update runtime architecture docs**

Required replacement language:

```markdown
The native runtime constructs a trust POMDP template and instantiates official
`pymdp.Agent` objects directly. Multi-partner experiments maintain a list of
partner-local `pymdp.Agent` instances plus external beta state. The experiment
runner performs the infer-policy-step-update loop procedurally.
```

- [ ] **Step 3: Update AGENTS.md**

Add a hard-transition rule:

```markdown
Do not reintroduce `TrustGameAgent`, `AffectiveAgent`, `LesionedAgent`, or
`TrustGameModel` as runtime abstractions. Use `tasks.trust.pomdp` to build
POMDP templates and official `pymdp.Agent` for inference/planning.
```

- [ ] **Step 4: Update theory docs carefully**

Keep scientific claims identical:

- same A/B/C/D/E
- same factorized controls
- same external beta
- same HESP inverse-beta precision mapping
- same betrayal/stance semantics

Only change implementation wording.

- [ ] **Step 5: Search stale docs again**

Run:

```bash
rg -n "TrustGameAgent|AffectiveAgent|LesionedAgent|TrustGameModel|plan_and_act|observe_outcome|get_metrics|pymdp-backed|custom agent|tasks/trust/agents|tasks/trust/models" README.md AGENTS.md docs notebooks/README.md
```

Expected:

```text
No stale supported-runtime claims remain
```

Historical mentions must be explicitly marked historical or migration context.

- [ ] **Step 6: Commit**

```bash
git add README.md AGENTS.md docs notebooks/README.md
git commit -m "docs: document native pymdp runtime"
```

## Task 8: Final hard-transition validation

**Files:**

- No planned implementation files.
- Modify only if validation reveals missed native migration edits.

- [ ] **Step 1: Run forbidden-symbol search**

Run:

```bash
rg -n "TrustGameAgent|AffectiveAgent|LesionedAgent|TrustGameModel|plan_and_act|observe_outcome|get_metrics|tasks\\.trust\\.agents|tasks\\.trust\\.models|pymdp_helpers" --glob '!archive/**' --glob '!results/**' --glob '!notebooks/**'
```

Expected:

```text
No supported runtime/test references remain
```

- [ ] **Step 2: Run native focused suite**

Run:

```bash
python -m pytest \
  tests/test_native_pymdp_template.py \
  tests/test_native_pymdp_runtime.py \
  tests/test_native_pymdp_affect.py \
  tests/test_native_runner_surface.py \
  tests/test_experiment_e2e_lightweight.py \
  tests/test_package_surface.py \
  tests/test_supported_surface.py \
  -q
```

Expected:

```text
all tests pass
```

- [ ] **Step 3: Run smoke script**

Run:

```bash
python scripts/experiment/smoke.py
```

Expected:

```text
smoke run completes using native pymdp runtime
```

- [ ] **Step 4: Run full supported tests**

Run:

```bash
python -m pytest tests/ -q
```

Expected:

```text
all supported tests pass or explicitly skipped with current native-migration reason
```

- [ ] **Step 5: Commit validation fixes**

```bash
git add -A
git commit -m "test: verify native pymdp transition"
```

## Worker Guidance

- Prefer deleting legacy code over adapting it.
- If a test failure asks for old agent classes, update the test to native runtime unless it reveals a true behavior regression.
- Preserve the original trust-game science logic exactly. If you think logic must change, stop and ask.
- Keep all active-inference calls inside official `pymdp.Agent`.
- Keep custom code boring: matrix construction, beta tracking, partner table, action encoding, logging.
- Do not update interpretation of experiment results from new outputs without user approval.

