"""Generative model specification for the trust game."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

import numpy as np

from affect_aif.core.maths import entropy, log_stable, normalize, softmax
from affect_aif.core.utils import obj_array
from affect_aif.generative_model.partner_types import (
    PARTNER_TYPE_ORDER,
    PartnerType,
    default_partner_type_params,
)
from affect_aif.generative_model.payoffs import (
    ACTION_NAMES,
    COOPERATE,
    DEFECT,
    build_graded_payoff_matrix,
    build_payoff_matrix,
    decode_action,
    encode_action,
    expected_agent_payoff,
    infer_payoff_levels,
    num_actions,
    payoff_distribution,
    payoff_to_index,
)


class TrustGameModel:
    """Construct the trust-game POMDP and context-conditioned observation helpers."""

    def __init__(self, config: dict):
        cfg = asdict(config) if is_dataclass(config) else dict(config)
        self.config = cfg
        self.num_partners = int(cfg.get("num_partners", 4))
        self.partner_type_names = tuple(cfg.get("partner_types", PARTNER_TYPE_ORDER))
        self.num_types = len(self.partner_type_names)
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

        self.num_social_actions = 2
        self.payoff_matrix = build_payoff_matrix(
            mutual_coop=tuple(cfg.get("mutual_coop", (3.0, 3.0))),
            sucker=tuple(cfg.get("sucker", (-1.0, 5.0))),
            temptation=tuple(cfg.get("temptation", (5.0, -1.0))),
            mutual_defect=tuple(cfg.get("mutual_defect", (1.0, 1.0))),
        )
        self.payoff_levels = infer_payoff_levels(self.payoff_matrix)
        self.num_obs = [2, len(self.payoff_levels)]
        self.num_controls = [num_actions(self.num_partners, self.assignment_mode)]
        self.switch_round = int(self.partner_type_params["exploiter"].get("switch_round", 4))

        self.partner_action_prob_table = self._build_partner_action_prob_table()
        self.payoff_index_table = self._build_payoff_index_table()
        self.agent_payoff_table = self.payoff_matrix[:, :, 0]
        self.A = self.build_A()
        self.B = self.build_B()
        self.C = self.build_C()
        self.D = self.build_D()

    def _build_partner_action_prob_table(self) -> np.ndarray:
        table = np.zeros((self.num_types, 2, 2), dtype=float)
        early_round = 0
        late_round = max(self.switch_round, 1)
        for type_idx, partner_type in enumerate(self.partner_types):
            for last_action in (COOPERATE, DEFECT):
                table[type_idx, last_action, 0] = partner_type.get_action_probability(last_action, early_round)
                table[type_idx, last_action, 1] = partner_type.get_action_probability(last_action, late_round)
        return table

    def _build_payoff_index_table(self) -> np.ndarray:
        indices = np.zeros((2, 2), dtype=int)
        for agent_action in (COOPERATE, DEFECT):
            for partner_action in (COOPERATE, DEFECT):
                payoff = self.payoff_matrix[agent_action, partner_action, 0]
                indices[agent_action, partner_action] = payoff_to_index(payoff, self.payoff_levels)
        return indices

    def phase_index(self, interaction_count: int) -> int:
        """Map a partner-specific interaction count to early or late phase."""

        return int(interaction_count >= self.switch_round)

    def build_A(self) -> np.ndarray:
        """Build context-conditioned likelihood tensors for partner action and payoff."""

        A = obj_array(2)
        partner_action = np.zeros((2, self.num_types, 2, 2), dtype=float)
        for type_idx in range(self.num_types):
            for last_action in (COOPERATE, DEFECT):
                for phase in (0, 1):
                    p_coop = self.partner_action_prob_table[type_idx, last_action, phase]
                    clean = np.asarray([p_coop, 1.0 - p_coop], dtype=float)
                    noisy = (1.0 - self.observation_noise) * clean + self.observation_noise * 0.5
                    partner_action[:, type_idx, last_action, phase] = noisy

        payoff_obs = np.zeros((len(self.payoff_levels), 2, 2), dtype=float)
        for agent_action in (COOPERATE, DEFECT):
            for partner_action_idx in (COOPERATE, DEFECT):
                payoff_obs[self.payoff_index_table[agent_action, partner_action_idx], agent_action, partner_action_idx] = 1.0

        A[0] = partner_action
        A[1] = payoff_obs
        return A

    def build_B(self) -> np.ndarray:
        """Build transition tensors for partner type and interaction context."""

        B = obj_array(2)
        num_actions_total = self.num_controls[0]
        type_transition = np.full((self.num_types, self.num_types), self.p_switch / max(self.num_types - 1, 1), dtype=float)
        np.fill_diagonal(type_transition, 1.0 - self.p_switch)
        B_type = np.repeat(type_transition[:, :, None], num_actions_total, axis=2)

        if self.assignment_mode == "agent_choice":
            context = np.zeros((self.num_partners, self.num_partners, num_actions_total), dtype=float)
            for action in range(num_actions_total):
                partner_idx, _ = decode_action(action, self.num_partners, self.assignment_mode)
                context[partner_idx, :, action] = 1.0
        else:
            context = np.full((self.num_partners, self.num_partners, num_actions_total), 1.0 / self.num_partners, dtype=float)

        B[0] = B_type
        B[1] = context
        return B

    def build_C(self) -> np.ndarray:
        """Build log-preferences over partner-action and payoff observations."""

        C = obj_array(2)
        C[0] = np.zeros(2, dtype=float)
        payoff_values = np.asarray(self.payoff_levels, dtype=float)
        scaled = payoff_values / max(self.preference_temperature, 1e-12)
        C[1] = log_stable(softmax(scaled, backend="numpy"), backend="numpy")
        return C

    def build_D(self) -> np.ndarray:
        """Build initial priors over partner type and interaction context."""

        D = obj_array(2)
        D[0] = np.full(self.num_types, 1.0 / self.num_types, dtype=float)
        D[1] = np.full(self.num_partners, 1.0 / self.num_partners, dtype=float)
        return D

    def get_matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return the canonical A, B, C, D tuple."""

        return self.A, self.B, self.C, self.D

    def contextual_partner_action_likelihood(self, last_agent_action: int, interaction_count: int) -> np.ndarray:
        """Likelihood tensor for the current partner context."""

        phase = self.phase_index(interaction_count)
        return np.asarray(self.A[0][:, :, last_agent_action, phase], dtype=float)

    def contextual_partner_action_distribution(
        self,
        type_belief: np.ndarray,
        last_agent_action: int,
        interaction_count: int,
    ) -> np.ndarray:
        """Predict partner actions given a belief over partner types."""

        likelihood = self.contextual_partner_action_likelihood(last_agent_action, interaction_count)
        return likelihood @ np.asarray(type_belief, dtype=float)

    def ambiguity_by_type(self, last_agent_action: int, interaction_count: int) -> np.ndarray:
        """Entropy of the partner-action channel for each latent type."""

        likelihood = self.contextual_partner_action_likelihood(last_agent_action, interaction_count)
        return np.asarray(entropy(likelihood, backend="numpy"), dtype=float)

    def predict_payoff_distribution(self, agent_action: int, partner_action_probs: np.ndarray) -> np.ndarray:
        """Predict own-payoff observations from a chosen action and partner behavior."""

        return payoff_distribution(
            agent_action=agent_action,
            partner_action_probs=partner_action_probs,
            payoff_matrix=self.payoff_matrix,
            payoff_levels=self.payoff_levels,
        )

    def expected_agent_payoff(self, agent_action: int, partner_action_probs: np.ndarray) -> float:
        """Expected payoff under the current partner-action forecast."""

        return expected_agent_payoff(agent_action, partner_action_probs, self.payoff_matrix)

    def observation_likelihood(
        self,
        observation: list[int],
        last_agent_action: int,
        interaction_count: int,
    ) -> np.ndarray:
        """Likelihood of the current observation under each partner type."""

        partner_obs = observation[0]
        likelihood = self.contextual_partner_action_likelihood(last_agent_action, interaction_count)
        return np.asarray(likelihood[partner_obs], dtype=float)

    def transition_for_action(self, action: int = 0) -> np.ndarray:
        """Partner-type transition matrix for a single action."""

        return np.asarray(self.B[0][:, :, action], dtype=float)


