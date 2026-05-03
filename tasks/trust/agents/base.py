"""Trust-game agent composition layer."""

from __future__ import annotations

import numpy as np

import aif
from aif.learning import update_transition_dirichlet
from aif.runtime import generate_observation_sequences
from aif.utils import obj_array, onehot
from tasks.trust.models import TrustGameModel
from tasks.trust.payoffs import encode_env_action_factorized, encode_instantaneous_index
from tasks.trust.rollout import (
    _partner_action_distribution,
    build_transition_views,
    decision_step_trust_game,
    decode_raw_action_to_partner_and_social,
)


class TrustGameAgent:
    """Active-inference agent for the multi-partner trust game."""

    def __init__(
        self,
        model: TrustGameModel,
        *,
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
        self.model = model
        self.num_partners = int(model.num_partners)
        self.num_types = int(model.num_types)
        self.num_stances = int(model.num_stances)
        self.num_controls = list(int(x) for x in model.num_controls)
        self.num_planning_instantaneous = int(np.prod(self.num_controls))
        self.num_social_actions = int(model.num_social_actions)
        self.factorized_policies = bool(model.uses_factorized_controls)
        self.assignment_mode_code = 1 if model.assignment_mode == "agent_choice" else 0
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

        policy_rng = np.random.default_rng(self.seed)
        self.policies = np.asarray(
            aif.construct_policies(
                num_controls=model.num_controls,
                planning_horizon=self.planning_horizon,
                max_policies=self.max_policies,
                rng=policy_rng,
            ),
            dtype=int,
        )
        self.observation_sequences = np.asarray(generate_observation_sequences(self.planning_horizon), dtype=int)

        shared_C = model.C
        shared_D = model.D
        self.partners: list[aif.Agent] = []
        for idx in range(self.num_partners):
            self.partners.append(
                aif.Agent(
                    A=model.build_A(),
                    B=model.build_B(),
                    C=shared_C,
                    D=shared_D,
                    E=None,
                    policies=self.policies,
                    pA=model.build_pA(self.pA_scale) if self.learn_A else None,
                    pB=model.build_pB(self.pB_scale) if self.learn_B else None,
                    gamma=self.gamma,
                    use_utility=self.use_utility,
                    use_information_gain=self.use_information_gain,
                    action_sampling=self.action_sampling,
                    rng=np.random.default_rng(self.seed + 1 + idx),
                )
            )

        self.partner_action_preferences = np.asarray(self.model.C[0], dtype=float)
        self.payoff_preferences = np.asarray(self.model.C[1], dtype=float)
        self.planning_cost = float((self.num_planning_instantaneous**self.planning_horizon) * self.planning_horizon)
        self.planning_cost_ratio = float(
            (self.num_planning_instantaneous**self.reference_horizon)
            / max(self.num_planning_instantaneous**self.planning_horizon, 1)
        )
        self.reset()

    @property
    def num_actions(self) -> int:
        """Instantaneous action cardinality for the planner."""

        return int(self.num_planning_instantaneous)

    @property
    def qs_per_partner(self) -> np.ndarray:
        out = np.zeros((self.num_partners, self.num_types, self.num_stances), dtype=float)
        for idx, partner in enumerate(self.partners):
            if partner.qs is None or len(partner.qs) == 0:
                out[idx] = np.asarray(self.partner_joint_beliefs[idx], dtype=float)
                continue
            out[idx] = self.model.as_joint_belief(partner.qs[0])
        return out

    @property
    def partner_action_prob_tables(self) -> np.ndarray:
        out = np.zeros((self.num_partners, self.num_types, self.num_stances), dtype=float)
        for idx, partner in enumerate(self.partners):
            out[idx] = np.asarray(partner.A[0][0], dtype=float)
        return out

    @property
    def partner_action_prob_table(self) -> np.ndarray:
        return self.partner_action_prob_tables

    def reset(self):
        type_prior = np.asarray(self.model.D[0], dtype=float)
        stance_prior = np.asarray(self.model.D[1], dtype=float)
        joint_prior = np.outer(type_prior, stance_prior)
        joint_prior /= max(float(joint_prior.sum()), 1e-16)
        self.partner_joint_beliefs = np.repeat(joint_prior[None, :, :], self.num_partners, axis=0)
        self.partner_joint_posteriors = np.repeat(joint_prior[None, :, :], self.num_partners, axis=0)
        self.partner_beliefs = np.repeat(type_prior[None, :], self.num_partners, axis=0)
        self.partner_stance_beliefs = np.repeat(stance_prior[None, :], self.num_partners, axis=0)

        for partner in self.partners:
            partner.reset()
            self._set_partner_qs(partner, joint_prior)

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
        default_action = int(np.argmax(np.asarray(self.model.D[2], dtype=float)))
        self._prev_own_actions = np.full((self.num_partners,), default_action, dtype=int)

    def precision_signal(self):
        return np.ones((self.num_partners,), dtype=float)

    def _set_partner_qs(self, partner: aif.Agent, joint_belief: np.ndarray) -> None:
        qs = obj_array(1)
        qs[0] = self.model.as_joint_belief(joint_belief)
        partner.qs = qs

    def _joint_observation_likelihood(self, A: np.ndarray, observation: list[int], own_action: int) -> np.ndarray:
        if len(observation) < 2:
            raise ValueError(f"TrustGameAgent expects both observation modalities; got {observation!r}.")
        action_likelihood = np.asarray(A[0][int(observation[0])], dtype=float)
        payoff_likelihood = np.asarray(A[1][int(observation[1]), int(own_action)], dtype=float)
        return action_likelihood * payoff_likelihood

    def _infer_joint_posterior(
        self, prior: np.ndarray, observation: list[int], own_action: int, A: np.ndarray
    ) -> np.ndarray:
        posterior = self.model.as_joint_belief(prior) * self._joint_observation_likelihood(A, observation, own_action)
        posterior /= max(float(posterior.sum()), 1e-16)
        return posterior

    def _predict_next_joint_belief(self, joint_belief: np.ndarray, action: int, B: np.ndarray) -> np.ndarray:
        joint = self.model.as_joint_belief(joint_belief)
        type_action = 0 if self.factorized_policies else int(action)
        type_transition = np.asarray(B[0][:, :, type_action], dtype=float)
        if self.factorized_policies:
            stance_transition = self.model.stance_transition_for_executed_own_action(int(action))
        else:
            stance_transition = np.asarray(B[1][:, :, int(action)], dtype=float)
        predictive = type_transition @ joint @ np.asarray(stance_transition, dtype=float).T
        predictive /= max(float(predictive.sum()), 1e-16)
        return predictive

    def _refresh_partner_payoff_likelihood(self, partner: aif.Agent) -> None:
        payoff_obs = np.zeros(
            (len(self.model.payoff_levels), self.num_social_actions, self.num_types, self.num_stances),
            dtype=float,
        )
        partner_table = np.asarray(partner.A[0][0], dtype=float)
        for agent_action in range(self.num_social_actions):
            coop_idx = int(self.model.payoff_index_table[agent_action, 0])
            defect_idx = int(self.model.payoff_index_table[agent_action, 1])
            payoff_obs[coop_idx, agent_action] += partner_table
            payoff_obs[defect_idx, agent_action] += 1.0 - partner_table
        partner.A[1] = payoff_obs

    def _apply_parameter_learning(self, partner_idx: int, posterior: np.ndarray, observed_partner_action: int) -> None:
        partner = self.partners[int(partner_idx)]
        table = np.asarray(partner.A[0][0], dtype=float)
        target = 1.0 if int(observed_partner_action) == 0 else 0.0
        updated = (1.0 - self.lr * posterior) * table + (self.lr * posterior) * target
        partner.A[0] = np.asarray([updated, 1.0 - updated], dtype=float)
        self._refresh_partner_payoff_likelihood(partner)

    def _build_transition_stacks(self) -> tuple[np.ndarray, np.ndarray]:
        B_type_stack = []
        B_stance_stack = []
        for partner in self.partners:
            B_type, B_stance_by_action = build_transition_views(
                partner.B,
                self.num_controls,
                factorized_policies=self.factorized_policies,
            )
            B_type_stack.append(B_type)
            B_stance_stack.append(B_stance_by_action)
        return np.stack(B_type_stack), np.stack(B_stance_stack)

    def choose_partner_and_action(self, active_partner: int | None = None) -> int:
        """Evaluate all policies and return the selected raw action."""

        active_partner_idx = -1 if active_partner is None else int(active_partner)
        B_type_stack, B_stance_stack = self._build_transition_stacks()
        decision = decision_step_trust_game(
            beliefs=self.partner_joint_beliefs,
            active_partner=active_partner_idx,
            policies=self.policies,
            observation_sequences=self.observation_sequences,
            B_type=B_type_stack,
            B_stance_by_action=B_stance_stack,
            partner_action_prob_tables=self.partner_action_prob_tables,
            payoff_index_table=self.model.payoff_index_table,
            agent_payoff_table=self.model.agent_payoff_table,
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
        sampled = aif.sample_action(self.partners[0], q_pi=q_pi, timestep=0)
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
                    self.model.assignment_mode,
                    self.num_partners,
                    self.num_controls,
                )
                selected_partner, selected_social_action = partner_sel, own_a
            else:
                stance_a = int(row[1])
                own_a = int(row[2])
                selected_partner = int(active_partner) if active_partner is not None else 0
                raw_action = encode_env_action_factorized(
                    selected_partner,
                    stance_a,
                    own_a,
                    self.model.assignment_mode,
                    self.num_partners,
                    self.num_controls,
                )
                selected_social_action = own_a
        else:
            raw_action = int(sampled)
            selected_partner, selected_social_action = decode_raw_action_to_partner_and_social(
                raw_action=raw_action,
                active_partner=0 if active_partner is None else int(active_partner),
                assignment_mode_code=self.assignment_mode_code,
                factorized_policies=self.factorized_policies,
                num_social_actions=self.num_social_actions,
                num_partners=self.num_partners,
            )

        predicted_partner_action_probs = _partner_action_distribution(
            self.partner_joint_beliefs[selected_partner],
            self.partner_action_prob_tables[selected_partner],
        )
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

    def plan_and_act(self, active_partner: int | None) -> int:
        return self.choose_partner_and_action(active_partner=active_partner)

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
    ) -> None:
        """Update beliefs and auxiliary state summaries from a realized interaction."""

        partner_idx = int(partner_idx)
        active = self.partners[partner_idx]
        round_log_ev = self._compute_round_log_evidence(partner_action)
        self.last_round_log_evidence = round_log_ev
        self.cumulative_log_evidence += round_log_ev

        prior = np.asarray(self.partner_joint_beliefs[partner_idx], dtype=float)
        posterior = self._infer_joint_posterior(
            prior,
            observation=observation,
            own_action=int(action_taken),
            A=active.A,
        )
        self._set_partner_qs(active, posterior)

        if self.learn_A:
            aif.update_pA(active, obs=[int(observation[0]), int(observation[1])], learning_rate=self.lr)
        elif self.use_parameter_learning:
            self._apply_parameter_learning(
                partner_idx=partner_idx,
                posterior=posterior,
                observed_partner_action=int(partner_action),
            )

        if self.learn_B and active.pB is not None:
            comp = (
                encode_instantaneous_index((0, int(action_taken), int(action_taken)), self.num_controls)
                if self.factorized_policies
                else int(action_taken)
            )
            qs_curr = obj_array(3)
            qs_curr[0] = posterior.sum(axis=1)
            qs_curr[1] = posterior.sum(axis=0)
            qs_curr[2] = onehot(int(action_taken), self.num_social_actions)
            qs_prev = obj_array(3)
            qs_prev[0] = prior.sum(axis=1)
            qs_prev[1] = prior.sum(axis=0)
            qs_prev[2] = onehot(int(self._prev_own_actions[partner_idx]), self.num_social_actions)
            active.pB = update_transition_dirichlet(active.pB, [comp, comp, comp], qs_curr, qs_prev)
            for factor in range(len(active.B)):
                conc = np.asarray(active.pB[factor], dtype=float)
                for action in range(conc.shape[2]):
                    sl = conc[:, :, action]
                    active.B[factor][:, :, action] = sl / np.maximum(sl.sum(axis=0, keepdims=True), 1e-16)

        if self.learn_E and self.last_q_pi.size:
            log_q = np.log(np.asarray(self.last_q_pi, dtype=float) + 1e-16)
            self.log_policy_prior = (1.0 - self.lr_E) * self.log_policy_prior + self.lr_E * log_q
            self.log_policy_prior -= float(np.mean(self.log_policy_prior))

        predictive_next = self._predict_next_joint_belief(
            posterior,
            action=int(action_taken),
            B=active.B,
        )
        self._prev_own_actions[partner_idx] = int(action_taken)
        self._update_auxiliary_states(partner_idx=partner_idx, partner_action=int(partner_action), payoff=float(payoff))

        self.partner_joint_posteriors[partner_idx] = posterior
        self.partner_joint_beliefs[partner_idx] = predictive_next
        self.partner_beliefs[partner_idx] = predictive_next.sum(axis=1)
        self.partner_stance_beliefs[partner_idx] = predictive_next.sum(axis=0)
        self._set_partner_qs(active, predictive_next)
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

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float) -> None:
        del partner_idx, partner_action, payoff
