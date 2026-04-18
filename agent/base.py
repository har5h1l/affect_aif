"""Base active inference agent for the trust game."""

from __future__ import annotations

import numpy as np

from agent.inference.control import construct_policies, decision_step_trust_game, generate_observation_sequences
from agent.inference.learning import update_likelihood_dirichlet, update_transition_dirichlet
from agent.inference.maths import dirichlet_expected_value
from agent.inference.policies import sample_action
from agent.inference.utils import obj_array, onehot
from agent.model.payoffs import encode_env_action_factorized, encode_instantaneous_index


class BaseAgent:
    """Standard active inference agent with joint type-stance beliefs per partner."""

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
        use_parameter_learning: bool = False,
        learn_A: bool = False,
        learn_B: bool = False,
        learn_E: bool = False,
        pA_scale: float = 1.0,
        pB_scale: float = 10.0,
        lr_E: float = 0.5,
    ):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
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
        self.use_parameter_learning = bool(use_parameter_learning)
        self.learn_A = bool(learn_A)
        self.learn_B = bool(learn_B)
        self.learn_E = bool(learn_E)
        self.pA_scale = float(pA_scale)
        self.pB_scale = float(pB_scale)
        self.lr_E = float(lr_E)
        self.pA = None
        self.pB = None
        if self.learn_A:
            self.pA = model.build_pA(self.pA_scale)
        if self.learn_B:
            self.pB = model.build_pB(self.pB_scale)

        self.num_partners = int(model.num_partners)
        self.num_types = int(model.num_types)
        self.num_stances = int(model.num_stances)
        self.num_controls = list(int(x) for x in model.num_controls)
        self.num_planning_instantaneous = int(np.prod(self.num_controls))
        self.num_social_actions = int(getattr(model, "num_social_actions", 2))
        self.factorized_policies = bool(getattr(model, "uses_factorized_controls", False))
        self.assignment_mode_code = 1 if model.assignment_mode == "agent_choice" else 0
        self.rng = np.random.default_rng(self.seed)

        self.policies = np.asarray(
            construct_policies(self.num_controls, self.planning_horizon, max_policies=self.max_policies, rng=self.rng),
            dtype=int,
        )
        self.observation_sequences = np.asarray(generate_observation_sequences(self.planning_horizon), dtype=int)
        self._refresh_transition_views()
        self.partner_action_prob_table = np.asarray(self.model.partner_action_prob_table, dtype=float)
        self.payoff_index_table = np.asarray(self.model.payoff_index_table, dtype=int)
        self.agent_payoff_table = np.asarray(self.model.agent_payoff_table, dtype=float)
        self.partner_action_preferences = np.asarray(self.C[0], dtype=float)
        self.payoff_preferences = np.asarray(self.C[1], dtype=float)
        self.max_abs_payoff = float(max(abs(level) for level in self.model.payoff_levels))

        self.planning_cost = float((self.num_planning_instantaneous**self.planning_horizon) * self.planning_horizon)
        self.planning_cost_ratio = float(
            (self.num_planning_instantaneous**self.reference_horizon)
            / max(self.num_planning_instantaneous**self.planning_horizon, 1)
        )
        self.reset()

    def reset(self):
        type_prior = np.asarray(self.D[0], dtype=float)
        stance_prior = np.asarray(self.D[1], dtype=float)
        joint_prior = np.outer(type_prior, stance_prior)
        joint_prior /= max(float(joint_prior.sum()), 1e-16)
        self.partner_joint_beliefs = np.repeat(joint_prior[None, :, :], self.num_partners, axis=0)
        self.partner_joint_posteriors = np.repeat(joint_prior[None, :, :], self.num_partners, axis=0)
        self.partner_beliefs = np.repeat(type_prior[None, :], self.num_partners, axis=0)
        self.partner_stance_beliefs = np.repeat(stance_prior[None, :], self.num_partners, axis=0)

        self.pending_prediction_partner: int | None = None
        self.pending_prediction_probs = np.asarray([0.5, 0.5], dtype=float)
        self.pending_social_action: int | None = None
        self.last_raw_action: int | None = None

        self.last_q_pi = np.asarray([], dtype=float)
        self.last_G = np.asarray([], dtype=float)
        self.last_best_policy_step_costs = np.asarray([], dtype=float)
        self.last_mean_abs_step_efe = np.nan
        self.last_selected_partner: int | None = None
        self.last_selected_action: int | None = None
        self.last_best_policy_idx: int | None = None
        self.last_observation_partner: int | None = None
        self.last_true_partner_type: str | None = None
        self.last_true_partner_stance: str | None = None
        self.last_partner_action: int | None = None
        self.last_payoff: float = np.nan
        self.last_round_log_evidence: float = np.nan
        self.cumulative_log_evidence: float = 0.0
        self.log_policy_prior = np.zeros(len(self.policies), dtype=float)
        self._prev_own_action = int(np.argmax(np.asarray(self.D[2], dtype=float)))

    @property
    def num_actions(self) -> int:
        """Instantaneous action cardinality (planning); env flat action may differ when factorized."""

        return int(self.num_planning_instantaneous)

    def precision_signal(self):
        return np.ones((self.num_partners,), dtype=float)

    def _refresh_transition_views(self):
        self.B_type = np.asarray(self.B[0][:, :, 0], dtype=float)
        if self.factorized_policies:
            idx_st0 = encode_instantaneous_index((0, 0, 0), self.num_controls)
            idx_st1 = encode_instantaneous_index((0, 1, 0), self.num_controls)
            self.B_stance_by_action = np.stack(
                [
                    np.asarray(self.B[1][:, :, idx_st0], dtype=float),
                    np.asarray(self.B[1][:, :, idx_st1], dtype=float),
                ],
                axis=0,
            )
        else:
            self.B_stance_by_action = np.asarray(np.moveaxis(self.B[1], 2, 0), dtype=float)

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float):
        del partner_idx, partner_action, payoff

    def _apply_parameter_learning(self, posterior: np.ndarray, observed_partner_action: int):
        if not self.use_parameter_learning:
            return
        target = 1.0 if int(observed_partner_action) == 0 else 0.0
        self.partner_action_prob_table = (
            (1.0 - self.lr * posterior) * self.partner_action_prob_table + (self.lr * posterior) * target
        )
        partner_action_likelihood = np.zeros((2, self.num_types, self.num_stances), dtype=float)
        partner_action_likelihood[0] = self.partner_action_prob_table
        partner_action_likelihood[1] = 1.0 - self.partner_action_prob_table
        self.A[0] = partner_action_likelihood
        self.model.A = self.A
        self.model.partner_action_prob_table = self.partner_action_prob_table

    def _decode_raw_action(self, raw_action: int, active_partner: int | None) -> tuple[int, int]:
        if self.factorized_policies:
            if self.assignment_mode_code == 1:
                partner_idx = int(raw_action) // 4
                rem = int(raw_action) % 4
                own_action = rem % 2
                return partner_idx, own_action
            return int(active_partner), int(raw_action)
        if self.assignment_mode_code == 1:
            partner_idx = int(raw_action) // self.num_social_actions
            social_action = int(raw_action) % self.num_social_actions
            return partner_idx, social_action
        return int(active_partner), int(raw_action)

    def plan_and_act(self, active_partner: int | None) -> int:
        """Evaluate all policies and return the selected action."""

        active_partner_idx = -1 if active_partner is None else int(active_partner)
        decision = decision_step_trust_game(
            beliefs=self.partner_joint_beliefs,
            active_partner=active_partner_idx,
            policies=self.policies,
            observation_sequences=self.observation_sequences,
            B_type=self.B_type,
            B_stance_by_action=self.B_stance_by_action,
            partner_action_prob_table=self.partner_action_prob_table,
            payoff_index_table=self.payoff_index_table,
            agent_payoff_table=self.agent_payoff_table,
            payoff_preferences=self.payoff_preferences,
            partner_action_preferences=self.partner_action_preferences,
            precision_signal=self.precision_signal(),
            assignment_mode_code=self.assignment_mode_code,
            gamma=self.gamma,
            use_utility_flag=float(self.use_utility),
            use_information_gain_flag=float(self.use_information_gain),
            num_social_actions=self.num_social_actions,
            log_policy_prior=self.log_policy_prior,
        )

        q_pi = np.asarray(decision["q_pi"], dtype=float)
        sampled = sample_action(
            q_pi=q_pi,
            policies=self.policies,
            timestep=0,
            sampling_mode=self.action_sampling,
            rng=self.rng,
        )
        if isinstance(sampled, np.ndarray):
            row = np.asarray(sampled, dtype=int).ravel()
            if self.assignment_mode_code == 1:
                partner_sel = int(row[0])
                stance_a = int(row[1])
                own_a = int(row[2])
                raw_action = encode_env_action_factorized(
                    partner_sel,
                    stance_a,
                    own_a,
                    "agent_choice",
                    self.num_partners,
                    self.num_controls,
                )
                selected_partner, selected_social_action = partner_sel, own_a
            else:
                stance_a = int(row[1])
                own_a = int(row[2])
                raw_action = encode_env_action_factorized(
                    int(active_partner) if active_partner is not None else 0,
                    stance_a,
                    own_a,
                    "random",
                    self.num_partners,
                    self.num_controls,
                )
                selected_partner = int(active_partner) if active_partner is not None else 0
                selected_social_action = own_a
        else:
            raw_action = int(sampled)
            selected_partner, selected_social_action = self._decode_raw_action(raw_action, active_partner)
        predicted_partner_action_probs = self.model.partner_action_distribution(self.partner_joint_beliefs[selected_partner])
        best_policy_idx = int(np.argmax(q_pi))

        self.last_q_pi = q_pi
        self.last_G = np.asarray(decision["G"], dtype=float)
        self.last_best_policy_step_costs = np.asarray(decision["step_costs"][best_policy_idx], dtype=float)
        self.last_mean_abs_step_efe = float(decision["mean_abs_step_efe"])
        self.last_best_policy_idx = best_policy_idx
        self.pending_prediction_partner = selected_partner
        self.pending_prediction_probs = np.asarray(predicted_partner_action_probs, dtype=float)
        self.pending_social_action = selected_social_action
        self.last_raw_action = raw_action
        self.last_selected_partner = selected_partner
        self.last_selected_action = selected_social_action
        return raw_action

    def _compute_round_log_evidence(self, partner_action: int) -> float:
        probs = np.asarray(self.pending_prediction_probs, dtype=float)
        p_obs = float(probs[int(partner_action)])
        return float(np.log(max(p_obs, 1e-16)))

    def observe_outcome(
        self,
        partner_idx: int,
        observation: list[int],
        action_taken: int,
        partner_action: int,
        payoff: float,
        true_partner_type: str | None = None,
        true_partner_stance: str | None = None,
    ):
        """Update beliefs and auxiliary state summaries from a realized interaction."""

        partner_idx = int(partner_idx)
        round_log_ev = self._compute_round_log_evidence(partner_action)
        self.last_round_log_evidence = round_log_ev
        self.cumulative_log_evidence += round_log_ev

        prior = np.asarray(self.partner_joint_beliefs[partner_idx], dtype=float)
        posterior = self.model.infer_joint_posterior(prior, observation, own_action=int(action_taken))
        predictive_next = self.model.predict_next_joint_belief(posterior, action=int(action_taken))
        if self.learn_A and self.pA is not None:
            qs_obj = obj_array(1)
            qs_obj[0] = posterior
            obs_list = [int(observation[0]), int(observation[1])]
            self.pA = update_likelihood_dirichlet(self.pA, obs_list, qs_obj, learning_rate=self.lr)
            for modality in range(len(self.A)):
                self.A[modality] = np.asarray(
                    dirichlet_expected_value(np.asarray(self.pA[modality], dtype=float), backend="numpy"),
                    dtype=float,
                )
            self.model.A = self.A
            self.partner_action_prob_table = np.asarray(self.A[0][0, :, :], dtype=float)
            self.model.partner_action_prob_table = self.partner_action_prob_table
        elif self.use_parameter_learning:
            self._apply_parameter_learning(posterior=posterior, observed_partner_action=int(partner_action))
        if self.learn_B and self.pB is not None:
            comp = (
                encode_instantaneous_index((0, int(action_taken), int(action_taken)), self.num_controls)
                if self.factorized_policies
                else int(action_taken)
            )
            actions_vec = [comp, comp, comp]
            qs_curr = [
                posterior.sum(axis=1),
                posterior.sum(axis=0),
                onehot(int(action_taken), self.num_social_actions),
            ]
            qs_prev = [
                prior.sum(axis=1),
                prior.sum(axis=0),
                onehot(int(self._prev_own_action), self.num_social_actions),
            ]
            self.pB = update_transition_dirichlet(self.pB, actions_vec, qs_curr, qs_prev)
            for factor in range(len(self.B)):
                conc = np.asarray(self.pB[factor], dtype=float)
                for action in range(conc.shape[2]):
                    sl = conc[:, :, action]
                    self.B[factor][:, :, action] = sl / np.maximum(sl.sum(axis=0, keepdims=True), 1e-16)
            self.model.B = self.B
            self._refresh_transition_views()
        if self.learn_E and self.last_q_pi.size:
            log_q = np.log(np.asarray(self.last_q_pi, dtype=float) + 1e-16)
            self.log_policy_prior = (1.0 - self.lr_E) * self.log_policy_prior + self.lr_E * log_q
            self.log_policy_prior -= float(np.mean(self.log_policy_prior))
        self._prev_own_action = int(action_taken)
        self._update_auxiliary_states(partner_idx=partner_idx, partner_action=int(partner_action), payoff=float(payoff))

        self.partner_joint_posteriors[partner_idx] = posterior
        self.partner_joint_beliefs[partner_idx] = predictive_next
        self.partner_beliefs[partner_idx] = predictive_next.sum(axis=1)
        self.partner_stance_beliefs[partner_idx] = predictive_next.sum(axis=0)
        self.last_observation_partner = partner_idx
        self.last_true_partner_type = true_partner_type
        self.last_true_partner_stance = true_partner_stance
        self.last_partner_action = int(partner_action)
        self.last_payoff = float(payoff)

    def get_partner_type_belief(self, partner_idx: int) -> np.ndarray:
        return np.asarray(self.partner_beliefs[int(partner_idx)], dtype=float)

    def get_partner_stance_belief(self, partner_idx: int) -> np.ndarray:
        return np.asarray(self.partner_stance_beliefs[int(partner_idx)], dtype=float)

    def get_predictive_log_likelihood(self, partner_action: int) -> float:
        probs = np.asarray(self.pending_prediction_probs, dtype=float)
        idx = int(partner_action)
        if idx < 0 or idx >= len(probs):
            return float("nan")
        p = float(probs[idx])
        return float(np.log(max(p, 1e-16)))

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
            "partner_posteriors": np.asarray(self.partner_joint_posteriors.sum(axis=2), dtype=float),
            "partner_joint_beliefs": np.asarray(self.partner_joint_beliefs, dtype=float),
            "partner_joint_posteriors": np.asarray(self.partner_joint_posteriors, dtype=float),
            "partner_stance_beliefs": np.asarray(self.partner_stance_beliefs, dtype=float),
            "planning_cost": self.planning_cost,
            "planning_cost_ratio": self.planning_cost_ratio,
            "round_log_evidence": self.last_round_log_evidence,
            "cumulative_log_evidence": self.cumulative_log_evidence,
        }
