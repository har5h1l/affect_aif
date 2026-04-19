"""Config schema for multi-focal trust-game experiments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_VALID_ROUND_MODES = {"turn_taking"}  # F1: extension seam
_VALID_FOCAL_SELECTIONS = {"round_robin", "random"}  # F2
_VALID_ASSIGNMENT_MODES = {"random", "agent_choice"}  # F3
_VALID_AGENT_KINDS = {"base", "affective", "lesioned"}  # F11
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
    def from_dict(cls, raw: dict) -> MultiFocalConfig:
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
