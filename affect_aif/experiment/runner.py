"""Experiment runner and process-safe task helpers."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.agent.base_agent import BaseAgent
from affect_aif.agent.lesioned_agent import LesionedAgent
from affect_aif.agent.discrete_affective_agent import DiscreteAffectiveAgent
from affect_aif.agent.reward_avg_agent import RewardAvgAgent
from affect_aif.environment.graded_trust_game import GradedTrustGameEnv
from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.conditions import get_condition_name
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.logger import MetricLogger
from affect_aif.experiment.progress import ProgressReporter, create_progress_reporter
from affect_aif.generative_model.model import GradedTrustGameModel, TrustGameModel


PRIMARY_CONDITIONS_REQUIRING_MU = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
SENSITIVITY_CONDITIONS = {2, 3, 5, 8}


def _build_calibration_summary(config: ExperimentConfig, efe_values: list[float], calibration_episodes: int) -> dict[str, float | int]:
    mean_abs_efe = float(np.nanmean(np.asarray(efe_values, dtype=float))) if efe_values else 0.0
    horizon_gap = max(1, config.deep_horizon - config.shallow_horizon)
    derived_mu = float(mean_abs_efe * horizon_gap)
    return {
        "requested_calibration_episodes": int(config.calibration_episodes),
        "calibration_episodes": int(calibration_episodes),
        "mean_abs_efe_per_step": mean_abs_efe,
        "derived_mu": derived_mu,
    }


def _serialize_config(config: ExperimentConfig) -> dict[str, Any]:
    return asdict(config)


def _deserialize_config(payload: dict[str, Any]) -> ExperimentConfig:
    return ExperimentConfig.from_dict(payload)


class ExperimentRunner:
    """Run all conditions, including a principled μ calibration phase."""

    MIN_FULL_RUN_CALIBRATION_EPISODES = 10

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.calibration_summary: dict | None = None
        self.progress: ProgressReporter = create_progress_reporter(
            enabled=self.config.verbose,
            mode=self.config.verbosity_mode,
            include_calibration=self.config.verbosity_include_calibration,
        )

    def _create_model(self) -> TrustGameModel:
        if self.config.payoff_mode == "graded":
            return GradedTrustGameModel(asdict(self.config))
        return TrustGameModel(asdict(self.config))

    def _create_env(self, seed: int) -> TrustGameEnv:
        if self.config.payoff_mode == "graded":
            return GradedTrustGameEnv(self.config, seed=seed)
        return TrustGameEnv(self.config, seed=seed)

    def _planning_horizon_for(self, condition: int, default_horizon: int) -> int:
        return int(self.config.horizon_overrides.get(int(condition), default_horizon))

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
            return BaseAgent(planning_horizon=self._planning_horizon_for(condition, self.config.deep_horizon), **common)
        if condition == 2:
            return AffectiveAgent(
                planning_horizon=self._planning_horizon_for(condition, self.config.shallow_horizon),
                num_partners=self.config.num_partners,
                lambda_smooth=self.config.lambda_smooth,
                alpha_charge=self.config.alpha_charge,
                sigma_0_sq=self.config.sigma_0_sq,
                initial_beta=self.config.initial_beta,
                beta_mode=self.config.beta_mode,
                num_levels=self.config.beta_num_levels,
                persistence=self.config.beta_persistence,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        if condition == 3:
            return LesionedAgent(
                planning_horizon=self._planning_horizon_for(condition, self.config.shallow_horizon),
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
            return BaseAgent(planning_horizon=self._planning_horizon_for(condition, self.config.shallow_horizon), **common)
        if condition == 5:
            return RewardAvgAgent(
                planning_horizon=self._planning_horizon_for(condition, self.config.shallow_horizon),
                num_partners=self.config.num_partners,
                lambda_smooth=self.config.lambda_smooth,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        if condition == 6:
            return BaseAgent(planning_horizon=self._planning_horizon_for(condition, 3), **common)
        if condition == 7:
            return BaseAgent(planning_horizon=self._planning_horizon_for(condition, 4), **common)
        if condition == 8:
            return AffectiveAgent(
                planning_horizon=self._planning_horizon_for(condition, self.config.deep_horizon),
                num_partners=self.config.num_partners,
                lambda_smooth=self.config.lambda_smooth,
                alpha_charge=self.config.alpha_charge,
                sigma_0_sq=self.config.sigma_0_sq,
                initial_beta=self.config.initial_beta,
                beta_mode=self.config.beta_mode,
                num_levels=self.config.beta_num_levels,
                persistence=self.config.beta_persistence,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        if condition in (9, 10, 11):
            return AffectiveAgent(
                planning_horizon=self._planning_horizon_for(condition, self.config.shallow_horizon),
                num_partners=self.config.num_partners,
                lambda_smooth=self.config.lambda_smooth,
                alpha_charge=self.config.alpha_charge,
                sigma_0_sq=self.config.sigma_0_sq,
                initial_beta=self.config.initial_beta,
                beta_mode=self.config.beta_mode,
                num_levels=self.config.beta_num_levels,
                persistence=self.config.beta_persistence,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        if condition == 12:
            return DiscreteAffectiveAgent(
                planning_horizon=self._planning_horizon_for(condition, self.config.shallow_horizon),
                num_partners=self.config.num_partners,
                num_beta_levels=self.config.num_beta_levels,
                beta_persistence=self.config.beta_persistence,
                sigma_0_sq=self.config.sigma_0_sq,
                initial_beta=self.config.initial_beta,
                mu=float(self.config.mu or 0.0),
                **common,
            )
        raise ValueError(f"Unknown condition '{condition}'.")

    def _resolve_calibration_episodes(self, enforce_minimum: bool) -> int:
        requested = int(self.config.calibration_episodes)
        if enforce_minimum:
            return max(requested, self.MIN_FULL_RUN_CALIBRATION_EPISODES)
        return requested

    def needs_mu_calibration(self) -> bool:
        return any(condition in PRIMARY_CONDITIONS_REQUIRING_MU for condition in self.config.conditions)

    def build_zero_calibration_summary(self) -> dict[str, float | int]:
        return {
            "requested_calibration_episodes": int(self.config.calibration_episodes),
            "calibration_episodes": 0,
            "mean_abs_efe_per_step": 0.0,
            "derived_mu": 0.0,
        }

    def _annotate_primary_records(
        self,
        rows: list[dict],
        *,
        condition: int,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict]:
        for row in rows:
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
            row["config_path"] = config_path or np.nan
            row["config_name"] = config_name or self.config.experiment_name
            row["batch_id"] = batch_id or np.nan
        return rows

    def _run_episode(
        self,
        agent: BaseAgent,
        env: TrustGameEnv,
        seed: int,
        condition: int,
        replication: int = 0,
    ) -> list[dict]:
        logger = MetricLogger(num_rounds=self.config.num_rounds, num_partners=self.config.num_partners)
        context = env.reset()

        for round_idx in range(self.config.num_rounds):
            active_partner = context["active_partner"]
            self.progress.emit(
                "round_start",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                active_partner=active_partner,
            )
            self.progress.emit(
                "planning_start",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                active_partner=active_partner,
            )
            action = agent.plan_and_act(active_partner=active_partner)
            planning_metrics = agent.get_metrics()
            self.progress.emit(
                "planning_end",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                selected_partner=planning_metrics["selected_partner"],
                selected_action=planning_metrics["selected_action"],
                raw_action=planning_metrics["raw_action"],
                best_policy_idx=planning_metrics["best_policy_idx"],
            )
            self.progress.emit(
                "environment_step_start",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                raw_action=action,
            )
            result = env.step(action)
            result["active_partner_start"] = active_partner
            self.progress.emit(
                "environment_step_end",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                partner_idx=result["partner_idx"],
                agent_action=result["agent_action"],
                partner_action=result["partner_action"],
                payoff=result["agent_payoff"],
                switch_kind=result.get("switch_kind", "none"),
            )
            self.progress.emit(
                "belief_update_start",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                partner_idx=result["partner_idx"],
            )
            predictive_log_lik = agent.get_predictive_log_likelihood(result["partner_action"])
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
            self.progress.emit(
                "belief_update_end",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                partner_idx=result["partner_idx"],
                inferred_type=inferred_type,
                inferred_type_correct=inferred_correct,
            )

            agent_metrics = agent.get_metrics()
            agent_metrics["inferred_type"] = inferred_type
            agent_metrics["inferred_type_correct"] = inferred_correct
            agent_metrics["predictive_log_lik"] = predictive_log_lik
            logger.log_round(
                round_idx=round_idx,
                condition=condition,
                seed=seed,
                agent_metrics=agent_metrics,
                env_result=result,
            )
            self.progress.emit(
                "metric_logging_end",
                condition=condition,
                replication=replication,
                round_idx=round_idx,
                round_count=self.config.num_rounds,
                payoff=result["agent_payoff"],
                inferred_type=inferred_type,
                q_pi_entropy=agent_metrics["q_pi_entropy"],
            )
            context = {"active_partner": result["active_partner"]}

        return logger.records

    def run_calibration_episode(self, episode_idx: int, seed: int) -> dict[str, float | int]:
        self.progress.emit(
            "calibration_episode_start",
            episode_idx=episode_idx,
            episode_count=self._resolve_calibration_episodes(enforce_minimum=False),
            seed=seed,
        )
        model = self._create_model()
        env = self._create_env(seed=seed)
        agent = self._create_agent(condition=1, model=model, seed=seed)
        calibration_records = self._run_episode(agent=agent, env=env, seed=seed, condition=1, replication=episode_idx)
        mean_abs_step_efe = float(np.nanmean([row["mean_abs_step_efe"] for row in calibration_records])) if calibration_records else 0.0
        self.progress.emit(
            "calibration_episode_end",
            episode_idx=episode_idx,
            episode_count=self._resolve_calibration_episodes(enforce_minimum=False),
            seed=seed,
            mean_abs_step_efe=mean_abs_step_efe,
        )
        return {
            "episode_idx": int(episode_idx),
            "seed": int(seed),
            "mean_abs_step_efe": mean_abs_step_efe,
        }

    def calibrate_mu(self, enforce_minimum: bool = False) -> float:
        """Derive μ from deep-planner EFE mass instead of tuning it."""

        calibration_episodes = self._resolve_calibration_episodes(enforce_minimum=enforce_minimum)
        efe_values: list[float] = []
        for offset in range(calibration_episodes):
            seed = self.config.random_seed + 10_000 + offset
            episode_summary = self.run_calibration_episode(episode_idx=offset, seed=seed)
            efe_values.append(float(episode_summary["mean_abs_step_efe"]))

        self.calibration_summary = _build_calibration_summary(self.config, efe_values, calibration_episodes)
        self.config.mu = float(self.calibration_summary["derived_mu"])
        return float(self.calibration_summary["derived_mu"])

    def run_replication(
        self,
        *,
        condition: int,
        replication: int,
        seed: int,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict]:
        self.progress.emit(
            "replication_start",
            condition=condition,
            replication=replication,
            seed=seed,
        )
        model = self._create_model()
        env = self._create_env(seed=seed)
        agent = self._create_agent(condition=condition, model=model, seed=seed)
        episode_records = self._run_episode(
            agent=agent,
            env=env,
            seed=seed,
            condition=condition,
            replication=replication,
        )
        self._annotate_primary_records(
            episode_records,
            condition=condition,
            config_path=config_path,
            config_name=config_name,
            batch_id=batch_id,
        )
        self.progress.emit(
            "replication_end",
            condition=condition,
            replication=replication,
            seed=seed,
            cumulative_payoff=sum(float(row["payoff"]) for row in episode_records),
        )
        return episode_records

    def run_all(
        self,
        *,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
        checkpoint_path: str | None = None,
        checkpoint_interval: int = 1,
    ) -> pd.DataFrame:
        """Run all configured conditions across all seeds.

        Args:
            checkpoint_path: If set, save partial results to this path after
                every ``checkpoint_interval`` replications per condition.
            checkpoint_interval: Number of replications between checkpoint
                saves. Defaults to 1 (save after every replication).
        """

        if self.needs_mu_calibration():
            self.calibrate_mu(enforce_minimum=True)

        records: list[dict] = []
        total_replications_done = 0
        for condition in self.config.conditions:
            self.progress.emit(
                "condition_start",
                condition=condition,
                replication=0,
                condition_name=get_condition_name(condition),
            )
            for replication in range(self.config.num_replications):
                seed = self.config.random_seed + replication
                records.extend(
                    self.run_replication(
                        condition=condition,
                        replication=replication,
                        seed=seed,
                        config_path=config_path,
                        config_name=config_name,
                        batch_id=batch_id,
                    )
                )
                total_replications_done += 1
                if checkpoint_path and total_replications_done % checkpoint_interval == 0:
                    self.save_results(pd.DataFrame(records), checkpoint_path)
            self.progress.emit(
                "condition_end",
                condition=condition,
                replication=self.config.num_replications - 1,
                rows=len([row for row in records if row["condition"] == condition and row["run_mode"] == "primary"]),
            )
        if self.config.run_sensitivity and self.calibration_summary is not None:
            records.extend(
                self.run_parameter_sensitivity(
                    config_path=config_path,
                    config_name=config_name,
                    batch_id=batch_id,
                ).to_dict(orient="records")
            )
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

    def _sensitivity_specs(self) -> list[tuple[str, float]]:
        sweep_specs = []
        for factor in self.config.sensitivity_factors["mu"]:
            sweep_specs.append(("mu", float(factor)))
        for value in self.config.sensitivity_factors["lambda_smooth"]:
            sweep_specs.append(("lambda_smooth", float(value)))
        for value in self.config.sensitivity_factors["alpha_charge"]:
            sweep_specs.append(("alpha_charge", float(value)))
        for value in self.config.sensitivity_factors["sigma_0_sq"]:
            sweep_specs.append(("sigma_0_sq", float(value)))
        return sweep_specs

    def _apply_sensitivity_override(self, parameter_name: str, parameter_value: float, base_mu: float):
        self.config.mu = base_mu
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
        return mu_factor

    def run_sensitivity_replication(
        self,
        *,
        parameter_name: str,
        parameter_value: float,
        condition: int,
        replication: int,
        seed: int,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict]:
        if self.calibration_summary is None:
            self.calibrate_mu(enforce_minimum=True)
        base_mu = float(self.calibration_summary["derived_mu"])
        original_mu = self.config.mu
        original_lambda = self.config.lambda_smooth
        original_alpha = self.config.alpha_charge
        original_sigma = self.config.sigma_0_sq
        try:
            mu_factor = self._apply_sensitivity_override(parameter_name, float(parameter_value), base_mu)
            model = self._create_model()
            env = self._create_env(seed=seed)
            agent = self._create_agent(condition=condition, model=model, seed=seed)
            rows = self._run_episode(agent=agent, env=env, seed=seed, condition=condition, replication=replication)
            for row in rows:
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
                row["config_path"] = config_path or np.nan
                row["config_name"] = config_name or self.config.experiment_name
                row["batch_id"] = batch_id or np.nan
            return rows
        finally:
            self.config.mu = original_mu
            self.config.lambda_smooth = original_lambda
            self.config.alpha_charge = original_alpha
            self.config.sigma_0_sq = original_sigma

    def run_parameter_sensitivity(
        self,
        *,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> pd.DataFrame:
        """Run one-at-a-time sensitivity sweeps for μ and affective state hyperparameters."""

        if self.calibration_summary is None:
            self.calibrate_mu(enforce_minimum=True)
        original_conditions = list(self.config.conditions)
        sensitivity_conditions = [condition for condition in original_conditions if condition in SENSITIVITY_CONDITIONS]
        if not sensitivity_conditions:
            return pd.DataFrame()

        records: list[dict] = []
        for parameter_name, parameter_value in self._sensitivity_specs():
            for condition in sensitivity_conditions:
                for replication in range(self.config.num_replications):
                    seed = self.config.random_seed + replication
                    records.extend(
                        self.run_sensitivity_replication(
                            parameter_name=parameter_name,
                            parameter_value=parameter_value,
                            condition=condition,
                            replication=replication,
                            seed=seed,
                            config_path=config_path,
                            config_name=config_name,
                            batch_id=batch_id,
                        )
                    )
        self.config.conditions = original_conditions
        return pd.DataFrame(records)


def run_calibration_episode_task(config_payload: dict[str, Any], episode_idx: int, seed: int) -> dict[str, float | int]:
    config = _deserialize_config(config_payload)
    config.verbose = False
    runner = ExperimentRunner(config)
    return runner.run_calibration_episode(episode_idx=episode_idx, seed=seed)


def run_primary_replication_task(
    config_payload: dict[str, Any],
    *,
    condition: int,
    replication: int,
    seed: int,
    calibration_summary: dict[str, Any] | None,
    config_path: str,
    config_name: str,
    batch_id: str,
) -> dict[str, Any]:
    config = _deserialize_config(config_payload)
    config.verbose = False
    if calibration_summary is not None:
        config.mu = float(calibration_summary["derived_mu"])
    runner = ExperimentRunner(config)
    runner.calibration_summary = calibration_summary
    rows = runner.run_replication(
        condition=condition,
        replication=replication,
        seed=seed,
        config_path=config_path,
        config_name=config_name,
        batch_id=batch_id,
    )
    return {
        "task_kind": "primary",
        "condition": int(condition),
        "replication": int(replication),
        "seed": int(seed),
        "records": rows,
        "cumulative_payoff": float(sum(float(row["payoff"]) for row in rows)),
    }


def run_sensitivity_replication_task(
    config_payload: dict[str, Any],
    *,
    parameter_name: str,
    parameter_value: float,
    condition: int,
    replication: int,
    seed: int,
    calibration_summary: dict[str, Any],
    config_path: str,
    config_name: str,
    batch_id: str,
) -> dict[str, Any]:
    config = _deserialize_config(config_payload)
    config.verbose = False
    config.mu = float(calibration_summary["derived_mu"])
    runner = ExperimentRunner(config)
    runner.calibration_summary = calibration_summary
    rows = runner.run_sensitivity_replication(
        parameter_name=parameter_name,
        parameter_value=parameter_value,
        condition=condition,
        replication=replication,
        seed=seed,
        config_path=config_path,
        config_name=config_name,
        batch_id=batch_id,
    )
    return {
        "task_kind": "sensitivity",
        "condition": int(condition),
        "replication": int(replication),
        "seed": int(seed),
        "parameter_name": parameter_name,
        "parameter_value": float(parameter_value),
        "records": rows,
    }


__all__ = [
    "ExperimentRunner",
    "PRIMARY_CONDITIONS_REQUIRING_MU",
    "SENSITIVITY_CONDITIONS",
    "run_calibration_episode_task",
    "run_primary_replication_task",
    "run_sensitivity_replication_task",
    "_build_calibration_summary",
    "_serialize_config",
]
