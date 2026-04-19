# multi-focal-agent runtime — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** add a multi-focal trust-game runtime where M `TrustGameAgent` instances play the trust game with each other (instead of one focal AIF agent + scripted partners), as a purely additive extension on top of the merged B+A codebase. No changes to `aif/` or `trust/` packages.

**Architecture:** new `experiment/multi_focal_runner.py` drives M agents through turn-taking rounds (per `pomdp_spec.md` §12). New `experiment/joint_resolution.py` resolves a pair's actions into payoffs without going through `env/trust_game.py` (the env's only role — simulating scripted partners — is irrelevant under multi-focal). New `experiment/multi_focal_config.py` parses heterogeneous `agents: [...]` config schema. `experiment/factory.py` gains a `create_agents_from_multi_focal_config()` helper. Four new configs ship for sub-project D's review.

**Tech Stack:** Python 3.11, NumPy, pytest. No JAX dependence in the new code (delegated to `aif/`).

**Spec reference:** [`docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md`](../specs/2026-04-18-multi-focal-runtime-design.md). Decision numbers (F1–F12) in this plan refer to that spec's decision log.

**Branch convention:** single PR — `feature/multi-focal-runtime` — branched from `main` after B+A is merged. CI green at every commit.

---

## Overview of phases

| phase | what it produces | est. duration |
|---|---|---|
| 0 | worktree + branch setup, baseline confirmation | 15 min |
| 1 | `experiment/joint_resolution.py` + tests | 1 h |
| 2 | `experiment/multi_focal_config.py` + factory extension + tests | 1.5 h |
| 3 | `experiment/multi_focal_runner.py` skeleton + index mapping + tests | 1.5 h |
| 4 | `multi_focal_runner.py` round loop + integration with config + tests | 2 h |
| 5 | 4 new configs + smoke run | 30 min |
| 6 | deterministic regression test (pinned seeds) | 1.5 h |
| 7 | emergent-dynamics smoke tests (statistical) | 2 h |
| 8 | doc breadcrumbs + AGENTS.md drive-by + STATE.md update | 30 min |
| **total** | | **~10 h** |

---

## Phase 0: setup

### Task 0.1: create worktree and branch

**Files:**
- Create: worktree `../affect_aif-multi-focal`
- Branch: `feature/multi-focal-runtime`

- [ ] **Step 1: create worktree from `main`**

```bash
cd /Users/harshilshah/Desktop/Active\ Inference/affect_aif
git fetch origin
git worktree add ../affect_aif-multi-focal -b feature/multi-focal-runtime origin/main
cd ../affect_aif-multi-focal
```

Expected: worktree created at `../affect_aif-multi-focal` on branch `feature/multi-focal-runtime`.

- [ ] **Step 2: confirm baseline is green**

Run: `pytest tests/ -q`
Expected: all tests pass (matches B+A baseline). If not, fix before continuing — multi-focal must layer onto a green tree.

- [ ] **Step 3: confirm `aif/` and `trust/` are present**

Run: `python -c "import aif; from trust import TrustGameAgent, AffectiveAgent, LesionedAgent, TrustGameModel; print('ok')"`
Expected: prints `ok`. If `ImportError`, B+A has not landed; stop and merge B+A first.

---

## Phase 1: joint resolution module

**Goal:** ship the smallest reusable piece — `joint_resolve(my_action, partner_action, model)` — and lock its semantics with tests before anything else depends on it.

### Task 1.1: create `experiment/joint_resolution.py`

**Files:**
- Create: `experiment/joint_resolution.py`

- [ ] **Step 1: write `joint_resolve` per spec Section 3**

```python
"""Joint action resolution for multi-focal trust-game pairs."""
from __future__ import annotations
import numpy as np
from trust.model import TrustGameModel

def joint_resolve(my_action: int, partner_action: int, model: TrustGameModel) -> tuple[int, float]:
    """Resolve a pair's actions into (payoff_obs_idx, payoff_value) for the agent
    whose action is `my_action`. Symmetric: payoff for the other side is computed
    by a second call with the arguments swapped against the partner's model.

    Returns:
        payoff_obs_idx: index into model.payoff_levels (used as the second
                        observation modality in observe_outcome).
        payoff_value:   raw payoff (used for logging / metrics).
    """
    payoff_value = float(model.payoff_matrix[int(my_action), int(partner_action), 0])
    levels = np.asarray(model.payoff_levels, dtype=float)
    diffs = np.abs(levels - payoff_value)
    obs_idx = int(np.argmin(diffs))
    if diffs[obs_idx] > 1e-9:
        raise ValueError(
            f"payoff_value={payoff_value} not found in model.payoff_levels={levels.tolist()}; "
            "model construction is inconsistent with the actions taken."
        )
    return obs_idx, payoff_value
```

- [ ] **Step 2: confirm import is clean**

Run: `python -c "from experiment.joint_resolution import joint_resolve; print(joint_resolve.__doc__[:60])"`
Expected: prints first 60 chars of the docstring. No import error.

### Task 1.2: tests for joint resolution

**Files:**
- Create: `tests/test_joint_resolution.py`

- [ ] **Step 1: write the test file**

```python
"""Unit tests for joint action resolution (multi-focal F)."""
from __future__ import annotations
import numpy as np
import pytest
from experiment.joint_resolution import joint_resolve
from trust.model import TrustGameModel

@pytest.fixture
def binary_model():
    return TrustGameModel({
        "payoff_mode": "binary",
        "num_partners": 1,
        "mutual_coop":   (3.0, 3.0),
        "sucker":        (-1.0, 5.0),
        "temptation":    (5.0, -1.0),
        "mutual_defect": (1.0, 1.0),
    })

@pytest.fixture
def graded_model():
    return TrustGameModel({
        "payoff_mode": "graded",
        "num_partners": 1,
        "num_investment_levels": 6,
        "endowment": 10.0,
        "multiplier": 3.0,
    })

# action index convention: 0 = cooperate, 1 = defect (binary)

def test_binary_mutual_cooperate_returns_3(binary_model):
    obs_idx, payoff = joint_resolve(my_action=0, partner_action=0, model=binary_model)
    assert payoff == pytest.approx(3.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(3.0)

def test_binary_sucker_returns_minus_1(binary_model):
    obs_idx, payoff = joint_resolve(my_action=0, partner_action=1, model=binary_model)
    assert payoff == pytest.approx(-1.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(-1.0)

def test_binary_temptation_returns_5(binary_model):
    obs_idx, payoff = joint_resolve(my_action=1, partner_action=0, model=binary_model)
    assert payoff == pytest.approx(5.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(5.0)

def test_binary_mutual_defect_returns_1(binary_model):
    obs_idx, payoff = joint_resolve(my_action=1, partner_action=1, model=binary_model)
    assert payoff == pytest.approx(1.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(1.0)

def test_graded_symmetric_max_invest(graded_model):
    """Both invest max → both should receive a known payoff in payoff_levels."""
    max_level = graded_model.num_social_actions - 1
    obs_idx, payoff = joint_resolve(my_action=max_level, partner_action=max_level, model=graded_model)
    assert obs_idx >= 0
    assert payoff in graded_model.payoff_levels or any(
        abs(l - payoff) < 1e-9 for l in graded_model.payoff_levels
    )

def test_graded_zero_zero(graded_model):
    """Both invest 0 → both get endowment."""
    obs_idx, payoff = joint_resolve(my_action=0, partner_action=0, model=graded_model)
    assert payoff == pytest.approx(10.0)

def test_round_trip_swap_for_partner(binary_model):
    """Swap (my, partner) to compute the partner's payoff."""
    obs_my, p_my = joint_resolve(my_action=0, partner_action=1, model=binary_model)
    obs_par, p_par = joint_resolve(my_action=1, partner_action=0, model=binary_model)
    assert p_my == pytest.approx(-1.0)   # I cooperated, partner defected → sucker
    assert p_par == pytest.approx(5.0)   # partner defected, I cooperated → temptation
```

