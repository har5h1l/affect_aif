"""Base JAX-first active inference agent for the trust game."""

from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

from affect_aif.core.control import construct_policies, decision_step_trust_game
from affect_aif.core.learning import update_likelihood_dirichlet
from affect_aif.core.maths import dirichlet_expected_value
from affect_aif.core.utils import obj_array, onehot


_LIKELIHOOD_PRIOR_STRENGTH = 10.0
_LIKELIHOOD_EPS = 1e-3


def _copy_model_array(array):
    if isinstance(array, np.ndarray) and array.dtype == object:
        copied = obj_array(len(array))
        for idx, value in enumerate(array):
            copied[idx] = np.asarray(value, dtype=float).copy()
        return copied
    return np.asarray(array, dtype=float).copy()


def _init_likelihood_dirichlet(A):
    qA = obj_array(len(A))
    for modality, likelihood in enumerate(A):
        probs = np.asarray(likelihood, dtype=float)
        qA[modality] = _LIKELIHOOD_PRIOR_STRENGTH * probs + _LIKELIHOOD_EPS
    return qA


@jax.jit
def infer_partner_state(
    prior_belief,
    observation,
    last_action,
    interaction_count,
    noisy_partner_action_likelihood,
    B_type,
    switch_round,
):
    """Infer partner type from the realized outcome and roll forward to the next encounter prior."""

    phase = jnp.where(interaction_count >= switch_round, 1, 0).astype(jnp.int32)
    likelihood = noisy_partner_action_likelihood[observation[0], :, last_action, phase]
    posterior = likelihood * prior_belief
    posterior = posterior / (jnp.sum(posterior) + 1e-16)
    predictive_next = B_type @ posterior
    predictive_next = predictive_next / (jnp.sum(predictive_next) + 1e-16)
    return posterior, predictive_next


