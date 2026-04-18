# aif/ extraction + canonical TrustGameModel — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** extract a generic `aif/` package, consolidate the trust-game model into a single canonical class, fix the `infer_joint_posterior` payoff-drop bug, and adopt per-partner Dirichlet learning — all in two PRs (no shims, no back-compat) without changing behavior on the no-learning / no-noise config subset.

**Architecture:** `agent/` is split into `aif/` (generic POMDP runtime, pymdp-style: stateful `Agent` dataclass + free functions for inference/learning) and `trust/` (project package: `TrustGameAgent` composes N per-partner `aif.Agent` instances; `TrustGameModel` is the canonical generative model with a `payoff_mode={"binary","graded"}` switch). Two intentional behavior changes land in this work: the `o_payoff` modality is now used in belief updates (decision #6), and Dirichlet learning is now per-partner private (decision #9).

**Tech Stack:** Python 3.11, NumPy, JAX (for `aif/runtime.py` JAX dispatch only), pytest, pytest-xfail.

**Spec reference:** [`docs/superpowers/specs/2026-04-18-aif-extraction-design.md`](../specs/2026-04-18-aif-extraction-design.md). Decision numbers in this plan refer to that spec's decision log.

**Branch convention:** PR-1 = `restructure/aif-skeleton`. PR-2 = `restructure/aif-cutover` (branched from `main` after PR-1 merges).

---

## Overview of phases

| phase | PR | what it produces | est. duration |
|---|---|---|---|
| 0 | — | worktree + branch setup | 10 min |
| 1 | PR-1 | `aif/` skeleton with verbatim moves, dead code on main | 2-3 h |
| 2 | PR-2 | `aif/agent.py`, `aif/inference.py`, `aif/affect/beta.py` (real new abstractions) | 3-4 h |
| 3 | PR-2 | `trust/` model layer + canonical `TrustGameModel` + bug fix + factory cutover | 4-5 h |
| 4 | PR-2 | `trust/` agent layer + per-partner architecture + `agent/` deletion | 5-7 h |
| 5 | PR-2 | verification artifacts (tier-1 + tier-2 equivalence tests, regression tests, STATE.md) | 4-6 h |

PR-1 lands first and is reviewed independently. PR-2 is branched from `main` after PR-1 merges.

---

## Phase 0: setup

### Task 0.1: create PR-1 worktree and branch

**Files:**
- Create: worktree `../affect_aif-restructure-pr1`
- Branch: `restructure/aif-skeleton`

- [ ] **Step 1: create worktree from main**

```bash
cd /Users/harshilshah/Desktop/Active\ Inference/affect_aif
git fetch origin
git worktree add ../affect_aif-restructure-pr1 -b restructure/aif-skeleton origin/main
cd ../affect_aif-restructure-pr1
```

Expected: worktree created at `../affect_aif-restructure-pr1` on branch `restructure/aif-skeleton`.

- [ ] **Step 2: confirm CI baseline is green on the branch start point**

Run: `pytest tests/ -q`
Expected: all tests pass, exit 0. Record the SHA of `HEAD` for later baseline-capture reference: `git rev-parse HEAD > /tmp/pre_pr_sha.txt`.

- [ ] **Step 3: install runtime (verify environment)**

Run: `python -c "import numpy, jax, pytest; print(numpy.__version__, jax.__version__, pytest.__version__)"`
Expected: prints three version strings, no import errors.

---

## Phase 1: PR-1 — `aif/` skeleton (commit 1)

**Goal:** create `aif/` directory containing verbatim copies of `agent/inference/{maths,utils,backend,efe,runtime,policies,learning}.py`, with internal imports rewritten so the new modules form a self-contained package. Nothing in the existing codebase imports from `aif/` yet — it's dead code that proves the abstraction.

**Why dead code is OK here:** decision #8 forbids shims, but decision #10 splits the work into two PRs to keep PR-1 small and reviewable. PR-2 will wire the rest of the codebase to `aif/`.

### Task 1.1: create `aif/` directory and `__init__.py`

**Files:**
- Create: `aif/__init__.py`

- [ ] **Step 1: create empty package marker**

```bash
mkdir -p aif
touch aif/__init__.py
```

- [ ] **Step 2: verify `import aif` works**

Run: `python -c "import aif; print(aif)"`
Expected: prints `<module 'aif' from '.../aif/__init__.py'>`.

### Task 1.2: copy `maths.py` into `aif/`

**Files:**
- Create: `aif/maths.py` (verbatim copy of `agent/inference/maths.py`)
- Test: `tests/test_aif_skeleton.py`

- [ ] **Step 1: write the failing test**

Create `tests/test_aif_skeleton.py`:

```python
"""Skeleton-equivalence tests for PR-1.

These tests prove that aif/<module>.<symbol> returns identical values to
agent.inference.<module>.<symbol> on representative inputs. They exist solely
to gate the verbatim-move commits in PR-1; PR-2 may delete or replace them as
the agent.inference.* modules are removed.
"""
from __future__ import annotations

import numpy as np


def test_aif_softmax_matches_agent_softmax():
    import aif.maths as new
    from agent.inference import maths as old

    x = np.asarray([0.1, 0.5, -0.3, 1.2], dtype=float)
    np.testing.assert_array_equal(new.softmax(x, backend="numpy"), old.softmax(x, backend="numpy"))


def test_aif_log_stable_matches_agent():
    import aif.maths as new
    from agent.inference import maths as old

    x = np.asarray([1e-20, 0.5, 1.0], dtype=float)
    np.testing.assert_array_equal(new.log_stable(x, backend="numpy"), old.log_stable(x, backend="numpy"))
```

- [ ] **Step 2: run test, expect ImportError**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'aif.maths'`.

- [ ] **Step 3: copy file**

```bash
cp agent/inference/maths.py aif/maths.py
```

- [ ] **Step 4: rewrite internal imports inside `aif/maths.py`**

Open `aif/maths.py`. If any line imports `from agent.inference.X` or `from agent.X`, rewrite to `from aif.X` (the corresponding sibling will land in subsequent tasks). For commit 1, `aif/maths.py` should have no `from agent.*` imports at the end.

If `aif/maths.py` imports nothing from `agent/`, no changes needed. (Maths is leaf-level; expected to be standalone.)

- [ ] **Step 5: run test, expect PASS**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: PASS.

### Task 1.3: copy `utils.py`, `backend.py` into `aif/`

**Files:**
- Create: `aif/utils.py`, `aif/backend.py`
- Modify: `tests/test_aif_skeleton.py`

- [ ] **Step 1: extend the test file**

Append to `tests/test_aif_skeleton.py`:

```python
def test_aif_obj_array_matches_agent():
    import aif.utils as new
    from agent.inference import utils as old

    a = new.obj_array(3)
    b = old.obj_array(3)
    assert a.shape == b.shape == (3,)
    assert a.dtype == b.dtype == object


def test_aif_backend_resolve_matches_agent():
    import aif.backend as new
    from agent.inference import backend as old
    # backend.get_backend with default arg should return the same string both ways
    assert new.get_backend("numpy") == old.get_backend("numpy")
```

(If `agent/inference/backend.py` exposes a different public symbol, replace `get_backend` with whatever exists — check `agent/inference/backend.py` first.)

- [ ] **Step 2: run test, expect failures for the new functions**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: 2 new tests FAIL with ImportError.

- [ ] **Step 3: copy files**

```bash
cp agent/inference/utils.py aif/utils.py
cp agent/inference/backend.py aif/backend.py
```

- [ ] **Step 4: rewrite internal imports**

In `aif/utils.py` and `aif/backend.py`: any `from agent.inference.maths import X` → `from aif.maths import X`. Any `from agent.inference.utils` → `from aif.utils`. After this, no `from agent.*` imports should remain in `aif/utils.py` or `aif/backend.py`.

- [ ] **Step 5: run test, expect PASS**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: PASS.

### Task 1.4: copy `efe.py`, `policies.py`, `learning.py` into `aif/`

**Files:**
- Create: `aif/efe.py`, `aif/policies.py`, `aif/learning.py`
- Modify: `tests/test_aif_skeleton.py`

- [ ] **Step 1: extend test file**

Append to `tests/test_aif_skeleton.py`:

```python
def test_aif_construct_policies_matches_agent():
    import aif.policies as new
    from agent.inference import policies as old

    rng_a = np.random.default_rng(7)
    rng_b = np.random.default_rng(7)
    p_new = new.construct_policies([2, 2], planning_horizon=3, rng=rng_a)
    p_old = old.construct_policies([2, 2], planning_horizon=3, rng=rng_b)
    np.testing.assert_array_equal(p_new, p_old)


def test_aif_efe_matches_agent_simple_pomdp():
    import aif.efe as new
    from agent.inference import efe as old
    # 2-state, 1-modality, 1-step horizon, single policy
    A = [np.eye(2)]
    B = [np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)]
    C = [np.asarray([1.0, 0.0])]
    qs = [np.asarray([0.5, 0.5])]
    policy = np.asarray([[0]])
    g_new = new.compute_expected_free_energy(qs, A, B, C, policy, gamma=1.0,
                                             use_utility=True, use_information_gain=True)
    g_old = old.compute_expected_free_energy(qs, A, B, C, policy, gamma=1.0,
                                             use_utility=True, use_information_gain=True)
    np.testing.assert_allclose(g_new, g_old, atol=1e-12)


def test_aif_update_likelihood_dirichlet_matches_agent():
    import aif.learning as new
    from agent.inference import learning as old

    pA = [np.ones((2, 2)) * 1.0]
    qs = [np.asarray([0.7, 0.3])]
    obs = [0]
    pA_new = new.update_likelihood_dirichlet([pa.copy() for pa in pA], qs, obs, lr=1.0)
    pA_old = old.update_likelihood_dirichlet([pa.copy() for pa in pA], qs, obs, lr=1.0)
    np.testing.assert_allclose(pA_new[0], pA_old[0])
```

If actual function signatures differ (check `agent/inference/learning.py` and `agent/inference/efe.py`), replace inline. Goal: each test calls one symbol from `aif.X` and one from `agent.inference.X` and asserts equality.

- [ ] **Step 2: run test, expect failures**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: 3 new tests FAIL with ImportError.

- [ ] **Step 3: copy files**

```bash
cp agent/inference/efe.py aif/efe.py
cp agent/inference/policies.py aif/policies.py
cp agent/inference/learning.py aif/learning.py
```

- [ ] **Step 4: rewrite internal imports in each new file**

In each of `aif/efe.py`, `aif/policies.py`, `aif/learning.py`:
- `from agent.inference.maths import X` → `from aif.maths import X`
- `from agent.inference.utils import X` → `from aif.utils import X`
- `from agent.inference.backend import X` → `from aif.backend import X`
- any other `from agent.X` → leave for now if it's a circular reference; flag for the next task.

After: `grep -n 'from agent' aif/efe.py aif/policies.py aif/learning.py` should produce zero output.

- [ ] **Step 5: run test, expect PASS**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: PASS.

### Task 1.5: copy `runtime.py` into `aif/` and add the generic `generate_observation_sequences` helper

**Files:**
- Create: `aif/runtime.py` (verbatim copy of `agent/inference/runtime.py` plus one moved function)
- Modify: `tests/test_aif_skeleton.py`

- [ ] **Step 1: extend test**

Append to `tests/test_aif_skeleton.py`:

```python
def test_aif_runtime_resolve_device_matches_agent():
    import aif.runtime as new
    from agent.inference import runtime as old
    assert new.resolve_device("cpu") == old.resolve_device("cpu")


def test_aif_generate_observation_sequences_matches_agent():
    """generate_observation_sequences moves from agent/inference/rollout.py
    into aif/runtime.py because it is task-agnostic (only depends on horizon
    and number of obs per modality)."""
    import aif.runtime as new
    from agent.inference import rollout as old

    seqs_new = new.generate_observation_sequences(planning_horizon=3, num_obs_per_modality=[2, 3])
    seqs_old = old.generate_observation_sequences(planning_horizon=3, num_obs_per_modality=[2, 3])
    np.testing.assert_array_equal(seqs_new, seqs_old)
