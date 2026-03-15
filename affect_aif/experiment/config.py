"""Experiment configuration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from affect_aif.generative_model.partner_types import PARTNER_TYPE_ORDER


DEFAULT_SENSITIVITY_FACTORS = {
    "mu": [0.5, 0.75, 1.0, 1.25, 1.5],
    "lambda_smooth": [0.7, 0.8, 0.9, 0.95],
    "alpha_charge": [0.5, 1.0, 2.0],
    "sigma_0_sq": [0.1, 0.25, 0.4],
}


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
    initial_partner_types: list[str] | None = None
    scheduled_type_switches: list[dict] = field(default_factory=list)

    mutual_coop: tuple[float, float] = (3.0, 3.0)
    sucker: tuple[float, float] = (-1.0, 5.0)
    temptation: tuple[float, float] = (5.0, -1.0)
    mutual_defect: tuple[float, float] = (1.0, 1.0)

    gamma: float = 1.0
    lr: float = 0.1
    action_sampling: str = "marginal"
    affect_modulates_precision: bool = False
    use_parameter_learning: bool = False

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
    sensitivity_factors: dict[str, list[float]] | list[float] = field(
        default_factory=lambda: {name: values[:] for name, values in DEFAULT_SENSITIVITY_FACTORS.items()}
    )
    experiment_name: str = "primary"
    verbose: bool = False
    verbosity_mode: str = "stage_stream"
    verbosity_include_calibration: bool = True
    gif_after_run: bool = False
    gif_output_dir: str | None = None

    def __post_init__(self):
        if isinstance(self.sensitivity_factors, dict):
            normalized = {}
            for key, defaults in DEFAULT_SENSITIVITY_FACTORS.items():
                normalized[key] = [float(value) for value in self.sensitivity_factors.get(key, defaults)]
        else:
            normalized = {
                "mu": [float(value) for value in self.sensitivity_factors],
                "lambda_smooth": DEFAULT_SENSITIVITY_FACTORS["lambda_smooth"][:],
                "alpha_charge": DEFAULT_SENSITIVITY_FACTORS["alpha_charge"][:],
                "sigma_0_sq": DEFAULT_SENSITIVITY_FACTORS["sigma_0_sq"][:],
            }
        self.sensitivity_factors = normalized
        self.verbose = bool(self.verbose)
        self.verbosity_mode = str(self.verbosity_mode)
        self.verbosity_include_calibration = bool(self.verbosity_include_calibration)
        self.gif_after_run = bool(self.gif_after_run)
        self.gif_output_dir = None if self.gif_output_dir is None else str(self.gif_output_dir)

    @classmethod
    def from_dict(cls, data: dict) -> "ExperimentConfig":
        """Build a configuration from a raw dictionary."""

        data = dict(data)
        tuple_fields = ("mutual_coop", "sucker", "temptation", "mutual_defect")
        for key in tuple_fields:
            if key in data:
                data[key] = tuple(data[key])
        return cls(**data)

    @classmethod
    def from_json(cls, path: str) -> "ExperimentConfig":
        """Load a configuration from disk."""

        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    def to_json(self, path: str):
        """Serialize this configuration to disk."""

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), indent=2))
