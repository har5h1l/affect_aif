# multi-focal-agent runtime — design spec

date: 2026-04-18
status: **READY FOR USER REVIEW** — sections 1–7 drafted; decisions log at top is current.
parent: [`2026-04-18-codebase-restructure-scoping.md`](2026-04-18-codebase-restructure-scoping.md) (sub-project F)
depends on: [`2026-04-18-aif-extraction-design.md`](2026-04-18-aif-extraction-design.md) (B+A merged: `aif/` + `trust/` packages live)
follow-on: implementation plan via `superpowers:writing-plans`, written to `docs/superpowers/plans/`

---

## decisions log (locked in, in order taken)

| # | decision | resolution |
|---|---|---|
| F1 | round structure | strict **turn-taking only** at launch (per `pomdp_spec.md` §12). single focal selected per round; engaged partner is one other agent. extension seam: `RoundProtocol` interface so `AllPairsProtocol` can be added later as additive code without touching `TurnTakingProtocol`. no all-pairs, no perfect matching, no `pairing_resolution` knob, no concurrent-unilateral semantics. |
| F2 | focal selection | `focal_selection: "round_robin" | "random"` config knob. round-robin guarantees equal turns; random matches `pomdp_spec` §12 step 1. default: `round_robin` (lower variance, easier interpretation). |
| F3 | engaged-partner selection | unchanged from single-focal: `assignment_mode: "random" | "agent_choice"`. `random` → runtime picks one global partner uniformly from M-1 candidates. `agent_choice` → focal calls `choose_partner_and_action()` which picks both the local partner index and the social action. **trivially "initiator wins"** because there is exactly one initiator per round. |
| F4 | move resolution | **simultaneous moves**, not literal `pomdp_spec` §12 step 4 (Stackelberg). both agents pick actions from prior beliefs in parallel; joint outcome computed; both run `observe_outcome` with full `[partner_action, payoff]`. **deviation from pomdp_spec is intentional**: literal Stackelberg requires a one-modality interim observation update, which B+A decision #6 explicitly removed (it was the payoff-drop bug). simultaneous-moves respects the post-B+A model API. ~30 LOC simpler than Stackelberg. documented as known divergence. |
| F5 | self-modeling | each focal agent's `num_partners = M-1` (no self in its model). global-to-local index mapping: for focal `g`, partner with global index `g'` maps to local `g'` if `g' < g` else `g' - 1`. owned by `experiment/multi_focal_runner.py:_local_partner_idx`. |
| F6 | engaged-partner action API | when global agent `P` is engaged this round (with focal `F`), `P.choose_partner_and_action(active_partner=local_idx_of_F_in_P_view)` is called. P treats F as the assigned partner, picks a social action via the planner. P's own partner-selection muscle (under `agent_choice`) is dormant when P is the engaged partner — exercised only when P is the focal. matches existing single-focal API; **no changes to `trust/agent.py`**. |
| F7 | heterogeneous populations | config schema gains a top-level `agents: [...]` list. each entry is an agent spec: `{kind: "base"|"affective"|"lesioned", planning_horizon, gamma, learn_A, lesion_mode, alpha_charge, ...}`. `M = len(agents)`. agents may have different `kind`s and parameters. shared `model_overrides` per-agent supported (e.g., agent 0 has different `preference_temperature`). when omitted, all agents use the top-level config. |
| F8 | shared vs per-agent `TrustGameModel` | each agent gets its own `TrustGameModel` instance constructed from `top_level_config + agent.get("model_overrides", {})`. cheap (model objects are <1 KB). enables heterogeneous `preference_temperature`, `payoff_mode`, etc. across agents. **constraint**: all agents in a single experiment must agree on `payoff_mode` (binary or graded) and `num_social_actions` — otherwise pair payoff resolution is undefined. enforced at config load. |
| F9 | logging schema | one row per `(round, focal_idx, partner_global_idx)` in long format. columns are the existing `TrustGameAgent.get_metrics()` keys plus four multi-focal columns: `focal_idx`, `engaged_partner_global_idx`, `agent_kind`, `is_focal_this_round`. partners not engaged this round emit no row. CSV size: with M=4 agents and 200 rounds → 200 rows (one row per round) when only the focal logs, or 400 rows when both focal and engaged log (option F9.b). chosen: **both focal and engaged log**, since both run inference and update beliefs each round. |
| F10 | graded payoff in multi-focal | symmetric: both agents in a pair pick from the same `num_investment_levels` set; payoffs computed via the symmetric graded matrix. only allowed when **all** agents have `payoff_mode: "graded"` and identical `num_investment_levels`. mixed binary+graded populations raise `ValueError` at config load. |
| F11 | scope of F | F is **AIF-on-AIF only**. baselines (`TitForTat`, `Random`, etc.) coexist in single-focal experiments and stay there. F does NOT add a "mixed AIF + scripted-baseline population" mode. that's potential future work, scoped separately if needed. |
| F12 | testing emergent dynamics | three categories: (a) unit tests on the runner + joint resolution + pairing (~250 LOC), (b) deterministic regression tests against pinned RNG seeds (~150 LOC), (c) emergent-dynamics smoke tests (cooperation can emerge from two `AffectiveAgent`s; defection can cascade through a 4-agent population) (~200 LOC). emergent tests are **statistical, not bit-precise** (cooperation rate > 0.6 over the last 50 rounds with 5/5 seeds). |

