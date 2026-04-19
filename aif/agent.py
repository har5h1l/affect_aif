"""Agent container for active inference state."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Agent:
    """Stateful POMDP container."""

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
        """Reset the posterior to the initial-state prior."""

        prior = np.asarray(self.D, dtype=object)
        qs = np.empty(len(prior), dtype=object)
        for idx, factor_prior in enumerate(prior):
            qs[idx] = np.asarray(factor_prior, dtype=float).copy()
        self.qs = qs
