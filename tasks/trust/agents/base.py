"""pymdp-backed trust-game agent composition layer."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np

from tasks.trust import pymdp_helpers
from tasks.trust.models import TrustGameModel
from tasks.trust.payoffs import encode_env_action_factorized


class TrustGameAgent:
    """Active-inference agent for the multi-partner trust game.

    The experiment-facing object owns one official ``pymdp.Agent`` per partner.
    Each local pymdp agent models a single partner using the shared trust-game
    model bundle; this wrapper handles partner selection, raw environment action
    encoding, and diagnostics expected by runners/loggers.
    """

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
        del pA_scale, pB_scale
        self.model = model
        self.num_partners = int(model.num_partners)
        self.num_types = int(model.num_types)
        self.num_stances = int(model.num_stances)
        self.num_controls = [int(x) for x in model.num_controls]
        self.num_planning_instantaneous = int(np.prod(self.num_controls))
        self.num_social_actions = int(model.num_social_actions)
        self.factorized_policies = bool(model.uses_factorized_controls)
        self.assignment_mode_code = 1 if model.assignment_mode == "agent_choice" else 0
        self.planning_horizon = int(planning_horizon)
        self.gamma = float(gamma)
        self.lr = float(lr)
        self.action_sampling = str(action_sampling)
        self.action_selection = str(action_sampling)
        self.use_utility = bool(use_utility)
        self.use_information_gain = bool(use_information_gain)
        self.max_policies = max_policies
        self.reference_horizon = int(reference_horizon if reference_horizon is not None else planning_horizon)
        self.seed = int(seed)
        self.use_parameter_learning = bool(use_parameter_learning)
        self.learn_A = bool(learn_A)
        self.learn_B = bool(learn_B)
        self.learn_E = bool(learn_E)
        self.lr_E = float(lr_E)
        self.rng = np.random.default_rng(self.seed)

        self.bundle = model.to_pymdp_bundle(
            planning_horizon=self.planning_horizon,
            max_policies=self.max_policies,
            rng=self.rng,
        )
        if not self.use_utility or not self.use_information_gain:
            self.bundle = replace(
                self.bundle,
                C=self.bundle.C if self.use_utility else [np.zeros_like(np.asarray(c, dtype=float)) for c in self.bundle.C],
            )
        self.policies = np.asarray(self.bundle.policies, dtype=int)
        self.partners = [pymdp_helpers.create_agent(self.bundle, gamma=self.gamma) for _ in range(self.num_partners)]
        for idx in range(self.num_partners):
            self._refresh_partner_agent(idx, use_information_gain=self.use_information_gain)

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
        return np.asarray(self.partner_beliefs, dtype=float)

    @property
    def partner_action_prob_tables(self) -> np.ndarray:
        return np.repeat(np.asarray(self.model.partner_action_prob_table, dtype=float)[None, :, :], self.num_partners, axis=0)

    @property
    def partner_action_prob_table(self) -> np.ndarray:
        return self.partner_action_prob_tables

    def reset(self):
        type_prior = np.asarray(self.model.D[0], dtype=float)
        stance_prior = np.asarray(self.model.D[1], dtype=float)
        own_prior = np.asarray(self.model.D[2], dtype=float)
        joint_prior = np.outer(type_prior, stance_prior)
        joint_prior /= max(float(joint_prior.sum()), 1e-16)

        self.partner_beliefs = np.repeat(joint_prior[None, :, :], self.num_partners, axis=0)
        self.partner_joint_beliefs = self.partner_beliefs.copy()
        self.partner_joint_posteriors = self.partner_beliefs.copy()
        self.partner_stance_beliefs = np.repeat(stance_prior[None, :], self.num_partners, axis=0)
        self.partner_type_beliefs = np.repeat(type_prior[None, :], self.num_partners, axis=0)

        self._partner_qs: list[Any] = [None for _ in range(self.num_partners)]
        for partner in self.partners:
            if hasattr(partner, "reset"):
                partner.reset()
        for idx in range(self.num_partners):
            self._set_partner_prior(idx, joint_prior, own_prior)

        self.q_pi = None
        self.policy_scores = None
        self.best_policy_idx = None
        self.selected_partner = None
        self.selected_action = None
        self.last_qs = None

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
        default_action = int(np.argmax(own_prior))
        self._prev_own_actions = np.full((self.num_partners,), default_action, dtype=int)
        self.post_observation_qs = None
        self.post_observation_q_pi = None
        self.post_observation_policy_scores = None
        self.post_observation_info: dict[str, Any] = {}

    def precision_signal(self):
        return np.ones((self.num_partners,), dtype=float)

    def _as_backend_array(self, values: np.ndarray) -> Any:
        try:
            import jax.numpy as jnp

            return jnp.asarray(values, dtype=float)
        except Exception:  # pragma: no cover - jax is a project dependency, but numpy is safe here.
            return np.asarray(values, dtype=float)

    def _onehot(self, idx: int, size: int) -> np.ndarray:
        out = np.zeros(int(size), dtype=float)
        out[int(idx)] = 1.0
        return out

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        array = np.asarray(values, dtype=float)
        total = float(array.sum())
        if not np.isfinite(total) or total <= 0.0:
            return np.full(array.shape, 1.0 / max(array.size, 1), dtype=float)
        return array / total

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        logits = np.asarray(logits, dtype=float)
        if logits.size == 0:
            return logits
        shifted = logits - float(np.max(logits))
        exp = np.exp(shifted)
        return self._normalize(exp)

    def _set_partner_prior(
        self,
        partner_idx: int,
        joint_belief: np.ndarray,
        own_belief: np.ndarray | None = None,
    ) -> None:
        joint = self.model.as_joint_belief(joint_belief)
        type_belief = self._normalize(joint.sum(axis=1))
        stance_belief = self._normalize(joint.sum(axis=0))
        own = self._normalize(np.asarray(own_belief if own_belief is not None else self.model.D[2], dtype=float))
        D = [
            self._as_backend_array(type_belief[None, :]),
            self._as_backend_array(stance_belief[None, :]),
            self._as_backend_array(own[None, :]),
        ]
        self._refresh_partner_agent(int(partner_idx), D=D)
        self._partner_qs[int(partner_idx)] = [self._as_backend_array(np.asarray(factor, dtype=float)[:, None, :]) for factor in D]

    def _refresh_partner_agent(
        self,
        partner_idx: int,
        *,
        D: Any | None = None,
        gamma: float | None = None,
        use_information_gain: bool | None = None,
    ) -> None:
        """Refresh mutable runtime fields on official frozen pymdp agents in one place."""

        partner = self.partners[int(partner_idx)]
        if D is not None:
            object.__setattr__(partner, "D", D)
        if gamma is not None:
            object.__setattr__(partner, "gamma", self._as_backend_array(np.asarray([float(gamma)], dtype=float)))
        if use_information_gain is not None:
            supported_fields = [field for field in ("use_states_info_gain", "use_param_info_gain") if hasattr(partner, field)]
            if not supported_fields and not bool(use_information_gain):
                raise NotImplementedError(
                    "use_information_gain=False cannot be represented by this pymdp.Agent API."
                )
            if hasattr(partner, "use_states_info_gain"):
                object.__setattr__(partner, "use_states_info_gain", bool(use_information_gain))
            if hasattr(partner, "use_param_info_gain"):
                has_parameter_posteriors = getattr(partner, "pA", None) is not None or getattr(partner, "pB", None) is not None
                object.__setattr__(partner, "use_param_info_gain", bool(use_information_gain and has_parameter_posteriors))

    def _qs_to_joint(self, qs: Any) -> np.ndarray:
        type_belief = self._normalize(np.asarray(qs[0], dtype=float).squeeze())
        stance_belief = self._normalize(np.asarray(qs[1], dtype=float).squeeze())
        joint = np.outer(type_belief, stance_belief)
        return self.model.as_joint_belief(joint)

    def _unpack_policy_result(self, policy_result: Any) -> tuple[np.ndarray, np.ndarray]:
        if not isinstance(policy_result, tuple) or len(policy_result) < 2:
            raise TypeError("partner.infer_policies(qs) must return (q_pi, policy_scores).")
        q_pi = np.asarray(policy_result[0], dtype=float).squeeze()
        policy_scores = np.asarray(policy_result[1], dtype=float).squeeze()
        if q_pi.ndim != 1 or policy_scores.ndim != 1:
            raise ValueError("pymdp policy diagnostics must be one-dimensional after squeezing.")
        return self._normalize(q_pi), policy_scores

    def _infer_partner(self, partner_idx: int) -> pymdp_helpers.PymdpInferenceResult:
        partner_idx = int(partner_idx)
        partner = self.partners[partner_idx]
        qs = self._partner_qs[partner_idx] if self._partner_qs[partner_idx] is not None else partner.D
        precision = float(np.asarray(self.precision_signal(), dtype=float)[partner_idx])
        if np.isfinite(precision) and precision > 0.0 and hasattr(partner, "gamma"):
            self._refresh_partner_agent(partner_idx, gamma=self.gamma / precision)
        policy_result = partner.infer_policies(qs)
        q_pi, policy_scores = self._unpack_policy_result(policy_result)
        return pymdp_helpers.PymdpInferenceResult(qs=qs, q_pi=q_pi, policy_scores=policy_scores, info={})

    def _choose_index(self, probabilities: np.ndarray, deterministic: bool) -> int:
        probs = self._normalize(probabilities)
        if deterministic:
            return int(np.argmax(probs))
        return int(self.rng.choice(len(probs), p=probs))

    def _deterministic_action_selection(self) -> bool:
        return self.action_selection in {"deterministic", "argmax", "mode"}

    def _encode_policy_action(self, partner_idx: int, first_step: np.ndarray) -> tuple[int, int, int]:
        controls = np.asarray(first_step, dtype=int).ravel()
        if self.factorized_policies:
            stance_action = int(controls[-2])
            own_action = int(controls[-1])
        else:
            stance_action = int(controls[0])
            own_action = int(controls[0])
        raw_action = encode_env_action_factorized(
            int(partner_idx),
            stance_action,
            own_action,
            self.model.assignment_mode,
            self.num_partners,
            self.num_controls,
        )
        return int(raw_action), stance_action, own_action

    def choose_partner_and_action(self, active_partner: int | None = None) -> int:
        """Plan with official pymdp and return the raw environment action."""

        deterministic = self._deterministic_action_selection()
        if active_partner is not None:
            partner_idx = int(active_partner)
            result = self._infer_partner(partner_idx)
            q_pi = np.asarray(result.q_pi, dtype=float)
            first_step = pymdp_helpers.select_first_timestep_action(
                self.policies,
                q_pi,
                deterministic=deterministic,
                rng=self.rng,
            )
            policy_idx = int(np.argmax(q_pi)) if deterministic else self._policy_index_for_first_step(first_step, q_pi)
            raw_action, _, own_action = self._encode_policy_action(partner_idx, first_step)
            selected_partner = partner_idx
            selected_social_action = own_action
            self._store_decision_diagnostics(result, q_pi, policy_idx, selected_partner, selected_social_action, raw_action)
            return raw_action

        candidates: list[tuple[int, int, np.ndarray, float]] = []
        partner_results: dict[int, pymdp_helpers.PymdpInferenceResult] = {}
        for partner_idx in range(self.num_partners):
            result = self._infer_partner(partner_idx)
            partner_results[partner_idx] = result
            for policy_idx, score in enumerate(np.asarray(result.policy_scores, dtype=float)):
                prior = self.log_policy_prior[policy_idx] if policy_idx < len(self.log_policy_prior) else 0.0
                first = np.asarray(self.policies[policy_idx, 0], dtype=int)
                candidates.append((partner_idx, policy_idx, first, float(score + prior)))

        candidate_scores = np.asarray([candidate[3] for candidate in candidates], dtype=float)
        candidate_probs = self._softmax(candidate_scores)
        candidate_idx = self._choose_index(candidate_probs, deterministic=deterministic)
        selected_partner, policy_idx, first_step, _ = candidates[candidate_idx]
        raw_action, _, own_action = self._encode_policy_action(selected_partner, first_step)

        result = partner_results[selected_partner]
        q_pi = np.zeros(len(candidates), dtype=float) if deterministic else candidate_probs
        if deterministic:
            q_pi[candidate_idx] = 1.0
        self._store_decision_diagnostics(
            result,
            q_pi,
            candidate_idx,
            selected_partner,
            own_action,
            raw_action,
            policy_scores=candidate_scores,
        )
        return raw_action

    def _policy_index_for_first_step(self, first_step: np.ndarray, q_pi: np.ndarray) -> int:
        matches = np.flatnonzero(np.all(self.policies[:, 0, :] == np.asarray(first_step, dtype=int), axis=1))
        if matches.size == 0:
            return int(np.argmax(q_pi))
        best_local = int(matches[np.argmax(np.asarray(q_pi, dtype=float)[matches])])
        return best_local

    def _store_decision_diagnostics(
        self,
        result: pymdp_helpers.PymdpInferenceResult,
        q_pi: np.ndarray,
        best_policy_idx: int,
        selected_partner: int,
        selected_social_action: int,
        raw_action: int,
        policy_scores: np.ndarray | None = None,
    ) -> None:
        predicted_partner_action_probs = self.model.partner_action_distribution(self.partner_beliefs[int(selected_partner)])
        self.q_pi = np.asarray(q_pi, dtype=float)
        self.policy_scores = np.asarray(
            result.policy_scores if policy_scores is None else policy_scores,
            dtype=float,
        )
        self.best_policy_idx = int(best_policy_idx)
        self.selected_partner = int(selected_partner)
        self.selected_action = int(selected_social_action)
        self.last_qs = result.qs

        self.last_q_pi = self.q_pi
        self.last_G = self.policy_scores
        self.last_best_policy_step_costs = np.asarray([], dtype=float)
        self.last_mean_abs_step_efe = float(np.mean(np.abs(self.policy_scores))) if self.policy_scores.size else np.nan
        self.last_best_policy_idx = self.best_policy_idx
        self.pending_prediction_partner = self.selected_partner
        self.pending_prediction_probs = np.asarray(predicted_partner_action_probs, dtype=float)
        self.pending_social_action = self.selected_action
        self.last_raw_action = int(raw_action)
        self.last_selected_partner = self.selected_partner
        self.last_selected_action = self.selected_action

    def plan_and_act(self, active_partner: int | None) -> int:
        return self.choose_partner_and_action(active_partner=active_partner)

    def _compute_round_log_evidence(self, partner_action: int) -> float:
        probs = np.asarray(self.pending_prediction_probs, dtype=float)
        p_obs = float(probs[int(partner_action)])
        return float(np.log(max(p_obs, 1e-16)))

    def observe_outcome(
        self,
        partner_idx: int | None = None,
        observation: list[int] | None = None,
        action_taken: int | None = None,
        partner_action: int | None = None,
        payoff: float = np.nan,
        true_partner_type: str | None = None,
        true_partner_stance: str | None = None,
        *,
        active_partner: int | None = None,
        agent_action: int | None = None,
    ) -> None:
        """Update partner-local pymdp beliefs and experiment diagnostics."""

        if partner_idx is None:
            partner_idx = active_partner
        if action_taken is None:
            action_taken = agent_action
        if partner_idx is None:
            raise ValueError("observe_outcome requires partner_idx or active_partner.")
        if observation is None:
            raise ValueError("observe_outcome requires observation=[partner_action, payoff_obs].")
        if action_taken is None:
            raise ValueError("observe_outcome requires action_taken or agent_action.")
        if partner_action is None:
            partner_action = int(observation[0])

        partner_idx = int(partner_idx)
        action_taken = int(action_taken)
        partner_action = int(partner_action)
        round_log_ev = self._compute_round_log_evidence(partner_action)
        self.last_round_log_evidence = round_log_ev
        self.cumulative_log_evidence += round_log_ev

        prior_joint = np.asarray(self.partner_beliefs[partner_idx], dtype=float)
        self._set_partner_prior(partner_idx, prior_joint, self._onehot(action_taken, self.num_social_actions))
        result = pymdp_helpers.infer_once(self.partners[partner_idx], [int(observation[0]), int(observation[1])], self.bundle)
        posterior = self._qs_to_joint(result.qs)
        self._partner_qs[partner_idx] = result.qs
        self.post_observation_qs = result.qs
        self.post_observation_q_pi = np.asarray(result.q_pi, dtype=float)
        self.post_observation_policy_scores = np.asarray(result.policy_scores, dtype=float)
        self.post_observation_info = dict(result.info)

        predictive_next = self.model.predict_next_joint_belief(posterior, action_taken)
        self._prev_own_actions[partner_idx] = action_taken
        self._update_auxiliary_states(partner_idx=partner_idx, partner_action=partner_action, payoff=float(payoff))

        self.partner_joint_posteriors[partner_idx] = posterior
        self.partner_beliefs[partner_idx] = predictive_next
        self.partner_joint_beliefs[partner_idx] = predictive_next
        self.partner_type_beliefs[partner_idx] = predictive_next.sum(axis=1)
        self.partner_stance_beliefs[partner_idx] = predictive_next.sum(axis=0)
        self._set_partner_prior(partner_idx, predictive_next, self._onehot(action_taken, self.num_social_actions))

        if self.learn_E and self.post_observation_q_pi.size == self.log_policy_prior.size:
            log_q = np.log(np.asarray(self.post_observation_q_pi, dtype=float) + 1e-16)
            self.log_policy_prior = (1.0 - self.lr_E) * self.log_policy_prior + self.lr_E * log_q
            self.log_policy_prior -= float(np.mean(self.log_policy_prior))

        self.last_observation_partner = partner_idx
        self.last_true_partner_type = true_partner_type
        self.last_true_partner_stance = true_partner_stance
        self.last_partner_action = partner_action
        self.last_payoff = float(payoff)

    def get_partner_type_belief(self, partner_idx: int) -> np.ndarray:
        return np.asarray(self.partner_beliefs[int(partner_idx)].sum(axis=1), dtype=float)

    def get_partner_stance_belief(self, partner_idx: int) -> np.ndarray:
        return np.asarray(self.partner_beliefs[int(partner_idx)].sum(axis=0), dtype=float)

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
            "partner_joint_beliefs": np.asarray(self.partner_beliefs, dtype=float),
            "partner_joint_posteriors": np.asarray(self.partner_joint_posteriors, dtype=float),
            "partner_stance_beliefs": np.asarray(self.partner_stance_beliefs, dtype=float),
            "planning_cost": self.planning_cost,
            "planning_cost_ratio": self.planning_cost_ratio,
            "round_log_evidence": self.last_round_log_evidence,
            "cumulative_log_evidence": self.cumulative_log_evidence,
        }

    def _update_auxiliary_states(self, partner_idx: int, partner_action: int, payoff: float) -> None:
        del partner_idx, partner_action, payoff
