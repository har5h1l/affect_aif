"""Runtime configuration for trust experiments."""

from __future__ import annotations

from dataclasses import dataclass, field

from tasks.trust.types import PARTNER_TYPE_ORDER


@dataclass
class ExperimentConfig:
    """Concrete runtime hyperparameters after TOML spec expansion."""

    num_partners: int = 4
    num_rounds: int = 200
    p_switch: float = 0.05
    assignment_mode: str = "random"
    observation_noise: float = 0.0
    correlation_pairs: list[list[int]] = field(default_factory=list)
    correlation_strength: float = 0.9
    initial_partner_types: list[str] | None = None
    initial_partner_stances: list[str] | None = None
    scheduled_type_switches: list[dict] = field(default_factory=list)
    scheduled_stance_switches: list[dict] = field(default_factory=list)

    payoff_mode: str = "binary"
    num_investment_levels: int = 6
    endowment: float = 10.0
    multiplier: float = 3.0

    mutual_coop: tuple[float, float] = (3.0, 3.0)
    sucker: tuple[float, float] = (-1.0, 5.0)
    temptation: tuple[float, float] = (5.0, -1.0)
    mutual_defect: tuple[float, float] = (1.0, 1.0)

    gamma: float = 1.0
    action_sampling: str = "marginal"
    max_policies: int = 4096
    debug_mode: bool = False
    log_policy_traces: bool = False

    alpha_charge: float = 3.0
    sigma_0_sq: float = 0.25
    initial_beta: float = 1.0
    beta_num_levels: int = 5
    beta_levels: list[float] | None = None
    beta_persistence: float = 0.8

    num_replications: int = 1
    random_seed: int = 42
    partner_types: list[str] = field(default_factory=lambda: list(PARTNER_TYPE_ORDER))

    def __post_init__(self):
        self.num_partners = int(self.num_partners)
        self.num_rounds = int(self.num_rounds)
        self.num_replications = int(self.num_replications)
        self.random_seed = int(self.random_seed)
        self.debug_mode = bool(self.debug_mode)
        self.log_policy_traces = bool(self.log_policy_traces or self.debug_mode)

    @classmethod
    def from_dict(cls, data: dict) -> ExperimentConfig:
        """Build a configuration from a raw dictionary."""

        data = dict(data)
        tuple_fields = ("mutual_coop", "sucker", "temptation", "mutual_defect")
        for key in tuple_fields:
            if key in data:
                data[key] = tuple(data[key])
        return cls(**data)
