"""Multi-focal-agent runtime for the trust game (sub-project F)."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from experiments.multifocal.config import MultiFocalConfig
from experiments.multifocal.joint_resolution import joint_resolve
from tasks.trust import TrustGameAgent


def _local_partner_idx(focal_global: int, other_global: int) -> int:
    """Global-to-local mapping. For focal F, partner P maps to local idx P if P<F else P-1."""
    if other_global == focal_global:
        raise ValueError("self-modeling not supported (F5)")
    return other_global if other_global < focal_global else other_global - 1


def _global_partner_idx(focal_global: int, local: int, M: int) -> int:
    """Inverse of _local_partner_idx."""
    return local if local < focal_global else local + 1


class RoundProtocol(Protocol):
    def select_pairs(
        self, round_idx: int, agents: list[TrustGameAgent], rng: np.random.Generator
    ) -> list[tuple[int, int | None]]:
        """Return (focal_global_idx, engaged_global_idx_or_None) pairs.

        For turn-taking, len()==1 and engaged is None (resolved later in the runner).
        """
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
        else:
            focal = int(rng.integers(M))
        return [(focal, None)]


_PROTOCOLS: dict[str, type] = {"turn_taking": TurnTakingProtocol}


class MultiFocalRunner:
    """Drive M TrustGameAgents through a multi-focal trust game.

    ``MultiFocalConfig.num_replications`` / ``logging`` are parsed for future batch
    drivers; this class only runs one population for ``num_rounds``.
    """

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
                    f"agent[{i}] has num_partners={a.num_partners}; expected M-1={self.M - 1} (F5: no self-modeling)"
                )

    def run(self) -> list[dict]:
        """Run num_rounds. Returns long-format rows (F9): one row per (round, agent_in_pair)."""
        rows: list[dict] = []
        for t in range(self.config.num_rounds):
            for focal_g, _placeholder in self.protocol.select_pairs(t, self.agents, self.rng):
                rows.extend(self._play_one_pair(t, focal_g))
        return rows

    def _play_one_pair(self, t: int, focal_g: int) -> list[dict]:
        focal = self.agents[focal_g]

        if self.config.assignment_mode == "agent_choice":
            focal.plan_and_act(active_partner=None)
            local_p = int(focal.selected_partner)
            focal_action = int(focal.selected_action)
            engaged_g = _global_partner_idx(focal_g, local_p, self.M)
        elif self.config.assignment_mode == "random":
            other_globals = [g for g in range(self.M) if g != focal_g]
            engaged_g = int(self.rng.choice(other_globals))
            local_p = _local_partner_idx(focal_g, engaged_g)
            focal.plan_and_act(active_partner=local_p)
            focal_action = int(focal.selected_action)
        else:
            raise ValueError(f"unknown assignment_mode={self.config.assignment_mode!r}")

        engaged = self.agents[engaged_g]
        local_f_in_engaged = _local_partner_idx(engaged_g, focal_g)
        engaged.plan_and_act(active_partner=local_f_in_engaged)
        engaged_action = int(engaged.selected_action)

        focal_payoff_obs, focal_payoff_value = joint_resolve(focal_action, engaged_action, focal.model)
        engaged_payoff_obs, engaged_payoff_value = joint_resolve(engaged_action, focal_action, engaged.model)

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

        rows: list[dict] = []
        for agent_g, agent, is_focal in [(focal_g, focal, True), (engaged_g, engaged, False)]:
            rows.append(self._row_for(agent_g, agent, t, focal_g, engaged_g, is_focal))
        return rows

    def _row_for(
        self,
        agent_g: int,
        agent: TrustGameAgent,
        t: int,
        focal_g: int,
        engaged_g: int,
        is_focal: bool,
    ) -> dict:
        metrics = agent.get_metrics()
        scalars = {k: v for k, v in metrics.items() if not _is_array(v)}
        arrays = {k: np.asarray(v, dtype=float).tolist() for k, v in metrics.items() if _is_array(v)}
        return {
            "round": t,
            "focal_idx": focal_g,
            "engaged_partner_global_idx": engaged_g,
            "agent_global_idx": agent_g,
            "agent_kind": getattr(agent, "_kind_label", "base"),
            "is_focal_this_round": bool(is_focal),
            **scalars,
            **arrays,
        }


def _is_array(v) -> bool:
    return isinstance(v, np.ndarray) and v.ndim > 0
