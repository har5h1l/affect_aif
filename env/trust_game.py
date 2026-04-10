"""Multi-partner trust game environment."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

import numpy as np

from env.partner import Partner
from agent.model.trust_game import TrustGameModel
from agent.model.payoffs import decode_action, payoff_to_index


class TrustGameEnv:
    """Ground-truth multi-partner trust game with type and stance dynamics."""

    def __init__(self, config: dict, seed: int | None = None):
        cfg = asdict(config) if is_dataclass(config) else dict(config)
        self.config = cfg
        self.seed = int(seed if seed is not None else cfg.get("random_seed", 42))
        self.rng = np.random.default_rng(self.seed)
        self.model = TrustGameModel(cfg)
        self.num_partners = int(cfg.get("num_partners", 4))
        self.num_rounds = int(cfg.get("num_rounds", 200))
        self.assignment_mode = str(cfg.get("assignment_mode", "random"))
        self.p_switch = float(cfg.get("p_switch", 0.05))
        self.observation_noise = float(cfg.get("observation_noise", 0.0))
        self.correlation_pairs = [tuple(pair) for pair in cfg.get("correlation_pairs", [])]
        self.correlation_strength = float(cfg.get("correlation_strength", 0.9))
        self.scheduled_type_switches = self._parse_scheduled_events(cfg.get("scheduled_type_switches", []), "to_type")
        self.scheduled_stance_switches = self._parse_scheduled_events(
            cfg.get("scheduled_stance_switches", []),
            "to_stance",
        )
        self.available_types = list(cfg.get("partner_types", self.model.partner_type_names))
        self.available_stances = list(cfg.get("stance_names", self.model.stance_names))
        self.type_lookup = {partner.type_name: partner for partner in self.model.partner_types}
        self.partners: list[Partner] = []
        self.active_partner: int | None = None
        self.round_idx = 0
        self.history: list[dict] = []

    def _parse_scheduled_events(self, events: list[dict], target_key: str) -> dict[int, list[dict]]:
        schedule: dict[int, list[dict]] = {}
        for event in events:
            round_number = int(event["round"])
            schedule.setdefault(round_number, []).append(
                {
                    "partner_idx": int(event["partner_idx"]),
                    target_key: str(event[target_key]),
                }
            )
        return schedule

    def _initial_types(self) -> list[str]:
        specified = self.config.get("initial_partner_types")
        if specified:
            return list(specified)
        if len(self.available_types) >= self.num_partners:
            return list(self.available_types[: self.num_partners])
        return [str(self.rng.choice(self.available_types)) for _ in range(self.num_partners)]

    def _initial_stances(self) -> list[str]:
        specified = self.config.get("initial_partner_stances")
        if specified:
            return list(specified)
        return ["neutral"] * self.num_partners

    def _select_next_active_partner(self) -> int | None:
        if self.assignment_mode == "agent_choice":
            return None
        return int(self.rng.integers(self.num_partners))

    def _correlated_action(self, partner_idx: int) -> int | None:
        for i, j in self.correlation_pairs:
            if partner_idx == i and j < len(self.partners):
                return self.partners[j].last_partner_action
            if partner_idx == j and i < len(self.partners):
                return self.partners[i].last_partner_action
        return None

    def _apply_scheduled_type_switches(self, round_number: int) -> set[int]:
        switched: set[int] = set()
        for event in self.scheduled_type_switches.get(int(round_number), []):
            partner_idx = int(event["partner_idx"])
            new_type = str(event["to_type"])
            if new_type not in self.type_lookup:
                raise ValueError(f"Unknown scheduled partner type '{new_type}'.")
            self.partners[partner_idx].force_type_switch(new_type)
            switched.add(partner_idx)
        return switched

    def _apply_scheduled_stance_switches(self, round_number: int) -> set[int]:
        switched: set[int] = set()
        for event in self.scheduled_stance_switches.get(int(round_number), []):
            partner_idx = int(event["partner_idx"])
            new_stance = str(event["to_stance"])
            if new_stance not in self.available_stances:
                raise ValueError(f"Unknown scheduled partner stance '{new_stance}'.")
            self.partners[partner_idx].force_stance_switch(new_stance)
            switched.add(partner_idx)
        return switched

    def reset(self) -> dict:
        """Reset the environment and return the initial control context."""

        self.rng = np.random.default_rng(self.seed)
        self.round_idx = 0
        self.history = []
        self.partners = [
            Partner(
                partner_idx=idx,
                type_name=type_name,
                stance_name=stance_name,
                type_lookup=self.type_lookup,
                rng=np.random.default_rng(int(self.rng.integers(2**31 - 1))),
                num_social_actions=self.model.num_social_actions,
            )
            for idx, (type_name, stance_name) in enumerate(zip(self._initial_types(), self._initial_stances()))
        ]
        self.active_partner = self._select_next_active_partner()
        return {
            "active_partner": self.active_partner,
            "observation": None,
            "observation_partner_idx": None,
            "round": self.round_idx,
            "true_types": [partner.type_name for partner in self.partners],
            "true_stances": [partner.stance_name for partner in self.partners],
        }

    def _partner_observed_action(self, social_action: int) -> int:
        return int(social_action)

    def step(self, agent_action: int) -> dict:
        """Execute one round of the trust game."""

        nsa = self.model.num_social_actions
        if self.assignment_mode == "agent_choice":
            partner_idx, social_action = decode_action(
                agent_action,
                num_partners=self.num_partners,
                assignment_mode=self.assignment_mode,
                num_social_actions=nsa,
            )
        else:
            partner_idx, social_action = decode_action(
                agent_action,
                num_partners=self.num_partners,
                assignment_mode=self.assignment_mode,
                active_partner=self.active_partner,
                num_social_actions=nsa,
            )

        scheduled_type_switched = self._apply_scheduled_type_switches(self.round_idx + 1)
        scheduled_stance_switched = self._apply_scheduled_stance_switches(self.round_idx + 1)
        partner = self.partners[partner_idx]
        true_partner_type = partner.type_name
        true_partner_stance = partner.stance_name
        correlated_action = self._correlated_action(partner_idx)
        partner_action = partner.plan_and_act(
            correlation_action=correlated_action,
            correlation_strength=self.correlation_strength,
        )

        agent_payoff = float(self.model.payoff_matrix[social_action, partner_action, 0])
        partner_payoff = float(self.model.payoff_matrix[social_action, partner_action, 1])
        observed_partner_action = partner_action
        if self.observation_noise > 0.0 and self.rng.random() < self.observation_noise:
            observed_partner_action = 1 - observed_partner_action
        payoff_obs = payoff_to_index(agent_payoff, self.model.payoff_levels)

        partner.observe_outcome(
            agent_action=self._partner_observed_action(social_action),
            partner_action=partner_action,
            partner_payoff=partner_payoff,
            agent_payoff=agent_payoff,
        )
        stochastic_type_switch = partner.maybe_switch_type(self.available_types, self.p_switch)
        type_switched = (partner_idx in scheduled_type_switched) or stochastic_type_switch
        stance_switched = partner_idx in scheduled_stance_switched
        switch_kind = (
            "scheduled_type"
            if partner_idx in scheduled_type_switched
            else "scheduled_stance"
            if partner_idx in scheduled_stance_switched
            else "stochastic_type"
            if stochastic_type_switch
            else "none"
        )

        self.round_idx += 1
        self.active_partner = self._select_next_active_partner()
        result = {
            "partner_idx": partner_idx,
            "partner_action": partner_action,
            "agent_action": social_action,
            "raw_action": int(agent_action),
            "agent_payoff": agent_payoff,
            "partner_payoff": partner_payoff,
            "observation": [int(observed_partner_action), int(payoff_obs)],
            "observation_partner_idx": partner_idx,
            "active_partner": self.active_partner,
            "round": self.round_idx,
            "type_switched": bool(type_switched),
            "stance_switched": bool(stance_switched),
            "switch_kind": switch_kind,
            "current_partner_switched": bool(type_switched or stance_switched),
            "current_partner_scheduled_switch": bool(partner_idx in scheduled_type_switched),
            "current_partner_scheduled_stance_switch": bool(partner_idx in scheduled_stance_switched),
            "scheduled_switch_partner_ids": sorted(int(idx) for idx in scheduled_type_switched),
            "scheduled_stance_switch_partner_ids": sorted(int(idx) for idx in scheduled_stance_switched),
            "true_partner_type": true_partner_type,
            "true_partner_stance": true_partner_stance,
            "true_types": [item.type_name for item in self.partners],
            "true_stances": [item.stance_name for item in self.partners],
        }
        self.history.append(result)
        return result

    def get_partner_type(self, partner_idx: int) -> str:
        """Return the current ground-truth type for a partner."""

        return self.partners[partner_idx].type_name

    def get_episode_summary(self) -> dict:
        """Return coarse summary statistics for the current episode."""

        payoffs = (
            np.asarray([row["agent_payoff"] for row in self.history], dtype=float) if self.history else np.asarray([])
        )
        return {
            "num_rounds": len(self.history),
            "cumulative_payoff": float(payoffs.sum()) if len(payoffs) else 0.0,
            "mean_payoff": float(payoffs.mean()) if len(payoffs) else 0.0,
            "type_switches": int(sum(int(row["type_switched"]) for row in self.history)),
            "stance_switches": int(sum(int(row["stance_switched"]) for row in self.history)),
        }
