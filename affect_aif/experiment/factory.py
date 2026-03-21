"""Factories for models, environments, and agents."""

from __future__ import annotations

from dataclasses import asdict

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.agent.base_agent import BaseAgent
from affect_aif.agent.lesioned_agent import LesionedAgent
from affect_aif.agent.reward_avg_agent import RewardAvgAgent
from affect_aif.environment.graded_trust_game import GradedTrustGameEnv
from affect_aif.environment.trust_game import TrustGameEnv
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


def planning_horizon_for(config: ExperimentConfig, condition: int, default_horizon: int) -> int:
    return int(config.horizon_overrides.get(int(condition), default_horizon))


def create_agent(config: ExperimentConfig, condition: int, model: TrustGameModel, seed: int) -> BaseAgent:
    matrices = model.get_matrices()
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
    )

    if condition == 1:
        return BaseAgent(planning_horizon=planning_horizon_for(config, condition, config.deep_horizon), **common)
    if condition == 3:
        return LesionedAgent(
            planning_horizon=planning_horizon_for(config, condition, config.shallow_horizon),
            num_partners=config.num_partners,
            lambda_smooth=config.lambda_smooth,
            alpha_charge=config.alpha_charge,
            sigma_0_sq=config.sigma_0_sq,
            initial_beta=config.initial_beta,
            lesion_mode=config.lesion_mode,
            mu=float(config.mu or 0.0),
            **common,
        )
    if condition == 4:
        return BaseAgent(planning_horizon=planning_horizon_for(config, condition, config.shallow_horizon), **common)
    if condition == 5:
        return RewardAvgAgent(
            planning_horizon=planning_horizon_for(config, condition, config.shallow_horizon),
            num_partners=config.num_partners,
            lambda_smooth=config.lambda_smooth,
            mu=float(config.mu or 0.0),
            **common,
        )
    if condition == 6:
        return BaseAgent(planning_horizon=planning_horizon_for(config, condition, 3), **common)
    if condition == 7:
        return BaseAgent(planning_horizon=planning_horizon_for(config, condition, 4), **common)
    if condition in {2, 8, 9, 10, 11, 12}:
        default_horizon = config.deep_horizon if condition == 8 else config.shallow_horizon
        beta_mode = "variational" if condition == 12 else config.beta_mode
        return AffectiveAgent(
            planning_horizon=planning_horizon_for(config, condition, default_horizon),
            num_partners=config.num_partners,
            lambda_smooth=config.lambda_smooth,
            alpha_charge=config.alpha_charge,
            sigma_0_sq=config.sigma_0_sq,
            initial_beta=config.initial_beta,
            beta_mode=beta_mode,
            num_levels=config.beta_num_levels,
            persistence=config.beta_persistence,
            mu=float(config.mu or 0.0),
            **common,
        )
    raise ValueError(f"Unknown condition '{condition}'.")