- [ ] **Step 2: run the tests**

Run: `pytest tests/test_joint_resolution.py -v`
Expected: 7 tests pass.

- [ ] **Step 3: commit**

```bash
git add experiment/joint_resolution.py tests/test_joint_resolution.py
git commit -m "feat(multifocal): joint action resolution module + tests"
```

---

## Phase 2: config schema + factory extension

**Goal:** parse heterogeneous `agents: [...]` configs into a typed shape, and extend `experiment/factory.py` with a builder that constructs M `TrustGameAgent` instances from the spec.

### Task 2.1: create `experiment/multi_focal_config.py`

**Files:**
- Create: `experiment/multi_focal_config.py`

- [ ] **Step 1: write the dataclass + loader per spec Section 4**

```python
"""Config schema for multi-focal trust-game experiments."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

_VALID_ROUND_MODES = {"turn_taking"}                       # F1: extension seam
_VALID_FOCAL_SELECTIONS = {"round_robin", "random"}        # F2
_VALID_ASSIGNMENT_MODES = {"random", "agent_choice"}       # F3
_VALID_AGENT_KINDS = {"base", "affective", "lesioned"}     # F11
_VALID_PAYOFF_MODES = {"binary", "graded"}

@dataclass
class MultiFocalConfig:
    experiment_name: str
    round_mode: str = "turn_taking"
    focal_selection: str = "round_robin"
    assignment_mode: str = "random"
    num_rounds: int = 200
    num_replications: int = 50
    random_seed: int = 42
    payoff_mode: str = "binary"
    agents: list[dict] = field(default_factory=list)
    logging: dict = field(default_factory=dict)

    def num_agents(self) -> int:
        return len(self.agents)

    @classmethod
    def from_dict(cls, raw: dict) -> "MultiFocalConfig":
        if "experiment_name" not in raw:
            raise ValueError("multi-focal config requires 'experiment_name'")
        if "agents" not in raw or not isinstance(raw["agents"], list):
            raise ValueError("multi-focal config requires 'agents' (list of agent specs)")
        if len(raw["agents"]) < 2:
            raise ValueError(f"multi-focal requires >= 2 agents; got {len(raw['agents'])}")
        cfg = cls(
            experiment_name=str(raw["experiment_name"]),
            round_mode=str(raw.get("round_mode", "turn_taking")),
            focal_selection=str(raw.get("focal_selection", "round_robin")),
            assignment_mode=str(raw.get("assignment_mode", "random")),
            num_rounds=int(raw.get("num_rounds", 200)),
            num_replications=int(raw.get("num_replications", 50)),
            random_seed=int(raw.get("random_seed", 42)),
            payoff_mode=str(raw.get("payoff_mode", "binary")),
            agents=list(raw["agents"]),
            logging=dict(raw.get("logging", {})),
        )
        cfg._validate()
        return cfg

    def _validate(self) -> None:
        if self.round_mode not in _VALID_ROUND_MODES:
            raise ValueError(
                f"round_mode={self.round_mode!r} not in {sorted(_VALID_ROUND_MODES)}; "
                "additional modes (e.g., all_pairs) are reserved for future work."
            )
        if self.focal_selection not in _VALID_FOCAL_SELECTIONS:
            raise ValueError(f"focal_selection={self.focal_selection!r} not in {sorted(_VALID_FOCAL_SELECTIONS)}")
        if self.assignment_mode not in _VALID_ASSIGNMENT_MODES:
            raise ValueError(f"assignment_mode={self.assignment_mode!r} not in {sorted(_VALID_ASSIGNMENT_MODES)}")
        if self.payoff_mode not in _VALID_PAYOFF_MODES:
            raise ValueError(f"payoff_mode={self.payoff_mode!r} not in {sorted(_VALID_PAYOFF_MODES)}")
        for i, spec in enumerate(self.agents):
            if not isinstance(spec, dict):
                raise ValueError(f"agents[{i}] must be a dict; got {type(spec).__name__}")
            kind = spec.get("kind")
            if kind not in _VALID_AGENT_KINDS:
                raise ValueError(f"agents[{i}]['kind']={kind!r} not in {sorted(_VALID_AGENT_KINDS)}")
            overrides = spec.get("model_overrides", {})
            if not isinstance(overrides, dict):
                raise ValueError(f"agents[{i}]['model_overrides'] must be a dict")
            if "payoff_mode" in overrides and overrides["payoff_mode"] != self.payoff_mode:
                raise ValueError(
                    f"agents[{i}]['model_overrides']['payoff_mode'] = {overrides['payoff_mode']!r} "
                    f"contradicts top-level payoff_mode={self.payoff_mode!r} (F8/F10 violation)."
                )
```

- [ ] **Step 2: smoke import**

Run: `python -c "from experiment.multi_focal_config import MultiFocalConfig; print(MultiFocalConfig.from_dict({'experiment_name': 'x', 'agents': [{'kind':'base'},{'kind':'base'}]}).num_agents())"`
Expected: prints `2`.

### Task 2.2: extend `experiment/factory.py`

**Files:**
- Edit: `experiment/factory.py`

- [ ] **Step 1: add `create_agents_from_multi_focal_config`** at the bottom of `experiment/factory.py`

```python
def create_agents_from_multi_focal_config(
    config: "MultiFocalConfig",
    seed: int,
) -> list[TrustGameAgent]:
    """Build M agents from a multi-focal config (spec Section 2 + 4).

    Each agent gets its own TrustGameModel built from population payoff_mode +
    per-agent model_overrides. num_partners is forced to M-1 (no self-modeling, F5).
    """
    from trust.model import TrustGameModel as _Model
    from trust import AffectiveAgent as _Aff, LesionedAgent as _Les, TrustGameAgent as _Base

    M = config.num_agents()
    agents: list[TrustGameAgent] = []
    for i, spec in enumerate(config.agents):
        model_cfg: dict = {
            "payoff_mode": config.payoff_mode,
            "num_partners": M - 1,
            "assignment_mode": config.assignment_mode,
        }
        model_cfg.update(spec.get("model_overrides", {}))
        # population-wide constraints (F8): payoff_mode + num_social_actions
        # are enforced at config-load time via _validate; double-check here for paranoia.
        model = _Model(model_cfg)

        kind = spec["kind"]
        agent_kwargs = {k: v for k, v in spec.items()
                        if k not in {"kind", "model_overrides", "_label"}}
        if kind == "base":
            agent = _Base(model, seed=seed + i, **agent_kwargs)
        elif kind == "affective":
            agent = _Aff(model, seed=seed + i, **agent_kwargs)
        elif kind == "lesioned":
            agent = _Les(model, seed=seed + i, **agent_kwargs)
        else:
            raise ValueError(f"unknown agent kind={kind!r}")
        # logging label (F9) — explicit _label overrides kind-derived default
        agent._kind_label = spec.get("_label", kind)
        agents.append(agent)
    return agents
```

