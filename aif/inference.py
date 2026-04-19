"""Free-function inference primitives for :mod:`aif`."""

from __future__ import annotations

import numpy as np

from aif.agent import Agent
from aif.efe import compute_efe_all_policies
from aif.maths import log_stable, softmax, spm_dot


def _get_prior(agent: Agent, action: list[int] | None) -> np.ndarray:
    num_factors = len(agent.D)
    prior = np.empty(num_factors, dtype=object)

    if action is None and agent.qs is None:
        source = agent.D
    elif agent.qs is not None:
        source = agent.qs
    else:
        source = agent.D

    for factor in range(num_factors):
        current = np.asarray(source[factor], dtype=float).copy()
        if action is not None:
            B_factor = np.asarray(agent.B[factor], dtype=float)
            action_idx = int(action[min(factor, len(action) - 1)])
            current = B_factor[:, :, action_idx] @ current
        prior[factor] = current
    return prior


def _factor_axis_map(likelihood_shape: tuple[int, ...], factor_sizes: list[int]) -> dict[int, int]:
    mapping: dict[int, int] = {}
    used_axes: set[int] = set()

    for factor, size in enumerate(factor_sizes):
        candidates = [axis for axis, axis_size in enumerate(likelihood_shape) if axis_size == size and axis not in used_axes]
        if not candidates:
            continue
        if len(candidates) > 1:
            raise ValueError(
                f"Ambiguous modality shape {likelihood_shape} for factor {factor} with size {size}; "
                "cannot infer factor axes safely."
            )
        mapping[factor] = candidates[0]
        used_axes.add(candidates[0])
    return mapping


def infer_states(agent: Agent, obs: list[int], action: list[int] | None = None) -> np.ndarray:
    """Perform a single Bayesian belief update over hidden-state factors."""

    prior = _get_prior(agent, action)
    num_factors = len(prior)
    likelihoods = np.asarray(agent.A, dtype=object)
    posterior = np.empty(num_factors, dtype=object)

    for factor in range(num_factors):
        log_belief = log_stable(prior[factor], backend="numpy")
        for modality, modality_likelihood in enumerate(likelihoods):
            observation_idx = int(obs[min(modality, len(obs) - 1)])
            likelihood_slice = np.asarray(modality_likelihood[observation_idx], dtype=float)
            if likelihood_slice.ndim == 1:
                factor_likelihood = likelihood_slice
            else:
                factor_axes = _factor_axis_map(likelihood_slice.shape, [len(q) for q in prior])
                if factor not in factor_axes:
                    continue
                factor_likelihood = likelihood_slice
                for other_factor, axis in sorted(factor_axes.items(), key=lambda item: item[1], reverse=True):
                    if other_factor == factor:
                        continue
                    factor_likelihood = np.tensordot(
                        factor_likelihood,
                        np.asarray(prior[other_factor], dtype=float),
                        axes=([axis], [0]),
                    )
                factor_likelihood = np.asarray(factor_likelihood, dtype=float).reshape(-1)
            log_belief = log_belief + log_stable(factor_likelihood, backend="numpy")
        posterior[factor] = softmax(log_belief, backend="numpy")

    agent.qs = posterior
    return posterior


def infer_policies(agent: Agent) -> tuple[np.ndarray, np.ndarray]:
    """Return policy posterior ``q_pi`` and expected free energy ``G``."""

    if agent.qs is None:
        agent.reset()

    if len(agent.qs) != 1 or len(agent.B) != 1 or any(np.asarray(modality).ndim != 2 for modality in agent.A):
        raise ValueError("infer_policies currently supports single-factor agents only")

    policies = np.asarray(agent.policies, dtype=int)
    if policies.ndim == 3 and policies.shape[-1] == 1:
        policies = policies[..., 0]

    G = compute_efe_all_policies(
        A=agent.A,
        B=agent.B,
        C=agent.C,
        qs=agent.qs,
        policies=policies,
        use_utility=agent.use_utility,
        use_information_gain=agent.use_information_gain,
    )
    logits = -float(agent.gamma) * np.asarray(G, dtype=float)
    if agent.E is not None:
        logits = logits + np.asarray(agent.E, dtype=float)
    q_pi = softmax(logits, backend="numpy")
    return q_pi, np.asarray(G, dtype=float)
