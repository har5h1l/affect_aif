"""Generative model specification for the trust game."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

import numpy as np

from agent.inference.maths import log_stable, softmax
from agent.inference.utils import obj_array
from agent.model.types import (
    PARTNER_TYPE_ORDER,
    PartnerType,
    default_partner_type_params,
)
from agent.model.payoffs import (
    build_graded_payoff_matrix,
    build_payoff_matrix,
    decode_action,
    expected_agent_payoff,
    infer_payoff_levels,
    num_actions,
    payoff_distribution,
    payoff_to_index,
)
from agent.model.stance import (
    STANCE_ORDER,
    cooperation_evidence_strength,
    get_type_stance_cooperation_table,
    interpolate_stance_transition,
)


class _BaseTrustGameModel:
    """Shared trust-game POMDP with type and stance factors."""

    def __init__(self, config: dict):
        cfg = asdict(config) if is_dataclass(config) else dict(config)
        self.config = cfg
        self.num_partners = int(cfg.get("num_partners", 4))
        self.partner_type_names = tuple(cfg.get("partner_types", PARTNER_TYPE_ORDER))
        self.stance_names = tuple(cfg.get("stance_names", STANCE_ORDER))
        self.num_types = len(self.partner_type_names)
        self.num_stances = len(self.stance_names)
        self.p_switch = float(cfg.get("p_switch", 0.05))
        self.assignment_mode = str(cfg.get("assignment_mode", cfg.get("variant", "random")))
        self.observation_noise = float(cfg.get("observation_noise", 0.0))
        self.preference_temperature = float(cfg.get("preference_temperature", 1.0))
        self.partner_type_params = default_partner_type_params()
        self.partner_type_params.update(cfg.get("partner_type_params", {}))
        self.partner_types = [
            PartnerType(type_name=name, params=self.partner_type_params.get(name, {}))
            for name in self.partner_type_names
        ]

        self._init_payoffs(cfg)
        self.payoff_levels = infer_payoff_levels(self.payoff_matrix)
        self.num_obs = [2, len(self.payoff_levels)]
        self.num_controls = [num_actions(self.num_partners, self.assignment_mode, self.num_social_actions)]

        self.partner_action_prob_table = self._build_partner_action_prob_table()
        self.payoff_index_table = self._build_payoff_index_table()
        self.agent_payoff_table = self.payoff_matrix[:, :, 0]
        self.A = self.build_A()
        self.B = self.build_B()
        self.C = self.build_C()
        self.D = self.build_D()

    def _init_payoffs(self, cfg: dict) -> None:  # pragma: no cover - implemented by subclasses
        raise NotImplementedError

    def _build_partner_action_prob_table(self) -> np.ndarray:
        return get_type_stance_cooperation_table(self.partner_type_names)

    def _build_payoff_index_table(self) -> np.ndarray:
        indices = np.zeros((self.num_social_actions, 2), dtype=int)
        for agent_action in range(self.num_social_actions):
            for partner_action in range(2):
                payoff = self.payoff_matrix[agent_action, partner_action, 0]
                indices[agent_action, partner_action] = payoff_to_index(payoff, self.payoff_levels)
        return indices

    def social_action_for_action(self, action: int) -> int:
        if self.assignment_mode == "agent_choice":
            _, social_action = decode_action(
                int(action),
                self.num_partners,
                self.assignment_mode,
                num_social_actions=self.num_social_actions,
            )
            return int(social_action)
        return int(action)

    def build_A(self) -> np.ndarray:
        """Build likelihood tensors for action and payoff observations."""

        A = obj_array(2)
        partner_action = np.zeros((2, self.num_types, self.num_stances), dtype=float)
        for type_idx in range(self.num_types):
            for stance_idx in range(self.num_stances):
                p_coop = self.partner_action_prob_table[type_idx, stance_idx]
                clean = np.asarray([p_coop, 1.0 - p_coop], dtype=float)
                noisy = (1.0 - self.observation_noise) * clean + self.observation_noise * 0.5
                partner_action[:, type_idx, stance_idx] = noisy

        payoff_obs = np.zeros((len(self.payoff_levels), self.num_social_actions, self.num_types, self.num_stances), dtype=float)
        for agent_action in range(self.num_social_actions):
            for type_idx in range(self.num_types):
                for stance_idx in range(self.num_stances):
                    p_coop = self.partner_action_prob_table[type_idx, stance_idx]
                    coop_idx = int(self.payoff_index_table[agent_action, 0])
                    defect_idx = int(self.payoff_index_table[agent_action, 1])
                    payoff_obs[coop_idx, agent_action, type_idx, stance_idx] += p_coop
                    payoff_obs[defect_idx, agent_action, type_idx, stance_idx] += 1.0 - p_coop

        A[0] = partner_action
        A[1] = payoff_obs
        return A

    def build_B(self) -> np.ndarray:
        """Build transition tensors for type, stance, and own action."""

        B = obj_array(3)
        num_actions_total = self.num_controls[0]

        type_transition = np.full(
            (self.num_types, self.num_types), self.p_switch / max(self.num_types - 1, 1), dtype=float
        )
        np.fill_diagonal(type_transition, 1.0 - self.p_switch)
        B[0] = np.repeat(type_transition[:, :, None], num_actions_total, axis=2)

        stance_transition = np.zeros((self.num_stances, self.num_stances, num_actions_total), dtype=float)
        for action in range(num_actions_total):
            evidence = cooperation_evidence_strength(
                action=self.social_action_for_action(action),
                num_social_actions=self.num_social_actions,
            )
            stance_transition[:, :, action] = interpolate_stance_transition(evidence)
        B[1] = stance_transition

        own_action = np.zeros((self.num_social_actions, self.num_social_actions, num_actions_total), dtype=float)
        for action in range(num_actions_total):
            social_action = self.social_action_for_action(action)
            own_action[social_action, :, action] = 1.0
        B[2] = own_action
        return B

    def build_C(self) -> np.ndarray:
        C = obj_array(2)
        C[0] = np.zeros(2, dtype=float)
        payoff_values = np.asarray(self.payoff_levels, dtype=float)
        scaled = payoff_values / max(self.preference_temperature, 1e-12)
        C[1] = log_stable(softmax(scaled, backend="numpy"), backend="numpy")
        return C

    def build_D(self) -> np.ndarray:
        D = obj_array(3)
        D[0] = np.full(self.num_types, 1.0 / self.num_types, dtype=float)
        D[1] = np.asarray([0.2, 0.6, 0.2], dtype=float)
        D[2] = np.full(self.num_social_actions, 1.0 / self.num_social_actions, dtype=float)
        return D

    def get_matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.A, self.B, self.C, self.D

    def as_joint_belief(self, belief: np.ndarray) -> np.ndarray:
        array = np.asarray(belief, dtype=float)
        if array.shape == (self.num_types, self.num_stances):
            joint = array
        elif array.size == self.num_types * self.num_stances:
            joint = array.reshape(self.num_types, self.num_stances)
        else:
            raise ValueError(
                f"Expected joint belief with shape {(self.num_types, self.num_stances)} or flat size "
                f"{self.num_types * self.num_stances}, got {array.shape}."
            )
        total = joint.sum()
        return joint / max(total, 1e-16)

    def partner_action_distribution(self, joint_belief: np.ndarray) -> np.ndarray:
        joint = self.as_joint_belief(joint_belief)
        p_coop = float(np.sum(joint * self.partner_action_prob_table))
        return np.asarray([p_coop, 1.0 - p_coop], dtype=float)

    def joint_observation_likelihood(self, partner_action: int, payoff_obs: int | None = None, own_action: int | None = None) -> np.ndarray:
        del payoff_obs, own_action
        return np.asarray(self.A[0][int(partner_action)], dtype=float)

    def observation_likelihood(self, observation: list[int], own_action: int | None = None) -> np.ndarray:
        payoff_obs = int(observation[1]) if len(observation) > 1 else None
        return self.joint_observation_likelihood(int(observation[0]), payoff_obs=payoff_obs, own_action=own_action)

    def type_transition_for_action(self, action: int) -> np.ndarray:
        return np.asarray(self.B[0][:, :, int(action)], dtype=float)

    def stance_transition_for_action(self, action: int) -> np.ndarray:
        return np.asarray(self.B[1][:, :, int(action)], dtype=float)

    def transition_for_action(self, action: int = 0) -> np.ndarray:
        return self.type_transition_for_action(action)

    def predict_next_joint_belief(self, joint_belief: np.ndarray, action: int) -> np.ndarray:
        joint = self.as_joint_belief(joint_belief)
        type_transition = self.type_transition_for_action(action)
        stance_transition = self.stance_transition_for_action(action)
        predictive = type_transition @ joint @ stance_transition.T
        predictive /= max(float(predictive.sum()), 1e-16)
        return predictive

    def infer_joint_posterior(
        self,
        joint_belief: np.ndarray,
        observation: list[int],
        own_action: int | None = None,
    ) -> np.ndarray:
        prior = self.as_joint_belief(joint_belief)
        likelihood = self.observation_likelihood(observation, own_action=own_action)
        posterior = prior * likelihood
        posterior /= max(float(posterior.sum()), 1e-16)
        return posterior

    def predict_payoff_distribution(self, agent_action: int, partner_action_probs: np.ndarray) -> np.ndarray:
        return payoff_distribution(
            agent_action=agent_action,
            partner_action_probs=partner_action_probs,
            payoff_matrix=self.payoff_matrix,
            payoff_levels=self.payoff_levels,
        )

    def expected_agent_payoff(self, agent_action: int, partner_action_probs: np.ndarray) -> float:
        return expected_agent_payoff(agent_action, partner_action_probs, self.payoff_matrix)


class TrustGameModel(_BaseTrustGameModel):
    """Construct the trust-game POMDP and joint type-stance helpers."""

    def _init_payoffs(self, cfg: dict) -> None:
        self.num_social_actions = 2
        self.payoff_matrix = build_payoff_matrix(
            mutual_coop=tuple(cfg.get("mutual_coop", (3.0, 3.0))),
            sucker=tuple(cfg.get("sucker", (-1.0, 5.0))),
            temptation=tuple(cfg.get("temptation", (5.0, -1.0))),
            mutual_defect=tuple(cfg.get("mutual_defect", (1.0, 1.0))),
        )


class GradedTrustGameModel(_BaseTrustGameModel):
    """Generative model for a graded investment trust game."""

    def _init_payoffs(self, cfg: dict) -> None:
        num_investment_levels = int(cfg.get("num_investment_levels", 6))
        endowment = float(cfg.get("endowment", 10.0))
        multiplier = float(cfg.get("multiplier", 3.0))
        self.num_social_actions = num_investment_levels
        self.payoff_matrix = build_graded_payoff_matrix(
            num_levels=num_investment_levels,
            endowment=endowment,
            multiplier=multiplier,
        )
