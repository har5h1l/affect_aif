"""Factories for models, environments, and agents."""

from __future__ import annotations

from dataclasses import asdict

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.agent.base_agent import BaseAgent
from affect_aif.agent.lesioned_agent import LesionedAgent
from affect_aif.agent.reward_avg_agent import RewardAvgAgent
from affect_aif.environment.graded_trust_game import GradedTrustGameEnv
from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.conditions import resolve_condition_spec
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.generative_model.model import GradedTrustGameModel, TrustGameModel


def create_model(config: ExperimentConfig) -> TrustGameModel:
    if config.payoff_mode == "graded":
        return GradedTrustGameModel(asdict(config))
    return TrustGameModel(asdict(config))


def create_env(config: ExperimentConfig, seed: int) -> TrustGameEnv:
    if config.payoff_mode == "graded":
        return GradedTrustGameEnv(config, seed=seed)
    return TrustGameEnv(config, seed=seed)


def _planning_horizon_for_condition(config: ExperimentConfig, condition: int | str, default_horizon: int) -> int:
    candidates: list[int | str] = [condition]
    if isinstance(condition, str) and condition.strip().isdigit():
        candidates.append(int(condition))
    elif not isinstance(condition, str):
        candidates.append(str(condition))
        candidates.append(resolve_condition_spec(condition).name)
    else:
        candidates.append(resolve_condition_spec(condition).name)

    for key in candidates:
        if key in config.horizon_overrides:
            return int(config.horizon_overrides[key])
    return int(default_horizon)


def create_agent(config: ExperimentConfig, condition: int | str, model: TrustGameModel, seed: int) -> BaseAgent:
    spec = resolve_condition_spec(condition)
    matrices = model.get_matrices()
    planning_horizon = _planning_horizon_for_condition(config, condition, spec.planning_horizon)
    common = dict(
        A=matrices[0],
        B=matrices[1],
        C=matrices[2],
        D=matrices[3],
        model=model,
        gamma=config.gamma,
        lr=config.lr,
        action_sampling=config.action_sampling,
        max_policies=config.max_policies,
        reference_horizon=config.deep_horizon,
        seed=seed,
        affect_modulates_precision=config.affect_modulates_precision,
        use_parameter_learning=config.use_parameter_learning,
        use_information_gain=spec.use_information_gain,
    )
    params = {
        "lambda_smooth": config.lambda_smooth,
        "alpha_charge": config.alpha_charge,
        "sigma_0_sq": config.sigma_0_sq,
        "initial_beta": config.initial_beta,
    }
    params.update(spec.parameter_overrides)

    if spec.agent_kind == "base":
        return BaseAgent(planning_horizon=planning_horizon, **common)
    if spec.agent_kind == "reward_average":
        return RewardAvgAgent(
            planning_horizon=planning_horizon,
            num_partners=config.num_partners,
            lambda_smooth=params["lambda_smooth"],
            mu=float(config.mu or 0.0),
            **common,
        )
    if spec.agent_kind == "lesioned":
        return LesionedAgent(
            planning_horizon=planning_horizon,
            num_partners=config.num_partners,
            lambda_smooth=params["lambda_smooth"],
            alpha_charge=params["alpha_charge"],
            sigma_0_sq=params["sigma_0_sq"],
            initial_beta=params["initial_beta"],
            lesion_mode=spec.lesion_mode or config.lesion_mode,
            mu=float(config.mu or 0.0),
            **common,
        )
    if spec.agent_kind == "affective":
        return AffectiveAgent(
            planning_horizon=planning_horizon,
            num_partners=config.num_partners,
            lambda_smooth=params["lambda_smooth"],
            alpha_charge=params["alpha_charge"],
            sigma_0_sq=params["sigma_0_sq"],
            initial_beta=params["initial_beta"],
            beta_mode=spec.beta_mode or config.beta_mode,
            num_levels=config.beta_num_levels,
            persistence=config.beta_persistence,
            mu=float(config.mu or 0.0),
            **common,
        )
    raise ValueError(f"Unknown agent kind '{spec.agent_kind}'.")
