"""Native trust-game POMDP template construction for official pymdp agents."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any

import jax.numpy as jnp
import numpy as np

from tasks.trust.payoffs import (
    build_graded_payoff_matrix,
    build_payoff_matrix,
    decode_instantaneous_index,
    encode_instantaneous_index,
    expected_agent_payoff,
    factorized_num_controls,
    infer_payoff_levels,
    payoff_distribution,
)
from tasks.trust.pomdp_matrices import (
    build_initial_beliefs,
    build_payoff_index_table,
    build_policies,
    build_preference_vectors,
    build_task_likelihoods,
    build_transition_matrices,
)
from tasks.trust.stance import (
    STANCE_ORDER,
    cooperation_evidence_strength,
    interpolate_stance_transition,
)
from tasks.trust.types import PARTNER_TYPE_ORDER, PartnerType, default_partner_type_params

_BINARY_KEYS = {"mutual_coop", "sucker", "temptation", "mutual_defect"}
_GRADED_KEYS = {"num_investment_levels", "endowment", "multiplier"}


@dataclass(frozen=True)
class TrustPomdpLabels:
    observation_modalities: tuple[str, ...]
    hidden_factors: tuple[str, ...]
    control_factors: tuple[str, ...]
    partner_types: tuple[str, ...]
    stances: tuple[str, ...]
    own_actions: tuple[str, ...]


@dataclass(frozen=True)
class TrustPomdpTemplate:
    A: list[jnp.ndarray]
    B: list[jnp.ndarray]
    C: list[jnp.ndarray]
    D: list[jnp.ndarray]
    E: jnp.ndarray
    policies: jnp.ndarray
    control_fac_idx: tuple[int, ...]
    labels: TrustPomdpLabels
    payoff_values: tuple[float, ...]
    num_obs: tuple[int, ...]
    num_states: tuple[int, ...]
    num_controls: tuple[int, ...]
    num_partners: int
    num_social_actions: int
    assignment_mode: str
    payoff_mode: str
    payoff_matrix: np.ndarray
    partner_action_prob_table: np.ndarray
    payoff_index_table: np.ndarray
    partner_types: tuple[PartnerType, ...]
    p_switch: float
    observation_noise: float
    preference_temperature: float

    @property
    def partner_type_names(self) -> tuple[str, ...]:
        return self.labels.partner_types

    @property
    def stance_names(self) -> tuple[str, ...]:
        return self.labels.stances

    @property
    def num_types(self) -> int:
        return int(self.num_states[0])

    @property
    def num_stances(self) -> int:
        return int(self.num_states[1])

    @property
    def payoff_levels(self) -> tuple[float, ...]:
        return self.payoff_values

    @property
    def uses_factorized_controls(self) -> bool:
        return len(self.num_controls) > 1

    def get_matrices(self) -> tuple[list[jnp.ndarray], list[jnp.ndarray], list[jnp.ndarray], list[jnp.ndarray]]:
        return self.A, self.B, self.C, self.D


def build_trust_pomdp_template(
    config: Any | Mapping[str, Any],
    *,
    planning_horizon: int,
    max_policies: int | None = None,
    rng: np.random.Generator | None = None,
) -> TrustPomdpTemplate:
    """Build static trust-task matrices and policy templates for ``pymdp.Agent``."""

    cfg = _config_dict(config)
    if "model_class" in cfg:
        raise ValueError("config key 'model_class' was removed. Use the native trust POMDP template.")
    if "variant" in cfg:
        raise ValueError("config key 'variant' was removed. use 'assignment_mode' instead.")
    if "payoff_mode" not in cfg:
        raise ValueError("config must specify payoff_mode={'binary','graded'}.")

    payoff_mode = str(cfg["payoff_mode"])
    num_partners = int(cfg.get("num_partners", 4))
    partner_type_names = tuple(cfg.get("partner_types", PARTNER_TYPE_ORDER))
    stance_names = tuple(cfg.get("stance_names", STANCE_ORDER))
    p_switch = float(cfg.get("p_switch", 0.05))
    assignment_mode = str(cfg.get("assignment_mode", "random"))
    observation_noise = float(cfg.get("observation_noise", 0.0))
    preference_temperature = float(cfg.get("preference_temperature", 1.0))
    partner_type_params = default_partner_type_params()
    partner_type_params.update(cfg.get("partner_type_params", {}))
    partner_types = tuple(
        PartnerType(type_name=name, params=partner_type_params.get(name, {})) for name in partner_type_names
    )

    if payoff_mode == "binary":
        if not is_dataclass(config):
            stray = _GRADED_KEYS & cfg.keys()
            if stray:
                raise ValueError(f"payoff_mode='binary' but graded-only keys present: {sorted(stray)}")
        num_social_actions = 2
        payoff_matrix = build_payoff_matrix(
            mutual_coop=tuple(cfg.get("mutual_coop", (3.0, 3.0))),
            sucker=tuple(cfg.get("sucker", (-1.0, 5.0))),
            temptation=tuple(cfg.get("temptation", (5.0, -1.0))),
            mutual_defect=tuple(cfg.get("mutual_defect", (1.0, 1.0))),
        )
        num_controls = tuple(factorized_num_controls(1, "random", num_social_actions))
        control_fac_idx = (1, 2)
    elif payoff_mode == "graded":
        if not is_dataclass(config):
            stray = _BINARY_KEYS & cfg.keys()
            if stray:
                raise ValueError(f"payoff_mode='graded' but binary-only keys present: {sorted(stray)}")
        num_social_actions = int(cfg.get("num_investment_levels", 6))
        payoff_matrix = build_graded_payoff_matrix(
            num_levels=num_social_actions,
            endowment=float(cfg.get("endowment", 10.0)),
            multiplier=float(cfg.get("multiplier", 3.0)),
        )
        num_controls = tuple(factorized_num_controls(1, "random", num_social_actions))
        control_fac_idx = (1, 2)
    else:
        raise ValueError(f"unknown payoff_mode={payoff_mode!r}, expected 'binary' or 'graded'")

    payoff_values = infer_payoff_levels(payoff_matrix)
    num_types = len(partner_type_names)
    num_stances = len(stance_names)
    num_states = (num_types, num_stances, num_social_actions)
    partner_action_prob_table = np.asarray(
        [
            [partner_type.get_action_probability(stance_name) for stance_name in stance_names]
            for partner_type in partner_types
        ],
        dtype=float,
    )
    payoff_index_table = build_payoff_index_table(
        payoff_matrix=payoff_matrix,
        payoff_values=payoff_values,
        num_social_actions=num_social_actions,
    )
    A_task = build_task_likelihoods(
        num_types=num_types,
        num_stances=num_stances,
        num_social_actions=num_social_actions,
        payoff_values=payoff_values,
        partner_action_prob_table=partner_action_prob_table,
        payoff_index_table=payoff_index_table,
        observation_noise=observation_noise,
    )
    B = build_transition_matrices(
        num_types=num_types,
        num_stances=num_stances,
        num_social_actions=num_social_actions,
        num_controls=num_controls,
        p_switch=p_switch,
    )
    C = build_preference_vectors(payoff_values=payoff_values, preference_temperature=preference_temperature)
    D = build_initial_beliefs(num_types=num_types, num_stances=num_stances, num_social_actions=num_social_actions)
    policies = build_policies(num_controls, planning_horizon=planning_horizon, max_policies=max_policies, rng=rng)
    E = jnp.full((policies.shape[0],), 1.0 / max(policies.shape[0], 1), dtype=float)

    labels = TrustPomdpLabels(
        observation_modalities=("partner_action", "payoff"),
        hidden_factors=("partner_type", "partner_stance", "own_action"),
        control_factors=("partner", "stance", "own_action") if len(num_controls) > 1 else ("social_action",),
        partner_types=partner_type_names,
        stances=stance_names,
        own_actions=tuple(f"action_{idx}" for idx in range(num_social_actions)),
    )
    return TrustPomdpTemplate(
        A=[
            jnp.asarray(np.repeat(A_task[0][..., None], num_social_actions, axis=-1)),
            jnp.asarray(np.transpose(A_task[1], (0, 2, 3, 1))),
        ],
        B=[jnp.asarray(B_f) for B_f in B],
        C=[jnp.asarray(C_m) for C_m in C],
        D=[jnp.asarray(D_f) for D_f in D],
        E=E,
        policies=jnp.asarray(policies),
        control_fac_idx=control_fac_idx,
        labels=labels,
        payoff_values=tuple(float(value) for value in payoff_values),
        num_obs=(2, len(payoff_values)),
        num_states=num_states,
        num_controls=tuple(int(value) for value in num_controls),
        num_partners=num_partners,
        num_social_actions=num_social_actions,
        assignment_mode=assignment_mode,
        payoff_mode=payoff_mode,
        payoff_matrix=np.asarray(payoff_matrix, dtype=float),
        partner_action_prob_table=np.asarray(partner_action_prob_table, dtype=float),
        payoff_index_table=payoff_index_table,
        partner_types=partner_types,
        p_switch=p_switch,
        observation_noise=observation_noise,
        preference_temperature=preference_temperature,
    )


def create_pymdp_agent(template: TrustPomdpTemplate, *, gamma: float):
    """Instantiate an official ``pymdp.Agent`` from a native trust template."""

    from pymdp.agent import Agent

    return Agent(
        A=template.A,
        B=template.B,
        C=template.C,
        D=template.D,
        E=template.E,
        policies=template.policies,
        control_fac_idx=list(template.control_fac_idx),
        gamma=gamma,
    )


def create_partner_agents(template: TrustPomdpTemplate, *, num_partners: int, gamma: float):
    return [create_pymdp_agent(template, gamma=gamma) for _ in range(int(num_partners))]


def as_joint_belief(template: TrustPomdpTemplate, belief: np.ndarray) -> np.ndarray:
    array = np.asarray(belief, dtype=float)
    if array.shape == (template.num_types, template.num_stances):
        joint = array
    elif array.size == template.num_types * template.num_stances:
        joint = array.reshape(template.num_types, template.num_stances)
    else:
        raise ValueError(
            f"Expected joint belief with shape {(template.num_types, template.num_stances)} or flat size "
            f"{template.num_types * template.num_stances}, got {array.shape}."
        )
    return joint / max(float(joint.sum()), 1e-16)


def partner_action_distribution(template: TrustPomdpTemplate, joint_belief: np.ndarray) -> np.ndarray:
    joint = as_joint_belief(template, joint_belief)
    p_coop = float(np.sum(joint * template.partner_action_prob_table))
    return np.asarray([p_coop, 1.0 - p_coop], dtype=float)


def joint_observation_likelihood(
    template: TrustPomdpTemplate,
    *,
    partner_action: int,
    payoff_obs: int,
    own_action: int,
) -> np.ndarray:
    action_likelihood = np.asarray(template.A[0][int(partner_action)], dtype=float)
    if action_likelihood.ndim > 2:
        action_likelihood = action_likelihood[..., int(own_action)]
    payoff_likelihood = np.asarray(template.A[1][int(payoff_obs)], dtype=float)[..., int(own_action)]
    return action_likelihood * payoff_likelihood


def observation_likelihood(
    template: TrustPomdpTemplate,
    observation: list[int],
    own_action: int | None,
) -> np.ndarray:
    if len(observation) < 2:
        raise ValueError(f"observation_likelihood requires both modalities; got {observation!r}.")
    if own_action is None:
        raise ValueError("observation_likelihood requires own_action to evaluate the payoff modality.")
    return joint_observation_likelihood(
        template,
        partner_action=int(observation[0]),
        payoff_obs=int(observation[1]),
        own_action=int(own_action),
    )


def infer_joint_posterior(
    template: TrustPomdpTemplate,
    joint_belief: np.ndarray,
    observation: list[int],
    own_action: int | None,
) -> np.ndarray:
    prior = as_joint_belief(template, joint_belief)
    likelihood = observation_likelihood(template, observation, own_action=own_action)
    posterior = prior * likelihood
    posterior /= max(float(posterior.sum()), 1e-16)
    return posterior


def type_transition(template: TrustPomdpTemplate) -> np.ndarray:
    return np.asarray(template.B[0][:, :, 0], dtype=float)


def stance_transition_for_executed_own_action(template: TrustPomdpTemplate, own_action: int) -> np.ndarray:
    evidence = cooperation_evidence_strength(int(own_action), num_social_actions=template.num_social_actions)
    return interpolate_stance_transition(evidence)


def predict_next_joint_belief(template: TrustPomdpTemplate, joint_belief: np.ndarray, own_action: int) -> np.ndarray:
    joint = as_joint_belief(template, joint_belief)
    predictive = type_transition(template) @ joint @ stance_transition_for_executed_own_action(
        template, int(own_action)
    ).T
    predictive /= max(float(predictive.sum()), 1e-16)
    return predictive


def predict_payoff_distribution(
    template: TrustPomdpTemplate,
    agent_action: int,
    partner_action_probs: np.ndarray,
) -> np.ndarray:
    return payoff_distribution(
        agent_action=agent_action,
        partner_action_probs=partner_action_probs,
        payoff_matrix=template.payoff_matrix,
        payoff_levels=template.payoff_values,
    )


def expected_payoff(template: TrustPomdpTemplate, agent_action: int, partner_action_probs: np.ndarray) -> float:
    return expected_agent_payoff(agent_action, partner_action_probs, template.payoff_matrix)


def _config_dict(config: Any | Mapping[str, Any]) -> dict[str, Any]:
    return asdict(config) if is_dataclass(config) else dict(config)


def stance_transition_for_action(template: TrustPomdpTemplate, action: int) -> np.ndarray:
    return np.asarray(template.B[1][:, :, int(action)], dtype=float)


def transition_for_action(template: TrustPomdpTemplate, action: int = 0) -> np.ndarray:
    del action
    return type_transition(template)


def flat_control_index(template: TrustPomdpTemplate, controls: tuple[int, ...]) -> int:
    return encode_instantaneous_index(controls, list(template.num_controls))


def controls_from_flat_index(template: TrustPomdpTemplate, index: int) -> tuple[int, ...]:
    return decode_instantaneous_index(index, list(template.num_controls))
