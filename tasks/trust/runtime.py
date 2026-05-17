"""Procedural trust-task runtime around official ``pymdp.Agent`` instances."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any

import jax.numpy as jnp
import numpy as np

from tasks.trust.payoffs import encode_action, encode_env_action_factorized
from tasks.trust.pomdp import (
    TrustPomdpTemplate,
    as_joint_belief,
    partner_action_distribution,
    predict_next_joint_belief,
)


@dataclass
class PartnerBank:
    agents: list[Any]
    latest_qs: list[Any | None] = field(default_factory=list)
    posterior_qs: list[Any | None] = field(default_factory=list)
    beta: Any | None = None
    latest_surprise: np.ndarray | None = None
    round_log_evidence: float = float("nan")
    cumulative_log_evidence: float = 0.0

    def __post_init__(self) -> None:
        if not self.latest_qs:
            self.latest_qs = [None for _ in self.agents]
        if not self.posterior_qs:
            self.posterior_qs = [None for _ in self.agents]


@dataclass(frozen=True)
class Decision:
    raw_action: int
    selected_partner: int
    selected_action: int
    stance_action: int
    own_action: int
    q_pi: np.ndarray
    policy_scores: np.ndarray
    best_policy_idx: int
    predicted_partner_action_probs: np.ndarray
    predictive_log_lik: float


@dataclass(frozen=True)
class PartnerSnapshot:
    partner_type_beliefs: np.ndarray
    partner_stance_beliefs: np.ndarray
    partner_joint_beliefs: np.ndarray
    partner_joint_posteriors: np.ndarray


def select_decision(
    *,
    bank: PartnerBank,
    template: TrustPomdpTemplate,
    active_partner: int | None,
    assignment_mode: str,
    base_gamma: float,
    action_selection: str,
    rng: np.random.Generator,
    affect_mode: str = "none",
) -> Decision:
    """Select a partner/action by calling official pymdp policy inference."""

    deterministic = str(action_selection) in {"deterministic", "argmax", "mode"}
    if str(assignment_mode) != "agent_choice":
        if active_partner is None:
            raise ValueError("active_partner is required for random assignment.")
        selected_partner = int(active_partner)
        q_pi, policy_scores = _infer_partner_policy(
            bank=bank,
            template=template,
            partner_idx=selected_partner,
            base_gamma=base_gamma,
            affect_mode=affect_mode,
        )
        policy_idx = _choose_index(q_pi, deterministic=deterministic, rng=rng)
        first_step = np.asarray(template.policies[policy_idx, 0], dtype=int)
        raw_action, stance_action, own_action = _encode_policy_action(
            template=template,
            partner_idx=selected_partner,
            first_step=first_step,
            assignment_mode=str(assignment_mode),
        )
        predicted = _predicted_action_probs(bank=bank, template=template, partner_idx=selected_partner)
        return Decision(
            raw_action=raw_action,
            selected_partner=selected_partner,
            selected_action=own_action,
            stance_action=stance_action,
            own_action=own_action,
            q_pi=q_pi,
            policy_scores=policy_scores,
            best_policy_idx=policy_idx,
            predicted_partner_action_probs=predicted,
            predictive_log_lik=float("nan"),
        )

    candidates: list[tuple[int, int, np.ndarray, float, float]] = []
    for partner_idx in range(len(bank.agents)):
        _q_pi, policy_scores = _infer_partner_policy(
            bank=bank,
            template=template,
            partner_idx=partner_idx,
            base_gamma=base_gamma,
            affect_mode=affect_mode,
        )
        partner_gamma = gamma_for_partner(
            base_gamma=base_gamma,
            beta=bank.beta,
            partner_idx=partner_idx,
            affect_mode=affect_mode,
        )
        for policy_idx, score in enumerate(policy_scores):
            candidates.append(
                (
                    partner_idx,
                    policy_idx,
                    np.asarray(template.policies[policy_idx, 0], dtype=int),
                    float(score),
                    float(partner_gamma) * float(score),
                )
            )
    scores = np.asarray([candidate[3] for candidate in candidates], dtype=float)
    candidate_logits = np.asarray([candidate[4] for candidate in candidates], dtype=float)
    candidate_probs = _softmax(candidate_logits)
    candidate_idx = _choose_index(candidate_probs, deterministic=deterministic, rng=rng)
    selected_partner, policy_idx, first_step, _score, _logit = candidates[candidate_idx]
    raw_action, stance_action, own_action = _encode_policy_action(
        template=template,
        partner_idx=selected_partner,
        first_step=first_step,
        assignment_mode=str(assignment_mode),
    )
    q_pi = np.zeros_like(candidate_probs) if deterministic else candidate_probs
    if deterministic:
        q_pi[candidate_idx] = 1.0
    predicted = _predicted_action_probs(bank=bank, template=template, partner_idx=selected_partner)
    return Decision(
        raw_action=raw_action,
        selected_partner=int(selected_partner),
        selected_action=int(own_action),
        stance_action=int(stance_action),
        own_action=int(own_action),
        q_pi=q_pi,
        policy_scores=scores,
        best_policy_idx=int(candidate_idx),
        predicted_partner_action_probs=predicted,
        predictive_log_lik=float("nan"),
    )


def update_partner_after_observation(
    *,
    bank: PartnerBank,
    template: TrustPomdpTemplate,
    partner_idx: int,
    obs: list[int],
    own_action: int,
) -> Any:
    """Update one partner-local official pymdp agent after an observation."""

    idx = int(partner_idx)
    agent = bank.agents[idx]
    prior_joint = _joint_from_qs(template, bank.latest_qs[idx] if bank.latest_qs[idx] is not None else agent.D)
    _set_partner_prior(agent, template, prior_joint, _onehot(int(own_action), template.num_social_actions))
    qs, _info = _infer_states(agent, obs)
    posterior = _joint_from_qs(template, qs)
    predictive_next = predict_next_joint_belief(template, posterior, int(own_action))
    next_qs = _qs_from_joint(template, predictive_next, _onehot(int(own_action), template.num_social_actions))
    bank.posterior_qs[idx] = qs
    bank.latest_qs[idx] = next_qs
    _set_partner_prior(agent, template, predictive_next, _onehot(int(own_action), template.num_social_actions))
    return qs


def snapshot_partner_bank(*, bank: PartnerBank, template: TrustPomdpTemplate) -> PartnerSnapshot:
    joint_beliefs = []
    joint_posteriors = []
    for idx, agent in enumerate(bank.agents):
        latest = bank.latest_qs[idx] if bank.latest_qs[idx] is not None else agent.D
        posterior = bank.posterior_qs[idx] if bank.posterior_qs[idx] is not None else latest
        joint_beliefs.append(_joint_from_qs(template, latest))
        joint_posteriors.append(_joint_from_qs(template, posterior))
    partner_joint_beliefs = np.asarray(joint_beliefs, dtype=float)
    partner_joint_posteriors = np.asarray(joint_posteriors, dtype=float)
    return PartnerSnapshot(
        partner_type_beliefs=partner_joint_beliefs.sum(axis=2),
        partner_stance_beliefs=partner_joint_beliefs.sum(axis=1),
        partner_joint_beliefs=partner_joint_beliefs,
        partner_joint_posteriors=partner_joint_posteriors,
    )


def gamma_for_partner(*, base_gamma: float, beta, partner_idx: int, affect_mode: str) -> float:
    if beta is None or affect_mode in {"none", "decouple", "fixed"}:
        return float(base_gamma)
    expected_beta = float(np.asarray(beta.expected_beta(), dtype=float)[int(partner_idx)])
    return float(base_gamma) / max(expected_beta, 1e-16)


def update_beta_after_observation(
    *,
    bank: PartnerBank,
    partner_idx: int,
    predicted_partner_action_probs: np.ndarray,
    observed_partner_action: int,
    affect_mode: str,
) -> float:
    if bank.beta is None or affect_mode in {"none", "fixed"}:
        return float("nan")
    probability = float(np.asarray(predicted_partner_action_probs, dtype=float)[int(observed_partner_action)])
    surprise = 1.0 - probability
    bank.beta.update(entity=int(partner_idx), surprise=surprise)
    if bank.latest_surprise is None:
        bank.latest_surprise = np.full((len(bank.agents),), np.nan, dtype=float)
    bank.latest_surprise[int(partner_idx)] = surprise
    return surprise


def predictive_log_likelihood(predicted_partner_action_probs: np.ndarray, observed_partner_action: int) -> float:
    probability = float(np.asarray(predicted_partner_action_probs, dtype=float)[int(observed_partner_action)])
    return float(np.log(max(probability, 1e-16)))


def _infer_partner_policy(
    *,
    bank: PartnerBank,
    template: TrustPomdpTemplate,
    partner_idx: int,
    base_gamma: float,
    affect_mode: str,
) -> tuple[np.ndarray, np.ndarray]:
    idx = int(partner_idx)
    agent = bank.agents[idx]
    _set_agent_gamma(
        agent,
        gamma_for_partner(base_gamma=base_gamma, beta=bank.beta, partner_idx=idx, affect_mode=affect_mode),
    )
    qs = bank.latest_qs[idx] if bank.latest_qs[idx] is not None else _policy_qs_from_agent_D(agent)
    result = agent.infer_policies(qs)
    q_pi, policy_scores = _unpack_policy_result(result)
    return _normalize_policy_posterior(q_pi), _as_policy_vector(policy_scores, "policy_scores")


def _encode_policy_action(
    *,
    template: TrustPomdpTemplate,
    partner_idx: int,
    first_step: np.ndarray,
    assignment_mode: str,
) -> tuple[int, int, int]:
    controls = np.asarray(first_step, dtype=int).ravel()
    if template.uses_factorized_controls:
        stance_action = int(controls[-2])
        own_action = int(controls[-1])
        raw_action = encode_env_action_factorized(
            int(partner_idx),
            stance_action,
            own_action,
            assignment_mode,
            template.num_partners,
            list(template.num_controls),
        )
        return int(raw_action), stance_action, own_action
    social_action = int(controls[0])
    if assignment_mode == "agent_choice":
        return (
            encode_action(
                int(partner_idx),
                social_action,
                template.num_partners,
                assignment_mode,
                num_social_actions=template.num_social_actions,
            ),
            social_action,
            social_action,
        )
    return social_action, social_action, social_action


def _predicted_action_probs(*, bank: PartnerBank, template: TrustPomdpTemplate, partner_idx: int) -> np.ndarray:
    agent = bank.agents[int(partner_idx)]
    qs = bank.latest_qs[int(partner_idx)] if bank.latest_qs[int(partner_idx)] is not None else agent.D
    return partner_action_distribution(template, _joint_from_qs(template, qs))


def _joint_from_qs(template: TrustPomdpTemplate, qs: Any) -> np.ndarray:
    type_belief = _normalize(np.asarray(qs[0], dtype=float).squeeze())
    stance_belief = _normalize(np.asarray(qs[1], dtype=float).squeeze())
    return as_joint_belief(template, np.outer(type_belief, stance_belief))


def _qs_from_joint(template: TrustPomdpTemplate, joint_belief: np.ndarray, own_belief: np.ndarray) -> list[jnp.ndarray]:
    joint = as_joint_belief(template, joint_belief)
    type_belief = _normalize(joint.sum(axis=1))
    stance_belief = _normalize(joint.sum(axis=0))
    own = _normalize(own_belief)
    return [
        jnp.asarray(type_belief[None, None, :]),
        jnp.asarray(stance_belief[None, None, :]),
        jnp.asarray(own[None, None, :]),
    ]


def _set_partner_prior(
    agent,
    template: TrustPomdpTemplate,
    joint_belief: np.ndarray,
    own_belief: np.ndarray,
) -> None:
    joint = as_joint_belief(template, joint_belief)
    D = [
        jnp.asarray(_normalize(joint.sum(axis=1))[None, :]),
        jnp.asarray(_normalize(joint.sum(axis=0))[None, :]),
        jnp.asarray(_normalize(own_belief)[None, :]),
    ]
    object.__setattr__(agent, "D", D)


def _policy_qs_from_agent_D(agent) -> list[jnp.ndarray]:
    return [jnp.asarray(np.asarray(factor, dtype=float).squeeze()[None, None, :]) for factor in agent.D]


def _set_agent_gamma(agent, gamma: float) -> None:
    if hasattr(agent, "gamma"):
        object.__setattr__(agent, "gamma", jnp.asarray([float(gamma)]))


def _infer_states(agent, obs: list[int]) -> tuple[Any, dict[str, Any]]:
    infer_states = agent.infer_states
    parameters = inspect.signature(infer_states).parameters
    accepts_kwargs = any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters.values())
    kwargs: dict[str, Any] = {}
    if accepts_kwargs or "return_info" in parameters:
        kwargs["return_info"] = True
    if "preprocess_fn" in parameters:
        kwargs["preprocess_fn"] = lambda observations: _batched_categorical_observations(
            observations,
            num_obs=agent.num_obs,
            batch_size=agent.batch_size,
        )
    state_result = infer_states(obs, agent.D, **kwargs)
    if isinstance(state_result, tuple) and len(state_result) >= 2 and isinstance(state_result[1], dict):
        return state_result[0], dict(state_result[1])
    if isinstance(state_result, tuple):
        return state_result[0], {}
    return state_result, {}


def _batched_categorical_observations(observations, num_obs, batch_size: int) -> list[np.ndarray]:
    categorical = []
    for modality, observation in enumerate(observations):
        vector = np.zeros((int(batch_size), int(num_obs[modality])), dtype=float)
        vector[:, int(observation)] = 1.0
        categorical.append(vector)
    return categorical


def _unpack_policy_result(policy_result) -> tuple[np.ndarray, np.ndarray]:
    if not isinstance(policy_result, tuple) or len(policy_result) < 2:
        raise TypeError("agent.infer_policies(qs) must return (q_pi, policy_scores).")
    return np.asarray(policy_result[0], dtype=float), np.asarray(policy_result[1], dtype=float)


def _as_policy_vector(values: np.ndarray, name: str) -> np.ndarray:
    vector = np.asarray(values, dtype=float).squeeze()
    if vector.ndim != 1:
        raise ValueError(f"{name} must be a single policy vector after squeezing; got shape {values.shape}.")
    if vector.size == 0:
        raise ValueError(f"{name} must not be empty.")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} contains non-finite values.")
    return vector


def _normalize_policy_posterior(q_pi: np.ndarray) -> np.ndarray:
    vector = _as_policy_vector(q_pi, name="q_pi")
    if np.any(vector < 0.0):
        raise ValueError("q_pi contains negative probabilities.")
    return _normalize(vector)


def _choose_index(probabilities: np.ndarray, *, deterministic: bool, rng: np.random.Generator) -> int:
    probs = _normalize(probabilities)
    return int(np.argmax(probs)) if deterministic else int(rng.choice(len(probs), p=probs))


def _softmax(values: np.ndarray) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    shifted = vector - float(np.max(vector))
    exp = np.exp(shifted)
    return _normalize(exp)


def _normalize(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    total = float(array.sum())
    if not np.isfinite(total) or total <= 0.0:
        return np.full(array.shape, 1.0 / max(array.size, 1), dtype=float)
    return array / total


def _onehot(idx: int, size: int) -> np.ndarray:
    out = np.zeros(int(size), dtype=float)
    out[int(idx)] = 1.0
    return out