---

## section 1 — protocol & round structure

### round protocol (strict pomdp_spec §12, simultaneous-moves variant)

each round in a multi-focal game proceeds as:

```
1. focal selection (F1, F2):
   focal_global_idx = round_robin_or_random(round, M, rng)

2. engaged partner selection (F3, F6):
   if assignment_mode == "random":
       engaged_global_idx = uniform_random(global indices excluding focal_global_idx)
   elif assignment_mode == "agent_choice":
       focal.choose_partner_and_action()  # picks local partner + social action
       engaged_local_idx, focal_social_action = decode_raw_action_to_partner_and_social(
           focal.last_raw_action, ..., assignment_mode_code=1, ...)
       engaged_global_idx = local_to_global(focal_global_idx, engaged_local_idx)
   else:
       raise ValueError

3. focal action commit:
   if assignment_mode == "random":
       focal.choose_partner_and_action(active_partner=local_idx_of(engaged_global_idx, in focal's view))
       _, focal_social_action = decode_raw_action_to_partner_and_social(
           focal.last_raw_action, ..., assignment_mode_code=0, ...)

4. engaged-partner action (F4 simultaneous, F6 forced active_partner):
   engaged.choose_partner_and_action(active_partner=local_idx_of(focal_global_idx, in engaged's view))
   _, engaged_social_action = decode_raw_action_to_partner_and_social(
       engaged.last_raw_action, ..., assignment_mode_code=0, ...)
   # engaged's own partner-selection is dormant; we force assignment_mode_code=0 in the decode

5. joint resolution (Section 3):
   focal_payoff_obs, focal_payoff_value = joint_resolve(focal_social_action, engaged_social_action, model, role="own")
   engaged_payoff_obs, engaged_payoff_value = joint_resolve(engaged_social_action, focal_social_action, model, role="own")

6. mutual observe + update (uses existing `observe_outcome` API unchanged):
   focal.observe_outcome(
       partner_idx=local_idx_of(engaged_global_idx, in focal's view),
       observation=[engaged_social_action, focal_payoff_obs],
       action_taken=focal_social_action,
       partner_action=engaged_social_action,
       payoff=focal_payoff_value,
       true_partner_type=engaged.kind_label,        # for diagnostic logging
       true_partner_stance=engaged.observable_stance_or_None,
   )
   engaged.observe_outcome(
       partner_idx=local_idx_of(focal_global_idx, in engaged's view),
       observation=[focal_social_action, engaged_payoff_obs],
       action_taken=engaged_social_action,
       partner_action=focal_social_action,
       payoff=engaged_payoff_value,
       true_partner_type=focal.kind_label,
       true_partner_stance=focal.observable_stance_or_None,
   )

7. log two rows (F9):
   row(round=t, focal_idx=focal_global_idx, engaged_partner_global_idx=engaged_global_idx, is_focal=True,  ...metrics from focal)
   row(round=t, focal_idx=focal_global_idx, engaged_partner_global_idx=engaged_global_idx, is_focal=False, ...metrics from engaged)
```