- [ ] **Step 2: confirm import**

Run: `python -c "from experiment.factory import create_agents_from_multi_focal_config; print('ok')"`
Expected: prints `ok`.

### Task 2.3: tests for config + factory

**Files:**
- Create: `tests/test_multi_focal_config.py`

- [ ] **Step 1: write the test file**

```python
"""Tests for multi-focal config parsing + agent factory (F)."""
from __future__ import annotations
import pytest
from experiment.multi_focal_config import MultiFocalConfig
from experiment.factory import create_agents_from_multi_focal_config

_GOOD = {
    "experiment_name": "x",
    "agents": [{"kind": "base"}, {"kind": "affective"}, {"kind": "lesioned", "lesion_mode": "decouple"}],
}

def test_good_config_parses():
    cfg = MultiFocalConfig.from_dict(_GOOD)
    assert cfg.num_agents() == 3
    assert cfg.payoff_mode == "binary"
    assert cfg.round_mode == "turn_taking"

def test_unknown_kind_raises():
    bad = dict(_GOOD); bad["agents"] = [{"kind": "ghost"}, {"kind": "base"}]
    with pytest.raises(ValueError, match="kind"):
        MultiFocalConfig.from_dict(bad)

def test_too_few_agents_raises():
    bad = dict(_GOOD); bad["agents"] = [{"kind": "base"}]
    with pytest.raises(ValueError, match=">= 2"):
        MultiFocalConfig.from_dict(bad)

def test_unknown_round_mode_raises():
    bad = dict(_GOOD); bad["round_mode"] = "all_pairs"
    with pytest.raises(ValueError, match="all_pairs"):
        MultiFocalConfig.from_dict(bad)

def test_payoff_mode_mismatch_in_overrides_raises():
    bad = dict(_GOOD)
    bad["agents"] = [
        {"kind": "base", "model_overrides": {"payoff_mode": "graded"}},
        {"kind": "base"},
    ]
    with pytest.raises(ValueError, match="payoff_mode"):
        MultiFocalConfig.from_dict(bad)

def test_factory_builds_M_agents_with_correct_num_partners():
    cfg = MultiFocalConfig.from_dict(_GOOD)
    agents = create_agents_from_multi_focal_config(cfg, seed=0)
    assert len(agents) == 3
    for a in agents:
        assert a.num_partners == 2          # M - 1 (F5)
    # kind labels propagate
    assert agents[0]._kind_label == "base"
    assert agents[1]._kind_label == "affective"
    assert agents[2]._kind_label == "lesioned"

def test_factory_label_override():
    cfg = MultiFocalConfig.from_dict({
        "experiment_name": "x",
        "agents": [
            {"kind": "affective", "_label": "healthy"},
            {"kind": "affective", "_label": "alexithymia", "alpha_charge": 0.5},
        ],
    })
    agents = create_agents_from_multi_focal_config(cfg, seed=0)
    assert agents[0]._kind_label == "healthy"
    assert agents[1]._kind_label == "alexithymia"
```

- [ ] **Step 2: run the tests**

Run: `pytest tests/test_multi_focal_config.py -v`
Expected: 7 tests pass.

- [ ] **Step 3: commit**

```bash
git add experiment/multi_focal_config.py experiment/factory.py tests/test_multi_focal_config.py
git commit -m "feat(multifocal): heterogeneous agents config + factory"
```

---

## Phase 3: runner skeleton + index mapping

**Goal:** ship the runner class shell, the global↔local index mapping, the `RoundProtocol` extension seam, and the `_validate_population` constraint check. Defer the round-loop body to Phase 4.

### Task 3.1: create `experiment/multi_focal_runner.py` (skeleton)

**Files:**
- Create: `experiment/multi_focal_runner.py`

- [ ] **Step 1: write the module skeleton per spec Section 2**

```python
"""Multi-focal-agent runtime for the trust game (sub-project F)."""
from __future__ import annotations
from typing import Protocol
import numpy as np
from trust import TrustGameAgent
from trust.rollout import decode_raw_action_to_partner_and_social
from experiment.joint_resolution import joint_resolve
from experiment.multi_focal_config import MultiFocalConfig

# ---------------------------------------------------------------------------
# index mapping (F5)
# ---------------------------------------------------------------------------

def _local_partner_idx(focal_global: int, other_global: int) -> int:
    """Global-to-local mapping. For focal F, partner P maps to local idx P if P<F else P-1."""
    if other_global == focal_global:
        raise ValueError("self-modeling not supported (F5)")
    return other_global if other_global < focal_global else other_global - 1

def _global_partner_idx(focal_global: int, local: int, M: int) -> int:
    """Inverse of _local_partner_idx."""
    return local if local < focal_global else local + 1

# ---------------------------------------------------------------------------
# round-protocol extension seam (F1)
# ---------------------------------------------------------------------------

class RoundProtocol(Protocol):
    def select_pairs(self, round_idx: int, agents: list[TrustGameAgent], rng: np.random.Generator) -> list[tuple[int, int | None]]:
        """Return a list of (focal_global_idx, engaged_global_idx_or_None) pairs.
        For turn-taking, len()==1 and engaged is None (resolved later in the runner)."""
        ...

class TurnTakingProtocol:
    def __init__(self, focal_selection: str):
        if focal_selection not in {"round_robin", "random"}:
            raise ValueError(f"unknown focal_selection={focal_selection!r}")
        self.focal_selection = focal_selection

    def select_pairs(self, round_idx, agents, rng):
        M = len(agents)
        if self.focal_selection == "round_robin":
            focal = round_idx % M
        else:                                     # "random"
            focal = int(rng.integers(M))
        return [(focal, None)]

_PROTOCOLS: dict[str, type] = {"turn_taking": TurnTakingProtocol}

# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------

class MultiFocalRunner:
    """Drive M TrustGameAgents through a multi-focal trust game."""

    def __init__(self, config: MultiFocalConfig, agents: list[TrustGameAgent], rng: np.random.Generator):
        self.config = config
        self.agents = list(agents)
        self.M = len(agents)
        self.rng = rng
        self.protocol = _PROTOCOLS[config.round_mode](focal_selection=config.focal_selection)
        self._validate_population()

    def _validate_population(self) -> None:
        if self.M < 2:
            raise ValueError(f"multi-focal requires >= 2 agents; got {self.M}")
        payoff_modes = {a.model.payoff_mode for a in self.agents}
        if len(payoff_modes) > 1:
            raise ValueError(f"all agents must share payoff_mode; got {payoff_modes}")
        nsas = {a.num_social_actions for a in self.agents}
        if len(nsas) > 1:
            raise ValueError(f"all agents must share num_social_actions; got {nsas}")
        for i, a in enumerate(self.agents):
            if a.num_partners != self.M - 1:
                raise ValueError(
                    f"agent[{i}] has num_partners={a.num_partners}; "
                    f"expected M-1={self.M - 1} (F5: no self-modeling)"
                )

    def run(self) -> list[dict]:
        """Run num_rounds. Returns long-format rows (F9). Round loop wired in Phase 4."""
        raise NotImplementedError("Round loop is wired in Phase 4")
```

