"""Multi-focal-agent runtime for the trust game (sub-project F)."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from experiments.multifocal.config import MultiFocalConfig
from experiments.multifocal.joint_resolution import joint_resolve
from experiments.trust.factory import NativeTrustRuntime
from tasks.trust.runtime import (
    Decision,
    PartnerSnapshot,
    predictive_log_likelihood,
    select_decision,
    snapshot_partner_bank,
    update_beta_after_observation,
    update_partner_after_observation,
)


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
        self, round_idx: int, agents: list[NativeTrustRuntime], rng: np.random.Generator
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
    """Drive M native trust runtimes through a multi-focal trust game.

    ``MultiFocalConfig.num_replications`` / ``logging`` are parsed for future batch
    drivers; this class only runs one population for ``num_rounds``.
    """

    def __init__(self, config: MultiFocalConfig, agents: list[NativeTrustRuntime], rng: np.random.Generator):
        self.config = config
        self.agents = list(agents)
        self.M = len(agents)
        self.rng = rng
        self.protocol = _PROTOCOLS[config.round_mode](focal_selection=config.focal_selection)
        self._validate_population()

    def _validate_population(self) -> None:
        if self.M < 2:
            raise ValueError(f"multi-focal requires >= 2 agents; got {self.M}")
        payoff_modes = {a.template.payoff_mode for a in self.agents}
        if len(payoff_modes) > 1:
            raise ValueError(f"all agents must share payoff_mode; got {payoff_modes}")
        nsas = {a.template.num_social_actions for a in self.agents}
        if len(nsas) > 1:
            raise ValueError(f"all agents must share num_social_actions; got {nsas}")
        for i, a in enumerate(self.agents):
            if len(a.partner_bank.agents) != self.M - 1:
                raise ValueError(
                    f"agent[{i}] has num_partners={len(a.partner_bank.agents)}; expected M-1={self.M - 1} "
                    "(F5: no self-modeling)"
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
            focal_decision = self._select(focal, active_partner=None)
            local_p = int(focal_decision.selected_partner)
            focal_action = int(focal_decision.selected_action)
            engaged_g = _global_partner_idx(focal_g, local_p, self.M)
        elif self.config.assignment_mode == "random":
            other_globals = [g for g in range(self.M) if g != focal_g]
            engaged_g = int(self.rng.choice(other_globals))
            local_p = _local_partner_idx(focal_g, engaged_g)
            focal_decision = self._select(focal, active_partner=local_p)
            focal_action = int(focal_decision.selected_action)
        else:
            raise ValueError(f"unknown assignment_mode={self.config.assignment_mode!r}")

        engaged = self.agents[engaged_g]
        local_f_in_engaged = _local_partner_idx(engaged_g, focal_g)
        engaged_decision = self._select(engaged, active_partner=local_f_in_engaged)
        engaged_action = int(engaged_decision.selected_action)

        focal_payoff_obs, _ = joint_resolve(focal_action, engaged_action, focal.template)
        engaged_payoff_obs, _ = joint_resolve(engaged_action, focal_action, engaged.template)

        focal_snapshot = self._update(
            runtime=focal,
            decision=focal_decision,
            partner_idx=local_p,
            observation=[int(engaged_action), int(focal_payoff_obs)],
            observed_partner_action=int(engaged_action),
            own_action=int(focal_action),
        )
        engaged_snapshot = self._update(
            runtime=engaged,
            decision=engaged_decision,
            partner_idx=local_f_in_engaged,
            observation=[int(focal_action), int(engaged_payoff_obs)],
            observed_partner_action=int(focal_action),
            own_action=int(engaged_action),
        )

        rows: list[dict] = []
        rows.append(self._row_for(focal_g, focal, focal_decision, focal_snapshot, t, focal_g, engaged_g, True))
        rows.append(self._row_for(engaged_g, engaged, engaged_decision, engaged_snapshot, t, focal_g, engaged_g, False))
        return rows

    def _select(self, runtime: NativeTrustRuntime, active_partner: int | None) -> Decision:
        return select_decision(
            bank=runtime.partner_bank,
            template=runtime.template,
            active_partner=active_partner,
            assignment_mode=self.config.assignment_mode if active_partner is None else "random",
            base_gamma=runtime.base_gamma,
            action_selection=runtime.action_selection,
            rng=runtime.rng,
            affect_mode=runtime.affect_mode,
        )

    def _update(
        self,
        *,
        runtime: NativeTrustRuntime,
        decision: Decision,
        partner_idx: int,
        observation: list[int],
        observed_partner_action: int,
        own_action: int,
    ) -> PartnerSnapshot:
        log_lik = predictive_log_likelihood(decision.predicted_partner_action_probs, observed_partner_action)
        runtime.partner_bank.round_log_evidence = log_lik
        runtime.partner_bank.cumulative_log_evidence += log_lik
        update_beta_after_observation(
            bank=runtime.partner_bank,
            partner_idx=partner_idx,
            predicted_partner_action_probs=decision.predicted_partner_action_probs,
            observed_partner_action=observed_partner_action,
            affect_mode=runtime.affect_mode,
        )
        update_partner_after_observation(
            bank=runtime.partner_bank,
            template=runtime.template,
            partner_idx=partner_idx,
            obs=observation,
            own_action=own_action,
        )
        return snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template)

    def _row_for(
        self,
        agent_g: int,
        runtime: NativeTrustRuntime,
        decision: Decision,
        snapshot: PartnerSnapshot,
        t: int,
        focal_g: int,
        engaged_g: int,
        is_focal: bool,
    ) -> dict:
        q_pi = np.asarray(decision.q_pi, dtype=float)
        entropy = float(-(q_pi * np.log(q_pi + 1e-16)).sum()) if q_pi.size else np.nan
        step_controls = int(np.prod(runtime.template.num_controls))
        planning_cost = float((step_controls**runtime.planning_horizon) * runtime.planning_horizon)
        planning_cost_ratio = float((step_controls**8) / max(step_controls**runtime.planning_horizon, 1))
        betas = (
            np.asarray(runtime.partner_bank.beta.expected_beta(), dtype=float)
            if runtime.partner_bank.beta is not None
            else np.full((len(runtime.partner_bank.agents),), np.nan, dtype=float)
        )
        errors = (
            np.asarray(runtime.partner_bank.latest_surprise, dtype=float)
            if runtime.partner_bank.latest_surprise is not None
            else np.full((len(runtime.partner_bank.agents),), np.nan, dtype=float)
        )
        return {
            "round": t,
            "focal_idx": focal_g,
            "engaged_partner_global_idx": engaged_g,
            "agent_global_idx": agent_g,
            "agent_kind": runtime.condition_name,
            "is_focal_this_round": bool(is_focal),
            "q_pi": q_pi.tolist(),
            "G": np.asarray(decision.policy_scores, dtype=float).tolist(),
            "best_policy_idx": int(decision.best_policy_idx),
            "selected_partner": int(decision.selected_partner),
            "selected_action": int(decision.selected_action),
            "raw_action": int(decision.raw_action),
            "q_pi_entropy": entropy,
            "planning_cost": planning_cost,
            "planning_cost_ratio": planning_cost_ratio,
            "round_log_evidence": float(runtime.partner_bank.round_log_evidence),
            "cumulative_log_evidence": float(runtime.partner_bank.cumulative_log_evidence),
            "mean_abs_step_efe": float(np.mean(np.abs(decision.policy_scores))) if decision.policy_scores.size else np.nan,
            "betas": betas.tolist(),
            "prediction_errors": errors.tolist(),
            "partner_beliefs": snapshot.partner_type_beliefs.tolist(),
            "partner_joint_beliefs": snapshot.partner_joint_beliefs.tolist(),
            "partner_joint_posteriors": snapshot.partner_joint_posteriors.tolist(),
        }
