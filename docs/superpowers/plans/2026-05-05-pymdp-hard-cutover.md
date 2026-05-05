# pymdp Hard Cutover Implementation Plan

> Historical implementation-plan artifact. Stale custom-runtime phrases below are migration checkpoints or search patterns, not supported public architecture. Current supported runtime is official `inferactively-pymdp==1.0.0` with task-local trust and affect wrappers.


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the custom active-inference runtime with official `inferactively-pymdp==1.0.0`, while keeping trust-game semantics and affective precision tracking as the project-owned layer.

**Architecture:** Official `pymdp` owns active-inference inference, planning, and action sampling. `tasks/trust` owns model construction, environments, per-partner wrappers, beta precision tracking, and experiment-facing diagnostics. This is a hard cutover: no dual backend, no compatibility shim, no supported top-level custom `aif` package.

**Tech Stack:** Python, NumPy, JAX-backed official `inferactively-pymdp==1.0.0`, pytest, existing trust experiment scripts.

---

## Source Design

Use the approved design spec:

- `docs/superpowers/specs/2026-05-04-pymdp-hard-cutover-design.md`

Use these references:

- `notebooks/references/apashea_trust_spec.ipynb` for project-specific A/B/C/D/E and factorized-control shape.
- `https://github.com/apashea/pymdp` for helper ideas only.
- Official `pymdp` docs/API for runtime behavior.

## Core Rules

- Do not retain custom `aif` inference, EFE, rollout, learning, policy construction, or policy sampling as supported runtime code.
- Do not add a backend flag.
- Do not add imports that fall back from `pymdp` to `aif`.
- Do not preserve old tests whose only purpose is validating the deleted custom core.
- Keep result-interpretation docs unchanged unless the user explicitly approves updating interpretations from new outputs.

## Target File Structure

```text
tasks/trust/
├── affect.py                  # task-local beta / precision tracking
├── pymdp_helpers.py           # thin helpers around official pymdp diagnostics
├── agents/
│   ├── base.py                # pymdp-backed TrustGameAgent
│   ├── affective.py           # affect modulation
│   └── lesioned.py            # lesion variants
├── models/
│   └── trust_game.py          # A/B/C/D/E and policy bundle construction
├── envs/
├── payoffs.py
├── stance.py
└── types.py
```

The end state should not expose `import aif` as a supported package.

## Task 1: Pin official pymdp and add dependency guard

**Files:**

- Modify: `pyproject.toml`
- Create: `tests/test_pymdp_dependency.py`

- [ ] **Step 1: Add dependency test**

Create `tests/test_pymdp_dependency.py`:

```python
from __future__ import annotations

import importlib.metadata as metadata


def test_official_inferactively_pymdp_is_pinned() -> None:
    assert metadata.version("inferactively-pymdp") == "1.0.0"


def test_pymdp_agent_api_is_available() -> None:
    from pymdp.agent import Agent

    assert Agent is not None
```

- [ ] **Step 2: Run dependency test to verify current failure**

Run:

```bash
python -m pytest tests/test_pymdp_dependency.py -q
```

Expected:

```text
FAIL or ERROR because inferactively-pymdp is missing or not pinned to 1.0.0
```

- [ ] **Step 3: Pin official pymdp**

Modify `pyproject.toml` dependency list to include:

```toml
"inferactively-pymdp==1.0.0"
```

If the project uses another dependency file instead of, or in addition to,
`pyproject.toml`, pin the same package there and remove duplicate unpinned
entries.

- [ ] **Step 4: Install dependencies**

Run the project-standard dependency install command. If no project-standard
command exists, use:

```bash
python -m pip install -e .
```

Expected:

```text
inferactively-pymdp==1.0.0 installs successfully
```

- [ ] **Step 5: Run dependency test**

Run:

```bash
python -m pytest tests/test_pymdp_dependency.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml tests/test_pymdp_dependency.py
git commit -m "build: pin official pymdp runtime"
```

## Task 2: Move affect out of custom aif

**Files:**

- Create: `tasks/trust/affect.py`
- Modify: `tasks/trust/agents/affective.py`
- Modify: `tasks/trust/agents/lesioned.py`
- Modify: `tasks/trust/__init__.py`
- Create: `tests/test_trust_affect.py`
- Delete later: `aif/affect/beta.py`
- Delete later: `aif/affect/__init__.py`

