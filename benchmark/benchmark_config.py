"""Benchmark configuration and agent declarations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from experiments.trust.conditions import CONDITIONS, PRESET_CONDITIONS

DEFAULT_BACKENDS = ["trust"]
DEFAULT_OUTPUT_DIR = "results/benchmark"
SCHEMA_VERSION = 2


@dataclass
class AgentSpec:
    """Agent declaration used by benchmark backends."""

    name: str
    backend: str = "trust"
    kind: str = "registry"
    implementation: str | None = None
    policy_spec: str | None = None
    config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_raw(cls, raw: str | dict[str, Any], default_backend: str = "trust") -> AgentSpec:
        if isinstance(raw, str):
            return cls(
                name=raw,
                backend=default_backend,
                kind="registry",
                implementation=raw,
            )

        data = dict(raw)
        backend = str(data.get("backend", default_backend))
        kind = str(data.get("kind", "registry"))
        name = str(data.get("name") or data.get("implementation") or data.get("policy_spec"))
        implementation = data.get("implementation")
        policy_spec = data.get("policy_spec")

        if implementation is None and kind == "registry":
            implementation = name

        return cls(
            name=name,
            backend=backend,
            kind=kind,
            implementation=None if implementation is None else str(implementation),
            policy_spec=None if policy_spec is None else str(policy_spec),
            config=dict(data.get("config", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark runs across explicit backends."""

    backends: list[str] = field(default_factory=lambda: DEFAULT_BACKENDS[:])
    agents: list[AgentSpec] = field(
        default_factory=lambda: [
            AgentSpec(name="tau4_affect", backend="trust", implementation="tau4_affect"),
            AgentSpec(name="tau4_no_affect", backend="trust", implementation="tau4_no_affect"),
            AgentSpec(name="random", backend="trust", implementation="random"),
            AgentSpec(name="tit_for_tat", backend="trust", implementation="tit_for_tat"),
        ]
    )
    num_replications: int = 10
    num_rounds: int = 100
    output_dir: str = DEFAULT_OUTPUT_DIR
    random_seed: int = 42
    backend_configs: dict[str, dict[str, Any]] = field(default_factory=dict)
    observatory: dict[str, Any] | None = None

    def __post_init__(self):
        self.backends = [str(name) for name in self.backends] or DEFAULT_BACKENDS[:]
        self.agents = [
            agent if isinstance(agent, AgentSpec) else AgentSpec.from_raw(agent, self.backends[0])
            for agent in self.agents
        ]
        self.backend_configs = {str(name): dict(config) for name, config in dict(self.backend_configs).items()}
        self.observatory = None if self.observatory is None else dict(self.observatory)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkConfig:
        raw = dict(data)

        if "backends" not in raw:
            run_trust = bool(raw.pop("run_trust_game", True))
            run_gridworld = bool(raw.pop("run_gridworld", False))
            backends: list[str] = []
            if run_trust:
                backends.append("trust")
            if run_gridworld:
                backends.append("toy_gridworld")
            raw["backends"] = backends or DEFAULT_BACKENDS[:]

        backend_configs = dict(raw.get("backend_configs", {}))

        legacy_scenario = raw.pop("scenario", None)
        if legacy_scenario is not None:
            backend_configs.setdefault("trust", {})
            backend_configs["trust"].setdefault("scenario", legacy_scenario)
            backend_configs.setdefault("toy_gridworld", {})
            backend_configs["toy_gridworld"].setdefault("scenario", legacy_scenario)

        legacy_ticks = raw.pop("ticks_per_round", None)
        if legacy_ticks is not None:
            backend_configs.setdefault("toy_gridworld", {})
            backend_configs["toy_gridworld"].setdefault("ticks_per_round", legacy_ticks)

        legacy_trust_overrides = raw.pop("trust_game_overrides", None)
        if legacy_trust_overrides is not None:
            backend_configs.setdefault("trust", {})
            backend_configs["trust"].setdefault("trust_game_overrides", legacy_trust_overrides)

        raw["backend_configs"] = backend_configs

        default_backend = raw["backends"][0] if raw["backends"] else "trust"
        raw_agents = raw.get("agents")
        if raw_agents is not None:
            raw["agents"] = [AgentSpec.from_raw(agent, default_backend) for agent in raw_agents]

        return cls(**raw)

    @classmethod
    def from_json(cls, path: str) -> BenchmarkConfig:
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    def to_json(self, path: str):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["agents"] = [agent.to_dict() for agent in self.agents]
        target.write_text(json.dumps(payload, indent=2))


# Trust and toy-gridworld backends share the same registry because both operate on
# the trust-game action protocol. Real CvC runs use explicit policy specs instead.
AGENT_REGISTRY = {
    **{spec.name: {"type": "aif", "condition": condition_id} for condition_id, spec in CONDITIONS.items()},
    **{spec.name: {"type": "aif", "preset": preset_name} for preset_name, spec in PRESET_CONDITIONS.items()},
    # Baseline agents
    "random": {"type": "baseline", "class": "RandomAgent"},
    "tit_for_tat": {"type": "baseline", "class": "TitForTatAgent"},
    "win_stay_lose_shift": {"type": "baseline", "class": "WinStayLoseShiftAgent"},
    "pavlov": {"type": "baseline", "class": "PavlovAgent"},
    "grim_trigger": {"type": "baseline", "class": "GrimTriggerAgent"},
    "q_learning": {"type": "baseline", "class": "QLearningAgent"},
}