### Task 3.2: tests for index mapping + runner construction

**Files:**
- Create: `tests/test_multi_focal_index_mapping.py`
- Create: `tests/test_multi_focal_runner_construction.py`

- [ ] **Step 1: write `tests/test_multi_focal_index_mapping.py`**

```python
"""Round-trip tests for global<->local partner index mapping (F5)."""
from __future__ import annotations
import pytest
from experiment.multi_focal_runner import _local_partner_idx, _global_partner_idx

@pytest.mark.parametrize("M", [2, 3, 4, 5, 8])
def test_round_trip_global_to_local_to_global(M):
    for g in range(M):
        for o in range(M):
            if o == g:
                continue
            local = _local_partner_idx(g, o)
            assert 0 <= local < M - 1
            assert _global_partner_idx(g, local, M) == o

@pytest.mark.parametrize("M", [2, 3, 4, 8])
def test_round_trip_local_to_global_to_local(M):
    for g in range(M):
        for l in range(M - 1):
            o = _global_partner_idx(g, l, M)
            assert o != g
            assert _local_partner_idx(g, o) == l

def test_self_modeling_local_raises():
    with pytest.raises(ValueError, match="self-modeling"):
        _local_partner_idx(2, 2)

def test_M2_smallest_case():
    assert _local_partner_idx(0, 1) == 0
    assert _local_partner_idx(1, 0) == 0
    assert _global_partner_idx(0, 0, 2) == 1
    assert _global_partner_idx(1, 0, 2) == 0
```

- [ ] **Step 2: write `tests/test_multi_focal_runner_construction.py`**

```python
"""Construction-time validation of the multi-focal runner (F8, F10, F5)."""
from __future__ import annotations
import numpy as np
import pytest
from experiment.multi_focal_runner import MultiFocalRunner
from experiment.multi_focal_config import MultiFocalConfig
from experiment.factory import create_agents_from_multi_focal_config

def _make_runner(agents_spec, payoff_mode="binary"):
    cfg = MultiFocalConfig.from_dict({"experiment_name": "x", "payoff_mode": payoff_mode, "agents": agents_spec})
    agents = create_agents_from_multi_focal_config(cfg, seed=0)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(0))

def test_construction_succeeds_with_2_agents():
    r = _make_runner([{"kind": "base"}, {"kind": "base"}])
    assert r.M == 2

def test_construction_succeeds_with_4_agents():
    r = _make_runner([{"kind": "base"}] * 4)
    assert r.M == 4
    for a in r.agents:
        assert a.num_partners == 3

def test_unknown_round_mode_rejected_at_config():
    # round_mode validation lives in MultiFocalConfig; verify it propagates
    with pytest.raises(ValueError, match="all_pairs"):
        MultiFocalConfig.from_dict({
            "experiment_name": "x",
            "round_mode": "all_pairs",
            "agents": [{"kind": "base"}, {"kind": "base"}],
        })

def test_run_raises_NotImplementedError_in_phase_3():
    """Phase 3 ships skeleton only; round loop arrives in Phase 4."""
    r = _make_runner([{"kind": "base"}, {"kind": "base"}])
    with pytest.raises(NotImplementedError):
        r.run()
```

- [ ] **Step 3: run tests**

Run: `pytest tests/test_multi_focal_index_mapping.py tests/test_multi_focal_runner_construction.py -v`
Expected: ~10 tests pass.

- [ ] **Step 4: commit**

```bash
git add experiment/multi_focal_runner.py tests/test_multi_focal_index_mapping.py tests/test_multi_focal_runner_construction.py
git commit -m "feat(multifocal): runner skeleton + index mapping + protocol seam"
```

---

## Phase 4: round loop + integration

**Goal:** wire the round-loop body. After this phase, `MultiFocalRunner.run()` produces real results.

### Task 4.1: implement `_play_one_pair` and `run`

**Files:**
- Edit: `experiment/multi_focal_runner.py`

- [ ] **Step 1: replace the `run` stub with the full implementation**

Add after `_validate_population`:

```python
    def run(self) -> list[dict]:
        """Run num_rounds. Returns long-format rows (F9): one row per (round, agent_in_pair)."""
        rows: list[dict] = []
        for t in range(self.config.num_rounds):
            for (focal_g, _placeholder) in self.protocol.select_pairs(t, self.agents, self.rng):
                rows.extend(self._play_one_pair(t, focal_g))
        return rows

    def _play_one_pair(self, t: int, focal_g: int) -> list[dict]:
        focal = self.agents[focal_g]

        # ---- step 2 + 3: select engaged partner + commit focal action ----
        if self.config.assignment_mode == "agent_choice":
            focal.choose_partner_and_action()
            local_p, focal_action = decode_raw_action_to_partner_and_social(
                raw_action=focal.last_raw_action,
                active_partner=0,
                assignment_mode_code=1,
                factorized_policies=focal.factorized_policies,
                num_social_actions=focal.num_social_actions,
                num_partners=focal.num_partners,
            )
            engaged_g = _global_partner_idx(focal_g, local_p, self.M)
        else:                                                      # "random"
            other_globals = [g for g in range(self.M) if g != focal_g]
            engaged_g = int(self.rng.choice(other_globals))
            local_p = _local_partner_idx(focal_g, engaged_g)
            focal.choose_partner_and_action(active_partner=local_p)
            _, focal_action = decode_raw_action_to_partner_and_social(
                raw_action=focal.last_raw_action,
                active_partner=local_p,
                assignment_mode_code=0,
                factorized_policies=focal.factorized_policies,
                num_social_actions=focal.num_social_actions,
                num_partners=focal.num_partners,
            )

        # ---- step 4: engaged-partner action (F6: forced active_partner = focal) ----
        engaged = self.agents[engaged_g]
        local_f_in_engaged = _local_partner_idx(engaged_g, focal_g)
        engaged.choose_partner_and_action(active_partner=local_f_in_engaged)
        _, engaged_action = decode_raw_action_to_partner_and_social(
            raw_action=engaged.last_raw_action,
            active_partner=local_f_in_engaged,
            assignment_mode_code=0,                                # FORCED 0 even if engaged.assignment_mode_code == 1
            factorized_policies=engaged.factorized_policies,
            num_social_actions=engaged.num_social_actions,
            num_partners=engaged.num_partners,
        )

        # ---- step 5: joint resolution ----
        focal_payoff_obs, focal_payoff_value = joint_resolve(focal_action, engaged_action, focal.model)
        engaged_payoff_obs, engaged_payoff_value = joint_resolve(engaged_action, focal_action, engaged.model)

        # ---- step 6: mutual observe + update ----
        focal.observe_outcome(
            partner_idx=local_p,
            observation=[int(engaged_action), int(focal_payoff_obs)],
            action_taken=int(focal_action),
            partner_action=int(engaged_action),
            payoff=float(focal_payoff_value),
            true_partner_type=getattr(engaged, "_kind_label", None),
            true_partner_stance=None,
        )
        engaged.observe_outcome(
            partner_idx=local_f_in_engaged,
            observation=[int(focal_action), int(engaged_payoff_obs)],
            action_taken=int(engaged_action),
            partner_action=int(focal_action),
            payoff=float(engaged_payoff_value),
            true_partner_type=getattr(focal, "_kind_label", None),
            true_partner_stance=None,
        )

        # ---- step 7: log two rows ----
        rows: list[dict] = []
        for agent_g, agent, is_focal in [(focal_g, focal, True), (engaged_g, engaged, False)]:
            rows.append(self._row_for(agent_g, agent, t, focal_g, engaged_g, is_focal))
        return rows

    def _row_for(self, agent_g: int, agent: TrustGameAgent, t: int, focal_g: int, engaged_g: int, is_focal: bool) -> dict:
        metrics = agent.get_metrics()
        scalars = {k: v for k, v in metrics.items() if not _is_array(v)}
        return {
            "round": t,
            "focal_idx": focal_g,
            "engaged_partner_global_idx": engaged_g,
            "agent_global_idx": agent_g,
            "agent_kind": getattr(agent, "_kind_label", "base"),
            "is_focal_this_round": bool(is_focal),
            **scalars,
        }


def _is_array(v) -> bool:
    return isinstance(v, np.ndarray) and v.ndim > 0
```