- [ ] **Step 1: Write task-local affect tests**

Create `tests/test_trust_affect.py`:

```python
from __future__ import annotations

import numpy as np

from tasks.trust.affect import DiscreteBetaState


def test_discrete_beta_state_starts_at_requested_level() -> None:
    state = DiscreteBetaState(num_entities=3, initial_beta=1.0)

    np.testing.assert_allclose(state.expected_beta(), np.array([1.0, 1.0, 1.0]))


def test_low_surprise_decreases_beta_rate() -> None:
    state = DiscreteBetaState(num_entities=1, initial_beta=1.0)

    before = state.expected_beta()[0]
    state.update(entity=0, surprise=0.0)
    after = state.expected_beta()[0]

    assert after < before


def test_high_surprise_increases_beta_rate() -> None:
    state = DiscreteBetaState(num_entities=1, initial_beta=1.0)

    before = state.expected_beta()[0]
    state.update(entity=0, surprise=1.0)
    after = state.expected_beta()[0]

    assert after > before
```

- [ ] **Step 2: Run affect tests to verify failure**

Run:

```bash
python -m pytest tests/test_trust_affect.py -q
```

Expected:

```text
ERROR because tasks.trust.affect does not exist
```

- [ ] **Step 3: Create `tasks/trust/affect.py`**

Move the supported `DiscreteBetaState` behavior from `aif/affect/beta.py` into
`tasks/trust/affect.py`.

Required public API:

```python
class DiscreteBetaState:
    def __init__(
        self,
        num_entities: int,
        initial_beta: float = 1.0,
        beta_levels: Sequence[float] | None = None,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        persistence: float = 0.8,
    ) -> None: ...

    def expected_beta(self) -> np.ndarray: ...

    def update(self, entity: int, surprise: float) -> None: ...
```

Keep the HESP inverse-beta convention:

```python
gamma_k = gamma_base / expected_beta_k
```

- [ ] **Step 4: Update affect imports**

Replace:

```python
from aif.affect.beta import DiscreteBetaState
```

with:

```python
from tasks.trust.affect import DiscreteBetaState
```

Only update supported trust-agent code in this task. Do not preserve an `aif`
alias.

- [ ] **Step 5: Run affect tests**

Run:

```bash
python -m pytest tests/test_trust_affect.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 6: Commit**

```bash
git add tasks/trust/affect.py tasks/trust/agents/affective.py tasks/trust/agents/lesioned.py tasks/trust/__init__.py tests/test_trust_affect.py
git commit -m "refactor: move affect tracking into trust task"
```

## Task 3: Build a pymdp-ready trust model bundle

**Files:**

- Modify: `tasks/trust/models/trust_game.py`
- Create: `tests/test_trust_pymdp_model.py`

- [ ] **Step 1: Write model bundle tests**

Create `tests/test_trust_pymdp_model.py`:

```python
from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.models import TrustGameModel


def test_binary_model_exports_pymdp_bundle_shapes() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary"))
    bundle = model.to_pymdp_bundle()

    assert len(bundle.A) == 2
    assert len(bundle.B) == 3
    assert bundle.A[0].shape == (2, 4, 3, 2)
    assert bundle.A[1].shape == (4, 4, 3, 2)
    assert bundle.B[0].shape == (4, 4, 1)
    assert bundle.B[1].shape == (3, 3, 2)
    assert bundle.B[2].shape == (2, 2, 2)
    assert bundle.control_fac_idx == [1, 2]


def test_binary_model_pymdp_bundle_is_normalized() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary"))
    bundle = model.to_pymdp_bundle()

    for A_m in bundle.A:
        np.testing.assert_allclose(A_m.sum(axis=0), 1.0)
    for B_f in bundle.B:
        np.testing.assert_allclose(B_f.sum(axis=0), 1.0)


def test_policies_have_pymdp_shape() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary"))
    bundle = model.to_pymdp_bundle(planning_horizon=2)

    assert bundle.policies.ndim == 3
    assert bundle.policies.shape[1] == 2
    assert bundle.policies.shape[2] == 3
