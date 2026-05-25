"""Benchmark configuration and agent declarations."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised only on Python < 3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

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
        name = str(data.get("name") or data.get("implementation"))
        implementation = data.get("implementation")

        if implementation is None and kind == "registry":
            implementation = name

        return cls(
            name=name,
            backend=backend,
            kind=kind,
            implementation=None if implementation is None else str(implementation),
            config=dict(data.get("config", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, str):
        return repr(value).replace("'", '"')
    if isinstance(value, list | tuple):
        return "[" + ", ".join(_format_toml_value(item) for item in value) + "]"
    if value is None:
        raise TypeError("TOML does not support null values in benchmark configs.")
    raise TypeError(f"Unsupported TOML value type: {type(value).__name__}")


def _write_table(lines: list[str], table_name: str, data: dict[str, Any]):
    scalar_items: dict[str, Any] = {}
    nested_tables: dict[str, dict[str, Any]] = {}
    array_tables: dict[str, list[dict[str, Any]]] = {}

    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, dict):
            nested_tables[str(key)] = value
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            array_tables[str(key)] = value
        else:
            scalar_items[str(key)] = value

    if scalar_items:
        lines.append(f"[{table_name}]")
        for key, value in scalar_items.items():
            lines.append(f"{key} = {_format_toml_value(value)}")
        lines.append("")

    for key, value in nested_tables.items():
        _write_table(lines, f"{table_name}.{key}", value)

    for key, values in array_tables.items():
        for item in values:
            lines.append(f"[[{table_name}.{key}]]")
            for item_key, item_value in item.items():
                if item_value is not None:
                    lines.append(f"{item_key} = {_format_toml_value(item_value)}")
            lines.append("")


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark runs across explicit backends."""

    backends: list[str] = field(default_factory=lambda: DEFAULT_BACKENDS[:])
    agents: list[AgentSpec] = field(
        default_factory=lambda: [
            AgentSpec(name="affect", backend="trust", implementation="affect"),
            AgentSpec(name="no_affect", backend="trust", implementation="no_affect"),
            AgentSpec(name="random", backend="trust", implementation="random"),
            AgentSpec(name="tit_for_tat", backend="trust", implementation="tit_for_tat"),
        ]
    )
    num_replications: int = 10
    num_rounds: int = 100
    output_dir: str = DEFAULT_OUTPUT_DIR
    random_seed: int = 42
    backend_configs: dict[str, dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        self.backends = [str(name) for name in self.backends] or DEFAULT_BACKENDS[:]
        self.agents = [
            agent if isinstance(agent, AgentSpec) else AgentSpec.from_raw(agent, self.backends[0])
            for agent in self.agents
        ]
        self.backend_configs = {str(name): dict(config) for name, config in dict(self.backend_configs).items()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BenchmarkConfig:
        raw = dict(data)
        raw["backends"] = [str(name) for name in raw.get("backends", DEFAULT_BACKENDS[:])] or DEFAULT_BACKENDS[:]
        backend_configs = dict(raw.get("backend_configs", {}))
        raw["backend_configs"] = backend_configs

        default_backend = raw["backends"][0] if raw["backends"] else "trust"
        raw_agents = raw.get("agents")
        if raw_agents is not None:
            raw["agents"] = [AgentSpec.from_raw(agent, default_backend) for agent in raw_agents]

        return cls(**raw)

    @classmethod
    def from_toml(cls, path: str | Path) -> BenchmarkConfig:
        data = tomllib.loads(Path(path).read_text())
        return cls.from_dict(data)

    @classmethod
    def from_experiment_spec(cls, spec) -> BenchmarkConfig:
        if spec.experiment.family != "benchmark" or spec.benchmark is None:
            raise ValueError("BenchmarkConfig requires a benchmark ExperimentSpec")

        backend_configs: dict[str, dict[str, Any]] = {}
        if spec.benchmark.trust:
            backend_configs["trust"] = dict(spec.benchmark.trust)

        agents = list(spec.benchmark.agent_specs) if spec.benchmark.agent_specs else list(spec.benchmark.agents)
        payload: dict[str, Any] = {
            "backends": list(spec.benchmark.backends),
            "agents": agents,
            "num_replications": spec.experiment.replications,
            "num_rounds": spec.experiment.rounds,
            "output_dir": f"results/{spec.hypothesis.id}/{spec.experiment.id}",
            "random_seed": spec.experiment.seed,
            "backend_configs": backend_configs,
        }
        return cls.from_dict(payload)

    @classmethod
    def from_json(cls, path: str | Path) -> BenchmarkConfig:
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    def to_toml(self, path: str | Path):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["agents"] = [agent.to_dict() for agent in self.agents]

        lines: list[str] = [
            f"backends = {_format_toml_value(payload['backends'])}",
            f"num_replications = {_format_toml_value(payload['num_replications'])}",
            f"num_rounds = {_format_toml_value(payload['num_rounds'])}",
            f"output_dir = {_format_toml_value(payload['output_dir'])}",
            f"random_seed = {_format_toml_value(payload['random_seed'])}",
            "",
        ]
        for agent in payload["agents"]:
            lines.append("[[agents]]")
            for key, value in agent.items():
                if value is not None and value != {}:
                    lines.append(f"{key} = {_format_toml_value(value)}")
            lines.append("")

        for backend_name, backend_config in payload["backend_configs"].items():
            _write_table(lines, f"backend_configs.{backend_name}", backend_config)

        target.write_text("\n".join(lines).rstrip() + "\n")

    def to_json(self, path: str | Path):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["agents"] = [agent.to_dict() for agent in self.agents]
        target.write_text(json.dumps(payload, indent=2))


# Trust-task evaluation agents use the registry.
AGENT_REGISTRY = {
    "no_affect": {
        "type": "aif",
        "variant": {"affect": "none", "planning_horizon": 4, "epistemic_value": True},
    },
    "no_affect_horizon_1": {
        "type": "aif",
        "variant": {"affect": "none", "planning_horizon": 1, "epistemic_value": True},
    },
    "no_affect_horizon_2": {
        "type": "aif",
        "variant": {"affect": "none", "planning_horizon": 2, "epistemic_value": True},
    },
    "no_affect_horizon_8": {
        "type": "aif",
        "variant": {"affect": "none", "planning_horizon": 8, "epistemic_value": True},
    },
    "affect": {
        "type": "aif",
        "variant": {"affect": "precision", "planning_horizon": 4, "epistemic_value": True},
    },
    "affect_horizon_1": {
        "type": "aif",
        "variant": {"affect": "precision", "planning_horizon": 1, "epistemic_value": True},
    },
    "affect_horizon_2": {
        "type": "aif",
        "variant": {"affect": "precision", "planning_horizon": 2, "epistemic_value": True},
    },
    "affect_horizon_8": {
        "type": "aif",
        "variant": {"affect": "precision", "planning_horizon": 8, "epistemic_value": True},
    },
    "no_epistemic": {
        "type": "aif",
        "variant": {"affect": "none", "planning_horizon": 4, "epistemic_value": False},
    },
    "tracked_only": {
        "type": "aif",
        "variant": {"affect": "tracked_only", "planning_horizon": 4, "epistemic_value": True},
    },
    "lesioned": {
        "type": "aif",
        "variant": {"affect": "tracked_only", "planning_horizon": 4, "epistemic_value": True},
    },
    "alexithymia": {
        "type": "aif",
        "variant": {"affect": "precision", "planning_horizon": 4, "alpha_charge": 0.1},
    },
    "borderline": {
        "type": "aif",
        "variant": {"affect": "precision", "planning_horizon": 4, "alpha_charge": 12.0},
    },
    "depression": {
        "type": "aif",
        "variant": {"affect": "precision", "planning_horizon": 4, "initial_beta": 2.0},
    },
    # Baseline agents
    "random": {"type": "baseline", "class": "RandomAgent"},
    "tit_for_tat": {"type": "baseline", "class": "TitForTatAgent"},
    "win_stay_lose_shift": {"type": "baseline", "class": "WinStayLoseShiftAgent"},
    "pavlov": {"type": "baseline", "class": "PavlovAgent"},
    "grim_trigger": {"type": "baseline", "class": "GrimTriggerAgent"},
    "q_learning": {"type": "baseline", "class": "QLearningAgent"},
}