- [ ] **Step 2: smoke import**

Run: `python -c "from experiment.multi_focal_runner import MultiFocalRunner; print('ok')"`
Expected: prints `ok`.

### Task 4.2: integration test — one round at M=2

**Files:**
- Create: `tests/test_multi_focal_round_loop.py`

- [ ] **Step 1: write the test file**

```python
"""End-to-end: one round of two AffectiveAgents in random assignment mode."""
from __future__ import annotations
import numpy as np
from experiment.multi_focal_runner import MultiFocalRunner
from experiment.multi_focal_config import MultiFocalConfig
from experiment.factory import create_agents_from_multi_focal_config

def _make_runner(M=2, assignment_mode="random", num_rounds=1, seed=0):
    cfg = MultiFocalConfig.from_dict({
        "experiment_name": "round_loop",
        "assignment_mode": assignment_mode,
        "num_rounds": num_rounds,
        "random_seed": seed,
        "agents": [{"kind": "affective", "planning_horizon": 2}] * M,
    })
    agents = create_agents_from_multi_focal_config(cfg, seed=seed)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(seed))

def test_one_round_random_M2_produces_two_rows():
    runner = _make_runner(M=2, assignment_mode="random", num_rounds=1)
    rows = runner.run()
    assert len(rows) == 2
    assert rows[0]["round"] == 0
    assert rows[1]["round"] == 0
    assert rows[0]["focal_idx"] == rows[1]["focal_idx"]
    assert rows[0]["engaged_partner_global_idx"] == rows[1]["engaged_partner_global_idx"]
    assert {rows[0]["agent_global_idx"], rows[1]["agent_global_idx"]} == {0, 1}
    assert {rows[0]["is_focal_this_round"], rows[1]["is_focal_this_round"]} == {True, False}

def test_three_rounds_M4_round_robin_focal_cycles():
    cfg = MultiFocalConfig.from_dict({
        "experiment_name": "x",
        "assignment_mode": "random",
        "num_rounds": 4,
        "focal_selection": "round_robin",
        "agents": [{"kind": "base", "planning_horizon": 2}] * 4,
    })
    agents = create_agents_from_multi_focal_config(cfg, seed=1)
    runner = MultiFocalRunner(cfg, agents, rng=np.random.default_rng(1))
    rows = runner.run()
    # 4 rounds × 2 rows per round = 8 rows
    assert len(rows) == 8
    # focal cycles 0, 1, 2, 3
    focal_per_round = {}
    for r in rows:
        focal_per_round.setdefault(r["round"], r["focal_idx"])
    assert focal_per_round == {0: 0, 1: 1, 2: 2, 3: 3}

def test_agent_choice_mode_runs_without_error():
    runner = _make_runner(M=3, assignment_mode="agent_choice", num_rounds=2, seed=7)
    rows = runner.run()
    assert len(rows) == 4
    # engaged partner global idx must differ from focal idx
    for r in rows:
        assert r["engaged_partner_global_idx"] != r["focal_idx"]

def test_metrics_columns_propagate():
    runner = _make_runner(M=2, num_rounds=1, seed=2)
    rows = runner.run()
    expected_keys = {
        "round", "focal_idx", "engaged_partner_global_idx", "agent_global_idx",
        "agent_kind", "is_focal_this_round",
        "best_policy_idx", "selected_partner", "selected_action", "raw_action",
        "q_pi_entropy", "planning_cost", "planning_cost_ratio",
        "round_log_evidence", "cumulative_log_evidence",
        "mean_abs_step_efe",
    }
    assert expected_keys.issubset(rows[0].keys())
```

- [ ] **Step 2: run tests**

Run: `pytest tests/test_multi_focal_round_loop.py -v`
Expected: 4 tests pass. **If any fail**: most likely cause is a mismatch between what `decode_raw_action_to_partner_and_social` expects and what the engaged-partner code passes (e.g., `assignment_mode_code` not being forced to 0). Inspect the failing test's traceback and adjust the runner.

- [ ] **Step 3: commit**

```bash
git add experiment/multi_focal_runner.py tests/test_multi_focal_round_loop.py
git commit -m "feat(multifocal): round loop + bilateral observe/update"
```

---

## Phase 5: ship 4 new configs + smoke run

**Goal:** wire the four configs from spec Section 4+7. Confirm each loads and the smoke config runs to completion.

### Task 5.1: ship the four configs

**Files:**
- Create: `configs/multifocal_smoke.json`
- Create: `configs/multifocal_homogeneous_affective.json`
- Create: `configs/multifocal_clinical_mix.json`
- Create: `configs/multifocal_assortative_choice.json`

- [ ] **Step 1: write `configs/multifocal_smoke.json`**

```json
{
  "experiment_name": "multifocal_smoke",
  "round_mode": "turn_taking",
  "focal_selection": "round_robin",
  "assignment_mode": "random",
  "num_rounds": 10,
  "num_replications": 1,
  "random_seed": 0,
  "payoff_mode": "binary",
  "agents": [
    {"kind": "affective", "planning_horizon": 4, "alpha_charge": 3.0},
    {"kind": "affective", "planning_horizon": 4, "alpha_charge": 3.0}
  ]
}
```

