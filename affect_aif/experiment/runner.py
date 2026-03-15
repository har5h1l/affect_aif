"""Experiment runner and μ calibration."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.agent.base_agent import BaseAgent
from affect_aif.agent.lesioned_agent import LesionedAgent
from affect_aif.agent.reward_avg_agent import RewardAvgAgent
from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.conditions import get_condition_name
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.logger import MetricLogger
from affect_aif.generative_model.model import TrustGameModel


class ExperimentRunner:
    """Run all conditions, including a principled μ calibration phase."""

    MIN_FULL_RUN_CALIBRATION_EPISODES = 10

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.calibration_summary: dict | None = None

    def _create_model(self) -> TrustGameModel:
        return TrustGameModel(asdict(self.config))

    def _create_agent(self, condition: int, model: TrustGameModel, seed: int) -> BaseAgent:
        matrices = model.get_matrices()
        common = dict(
            A=matrices[0],
            B=matrices[1],
            C=matrices[2],
            D=matrices[3],
            model=model,
            gamma=self.config.gamma,
            lr=self.config.lr,
            action_sampling=self.config.action_sampling,
            max_policies=self.config.max_policies,
            reference_horizon=self.config.deep_horizon,
            seed=seed,
            affect_modulates_precision=self.config.affect_modulates_precision,
            use_parameter_learning=self.config.use_parameter_learning,
        )
        if condition == 1:
            return BaseAgent(planning_horizon=self.config.deep_horizon, **common)
        if condition == 2:
            return AffectiveAgent(
                planning_horizon=self.config.shallow_horizon,
                num_partners=self.config.num_partners,
                lambda_smooth=self.config.lambda_smooth,
                alpha_charge=self.config.alpha_charge,
                sigma_0_sq=self.config.sigma_0_sq,
                initial_beta=self.config.initial_beta,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        if condition == 3:
            return LesionedAgent(
                planning_horizon=self.config.shallow_horizon,
                num_partners=self.config.num_partners,
                lambda_smooth=self.config.lambda_smooth,
                alpha_charge=self.config.alpha_charge,
                sigma_0_sq=self.config.sigma_0_sq,
                initial_beta=self.config.initial_beta,
                lesion_mode=self.config.lesion_mode,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        if condition == 4:
            return BaseAgent(planning_horizon=self.config.shallow_horizon, **common)
        if condition == 5:
            return RewardAvgAgent(
                planning_horizon=self.config.shallow_horizon,
                num_partners=self.config.num_partners,
                lambda_smooth=self.config.lambda_smooth,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        raise ValueError(f"Unknown condition '{condition}'.")

    def _resolve_calibration_episodes(self, enforce_minimum: bool) -> int:
        requested = int(self.config.calibration_episodes)
        if enforce_minimum:
            return max(requested, self.MIN_FULL_RUN_CALIBRATION_EPISODES)
        return requested

    def calibrate_mu(self, enforce_minimum: bool = False) -> float:
        """Derive μ from deep-planner EFE mass instead of tuning it."""

        if self.config.deep_horizon <= self.config.shallow_horizon:
            self.config.mu = 0.0
            self.calibration_summary = {
                "requested_calibration_episodes": int(self.config.calibration_episodes),
                "calibration_episodes": 0,
                "mean_abs_efe_per_step": 0.0,
                "derived_mu": 0.0,
            }
            return 0.0

        calibration_episodes = self._resolve_calibration_episodes(enforce_minimum=enforce_minimum)
        efe_values = []
        for offset in range(calibration_episodes):
            seed = self.config.random_seed + 10_000 + offset
            model = self._create_model()
            env = TrustGameEnv(self.config, seed=seed)
            agent = self._create_agent(condition=1, model=model, seed=seed)
            for record in self._run_episode(agent=agent, env=env, seed=seed, condition=1):
                efe_values.append(record["mean_abs_step_efe"])

        mean_abs_efe = float(np.nanmean(np.asarray(efe_values, dtype=float))) if efe_values else 0.0
        derived_mu = float(mean_abs_efe * (self.config.deep_horizon - self.config.shallow_horizon))
        self.config.mu = derived_mu
        self.calibration_summary = {
            "requested_calibration_episodes": int(self.config.calibration_episodes),
            "calibration_episodes": calibration_episodes,
            "mean_abs_efe_per_step": mean_abs_efe,
            "derived_mu": derived_mu,
        }
        return derived_mu

    def _run_episode(self, agent: BaseAgent, env: TrustGameEnv, seed: int, condition: int) -> list[dict]:
        logger = MetricLogger(num_rounds=self.config.num_rounds, num_partners=self.config.num_partners)
        context = env.reset()

        for round_idx in range(self.config.num_rounds):
            action = agent.plan_and_act(active_partner=context["active_partner"])
            result = env.step(action)
            agent.observe_outcome(
                partner_idx=result["partner_idx"],
                observation=result["observation"],
                action_taken=result["agent_action"],
                partner_action=result["partner_action"],
                payoff=result["agent_payoff"],
                true_partner_type=result["true_partner_type"],
            )
            partner_belief = agent.get_partner_type_belief(result["partner_idx"])
            inferred_type_idx = int(np.argmax(partner_belief))
            inferred_type = agent.model.partner_type_names[inferred_type_idx]
            inferred_correct = inferred_type == result["true_partner_type"]

            agent_metrics = agent.get_metrics()
            agent_metrics["inferred_type"] = inferred_type
            agent_metrics["inferred_type_correct"] = inferred_correct
            logger.log_round(
                round_idx=round_idx,
                condition=condition,
                seed=seed,
                agent_metrics=agent_metrics,
                env_result=result,
            )
            context = {"active_partner": result["active_partner"]}

        return logger.records

    def run_all(self) -> pd.DataFrame:
        """Run all configured conditions across all seeds."""

        if any(condition in {2, 3, 4, 5} for condition in self.config.conditions):
            self.calibrate_mu(enforce_minimum=True)

        records: list[dict] = []
        for condition in self.config.conditions:
            for replication in range(self.config.num_replications):
                seed = self.config.random_seed + replication
                model = self._create_model()
                env = TrustGameEnv(self.config, seed=seed)
                agent = self._create_agent(condition=condition, model=model, seed=seed)
                for row in self._run_episode(agent=agent, env=env, seed=seed, condition=condition):
                    row["condition_name"] = get_condition_name(condition)
                    if self.calibration_summary is not None:
                        row["mu_source"] = "derived"
                        row["calibration_mean_abs_efe_per_step"] = self.calibration_summary["mean_abs_efe_per_step"]
                        row["derived_mu"] = self.calibration_summary["derived_mu"]
                    else:
                        row["mu_source"] = "not_required"
                        row["calibration_mean_abs_efe_per_step"] = np.nan
                        row["derived_mu"] = np.nan
                    row["run_mode"] = "primary"
                    records.append(row)
        if self.config.run_sensitivity and self.calibration_summary is not None:
            records.extend(self.run_parameter_sensitivity().to_dict(orient="records"))
        return pd.DataFrame(records)

    def save_results(self, results: pd.DataFrame, path: str):
        """Persist results to CSV or parquet."""

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".parquet":
            results.to_parquet(target, index=False)
            return
        results.to_csv(target, index=False)

    def run_mu_sensitivity(self) -> pd.DataFrame:
        """Backward-compatible wrapper around the full parameter sensitivity sweep."""

        return self.run_parameter_sensitivity()

    def run_parameter_sensitivity(self) -> pd.DataFrame:
        """Run one-at-a-time sensitivity sweeps for μ and affective state hyperparameters."""

        if self.calibration_summary is None:
            self.calibrate_mu(enforce_minimum=True)
        base_mu = float(self.calibration_summary["derived_mu"])
        original_mu = self.config.mu
        original_lambda = self.config.lambda_smooth
        original_alpha = self.config.alpha_charge
        original_sigma = self.config.sigma_0_sq
        original_conditions = list(self.config.conditions)
        sensitivity_conditions = [condition for condition in original_conditions if condition in {2, 3, 5}]
        if not sensitivity_conditions:
            return pd.DataFrame()

        records: list[dict] = []
        sweep_specs = []
        for factor in self.config.sensitivity_factors["mu"]:
            sweep_specs.append(("mu", float(factor)))
        for value in self.config.sensitivity_factors["lambda_smooth"]:
            sweep_specs.append(("lambda_smooth", float(value)))
        for value in self.config.sensitivity_factors["alpha_charge"]:
            sweep_specs.append(("alpha_charge", float(value)))
        for value in self.config.sensitivity_factors["sigma_0_sq"]:
            sweep_specs.append(("sigma_0_sq", float(value)))

        for parameter_name, parameter_value in sweep_specs:
            self.config.mu = base_mu
            self.config.lambda_smooth = original_lambda
            self.config.alpha_charge = original_alpha
            self.config.sigma_0_sq = original_sigma
            mu_factor = np.nan
            if parameter_name == "mu":
                mu_factor = float(parameter_value)
                self.config.mu = base_mu * float(parameter_value)
            elif parameter_name == "lambda_smooth":
                self.config.lambda_smooth = float(parameter_value)
            elif parameter_name == "alpha_charge":
                self.config.alpha_charge = float(parameter_value)
            elif parameter_name == "sigma_0_sq":
                self.config.sigma_0_sq = float(parameter_value)
            self.config.conditions = sensitivity_conditions
            for condition in sensitivity_conditions:
                for replication in range(self.config.num_replications):
                    seed = self.config.random_seed + replication
                    model = self._create_model()
                    env = TrustGameEnv(self.config, seed=seed)
                    agent = self._create_agent(condition=condition, model=model, seed=seed)
                    for row in self._run_episode(agent=agent, env=env, seed=seed, condition=condition):
                        row["condition_name"] = get_condition_name(condition)
                        row["mu_source"] = "sensitivity"
                        row["calibration_mean_abs_efe_per_step"] = self.calibration_summary["mean_abs_efe_per_step"]
                        row["derived_mu"] = base_mu
                        row["mu_factor"] = mu_factor
                        row["sensitivity_parameter"] = parameter_name
                        row["sensitivity_value"] = float(self.config.mu if parameter_name == "mu" else parameter_value)
                        row["sensitivity_lambda_smooth"] = float(self.config.lambda_smooth)
                        row["sensitivity_alpha_charge"] = float(self.config.alpha_charge)
                        row["sensitivity_sigma_0_sq"] = float(self.config.sigma_0_sq)
                        row["run_mode"] = "sensitivity"
                        records.append(row)
        self.config.mu = original_mu
        self.config.lambda_smooth = original_lambda
        self.config.alpha_charge = original_alpha
        self.config.sigma_0_sq = original_sigma
        self.config.conditions = original_conditions
        return pd.DataFrame(records)
