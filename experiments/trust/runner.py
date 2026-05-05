"""Experiment runner and process-safe task helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from experiments.trust.calibration import (
    build_sensitivity_specs,
)
from experiments.trust.conditions import resolve_condition_spec
from experiments.trust.config import ExperimentConfig
from experiments.trust.constants import SENSITIVITY_CONDITIONS
from experiments.trust.factory import create_agent, create_env, create_model
from experiments.trust.logger import MetricLogger
from experiments.trust.progress import ProgressReporter, create_progress_reporter
from tasks.trust import TrustGameAgent, TrustGameModel
from tasks.trust.envs import TrustGameEnv


class ExperimentRunner:
    """Run all conditions for an experiment configuration."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.progress: ProgressReporter = create_progress_reporter(
            enabled=self.config.verbose,
            mode=self.config.verbosity_mode,
            include_calibration=self.config.verbosity_include_calibration,
        )

    def _create_model(self) -> TrustGameModel:
        return create_model(self.config)

    def _create_env(self, seed: int) -> TrustGameEnv:
        return create_env(self.config, seed=seed)

    def _create_agent(self, condition: int | str, model: TrustGameModel, seed: int) -> TrustGameAgent:
        return create_agent(self.config, condition, model, seed)

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
            row["run_mode"] = "primary"
            row["config_path"] = config_path or np.nan
            row["config_name"] = config_name or self.config.experiment_name
            row["batch_id"] = batch_id or np.nan
        return rows

    def _run_episode(
        self,
        agent: TrustGameAgent,
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
            planning_metrics = self._agent_diagnostics(agent, agent.get_metrics())
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

            agent_metrics = self._agent_diagnostics(agent, agent.get_metrics())
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

    def _agent_diagnostics(self, agent: TrustGameAgent, metrics: dict) -> dict:
        """Expose pymdp-backed public diagnostics under experiment column names."""

        diagnostics = dict(metrics)
        for column, attr in (
            ("q_pi", "q_pi"),
            ("G", "policy_scores"),
            ("best_policy_idx", "best_policy_idx"),
            ("selected_partner", "selected_partner"),
            ("selected_action", "selected_action"),
            ("raw_action", "last_raw_action"),
            ("partner_beliefs", "partner_beliefs"),
        ):
            if diagnostics.get(column) is None and hasattr(agent, attr):
                diagnostics[column] = getattr(agent, attr)
        if hasattr(agent, "latest_surprise_by_partner"):
            diagnostics["latest_surprise_by_partner"] = getattr(agent, "latest_surprise_by_partner")
            diagnostics["prediction_errors"] = getattr(agent, "latest_surprise_by_partner")
        if "betas" not in diagnostics and hasattr(agent, "get_betas"):
            diagnostics["betas"] = agent.get_betas()
        if "terminal_signal" not in diagnostics:
            diagnostics["terminal_signal"] = diagnostics.get("betas", np.full((agent.num_partners,), np.nan))
        return diagnostics

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
        if self.config.run_sensitivity:
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

    def _apply_sensitivity_override(self, parameter_name: str, parameter_value: float):
        if parameter_name == "alpha_charge":
            self.config.alpha_charge = float(parameter_value)
        elif parameter_name == "sigma_0_sq":
            self.config.sigma_0_sq = float(parameter_value)
        elif parameter_name == "beta_persistence":
            self.config.beta_persistence = float(parameter_value)
        elif parameter_name == "initial_beta":
            self.config.initial_beta = float(parameter_value)

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
        original_alpha = self.config.alpha_charge
        original_sigma = self.config.sigma_0_sq
        original_persistence = self.config.beta_persistence
        original_initial_beta = self.config.initial_beta
        try:
            self._apply_sensitivity_override(parameter_name, float(parameter_value))
            model = self._create_model()
            env = self._create_env(seed=seed)
            agent = self._create_agent(condition=condition, model=model, seed=seed)
            rows = self._run_episode(agent=agent, env=env, seed=seed, condition=condition, replication=replication)
            for row in rows:
                row["condition_name"] = resolve_condition_spec(condition).name
                row["sensitivity_parameter"] = parameter_name
                row["sensitivity_value"] = float(parameter_value)
                row["run_mode"] = "sensitivity"
                row["config_path"] = config_path or np.nan
                row["config_name"] = config_name or self.config.experiment_name
                row["batch_id"] = batch_id or np.nan
            return rows
        finally:
            self.config.alpha_charge = original_alpha
            self.config.sigma_0_sq = original_sigma
            self.config.beta_persistence = original_persistence
            self.config.initial_beta = original_initial_beta

    def run_parameter_sensitivity(
        self,
        *,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> pd.DataFrame:
        """Run one-at-a-time sensitivity sweeps for affective state hyperparameters."""

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


__all__ = [
    "ExperimentRunner",
]
