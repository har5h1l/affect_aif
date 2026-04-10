"""Experiment runner and process-safe task helpers."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from agent.base import BaseAgent
from env.trust_game import TrustGameEnv
from experiment.conditions import get_condition_name, resolve_condition_spec
from experiment.calibration import (
    MIN_FULL_RUN_CALIBRATION_EPISODES as CALIBRATION_MIN_FULL_RUN_EPISODES,
    build_calibration_summary,
    build_sensitivity_specs,
    build_zero_calibration_summary,
    deserialize_config,
    resolve_calibration_episodes,
)
from experiment.config import ExperimentConfig
from experiment.factory import create_agent, create_env, create_model
from experiment.logger import MetricLogger
from experiment.progress import ProgressReporter, create_progress_reporter
from agent.model.trust_game import TrustGameModel

from experiment.constants import SENSITIVITY_CONDITIONS


class ExperimentRunner:
    """Run all conditions, including a principled μ calibration phase."""

    MIN_FULL_RUN_CALIBRATION_EPISODES = CALIBRATION_MIN_FULL_RUN_EPISODES

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.calibration_summary: dict | None = None
        self.progress: ProgressReporter = create_progress_reporter(
            enabled=self.config.verbose,
            mode=self.config.verbosity_mode,
            include_calibration=self.config.verbosity_include_calibration,
        )

    def _create_model(self) -> TrustGameModel:
        return create_model(self.config)

    def _create_env(self, seed: int) -> TrustGameEnv:
        return create_env(self.config, seed=seed)

    def _create_agent(self, condition: int | str, model: TrustGameModel, seed: int) -> BaseAgent:
        return create_agent(self.config, condition, model, seed)

    def _resolve_calibration_episodes(self, enforce_minimum: bool) -> int:
        return resolve_calibration_episodes(self.config, enforce_minimum=enforce_minimum)

    def _calibration_condition(self) -> int:
        configured = list(self.config.conditions) + list(self.config.presets)
        configured_base_conditions = [
            int(condition)
            for condition in configured
            if isinstance(condition, int) and resolve_condition_spec(condition).agent_kind == "base"
        ]
        if configured_base_conditions:
            return max(configured_base_conditions)
        # Named presets are tau-4 based; use the matched no-affect core condition.
        return 5

    def needs_mu_calibration(self) -> bool:
        configured = list(self.config.conditions) + list(self.config.presets)
        return any(resolve_condition_spec(condition).agent_kind != "base" for condition in configured)

    def build_zero_calibration_summary(self) -> dict[str, float | int]:
        return build_zero_calibration_summary(self.config)

    def _annotate_primary_records(
        self,
        rows: list[dict],
        *,
        condition: int | str,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict]:
        for row in rows:
            row["condition_name"] = resolve_condition_spec(condition).name
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
        condition: int | str,
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
                true_partner_stance=result.get("true_partner_stance"),
            )
            partner_belief = agent.get_partner_type_belief(result["partner_idx"])
            inferred_type_idx = int(np.argmax(partner_belief))
            inferred_type = agent.model.partner_type_names[inferred_type_idx]
            inferred_correct = inferred_type == result["true_partner_type"]
            stance_belief = agent.get_partner_stance_belief(result["partner_idx"])
            inferred_stance_idx = int(np.argmax(stance_belief))
            inferred_stance = agent.model.stance_names[inferred_stance_idx]
            inferred_stance_correct = inferred_stance == result.get("true_partner_stance")
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
            agent_metrics["inferred_stance"] = inferred_stance
            agent_metrics["inferred_stance_correct"] = inferred_stance_correct
            agent_metrics["inferred_joint_correct"] = bool(inferred_correct and inferred_stance_correct)
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
            episode_count=resolve_calibration_episodes(self.config, enforce_minimum=False),
            seed=seed,
        )
        model = self._create_model()
        env = self._create_env(seed=seed)
        agent = self._create_agent(condition=self._calibration_condition(), model=model, seed=seed)
        context = env.reset()
        agent.plan_and_act(context["active_partner"])
        mean_abs_step_efe = float(agent.get_metrics()["mean_abs_step_efe"])
        self.progress.emit(
            "calibration_episode_end",
            episode_idx=episode_idx,
            episode_count=resolve_calibration_episodes(self.config, enforce_minimum=False),
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

        calibration_episodes = resolve_calibration_episodes(self.config, enforce_minimum=enforce_minimum)
        efe_values: list[float] = []
        for offset in range(calibration_episodes):
            seed = self.config.random_seed + 10_000 + offset
            episode_summary = self.run_calibration_episode(episode_idx=offset, seed=seed)
            efe_values.append(float(episode_summary["mean_abs_step_efe"]))

        self.calibration_summary = build_calibration_summary(self.config, efe_values, calibration_episodes)
        self.config.mu = float(self.calibration_summary["derived_mu"])
        return float(self.calibration_summary["derived_mu"])

    def run_replication(
        self,
        *,
        condition: int | str,
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
            checkpoint_path: If set, save partial results to this path after every
                ``checkpoint_interval`` replications per condition.
            checkpoint_interval: How often (in replications) to write a checkpoint.
                Defaults to 1 (save after every replication).
        """

        if self.needs_mu_calibration():
            self.calibrate_mu(enforce_minimum=True)

        records: list[dict] = []
        reps_since_checkpoint = 0
        configured_conditions: list[int | str] = list(self.config.conditions) + list(self.config.presets)
        for condition in configured_conditions:
            self.progress.emit(
                "condition_start",
                condition=condition,
                replication=0,
                condition_name=resolve_condition_spec(condition).name,
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
                reps_since_checkpoint += 1
                if checkpoint_path and reps_since_checkpoint >= checkpoint_interval:
                    self.save_results(pd.DataFrame(records), checkpoint_path)
                    reps_since_checkpoint = 0
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
        return build_sensitivity_specs(self.config)

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
        condition: int | str,
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
                row["condition_name"] = resolve_condition_spec(condition).name
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
        for parameter_name, parameter_value in build_sensitivity_specs(self.config):
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
    config = deserialize_config(config_payload)
    config.verbose = False
    runner = ExperimentRunner(config)
    return runner.run_calibration_episode(episode_idx=episode_idx, seed=seed)


def run_primary_replication_task(
    config_payload: dict[str, Any],
    *,
    condition: int | str,
    replication: int,
    seed: int,
    calibration_summary: dict[str, Any] | None,
    config_path: str,
    config_name: str,
    batch_id: str,
) -> dict[str, Any]:
    config = deserialize_config(config_payload)
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
        "condition": condition,
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
    condition: int | str,
    replication: int,
    seed: int,
    calibration_summary: dict[str, Any],
    config_path: str,
    config_name: str,
    batch_id: str,
) -> dict[str, Any]:
    config = deserialize_config(config_payload)
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
        "condition": condition,
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
]