class BaseAgent:
    """Standard active inference agent used for the deep and shallow no-affect conditions."""

    def __init__(
        self,
        A,
        B,
        C,
        D,
        model,
        planning_horizon: int = 8,
        gamma: float = 1.0,
        lr: float = 0.1,
        action_sampling: str = "marginal",
        use_utility: bool = True,
        use_information_gain: bool = True,
        max_policies: int | None = None,
        reference_horizon: int | None = None,
        seed: int = 0,
        affect_modulates_precision: bool = False,
        use_parameter_learning: bool = False,
    ):
        self.A = _copy_model_array(A)
        self.B = _copy_model_array(B)
        self.C = _copy_model_array(C)
        self.D = _copy_model_array(D)
        self.model = model
        self.planning_horizon = int(planning_horizon)
        self.gamma = float(gamma)
        self.lr = float(lr)
        self.action_sampling = str(action_sampling)
        self.use_utility = bool(use_utility)
        self.use_information_gain = bool(use_information_gain)
        self.max_policies = max_policies
        self.reference_horizon = int(reference_horizon if reference_horizon is not None else planning_horizon)
        self.seed = int(seed)
        self.affect_modulates_precision = bool(affect_modulates_precision)
        self.use_parameter_learning = bool(use_parameter_learning)

        self.num_partners = int(model.num_partners)
        self.num_types = int(model.num_types)
        self.num_actions = int(model.num_controls[0])
        self.assignment_mode_code = 1 if model.assignment_mode == "agent_choice" else 0
        self.sampling_mode_code = 0 if self.action_sampling == "marginal" else 1

        rng = np.random.default_rng(self.seed)
        self.policies = jnp.asarray(
            construct_policies([self.num_actions], self.planning_horizon, max_policies=self.max_policies, rng=rng),
            dtype=jnp.int32,
        )
        self.B_type = jnp.asarray(self.B[0][:, :, 0], dtype=jnp.float32)
        self.payoff_index_table = jnp.asarray(self.model.payoff_index_table, dtype=jnp.int32)
        self.agent_payoff_table = jnp.asarray(self.model.agent_payoff_table, dtype=jnp.float32)
        self.partner_action_preferences = jnp.asarray(self.C[0], dtype=jnp.float32)
        self.payoff_preferences = jnp.asarray(self.C[1], dtype=jnp.float32)
        self.max_abs_payoff = float(max(abs(level) for level in self.model.payoff_levels))
        self._initial_A = _copy_model_array(self.A)
        self._initial_qA = _init_likelihood_dirichlet(self._initial_A) if self.use_parameter_learning else None

        self.planning_cost = float((self.num_actions ** self.planning_horizon) * self.planning_horizon)
        self.planning_cost_ratio = float((self.num_actions ** self.reference_horizon) / (self.num_actions ** self.planning_horizon))
        self.reset()

    def reset(self):
        self._reset_likelihood_model()
        prior = jnp.asarray(self.D[0], dtype=jnp.float32)
        self.partner_beliefs = jnp.tile(prior[None, :], (self.num_partners, 1))
        self.partner_posteriors = jnp.tile(prior[None, :], (self.num_partners, 1))
        self.partner_last_agent_actions = jnp.zeros((self.num_partners,), dtype=jnp.int32)
        self.partner_interaction_counts = jnp.zeros((self.num_partners,), dtype=jnp.int32)
        self.key = jax.random.PRNGKey(self.seed)

        self.pending_prediction_partner: int | None = None
        self.pending_prediction_probs = jnp.asarray([0.5, 0.5], dtype=jnp.float32)
        self.pending_social_action: int | None = None
        self.last_raw_action: int | None = None

        self.last_q_pi = jnp.asarray([], dtype=jnp.float32)
        self.last_G = jnp.asarray([], dtype=jnp.float32)
        self.last_terminal_values = jnp.asarray([], dtype=jnp.float32)
        self.last_best_policy_step_costs = jnp.asarray([], dtype=jnp.float32)
        self.last_mean_abs_step_efe = np.nan
        self.last_selected_partner: int | None = None
        self.last_selected_action: int | None = None
        self.last_best_policy_idx: int | None = None
        self.last_observation_partner: int | None = None
        self.last_true_partner_type: str | None = None
        self.last_partner_action: int | None = None
        self.last_payoff: float = np.nan

    def current_mu(self) -> float:
        return 0.0

    def terminal_signal(self):
        return jnp.zeros((self.num_partners,), dtype=jnp.float32)

    def precision_signal(self):
        return jnp.zeros((self.num_partners,), dtype=jnp.float32)

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float):
        del partner_idx, partner_action, payoff

    def _reset_likelihood_model(self):
        if self.use_parameter_learning:
            self.qA = _copy_model_array(self._initial_qA)
            self.A = obj_array(len(self.qA))
            for modality, concentrations in enumerate(self.qA):
                self.A[modality] = dirichlet_expected_value(concentrations, backend="numpy")
        else:
            self.qA = None
            self.A = _copy_model_array(self._initial_A)
        self._refresh_likelihood_views()

    def _refresh_likelihood_views(self):
        self.A_partner_action = jnp.asarray(self.A[0], dtype=jnp.float32)
        self.partner_action_prob_table = jnp.asarray(self.A[0][0], dtype=jnp.float32)
        self.model.A = self.A
        self.model.partner_action_prob_table = np.asarray(self.A[0][0], dtype=float)

    def _apply_parameter_learning(
        self,
        partner_idx: int,
        observation: np.ndarray,
        posterior: np.ndarray,
        action_taken: int,
        partner_action: int,
    ):
        if not self.use_parameter_learning:
            return

        last_action = int(self.partner_last_agent_actions[partner_idx])
        phase = int(self.partner_interaction_counts[partner_idx] >= self.model.switch_round)

        partner_qA = obj_array(1)
        partner_qA[0] = np.asarray(self.qA[0], dtype=float)
        partner_qs = obj_array(3)
        partner_qs[0] = np.asarray(posterior, dtype=float)
        partner_qs[1] = onehot(last_action, self.qA[0].shape[2])
        partner_qs[2] = onehot(phase, self.qA[0].shape[3])
        updated_partner_qA = update_likelihood_dirichlet(
            qA=partner_qA,
            obs=[int(observation[0])],
            qs=partner_qs,
            learning_rate=self.lr,
        )
        self.qA[0] = updated_partner_qA[0]

        payoff_qA = obj_array(1)
        payoff_qA[0] = np.asarray(self.qA[1], dtype=float)
        payoff_qs = obj_array(2)
        payoff_qs[0] = onehot(int(action_taken), self.qA[1].shape[1])
        payoff_qs[1] = onehot(int(partner_action), self.qA[1].shape[2])
        updated_payoff_qA = update_likelihood_dirichlet(
            qA=payoff_qA,
            obs=[int(observation[1])],
            qs=payoff_qs,
            learning_rate=self.lr,
        )
        self.qA[1] = updated_payoff_qA[0]

        for modality, concentrations in enumerate(self.qA):
            self.A[modality] = dirichlet_expected_value(concentrations, backend="numpy")
        self._refresh_likelihood_views()

    def plan_and_act(self, active_partner: int | None) -> int:
        """Evaluate all policies and return the selected action."""

        active_partner_idx = -1 if active_partner is None else int(active_partner)
        decision = decision_step_trust_game(
            beliefs=self.partner_beliefs,
            last_actions=self.partner_last_agent_actions,
            counts=self.partner_interaction_counts,
            active_partner=jnp.int32(active_partner_idx),
            policies=self.policies,
            key=self.key,
            B_type=self.B_type,
            partner_action_prob_table=self.partner_action_prob_table,
            payoff_index_table=self.payoff_index_table,
            agent_payoff_table=self.agent_payoff_table,
            payoff_preferences=self.payoff_preferences,
            partner_action_preferences=self.partner_action_preferences,
            terminal_signal=self.terminal_signal(),
            precision_signal=self.precision_signal(),
            assignment_mode_code=jnp.int32(self.assignment_mode_code),
            switch_round=jnp.int32(self.model.switch_round),
            gamma=jnp.float32(self.gamma),
            mu=jnp.float32(self.current_mu()),
            num_actions=self.num_actions,
            sampling_mode_code=jnp.int32(self.sampling_mode_code),
            use_utility_flag=jnp.float32(1.0 if self.use_utility else 0.0),
            use_information_gain_flag=jnp.float32(1.0 if self.use_information_gain else 0.0),
            modulate_precision_flag=jnp.int32(1 if self.affect_modulates_precision else 0),
            max_abs_payoff=jnp.float32(self.max_abs_payoff),
        )
        self.key = decision["key"]
        self.last_q_pi = decision["q_pi"]
        self.last_G = decision["G"]
        self.last_terminal_values = decision["terminal_values"]
        self.last_best_policy_step_costs = decision["best_policy_step_costs"]
        self.last_mean_abs_step_efe = float(decision["mean_abs_step_efe"])
        self.last_best_policy_idx = int(decision["best_policy_idx"])
        self.pending_prediction_partner = int(decision["selected_partner"])
        self.pending_prediction_probs = decision["predicted_partner_action_probs"]
        self.pending_social_action = int(decision["selected_social_action"])
        self.last_raw_action = int(decision["action"])
        self.last_selected_partner = self.pending_prediction_partner
        self.last_selected_action = self.pending_social_action
        return self.last_raw_action

    def observe_outcome(
        self,
        partner_idx: int,
        observation: list[int],
        action_taken: int,
        partner_action: int,
        payoff: float,
        true_partner_type: str | None = None,
    ):
        """Update beliefs and auxiliary state summaries from a realized interaction."""

        partner_idx = int(partner_idx)
        observation_arr = jnp.asarray(observation, dtype=jnp.int32)
        prior = self.partner_beliefs[partner_idx]
        posterior, predictive_next = infer_partner_state(
            prior_belief=prior,
            observation=observation_arr,
            last_action=self.partner_last_agent_actions[partner_idx],
            interaction_count=self.partner_interaction_counts[partner_idx],
            noisy_partner_action_likelihood=self.A_partner_action,
            B_type=self.B_type,
            switch_round=self.model.switch_round,
        )
        self._apply_parameter_learning(
            partner_idx=partner_idx,
            observation=np.asarray(observation_arr, dtype=int),
            posterior=np.asarray(posterior, dtype=float),
            action_taken=int(action_taken),
            partner_action=int(partner_action),
        )
        self._update_auxiliary_states(partner_idx=partner_idx, partner_action=int(partner_action), payoff=float(payoff))
        self.partner_posteriors = self.partner_posteriors.at[partner_idx].set(posterior)
        self.partner_beliefs = self.partner_beliefs.at[partner_idx].set(predictive_next)
        self.partner_last_agent_actions = self.partner_last_agent_actions.at[partner_idx].set(int(action_taken))
        self.partner_interaction_counts = self.partner_interaction_counts.at[partner_idx].set(
            self.partner_interaction_counts[partner_idx] + 1
        )
        self.last_observation_partner = partner_idx
        self.last_true_partner_type = true_partner_type
        self.last_partner_action = int(partner_action)
        self.last_payoff = float(payoff)

    def get_partner_type_belief(self, partner_idx: int) -> np.ndarray:
        """Return the latest posterior over a specific partner's type."""

        return np.asarray(self.partner_posteriors[int(partner_idx)], dtype=float)

    def get_reward_avgs(self) -> np.ndarray:
        return np.full((self.num_partners,), np.nan, dtype=float)

    def get_betas(self) -> np.ndarray:
        return np.full((self.num_partners,), np.nan, dtype=float)

    def get_prediction_errors(self) -> np.ndarray:
        return np.full((self.num_partners,), np.nan, dtype=float)

    def get_metrics(self) -> dict:
        """Return round-level metrics from the most recent decision and outcome."""

        q_pi_np = np.asarray(self.last_q_pi, dtype=float)
        q_pi_entropy = float(-(q_pi_np * np.log(q_pi_np + 1e-16)).sum()) if q_pi_np.size else np.nan
        return {
            "q_pi": q_pi_np,
            "G": np.asarray(self.last_G, dtype=float),
            "terminal_values": np.asarray(self.last_terminal_values, dtype=float),
            "best_policy_step_costs": np.asarray(self.last_best_policy_step_costs, dtype=float),
            "mean_abs_step_efe": float(self.last_mean_abs_step_efe),
            "best_policy_idx": self.last_best_policy_idx,
            "selected_partner": self.last_selected_partner,
            "selected_action": self.last_selected_action,
            "raw_action": self.last_raw_action,
            "q_pi_entropy": q_pi_entropy,
            "betas": self.get_betas(),
            "prediction_errors": self.get_prediction_errors(),
            "reward_avgs": self.get_reward_avgs(),
            "partner_beliefs": np.asarray(self.partner_beliefs, dtype=float),
            "partner_posteriors": np.asarray(self.partner_posteriors, dtype=float),
            "planning_cost": self.planning_cost,
            "planning_cost_ratio": self.planning_cost_ratio,
            "mu": self.current_mu(),
        }
