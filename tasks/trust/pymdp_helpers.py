"""Thin helpers around the official pymdp API for trust-task agents."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
from typing import Any

import numpy as np


@dataclass
class PymdpInferenceResult:
    qs: Any
    q_pi: np.ndarray
    policy_scores: np.ndarray
    info: dict[str, Any]


def create_agent(bundle, gamma: float):
    from pymdp.agent import Agent

    return Agent(
        A=bundle.A,
        B=bundle.B,
        C=bundle.C,
        D=bundle.D,
        E=bundle.E,
        policies=bundle.policies,
        control_fac_idx=bundle.control_fac_idx,
        gamma=gamma,
    )


def infer_once(agent, obs: list[int], bundle) -> PymdpInferenceResult:
    del bundle

    state_result = _infer_states_with_empirical_prior(agent, obs)
    qs, info = _unpack_state_result(state_result)
    policy_result = agent.infer_policies(qs)
    q_pi, policy_scores = _unpack_policy_result(policy_result)

    return PymdpInferenceResult(
        qs=qs,
        q_pi=_normalize_policy_posterior(q_pi),
        policy_scores=_as_policy_vector(policy_scores, name="policy_scores"),
        info=info,
    )


def select_first_timestep_action(
    policies: np.ndarray,
    q_pi: np.ndarray,
    deterministic: bool,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    probabilities = _normalize_policy_posterior(q_pi)
    policy_array = np.asarray(policies)
    if policy_array.ndim != 3:
        raise ValueError(f"policies must have shape (num_policies, horizon, num_factors); got {policy_array.shape}.")
    if policy_array.shape[1] < 1:
        raise ValueError("policies must include at least one timestep.")
    if len(probabilities) != policy_array.shape[0]:
        raise ValueError(f"len(q_pi) must match number of policies; got {len(probabilities)} and {policy_array.shape[0]}.")

    policy_idx = (
        int(np.argmax(probabilities))
        if deterministic
        else int((rng or np.random.default_rng()).choice(len(probabilities), p=probabilities))
    )
    return np.asarray(policy_array[policy_idx, 0], dtype=int)


def _infer_states_with_empirical_prior(agent, obs: list[int]):
    infer_states = agent.infer_states
    signature = inspect.signature(infer_states)
    parameters = signature.parameters
    accepts_kwargs = any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters.values())
    accepts_args = any(parameter.kind is inspect.Parameter.VAR_POSITIONAL for parameter in parameters.values())
    accepts_empirical_prior_kw = accepts_kwargs or "empirical_prior" in parameters
    accepts_return_info_kw = accepts_kwargs or "return_info" in parameters
    accepts_preprocess_fn_kw = "preprocess_fn" in parameters
    accepts_positional_empirical_prior = accepts_args or _positional_parameter_count(parameters) >= 2

    if accepts_empirical_prior_kw:
        kwargs: dict[str, Any] = {"empirical_prior": agent.D}
        if accepts_return_info_kw:
            kwargs["return_info"] = True
        if accepts_preprocess_fn_kw:
            kwargs["preprocess_fn"] = lambda observations: _batched_categorical_observations(
                observations,
                num_obs=agent.num_obs,
                batch_size=agent.batch_size,
            )
        return infer_states(obs, **kwargs)

    if accepts_positional_empirical_prior:
        if accepts_return_info_kw:
            kwargs = {"return_info": True}
            if accepts_preprocess_fn_kw:
                kwargs["preprocess_fn"] = lambda observations: _batched_categorical_observations(
                    observations,
                    num_obs=agent.num_obs,
                    batch_size=agent.batch_size,
                )
            return infer_states(obs, agent.D, **kwargs)
        return infer_states(obs, agent.D)

    raise TypeError("agent.infer_states must accept an empirical_prior argument.")


def _positional_parameter_count(parameters: Any) -> int:
    return sum(
        parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        for parameter in parameters.values()
    )


def _unpack_state_result(state_result) -> tuple[Any, dict[str, Any]]:
    if not isinstance(state_result, tuple):
        return state_result, {}
    if len(state_result) >= 2 and isinstance(state_result[1], dict):
        return state_result[0], dict(state_result[1])
    return state_result[0], {}


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

    total = float(vector.sum())
    if not np.isfinite(total):
        raise ValueError("q_pi must have finite probability mass.")
    if not np.isclose(total, 1.0, rtol=1e-6, atol=1e-8):
        raise ValueError(f"q_pi probabilities must sum to 1 within tolerance; got {total}.")
    if total != 1.0:
        return vector / total
    return vector
