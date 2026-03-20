"""Scripted gridworld partner policies that mirror trust game partner types.

These policies control non-focal agents in the MettaGrid/CoGames environment,
producing behavior patterns that map to cooperator, reciprocator, exploiter,
and random partner types from the trust game.
"""

from __future__ import annotations

import numpy as np

from affect_aif.benchmark.interaction_tracker import InteractionEvent


class ScriptedPartner:
    """Base class for scripted gridworld partner policies."""

    def __init__(self, partner_idx: int, seed: int = 0):
        self.partner_idx = partner_idx
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self._interaction_count = 0
        self._focal_last_action: int | None = None  # last action focal agent took toward us

    @property
    def type_name(self) -> str:
        return self.__class__.__name__.lower().replace("partner", "")

    def reset(self):
        self.rng = np.random.default_rng(self.seed)
        self._interaction_count = 0
        self._focal_last_action = None

    def decide(self) -> str:
        """Return 'share' or 'attack' as the intended action."""
        raise NotImplementedError

    def observe_focal_action(self, action_type: str):
        """Record what the focal agent did to us."""
        if action_type in ("share", "receive"):
            self._focal_last_action = 0  # cooperate
        elif action_type in ("attack", "steal"):
            self._focal_last_action = 1  # defect
        self._interaction_count += 1


class CooperatorPartner(ScriptedPartner):
    """Always shares resources with the focal agent (p_share=0.9)."""

    def __init__(self, partner_idx: int, seed: int = 0, p_share: float = 0.9):
        super().__init__(partner_idx, seed)
        self.p_share = p_share

    def decide(self) -> str:
        return "share" if self.rng.random() < self.p_share else "attack"


class ReciprocatorPartner(ScriptedPartner):
    """Mirrors the focal agent's last action. Cooperates initially."""

    def __init__(self, partner_idx: int, seed: int = 0, noise: float = 0.1):
        super().__init__(partner_idx, seed)
        self.noise = noise

    def decide(self) -> str:
        if self._focal_last_action is None:
            return "share"  # cooperate initially

        if self.rng.random() < self.noise:
            return "share" if self.rng.random() < 0.5 else "attack"

        return "share" if self._focal_last_action == 0 else "attack"


class ExploiterPartner(ScriptedPartner):
    """Cooperates initially, then switches to exploitation after switch_round.

    Mirrors the trust game's exploiter partner type.
    """

    def __init__(
        self,
        partner_idx: int,
        seed: int = 0,
        switch_round: int = 20,
        p_share_early: float = 0.9,
        p_share_late: float = 0.1,
    ):
        super().__init__(partner_idx, seed)
        self.switch_round = switch_round
        self.p_share_early = p_share_early
        self.p_share_late = p_share_late

    @property
    def type_name(self) -> str:
        return "exploiter"

    def decide(self) -> str:
        if self._interaction_count < self.switch_round:
            return "share" if self.rng.random() < self.p_share_early else "attack"
        return "share" if self.rng.random() < self.p_share_late else "attack"


class RandomPartner(ScriptedPartner):
    """Shares or attacks with equal probability."""

    def __init__(self, partner_idx: int, seed: int = 0, p_share: float = 0.5):
        super().__init__(partner_idx, seed)
        self.p_share = p_share

    @property
    def type_name(self) -> str:
        return "random"

    def decide(self) -> str:
        return "share" if self.rng.random() < self.p_share else "attack"


PARTNER_TYPE_MAP = {
    "cooperator": CooperatorPartner,
    "reciprocator": ReciprocatorPartner,
    "exploiter": ExploiterPartner,
    "random": RandomPartner,
}


def create_partner(type_name: str, partner_idx: int, seed: int = 0, **kwargs) -> ScriptedPartner:
    """Create a scripted partner by type name."""
    if type_name not in PARTNER_TYPE_MAP:
        available = ", ".join(sorted(PARTNER_TYPE_MAP.keys()))
        raise ValueError(f"Unknown partner type '{type_name}'. Available: {available}")
    return PARTNER_TYPE_MAP[type_name](partner_idx=partner_idx, seed=seed, **kwargs)