```

- [ ] **Step 2: Run model bundle tests to verify failure**

Run:

```bash
python -m pytest tests/test_trust_pymdp_model.py -q
```

Expected:

```text
FAIL because to_pymdp_bundle is missing
```

- [ ] **Step 3: Add model bundle dataclass**

In `tasks/trust/models/trust_game.py`, add:

```python
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PymdpTrustModelBundle:
    A: Any
    B: Any
    C: Any
    D: Any
    E: Any
    policies: np.ndarray
    control_fac_idx: list[int]
    num_obs: list[int]
    num_states: list[int]
    num_controls: list[int]
    payoff_values: list[int]
```

- [ ] **Step 4: Implement `TrustGameModel.to_pymdp_bundle`**

Add method:

```python
def to_pymdp_bundle(
    self,
    planning_horizon: int = 1,
    max_policies: int | None = None,
    rng: np.random.Generator | None = None,
) -> PymdpTrustModelBundle:
    ...
```

Implementation requirements:

- Reuse existing trust-game A/B/C/D construction.
- Return object arrays or lists accepted by official `pymdp.Agent`.
- Use factorized controls for binary trust games.
- Preserve Apashea reference order: hidden factors are `s_type`, `s_stance`, `s_own`.
- Construct policies with shape `(num_policies, planning_horizon, num_factors)`.
- Use `control_fac_idx=[1, 2]` for the local partner agent.
- Use uniform `E` over policies unless config/model specifies otherwise.

- [ ] **Step 5: Run model bundle tests**

Run:

```bash
python -m pytest tests/test_trust_pymdp_model.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 6: Commit**

```bash
git add tasks/trust/models/trust_game.py tests/test_trust_pymdp_model.py
git commit -m "feat: export trust model for pymdp"
```

## Task 4: Add thin pymdp helper layer

**Files:**

- Create: `tasks/trust/pymdp_helpers.py`
- Create: `tests/test_trust_pymdp_helpers.py`

- [ ] **Step 1: Write helper tests**

Create `tests/test_trust_pymdp_helpers.py`:

```python
from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.models import TrustGameModel
from tasks.trust.pymdp_helpers import create_agent, infer_once, select_first_timestep_action


def test_create_agent_uses_official_pymdp_agent() -> None:
    bundle = TrustGameModel(ExperimentConfig(payoff_mode="binary")).to_pymdp_bundle()
    agent = create_agent(bundle, gamma=1.0)

    assert agent.__class__.__module__.startswith("pymdp.")


def test_infer_once_returns_policy_diagnostics() -> None:
    bundle = TrustGameModel(ExperimentConfig(payoff_mode="binary")).to_pymdp_bundle()
    agent = create_agent(bundle, gamma=1.0)

    result = infer_once(agent, obs=[0, 2], bundle=bundle)

    assert result.q_pi.ndim == 1
    assert np.isclose(result.q_pi.sum(), 1.0)
    assert result.policy_scores.shape == result.q_pi.shape


def test_select_first_timestep_action_returns_factor_actions() -> None:
    bundle = TrustGameModel(ExperimentConfig(payoff_mode="binary")).to_pymdp_bundle()
    q_pi = np.zeros(len(bundle.policies), dtype=float)
    q_pi[0] = 1.0

    action = select_first_timestep_action(bundle.policies, q_pi, deterministic=True)

    assert action.shape == (bundle.policies.shape[2],)
```

- [ ] **Step 2: Run helper tests to verify failure**

Run:

```bash
python -m pytest tests/test_trust_pymdp_helpers.py -q
```

Expected:

```text
ERROR because tasks.trust.pymdp_helpers does not exist
```

- [ ] **Step 3: Implement helper result dataclass**

Create `tasks/trust/pymdp_helpers.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class PymdpInferenceResult:
    qs: Any
    q_pi: np.ndarray
    policy_scores: np.ndarray
    info: dict[str, Any]
```

- [ ] **Step 4: Implement `create_agent`**

Implement:

```python
def create_agent(bundle, gamma: float):
    from pymdp.agent import Agent

    return Agent(
        A=bundle.A,
        B=bundle.B,
        C=bundle.C,
        D=bundle.D,
        E=bundle.E,
        policies=bundle.policies,
        control_fac_idx=bundle.control_fac_idx,
        gamma=gamma,
    )
```