```

(If signature differs, check `agent/inference/rollout.py:generate_observation_sequences` first and adjust the call.)

- [ ] **Step 2: run, expect failure**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: 2 new tests FAIL.

- [ ] **Step 3: copy `runtime.py` and rewrite imports**

```bash
cp agent/inference/runtime.py aif/runtime.py
```

In `aif/runtime.py`: rewrite any `from agent.inference.X` → `from aif.X`. After: no `from agent.*` imports.

- [ ] **Step 4: copy `generate_observation_sequences` into `aif/runtime.py`**

Open `agent/inference/rollout.py`, find `def generate_observation_sequences(`, copy the entire function body, and append it to `aif/runtime.py`. Add any required imports at the top of `aif/runtime.py`.

Do NOT remove it from `agent/inference/rollout.py` yet — this is PR-1 (no deletions in `agent/`).

- [ ] **Step 5: run, expect PASS**

Run: `pytest tests/test_aif_skeleton.py -q`
Expected: PASS.

### Task 1.6: populate `aif/__init__.py` with public re-exports

**Files:**
- Modify: `aif/__init__.py`

- [ ] **Step 1: write final `__init__.py` content**

```python
"""Generic active-inference primitives. POMDP-style stateful Agent + free
inference/learning functions, mirroring andrew pescia's pymdp pattern.

Public surface (commit 2 will add Agent, infer_states, infer_policies):
    aif.maths     — softmax, log_stable, dirichlet_expected_value, ...
    aif.utils     — obj_array, onehot, normalize, ...
    aif.backend   — numpy/jax dispatch helpers
    aif.efe       — expected free energy computation
    aif.policies  — construct_policies, gamma_per_policy, sample_action
    aif.learning  — update_pA, update_pB, update_pD, update_pE,
                    update_likelihood_dirichlet, update_transition_dirichlet
    aif.runtime   — RuntimeConfig, resolve_device, runtime_context, as_jax,
                    to_numpy, generate_observation_sequences
"""
from aif.maths import softmax, log_stable
from aif.utils import obj_array
from aif.policies import construct_policies
```

(Keep this minimal in PR-1; commit 2 will add `Agent`, `infer_states`, `infer_policies`, `sample_action`, etc.)

- [ ] **Step 2: verify `import aif` resolves**

Run: `python -c "import aif; print(aif.softmax([1,2]))"`
Expected: prints a numpy array.

### Task 1.7: PR-1 verification + commit

- [ ] **Step 1: run the full skeleton test suite**

Run: `pytest tests/test_aif_skeleton.py -v`
Expected: all skeleton tests PASS.

- [ ] **Step 2: confirm zero `from agent.*` imports inside `aif/`**

Run: `grep -rn 'from agent' aif/ ; grep -rn 'import agent' aif/`
Expected: no output (zero hits).

- [ ] **Step 3: confirm full pre-existing test suite still passes**

Run: `pytest tests/ -q`
Expected: 0 failures, 0 errors. Same test count as on `main` plus the new skeleton tests.

- [ ] **Step 4: confirm zero new behavior on existing modules**

Run: `git diff --stat origin/main -- agent/`
Expected: empty diff under `agent/` (PR-1 only ADDS `aif/` and the test file; it does NOT modify `agent/`).

- [ ] **Step 5: stage and commit**

```bash
git add aif/ tests/test_aif_skeleton.py
git status
```

Expected: only `aif/*` and `tests/test_aif_skeleton.py` staged.

```bash
git commit -m "feat(aif): add aif/ skeleton with verbatim moves from agent/inference

Creates aif/ as a generic active-inference package. This commit only
ADDS code; agent/inference/ is untouched. The skeleton is dead code
on main — PR-2 will wire the codebase to import from aif/.

Modules added (verbatim copies, internal imports rewritten):
- aif/maths.py, aif/utils.py, aif/backend.py
- aif/efe.py, aif/policies.py, aif/learning.py
- aif/runtime.py (plus generate_observation_sequences moved from rollout.py)

Test file tests/test_aif_skeleton.py asserts numerical equivalence
between aif.<symbol> and agent.inference.<symbol>. Will be deleted
in PR-2 once agent.inference is removed.

Spec: docs/superpowers/specs/2026-04-18-aif-extraction-design.md
Decision #10 — two-PR split for reviewability."
```

- [ ] **Step 6: push and open PR-1**

```bash
git push -u origin restructure/aif-skeleton
gh pr create --title "restructure(PR-1): aif/ skeleton (verbatim moves, dead code)" \
  --body "$(cat <<'EOF'
## Summary

PR-1 of two for the `aif/` extraction. This PR only adds `aif/` as a self-contained package containing verbatim copies of `agent/inference/{maths,utils,backend,efe,runtime,policies,learning}.py` (with internal imports rewritten). Nothing in `agent/` is touched. `aif/` is dead code on `main` after this merges; PR-2 wires the codebase to it.

## Why two PRs

Per decision #10 of the design spec, the cutover is split into a small dead-code PR (this one) and a large cutover PR (PR-2). PR-1 is reviewable in <30 minutes and de-risks the abstraction by getting the new module shape on `main` before any cutover work begins.

## Test plan
- [x] `pytest tests/test_aif_skeleton.py -v` — all new equivalence tests pass
- [x] `pytest tests/` — full pre-existing suite still passes (no regressions)
- [x] `grep -rn 'from agent' aif/` — zero imports of `agent.*` inside `aif/`
- [x] `git diff --stat origin/main -- agent/` — empty (no changes outside `aif/` and `tests/test_aif_skeleton.py`)

## Spec
`docs/superpowers/specs/2026-04-18-aif-extraction-design.md`
EOF
)"
```

Expected: PR opened, URL printed.

---

## Phase 2: PR-2 commit 2 — `aif/agent.py`, `aif/inference.py`, `aif/affect/beta.py`

**Goal:** introduce the real new abstractions: the `Agent` dataclass, `infer_states` / `infer_policies` free functions, and the entity-renamed `DiscreteBetaState`. After this commit, `agent/affective.py` imports `DiscreteBetaState` from `aif.affect.beta` (not `agent/affect/beta.py`); behavior is unchanged because the rename is purely cosmetic (`partner` → `entity` at the public boundary).

**Branch:** create PR-2 worktree from `main` *after* PR-1 has merged. Do NOT branch off PR-1's branch.

### Task 2.0: setup PR-2 worktree

- [ ] **Step 1: confirm PR-1 has merged to main**

Run: `git fetch origin && git log origin/main --oneline -5`
Expected: top commit on `origin/main` is the squash of PR-1 (commit message starts with `restructure(PR-1)` or `feat(aif): add aif/ skeleton`).

- [ ] **Step 2: create PR-2 worktree**

```bash
cd /Users/harshilshah/Desktop/Active\ Inference/affect_aif
git worktree add ../affect_aif-restructure-pr2 -b restructure/aif-cutover origin/main
cd ../affect_aif-restructure-pr2
```

- [ ] **Step 3: confirm CI baseline green**

Run: `pytest tests/ -q`
Expected: 0 failures.

### Task 2.1: write tests for `aif.Agent` dataclass

**Files:**
- Test: `tests/test_aif_agent.py` (new)

- [ ] **Step 1: create the test file**

```python
"""Tests for aif.Agent stateful container (decision #3 of design spec)."""
from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def tiny_pomdp():
    """A 2-state, 2-obs, 2-action POMDP for quick agent tests."""
    A = np.empty(1, dtype=object)
    A[0] = np.asarray([[0.9, 0.1], [0.1, 0.9]], dtype=float)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0], dtype=float)
    D = np.empty(1, dtype=object)
    D[0] = np.asarray([0.5, 0.5], dtype=float)
    policies = np.asarray([[[0]], [[1]]], dtype=int)
    return dict(A=A, B=B, C=C, D=D, policies=policies)


def test_agent_dataclass_basic_construction(tiny_pomdp):
    import aif
    agent = aif.Agent(**tiny_pomdp)
    assert agent.qs is None
    assert agent.E is None
    assert agent.pA is None
    assert agent.gamma == 1.0
    assert agent.use_utility is True
    assert agent.use_information_gain is True
    assert agent.action_sampling == "marginal"


def test_agent_reset_initialises_qs_to_D(tiny_pomdp):
    import aif
    agent = aif.Agent(**tiny_pomdp)
    agent.reset()
    assert agent.qs is not None
    np.testing.assert_array_equal(agent.qs[0], tiny_pomdp["D"][0])


def test_agent_rng_default_seed_reproducible(tiny_pomdp):
    import aif
    a = aif.Agent(**tiny_pomdp)
    b = aif.Agent(**tiny_pomdp)
    assert a.rng.integers(0, 100) == b.rng.integers(0, 100)


def test_agent_optional_dirichlet_fields_default_to_none(tiny_pomdp):
    import aif
    agent = aif.Agent(**tiny_pomdp)
    for field in ("pA", "pB", "pD", "pE", "E", "qs"):
        assert getattr(agent, field) is None
```

- [ ] **Step 2: run, expect ImportError**

Run: `pytest tests/test_aif_agent.py -q`
Expected: FAIL with `AttributeError: module 'aif' has no attribute 'Agent'`.

### Task 2.2: implement `aif/agent.py`

**Files:**
- Create: `aif/agent.py`
- Modify: `aif/__init__.py`

- [ ] **Step 1: create `aif/agent.py`**

```python
"""Stateful container for a single-agent POMDP, pymdp-style.

The Agent has no `step()` method — the loop lives in the runner. All
operations on an Agent are free functions in aif (infer_states, infer_policies,
sample_action, update_pA/pB/pD/pE).

Decision #3 of the B+A design spec.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Agent:
    """POMDP container.

    Required fields:
        A         object-array of likelihoods, one per modality
        B         object-array of transitions, one per factor
        C         object-array of preferences, one per modality
        D         object-array of initial-state priors, one per factor
        policies  (num_policies, horizon) or (num_policies, horizon, num_factors)

    Optional state:
        qs        current posterior, one entry per factor; None until first
                  inference
        E         log-prior over policies
        pA, pB    Dirichlet hyperparams for A, B
        pD, pE    Dirichlet hyperparams for D, E
    """

    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray
    policies: np.ndarray
    qs: np.ndarray | None = None
    E: np.ndarray | None = None
    pA: np.ndarray | None = None
    pB: np.ndarray | None = None
    pD: np.ndarray | None = None
    pE: np.ndarray | None = None
    gamma: float = 1.0
    use_utility: bool = True
    use_information_gain: bool = True
    action_sampling: str = "marginal"
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(0))

    def reset(self) -> None:
        """Reset qs to the initial-state prior D (or expected value of pD if learning)."""
        num_factors = len(self.D)
        qs = np.empty(num_factors, dtype=object)
        for f in range(num_factors):
            qs[f] = np.asarray(self.D[f], dtype=float).copy()
        self.qs = qs
```

- [ ] **Step 2: re-export from `aif/__init__.py`**

Edit `aif/__init__.py`, append:

```python
from aif.agent import Agent
```

- [ ] **Step 3: run tests, expect PASS**

Run: `pytest tests/test_aif_agent.py -v`
Expected: 4 tests PASS.

### Task 2.3: write tests for `aif.infer_states` (1-step Bayes)

**Files:**
- Test: `tests/test_aif_inference.py` (new)

- [ ] **Step 1: create test file**

```python
"""Tests for aif.infer_states (1-step Bayesian belief update).

Per design-spec section 2: this is a 1-step posterior update, not a
fixed-point or MMP scheme. It writes back to agent.qs and returns the
new posterior.
"""
from __future__ import annotations

import numpy as np


def _build_simple_agent():
    """2-state, 1-modality, 2-obs, 2-action toy POMDP."""
    import aif

    A = np.empty(1, dtype=object)
    A[0] = np.asarray([[0.8, 0.2], [0.2, 0.8]], dtype=float)  # P(o|s)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0], dtype=float)
    D = np.empty(1, dtype=object)
    D[0] = np.asarray([0.5, 0.5], dtype=float)
    policies = np.asarray([[[0]], [[1]]], dtype=int)
    return aif.Agent(A=A, B=B, C=C, D=D, policies=policies)


def test_infer_states_no_action_uses_D_as_prior():
    """With qs=None and action=None, prior is D, posterior ∝ D · L(o)."""
    import aif
    agent = _build_simple_agent()

    qs = aif.infer_states(agent, obs=[0])

    # Manual: prior = [0.5, 0.5], L = A[0][0] = [0.8, 0.2]
    # posterior ∝ [0.4, 0.1] → normalized [0.8, 0.2]
    np.testing.assert_allclose(qs[0], [0.8, 0.2], atol=1e-12)
    np.testing.assert_allclose(agent.qs[0], [0.8, 0.2], atol=1e-12)


def test_infer_states_uses_existing_qs_when_no_action():
    import aif
    agent = _build_simple_agent()
    agent.qs = np.empty(1, dtype=object)
    agent.qs[0] = np.asarray([0.9, 0.1])

    qs = aif.infer_states(agent, obs=[0])

    # prior = [0.9, 0.1], L = [0.8, 0.2]; posterior ∝ [0.72, 0.02] → [0.973, 0.027]
    np.testing.assert_allclose(qs[0], [0.72 / 0.74, 0.02 / 0.74], atol=1e-12)


def test_infer_states_predicts_through_B_when_action_provided():
    """With action=[1] (B[0][:,:,1] is anti-identity), prior is rotated."""
    import aif
    agent = _build_simple_agent()
    agent.qs = np.empty(1, dtype=object)
    agent.qs[0] = np.asarray([0.9, 0.1])

    qs = aif.infer_states(agent, obs=[0], action=[1])

    # predicted prior = B[0][:,:,1] @ [0.9, 0.1] = [0.1, 0.9]
    # L = A[0][0] = [0.8, 0.2]; posterior ∝ [0.08, 0.18] → [0.308, 0.692]
    np.testing.assert_allclose(qs[0], [0.08 / 0.26, 0.18 / 0.26], atol=1e-12)


def test_infer_policies_returns_q_pi_and_G_with_correct_shapes():
    import aif
    agent = _build_simple_agent()
    agent.reset()

    q_pi, G = aif.infer_policies(agent)

    assert q_pi.shape == (2,)  # 2 policies
    assert G.shape == (2,)
    np.testing.assert_allclose(q_pi.sum(), 1.0, atol=1e-12)
    assert np.all(np.isfinite(G))
```

- [ ] **Step 2: run, expect ImportError**

Run: `pytest tests/test_aif_inference.py -q`
Expected: FAIL — `infer_states` doesn't exist yet.

### Task 2.4: implement `aif/inference.py`

**Files:**
- Create: `aif/inference.py`
- Modify: `aif/__init__.py`

- [ ] **Step 1: create `aif/inference.py`**

```python
"""Free functions that operate on aif.Agent.

Decision #3: no methods on Agent beyond `reset()`. All inference and
learning happen through these free functions.
"""
from __future__ import annotations

import numpy as np

from aif.agent import Agent
from aif.efe import compute_efe_all_policies
from aif.maths import log_stable, softmax


def infer_states(agent: Agent, obs: list[int], action: list[int] | None = None) -> np.ndarray:
    """Single-step Bayesian belief update over hidden-state factors.

    Computes qs[f] ∝ prior[f] · P(o | s_f) factorized across modalities,
    where prior[f] is either:
      - B[f][:, :, action[f]] @ agent.qs[f]  (if action is provided)
      - agent.qs[f]                           (if qs is set, no action)
      - D[f]                                  (otherwise)

    Writes back to agent.qs and returns the new posterior obj-array.

    NOTE: This is a 1-step update, not a fixed-point or MMP scheme. See the
    follow-up tasks appendix in the design spec for optional MMP extension.
    """
    num_factors = len(agent.D)
    num_modalities = len(agent.A)

    # construct prior
    prior = np.empty(num_factors, dtype=object)
    for f in range(num_factors):
        if action is not None:
            qs_prev = agent.qs[f] if agent.qs is not None else np.asarray(agent.D[f], dtype=float)
            B_f = np.asarray(agent.B[f], dtype=float)
            prior[f] = B_f[:, :, int(action[f])] @ qs_prev
        elif agent.qs is not None:
            prior[f] = np.asarray(agent.qs[f], dtype=float).copy()
        else:
            prior[f] = np.asarray(agent.D[f], dtype=float).copy()

    # likelihood: for each factor, sum-out other factors of A[m]
    # for the simple 1-factor case this collapses to A[m][o[m], :]
    log_post = np.empty(num_factors, dtype=object)
    for f in range(num_factors):
        log_post[f] = log_stable(prior[f], backend="numpy")
        for m in range(num_modalities):
            A_m = np.asarray(agent.A[m], dtype=float)
            # A_m shape: (num_obs[m], num_states_factor_0, ..., num_states_factor_F-1)
            # for 1-factor case: (num_obs[m], num_states[0])
            # marginalize over other factors using current qs (or prior)
            if A_m.ndim == 2:
                # 1-factor likelihood
                log_post[f] = log_post[f] + log_stable(A_m[int(obs[m])], backend="numpy")
            else:
                # multi-factor: sum-out other factors
                slice_axes = tuple(g + 1 for g in range(num_factors) if g != f)
                # weight by qs of the other factors
                L = A_m[int(obs[m])]  # shape (num_states_f0, ..., num_states_F-1)
                for g_axis, g in enumerate(range(num_factors)):
                    if g == f:
                        continue
                    weight = prior[g]
                    L = (L * weight.reshape([-1 if dim == g_axis else 1
                                             for dim in range(L.ndim)])).sum(axis=0 if g_axis < f else g_axis)
                log_post[f] = log_post[f] + log_stable(L, backend="numpy")

    qs = np.empty(num_factors, dtype=object)
    for f in range(num_factors):
        qs[f] = softmax(log_post[f], backend="numpy")
    agent.qs = qs
    return qs


def infer_policies(agent: Agent) -> tuple[np.ndarray, np.ndarray]:
    """Compute posterior over policies and per-policy expected free energy.

    Returns (q_pi, G) where:
      G shape:    (num_policies,) — expected free energy
      q_pi shape: (num_policies,) — softmax(-gamma * G + (E or 0))
    """
    if agent.qs is None:
        agent.reset()
    G = compute_efe_all_policies(
        qs=agent.qs,
        A=agent.A,
        B=agent.B,
        C=agent.C,
        policies=agent.policies,
        gamma=agent.gamma,
        use_utility=agent.use_utility,
        use_information_gain=agent.use_information_gain,
    )
    log_q_pi = -agent.gamma * G
    if agent.E is not None:
        log_q_pi = log_q_pi + agent.E
    q_pi = softmax(log_q_pi, backend="numpy")
    return q_pi, G
```

NOTE: The multi-factor marginalization in `infer_states` is intricate. If `agent/inference/` has an existing implementation that handles this (look in `agent/base.py:infer_*` or `agent/inference/utils.py`), prefer porting that logic verbatim and adapting the signature. The 1-factor case (which is what the trust game uses for each per-partner agent's `(s_type, s_stance)` joint factor) is the critical path — get that right first.

- [ ] **Step 2: re-export**

Append to `aif/__init__.py`:

```python
from aif.inference import infer_states, infer_policies
```

- [ ] **Step 3: run tests, expect PASS**

Run: `pytest tests/test_aif_inference.py -v`
Expected: 4 tests PASS. If multi-factor marginalization fails on a real trust-game POMDP, debug by porting the existing `_BaseTrustGameModel.infer_joint_posterior` math (without the bug — see Phase 3) into `aif.infer_states`.

- [ ] **Step 4: cross-check on the real trust-game model**

Add this test to `tests/test_aif_inference.py`:

```python
def test_infer_states_on_trust_game_joint_factor():
    """Sanity: aif.infer_states reproduces the joint type-stance posterior
    that BaseAgent.infer_joint_posterior produces today (excluding the
    payoff-drop bug, which we test in Phase 3)."""
    import aif
    from agent.model.trust_game import TrustGameModel  # will be deleted later
    model = TrustGameModel({"num_partners": 2, "observation_noise": 0.0})

    # reshape model.A[0] to 1-modality, 1-factor view: (num_partner_action, num_types*num_stances)
    num_types, num_stances = model.num_types, model.num_stances
    A = np.empty(1, dtype=object)
    A[0] = model.A[0].reshape(2, num_types * num_stances)
    B = np.empty(1, dtype=object)
    B[0] = np.stack([np.eye(num_types * num_stances)] * 2, axis=-1)
    C = np.empty(1, dtype=object)
    C[0] = np.asarray([1.0, 0.0])
    D = np.empty(1, dtype=object)
    D[0] = np.full(num_types * num_stances, 1.0 / (num_types * num_stances))
    agent = aif.Agent(A=A, B=B, C=C, D=D, policies=np.asarray([[[0]]], dtype=int))

    qs = aif.infer_states(agent, obs=[0])
    # Compare to model.infer_joint_posterior with same prior + observation
    prior = D[0].reshape(num_types, num_stances)
    posterior_old = model.infer_joint_posterior(prior, observation=[0, 0], own_action=0)
    np.testing.assert_allclose(qs[0].reshape(num_types, num_stances), posterior_old, atol=1e-10)
```

NOTE: This test compares the NEW `aif.infer_states` against the OLD `model.infer_joint_posterior` (which has the bug). With the bug, both treat the payoff modality as missing. After Phase 3 lands the bug fix, this test will need to be updated (or marked `xfail`) — that's flagged in Task 5.x.

Run: `pytest tests/test_aif_inference.py::test_infer_states_on_trust_game_joint_factor -v`
Expected: PASS.

### Task 2.5: write tests for `aif.policies.sample_action` (new signature)

**Files:**
- Test: `tests/test_aif_policies.py` (new)

- [ ] **Step 1: create test file**

```python
"""Tests for aif.policies.sample_action with new (agent, q_pi) signature."""
from __future__ import annotations

import numpy as np


def _build_agent_with_two_policies(action_sampling="marginal"):
    import aif
    A = np.empty(1, dtype=object); A[0] = np.eye(2)
    B = np.empty(1, dtype=object); B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object); C[0] = np.asarray([1.0, 0.0])
    D = np.empty(1, dtype=object); D[0] = np.asarray([0.5, 0.5])
    policies = np.asarray([[[0]], [[1]]], dtype=int)
    return aif.Agent(A=A, B=B, C=C, D=D, policies=policies, action_sampling=action_sampling,
                     rng=np.random.default_rng(42))


def test_sample_action_marginal_returns_int():
    import aif
    agent = _build_agent_with_two_policies("marginal")
    q_pi = np.asarray([0.99, 0.01])
    action = aif.sample_action(agent, q_pi)
    assert action == 0  # almost-deterministic on the first policy's action


def test_sample_action_uses_agent_rng_for_reproducibility():
    import aif
    a1 = _build_agent_with_two_policies("marginal")
    a2 = _build_agent_with_two_policies("marginal")
    q_pi = np.asarray([0.5, 0.5])
    seq1 = [aif.sample_action(a1, q_pi) for _ in range(20)]
    seq2 = [aif.sample_action(a2, q_pi) for _ in range(20)]
    assert seq1 == seq2


def test_sample_action_full_mode_returns_int():
    import aif
    agent = _build_agent_with_two_policies("full")
    q_pi = np.asarray([0.99, 0.01])
    action = aif.sample_action(agent, q_pi)
    assert isinstance(int(action), int)
```

- [ ] **Step 2: run, expect failure**

Run: `pytest tests/test_aif_policies.py -q`
Expected: FAIL — `aif.sample_action` not yet exported with the new signature.

### Task 2.6: implement new `sample_action` signature in `aif/policies.py`

**Files:**
- Modify: `aif/policies.py`
- Modify: `aif/__init__.py`

- [ ] **Step 1: rename old `sample_action` to `_sample_action_legacy`**

Open `aif/policies.py`. The existing `sample_action` (copied from `agent/inference/policies.py`) takes `(q_pi, policies, sampling_mode, rng)`. Rename it in-place to `_sample_action_impl`.

- [ ] **Step 2: add the agent-aware wrapper**

Append to `aif/policies.py`:

```python
def sample_action(agent, q_pi):
    """Sample an action using agent.action_sampling and agent.rng.

    Wraps the underlying sampler so callers don't pass policies/rng/mode
    repeatedly. Agent-aware variant per design-spec section 2.
    """
    return _sample_action_impl(
        q_pi=q_pi,
        policies=agent.policies,
        sampling_mode=agent.action_sampling,
        rng=agent.rng,
    )
```

- [ ] **Step 3: re-export from `aif/__init__.py`**

Append to `aif/__init__.py`:

```python
from aif.policies import sample_action
```

- [ ] **Step 4: run tests, expect PASS**

Run: `pytest tests/test_aif_policies.py -v`
Expected: 3 tests PASS.

### Task 2.7: write tests for Agent-aware learning wrappers

**Files:**
- Test: `tests/test_aif_learning.py` (new)

- [ ] **Step 1: create test file**

```python
"""Tests for aif.learning.update_pA/pB/pD/pE — Agent-aware wrappers."""
from __future__ import annotations

import numpy as np


def _build_agent_with_pA():
    import aif
    A = np.empty(1, dtype=object); A[0] = np.asarray([[0.8, 0.2], [0.2, 0.8]])
    B = np.empty(1, dtype=object); B[0] = np.stack([np.eye(2), np.eye(2)[::-1]], axis=-1)
    C = np.empty(1, dtype=object); C[0] = np.asarray([1.0, 0.0])
    D = np.empty(1, dtype=object); D[0] = np.asarray([0.5, 0.5])
    pA = np.empty(1, dtype=object); pA[0] = np.ones((2, 2))
    policies = np.asarray([[[0]]], dtype=int)
    return aif.Agent(A=A, B=B, C=C, D=D, pA=pA, policies=policies)


def test_update_pA_in_place_mutates_agent_pA():
    import aif
    agent = _build_agent_with_pA()
    agent.reset()
    pA_before = agent.pA[0].copy()
    aif.update_pA(agent, obs=[0], learning_rate=1.0)
    assert not np.allclose(agent.pA[0], pA_before)


def test_update_pA_does_not_touch_pB(monkeypatch):
    import aif
    agent = _build_agent_with_pA()
    agent.pB = np.empty(1, dtype=object); agent.pB[0] = np.ones((2, 2, 2))
    agent.reset()
    pB_before = agent.pB[0].copy()
    aif.update_pA(agent, obs=[0])
    np.testing.assert_array_equal(agent.pB[0], pB_before)
```

- [ ] **Step 2: run, expect failure**

Run: `pytest tests/test_aif_learning.py -q`
Expected: FAIL — `aif.update_pA` doesn't exist.

### Task 2.8: implement Agent-aware learning wrappers

**Files:**
- Modify: `aif/learning.py`
- Modify: `aif/__init__.py`

- [ ] **Step 1: append wrappers to `aif/learning.py`**

```python
def update_pA(agent, obs, learning_rate: float = 1.0) -> None:
    """In-place update of agent.pA from current agent.qs and obs.

    Agent-aware wrapper around update_likelihood_dirichlet.
    """
    if agent.pA is None:
        raise ValueError("update_pA called on Agent with pA=None (no Dirichlet prior set)")
    if agent.qs is None:
        raise ValueError("update_pA called before any inference; agent.qs is None")
    new_pA = update_likelihood_dirichlet(
        pA=[pa.copy() for pa in agent.pA],
        qs=agent.qs,
        obs=obs,
        lr=learning_rate,
    )
    for m in range(len(agent.pA)):
        agent.pA[m] = new_pA[m]


def update_pB(agent, qs_previous, action) -> None:
    """In-place update of agent.pB from qs_previous → agent.qs over action."""
    if agent.pB is None:
        raise ValueError("update_pB called on Agent with pB=None")
    if agent.qs is None:
        raise ValueError("update_pB called before any inference")
    new_pB = update_transition_dirichlet(
        pB=[pb.copy() for pb in agent.pB],
        qs=agent.qs,
        qs_previous=qs_previous,
        action=action,
    )
    for f in range(len(agent.pB)):
        agent.pB[f] = new_pB[f]


def update_pD(agent, learning_rate: float = 1.0) -> None:
    """Accumulate current qs into pD."""
    if agent.pD is None:
        raise ValueError("update_pD called on Agent with pD=None")
    for f in range(len(agent.pD)):
        agent.pD[f] = agent.pD[f] + learning_rate * np.asarray(agent.qs[f])


def update_pE(agent, q_pi, learning_rate: float = 0.5) -> None:
    """Accumulate q_pi into pE."""
    if agent.pE is None:
        raise ValueError("update_pE called on Agent with pE=None")
    agent.pE[:] = agent.pE + learning_rate * np.asarray(q_pi)
```

- [ ] **Step 2: re-export from `__init__.py`**

Append to `aif/__init__.py`:

```python
from aif.learning import update_pA, update_pB, update_pD, update_pE
```

- [ ] **Step 3: run tests, expect PASS**

Run: `pytest tests/test_aif_learning.py -v`
Expected: PASS.

### Task 2.9: write tests for `aif.affect.beta.DiscreteBetaState` (entity rename)

**Files:**
- Test: `tests/test_aif_affect_beta.py` (new)

- [ ] **Step 1: create test file**

```python
"""Tests for aif.affect.beta.DiscreteBetaState (entity-renamed from partner).

Decision #7: API rename `partner` → `entity` at the public boundary.
Numerics MUST be identical to agent.affect.beta.DiscreteBetaState on a
recorded sequence.
"""
from __future__ import annotations

import numpy as np


def test_entity_renamed_construction():
    from aif.affect.beta import DiscreteBetaState
    s = DiscreteBetaState(num_entities=3, num_levels=5, persistence=0.8,
                          alpha_charge=3.0, sigma_0_sq=0.25, initial_beta=1.0)
    assert s.num_entities == 3
    assert s.get_all_betas().shape == (3,)


def test_update_uses_entity_idx_kwarg():
    from aif.affect.beta import DiscreteBetaState
    s = DiscreteBetaState(num_entities=2, num_levels=5, persistence=0.8,
                          alpha_charge=3.0, sigma_0_sq=0.25, initial_beta=1.0)
    s.update(entity_idx=0, predicted_action_probs=np.asarray([0.7, 0.3]), observed_action=1)
    betas = s.get_all_betas()
    # Entity 0 should have updated; entity 1 should still be initial_beta
    assert betas[0] != 1.0
    assert betas[1] == 1.0


def test_aif_beta_numerically_matches_agent_beta_on_sequence():
    """Run a 10-step sequence through both implementations and assert per-step
    beta arrays are identical."""
    from aif.affect.beta import DiscreteBetaState as NewBeta
    from agent.affect.beta import DiscreteBetaState as OldBeta

    rng = np.random.default_rng(42)
    new_state = NewBeta(num_entities=3, num_levels=5, persistence=0.8,
                        alpha_charge=3.0, sigma_0_sq=0.25, initial_beta=1.0)
    old_state = OldBeta(num_partners=3, num_levels=5, persistence=0.8,
                        alpha_charge=3.0, sigma_0_sq=0.25, initial_beta=1.0)

    for t in range(10):
        eidx = int(rng.integers(0, 3))
        probs = np.asarray([rng.random(), 0.0])
        probs[1] = 1.0 - probs[0]
        obs_action = int(rng.integers(0, 2))
        new_state.update(entity_idx=eidx, predicted_action_probs=probs, observed_action=obs_action)
        old_state.update(partner_idx=eidx, predicted_action_probs=probs, observed_action=obs_action)
        np.testing.assert_array_equal(new_state.get_all_betas(), old_state.get_all_betas())
```

- [ ] **Step 2: run, expect failure**

Run: `pytest tests/test_aif_affect_beta.py -q`
Expected: FAIL — `aif.affect.beta` doesn't exist.

### Task 2.10: implement `aif/affect/beta.py`

**Files:**
- Create: `aif/affect/__init__.py`, `aif/affect/beta.py`

- [ ] **Step 1: create the affect subpackage**

```bash
mkdir -p aif/affect
touch aif/affect/__init__.py
cp agent/affect/beta.py aif/affect/beta.py
```

- [ ] **Step 2: rename `partner` → `entity` at the public boundary in `aif/affect/beta.py`**

Open `aif/affect/beta.py`. Apply these edits:

| current | new |
|---|---|
| `__init__(self, num_partners=...)` | `__init__(self, num_entities=...)` |
| `self.num_partners` | `self.num_entities` |
| `def update(self, partner_idx, ...)` | `def update(self, entity_idx, ...)` |
| `def get_beta(self, partner_idx)` | `def get_beta(self, entity_idx)` |
| `def get_prediction_error(self, partner_idx)` | `def get_prediction_error(self, entity_idx)` |
| internal `partner_idx` variables | rename to `entity_idx` for consistency |

`get_all_betas()` and `get_prediction_errors()` are already factor-neutral; leave names alone.

Update internal imports if needed (`from agent.X` → `from aif.X`).

- [ ] **Step 3: run tests, expect PASS**

Run: `pytest tests/test_aif_affect_beta.py -v`
Expected: 3 tests PASS.

### Task 2.11: re-point `agent/affective.py` to import from `aif.affect.beta`

**Files:**
- Modify: `agent/affective.py`
- Delete: `agent/affect/beta.py`, `agent/affect/interoception.py`, `agent/affect/__init__.py`

- [ ] **Step 1: update `agent/affective.py`**

Open `agent/affective.py`. Find:

```python
from agent.affect.beta import DiscreteBetaState
```

Replace with:

```python
from aif.affect.beta import DiscreteBetaState
```

Then within `AffectiveAgent.__init__`, find the `DiscreteBetaState(num_partners=..., ...)` call and rename `num_partners=` to `num_entities=`.

Then within any method that calls `self.affect.update(partner_idx=..., ...)`, rename to `entity_idx=`.

Same for `get_beta(partner_idx=...)` → `get_beta(entity_idx=...)` if used.

- [ ] **Step 2: delete `agent/affect/`**

```bash
git rm agent/affect/beta.py agent/affect/interoception.py agent/affect/__init__.py
```

(Per decision #7: `interoception.py` is a YAGNI 10-line stub.)

- [ ] **Step 3: confirm full test suite still passes**

Run: `pytest tests/ -q`
Expected: PASS, except `tests/test_interoception.py` should now FAIL (its target file is gone) and the existing `tests/test_discrete_beta.py` may FAIL (still uses `partner_idx=` against old API — but actually it imports from `agent.affect.beta` which is deleted, so it will fail with ImportError).

- [ ] **Step 4: defer test fixes to Phase 4**

Bucket-b test updates (including `tests/test_discrete_beta.py` and deletion of `tests/test_interoception.py`) happen in Phase 4 commit 4. For now, those failures are expected. Mark:

```bash
pytest tests/ -q --ignore=tests/test_interoception.py --ignore=tests/test_discrete_beta.py
```

Expected: 0 failures with the two excluded files.

### Task 2.12: andrew's notebook parity test

**Files:**
- Test: `tests/test_aif_apashea_parity.py` (new)

- [ ] **Step 1: read `notebooks/04_apashea_trust_spec.ipynb` to find andrew's setup**

Use jupyter to extract the first ~5 cells of inference setup from the notebook:

```bash
python -c "
import json
nb = json.load(open('notebooks/04_apashea_trust_spec.ipynb'))
for i, cell in enumerate(nb['cells'][:8]):
    print(f'--- cell {i} ({cell[\"cell_type\"]}) ---')
    print(''.join(cell['source']))
"
```

Read the output. Identify the A/B/C/D matrix construction and the first observation Andrew passes to `pymdp.Agent`.

- [ ] **Step 2: write the parity test**

Create `tests/test_aif_apashea_parity.py`:

```python
"""Acceptance: aif.Agent reproduces pymdp.Agent's posterior on andrew's
notebook setup to atol=1e-3 (loose because we use 1-step Bayes vs pymdp's
MMP — see follow-up tasks)."""
from __future__ import annotations

import numpy as np
import pytest


pymdp = pytest.importorskip("pymdp")


def test_aif_matches_pymdp_first_5_steps():
    """Reproduce the first 5 timesteps of the apashea notebook with aif.Agent
    and compare to pymdp.Agent's qs at each step."""
    import aif
    from pymdp import Agent as PymdpAgent

    # ===== reproduce andrew's A/B/C/D from the notebook =====
    # FILL IN from notebook cell inspection in Step 1.
    # Example skeleton (real values from notebook):
    A_pymdp = ...
    B_pymdp = ...
    C_pymdp = ...
    D_pymdp = ...

    pymdp_agent = PymdpAgent(A=A_pymdp, B=B_pymdp, C=C_pymdp, D=D_pymdp)

    # mirror the same structure as aif.Agent inputs
    A = np.asarray(A_pymdp, dtype=object)
    B = np.asarray(B_pymdp, dtype=object)
    C = np.asarray(C_pymdp, dtype=object)
    D = np.asarray(D_pymdp, dtype=object)
    policies = pymdp_agent.policies  # use same enumeration
    aif_agent = aif.Agent(A=A, B=B, C=C, D=D, policies=policies)
    aif_agent.reset()

    # ===== run 5 steps and compare =====
    obs_sequence = [...]  # also from the notebook
    for t, obs in enumerate(obs_sequence[:5]):
        pymdp_agent.infer_states(obs)
        aif.infer_states(aif_agent, obs)
        for f in range(len(D)):
            np.testing.assert_allclose(aif_agent.qs[f], pymdp_agent.qs[f], atol=1e-3,
                                       err_msg=f"mismatch at step {t}, factor {f}")
```

NOTE: This test is intentionally open-ended in this plan — Step 1's notebook inspection determines the exact A/B/C/D values. If `pymdp` is not installed in the dev environment, the `importorskip` line skips the test. CI must have `pymdp` installed for this test to run.

- [ ] **Step 3: install pymdp if needed**

Run: `pip install inferactively-pymdp` (the package name; double-check via `pip search` if needed).
Expected: install succeeds.

- [ ] **Step 4: run the test, debug as needed**

Run: `pytest tests/test_aif_apashea_parity.py -v`
Expected: PASS at `atol=1e-3`. If it fails, the most likely cause is single-step vs multi-step inference — pymdp's `Agent` uses MMP by default (`inference_horizon > 1`). Configure pymdp explicitly: `PymdpAgent(A=A, B=B, C=C, D=D, inference_algo="VANILLA", inference_horizon=1)` to use single-step inference and re-test.

### Task 2.13: commit 2

- [ ] **Step 1: confirm tests green**

Run: `pytest tests/ -q --ignore=tests/test_interoception.py --ignore=tests/test_discrete_beta.py`
Expected: 0 failures.

- [ ] **Step 2: stage and commit**

```bash
git add aif/agent.py aif/inference.py aif/affect/ aif/policies.py aif/learning.py aif/__init__.py \
        tests/test_aif_agent.py tests/test_aif_inference.py tests/test_aif_policies.py \
        tests/test_aif_learning.py tests/test_aif_affect_beta.py tests/test_aif_apashea_parity.py \
        agent/affective.py
git rm agent/affect/beta.py agent/affect/interoception.py agent/affect/__init__.py
git commit -m "feat(aif): add Agent dataclass, inference free fns, affect/beta with entity rename

- aif.Agent: stateful POMDP container, no step() method (decision #3)
- aif.infer_states: 1-step Bayes update over factored hidden states
- aif.infer_policies: q_pi + G via aif.efe
- aif.sample_action(agent, q_pi): agent-aware wrapper
- aif.update_pA/pB/pD/pE: agent-aware Dirichlet learning wrappers
- aif.affect.beta.DiscreteBetaState: moved from agent/affect/, with
  partner→entity rename at the public boundary (decision #7)

agent/affect/{beta,interoception,__init__}.py deleted.
agent/affective.py rewired to import from aif.affect.beta.
agent/affective.py uses entity_idx= kwarg.

Spec: docs/superpowers/specs/2026-04-18-aif-extraction-design.md"
```

---

## Phase 3: PR-2 commit 3 — `trust/` model layer + canonical `TrustGameModel`

**Goal:** create `trust/` package containing the canonical `TrustGameModel` (decisions #5, #6) plus the verbatim moves from `agent/model/`. Delete `agent/model/`. Update `experiment/factory.py` to use the new model. Add `payoff_mode` keys to 22 binary configs. Update the 2 model-class tests to use the new API.

### Task 3.1: create `trust/` skeleton with verbatim moves

**Files:**
- Create: `trust/__init__.py`, `trust/types.py`, `trust/stance.py`, `trust/payoffs.py`

- [ ] **Step 1: create directory and verbatim copies**

```bash
mkdir -p trust
touch trust/__init__.py
cp agent/model/types.py trust/types.py
cp agent/model/stance.py trust/stance.py
cp agent/model/payoffs.py trust/payoffs.py
```

- [ ] **Step 2: rewrite imports in `trust/{types,stance,payoffs}.py`**

In each file:
- `from agent.inference.maths import X` → `from aif.maths import X`
- `from agent.inference.utils import X` → `from aif.utils import X`
- `from agent.model.<sibling> import X` → `from trust.<sibling> import X`

Run: `grep -rn 'from agent' trust/`
Expected: no output.

- [ ] **Step 3: smoke import**

Run: `python -c "import trust.types, trust.stance, trust.payoffs; print('ok')"`
Expected: prints `ok`.

### Task 3.2: write tests for canonical `TrustGameModel` constructor

**Files:**
- Test: `tests/test_trust_model_canonical.py` (new)

- [ ] **Step 1: create test file**

```python
"""Tests for the canonical trust.model.TrustGameModel (decisions #5, #6)."""
from __future__ import annotations

import numpy as np
import pytest


def test_payoff_mode_required():
    from trust.model import TrustGameModel
    with pytest.raises(ValueError, match="payoff_mode"):
        TrustGameModel({"num_partners": 2})


def test_payoff_mode_binary_constructs():
    from trust.model import TrustGameModel
    m = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    assert m.payoff_mode == "binary"
    assert m.num_social_actions == 2


def test_payoff_mode_graded_constructs():
    from trust.model import TrustGameModel
    m = TrustGameModel({"payoff_mode": "graded", "num_partners": 2,
                        "num_investment_levels": 6, "endowment": 10.0, "multiplier": 3.0})
    assert m.payoff_mode == "graded"
    assert m.num_social_actions == 6


def test_unknown_payoff_mode_raises():
    from trust.model import TrustGameModel
    with pytest.raises(ValueError, match="unknown payoff_mode"):
        TrustGameModel({"payoff_mode": "rocket-fuel", "num_partners": 2})


def test_variant_key_raises():
    from trust.model import TrustGameModel
    with pytest.raises(ValueError, match="'variant' was removed"):
        TrustGameModel({"payoff_mode": "binary", "variant": "agent_choice"})


def test_model_class_key_raises():
    from trust.model import TrustGameModel
    with pytest.raises(ValueError, match="'model_class' was removed"):
        TrustGameModel({"payoff_mode": "binary", "model_class": "TrustGameModel"})


def test_binary_with_graded_keys_raises():
    from trust.model import TrustGameModel
    with pytest.raises(ValueError, match="graded-only keys"):
        TrustGameModel({"payoff_mode": "binary", "num_investment_levels": 6})


def test_graded_with_binary_keys_raises():
    from trust.model import TrustGameModel
    with pytest.raises(ValueError, match="binary-only keys"):
        TrustGameModel({"payoff_mode": "graded", "num_investment_levels": 6,
                        "mutual_coop": (3.0, 3.0)})


def test_build_A_returns_fresh_copy_each_call():
    """Decision: build_A/build_B are non-caching; each call returns a fresh
    allocation. TrustGameAgent relies on this for per-partner copies."""
    from trust.model import TrustGameModel
    m = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    a1 = m.build_A()
    a2 = m.build_A()
    a1[0][0, 0, 0] = 999.0
    assert a2[0][0, 0, 0] != 999.0


def test_build_B_returns_fresh_copy_each_call():
    from trust.model import TrustGameModel
    m = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    b1 = m.build_B()
    b2 = m.build_B()
    b1[0][0, 0, 0] = 999.0
    assert b2[0][0, 0, 0] != 999.0
```

- [ ] **Step 2: run, expect failure**

Run: `pytest tests/test_trust_model_canonical.py -q`
Expected: FAIL (no `trust.model` yet).

### Task 3.3: write tests for the `infer_joint_posterior` bug fix

**Files:**
- Test: `tests/test_payoff_modality_in_likelihood.py` (new)

- [ ] **Step 1: create test file**

```python
"""Decision #6: o_payoff modality must contribute to the joint posterior.
Pre-fix code dropped it; new code multiplies through both modalities."""
from __future__ import annotations

import numpy as np
import pytest


def test_payoff_modality_contributes_to_posterior():
    from trust.model import TrustGameModel
    model = TrustGameModel({
        "payoff_mode": "binary",
        "observation_noise": 0.5,             # makes o_partner_action uninformative
        "mutual_coop":   (10.0, 10.0),
        "sucker":        (-10.0, 10.0),
        "temptation":    (10.0, -10.0),
        "mutual_defect": (-10.0, -10.0),
    })
    prior_flat = np.full((model.num_types, model.num_stances),
                         1.0 / (model.num_types * model.num_stances))
    posterior = model.infer_joint_posterior(prior_flat, observation=[0, 1], own_action=0)
    # Posterior MUST diverge from prior because payoff modality is informative.
    assert not np.allclose(posterior, prior_flat, atol=0.05), (
        "Posterior identical to prior — payoff modality is being dropped (regression of #6)."
    )


def test_observation_likelihood_requires_own_action():
    from trust.model import TrustGameModel
    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    with pytest.raises(ValueError, match="own_action"):
        model.observation_likelihood([0, 1], own_action=None)


def test_observation_likelihood_requires_both_modalities():
    from trust.model import TrustGameModel
    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    with pytest.raises(ValueError, match="both modalities"):
        model.observation_likelihood([0], own_action=0)


def test_joint_observation_likelihood_multiplies_both_modalities():
    """Sanity: L = A[0][o0] * A[1][o1, own]."""
    from trust.model import TrustGameModel
    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    L = model.joint_observation_likelihood(partner_action=0, payoff_obs=0, own_action=0)
    expected = np.asarray(model.A[0][0]) * np.asarray(model.A[1][0, 0])
    np.testing.assert_allclose(L, expected, atol=1e-12)
```

- [ ] **Step 2: run, expect failure**

Run: `pytest tests/test_payoff_modality_in_likelihood.py -q`
Expected: FAIL (no `trust.model` yet).

### Task 3.4: implement `trust/model.py`

**Files:**
- Create: `trust/model.py`

- [ ] **Step 1: write the new canonical class**

```python
"""Canonical trust-game POMDP. Replaces the old TrustGameModel +
GradedTrustGameModel + _BaseTrustGameModel hierarchy with a single class
that branches on payoff_mode (decisions #5, #6 of the design spec).
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass

import numpy as np

from aif.maths import log_stable, softmax
from aif.utils import obj_array
from trust.payoffs import (
    build_graded_payoff_matrix,
    build_payoff_matrix,
    decode_action,
    decode_instantaneous_index,
    expected_agent_payoff,
    factorized_num_controls,
    infer_payoff_levels,
    payoff_distribution,
    payoff_to_index,
)
from trust.stance import (
    STANCE_ORDER,
    cooperation_evidence_strength,
    get_type_stance_cooperation_table,
    interpolate_stance_transition,
)
from trust.types import (
    PARTNER_TYPE_ORDER,
    PartnerType,
    default_partner_type_params,
)

_BINARY_KEYS = {"mutual_coop", "sucker", "temptation", "mutual_defect"}
_GRADED_KEYS = {"num_investment_levels", "endowment", "multiplier"}


class TrustGameModel:
    """Active-inference generative model for the multi-partner trust game.

    Per decision #5: single class with payoff_mode={'binary','graded'}.
    Per decision #6: infer_joint_posterior uses both observation modalities.
    Per decision #8: no back-compat — removed config keys raise ValueError.
    Per decision #9 (downstream): build_A/build_B return fresh copies each
    call (so TrustGameAgent can give each per-partner aif.Agent its own copy).
    """

    def __init__(self, config):
        cfg = asdict(config) if is_dataclass(config) else dict(config)
        self.config = cfg

        # ----- removed legacy keys -----
        if "model_class" in cfg:
            raise ValueError(
                "config key 'model_class' was removed in the B+A restructure. "
                "TrustGameModel is now the only class. drop the key and add payoff_mode."
            )
        if "variant" in cfg:
            raise ValueError(
                "config key 'variant' was removed in the B+A restructure. "
                "rename to 'assignment_mode' and rerun."
            )

        # ----- shared knobs -----
        self.num_partners = int(cfg.get("num_partners", 4))
        self.partner_type_names = tuple(cfg.get("partner_types", PARTNER_TYPE_ORDER))
        self.stance_names = tuple(cfg.get("stance_names", STANCE_ORDER))
        self.num_types = len(self.partner_type_names)
        self.num_stances = len(self.stance_names)
        self.p_switch = float(cfg.get("p_switch", 0.05))
        self.assignment_mode = str(cfg.get("assignment_mode", "random"))
        self.observation_noise = float(cfg.get("observation_noise", 0.0))
        self.preference_temperature = float(cfg.get("preference_temperature", 1.0))
        self.partner_type_params = default_partner_type_params()
        self.partner_type_params.update(cfg.get("partner_type_params", {}))
        self.partner_types = [
            PartnerType(type_name=n, params=self.partner_type_params.get(n, {}))
            for n in self.partner_type_names
        ]

        # ----- payoff branch (decision #5) -----
        if "payoff_mode" not in cfg:
            raise ValueError(
                "config must specify payoff_mode={'binary','graded'}. "
                "defaulting was removed in the B+A restructure."
            )
        self.payoff_mode = str(cfg["payoff_mode"])
        if self.payoff_mode == "binary":
            stray = _GRADED_KEYS & cfg.keys()
            if stray:
                raise ValueError(f"payoff_mode='binary' but graded-only keys present: {sorted(stray)}")
            self.num_social_actions = 2
            self.payoff_matrix = build_payoff_matrix(
                mutual_coop=tuple(cfg.get("mutual_coop", (3.0, 3.0))),
                sucker=tuple(cfg.get("sucker", (-1.0, 5.0))),
                temptation=tuple(cfg.get("temptation", (5.0, -1.0))),
                mutual_defect=tuple(cfg.get("mutual_defect", (1.0, 1.0))),
            )
        elif self.payoff_mode == "graded":
            stray = _BINARY_KEYS & cfg.keys()
            if stray:
                raise ValueError(f"payoff_mode='graded' but binary-only keys present: {sorted(stray)}")
            num_levels = int(cfg.get("num_investment_levels", 6))
            self.num_social_actions = num_levels
            self.payoff_matrix = build_graded_payoff_matrix(
                num_levels=num_levels,
                endowment=float(cfg.get("endowment", 10.0)),
                multiplier=float(cfg.get("multiplier", 3.0)),
            )
        else:
            raise ValueError(f"unknown payoff_mode={self.payoff_mode!r}, expected 'binary' or 'graded'")

        # ----- derived structure (mode-agnostic) -----
        self.payoff_levels = infer_payoff_levels(self.payoff_matrix)
        self.num_obs = [2, len(self.payoff_levels)]
        self.num_controls = factorized_num_controls(
            self.num_partners, self.assignment_mode, self.num_social_actions
        )
        self.partner_action_prob_table = self._build_partner_action_prob_table()
        self.payoff_index_table = self._build_payoff_index_table()
        self.agent_payoff_table = self.payoff_matrix[:, :, 0]

        # ----- cached canonical matrices -----
        self.A = self.build_A()
        self.B = self.build_B()
        self.C = self.build_C()
        self.D = self.build_D()

    # ----- properties -----

    @property
    def uses_factorized_controls(self) -> bool:
        return len(self.num_controls) > 1

    # ----- builders (fresh copy each call) -----

    def _build_partner_action_prob_table(self) -> np.ndarray:
        return get_type_stance_cooperation_table(self.partner_type_names)

    def _build_payoff_index_table(self) -> np.ndarray:
        indices = np.zeros((self.num_social_actions, 2), dtype=int)
        for agent_action in range(self.num_social_actions):
            for partner_action in range(2):
                payoff = self.payoff_matrix[agent_action, partner_action, 0]
                indices[agent_action, partner_action] = payoff_to_index(payoff, self.payoff_levels)
        return indices

    def social_action_for_action(self, action: int) -> int:
        if self.assignment_mode == "agent_choice":
            _, social_action = decode_action(
                int(action), self.num_partners, self.assignment_mode,
                num_social_actions=self.num_social_actions,
            )
            return int(social_action)
        return int(action)

    def build_A(self) -> np.ndarray:
        """Build (fresh copy of) the likelihood object-array."""
        A = obj_array(2)
        partner_action = np.zeros((2, self.num_types, self.num_stances), dtype=float)
        for type_idx in range(self.num_types):
            for stance_idx in range(self.num_stances):
                p_coop = self.partner_action_prob_table[type_idx, stance_idx]
                clean = np.asarray([p_coop, 1.0 - p_coop], dtype=float)
                noisy = (1.0 - self.observation_noise) * clean + self.observation_noise * 0.5
                partner_action[:, type_idx, stance_idx] = noisy

        payoff_obs = np.zeros((len(self.payoff_levels), self.num_social_actions, self.num_types, self.num_stances), dtype=float)
        for agent_action in range(self.num_social_actions):
            for type_idx in range(self.num_types):
                for stance_idx in range(self.num_stances):
                    p_coop = self.partner_action_prob_table[type_idx, stance_idx]
                    coop_idx = int(self.payoff_index_table[agent_action, 0])
                    defect_idx = int(self.payoff_index_table[agent_action, 1])
                    payoff_obs[coop_idx, agent_action, type_idx, stance_idx] += p_coop
                    payoff_obs[defect_idx, agent_action, type_idx, stance_idx] += 1.0 - p_coop

        A[0] = partner_action
        A[1] = payoff_obs
        return A

    def build_B(self) -> np.ndarray:
        """Build (fresh copy of) the transition object-array."""
        B = obj_array(3)
        num_actions_total = int(np.prod(self.num_controls))

        type_transition = np.full(
            (self.num_types, self.num_types),
            self.p_switch / max(self.num_types - 1, 1), dtype=float,
        )
        np.fill_diagonal(type_transition, 1.0 - self.p_switch)
        B[0] = np.repeat(type_transition[:, :, None], num_actions_total, axis=2)

        stance_transition = np.zeros((self.num_stances, self.num_stances, num_actions_total), dtype=float)
        own_tensor = np.zeros((self.num_social_actions, self.num_social_actions, num_actions_total), dtype=float)
        for action in range(num_actions_total):
            controls = decode_instantaneous_index(action, self.num_controls)
            if self.uses_factorized_controls:
                stance_idx = int(controls[-2])
                own_idx = int(controls[-1])
                evidence = cooperation_evidence_strength(stance_idx, num_social_actions=self.num_social_actions)
                stance_transition[:, :, action] = interpolate_stance_transition(evidence)
                own_tensor[own_idx, :, action] = 1.0
            else:
                evidence = cooperation_evidence_strength(
                    action=self.social_action_for_action(action),
                    num_social_actions=self.num_social_actions,
                )
                stance_transition[:, :, action] = interpolate_stance_transition(evidence)
                social_action = self.social_action_for_action(action)
                own_tensor[social_action, :, action] = 1.0
        B[1] = stance_transition
        B[2] = own_tensor
        return B

    def build_C(self) -> np.ndarray:
        C = obj_array(2)
        C[0] = np.zeros(2, dtype=float)
        payoff_values = np.asarray(self.payoff_levels, dtype=float)
        scaled = payoff_values / max(self.preference_temperature, 1e-12)
        C[1] = log_stable(softmax(scaled, backend="numpy"), backend="numpy")
        return C

    def build_D(self) -> np.ndarray:
        D = obj_array(3)
        D[0] = np.full(self.num_types, 1.0 / self.num_types, dtype=float)
        D[1] = np.asarray([0.2, 0.6, 0.2], dtype=float)
        D[2] = np.full(self.num_social_actions, 1.0 / self.num_social_actions, dtype=float)
        return D

    def build_pA(self, scale: float = 1.0) -> np.ndarray:
        pA = obj_array(len(self.A))
        A = self.build_A()  # fresh copy as starting point
        for modality in range(len(A)):
            pA[modality] = float(scale) * np.asarray(A[modality], dtype=float).copy()
        return pA

    def build_pB(self, scale: float = 10.0) -> np.ndarray:
        pB = obj_array(len(self.B))
        B = self.build_B()
        for factor in range(len(B)):
            pB[factor] = float(scale) * np.asarray(B[factor], dtype=float).copy()
        return pB

    def get_matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.A, self.B, self.C, self.D

    # ----- belief operations -----

    def as_joint_belief(self, belief: np.ndarray) -> np.ndarray:
        array = np.asarray(belief, dtype=float)
        if array.shape == (self.num_types, self.num_stances):
            joint = array
        elif array.size == self.num_types * self.num_stances:
            joint = array.reshape(self.num_types, self.num_stances)
        else:
            raise ValueError(
                f"Expected joint belief with shape {(self.num_types, self.num_stances)} or flat size "
                f"{self.num_types * self.num_stances}, got {array.shape}."
            )
        total = joint.sum()
        return joint / max(total, 1e-16)

    def partner_action_distribution(self, joint_belief: np.ndarray) -> np.ndarray:
        joint = self.as_joint_belief(joint_belief)
        p_coop = float(np.sum(joint * self.partner_action_prob_table))
        return np.asarray([p_coop, 1.0 - p_coop], dtype=float)

    def joint_observation_likelihood(self, partner_action: int, payoff_obs: int, own_action: int) -> np.ndarray:
        """Decision #6: likelihood multiplies through both modalities."""
        L_action = np.asarray(self.A[0][int(partner_action)], dtype=float)
        L_payoff = np.asarray(self.A[1][int(payoff_obs), int(own_action)], dtype=float)
        return L_action * L_payoff

    def observation_likelihood(self, observation, own_action) -> np.ndarray:
        if len(observation) < 2:
            raise ValueError(
                f"observation_likelihood now requires both modalities; got {observation!r}. "
                "callers must pass [o_partner_action, o_payoff]."
            )
        if own_action is None:
            raise ValueError(
                "observation_likelihood now requires own_action to evaluate the payoff modality."
            )
        return self.joint_observation_likelihood(
            int(observation[0]),
            payoff_obs=int(observation[1]),
            own_action=int(own_action),
        )

    def type_transition_for_action(self, action: int) -> np.ndarray:
        return np.asarray(self.B[0][:, :, int(action)], dtype=float)

    def stance_transition_for_action(self, action: int) -> np.ndarray:
        return np.asarray(self.B[1][:, :, int(action)], dtype=float)

    def transition_for_action(self, action: int = 0) -> np.ndarray:
        return self.type_transition_for_action(action)

    def stance_transition_for_executed_own_action(self, own_action: int) -> np.ndarray:
        evidence = cooperation_evidence_strength(int(own_action), num_social_actions=self.num_social_actions)
        return interpolate_stance_transition(evidence)

    def predict_next_joint_belief(self, joint_belief: np.ndarray, action: int) -> np.ndarray:
        joint = self.as_joint_belief(joint_belief)
        type_transition = self.type_transition_for_action(int(action) if not self.uses_factorized_controls else 0)
        if self.uses_factorized_controls:
            stance_transition = self.stance_transition_for_executed_own_action(int(action))
        else:
            stance_transition = self.stance_transition_for_action(int(action))
        predictive = type_transition @ joint @ stance_transition.T
        predictive /= max(float(predictive.sum()), 1e-16)
        return predictive

    def infer_joint_posterior(self, joint_belief, observation, own_action) -> np.ndarray:
        """Decision #6: bug-fixed. Now multiplies through both modalities."""
        prior = self.as_joint_belief(joint_belief)
        likelihood = self.observation_likelihood(observation, own_action=own_action)
        posterior = prior * likelihood
        posterior /= max(float(posterior.sum()), 1e-16)
        return posterior

    def predict_payoff_distribution(self, agent_action: int, partner_action_probs: np.ndarray) -> np.ndarray:
        return payoff_distribution(
            agent_action=agent_action,
            partner_action_probs=partner_action_probs,
            payoff_matrix=self.payoff_matrix,
            payoff_levels=self.payoff_levels,
        )

    def expected_agent_payoff(self, agent_action: int, partner_action_probs: np.ndarray) -> float:
        return expected_agent_payoff(agent_action, partner_action_probs, self.payoff_matrix)
```

- [ ] **Step 2: run model tests, expect PASS**

Run: `pytest tests/test_trust_model_canonical.py tests/test_payoff_modality_in_likelihood.py -v`
Expected: all PASS.

### Task 3.5: re-export `TrustGameModel` and rewrite `experiment/factory.py`

**Files:**
- Modify: `trust/__init__.py`, `experiment/factory.py`, `experiment/runner.py`, `experiment/config.py`

- [ ] **Step 1: add re-exports to `trust/__init__.py`**

```python
"""trust — project package for the multi-partner trust game."""
from trust.model import TrustGameModel
```

(`TrustGameAgent` etc. land in Phase 4.)

- [ ] **Step 2: rewrite `experiment/factory.py:create_model`**

Open `experiment/factory.py`. Replace:

```python
from agent.model.trust_game import GradedTrustGameModel, TrustGameModel
...
def create_model(config: ExperimentConfig) -> TrustGameModel:
    if config.payoff_mode == "graded":
        return GradedTrustGameModel(asdict(config))
    return TrustGameModel(asdict(config))
```

with:

```python
from trust.model import TrustGameModel
...
def create_model(config: ExperimentConfig) -> TrustGameModel:
    return TrustGameModel(asdict(config))
```

The dispatch on `payoff_mode` now happens inside `TrustGameModel.__init__` itself.

- [ ] **Step 3: update remaining experiment imports**

In `experiment/config.py`: replace `from agent.model.types import PARTNER_TYPE_ORDER` with `from trust.types import PARTNER_TYPE_ORDER`.

In `experiment/runner.py`: replace `from agent.model.trust_game import TrustGameModel` with `from trust.model import TrustGameModel`. (The `from agent.base import BaseAgent` import there waits for Phase 4.)

- [ ] **Step 4: smoke test**

Run: `pytest tests/test_trust_model_canonical.py -v && python -c "from experiment.factory import create_model; print('factory ok')"`
Expected: tests PASS, factory imports cleanly.

### Task 3.6: add `payoff_mode: "binary"` to 22 configs

**Files:**
- Modify: 22 JSON files in `configs/` (all except `graded_betrayal.json`, `graded_trust_factorial.json`, and `benchmark_cvc_*.json`)

- [ ] **Step 1: enumerate the configs to edit**

```bash
ls configs/*.json | grep -v cvc | grep -v graded_
```

Expected output (22 files):
```
configs/benchmark_betrayal.json
configs/benchmark_betrayal_comprehensive.json
configs/benchmark_betrayal_fair.json
configs/benchmark_comprehensive.json
configs/benchmark_default.json
configs/benchmark_full.json
configs/benchmark_noisy.json
configs/benchmark_resource_sharing.json
configs/clinical_betrayal.json
configs/clinical_phenotypes.json
configs/h1_depth_affect_factorial.json
configs/h2_lesion_dissociation.json
configs/h4_betrayal_recovery.json
configs/h5_partner_selection.json
configs/sensitivity_affect_params.json
configs/shallow_affect_confirm.json
configs/smoke_test.json
```

(Count may vary — confirm against actual `ls` output.)

- [ ] **Step 2: add `"payoff_mode": "binary"` as a top-level key**

For each file, insert `"payoff_mode": "binary",` immediately after the opening `{`. Example for `configs/smoke_test.json`:

before:
```json
{
  "experiment_name": "smoke_test",
  "num_partners": 4,
  ...
}
```

after:
```json
{
  "payoff_mode": "binary",
  "experiment_name": "smoke_test",
  "num_partners": 4,
  ...
}
```

This can be scripted but DO NOT use sed — JSON is structured. A safe Python one-liner:

```bash
python -c "
import json, pathlib
configs = pathlib.Path('configs')
for p in configs.glob('*.json'):
    if 'cvc' in p.name or p.name in ('graded_betrayal.json', 'graded_trust_factorial.json'):
        continue
    cfg = json.loads(p.read_text())
    if 'payoff_mode' in cfg:
        continue
    new = {'payoff_mode': 'binary', **cfg}
    p.write_text(json.dumps(new, indent=2) + '\n')
    print(f'updated {p.name}')
"
```

- [ ] **Step 3: verify graded configs untouched**

Run: `python -c "import json; print(json.loads(open('configs/graded_betrayal.json').read())['payoff_mode'])"`
Expected: prints `graded`.

- [ ] **Step 4: config-loader smoke test**

```bash
python -c "
import json, pathlib
from trust.model import TrustGameModel
for p in pathlib.Path('configs').glob('*.json'):
    if 'cvc' in p.name:
        continue
    cfg = json.loads(p.read_text())
    try:
        TrustGameModel(cfg)
        print(f'{p.name}: ok')
    except Exception as e:
        print(f'{p.name}: FAIL - {e}')
        raise
"
```

Expected: all 24 non-cvc configs print `ok`. If any FAIL, fix the offending config and re-run.

### Task 3.7: update model-class tests

**Files:**
- Modify: `tests/test_generative_model.py`, `tests/test_action_dependent_model.py`

- [ ] **Step 1: rewrite imports and class usages in `tests/test_generative_model.py`**

Replace:
```python
from agent.model.trust_game import GradedTrustGameModel, TrustGameModel
```
with:
```python
from trust.model import TrustGameModel
```

For every `GradedTrustGameModel(cfg)` call, rewrite as:
```python
TrustGameModel({**cfg, "payoff_mode": "graded"})
```

For every `TrustGameModel(cfg)` call without an explicit `payoff_mode`, rewrite as:
```python
TrustGameModel({**cfg, "payoff_mode": "binary"})
```

(In-test fixtures may need a `"payoff_mode"` key added.)

- [ ] **Step 2: same edits for `tests/test_action_dependent_model.py`**

- [ ] **Step 3: run those tests, expect PASS**

Run: `pytest tests/test_generative_model.py tests/test_action_dependent_model.py -v`
Expected: PASS.

### Task 3.8: delete `agent/model/`

**Files:**
- Delete: `agent/model/types.py`, `agent/model/stance.py`, `agent/model/payoffs.py`, `agent/model/trust_game.py`, `agent/model/__init__.py`

- [ ] **Step 1: confirm nothing in `agent/` still imports from `agent/model/`**

Run: `grep -rn 'from agent.model' agent/`
Expected: a few hits in `agent/base.py` and `agent/inference/rollout.py`. These must be rewritten before deletion. Update each:
- `from agent.model.trust_game import _BaseTrustGameModel, TrustGameModel` → `from trust.model import TrustGameModel` (drop `_BaseTrustGameModel` references; it doesn't exist post-merge)
- `from agent.model.types import X` → `from trust.types import X`
- `from agent.model.payoffs import X` → `from trust.payoffs import X`
- `from agent.model.stance import X` → `from trust.stance import X`

- [ ] **Step 2: delete `agent/model/`**

```bash
git rm -r agent/model/
```

- [ ] **Step 3: run full test suite (with the same Phase-2 ignores)**

Run: `pytest tests/ -q --ignore=tests/test_interoception.py --ignore=tests/test_discrete_beta.py`
Expected: PASS. If `tests/conftest.py` fails on import (it has `from agent.X` lines), defer those failures to Phase 4 by extending the ignore list. Goal: Phase 3 leaves the test suite in a state where new + ported model tests pass; agent-class tests are still on the old code.

### Task 3.9: commit 3

- [ ] **Step 1: stage and commit**

```bash
git add trust/ tests/test_trust_model_canonical.py tests/test_payoff_modality_in_likelihood.py \
        tests/test_generative_model.py tests/test_action_dependent_model.py \
        experiment/factory.py experiment/runner.py experiment/config.py \
        configs/
git rm -r agent/model/
git commit -m "feat(trust): canonical TrustGameModel + payoff-drop bug fix

Decisions #5, #6, #8 of the design spec land in this commit:

- trust.model.TrustGameModel replaces TrustGameModel + GradedTrustGameModel
  + _BaseTrustGameModel. payoff_mode={'binary','graded'} switch in the
  constructor; removed config keys (variant, model_class) raise ValueError.
- infer_joint_posterior now multiplies through both observation modalities
  (decision #6). observation_likelihood and joint_observation_likelihood go
  fail-fast on missing args. invalidates noisy-observation experiments.
- experiment.factory.create_model collapses to a single TrustGameModel call.
- 22 binary configs gain explicit 'payoff_mode': 'binary'. graded configs
  unchanged (already declare it).
- agent/model/ deleted entirely.

Spec: docs/superpowers/specs/2026-04-18-aif-extraction-design.md"
```

---

## Phase 4: PR-2 commit 4 — `trust/` agent layer + per-partner architecture + `agent/` deletion

**Goal:** create `trust/agent.py` with `TrustGameAgent` (per decisions #4 + #9: composes N per-partner `aif.Agent` instances with their own A/B/pA/pB), `trust/affective.py`, `trust/lesioned.py`, `trust/rollout.py`. Delete `agent/` directory entirely. Update remaining 13 test files.

### Task 4.1: write tests for per-partner Dirichlet learning (decision #9)

**Files:**
- Test: `tests/test_per_partner_learning.py` (new)

- [ ] **Step 1: create test file**

```python
"""Decision #9: each per-partner aif.Agent holds its OWN A, B, pA, pB.
C, D, E remain shared by reference."""
from __future__ import annotations

import numpy as np


def test_each_partner_has_independent_pA():
    from trust.agent import TrustGameAgent
    from trust.model import TrustGameModel
    cfg = {"payoff_mode": "binary", "num_partners": 3}
    agent = TrustGameAgent(TrustGameModel(cfg), learn_A=True, pA_scale=1.0)

    # All 3 partners' pA start identical (fresh copies):
    for i in range(1, 3):
        np.testing.assert_allclose(agent.partners[0].pA[0], agent.partners[i].pA[0])

    # Mutating one must not affect the others:
    agent.partners[0].pA[0] += 5.0
    for i in range(1, 3):
        assert not np.allclose(agent.partners[0].pA[0], agent.partners[i].pA[0])


def test_each_partner_has_independent_A():
    from trust.agent import TrustGameAgent
    from trust.model import TrustGameModel
    cfg = {"payoff_mode": "binary", "num_partners": 3}
    agent = TrustGameAgent(TrustGameModel(cfg))
    for i in range(1, 3):
        np.testing.assert_allclose(agent.partners[0].A[0], agent.partners[i].A[0])

    agent.partners[0].A[0][0, 0, 0] = 999.0
    assert agent.partners[1].A[0][0, 0, 0] != 999.0


def test_C_D_shared_by_reference():
    from trust.agent import TrustGameAgent
    from trust.model import TrustGameModel
    cfg = {"payoff_mode": "binary", "num_partners": 3}
    agent = TrustGameAgent(TrustGameModel(cfg))
    for i in range(1, 3):
        assert agent.partners[0].C is agent.partners[i].C
        assert agent.partners[0].D is agent.partners[i].D


def test_observe_outcome_only_updates_active_partner_pA():
    from trust.agent import TrustGameAgent
    from trust.model import TrustGameModel
    cfg = {"payoff_mode": "binary", "num_partners": 3, "observation_noise": 0.0}
    agent = TrustGameAgent(TrustGameModel(cfg), learn_A=True)
    agent.reset()

    pA_before = [np.asarray(p.pA[0]).copy() for p in agent.partners]
    agent.observe_outcome(partner_idx=1, observation=[0, 0], action_taken=0,
                          partner_action=0, payoff=3.0)
    pA_after = [np.asarray(p.pA[0]).copy() for p in agent.partners]

    np.testing.assert_array_equal(pA_after[0], pA_before[0])  # untouched
    assert not np.allclose(pA_after[1], pA_before[1])           # changed
    np.testing.assert_array_equal(pA_after[2], pA_before[2])  # untouched
```

- [ ] **Step 2: run, expect failure**

Run: `pytest tests/test_per_partner_learning.py -q`
Expected: FAIL — `trust.agent` doesn't exist yet.

### Task 4.2: implement `trust/rollout.py`

**Files:**
- Create: `trust/rollout.py` (move trust-specific helpers from `agent/inference/rollout.py`, plus the per-partner-aware planner)

- [ ] **Step 1: copy and rename**

```bash
cp agent/inference/rollout.py trust/rollout.py
```

- [ ] **Step 2: rewrite imports in `trust/rollout.py`**

`from agent.inference.X` → `from aif.X` for generic deps.
`from agent.model.X` → `from trust.X` for trust deps (already moved in Phase 3).

Run: `grep -n 'from agent' trust/rollout.py`
Expected: no output.

- [ ] **Step 3: extract `generate_observation_sequences`**

Already moved to `aif/runtime.py` in Phase 1. Delete the function definition from `trust/rollout.py` and add `from aif.runtime import generate_observation_sequences` at the top if anything in `trust/rollout.py` calls it.

- [ ] **Step 4: rewrite `decision_step_trust_game` to take per-partner stacks**

Per design-spec Section 3, the planner signature changes:

```python
def decision_step_trust_game(
    beliefs: np.ndarray,                              # (N, num_types, num_stances)
    active_partner: int,                              # -1 in agent_choice mode
    policies: np.ndarray,
    observation_sequences: np.ndarray,
    B_type: np.ndarray,                               # (N, num_types, num_types)
    B_stance_by_action: np.ndarray,                   # (N, num_actions, num_stances, num_stances)
    partner_action_prob_tables: np.ndarray,           # (N, num_types, num_stances) — per-partner
    payoff_index_table: np.ndarray,
    agent_payoff_table: np.ndarray,
    payoff_preferences: np.ndarray,
    partner_action_preferences: np.ndarray,
    precision_signal: np.ndarray,                     # (N,)
    assignment_mode_code: int,
    gamma: float,
    use_utility_flag: float,
    use_information_gain_flag: float,
    num_social_actions: int,
    log_policy_prior: np.ndarray,
) -> dict:
    ...
```

The body needs per-partner indexing where the old code had a single shared `partner_action_prob_table`. Where the old code reads `partner_action_prob_table[t, s]`, the new code reads `partner_action_prob_tables[partner_idx, t, s]`. The `_rollout_policy_trust_game_*` helpers also need a `partner_idx` argument so they can index into the per-partner stacks.

This is the most subtle code change in the entire restructure. Approach:

1. Read the old `decision_step_trust_game` body carefully.
2. For each line that reads `partner_action_prob_table`, `B_type`, `B_stance_by_action` — rewrite to index by `partner_idx` (the loop variable that iterates over partners).
3. The output structure (returned dict) stays the same shape.

- [ ] **Step 5: add `build_transition_views` helper**

```python
def build_transition_views(B, num_controls, factorized_policies):
    """Returns (B_type, B_stance_by_action) for ONE partner's B object-array.

    Called per-partner by TrustGameAgent to assemble the per-partner stacks
    that decision_step_trust_game expects (decision #9)."""
    # ... port the equivalent logic from agent/base.py:_refresh_transition_views
    ...
```

Look at `agent/base.py` for the existing `_refresh_transition_views` method and port the relevant slicing logic.

- [ ] **Step 6: add `decode_raw_action_to_partner_and_social` helper**

```python
def decode_raw_action_to_partner_and_social(
    raw_action: int,
    active_partner: int,
    assignment_mode_code: int,
    factorized_policies: bool,
    num_social_actions: int,
    num_partners: int,
) -> tuple[int, int]:
    """Decompose a raw env action into (partner_idx, social_action).

    Verbatim port of BaseAgent._decode_raw_action."""
    # ... copy the logic from agent/base.py
```

- [ ] **Step 7: smoke compile**

Run: `python -c "import trust.rollout; print('ok')"`
Expected: prints `ok`.

### Task 4.3: implement `trust/agent.py`

**Files:**
- Create: `trust/agent.py`

- [ ] **Step 1: write the new class**

Per design-spec Section 3:

```python
"""trust.TrustGameAgent — composes N per-partner aif.Agent instances."""
from __future__ import annotations

import numpy as np

import aif
from trust.model import TrustGameModel
from trust.rollout import (
    build_transition_views,
    decision_step_trust_game,
    decode_raw_action_to_partner_and_social,
)


class TrustGameAgent:
    """Active-inference agent for the multi-partner trust game.

    Composes N aif.Agent instances (one per partner). Each per-partner agent
    holds its own A, B, pA, pB (per-partner Dirichlet learning, decision #9).
    C, D, E are shared by reference. Per-partner posterior qs and ephemeral
    state are private. Cross-partner action selection (agent_choice mode)
    lives here. The trust-specific planner is delegated to trust.rollout.
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
        self.model = model
        self.num_partners = model.num_partners
        self.planning_horizon = planning_horizon
        self.gamma = gamma
        self.lr = lr
        self.action_sampling = action_sampling
        self.use_utility = use_utility
        self.use_information_gain = use_information_gain
        self.max_policies = max_policies
        self.reference_horizon = reference_horizon
        self.seed = seed
        self.use_parameter_learning = use_parameter_learning
        self.learn_A = learn_A
        self.learn_B = learn_B
        self.learn_E = learn_E
        self.pA_scale = pA_scale
        self.pB_scale = pB_scale
        self.lr_E = lr_E

        single_partner_policies = aif.policies.construct_policies(
            num_controls=model.num_controls,
            planning_horizon=planning_horizon,
            max_policies=max_policies,
            rng=np.random.default_rng(seed),
        )

        self.partners: list[aif.Agent] = [
            aif.Agent(
                A=model.build_A(),       # fresh per-partner copy (decision #9)
                B=model.build_B(),       # fresh per-partner copy (decision #9)
                C=model.C,                # shared by reference
                D=model.D,                # shared by reference
                E=None,
                policies=single_partner_policies,
                pA=model.build_pA(pA_scale) if learn_A else None,
                pB=model.build_pB(pB_scale) if learn_B else None,
                gamma=gamma,
                use_utility=use_utility,
                use_information_gain=use_information_gain,
                action_sampling=action_sampling,
                rng=np.random.default_rng(seed + 1 + i),
            )
            for i in range(self.num_partners)
        ]
        self.reset()

    def reset(self) -> None:
        for p in self.partners:
            p.reset()

    # ----- belief views -----

    @property
    def qs_per_partner(self) -> np.ndarray:
        """(N, num_types, num_stances) — joint type-stance posteriors per partner.

        Each partner's qs is a single object-array entry (the joint factor),
        reshaped to (num_types, num_stances)."""
        out = np.zeros((self.num_partners, self.model.num_types, self.model.num_stances), dtype=float)
        for i, p in enumerate(self.partners):
            qs0 = np.asarray(p.qs[0]) if p.qs is not None else np.asarray(p.D[0])
            out[i] = qs0.reshape(self.model.num_types, self.model.num_stances)
        return out

    @property
    def partner_beliefs(self) -> np.ndarray:
        return self.qs_per_partner.sum(axis=2)

    @property
    def partner_stance_beliefs(self) -> np.ndarray:
        return self.qs_per_partner.sum(axis=1)

    @property
    def partner_action_prob_tables(self) -> np.ndarray:
        """(N, num_types, num_stances) — derived from each partner's A[0].

        Reflects per-partner learning."""
        out = np.zeros((self.num_partners, self.model.num_types, self.model.num_stances), dtype=float)
        for i, p in enumerate(self.partners):
            out[i] = p.A[0][0]  # P(o_partner_action=0 | t, s) = P(coop | t, s)
        return out

    # ----- planner / action selection -----

    def precision_signal(self) -> np.ndarray:
        """(N,) — per-partner gamma multiplier. Default: ones."""
        return np.ones((self.num_partners,), dtype=float)

    def choose_partner_and_action(self, active_partner: int | None = None) -> int:
        """Plan + sample raw env action."""
        # Build per-partner stacks expected by trust.rollout.decision_step_trust_game
        Btype_stack = np.stack([build_transition_views(p.B, self.model.num_controls,
                                                       factorized_policies=self.model.uses_factorized_controls)[0]
                                for p in self.partners])
        Bstance_stack = np.stack([build_transition_views(p.B, self.model.num_controls,
                                                         factorized_policies=self.model.uses_factorized_controls)[1]
                                  for p in self.partners])
        result = decision_step_trust_game(
            beliefs=self.qs_per_partner,
            active_partner=active_partner if active_partner is not None else -1,
            policies=self.partners[0].policies,
            observation_sequences=...,  # construct via aif.runtime.generate_observation_sequences
            B_type=Btype_stack,
            B_stance_by_action=Bstance_stack,
            partner_action_prob_tables=self.partner_action_prob_tables,
            payoff_index_table=self.model.payoff_index_table,
            agent_payoff_table=self.model.agent_payoff_table,
            payoff_preferences=self.model.C[1],
            partner_action_preferences=self.model.C[0],
            precision_signal=self.precision_signal(),
            assignment_mode_code=0 if self.model.assignment_mode == "random" else 1,
            gamma=self.gamma,
            use_utility_flag=1.0 if self.use_utility else 0.0,
            use_information_gain_flag=1.0 if self.use_information_gain else 0.0,
            num_social_actions=self.model.num_social_actions,
            log_policy_prior=np.zeros(self.partners[0].policies.shape[0]),
        )
        # extract raw action via aif.sample_action on result['q_pi']
        # ...
        return raw_action

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
        """Belief update + Dirichlet learning for the active partner only (decision #9)."""
        active = self.partners[partner_idx]
        qs_prev = active.qs

        # 1-step Bayes update on the active partner only
        aif.infer_states(active, obs=observation)

        if self.learn_A:
            aif.update_pA(active, obs=observation, learning_rate=self.lr)
            # rebuild A from updated pA for this partner only
            for m in range(len(active.A)):
                active.A[m] = (active.pA[m] / active.pA[m].sum(axis=0, keepdims=True))

        if self.learn_B:
            # placeholder — wire up update_pB with qs_prev and the action
            pass

        self._update_auxiliary_states(partner_idx, partner_action, payoff)

    def get_metrics(self) -> dict:
        """Round-level metrics for analysis. Mirrors current BaseAgent.get_metrics."""
        return {
            "qs_per_partner": self.qs_per_partner.copy(),
            "partner_beliefs": self.partner_beliefs.copy(),
            "partner_stance_beliefs": self.partner_stance_beliefs.copy(),
        }

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float) -> None:
        """No-op on TrustGameAgent. AffectiveAgent overrides."""
        pass
```

NOTE: The `choose_partner_and_action` body has placeholder ellipses for the observation-sequence construction and the `raw_action` extraction. Look at the current `agent/base.py:plan_and_act` (or whatever the current method is named) for the reference implementation; port that code path with the per-partner-aware signatures.

The `learn_B` branch has a placeholder; use `aif.update_pB(active, qs_previous=qs_prev, action=[action_taken, ...])` once the action-encoding for the trust game is sorted (look at `agent/base.py` for the pattern).

- [ ] **Step 2: re-export from `trust/__init__.py`**

```python
from trust.agent import TrustGameAgent
```

- [ ] **Step 3: run per-partner-learning tests, expect mostly PASS**

Run: `pytest tests/test_per_partner_learning.py -v`
Expected: `test_each_partner_has_independent_pA`, `test_each_partner_has_independent_A`, `test_C_D_shared_by_reference` PASS. `test_observe_outcome_only_updates_active_partner_pA` may need `aif.update_pA` wiring to work — fix as needed.

### Task 4.4: implement `trust/affective.py` and `trust/lesioned.py`

**Files:**
- Create: `trust/affective.py`, `trust/lesioned.py`

- [ ] **Step 1: write `trust/affective.py`**

```python
"""trust.AffectiveAgent — Hesp-style per-entity affective precision."""
from __future__ import annotations

import numpy as np

from aif.affect.beta import DiscreteBetaState
from trust.agent import TrustGameAgent
from trust.model import TrustGameModel


class AffectiveAgent(TrustGameAgent):
    """Trust-game agent with per-entity affective precision."""

    def __init__(
        self,
        model: TrustGameModel,
        *,
        alpha_charge: float = 3.0,
        sigma_0_sq: float = 0.25,
        initial_beta: float = 1.0,
        num_levels: int = 5,
        persistence: float = 0.8,
        **kwargs,
    ):
        super().__init__(model, **kwargs)
        self.affect = DiscreteBetaState(
            num_entities=self.num_partners,
            num_levels=num_levels,
            persistence=persistence,
            alpha_charge=alpha_charge,
            sigma_0_sq=sigma_0_sq,
            initial_beta=initial_beta,
        )
        self.pending_prediction_partner: int | None = None
        self.pending_prediction_probs: np.ndarray | None = None

    def precision_signal(self) -> np.ndarray:
        return self.affect.get_all_betas()

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float) -> None:
        if self.pending_prediction_partner != partner_idx:
            return
        self.affect.update(
            entity_idx=partner_idx,
            predicted_action_probs=self.pending_prediction_probs,
            observed_action=partner_action,
        )

    def get_betas(self) -> np.ndarray:
        return self.affect.get_all_betas()

    def get_prediction_errors(self) -> np.ndarray:
        return self.affect.get_prediction_errors()
```

- [ ] **Step 2: write `trust/lesioned.py`**

```python
"""trust.LesionedAgent — variant of AffectiveAgent for ablation studies."""
from __future__ import annotations

import numpy as np

from trust.affective import AffectiveAgent


class LesionedAgent(AffectiveAgent):
    def __init__(self, *args, lesion_mode: str = "decouple", **kwargs):
        super().__init__(*args, **kwargs)
        self.lesion_mode = lesion_mode

    def precision_signal(self) -> np.ndarray:
        if self.lesion_mode in {"decouple", "freeze"}:
            return np.ones((self.num_partners,), dtype=float)
        return super().precision_signal()

    def _update_auxiliary_states(self, partner_idx, partner_action, payoff):
        if self.lesion_mode == "freeze":
            return
        super()._update_auxiliary_states(partner_idx, partner_action, payoff)
```

- [ ] **Step 3: re-export**

Append to `trust/__init__.py`:

```python
from trust.affective import AffectiveAgent
from trust.lesioned import LesionedAgent
```

- [ ] **Step 4: smoke**

```bash
python -c "from trust import TrustGameModel, TrustGameAgent, AffectiveAgent, LesionedAgent; print('ok')"
```
Expected: `ok`.

### Task 4.5: rewrite `experiment/factory.py` and `experiment/runner.py` to use `trust.*`

**Files:**
- Modify: `experiment/factory.py`, `experiment/runner.py`

- [ ] **Step 1: replace agent imports**

In `experiment/factory.py`:
```python
from agent.affective import AffectiveAgent
from agent.base import BaseAgent
from agent.lesioned import LesionedAgent
```
becomes:
```python
from trust import AffectiveAgent, LesionedAgent, TrustGameAgent
```

Find every reference to `BaseAgent` and rename to `TrustGameAgent`.

- [ ] **Step 2: same for `experiment/runner.py`**

`from agent.base import BaseAgent` → `from trust import TrustGameAgent`. Rename `BaseAgent` → `TrustGameAgent` throughout.

- [ ] **Step 3: smoke run**

```bash
python -c "from experiment.factory import create_model, create_agent; print('ok')"
```
Expected: `ok` (or imports succeed).

### Task 4.6: update bucket-b test files (13 files)

**Files:**
- Modify: 13 test files (see spec Section 6 bucket b)
- Delete: `tests/test_interoception.py`

- [ ] **Step 1: list affected files**

```bash
grep -l 'from agent\.' tests/*.py
```

Expected output (13 files):
```
tests/test_core.py
tests/test_joint_agent_and_conditions.py
tests/test_hesp_agents.py
tests/test_hesp_v3_model.py
tests/test_hesp_precision_modulation.py
tests/test_theory_alignment.py
tests/test_supported_surface.py
tests/test_environment.py
tests/test_stance_dynamics.py
tests/test_discrete_beta.py
tests/conftest.py
tests/test_generative_model.py        # already done in Phase 3
tests/test_action_dependent_model.py  # already done in Phase 3
```

- [ ] **Step 2: apply mechanical rewrites to each file**

For each, run the following find/replace mentally and apply:
- `from agent.base import BaseAgent` → `from trust import TrustGameAgent`
- `from agent.affective import AffectiveAgent` → `from trust import AffectiveAgent`
- `from agent.lesioned import LesionedAgent` → `from trust import LesionedAgent`
- `from agent.affect.beta import DiscreteBetaState` → `from aif.affect.beta import DiscreteBetaState`
- `from agent.inference.X import Y` → `from aif.X import Y` for `X in {maths, utils, backend, efe, runtime, policies, learning}`
- `from agent.inference.rollout import generate_observation_sequences` → `from aif.runtime import generate_observation_sequences`
- `from agent.inference.rollout import <trust-specific>` → `from trust.rollout import <trust-specific>`
- `from agent.model.types import X` → `from trust.types import X`
- All `BaseAgent(` calls → `TrustGameAgent(` calls.
- All `partner_idx=` kwargs to `DiscreteBetaState` methods → `entity_idx=`.
- All `num_partners=` kwarg to `DiscreteBetaState(...)` → `num_entities=`.

Per file, after edits, run `grep 'from agent' <file>` — expected: no output.

- [ ] **Step 3: delete `tests/test_interoception.py`**

```bash
git rm tests/test_interoception.py
```

- [ ] **Step 4: special handling for `tests/test_supported_surface.py`**

This test asserts which symbols are exported from packages. Rewrite its assertions:
```python
# was: assert hasattr(agent, "BaseAgent")
# now: assert hasattr(trust, "TrustGameAgent")
# was: assert "TrustGameModel" in dir(agent.model)
# now: assert "TrustGameModel" in dir(trust)
```
Open the file, audit each assertion, update accordingly.

- [ ] **Step 5: full test suite**

Run: `pytest tests/ -q`
Expected: 0 failures, 0 errors.

### Task 4.7: delete `agent/` directory entirely

**Files:**
- Delete: all remaining files under `agent/`

- [ ] **Step 1: confirm nothing in the repo still imports `agent.*`**

Run: `grep -rn 'from agent\.\|import agent\.\|import agent$' --include='*.py' .` (excluding `agent/` itself and `archive/`).
Expected: only `agent/` files match (which we're about to delete) and possibly `archive/` (which we leave).

To exclude `archive/`:
```bash
grep -rn 'from agent\.\|import agent\.' --include='*.py' . | grep -v '^agent/\|^archive/'
```
Expected: no output.

- [ ] **Step 2: delete agent/**

```bash
git rm -r agent/
```

- [ ] **Step 3: full test suite**

Run: `pytest tests/ -q`
Expected: 0 failures, 0 errors.

- [ ] **Step 4: update `AGENTS.md`**

Open `AGENTS.md`. Find and update the lines referencing `BaseAgent`, `GradedTrustGameModel`, `agent.model`, `agent.base`. Rewrite to reference `trust.TrustGameAgent`, `trust.TrustGameModel`, etc.

- [ ] **Step 5: delete `tests/test_aif_skeleton.py`**

Per Phase 1 commit message, this test file existed only to gate the dead-code commit. After Phase 4 it has no purpose because `agent.inference.X` no longer exists.

```bash
git rm tests/test_aif_skeleton.py
```

Run: `pytest tests/ -q` to confirm still green.

### Task 4.8: commit 4

- [ ] **Step 1: commit**

```bash
git add trust/agent.py trust/affective.py trust/lesioned.py trust/rollout.py trust/__init__.py \
        tests/test_per_partner_learning.py \
        tests/test_core.py tests/test_joint_agent_and_conditions.py tests/test_hesp_agents.py \
        tests/test_hesp_v3_model.py tests/test_hesp_precision_modulation.py \
        tests/test_theory_alignment.py tests/test_supported_surface.py tests/test_environment.py \
        tests/test_stance_dynamics.py tests/test_discrete_beta.py tests/conftest.py \
        experiment/factory.py experiment/runner.py AGENTS.md
git rm -r agent/
git rm tests/test_interoception.py tests/test_aif_skeleton.py
git commit -m "feat(trust): TrustGameAgent with per-partner aif.Agents; delete agent/

Decisions #4 and #9 land in this commit:

- trust.TrustGameAgent composes N per-partner aif.Agent instances. Each
  per-partner agent holds its own A, B, pA, pB (fresh copies). C, D, E
  are shared by reference. observe_outcome routes belief updates and
  Dirichlet learning to the active partner only.
- trust.AffectiveAgent / trust.LesionedAgent moved.
- trust.rollout.decision_step_trust_game updated for per-partner stacks
  of A/B views.
- 13 test files mechanically updated. tests/test_interoception.py and
  tests/test_aif_skeleton.py deleted.
- agent/ directory deleted entirely.
- AGENTS.md references updated.

Spec: docs/superpowers/specs/2026-04-18-aif-extraction-design.md"
```

---

## Phase 5: PR-2 commit 5 — verification artifacts

**Goal:** add tier-1 hand-written equivalence assertions, tier-2 aggregate sweep, regression tests for decisions #6+#9, STATE.md blocker update, CHANGELOG entry. No source code changes in this commit.

### Task 5.1: write tier-1 equivalence test scaffold

**Files:**
- Test: `tests/test_behavioral_equivalence_pinpoint.py`

- [ ] **Step 1: write the helper module + initial scaffold**

```python
"""Tier-1 equivalence test: ~45 hand-written assert_allclose checks against
specific (config, seed, round, modality) tuples captured from the pre-PR SHA.

Each test was captured by running the OLD code once and pasting the value.

For configs where decision #6 + #9 should NOT change behavior (no learning,
no observation noise), the assertion is bit-identical (atol=1e-6).

For configs where decisions #6 or #9 are EXPECTED to change behavior, the
test is marked xfail(strict=True) — flipping to xpass is a CI failure.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from experiment.config import ExperimentConfig
from experiment.factory import create_agent, create_env, create_model

CONFIGS_DIR = Path("configs")
CAPTURED_FROM_SHA = "PRE_PR_SHA_HERE"  # filled in during Step 4


def _build_run(config_name: str, seed: int, num_rounds: int):
    """Helper: build agent+env from a config file, run N rounds, return agent."""
    cfg_dict = json.loads((CONFIGS_DIR / config_name).read_text())
    cfg_dict["random_seed"] = seed
    cfg = ExperimentConfig(**cfg_dict)
    model = create_model(cfg)
    agent = create_agent(cfg, model)
    env = create_env(cfg, seed=seed)
    obs, info = env.reset()
    agent.reset()
    for _ in range(num_rounds):
        active = info.get("partner_idx", None)
        raw_action = agent.choose_partner_and_action(active_partner=active)
        obs, partner_action, payoff, info = env.step(raw_action)
        agent.observe_outcome(
            partner_idx=info["partner_idx"],
            observation=obs,
            action_taken=info["social_action"],
            partner_action=partner_action,
            payoff=payoff,
        )
    return agent


# ===== smoke_test.json (no learning, no noise — must be bit-identical) =====


def test_smoke_test_seed42_round5_partner0_type_belief():
    agent = _build_run("smoke_test.json", seed=42, num_rounds=5)
    np.testing.assert_allclose(
        agent.partner_beliefs[0],
        [0.0, 0.0, 0.0, 0.0],  # PLACEHOLDER — replace in Step 4
        atol=1e-6,
    )


def test_smoke_test_seed42_round5_partner0_stance_belief():
    agent = _build_run("smoke_test.json", seed=42, num_rounds=5)
    np.testing.assert_allclose(
        agent.partner_stance_beliefs[0],
        [0.0, 0.0, 0.0],  # PLACEHOLDER
        atol=1e-6,
    )


def test_smoke_test_seed43_round10_partner1_belief():
    agent = _build_run("smoke_test.json", seed=43, num_rounds=10)
    np.testing.assert_allclose(
        agent.partner_beliefs[1],
        [0.0, 0.0, 0.0, 0.0],  # PLACEHOLDER
        atol=1e-6,
    )


def test_smoke_test_seed42_round20_mean_payoff():
    agent = _build_run("smoke_test.json", seed=42, num_rounds=20)
    # capture mean payoff from agent.get_metrics() history
    pass  # PLACEHOLDER


# ===== benchmark_default.json (no learning, no noise) =====
# 6 assertions, same shape as above

def test_benchmark_default_seed42_round5_partner0_belief():
    agent = _build_run("benchmark_default.json", seed=42, num_rounds=5)
    np.testing.assert_allclose(agent.partner_beliefs[0], [0.0]*4, atol=1e-6)  # PLACEHOLDER

# ... 5 more for benchmark_default + benchmark_full

# ===== h1, h2, h4, h5 configs (no learning, no noise) =====
# 4 assertions each (16 total)

def test_h1_seed42_round5_partner0_belief():
    agent = _build_run("h1_depth_affect_factorial.json", seed=42, num_rounds=5)
    np.testing.assert_allclose(agent.partner_beliefs[0], [0.0]*4, atol=1e-6)

# ... 15 more

# ===== graded configs =====

def test_graded_betrayal_seed42_round5_partner0_belief():
    agent = _build_run("graded_betrayal.json", seed=42, num_rounds=5)
    np.testing.assert_allclose(agent.partner_beliefs[0], [0.0]*4, atol=1e-6)

# ... 5 more for both graded configs

# ===== assignment_mode='agent_choice' coverage =====

def test_h5_partner_selection_seed42_round5_choices():
    agent = _build_run("h5_partner_selection.json", seed=42, num_rounds=5)
    # capture the chosen partners over 5 rounds
    pass  # PLACEHOLDER (4 assertions)

# ===== xfail buckets — decisions #6 + #9 expected to change behavior =====

@pytest.mark.xfail(strict=True, reason="Decision #6 changes behavior on noisy configs")
def test_benchmark_noisy_seed42_round5_partner0_belief_under_old_semantics():
    agent = _build_run("benchmark_noisy.json", seed=42, num_rounds=5)
    np.testing.assert_allclose(agent.partner_beliefs[0], [0.0]*4, atol=1e-6)  # OLD value

# ... 2 more for noise

@pytest.mark.xfail(strict=True, reason="Decision #9 changes behavior on learning configs")
def test_h1_with_learn_A_seed42_round5_partner0_belief_under_old_semantics():
    agent = _build_run("h1_depth_affect_factorial.json", seed=42, num_rounds=5)  # config with learn_A=True
    np.testing.assert_allclose(agent.partner_beliefs[0], [0.0]*4, atol=1e-6)  # OLD value

# ... 2 more for learning
```

(Total: ~45 assertions per spec Section 6 / Section 5.)

- [ ] **Step 2: confirm scaffold imports cleanly**

Run: `pytest tests/test_behavioral_equivalence_pinpoint.py --collect-only -q`
Expected: ~45 test items collected, no collection errors.

### Task 5.2: capture pre-PR baselines for tier-1

**Files:**
- Modify: `tests/test_behavioral_equivalence_pinpoint.py`

- [ ] **Step 1: in a separate worktree, check out pre-PR SHA**

```bash
PRE_PR_SHA=$(cat /tmp/pre_pr_sha.txt)
git worktree add ../affect_aif-baseline-capture $PRE_PR_SHA
cd ../affect_aif-baseline-capture
```

- [ ] **Step 2: write a temporary capture script in the baseline worktree**

Create `tools/capture_pinpoint_baseline.py`:

```python
"""One-shot baseline capture for tier-1 pinpoint assertions.

Reads tests/test_behavioral_equivalence_pinpoint.py from the post-PR worktree
to identify the (config_name, seed, num_rounds, attribute) tuples; runs each
on the OLD code; prints the values with code patches the engineer can paste
back into the test file.
"""
import json
from pathlib import Path

# Hardcoded list mirroring the test scaffold in Phase 5 Task 5.1
SPECS = [
    ("smoke_test.json", 42, 5, "partner_beliefs", 0, "[0.31, 0.19, 0.27, 0.23]"),
    ("smoke_test.json", 42, 5, "partner_stance_beliefs", 0, "[0.X, 0.Y, 0.Z]"),
    # ... fill in the rest
]

# For each spec, build agent on OLD code, run rounds, print the value:
# from old code (this script lives in baseline worktree, so 'agent.*' imports work)
from agent.base import BaseAgent
from agent.model.trust_game import TrustGameModel  # OLD class
# ... build, run, print
```

NOTE: This is a one-time capture script. It does NOT need to be checked into the post-PR worktree. After the values are captured and pasted into `tests/test_behavioral_equivalence_pinpoint.py` in the cutover worktree, this file is discarded.

- [ ] **Step 3: run capture and paste values**

```bash
python tools/capture_pinpoint_baseline.py > /tmp/pinpoint_baselines.txt
cat /tmp/pinpoint_baselines.txt
```

Open `/tmp/pinpoint_baselines.txt` in an editor. For each PLACEHOLDER in `tests/test_behavioral_equivalence_pinpoint.py` (in the cutover worktree), copy the corresponding captured value and paste it.

- [ ] **Step 4: also capture the SHA**

In `tests/test_behavioral_equivalence_pinpoint.py`, replace `CAPTURED_FROM_SHA = "PRE_PR_SHA_HERE"` with the actual SHA from `/tmp/pre_pr_sha.txt`.

- [ ] **Step 5: clean up the baseline worktree**

```bash
cd ../affect_aif-restructure-pr2
git worktree remove ../affect_aif-baseline-capture
```

- [ ] **Step 6: run tier-1 tests on post-PR code**

Run: `pytest tests/test_behavioral_equivalence_pinpoint.py -v`
Expected: all non-xfail tests PASS at `atol=1e-6`. The 6 `xfail`-marked tests (3 for decision #6, 3 for decision #9) FAIL as expected → counted as PASS by pytest. If any `xfail` flips to `xpass`, that's a real bug — investigate.

### Task 5.3: write tier-2 aggregate sweep test

**Files:**
- Test: `tests/test_behavioral_equivalence_aggregates.py`
- Data: `tests/data/equivalence_aggregates.json`
- Script: `tests/data/regenerate_aggregates.py`

- [ ] **Step 1: write the aggregate computation**

Create `tests/data/regenerate_aggregates.py`:

```python
"""Compute aggregate equivalence metrics for every config in configs/
(except cvc). Run with the OLD code once on the pre-PR SHA to produce
tests/data/equivalence_aggregates.json. Run with the NEW code to verify
the sweep matches.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiment.config import ExperimentConfig
from experiment.factory import create_agent, create_env, create_model


def run_aggregate(config_path: Path, seed: int, num_rounds: int = 50) -> dict:
    cfg_dict = json.loads(config_path.read_text())
    cfg_dict["random_seed"] = seed
    cfg = ExperimentConfig(**cfg_dict)
    model = create_model(cfg)
    agent = create_agent(cfg, model)
    env = create_env(cfg, seed=seed)
    obs, info = env.reset()
    agent.reset()

    payoffs = []
    own_actions = []
    map_partner_types = []
    for _ in range(num_rounds):
        active = info.get("partner_idx", None)
        raw_action = agent.choose_partner_and_action(active_partner=active)
        obs, partner_action, payoff, info = env.step(raw_action)
        agent.observe_outcome(
            partner_idx=info["partner_idx"],
            observation=obs,
            action_taken=info["social_action"],
            partner_action=partner_action,
            payoff=payoff,
        )
        payoffs.append(float(payoff))
        own_actions.append(int(info["social_action"]))
        map_partner_types.append(int(np.argmax(agent.partner_beliefs[info["partner_idx"]])))

    cooperation_rate = sum(a == 0 for a in own_actions) / len(own_actions)
    final_belief_entropies = [-float(np.sum(b * np.log(b + 1e-16)))
                              for b in agent.partner_beliefs]
    has_affect = hasattr(agent, "get_betas")
    mean_final_beta = float(np.mean(agent.get_betas())) if has_affect else None
    switches = sum(1 for i in range(1, len(map_partner_types))
                   if map_partner_types[i] != map_partner_types[i-1])

    return {
        "mean_payoff": float(np.mean(payoffs)),
        "cooperation_rate": cooperation_rate,
        "mean_final_partner_belief_entropy": float(np.mean(final_belief_entropies)),
        "mean_final_beta": mean_final_beta,
        "total_partner_switches": switches,
    }


def main():
    out = {
        "captured_from_sha": "PRE_PR_SHA_HERE",  # fill in
        "captured_on": "2026-04-18",
        "configs": {},
        "post_pr_acceptance": {
            "no_learning_no_noise": {"atol": 1e-6, "behavior": "must match bit-identical"},
            "with_learning_or_noise": {
                "cooperation_rate_atol": 0.10,
                "mean_payoff_rtol": 0.15,
                "behavior": "direction + order of magnitude",
            },
        },
    }
    seeds = [42, 43, 44, 45, 46]
    for cfg_path in sorted(Path("configs").glob("*.json")):
        if "cvc" in cfg_path.name:
            continue
        out["configs"][cfg_path.name] = {}
        for seed in seeds:
            try:
                out["configs"][cfg_path.name][f"seed_{seed}"] = run_aggregate(cfg_path, seed)
            except Exception as e:
                out["configs"][cfg_path.name][f"seed_{seed}"] = {"error": str(e)}
    Path("tests/data/equivalence_aggregates.json").write_text(json.dumps(out, indent=2))
    print(f"wrote tests/data/equivalence_aggregates.json")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: capture aggregates on pre-PR SHA**

In the baseline worktree (re-create if removed), run:
```bash
cd ../affect_aif-baseline-capture  # if removed in Task 5.2 Step 5, recreate it
mkdir -p tests/data
python tests/data/regenerate_aggregates.py
cp tests/data/equivalence_aggregates.json /tmp/equivalence_aggregates.json
```

Then in the cutover worktree:
```bash
cd ../affect_aif-restructure-pr2
mkdir -p tests/data
cp /tmp/equivalence_aggregates.json tests/data/equivalence_aggregates.json
```

- [ ] **Step 3: replace `PRE_PR_SHA_HERE` placeholder in the JSON**

```bash
sed -i '' "s/PRE_PR_SHA_HERE/$(cat /tmp/pre_pr_sha.txt)/g" tests/data/equivalence_aggregates.json
```

- [ ] **Step 4: write the sweep test**

Create `tests/test_behavioral_equivalence_aggregates.py`:

```python
"""Tier-2 equivalence test: every config × 5 seeds, compare aggregates to
tests/data/equivalence_aggregates.json (captured on pre-PR SHA)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.data.regenerate_aggregates import run_aggregate

BASELINE = json.loads(Path("tests/data/equivalence_aggregates.json").read_text())
NO_LEARNING_KEYS = ("learn_A", "learn_B", "use_parameter_learning")


def _has_learning_or_noise(config_path: Path) -> bool:
    cfg = json.loads(config_path.read_text())
    if cfg.get("observation_noise", 0.0) > 0:
        return True
    return any(cfg.get(k, False) for k in NO_LEARNING_KEYS)


@pytest.mark.parametrize("config_name,seed_key",
                         [(c, s) for c in BASELINE["configs"]
                          for s in BASELINE["configs"][c]])
def test_aggregate_matches_baseline(config_name, seed_key):
    cfg_path = Path("configs") / config_name
    seed = int(seed_key.split("_")[1])
    expected = BASELINE["configs"][config_name][seed_key]
    if "error" in expected:
        pytest.skip(f"baseline errored: {expected['error']}")

    actual = run_aggregate(cfg_path, seed)

    if _has_learning_or_noise(cfg_path):
        # direction + order-of-magnitude
        assert abs(actual["cooperation_rate"] - expected["cooperation_rate"]) < 0.10, (
            f"{config_name} seed_{seed} cooperation_rate drifted: "
            f"{actual['cooperation_rate']} vs {expected['cooperation_rate']}"
        )
        # mean_payoff: relative tolerance 0.15
        if abs(expected["mean_payoff"]) > 1e-6:
            rel = abs(actual["mean_payoff"] - expected["mean_payoff"]) / abs(expected["mean_payoff"])
            assert rel < 0.15, f"mean_payoff rel drift {rel:.3f}"
    else:
        # bit-identical
        assert actual == expected, (
            f"{config_name} seed_{seed} aggregate mismatch:\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}"
        )
```

- [ ] **Step 5: run the sweep on post-PR code**

Run: `pytest tests/test_behavioral_equivalence_aggregates.py -v`
Expected: all PASS. `with_learning_or_noise` configs may show real drift (allowed within tolerances). `no_learning_no_noise` configs MUST be bit-identical — any failure here is a real bug.

### Task 5.4: write decision-#6 + #9 combined smoke regression test

**Files:**
- Test: `tests/test_decisions_combined_smoke.py`

- [ ] **Step 1: create file**

```python
"""End-to-end smoke regression for decisions #6 + #9 combined.

Confirms that a `learn_A=True, observation_noise=0.3, num_partners=4` config
runs to completion under the new semantics, finishes without errors, and
produces final beliefs that DIFFER from the pre-PR baseline (proving the
fix actually changed behavior).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from experiment.config import ExperimentConfig
from experiment.factory import create_agent, create_env, create_model

PRE_PR_BASELINE_PARTNER_BELIEFS = np.asarray([
    # PLACEHOLDER — captured from pre-PR SHA on benchmark_noisy.json with
    # learn_A=True override, seed 42, after 30 rounds. Fill in via Task 5.4
    # Step 2.
    [0.25, 0.25, 0.25, 0.25],
    [0.25, 0.25, 0.25, 0.25],
    [0.25, 0.25, 0.25, 0.25],
    [0.25, 0.25, 0.25, 0.25],
])


def test_combined_decisions_changed_behavior_on_noisy_learning_config():
    """Both bug-fix + per-partner learning should change final beliefs vs old."""
    cfg_dict = json.loads(Path("configs/benchmark_noisy.json").read_text())
    cfg_dict["random_seed"] = 42
    cfg_dict["use_parameter_learning"] = True  # force learning on
    cfg = ExperimentConfig(**cfg_dict)
    model = create_model(cfg)
    agent = create_agent(cfg, model)
    env = create_env(cfg, seed=42)
    obs, info = env.reset()
    agent.reset()
    for _ in range(30):
        active = info.get("partner_idx", None)
        raw_action = agent.choose_partner_and_action(active_partner=active)
        obs, partner_action, payoff, info = env.step(raw_action)
        agent.observe_outcome(
            partner_idx=info["partner_idx"],
            observation=obs,
            action_taken=info["social_action"],
            partner_action=partner_action,
            payoff=payoff,
        )

    new_beliefs = agent.partner_beliefs
    assert new_beliefs.shape == PRE_PR_BASELINE_PARTNER_BELIEFS.shape
    # Beliefs MUST differ from old code (otherwise both fixes silently failed)
    assert not np.allclose(new_beliefs, PRE_PR_BASELINE_PARTNER_BELIEFS, atol=1e-3), (
        "Combined regression: new beliefs match old beliefs — bug fix and/or "
        "per-partner learning changes did not actually take effect."
    )
```

- [ ] **Step 2: capture the pre-PR baseline value**

In the baseline worktree, run the equivalent of the test (without the assertion) to dump `agent.partner_beliefs`. Paste the captured value into `PRE_PR_BASELINE_PARTNER_BELIEFS`.

- [ ] **Step 3: run, expect PASS**

Run: `pytest tests/test_decisions_combined_smoke.py -v`
Expected: PASS (new beliefs differ from old).

### Task 5.5: update `STATE.md` blockers list

**Files:**
- Modify: `conductor/STATE.md`

- [ ] **Step 1: identify configs requiring rerun**

```bash
python -c "
import json, pathlib
for p in sorted(pathlib.Path('configs').glob('*.json')):
    if 'cvc' in p.name: continue
    cfg = json.loads(p.read_text())
    flags = []
    if cfg.get('observation_noise', 0) > 0: flags.append('noise>0')
    if cfg.get('learn_A', False): flags.append('learn_A')
    if cfg.get('learn_B', False): flags.append('learn_B')
    if cfg.get('use_parameter_learning', False): flags.append('param_learning')
    if flags: print(f'{p.name}: {flags}')
"
```

- [ ] **Step 2: add a section to `conductor/STATE.md`**

Append a new section under blockers/known-issues:

```markdown
## post-restructure rerun queue (decisions #6, #9)

The B+A restructure introduced two intentional behavior changes:
- decision #6: `infer_joint_posterior` now uses both observation modalities
- decision #9: Dirichlet learning is now per-partner private

Configs affected and requiring rerun with new acceptance criteria
(direction + order-of-magnitude, not bit-identical):

<paste the list from Step 1 here>

Rerun protocol: bump `num_replications` to 50, regenerate H5 artifacts,
update analysis scripts to use new partner-belief shape (per-partner pA
gives slightly different posteriors than the old shared-table version).
```

### Task 5.6: write CHANGELOG entry

**Files:**
- Modify: `CHANGELOG.md` (create if missing)

- [ ] **Step 1: prepend a new entry**

```markdown
## [unreleased] — 2026-04-XX (B+A restructure)

### Breaking changes

- `agent/` package removed entirely. Imports must be updated:
  - `from agent.base import BaseAgent` → `from trust import TrustGameAgent`
  - `from agent.affective import AffectiveAgent` → `from trust import AffectiveAgent`
  - `from agent.lesioned import LesionedAgent` → `from trust import LesionedAgent`
  - `from agent.model.trust_game import TrustGameModel` → `from trust.model import TrustGameModel`
  - `from agent.affect.beta import DiscreteBetaState` → `from aif.affect.beta import DiscreteBetaState`
  - `from agent.inference.X import Y` → `from aif.X import Y` (X ∈ {maths, utils, backend, efe, runtime, policies, learning})
- `GradedTrustGameModel` deleted. Use `TrustGameModel({"payoff_mode": "graded", ...})`.
- `_BaseTrustGameModel` deleted (was internal anyway).
- Config keys removed: `variant` (use `assignment_mode`), `model_class` (no longer needed).
- New required config key: `payoff_mode` ∈ {"binary", "graded"}.
- `DiscreteBetaState` API: `partner` → `entity` rename. `num_partners` → `num_entities`, `partner_idx` → `entity_idx`.

### Behavior changes (intentional, per design spec decisions)

- decision #6: `TrustGameModel.infer_joint_posterior` now multiplies through both observation modalities. Configs with `observation_noise > 0` will produce different posteriors.
- decision #9: Dirichlet learning is per-partner private. Each per-partner `aif.Agent` holds its own `pA`/`pB`. Configs with `learn_A`, `learn_B`, or `use_parameter_learning` will produce different beliefs over multi-partner trajectories.

### New packages

- `aif/`: generic active-inference primitives (Agent dataclass + free functions for inference/learning/EFE).
- `trust/`: project package (TrustGameModel + TrustGameAgent + AffectiveAgent + LesionedAgent + rollout helpers).

### Spec

`docs/superpowers/specs/2026-04-18-aif-extraction-design.md`
```

### Task 5.7: commit 5 + open PR-2

- [ ] **Step 1: full test suite**

Run: `pytest tests/ -v`
Expected: 0 failures (xfails counted as expected). Note the test count and runtime; should be ~2x larger than pre-PR baseline.

- [ ] **Step 2: commit**

```bash
git add tests/test_behavioral_equivalence_pinpoint.py \
        tests/test_behavioral_equivalence_aggregates.py \
        tests/data/equivalence_aggregates.json \
        tests/data/regenerate_aggregates.py \
        tests/test_decisions_combined_smoke.py \
        conductor/STATE.md CHANGELOG.md
git commit -m "test(aif,trust): equivalence + regression test suite for B+A restructure

- tier-1: ~45 hand-written assert_allclose pinpoint checks against
  pre-PR baselines. xfail-marked checks for decisions #6 and #9.
- tier-2: aggregate sweep over every config × 5 seeds, compares
  cooperation_rate, mean_payoff, belief entropy, beta, partner switches
  against checked-in JSON baseline (captured from pre-PR SHA).
- regression smoke: confirms decisions #6 + #9 actually change behavior
  on the noisy+learning config.
- STATE.md updated with post-restructure rerun queue.
- CHANGELOG entry summarizing all breaking changes and behavior changes.

No source code changes in this commit — verification only.

Spec: docs/superpowers/specs/2026-04-18-aif-extraction-design.md"
```

- [ ] **Step 3: push and open PR-2**

```bash
git push -u origin restructure/aif-cutover
gh pr create --title "restructure(PR-2): cutover — agent/ → aif/ + trust/" \
  --body "$(cat <<'EOF'
## Summary

PR-2 of two for the `aif/` extraction. This PR is the real cutover: it deletes `agent/` entirely and replaces it with `aif/` (generic POMDP runtime) and `trust/` (project package). Two intentional behavior changes land here per the design spec: decision #6 (payoff modality used in belief updates) and decision #9 (per-partner Dirichlet learning).

## Commits in this PR

1. `feat(aif): add Agent dataclass, inference free fns, affect/beta with entity rename` — adds the new abstractions, repoints `agent/affective.py` to `aif.affect.beta`.
2. `feat(trust): canonical TrustGameModel + payoff-drop bug fix` — adds `trust/model.py` with `payoff_mode` switch and the bug fix; deletes `agent/model/`.
3. `feat(trust): TrustGameAgent with per-partner aif.Agents; delete agent/` — adds `trust/{agent,affective,lesioned,rollout}.py`, deletes `agent/` entirely, updates 13 test files.
4. `test(aif,trust): equivalence + regression test suite` — tier-1 pinpoint + tier-2 aggregate equivalence checks + STATE.md update + CHANGELOG.

Each commit is independently CI-green.

## Reviewer focus

Per the design spec Section 5 callout, mechanical edits dominate the diff. Focus review on:
- `trust/model.py` — constructor + bug fix
- `trust/agent.py` — per-partner architecture
- `trust/rollout.py` — per-partner planner signature
- `tests/test_behavioral_equivalence_pinpoint.py` — captured baselines

The rest can be eyeballed.

## Test plan
- [x] `pytest tests/ -v` — full suite passes including ~45 new pinpoint tests + aggregate sweep
- [x] `xfail`-marked tests fail as expected (decisions #6, #9 explicitly change behavior)
- [x] `grep -rn 'from agent\.' --include='*.py' . | grep -v archive/` — zero hits
- [x] `tests/data/equivalence_aggregates.json` matches the post-PR sweep within tolerances

## Spec
`docs/superpowers/specs/2026-04-18-aif-extraction-design.md`
EOF
)"
```

Expected: PR opened, URL printed.

---

## Self-review notes

- **Spec coverage:** every decision (1–10) maps to at least one task. Decisions 1, 2, 7 are repo-layout/naming and land in Phase 0–4 implicitly. Decisions 3, 4, 5, 6, 9 each have explicit implementation tasks. Decision 8 (no back-compat) is enforced via the constructor-level `ValueError` checks (Task 3.4) and the test in Task 3.2. Decision 10 (two PRs) is the phase boundary itself.
- **Multi-focal compatibility appendix:** Task 4.3 (`TrustGameAgent`) preserves the contract listed in the appendix. The 30-min smoke test the appendix recommends (instantiating two `TrustGameAgent`s and running a round of mutual selection) is captured as a follow-up in the spec, not in this plan — it belongs to sub-project F.
- **Placeholders deliberately left:** the tier-1 baseline values in Task 5.1 and the combined smoke baseline in Task 5.4 are explicitly "PLACEHOLDER — capture in next step" and are filled in by Tasks 5.2 / 5.4 Step 2 respectively. These are NOT spec gaps; they're values that can only be captured at execution time from the pre-PR SHA.
- **Andrew's notebook test (Task 2.12):** intentionally open-ended on the A/B/C/D values because they require notebook inspection. Step 1 specifies the exact procedure.
- **`infer_states` multi-factor marginalization:** flagged in Task 2.4 Step 1 as the most fragile new code; recommended to port from existing `_BaseTrustGameModel.infer_joint_posterior` math (without the bug). The test in Task 2.4 Step 4 cross-checks against the live trust-game model.
- **`decision_step_trust_game` per-partner refactor:** the most subtle code change in Phase 4. Task 4.2 Step 4 deliberately walks through the rewrite mechanically rather than embedding the full new function body — the existing function is too long and the change is line-by-line indexing.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-18-aif-extraction-plan.md`.**

Two execution options:

1. **Subagent-driven (recommended)** — dispatch a fresh subagent per task using `superpowers:subagent-driven-development`. Review between tasks; fast iteration. Each task in this plan is sized to be independently completable by a fresh agent reading only that task. **Recommended for this plan because:** the work spans ~5 commits and ~57 files; per-task subagent dispatch keeps each agent's context focused on one bite-sized change.

2. **Inline execution** — execute tasks in this session using `superpowers:executing-plans`. Batch execution with checkpoints for review.

**Which approach?** (After your answer, I'll either start dispatching subagents or hand off to executing-plans.)