- [ ] **Step 2: write `configs/multifocal_homogeneous_affective.json`**

```json
{
  "experiment_name": "multifocal_homogeneous_affective",
  "round_mode": "turn_taking",
  "focal_selection": "round_robin",
  "assignment_mode": "random",
  "num_rounds": 200,
  "num_replications": 50,
  "random_seed": 42,
  "payoff_mode": "binary",
  "agents": [
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "num_levels": 5, "persistence": 0.8},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "num_levels": 5, "persistence": 0.8},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "num_levels": 5, "persistence": 0.8},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "num_levels": 5, "persistence": 0.8}
  ]
}
```

- [ ] **Step 3: write `configs/multifocal_clinical_mix.json`**

```json
{
  "experiment_name": "multifocal_clinical_mix",
  "round_mode": "turn_taking",
  "focal_selection": "round_robin",
  "assignment_mode": "random",
  "num_rounds": 300,
  "num_replications": 50,
  "random_seed": 42,
  "payoff_mode": "binary",
  "agents": [
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "_label": "healthy"},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 0.5, "_label": "alexithymia"},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 8.0, "_label": "borderline"},
    {"kind": "lesioned",  "planning_horizon": 8, "lesion_mode": "decouple", "_label": "vmPFC_lesion"}
  ]
}
```

- [ ] **Step 4: write `configs/multifocal_assortative_choice.json`**

```json
{
  "experiment_name": "multifocal_assortative_choice",
  "round_mode": "turn_taking",
  "focal_selection": "round_robin",
  "assignment_mode": "agent_choice",
  "num_rounds": 400,
  "num_replications": 50,
  "random_seed": 42,
  "payoff_mode": "binary",
  "agents": [
    {"kind": "affective", "planning_horizon": 8, "_label": "deep_affective_A"},
    {"kind": "affective", "planning_horizon": 8, "_label": "deep_affective_B"},
    {"kind": "base",      "planning_horizon": 2, "_label": "shallow_no_affect_C"},
    {"kind": "base",      "planning_horizon": 2, "_label": "shallow_no_affect_D"}
  ]
}
```

### Task 5.2: smoke run + config-loader test

**Files:**
- Edit: `tests/test_multi_focal_config.py` (add a config-loader sweep test)

- [ ] **Step 1: append a sweep test**

```python
import json
from pathlib import Path

_MULTIFOCAL_GLOB = "configs/multifocal_*.json"

def test_all_multifocal_configs_load_and_validate():
    paths = sorted(Path(".").glob(_MULTIFOCAL_GLOB))
    assert len(paths) >= 4, f"expected >= 4 configs, found {len(paths)}: {paths}"
    for p in paths:
        raw = json.loads(p.read_text())
        cfg = MultiFocalConfig.from_dict(raw)
        assert cfg.num_agents() >= 2, f"{p}: M={cfg.num_agents()}"
```

- [ ] **Step 2: run loader sweep**

Run: `pytest tests/test_multi_focal_config.py -v`
Expected: 8 tests pass (7 from before + the new sweep).

- [ ] **Step 3: smoke-run the smoke config end-to-end**

Run:

```bash
python -c "
import json, numpy as np
from experiment.multi_focal_config import MultiFocalConfig
from experiment.multi_focal_runner import MultiFocalRunner
from experiment.factory import create_agents_from_multi_focal_config
raw = json.loads(open('configs/multifocal_smoke.json').read())
cfg = MultiFocalConfig.from_dict(raw)
agents = create_agents_from_multi_focal_config(cfg, seed=cfg.random_seed)
rows = MultiFocalRunner(cfg, agents, rng=np.random.default_rng(cfg.random_seed)).run()
print(f'{len(rows)} rows from {cfg.num_rounds} rounds')
print('sample row keys:', sorted(rows[0].keys())[:8])
"
```

Expected: prints `20 rows from 10 rounds` and a list of column keys. No errors.

- [ ] **Step 4: commit**

```bash
git add configs/multifocal_*.json tests/test_multi_focal_config.py
git commit -m "feat(multifocal): four sanity-check configs (D inventory)"
```

---

## Phase 6: deterministic regression test

**Goal:** lock down per-round numerical behavior with hand-captured assertions on pinned RNG seeds. Same philosophy as B+A spec Section 5: code, not blobs; greppable; diagnostic.

### Task 6.1: capture baseline values

**Files:**
- Create: `tests/test_multi_focal_deterministic.py` (with placeholder values)

- [ ] **Step 1: write the test file with placeholder values**

```python
"""Deterministic regression tests for the multi-focal runner.
Captured from SHA <FILL_ME> on 2026-04-18 — pinned RNG seeds, no learning, no noise.
Any divergence in the post-PR code from these numbers is a regression."""
from __future__ import annotations
import numpy as np
import pytest
from experiment.multi_focal_runner import MultiFocalRunner
from experiment.multi_focal_config import MultiFocalConfig
from experiment.factory import create_agents_from_multi_focal_config

def _build(M=4, num_rounds=50, seed=42):
    cfg = MultiFocalConfig.from_dict({
        "experiment_name": "det",
        "round_mode": "turn_taking",
        "focal_selection": "round_robin",
        "assignment_mode": "random",
        "num_rounds": num_rounds,
        "random_seed": seed,
        "payoff_mode": "binary",
        "agents": [
            {"kind": "affective", "planning_horizon": 4, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "num_levels": 5, "persistence": 0.8},
        ] * M,
    })
    agents = create_agents_from_multi_focal_config(cfg, seed=seed)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(seed))

def _run_and_index(runner) -> dict:
    rows = runner.run()
    by = {}
    for r in rows:
        by[(r["round"], r["agent_global_idx"], r["is_focal_this_round"])] = r
    return by

@pytest.fixture(scope="module")
def baseline_rows():
    return _run_and_index(_build())

# ---- captured assertions (placeholders; replace after first run) ----

def test_round0_focal_idx(baseline_rows):
    # round 0, focal selected as round-robin → focal_idx should be 0
    keys_round_0 = [k for k in baseline_rows if k[0] == 0]
    focal_keys = [k for k in keys_round_0 if k[2] is True]
    assert len(focal_keys) == 1
    assert focal_keys[0][1] == 0

def test_round0_focal_action_pinned(baseline_rows):
    """Pinned: under seed=42, M=4 affectives, planning_horizon=4, focal_idx=0
    selects social_action == _____ at round 0."""
    row = baseline_rows[(0, 0, True)]
    # PLACEHOLDER: replace _____ with the value observed on first run
    # assert row["selected_action"] == 0
    assert row["selected_action"] in {0, 1}     # placeholder bound; refine

def test_round25_focal_idx_round_robin(baseline_rows):
    keys = [k for k in baseline_rows if k[0] == 25 and k[2] is True]
    assert len(keys) == 1
    assert keys[0][1] == 25 % 4   # round-robin

def test_round49_payoff_in_legal_set(baseline_rows):
    row = baseline_rows[(49, 49 % 4, True)]
    assert row.get("round_log_evidence") is not None
```