If official `pymdp==1.0.0` uses a different constructor signature, adapt here
only. Keep the adaptation local to this helper module.

- [ ] **Step 5: Implement `infer_once`**

Implement:

```python
def infer_once(agent, obs: list[int], bundle) -> PymdpInferenceResult:
    qs_result = agent.infer_states(obs)
    qs = qs_result[0] if isinstance(qs_result, tuple) else qs_result

    policy_result = agent.infer_policies(qs) if _infer_policies_accepts_qs(agent) else agent.infer_policies()
    if isinstance(policy_result, tuple):
        q_pi = np.asarray(policy_result[0], dtype=float)
        scores = np.asarray(policy_result[1], dtype=float)
    else:
        q_pi = np.asarray(agent.q_pi, dtype=float)
        scores = np.asarray(getattr(agent, "neg_efe", getattr(agent, "G", np.zeros_like(q_pi))), dtype=float)

    return PymdpInferenceResult(qs=qs, q_pi=q_pi, policy_scores=scores, info={})
```

Use official API inspection carefully. The helper should hide API differences
from trust agents.

- [ ] **Step 6: Implement first-timestep policy action selection**

Implement:

```python
def select_first_timestep_action(
    policies: np.ndarray,
    q_pi: np.ndarray,
    deterministic: bool,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    policy_idx = int(np.argmax(q_pi)) if deterministic else int((rng or np.random.default_rng()).choice(len(q_pi), p=q_pi))
    return np.asarray(policies[policy_idx, 0], dtype=int)
```

- [ ] **Step 7: Run helper tests**

Run:

```bash
python -m pytest tests/test_trust_pymdp_helpers.py -q
```

Expected:

```text
3 passed
```

- [ ] **Step 8: Commit**

```bash
git add tasks/trust/pymdp_helpers.py tests/test_trust_pymdp_helpers.py
git commit -m "feat: add thin pymdp trust helpers"
```

## Task 5: Rewrite TrustGameAgent around pymdp

**Files:**

- Modify: `tasks/trust/agents/base.py`
- Modify: `tasks/trust/agents/__init__.py`
- Modify: `tasks/trust/__init__.py`
- Create: `tests/test_pymdp_trust_agent.py`

- [ ] **Step 1: Write agent behavior tests**

Create `tests/test_pymdp_trust_agent.py`:

```python
from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust import TrustGameAgent, TrustGameModel


def test_trust_game_agent_uses_pymdp_partner_agents() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=2))
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0)

    assert len(agent.partners) == 2
    assert all(p.__class__.__module__.startswith("pymdp.") for p in agent.partners)


def test_agent_can_plan_and_observe_single_outcome() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=2))
    agent = TrustGameAgent(model=model, planning_horizon=1, seed=0)

    action = agent.plan_and_act(active_partner=0)
    assert isinstance(action, int)

    agent.observe_outcome(
        active_partner=0,
        agent_action=action % 2,
        partner_action=0,
        payoff=3.0,
        observation=[0, 2],
    )

    assert agent.partner_beliefs.shape[0] == 2
    np.testing.assert_allclose(agent.partner_beliefs[0].sum(), 1.0)
```

- [ ] **Step 2: Run agent tests to verify failure**

Run:

```bash
python -m pytest tests/test_pymdp_trust_agent.py -q
```

Expected:

```text
FAIL because TrustGameAgent still uses custom aif.Agent
```

- [ ] **Step 3: Remove custom aif imports from base agent**

In `tasks/trust/agents/base.py`, remove imports from:

```python
import aif
from aif.learning import ...
from aif.runtime import ...
from aif.utils import ...
```

Replace with:

```python
from tasks.trust import pymdp_helpers
```

and model-bundle imports from `tasks.trust.models.trust_game`.

- [ ] **Step 4: Replace partner construction**

Build one official `pymdp.Agent` per partner:

```python
self.bundle = model.to_pymdp_bundle(
    planning_horizon=self.planning_horizon,
    max_policies=self.max_policies,
    rng=self.rng,
)
self.partners = [
    pymdp_helpers.create_agent(self.bundle, gamma=self.gamma)
    for _ in range(self.num_partners)
]
```

