"""Experiment runner and process-safe task helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import (
    NativeTrustRuntime,
    create_env,
    create_native_runtime_from_run,
)
from experiments.trust.logger import MetricLogger
from experiments.trust.progress import ProgressReporter, create_progress_reporter
from experiments.trust.spec import ExpandedRunSpec, ExperimentSpec
from tasks.trust.envs import TrustGameEnv
from tasks.trust.runtime import (
    Decision,
    PartnerSnapshot,
    predictive_log_likelihood,
    select_decision,
    snapshot_partner_bank,
    update_beta_after_observation,
    update_partner_after_observation,
)


def checkpoint_group_complete(group: pd.DataFrame, expected_rounds: int) -> bool:
    """Return True when a partial checkpoint has one row for every expected round."""

    if "round" not in group.columns:
        return False
    observed_rounds = set(pd.to_numeric(group["round"], errors="coerce").dropna().astype(int))
    return observed_rounds >= set(range(int(expected_rounds)))


class ExperimentRunner:
    """Run expanded TOML experiment variants."""

    def __init__(self, *, spec: ExperimentSpec, verbose: bool = False, verbosity_mode: str = "stage_stream"):
        self.spec = spec
        self.progress: ProgressReporter = create_progress_reporter(
            enabled=bool(verbose),
            mode=str(verbosity_mode),
        )

    @classmethod
    def from_spec(
        cls,
        spec: ExperimentSpec,
        *,
        verbose: bool = False,
        verbosity_mode: str = "stage_stream",
    ) -> ExperimentRunner:
        return cls(spec=spec, verbose=verbose, verbosity_mode=verbosity_mode)

    def _create_env(self, config: ExperimentConfig, seed: int) -> TrustGameEnv:
        return create_env(config, seed=seed)

    def _run_episode(
        self,
        runtime: NativeTrustRuntime,
        env: TrustGameEnv,
        config: ExperimentConfig,
        seed: int,
        variant_id: str,
        replication: int = 0,
    ) -> list[dict]:
        logger = MetricLogger(
            num_rounds=config.num_rounds,
            num_partners=config.num_partners,
            log_policy_traces=config.log_policy_traces,
        )
        context = env.reset()

        for round_idx in range(config.num_rounds):
            active_partner = context["active_partner"]
            self.progress.emit(
                "round_start",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                active_partner=active_partner,
            )
            self.progress.emit(
                "planning_start",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                active_partner=active_partner,
            )
            decision = select_decision(
                bank=runtime.partner_bank,
                template=runtime.template,
                active_partner=active_partner,
                assignment_mode=config.assignment_mode,
                base_gamma=runtime.base_gamma,
                action_selection=runtime.action_selection,
                rng=runtime.rng,
                affect_mode=runtime.affect_mode,
            )
            planning_metrics = self._decision_diagnostics(config, runtime, decision, None, None)
            self.progress.emit(
                "planning_end",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                selected_partner=planning_metrics["selected_partner"],
                selected_action=planning_metrics["selected_action"],
                raw_action=planning_metrics["raw_action"],
                best_policy_idx=planning_metrics["best_policy_idx"],
            )
            self.progress.emit(
                "environment_step_start",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                raw_action=decision.raw_action,
            )
            result = env.step(decision.raw_action)
            result["active_partner_start"] = active_partner
            self.progress.emit(
                "environment_step_end",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                partner_idx=result["partner_idx"],
                agent_action=result["agent_action"],
                partner_action=result["partner_action"],
                payoff=result["agent_payoff"],
                switch_kind=result.get("switch_kind", "none"),
            )
            self.progress.emit(
                "belief_update_start",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                partner_idx=result["partner_idx"],
            )
            predictive_log_lik = predictive_log_likelihood(
                decision.predicted_partner_action_probs,
                result["partner_action"],
            )
            runtime.partner_bank.round_log_evidence = predictive_log_lik
            runtime.partner_bank.cumulative_log_evidence += predictive_log_lik
            update_beta_after_observation(
                bank=runtime.partner_bank,
                partner_idx=result["partner_idx"],
                predicted_partner_action_probs=decision.predicted_partner_action_probs,
                observed_partner_action=result["partner_action"],
                affect_mode=runtime.affect_mode,
            )
            update_partner_after_observation(
                bank=runtime.partner_bank,
                template=runtime.template,
                partner_idx=result["partner_idx"],
                obs=result["observation"],
                own_action=result["agent_action"],
            )
            snapshot = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template)
            partner_belief = snapshot.partner_type_beliefs[result["partner_idx"]]
            inferred_type_idx = int(np.argmax(partner_belief))
            inferred_type = runtime.template.partner_type_names[inferred_type_idx]
            inferred_correct = inferred_type == result["true_partner_type"]
            stance_belief = snapshot.partner_stance_beliefs[result["partner_idx"]]
            inferred_stance_idx = int(np.argmax(stance_belief))
            inferred_stance = runtime.template.stance_names[inferred_stance_idx]
            inferred_stance_correct = inferred_stance == result.get("true_partner_stance")
            self.progress.emit(
                "belief_update_end",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                partner_idx=result["partner_idx"],
                inferred_type=inferred_type,
                inferred_type_correct=inferred_correct,
            )

            agent_metrics = self._decision_diagnostics(config, runtime, decision, snapshot, result)
            agent_metrics["inferred_type"] = inferred_type
            agent_metrics["inferred_type_correct"] = inferred_correct
            agent_metrics["inferred_stance"] = inferred_stance
            agent_metrics["inferred_stance_correct"] = inferred_stance_correct
            agent_metrics["inferred_joint_correct"] = bool(inferred_correct and inferred_stance_correct)
            agent_metrics["predictive_log_lik"] = predictive_log_lik
            logger.log_round(
                round_idx=round_idx,
                seed=seed,
                agent_metrics=agent_metrics,
                env_result=result,
            )
            self.progress.emit(
                "metric_logging_end",
                variant_id=variant_id,
                replication=replication,
                round_idx=round_idx,
                round_count=config.num_rounds,
                payoff=result["agent_payoff"],
                inferred_type=inferred_type,
                q_pi_entropy=agent_metrics["q_pi_entropy"],
            )
            context = {"active_partner": result["active_partner"]}

        return logger.records

    def _decision_diagnostics(
        self,
        config: ExperimentConfig,
        runtime: NativeTrustRuntime,
        decision: Decision,
        snapshot: PartnerSnapshot | None,
        env_result: dict | None,
    ) -> dict:
        """Expose native pymdp decisions under experiment column names."""

        del env_result
        q_pi = np.asarray(decision.q_pi, dtype=float)
        entropy = float(-(q_pi * np.log(q_pi + 1e-16)).sum()) if q_pi.size else np.nan
        num_step_controls = int(np.prod(runtime.template.num_controls))
        planning_cost = float((num_step_controls**runtime.planning_horizon) * runtime.planning_horizon)
        planning_cost_ratio = 1.0
        default_vector = np.full((config.num_partners,), np.nan, dtype=float)
        betas = (
            np.asarray(runtime.partner_bank.beta.expected_beta(), dtype=float)
            if runtime.partner_bank.beta is not None
            else default_vector
        )
        prediction_errors = (
            np.asarray(runtime.partner_bank.latest_surprise, dtype=float)
            if runtime.partner_bank.latest_surprise is not None
            else default_vector
        )
        if snapshot is None:
            snapshot = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template)
        return {
            "q_pi": q_pi,
            "G": np.asarray(decision.policy_scores, dtype=float),
            "best_policy_step_costs": np.asarray([], dtype=float),
            "mean_abs_step_efe": (
                float(np.mean(np.abs(decision.policy_scores))) if decision.policy_scores.size else np.nan
            ),
            "best_policy_idx": int(decision.best_policy_idx),
            "selected_partner": int(decision.selected_partner),
            "selected_action": int(decision.selected_action),
            "raw_action": int(decision.raw_action),
            "q_pi_entropy": entropy,
            "betas": betas,
            "prediction_errors": prediction_errors,
            "latest_surprise_by_partner": prediction_errors,
            "terminal_signal": betas,
            "reward_avgs": default_vector,
            "partner_beliefs": snapshot.partner_type_beliefs,
            "partner_posteriors": snapshot.partner_joint_posteriors.sum(axis=2),
            "partner_joint_beliefs": snapshot.partner_joint_beliefs,
            "partner_joint_posteriors": snapshot.partner_joint_posteriors,
            "partner_stance_beliefs": snapshot.partner_stance_beliefs,
            "planning_cost": planning_cost,
            "planning_cost_ratio": planning_cost_ratio,
            "round_log_evidence": runtime.partner_bank.round_log_evidence,
            "cumulative_log_evidence": runtime.partner_bank.cumulative_log_evidence,
        }

    def run_replication(
        self,
        *,
        run: ExpandedRunSpec,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict]:
        return self._run_variant_replication(
            run=run,
            config_path=config_path,
            config_name=config_name,
            batch_id=batch_id,
        )

    def _run_variant_replication(
        self,
        *,
        run: ExpandedRunSpec,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
    ) -> list[dict]:
        runtime_config = run.to_runtime_config()
        self.progress.emit(
            "replication_start",
            variant_id=run.variant_id,
            replication=run.replication,
            seed=run.seed,
        )
        env = self._create_env(runtime_config, seed=run.seed)
        runtime = create_native_runtime_from_run(run)
        rows = self._run_episode(
            runtime=runtime,
            env=env,
            config=runtime_config,
            seed=run.seed,
            variant_id=run.variant_id,
            replication=run.replication,
        )
        for row in rows:
            row["hypothesis_id"] = run.hypothesis_id
            row["experiment_id"] = run.experiment_id
            row["variant_id"] = run.variant_id
            row["replication"] = int(run.replication)
            row["seed"] = int(run.seed)
            row["config_path"] = config_path or np.nan
            row["config_name"] = config_name or run.experiment_id
            row["batch_id"] = batch_id or np.nan
        return rows

    def run_all(
        self,
        *,
        config_path: str | None = None,
        config_name: str | None = None,
        batch_id: str | None = None,
        checkpoint_path: str | None = None,
        checkpoint_interval: int = 1,
    ) -> pd.DataFrame:
        """Run all expanded variants across all seeds.

        Args:
            checkpoint_path: If set, save partial results to this path after every
                ``checkpoint_interval`` replications per variant.
            checkpoint_interval: How often (in replications) to write a checkpoint.
                Defaults to 1 (save after every replication).
        """

        expanded_runs = self.spec.expand_runs()
        records: list[dict] = []
        completed_keys: set[tuple[str, int, int]] = set()
        if checkpoint_path:
            checkpoint = Path(checkpoint_path)
            if checkpoint.exists():
                partial = pd.read_csv(checkpoint, low_memory=False)
                required = {"variant_id", "seed", "replication", "round"}
                if not partial.empty and required <= set(partial.columns):
                    expected_rounds = {
                        (str(run.variant_id), int(run.seed), int(run.replication)): int(run.rounds)
                        for run in expanded_runs
                    }
                    for values, group in partial.groupby(["variant_id", "seed", "replication"], dropna=False):
                        key = (str(values[0]), int(values[1]), int(values[2]))
                        expected = expected_rounds.get(key)
                        if expected is not None and checkpoint_group_complete(group, expected):
                            completed_keys.add(key)
                    if completed_keys:
                        resumed = partial[
                            partial.apply(
                                lambda row: (
                                    str(row["variant_id"]),
                                    int(row["seed"]),
                                    int(row["replication"]),
                                )
                                in completed_keys,
                                axis=1,
                            )
                        ]
                        records.extend(resumed.to_dict(orient="records"))
        reps_since_checkpoint = 0
        for run in expanded_runs:
            key = (str(run.variant_id), int(run.seed), int(run.replication))
            if key in completed_keys:
                continue
            records.extend(
                self.run_replication(
                    run=run,
                    config_path=config_path or self.spec.path,
                    config_name=config_name or self.spec.experiment.id,
                    batch_id=batch_id,
                )
            )
            reps_since_checkpoint += 1
            if checkpoint_path and reps_since_checkpoint >= checkpoint_interval:
                self.save_results(pd.DataFrame(records), checkpoint_path)
                reps_since_checkpoint = 0
        return pd.DataFrame(records)

    def save_results(self, results: pd.DataFrame, path: str):
        """Persist results to CSV or parquet."""

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".parquet":
            results.to_parquet(target, index=False)
            return
        results.to_csv(target, index=False)

__all__ = [
    "ExperimentRunner",
]