- [ ] **Step 2: run once to capture actual values**

Run: `pytest tests/test_multi_focal_deterministic.py -v -s`
Expected: tests pass (the placeholder bounds are loose). **Note the actual `selected_action` values from the failing assertions** for hardening.

- [ ] **Step 3: harden ~12 assertions**

Add specific numerical assertions for ~12 specific (round, agent_idx, is_focal) tuples. Choose: rounds 0, 5, 10, 25, 49 × focal-only (5 assertions on `selected_action`), plus 4 assertions on `cumulative_log_evidence` at rounds 10, 25, 40, 49, plus 3 assertions on `q_pi_entropy` decreasing over rounds. Each captured by running once and pasting the value. ~12 assertions total. Replace the placeholder block.

- [ ] **Step 4: capture the SHA in the docstring**

Run: `git rev-parse HEAD`. Edit the module docstring to replace `<FILL_ME>` with the SHA.

- [ ] **Step 5: re-run with hardened values**

Run: `pytest tests/test_multi_focal_deterministic.py -v`
Expected: all hardened assertions pass.

- [ ] **Step 6: commit**

```bash
git add tests/test_multi_focal_deterministic.py
git commit -m "test(multifocal): deterministic regression w/ pinned seeds"
```

---

## Phase 7: emergent-dynamics smoke tests

**Goal:** confirm the qualitative phenomena F is meant to enable (cooperation emergence, defection cascade, assortative pairing) actually appear.

### Task 7.1: cooperation emergence (N1)

**Files:**
- Create: `tests/test_multi_focal_emergent.py`

- [ ] **Step 1: write `tests/test_multi_focal_emergent.py`**

```python
"""Statistical smoke tests for emergent multi-focal dynamics.
These are intentionally not bit-precise — they test the phenomenon, not the value."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from experiment.multi_focal_runner import MultiFocalRunner
from experiment.multi_focal_config import MultiFocalConfig
from experiment.factory import create_agents_from_multi_focal_config

def _build(agents_spec, num_rounds=200, seed=42, assignment_mode="random"):
    cfg = MultiFocalConfig.from_dict({
        "experiment_name": "emerge",
        "round_mode": "turn_taking",
        "focal_selection": "round_robin",
        "assignment_mode": assignment_mode,
        "num_rounds": num_rounds,
        "random_seed": seed,
        "payoff_mode": "binary",
        "agents": agents_spec,
    })
    agents = create_agents_from_multi_focal_config(cfg, seed=seed)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(seed)).run()

def _coop_rate_last_quartile(rows: list[dict]) -> float:
    df = pd.DataFrame(rows)
    last_quartile = df["round"] >= int(0.75 * df["round"].max())
    actions = df.loc[last_quartile, "selected_action"]
    # action 0 = cooperate (binary)
    return float((actions == 0).mean())

def test_n1_cooperation_emerges_among_4_affectives():
    """N1: 4 affective agents should converge to high cooperation rate."""
    spec = [{"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0}] * 4
    rates = []
    for seed in [42, 43, 44, 45, 46]:
        rows = _build(spec, num_rounds=200, seed=seed)
        rates.append(_coop_rate_last_quartile(rows))
    # statistical assertion: mean rate > 0.55, ≥ 4/5 seeds individually > 0.5
    assert np.mean(rates) > 0.55, f"mean cooperation rate {np.mean(rates):.3f} below 0.55; rates={rates}"
    assert sum(r > 0.5 for r in rates) >= 4, f"only {sum(r > 0.5 for r in rates)}/5 seeds above 0.5"

def test_n2_defection_cascade_from_lesioned_agent():
    """N2: replacing one of four affectives with a lesioned-decouple should
    measurably depress cooperation rate vs the all-affective baseline."""
    spec_baseline = [{"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0}] * 4
    spec_cascade = [
        {"kind": "lesioned", "planning_horizon": 8, "lesion_mode": "decouple"},
        {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0},
        {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0},
        {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0},
    ]
    base_rates, cas_rates = [], []
    for seed in [42, 43, 44]:
        base_rates.append(_coop_rate_last_quartile(_build(spec_baseline, num_rounds=200, seed=seed)))
        cas_rates.append(_coop_rate_last_quartile(_build(spec_cascade, num_rounds=200, seed=seed)))
    assert np.mean(cas_rates) < np.mean(base_rates), (
        f"defection cascade not observed: cascade={np.mean(cas_rates):.3f}, baseline={np.mean(base_rates):.3f}"
    )

def test_n3_assortative_pairing_in_agent_choice():
    """N3: under agent_choice with deep-affective vs shallow-no-affect, deep agents
    should pick deep partners more than 50% of the time in the final quartile."""
    spec = [
        {"kind": "affective", "planning_horizon": 8, "_label": "deep"},
        {"kind": "affective", "planning_horizon": 8, "_label": "deep"},
        {"kind": "base",      "planning_horizon": 2, "_label": "shallow"},
        {"kind": "base",      "planning_horizon": 2, "_label": "shallow"},
    ]
    deep_picks_deep = []
    for seed in [42, 43, 44]:
        rows = _build(spec, num_rounds=300, seed=seed, assignment_mode="agent_choice")
        df = pd.DataFrame(rows)
        last_quartile = df["round"] >= int(0.75 * df["round"].max())
        # rows with is_focal_this_round=True and agent_kind=="deep": did engaged agent's kind == "deep"?
        deep_focals = df.loc[last_quartile & df["is_focal_this_round"] & (df["agent_kind"] == "deep")].copy()
        # find the engaged partner's kind for each deep-focal row
        engaged_kinds = []
        for _, r in deep_focals.iterrows():
            engaged_row = df[(df["round"] == r["round"])
                             & (df["agent_global_idx"] == r["engaged_partner_global_idx"])
                             & (~df["is_focal_this_round"])]
            if not engaged_row.empty:
                engaged_kinds.append(engaged_row.iloc[0]["agent_kind"])
        if engaged_kinds:
            deep_picks_deep.append(np.mean([k == "deep" for k in engaged_kinds]))
    assert deep_picks_deep, "no deep-focal rows in last quartile across any seed (test setup error)"
    assert np.mean(deep_picks_deep) > 0.5, (
        f"deep agents do not preferentially pick deep partners: {deep_picks_deep}"
    )
```

- [ ] **Step 2: run the emergent tests**

Run: `pytest tests/test_multi_focal_emergent.py -v`
Expected: all 3 tests pass. Runtime ~30s (each test runs 3-5 200-300 round simulations).

> **If a test fails statistically**: this is the primary feedback signal — either (a) a bug exists in the runner that breaks the dynamics, or (b) the threshold is too tight. Investigate (a) first. **Do not loosen thresholds without verifying the underlying dynamics are correct** — a passing-but-loose test is no test at all.

- [ ] **Step 3: commit**

```bash
git add tests/test_multi_focal_emergent.py
git commit -m "test(multifocal): emergent dynamics smoke (N1, N2, N3)"
```

---

## Phase 8: doc + handoff