Keep public attributes used by loggers:

```python
self.q_pi = None
self.policy_scores = None
self.best_policy_idx = None
self.selected_partner = None
self.selected_action = None
self.partner_beliefs = np.zeros((self.num_partners, 4, 3), dtype=float)
```

- [ ] **Step 5: Implement random-assignment action selection**

For `active_partner is not None`, run inference/planning against that partner's
`pymdp.Agent`.

Required behavior:

```python
local = self._infer_partner(active_partner)
factor_action = pymdp_helpers.select_first_timestep_action(
    self.bundle.policies,
    local.q_pi,
    deterministic=self.action_selection == "deterministic",
    rng=self.rng,
)
raw_action = self._encode_factor_action(active_partner, factor_action)
```

Return the raw environment action expected by existing envs.

- [ ] **Step 6: Implement agent-choice action selection**

Do not build a huge global product POMDP. Evaluate each partner independently
through its own `pymdp.Agent`, then aggregate first-step candidate scores:

```python
candidates = []
for partner_idx in range(self.num_partners):
    result = self._infer_partner(partner_idx)
    for policy_idx, score in enumerate(result.policy_scores):
        first = self.bundle.policies[policy_idx, 0]
        candidates.append((partner_idx, policy_idx, first, score))
```

Softmax candidate scores with any supported policy prior. Choose candidate,
then encode raw action as:

```python
partner_idx * 4 + stance_action * 2 + own_action
```

This is the new hard-cutover semantics for partner choice. Do not call old
custom rollout code.

- [ ] **Step 7: Implement outcome observation**

`observe_outcome` should:

- infer states for the active partner using official `pymdp`
- store latest `qs`
- update `partner_beliefs[partner_idx]` from type x stance marginal
- refresh any diagnostics needed by the logger
- avoid custom `aif.update_pA` and old rollout calls

- [ ] **Step 8: Run agent tests**

Run:

```bash
python -m pytest tests/test_pymdp_trust_agent.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 9: Commit**

```bash
git add tasks/trust/agents/base.py tasks/trust/agents/__init__.py tasks/trust/__init__.py tests/test_pymdp_trust_agent.py
git commit -m "feat: rewrite trust agent on pymdp"
```

## Task 6: Rewire affective and lesioned agents

**Files:**

- Modify: `tasks/trust/agents/affective.py`
- Modify: `tasks/trust/agents/lesioned.py`
- Modify: `tasks/trust/pymdp_helpers.py`
- Modify: `tests/test_pymdp_trust_agent.py`
- Create or modify: `tests/test_hesp_agents.py`
- Create or modify: `tests/test_theory_alignment.py`

- [ ] **Step 1: Add affective agent tests**

Add to `tests/test_pymdp_trust_agent.py`:

```python
from tasks.trust import AffectiveAgent, LesionedAgent


def test_affective_agent_updates_beta_after_observation() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=1))
    agent = AffectiveAgent(model=model, planning_horizon=1, seed=0, initial_beta=1.0)

    before = agent.affect.expected_beta()[0]
    agent.observe_outcome(
        active_partner=0,
        agent_action=0,
        partner_action=1,
        payoff=-1.0,
        observation=[1, 0],
    )
    after = agent.affect.expected_beta()[0]

    assert after != before


