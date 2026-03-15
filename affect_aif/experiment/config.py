"""Experiment configuration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from affect_aif.generative_model.partner_types import PARTNER_TYPE_ORDER


@dataclass
class ExperimentConfig:
    """All experiment hyperparameters in one place."""

    num_partners: int = 4
    num_rounds: int = 200
    p_switch: float = 0.05
    assignment_mode: str = "random"
    observation_noise: float = 0.0
    correlation_pairs: list[list[int]] = field(default_factory=list)
    correlation_strength: float = 0.9

    mutual_coop: tuple[float, float] = (3.0, 3.0)
    sucker: tuple[float, float] = (-1.0, 5.0)
    temptation: tuple[float, float] = (5.0, -1.0)
    mutual_defect: tuple[float, float] = (1.0, 1.0)

    gamma: float = 1.0
    lr: float = 0.1
    action_sampling: str = "marginal"
    affect_modulates_precision: bool = False

    deep_horizon: int = 8
    shallow_horizon: int = 2
    max_policies: int = 4096

    lambda_smooth: float = 0.9
    alpha_charge: float = 1.0
    sigma_0_sq: float = 0.25
    mu: float | None = None
    initial_beta: float = 0.5

    lesion_mode: str = "decouple"

    num_replications: int = 100
    calibration_episodes: int = 20
    random_seed: int = 42
    conditions: list[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    partner_types: list[str] = field(default_factory=lambda: list(PARTNER_TYPE_ORDER))

    run_sensitivity: bool = False
    sensitivity_factors: list[float] = field(default_factory=lambda: [0.5, 0.75, 1.0, 1.25, 1.5])
    experiment_name: str = "primary"

    @classmethod
    def from_json(cls, path: str) -> "ExperimentConfig":
        """Load a configuration from disk."""

        data = json.loads(Path(path).read_text())
        tuple_fields = ("mutual_coop", "sucker", "temptation", "mutual_defect")
        for key in tuple_fields:
            if key in data:
                data[key] = tuple(data[key])
        return cls(**data)

    def to_json(self, path: str):
        """Serialize this configuration to disk."""

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2))