**why simultaneous-moves and not literal Stackelberg** (F4): pomdp_spec §12 step 4 has the engaged partner observe `u_focal` *before* planning. To do that under post-B+A model semantics would require either (a) a partial `infer_states` call on only the action modality (regression of decision #6 fail-fast) or (b) a one-off bypass that calls `aif.infer_states` with a custom one-modality likelihood — both add API surface and reintroduce the bug class B+A explicitly closed. Simultaneous-moves keeps `TrustGameAgent` untouched, makes the protocol a pure addition, and the loss of "engaged partner peeks" is small in expectation (the engaged partner still gets the joint observation in step 6, before its next round's planning).

**a note on inference asymmetry**: under simultaneous-moves, the engaged partner P plans against its prior belief about F (not updated for F's current-round action). One round later (when P is the focal or is engaged again), P's belief about F includes F's previous action. So P always lags by one round in its model of F. The same is true of F's model of P. This is symmetric and well-defined. It matches Markov-game conventions.

### round structure config

```json
{
  "round_mode": "turn_taking",           // F1: only "turn_taking" valid at launch; "all_pairs" reserved
  "focal_selection": "round_robin",      // F2: "round_robin" | "random"
  "assignment_mode": "random",           // F3: "random" | "agent_choice"
  "num_rounds": 200,                     // total rounds
  "num_replications": 50,                // independent seeds per condition
  "random_seed": 42                      // base seed; per-replication seeds derive from this
}
```

**extension seam (F1)**: `RoundProtocol` is an internal `Protocol`-typed interface on the runner:

```python
class RoundProtocol(Protocol):
    def select_pairs(self, round_idx: int, agents: list[TrustGameAgent], rng: np.random.Generator) -> list[tuple[int, int]]:
        """Returns a list of (focal_global_idx, engaged_global_idx) pairs to play this round.
        TurnTakingProtocol returns exactly one pair. AllPairsProtocol (future) returns ⌊M/2⌋ pairs."""
```

at launch we ship only `TurnTakingProtocol`. adding `AllPairsProtocol` later means: implement the `select_pairs` method for it, register it in the runner's `_protocols` dict, accept `round_mode: "all_pairs"` in the config schema. **no changes to `aif/`, `trust/`, or `experiment/joint_resolution.py`.**

---

## section 2 — runner architecture

### file layout

| file | role | LOC est. |
|---|---|---|
| `experiment/multi_focal_runner.py` | runner class, round loop, focal selection, global↔local index mapping | ~120 |
| `experiment/joint_resolution.py` | `joint_resolve(my_action, partner_action, model, role)` → `(payoff_obs_idx, payoff_value)` | ~40 |
| `experiment/multi_focal_config.py` | parse heterogeneous `agents: [...]` config; validate constraints | ~80 |
| `experiment/factory.py` (extended) | new `create_agents_from_multi_focal_config(config)` returning `list[TrustGameAgent]` | +30 |
| **total new code** | | **~270 LOC** |

(scoping doc estimated 150 + 50 + 100 = 300 LOC. close.)

### `experiment/multi_focal_runner.py`

```python
from typing import Protocol
import numpy as np
from trust import TrustGameAgent
from trust.rollout import decode_raw_action_to_partner_and_social
from experiment.joint_resolution import joint_resolve

class RoundProtocol(Protocol):
    def select_pairs(self, round_idx, agents, rng): ...

class TurnTakingProtocol:
    def __init__(self, focal_selection: str):
        self.focal_selection = focal_selection
    def select_pairs(self, round_idx, agents, rng):
        M = len(agents)
        if self.focal_selection == "round_robin":
            focal = round_idx % M
        elif self.focal_selection == "random":
            focal = int(rng.integers(M))
        else:
            raise ValueError(f"unknown focal_selection={self.focal_selection!r}")
        # engaged partner is selected later by the runner (random or agent_choice)
        return [(focal, None)]   # None = "to be decided in step 2 of the protocol"

_PROTOCOLS = {"turn_taking": TurnTakingProtocol}    # extension seam: register others here

def _local_partner_idx(focal_global: int, other_global: int) -> int:
    """Global-to-local mapping: for focal F, partner P maps to local index P if P<F else P-1."""
    if other_global == focal_global:
        raise ValueError("self-modeling not supported (F5)")
    return other_global if other_global < focal_global else other_global - 1

def _global_partner_idx(focal_global: int, local: int, M: int) -> int:
    """Inverse of _local_partner_idx."""
    return local if local < focal_global else local + 1

class MultiFocalRunner:
    """Drive M TrustGameAgents through a multi-focal trust game."""

    def __init__(self, config, agents: list[TrustGameAgent], rng: np.random.Generator):
        self.config = config
        self.agents = agents
        self.M = len(agents)
        self.rng = rng
        self.protocol = _PROTOCOLS[config.round_mode](focal_selection=config.focal_selection)
        # cross-agent constraint check (F8): all share payoff_mode and num_social_actions
        self._validate_population()

    def run(self) -> list[dict]:
        """Run num_rounds. Returns a list of per-row dicts (long format, F9)."""
        rows = []
        for t in range(self.config.num_rounds):
            for (focal_g, _placeholder) in self.protocol.select_pairs(t, self.agents, self.rng):
                rows.extend(self._play_one_pair(t, focal_g))
        return rows

    def _play_one_pair(self, t: int, focal_g: int) -> list[dict]:
        focal = self.agents[focal_g]
        # ---- step 2: engaged-partner selection ----
        if self.config.assignment_mode == "agent_choice":
            focal.choose_partner_and_action()    # focal picks (local partner, social action)
            local_p, focal_action = decode_raw_action_to_partner_and_social(
                raw_action=focal.last_raw_action,
                active_partner=0,   # ignored when assignment_mode_code=1
                assignment_mode_code=1,
                factorized_policies=focal.factorized_policies,
                num_social_actions=focal.num_social_actions,
                num_partners=focal.num_partners,
            )
            engaged_g = _global_partner_idx(focal_g, local_p, self.M)
        elif self.config.assignment_mode == "random":
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
        else:
            raise ValueError(f"unknown assignment_mode={self.config.assignment_mode!r}")

        # ---- step 4: engaged partner picks (forced active_partner = focal) ----
        engaged = self.agents[engaged_g]
        local_f_in_engaged = _local_partner_idx(engaged_g, focal_g)
        engaged.choose_partner_and_action(active_partner=local_f_in_engaged)
        _, engaged_action = decode_raw_action_to_partner_and_social(
            raw_action=engaged.last_raw_action,
            active_partner=local_f_in_engaged,
            assignment_mode_code=0,             # FORCED 0 even if agent's own mode is agent_choice (F6)
            factorized_policies=engaged.factorized_policies,
            num_social_actions=engaged.num_social_actions,
            num_partners=engaged.num_partners,
        )

        # ---- step 5: joint resolution ----
        focal_payoff_obs, focal_payoff_value = joint_resolve(
            my_action=focal_action, partner_action=engaged_action, model=focal.model
        )
        engaged_payoff_obs, engaged_payoff_value = joint_resolve(
            my_action=engaged_action, partner_action=focal_action, model=engaged.model
        )

        # ---- step 6: mutual observe + update ----
        focal.observe_outcome(
            partner_idx=local_p,
            observation=[engaged_action, focal_payoff_obs],
            action_taken=focal_action,
            partner_action=engaged_action,
            payoff=focal_payoff_value,
            true_partner_type=getattr(engaged, "_kind_label", None),
            true_partner_stance=None,           # not directly observable in F (no "true stance")
        )
        engaged.observe_outcome(
            partner_idx=local_f_in_engaged,
            observation=[focal_action, engaged_payoff_obs],
            action_taken=engaged_action,
            partner_action=focal_action,
            payoff=engaged_payoff_value,
            true_partner_type=getattr(focal, "_kind_label", None),
            true_partner_stance=None,
        )

        # ---- step 7: log ----
        rows = []
        for agent_g, agent, is_focal in [(focal_g, focal, True), (engaged_g, engaged, False)]:
            metrics = agent.get_metrics()
            rows.append({
                "round": t,
                "focal_idx": focal_g,
                "engaged_partner_global_idx": engaged_g,
                "agent_global_idx": agent_g,
                "agent_kind": getattr(agent, "_kind_label", "base"),
                "is_focal_this_round": is_focal,
                **{k: v for k, v in metrics.items() if not _is_array(v)},
                # arrays (q_pi, G, partner_beliefs, ...) are stored separately if a 'rich logger' is on.
                # by default, we flatten only scalar metrics; arrays require explicit opt-in.
            })
        return rows

    def _validate_population(self) -> None:
        payoff_modes = {a.model.payoff_mode for a in self.agents}
        if len(payoff_modes) > 1:
            raise ValueError(f"all agents must share payoff_mode; got {payoff_modes}")
        nsas = {a.num_social_actions for a in self.agents}
        if len(nsas) > 1:
            raise ValueError(f"all agents must share num_social_actions; got {nsas}")
        # M must be ≥ 2
        if self.M < 2:
            raise ValueError(f"multi-focal requires at least 2 agents; got {self.M}")
        # if any agent has num_partners != self.M - 1, that's a config error (F5)
        for i, a in enumerate(self.agents):
            if a.num_partners != self.M - 1:
                raise ValueError(
                    f"agent[{i}] has num_partners={a.num_partners}; "
                    f"expected M-1={self.M - 1} (no self-modeling, F5)"
                )

def _is_array(v):
    return isinstance(v, np.ndarray) and v.ndim > 0
```

### `experiment/joint_resolution.py`

```python
import numpy as np
from trust.model import TrustGameModel

def joint_resolve(my_action: int, partner_action: int, model: TrustGameModel) -> tuple[int, float]:
    """Resolve a single pair's actions into (payoff_obs_idx, payoff_value) for the agent
    whose action is `my_action`. Symmetric: payoff for the other side is computed by
    a second call with the arguments swapped.

    Returns:
        payoff_obs_idx: int — the index into model.payoff_levels for this agent's outcome
                       (used as the second observation modality).
        payoff_value: float — the raw payoff (used for logging / metrics; not for inference).
    """
    payoff_value = float(model.payoff_matrix[my_action, partner_action, 0])  # [0] = my row
    # find the discrete payoff level that equals payoff_value
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

graded mode adds no special path: the graded `payoff_matrix` is built with the same `(my_action, partner_action) → payoff` shape; `payoff_levels` enumerates all possible discrete outcomes. `joint_resolve` works unchanged.

### `experiment/multi_focal_config.py`

```python
from dataclasses import dataclass, field
from experiment.factory import create_agents_from_multi_focal_config

@dataclass
class MultiFocalConfig:
    """Top-level multi-focal experiment config.

    Schema:
        {
          "experiment_name": "multifocal_smoke",
          "round_mode": "turn_taking",
          "focal_selection": "round_robin",
          "assignment_mode": "random",
          "num_rounds": 200,
          "num_replications": 50,
          "random_seed": 42,
          "payoff_mode": "binary",                 // population-wide; per-agent override allowed if all match
          "agents": [
            {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "model_overrides": {}},
            {"kind": "lesioned",  "planning_horizon": 8, "lesion_mode": "decouple", "model_overrides": {}},
            {"kind": "base",      "planning_horizon": 4},
            {"kind": "affective", "planning_horizon": 8, "model_overrides": {"preference_temperature": 2.0}}
          ],
          "logging": {
            "include_arrays": false,    // q_pi, G, beliefs as columns vs scalar-only (default false)
            "include_diagnostic_metrics": true
          }
        }
    """
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

    @classmethod
    def from_dict(cls, raw: dict) -> "MultiFocalConfig":
        # validate required keys, raise loudly on unknown keys
        ...

    def num_agents(self) -> int:
        return len(self.agents)
```

constraints enforced at load time:
- `len(agents) >= 2`
- all agent specs use a known `kind`
- all `model_overrides` produce models with the same `payoff_mode` and `num_social_actions` (F8, F10)
- if `assignment_mode == "agent_choice"`, all agents must have `num_partners == M-1` after construction
- `round_mode` must be in `_PROTOCOLS`

### `experiment/factory.py` extension

```python
def create_agents_from_multi_focal_config(
    config: MultiFocalConfig,
    seed: int,
) -> list[TrustGameAgent]:
    """Build M agents from a multi-focal config. Each agent gets its own model
    (sharing payoff_mode and num_social_actions; per-agent model_overrides allowed)."""
    M = config.num_agents()
    agents = []
    for i, spec in enumerate(config.agents):
        # build per-agent model with population payoff_mode + per-agent overrides
        model_cfg = {
            "payoff_mode": config.payoff_mode,
            "num_partners": M - 1,
            "assignment_mode": config.assignment_mode,
            **spec.get("model_overrides", {}),
        }
        model = TrustGameModel(model_cfg)

        kind = spec["kind"]
        agent_kwargs = {k: v for k, v in spec.items() if k not in {"kind", "model_overrides"}}
        if kind == "base":
            agent = TrustGameAgent(model, seed=seed + i, **agent_kwargs)
        elif kind == "affective":
            agent = AffectiveAgent(model, seed=seed + i, **agent_kwargs)
        elif kind == "lesioned":
            agent = LesionedAgent(model, seed=seed + i, **agent_kwargs)
        else:
            raise ValueError(f"unknown agent kind={kind!r}")
        agent._kind_label = kind   # for logging (F9)
        agents.append(agent)
    return agents
```

---

## section 3 — joint resolution module

(specced inline above as `experiment/joint_resolution.py`. ~40 LOC, single function `joint_resolve`. graded mode requires no special path.)

key design choices flagged here:

1. **the env is bypassed for multi-focal**. current single-focal experiments use `env/trust_game.py:TrustGameEnv` to (a) generate scripted partner actions, (b) compute payoff observations, (c) maintain the "true" stance/type ground truth. Under multi-focal, partners *are* AIF agents — there is no scripted partner to simulate. The env's role collapses to "compute payoff outcome", which is exactly what `joint_resolve` does in 40 LOC. **`MultiFocalRunner` does not instantiate `TrustGameEnv`.** This is a clean architectural separation: single-focal uses `env/`, multi-focal does not.

2. **no "true partner type/stance" available in multi-focal**. In single-focal, `TrustGameEnv` knows each scripted partner's true type and stance (because it generated them). In multi-focal, "true type" is a category we ascribe to AIF agents externally (`agent._kind_label`). True stance is undefined — there is no ground-truth stance for an agent that doesn't have one as a state. `observe_outcome` accepts `true_partner_stance=None` already; the multi-focal runner just passes `None`.

3. **payoff symmetry enforced by model construction**. `TrustGameModel.payoff_matrix` has shape `(num_my_actions, num_their_actions, 2)` where `[..., 0]` is my payoff and `[..., 1]` is their payoff. `joint_resolve` reads `[..., 0]`. To compute the OTHER agent's payoff, the runner calls `joint_resolve` again with my_action and partner_action swapped, and reads `[..., 0]` of that agent's model. This means **each agent's view of the payoff matrix may differ** if `model_overrides` change payoff parameters. That's intentional: heterogeneous preferences / payoff perceptions are a feature.

4. **edge case: graded action mismatch**. If agent A picks investment level 4 from its model (which has 6 levels) and agent B picks level 3 from its model (which has 5 levels), `joint_resolve` may misalign. F8 (population-wide `num_social_actions`) prevents this at config load. flagged as a hard error.

---

## section 4 — config schema (heterogeneous populations)

specced as `MultiFocalConfig` in Section 2. recap of why this shape was chosen:

- **list-of-agent-specs at top level** mirrors the single-focal `conditions: [1, 2, 3, ...]` pattern (each int resolves to a `ConditionSpec`). multi-focal generalizes this: each entry is a *full* spec, not a numeric condition reference. agents in multi-focal are not "conditions"; they are independent participants.
- **per-agent `model_overrides`** dict allows heterogeneous payoff preferences without forking the schema. Default overrides are empty → all agents share the same `TrustGameModel`-equivalent (modulo per-agent fresh-copy semantics).
- **population-wide `payoff_mode`** is a top-level key (not per-agent). enforces F10 constraint by structure rather than runtime check.
- **two reserved future keys**: `pairing_resolution` (F1 extension seam, ignored under turn-taking), `round_mode` (F1, ignored when not "turn_taking").

### example configs (3 — for sub-project D's review)

#### 1. `configs/multifocal_homogeneous_affective.json`

four `AffectiveAgent`s, identical params, random assignment. simplest case. tests N1 (does cooperation emerge among AIF agents?).

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
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "beta_num_levels": 5, "beta_persistence": 0.8},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "beta_num_levels": 5, "beta_persistence": 0.8},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "beta_num_levels": 5, "beta_persistence": 0.8},
    {"kind": "affective", "planning_horizon": 8, "alpha_charge": 3.0, "sigma_0_sq": 0.25, "initial_beta": 1.0, "beta_num_levels": 5, "beta_persistence": 0.8}
  ]
}
```

#### 2. `configs/multifocal_clinical_mix.json`

heterogeneous clinical population. tests N5 (how does Alexithymia fare against Borderline + healthy?).

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

`_label` is a logging-only annotation; the runner reads it into `agent._kind_label` for the metrics rows (overrides the kind-derived default). Sub-project D may rename/canonicalize.

#### 3. `configs/multifocal_assortative_choice.json`

`agent_choice` with mixed planning depth. tests N3 (do high-trust agents preferentially pick each other?).

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

these three configs are **the deliverable for sub-project D's inventory** — D decides whether they survive, get renamed, or are merged.

---

## section 5 — agent index mapping

### the problem

with M agents globally indexed 0..M-1, each focal agent `g` maintains beliefs over **M-1 partners** with local indices 0..M-2. The runner needs deterministic round-trip mapping between global indices (used in pair selection, logging) and local indices (used inside each agent).

### the convention (F5)

```python
def _local_partner_idx(focal_global: int, other_global: int) -> int:
    if other_global == focal_global:
        raise ValueError("self-modeling not supported (F5)")
    return other_global if other_global < focal_global else other_global - 1

def _global_partner_idx(focal_global: int, local: int, M: int) -> int:
    return local if local < focal_global else local + 1
```

example with M=4:

| focal `g` | local 0 → global | local 1 → global | local 2 → global |
|---|---|---|---|
| 0 | 1 | 2 | 3 |
| 1 | 0 | 2 | 3 |
| 2 | 0 | 1 | 3 |
| 3 | 0 | 1 | 2 |

### invariants (tested in `tests/test_multi_focal_index_mapping.py`)

- `_local_partner_idx(g, _global_partner_idx(g, l, M)) == l` for all valid `(g, l, M)`
- `_global_partner_idx(g, _local_partner_idx(g, o), M) == o` for all valid `(g, o)` with `g != o`
- both raise on self-modeling attempt

### a subtle point

each agent's per-partner Dirichlet `pA` (decision #9) accumulates evidence keyed by **its own local partner index**. This means agent 0's `partners[0]` (global agent 1's beliefs from agent 0's perspective) and agent 1's `partners[0]` (global agent 0's beliefs from agent 1's perspective) are **independent learning containers** for the *same global pair*. They can diverge based on different observation streams. This is correct under F4/F5 — there is no "shared model of the (0,1) interaction"; each focal maintains its own private model.

---

## section 6 — testing strategy

### a — unit tests for runner mechanics (~250 LOC)

| test file | what it covers | LOC |
|---|---|---|
| `tests/test_multi_focal_index_mapping.py` | `_local_partner_idx` ↔ `_global_partner_idx` round-trip; self-modeling raises; M=2..8 edge cases | ~80 |
| `tests/test_multi_focal_runner_construction.py` | `MultiFocalRunner` validates population (mixed `payoff_mode` raises; `num_partners != M-1` raises; M < 2 raises) | ~70 |
| `tests/test_multi_focal_round_loop.py` | one round of M=2 agents executes cleanly: focal picks, engaged responds, both observe, two rows logged. assertions on row schema. | ~100 |

### b — joint-resolution + config tests (~80 LOC)

| test file | what it covers | LOC |
|---|---|---|
| `tests/test_joint_resolution.py` | `joint_resolve(my=C, partner=C)` → mutual_coop payoff; `(C, D)` → sucker; `(D, C)` → temptation; `(D, D)` → mutual_defect. binary + graded. raises if payoff_value not in payoff_levels. | ~50 |
| `tests/test_multi_focal_config.py` | `MultiFocalConfig.from_dict` parses good configs; rejects mixed `payoff_mode`; rejects M<2; rejects unknown agent kind | ~30 |

### c — deterministic regression tests (~150 LOC)

| test file | what it covers | LOC |
|---|---|---|
| `tests/test_multi_focal_deterministic.py` | Pin RNG seeds. Run M=4 affective agents for 50 rounds. Assert specific (round, focal_idx, agent_action, payoff) tuples at rounds 0, 5, 10, 25, 49. ~15 hand-captured assertions; same hand-written-rather-than-binary-blob philosophy as B+A spec Section 5. | ~150 |

### d — emergent-dynamics smoke tests (~200 LOC, statistical not bit-precise)

| test file | what it covers | LOC |
|---|---|---|
| `tests/test_multi_focal_emergent.py` | (N1) cooperation emerges: 4 affective agents, 200 rounds, 5 seeds → mean cooperation rate over rounds [150, 200] ≥ 0.55 in ≥ 4/5 seeds. (N2) defection cascades: 1 always-defect lesioned + 3 affective; the affective agents' final-quartile cooperation rate is significantly lower than in the all-affective baseline. (N3) under agent_choice with deep-affective vs shallow-no-affect, deep agents pick deep partners > 50% of the time in the final quartile. | ~200 |

**why statistical thresholds not bit-precise**: emergent dynamics are inherently stochastic; the goal is to confirm the *phenomenon* exists, not pin a specific numerical value. each assertion fires on ≥4/5 seeds at the cooperation thresholds picked. tightening would create false-positive failure noise. failures should be diagnostic (which seed broke; what cooperation rate did it reach).

### e — integration with existing test suite

- no changes to existing tests in `tests/` (multi-focal is purely additive code).
- run the full suite (`pytest tests/`) including new files. expect pass rate to match B+A baseline + the ~680 LOC of new tests.

### test totals

| bucket | files | LOC | net file delta |
|---|---|---|---|
| (a) runner mechanics | 3 | ~250 | +3 |
| (b) joint resolution + config | 2 | ~80 | +2 |
| (c) deterministic regression | 1 | ~150 | +1 |
| (d) emergent dynamics | 1 | ~200 | +1 |
| **total** | **7 new files** | **~680 LOC** | **+7** |

### CI integration

- pytest runtime grows by ~30s (mostly the 5-seed × 200-round emergent tests). Acceptable.
- new tests live under the same `tests/` dir. no separate marker needed.

---

## section 7 — sanity-check experiments (3, for sub-project D)

per the F prompt: "2-3 sanity-check experiments wired to configs/ for sub-project D to review." The three configs from Section 4 fit this. Plus one ultra-short "smoke" config:

#### 4. `configs/multifocal_smoke.json`

10 rounds, 1 replication, M=2 affective agents. ~3 second runtime. for CI-tier smoke pre-checks.

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

so the deliverable is **4 new configs**: `multifocal_smoke.json`, `multifocal_homogeneous_affective.json`, `multifocal_clinical_mix.json`, `multifocal_assortative_choice.json`.

---

## known divergences from `pomdp_spec.md` v4

1. **simultaneous-moves vs Stackelberg in §12 step 4** (F4): pomdp_spec has the engaged partner update beliefs on `u_focal` *before* planning. We use simultaneous-moves to respect post-B+A decision #6 (no one-modality observations). Documented and intentional.
2. **all other multi-agent semantics match pomdp_spec §12 + §11** (F1, F2, F3, F5, F6).

---

## explicitly out of scope (F)

- **all-pairs-parallel round mode** (F1 extension seam in place; future work).
- **mutual-selection conflict semantics** (F1; not relevant under turn-taking).
- **mixed AIF + scripted-baseline populations** (F11; future work if needed).
- **Stackelberg ordering** (F4; would require regressing decision #6).
- **self-modeling** (F5; future work).
- **changes to `aif/` or `trust/`** (F6; F adds purely additive code in `experiment/`).
- **CvC / cogames** stack (per MISSION).
- **agent inventory cleanup** (sub-project C, already complete).
- **experiment / config pruning** (sub-project D — F delivers 4 new configs for D to inventory).
- **doc rewrite** (sub-project E).
- **paper updates** (`docs/paper/main.tex`).

---

## follow-up tasks (post-this-spec)

1. **`AllPairsProtocol`**: implement when an experiment needs simultaneous-pair throughput. ~80 LOC additive; does not touch existing code.
2. **`pairing_resolution: "mutual_required"`**: relevant only under all-pairs; defer with `AllPairsProtocol`.
3. **Stackelberg ordering as a `move_resolution: "stackelberg" | "simultaneous"` knob**: would require a new `aif`/`trust` API for one-modality `infer_states`. Intentionally deferred to avoid regressing decision #6. Revisit if a hypothesis specifically needs it.
4. **mixed AIF + scripted-baseline populations**: extend `create_agents_from_multi_focal_config` to handle `kind: "tit_for_tat" | "random" | ...` from `benchmark/baselines.py`. Worth ~50 LOC if D decides the scripted-baseline hypothesis space is interesting in multi-focal.
5. **rich-array logging**: Section 2's `_play_one_pair` flattens scalars only. Add an `include_arrays: true` mode that serializes per-round `q_pi`, `partner_beliefs` (as parquet, not CSV) for fine-grained post-hoc analysis.
6. **multi-focal CLI entry point**: `scripts/run_multi_focal.py` analogous to `scripts/run_experiment.py` for the existing single-focal runner. Defer to sub-project D's tooling pass.
7. **emergent-dynamics analysis hypothesis tests**: `analysis/multi_focal_hypotheses.py` with `test_n1_emergent_cooperation`, `test_n2_defection_cascade`, `test_n3_assortative_pairing`. Defer to sub-project D's hypothesis cleanup.

---

## handoff (per scoping doc)

on completion of this spec + its writing-plans plan:

1. commit this spec to `docs/superpowers/specs/`
2. commit implementation plan from writing-plans to `docs/superpowers/plans/`
3. append entry under "completed sub-projects" in the parent scoping doc
4. NOT start implementation in the same session — implementation runs in a fresh executing-plans session