def test_lesioned_decouple_updates_beta_but_uses_base_precision() -> None:
    model = TrustGameModel(ExperimentConfig(payoff_mode="binary", num_partners=1))
    agent = LesionedAgent(model=model, planning_horizon=1, seed=0, lesion_mode="decouple")

    assert agent.affect_modulates_precision is False
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_pymdp_trust_agent.py::test_affective_agent_updates_beta_after_observation tests/test_pymdp_trust_agent.py::test_lesioned_decouple_updates_beta_but_uses_base_precision -q
```

Expected:

```text
FAIL because affective/lesioned agents still assume old aif internals
```

- [ ] **Step 3: Rewire `AffectiveAgent`**

Make `AffectiveAgent` inherit the new `TrustGameAgent` and own:

```python
self.affect = DiscreteBetaState(...)
self.affect_modulates_precision = affect_modulates_precision
```

Before policy selection for partner `k`, compute:

```python
expected_beta = self.affect.expected_beta()[k]
partner_gamma = self.gamma / expected_beta if self.affect_modulates_precision else self.gamma
```

Pass `partner_gamma` into the helper path for that partner.

- [ ] **Step 4: Rewire beta update**

After observing partner action, compute social surprise:

```python
surprise = 1.0 - predicted_partner_action_probability
self.affect.update(entity=active_partner, surprise=surprise)
```

The predicted partner-action probability should be read from the current
partner belief and `A[0]`. If a diagnostic is unavailable, compute it directly
from the bundle A matrix and current type x stance belief.

- [ ] **Step 5: Rewire `LesionedAgent`**

Supported modes:

```text
decouple: beta updates but does not modulate policy precision
fixed: beta remains fixed and does not modulate policy precision
```

Remove old paths that depend on `aif` internals.

- [ ] **Step 6: Run affective tests**

Run:

```bash
python -m pytest tests/test_pymdp_trust_agent.py tests/test_trust_affect.py -q
```

Expected:

```text
all tests pass
```

- [ ] **Step 7: Commit**

```bash
git add tasks/trust/agents/affective.py tasks/trust/agents/lesioned.py tasks/trust/pymdp_helpers.py tests/test_pymdp_trust_agent.py tests/test_hesp_agents.py tests/test_theory_alignment.py
git commit -m "feat: layer affect on pymdp agents"
```

## Task 7: Adapt experiment runners and logging

**Files:**

- Modify: `experiments/trust/factory.py`
- Modify: `experiments/trust/runner.py`
- Modify: `experiments/trust/logger.py`
- Modify: `experiments/multifocal/runner.py`
- Modify: `tests/test_experiment_e2e_lightweight.py`
- Modify: `tests/test_multi_focal_round_loop.py`

- [ ] **Step 1: Write or update experiment smoke assertions**

In `tests/test_experiment_e2e_lightweight.py`, ensure the smoke test asserts:

```python
assert "q_pi_entropy" in results.columns
assert "partner_beliefs" in results.columns
assert "selected_action" in results.columns
assert "selected_partner" in results.columns
```

Keep the test lightweight.

- [ ] **Step 2: Run experiment smoke to verify failure**

Run:

```bash
python -m pytest tests/test_experiment_e2e_lightweight.py -q
```

Expected:

```text
FAIL where runner/logger expects old custom agent diagnostics
```

- [ ] **Step 3: Update factory**

`experiments/trust/factory.py` should instantiate the rewritten:

```python
TrustGameAgent
AffectiveAgent
LesionedAgent
```

Do not pass old custom-core-only arguments. Remove or ignore config fields only
after docs are updated.

- [ ] **Step 4: Update logger**

Map new agent diagnostics to existing result columns where meaningful:

```text
q_pi -> agent.q_pi
best_policy_idx -> agent.best_policy_idx
partner_beliefs -> agent.partner_beliefs
prediction_errors -> agent.latest_surprise_by_partner
beta -> affective agent expected beta
terminal_signal -> beta-derived or NaN if not supported
```

If an old diagnostic only existed because of custom EFE internals, remove it
from supported docs or set it to `NaN` with an explicit docs update.

- [ ] **Step 5: Update multifocal runner**

Replace direct assumptions about old `factorized_policies` internals with
public methods:

```python
raw_action = agent.plan_and_act(active_partner=partner_idx)
agent.observe_outcome(...)
```

Avoid reading custom policy arrays from outside the agent unless unavoidable.

- [ ] **Step 6: Run runner tests**

Run:

```bash
python -m pytest tests/test_experiment_e2e_lightweight.py tests/test_multi_focal_round_loop.py -q
```

Expected:

```text
all tests pass
```

- [ ] **Step 7: Commit**

```bash
git add experiments/trust/factory.py experiments/trust/runner.py experiments/trust/logger.py experiments/multifocal/runner.py tests/test_experiment_e2e_lightweight.py tests/test_multi_focal_round_loop.py
git commit -m "refactor: adapt experiments to pymdp agents"
```

## Task 8: Remove legacy custom aif package and tests

**Files:**

- Delete: `aif/`
- Delete or rewrite: `tests/test_aif_agent.py`
- Delete or rewrite: `tests/test_aif_affect_beta.py`
- Delete or rewrite: `tests/test_aif_apashea_parity.py`
- Delete or rewrite: `tests/test_aif_inference.py`
- Delete or rewrite: `tests/test_aif_jax_core.py`
- Delete or rewrite: `tests/test_aif_learning.py`
- Delete or rewrite: `tests/test_aif_policies.py`
- Delete or rewrite: `tests/test_core.py`
- Delete or rewrite: `tests/test_hesp_precision_modulation.py`
- Modify: `tests/test_package_surface.py`
- Modify: `tests/test_supported_surface.py`

- [ ] **Step 1: Search for remaining supported `aif` imports**

Run:

```bash
rg -n "from aif|import aif|aif\\." --glob '!archive/**' --glob '!results/**' --glob '!notebooks/**'
```

Expected:

```text
Only legacy tests/docs still reference aif
```

- [ ] **Step 2: Delete custom-core tests**

Remove tests that validate deleted code rather than supported behavior:

```bash
rm tests/test_aif_agent.py
rm tests/test_aif_affect_beta.py
rm tests/test_aif_apashea_parity.py
rm tests/test_aif_inference.py
rm tests/test_aif_jax_core.py
rm tests/test_aif_learning.py
rm tests/test_aif_policies.py
rm tests/test_core.py
rm tests/test_hesp_precision_modulation.py
```

If any test contains a still-valid trust/affect behavior, port that behavior to
the new trust tests before deleting the old file.

- [ ] **Step 3: Delete `aif/`**

Remove:

```bash
rm -rf aif
```

This is intentional. Do not keep `aif/__init__.py` as an alias.

- [ ] **Step 4: Update package surface tests**

In `tests/test_package_surface.py` and `tests/test_supported_surface.py`, remove
expectations that `aif` is importable or supported.

Add expectations that these are importable:

```python
import tasks.trust.affect
import tasks.trust.pymdp_helpers
from tasks.trust import TrustGameAgent, AffectiveAgent, LesionedAgent
```

- [ ] **Step 5: Search again**

Run:

```bash
rg -n "from aif|import aif|aif\\." --glob '!archive/**' --glob '!results/**' --glob '!notebooks/**'
```

Expected:

```text
No supported runtime imports remain
```

Docs may still reference historical `aif` until Task 9.

- [ ] **Step 6: Run package and trust tests**

Run:

```bash
python -m pytest tests/test_package_surface.py tests/test_supported_surface.py tests/test_trust_affect.py tests/test_pymdp_trust_agent.py -q
```

Expected:

```text
all tests pass
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: remove legacy custom aif engine"
```

## Task 9: Update documentation for hard cutover

**Files:**

- Modify: `README.md`
- Modify: `docs/state/current/mission.md`
- Modify: `docs/state/decisions/architecture.md`
- Modify: `docs/theory/apashea_alignment.md`
- Modify: `docs/theory/pomdp_spec.md`
- Modify: `docs/design/implementation.md`
- Modify: `docs/experiment/design.md`
- Modify: `docs/future/roadmap.md`
- Modify: `notebooks/README.md`
- Modify: `AGENTS.md` if it still describes the old custom core as supported

- [ ] **Step 1: Search docs for stale custom-core language**

Run:

```bash
rg -n "does not embed pymdp|reusable JAX-based `aif/` core|aif\\.Agent|aif\\.affect|custom active-inference|No pymdp migration path|without embedding pymdp" README.md docs AGENTS.md notebooks/README.md
```

Expected:

```text
Matches identify stale docs to update
```

- [ ] **Step 2: Update README**

Required README claims:

```markdown
The supported trust-game runtime is built on official `inferactively-pymdp==1.0.0`.
Project code owns trust-game model construction, affective precision tracking,
experiments, logging, and analysis.
```

Remove setup or architecture text that tells users to use custom `aif`.

- [ ] **Step 3: Update architecture and mission docs**

In `docs/state/current/mission.md`, replace the custom-core mission with:

```markdown
Re-ground affect_aif around official `inferactively-pymdp==1.0.0`, trust-task
wrappers, external affective precision tracking, canonical script-driven
experiments, and docs/state steering.
```

In `docs/state/decisions/architecture.md`, record:

```markdown
The project no longer owns the active-inference engine. Official `pymdp` is the
runtime dependency; Apashea's notebook/fork is reference material for model
construction and helper ideas.
```

- [ ] **Step 4: Update theory/design docs**

Required changes:

```text
docs/theory/apashea_alignment.md: official pymdp is runtime, Apashea is reference.
docs/theory/pomdp_spec.md: keep A/B/C/D/E spec, remove "without embedding pymdp".
docs/design/implementation.md: describe pymdp.Agent wrappers and task-local affect.
docs/experiment/design.md: describe pymdp policy inference plus external beta.
docs/future/roadmap.md: remove stale "no pymdp migration path" decision.
notebooks/README.md: reference notebook is not runtime dependency.
```

- [ ] **Step 5: Update AGENTS.md if needed**

If `AGENTS.md` still says preserve `aif/` as a reusable core, update it to say:

```markdown
Do not reintroduce a custom active-inference engine. Use official
`inferactively-pymdp==1.0.0`; keep affect/trust logic in task modules.
```

- [ ] **Step 6: Search docs again**

Run:

```bash
rg -n "does not embed pymdp|reusable JAX-based `aif/` core|aif\\.Agent|aif\\.affect|No pymdp migration path|without embedding pymdp" README.md docs AGENTS.md notebooks/README.md
```

Expected:

```text
No stale supported-runtime claims remain
```

Historical mentions are acceptable only if explicitly marked historical.

- [ ] **Step 7: Commit**

```bash
git add README.md docs notebooks/README.md AGENTS.md
git commit -m "docs: document pymdp hard cutover"
```

## Task 10: Final validation gate

**Files:**

- No implementation files unless failures reveal missed migration edits.

- [ ] **Step 1: Run import search**

Run:

```bash
rg -n "from aif|import aif|aif\\." --glob '!archive/**' --glob '!results/**' --glob '!notebooks/**'
```

Expected:

```text
No supported runtime imports remain
```

- [ ] **Step 2: Run focused test suite**

Run:

```bash
python -m pytest \
  tests/test_pymdp_dependency.py \
  tests/test_trust_pymdp_model.py \
  tests/test_trust_pymdp_helpers.py \
  tests/test_trust_affect.py \
  tests/test_pymdp_trust_agent.py \
  tests/test_experiment_e2e_lightweight.py \
  tests/test_multi_focal_round_loop.py \
  tests/test_package_surface.py \
  tests/test_supported_surface.py \
  -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 3: Run smoke script**