**Goal:** drop a CHANGELOG note, update `AGENTS.md` with the new module surface, append the F entry to the parent scoping doc, and refresh `STATE.md`.

### Task 8.1: scoping doc append

**Files:**
- Edit: `docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md`

- [ ] **Step 1: append a new entry under "completed sub-projects"**

After the existing C entry, add:

```markdown
- **F (multi-focal-agent runtime)** — 2026-04-18: added `experiment/multi_focal_runner.py` (turn-taking single-focal-per-round, simultaneous-moves resolution, RoundProtocol extension seam for future all-pairs), `experiment/joint_resolution.py`, `experiment/multi_focal_config.py` (heterogeneous `agents: [...]` schema), and `create_agents_from_multi_focal_config` factory. Four new configs shipped (`multifocal_smoke.json`, `multifocal_homogeneous_affective.json`, `multifocal_clinical_mix.json`, `multifocal_assortative_choice.json`) for sub-project D's inventory. ~270 LOC of code + ~680 LOC of tests, no changes to `aif/` or `trust/`. Documented divergence from `pomdp_spec.md` §12 step 4 (simultaneous-moves vs Stackelberg) under decisions log F4.
```

### Task 8.2: AGENTS.md drive-by

**Files:**
- Edit: `AGENTS.md`

- [ ] **Step 1: add a section pointing to the multi-focal runner**

Find a "Module map" or "Key modules" section in `AGENTS.md`. Add (or update):

```markdown
- `experiment/multi_focal_runner.py` — drives M `TrustGameAgent` instances through a turn-taking trust game (sub-project F). Heterogeneous populations supported via `agents: [{kind, planning_horizon, ...}]` config schema parsed by `experiment/multi_focal_config.py`. Joint payoff resolution lives in `experiment/joint_resolution.py`. See `docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md`.
```

If `AGENTS.md` has no "Module map" section, add one near the top after the high-level overview.

### Task 8.3: STATE.md note

**Files:**
- Edit: `conductor/STATE.md`

- [ ] **Step 1: add a session entry summarizing F**

Append to the session log (near the existing Session 107 entry):

```markdown
### Session 108 — multi-focal-runtime (F) implementation
- Added `experiment/multi_focal_runner.py`, `multi_focal_config.py`, `joint_resolution.py`, factory extension. Four new configs in `configs/multifocal_*.json`.
- Strict pomdp_spec §12 turn-taking (single focal per round). RoundProtocol extension seam for future all-pairs. Simultaneous-moves move resolution (deviation from pomdp_spec §12 step 4 documented as decision F4 — required to respect post-B+A decision #6).
- ~270 LOC of new code + ~680 LOC of tests across 7 new test files. No changes to `aif/` or `trust/`.
- Spec at `docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md`; plan at `docs/superpowers/plans/2026-04-18-multi-focal-runtime-plan.md`.
- Sub-project D should inventory the 4 new configs alongside the existing 24.
```

### Task 8.4: full test sweep + commit + PR

- [ ] **Step 1: run full pytest suite**

Run: `pytest tests/ -q`
Expected: all tests pass. Total count = baseline + ~20 new test functions across 7 new files.

- [ ] **Step 2: commit doc updates**

```bash
git add docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md AGENTS.md conductor/STATE.md
git commit -m "docs(multifocal): scoping append + agents map + STATE entry"
```

- [ ] **Step 3: open PR**

```bash
git push -u origin feature/multi-focal-runtime
gh pr create --title "feat(multifocal): turn-taking M-agent runtime" --body "$(cat <<'EOF'
## Summary
- Implements sub-project F per `docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md`.
- Strict pomdp_spec §12 turn-taking (single focal per round); RoundProtocol extension seam reserves room for future all-pairs.
- Simultaneous-moves resolution (deviation from §12 step 4) documented as decision F4.
- Heterogeneous AIF populations via `agents: [...]` config schema.
- Four new configs land for sub-project D's inventory: `multifocal_smoke.json`, `multifocal_homogeneous_affective.json`, `multifocal_clinical_mix.json`, `multifocal_assortative_choice.json`.
- No changes to `aif/` or `trust/`; this PR is purely additive in `experiment/` + `tests/` + `configs/`.

## Test plan
- [x] all unit tests pass (`pytest tests/`)
- [x] deterministic regression test pinned against captured SHA
- [x] emergent-dynamics smoke (N1 cooperation, N2 cascade, N3 assortative) passes 3-5 seeds
- [x] 4 new configs round-trip through `MultiFocalConfig.from_dict`
- [x] smoke config runs end-to-end in <5s

## Out of scope
- All-pairs-parallel mode (extension seam in place; future work).
- Mixed AIF + scripted-baseline populations (F11; future work).
- Stackelberg ordering (F4; would regress decision #6).
- CvC / cogames stack (per MISSION).
EOF
)"
```

---

## Risk register

| risk | likelihood | mitigation |
|---|---|---|
| `decode_raw_action_to_partner_and_social` semantics differ between focal and engaged paths | medium | Phase 4 test `test_agent_choice_mode_runs_without_error` exercises both paths; if it breaks, inspect `assignment_mode_code` plumbing |
| emergent test thresholds too tight → flake | medium | Phase 7 uses 5-seed averages with explicit `>= 4/5 seeds individually` clauses; if flake observed, investigate the dynamics first, only loosen as last resort |
| `TrustGameAgent.choose_partner_and_action(active_partner=k)` writes state that affects the next call | low | each agent owns its own state; `choose_partner_and_action` is the canonical entry point and is called once per round per agent in this design — no interleaving |
| graded-mode payoff resolution misalignment if agents have different `num_investment_levels` | low | F8/F10 enforce population-wide `num_social_actions` at config load |
| `infer_joint_posterior` payoff-drop bug fix (B+A decision #6) interacts subtly with bilateral observation flow | low | both agents call `observe_outcome` with the full `[partner_action, payoff_obs]` joint observation per F4; bug fix is exercised twice per round |
| logging row count >> expected because of "include_arrays" flag inadvertently on | low | default `_is_array` filter is on; `include_arrays` is opt-in (and not implemented in this PR — flagged as follow-up #5) |

---

## Definition of done

- [ ] all 8 phases complete; all tasks checked
- [ ] `pytest tests/` passes (baseline + new tests)
- [ ] 4 new configs round-trip through `MultiFocalConfig.from_dict`
- [ ] `multifocal_smoke.json` runs end-to-end via `MultiFocalRunner.run()` in < 5s
- [ ] deterministic regression test pinned against the captured SHA
- [ ] N1, N2, N3 emergent tests pass on 5/5, 3/3, 3/3 seeds respectively
- [ ] PR opened with the body above
- [ ] sub-project F entry appended to scoping doc's "completed sub-projects"
- [ ] `STATE.md` Session 108 entry added
- [ ] `AGENTS.md` module map mentions `experiment/multi_focal_runner.py`
- [ ] no diff in `aif/`, `trust/`, `analysis/`, `benchmark/`, `notebooks/`, `scripts/`, or `archive/` (verify with `git diff --stat origin/main`)