class GradedTrustGameModel:
    """Generative model for a graded investment trust game.

    The agent chooses an investment level (0 to num_investment_levels-1).
    The partner still cooperates or defects (binary).
    """

    def __init__(self, config: dict):
        cfg = asdict(config) if is_dataclass(config) else dict(config)
        self.config = cfg
        self.num_partners = int(cfg.get("num_partners", 4))
        self.partner_type_names = tuple(cfg.get("partner_types", PARTNER_TYPE_ORDER))
        self.num_types = len(self.partner_type_names)
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

        num_investment_levels = int(cfg.get("num_investment_levels", 6))
        endowment = float(cfg.get("endowment", 10.0))
        multiplier = float(cfg.get("multiplier", 3.0))
        self.num_social_actions = num_investment_levels
        self.payoff_matrix = build_graded_payoff_matrix(
            num_levels=num_investment_levels,
            endowment=endowment,
            multiplier=multiplier,
        )
        self.payoff_levels = infer_payoff_levels(self.payoff_matrix)
        self.num_obs = [2, len(self.payoff_levels)]
        self.num_controls = [num_actions(self.num_partners, self.assignment_mode, self.num_social_actions)]
        self.switch_round = int(self.partner_type_params["exploiter"].get("switch_round", 4))

        self.partner_action_prob_table = self._build_partner_action_prob_table()
        self.payoff_index_table = self._build_payoff_index_table()
        self.agent_payoff_table = self.payoff_matrix[:, :, 0]
        self.A = self.build_A()
        self.B = self.build_B()
        self.C = self.build_C()
        self.D = self.build_D()

    def _build_partner_action_prob_table(self) -> np.ndarray:
        table = np.zeros((self.num_types, 2, 2), dtype=float)
        early_round = 0
        late_round = max(self.switch_round, 1)
        for type_idx, partner_type in enumerate(self.partner_types):
            for last_action in (COOPERATE, DEFECT):
                table[type_idx, last_action, 0] = partner_type.get_action_probability(last_action, early_round)
                table[type_idx, last_action, 1] = partner_type.get_action_probability(last_action, late_round)
        return table

    def _build_payoff_index_table(self) -> np.ndarray:
        indices = np.zeros((self.num_social_actions, 2), dtype=int)
        for agent_action in range(self.num_social_actions):
            for partner_action in (COOPERATE, DEFECT):
                payoff = self.payoff_matrix[agent_action, partner_action, 0]
                indices[agent_action, partner_action] = payoff_to_index(payoff, self.payoff_levels)
        return indices

    def phase_index(self, interaction_count: int) -> int:
        return int(interaction_count >= self.switch_round)

    def build_A(self) -> np.ndarray:
        A = obj_array(2)
        partner_action = np.zeros((2, self.num_types, 2, 2), dtype=float)
        for type_idx in range(self.num_types):
            for last_action in (COOPERATE, DEFECT):
                for phase in (0, 1):
                    p_coop = self.partner_action_prob_table[type_idx, last_action, phase]
                    clean = np.asarray([p_coop, 1.0 - p_coop], dtype=float)
                    noisy = (1.0 - self.observation_noise) * clean + self.observation_noise * 0.5
                    partner_action[:, type_idx, last_action, phase] = noisy

        payoff_obs = np.zeros((len(self.payoff_levels), self.num_social_actions, 2), dtype=float)
        for agent_action in range(self.num_social_actions):
            for partner_action_idx in (COOPERATE, DEFECT):
                payoff_obs[self.payoff_index_table[agent_action, partner_action_idx], agent_action, partner_action_idx] = 1.0

        A[0] = partner_action
        A[1] = payoff_obs
        return A

    def build_B(self) -> np.ndarray:
        B = obj_array(2)
        num_actions_total = self.num_controls[0]
        type_transition = np.full((self.num_types, self.num_types), self.p_switch / max(self.num_types - 1, 1), dtype=float)
        np.fill_diagonal(type_transition, 1.0 - self.p_switch)
        B_type = np.repeat(type_transition[:, :, None], num_actions_total, axis=2)

        if self.assignment_mode == "agent_choice":
            context = np.zeros((self.num_partners, self.num_partners, num_actions_total), dtype=float)
            for action in range(num_actions_total):
                partner_idx, _ = decode_action(
                    action, self.num_partners, self.assignment_mode,
                    num_social_actions=self.num_social_actions,
                )
                context[partner_idx, :, action] = 1.0
        else:
            context = np.full((self.num_partners, self.num_partners, num_actions_total), 1.0 / self.num_partners, dtype=float)

        B[0] = B_type
        B[1] = context
        return B

    def build_C(self) -> np.ndarray:
        C = obj_array(2)
        C[0] = np.zeros(2, dtype=float)
        payoff_values = np.asarray(self.payoff_levels, dtype=float)
        scaled = payoff_values / max(self.preference_temperature, 1e-12)
        C[1] = log_stable(softmax(scaled, backend="numpy"), backend="numpy")
        return C

    def build_D(self) -> np.ndarray:
        D = obj_array(2)
        D[0] = np.full(self.num_types, 1.0 / self.num_types, dtype=float)
        D[1] = np.full(self.num_partners, 1.0 / self.num_partners, dtype=float)
        return D

    def get_matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return self.A, self.B, self.C, self.D

    def contextual_partner_action_likelihood(self, last_agent_action: int, interaction_count: int) -> np.ndarray:
        phase = self.phase_index(interaction_count)
        return np.asarray(self.A[0][:, :, last_agent_action, phase], dtype=float)

    def contextual_partner_action_distribution(
        self,
        type_belief: np.ndarray,
        last_agent_action: int,
        interaction_count: int,
    ) -> np.ndarray:
        likelihood = self.contextual_partner_action_likelihood(last_agent_action, interaction_count)
        return likelihood @ np.asarray(type_belief, dtype=float)

    def ambiguity_by_type(self, last_agent_action: int, interaction_count: int) -> np.ndarray:
        likelihood = self.contextual_partner_action_likelihood(last_agent_action, interaction_count)
        return np.asarray(entropy(likelihood, backend="numpy"), dtype=float)

    def predict_payoff_distribution(self, agent_action: int, partner_action_probs: np.ndarray) -> np.ndarray:
        return payoff_distribution(
            agent_action=agent_action,
            partner_action_probs=partner_action_probs,
            payoff_matrix=self.payoff_matrix,
            payoff_levels=self.payoff_levels,
        )

    def expected_agent_payoff(self, agent_action: int, partner_action_probs: np.ndarray) -> float:
        return expected_agent_payoff(agent_action, partner_action_probs, self.payoff_matrix)

    def observation_likelihood(
        self,
        observation: list[int],
        last_agent_action: int,
        interaction_count: int,
    ) -> np.ndarray:
        partner_obs = observation[0]
        likelihood = self.contextual_partner_action_likelihood(last_agent_action, interaction_count)
        return np.asarray(likelihood[partner_obs], dtype=float)

    def transition_for_action(self, action: int = 0) -> np.ndarray:
        return np.asarray(self.B[0][:, :, action], dtype=float)