Run:

```bash
python scripts/experiment/smoke.py
```

Expected:

```text
smoke run completes and writes expected lightweight outputs
```

- [ ] **Step 4: Run full tests only if time permits**

Run:

```bash
python -m pytest tests/ -q
```

Expected:

```text
all remaining supported tests pass
```

If failures are from tests asserting deleted custom `aif` behavior, delete or
rewrite those tests instead of restoring legacy code.

- [ ] **Step 5: Commit final fixes**

```bash
git add -A
git commit -m "test: verify pymdp hard cutover"
```

## Implementation Notes for Workers

- Use official `pymdp` APIs as the runtime contract, even if Apashea's fork has
  convenient helpers.
- Keep all fork-inspired helpers in `tasks/trust/pymdp_helpers.py`.
- If official `pymdp` exposes diagnostics differently, adapt only the helper
  module.
- If a logger field no longer has a meaningful source, document it and remove
  it or emit `NaN`; do not rebuild a custom active-inference engine to preserve
  the field.
- For agent-choice mode, prefer independent per-partner `pymdp.Agent`
  evaluation plus global candidate aggregation over a huge product-state POMDP.
- Do not update interpretation of experiment results from new outputs without
  user approval.

## Handoff Options

Recommended execution mode:

```text
superpowers:subagent-driven-development
```

Use one worker per task where write sets do not overlap, then review and
integrate sequentially. If implementing inline, use:

```text
superpowers:executing-plans
```

and stop after each task for review.
