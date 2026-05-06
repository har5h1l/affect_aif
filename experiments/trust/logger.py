"""Round-level metric logging."""

from __future__ import annotations

import numpy as np
import pandas as pd


class MetricLogger:
    """Track round-by-round metrics for a single episode."""

    def __init__(self, num_rounds: int, num_partners: int):
        self.num_rounds = int(num_rounds)
        self.num_partners = int(num_partners)
        self.records: list[dict] = []

    def log_round(
        self,
        round_idx: int,
        seed: int,
        agent_metrics: dict,
        env_result: dict,
    ):
        """Record a single round."""

        def _to_float_list(values):
            return [float(item) for item in np.asarray(values, dtype=float).tolist()]

        def _metric(name: str, default=None):
            value = agent_metrics.get(name, default)
            return default if value is None else value

        def _float_metric(name: str, default: float = float("nan")) -> float:
            value = _metric(name, default)
            try:
                return float(value)
            except (TypeError, ValueError):
                return float(default)

        def _int_metric(name: str, default: int = -1) -> int:
            value = _metric(name, default)
            try:
                if isinstance(value, float) and not np.isfinite(value):
                    return int(default)
                return int(value)
            except (TypeError, ValueError):
                return int(default)

        def _array_metric(name: str, default):
            return np.asarray(_metric(name, default), dtype=float)

        default_partner_vector = np.full((self.num_partners,), np.nan, dtype=float)
        default_partner_beliefs = np.full((self.num_partners, 0), np.nan, dtype=float)
        default_posteriors = np.asarray([], dtype=float)
        partner_beliefs = _array_metric("partner_beliefs", default_partner_beliefs)
        partner_posteriors = _array_metric("partner_posteriors", default_posteriors)
        partner_joint_beliefs = _array_metric("partner_joint_beliefs", partner_beliefs)
        partner_joint_posteriors = _array_metric("partner_joint_posteriors", default_posteriors)
        partner_stance_beliefs = _array_metric("partner_stance_beliefs", default_partner_beliefs)
        betas = _array_metric("betas", default_partner_vector)
        terminal_signal = _array_metric("terminal_signal", betas)
        prediction_errors = _array_metric(
            "latest_surprise_by_partner",
            _metric("prediction_errors", default_partner_vector),
        )

        record = {
            "seed": int(seed),
            "round": int(round_idx),
            "partner_idx": int(env_result["partner_idx"]),
            "active_partner": (
                -1
                if env_result.get("active_partner_start", -1) is None
                else int(env_result.get("active_partner_start", -1))
            ),
            "true_partner_type": str(env_result["true_partner_type"]),
            "true_partner_stance": str(env_result.get("true_partner_stance", "unknown")),
            "agent_action": int(env_result["agent_action"]),
            "raw_action": int(env_result["raw_action"]),
            "partner_action": int(env_result["partner_action"]),
            "payoff": float(env_result["agent_payoff"]),
            "partner_payoff": float(env_result["partner_payoff"]),
            "type_switched": bool(env_result["type_switched"]),
            "stance_switched": bool(env_result.get("stance_switched", False)),
            "switch_kind": str(env_result.get("switch_kind", "none")),
            "current_partner_switched": bool(env_result.get("current_partner_switched", env_result["type_switched"])),
            "current_partner_scheduled_switch": bool(env_result.get("current_partner_scheduled_switch", False)),
            "current_partner_scheduled_stance_switch": bool(
                env_result.get("current_partner_scheduled_stance_switch", False)
            ),
            "scheduled_switch_partner_ids": list(env_result.get("scheduled_switch_partner_ids", [])),
            "scheduled_stance_switch_partner_ids": list(env_result.get("scheduled_stance_switch_partner_ids", [])),
            "active_partner_next": env_result["active_partner"],
            "true_types": list(env_result["true_types"]),
            "true_stances": list(env_result.get("true_stances", [])),
            "inferred_type": str(agent_metrics["inferred_type"]),
            "inferred_type_correct": bool(agent_metrics["inferred_type_correct"]),
            "inferred_stance": str(agent_metrics.get("inferred_stance", "unknown")),
            "inferred_stance_correct": bool(agent_metrics.get("inferred_stance_correct", False)),
            "inferred_joint_correct": bool(agent_metrics.get("inferred_joint_correct", False)),
            "selected_partner": _int_metric("selected_partner"),
            "selected_action": _int_metric("selected_action"),
            "best_policy_idx": _int_metric("best_policy_idx"),
            "q_pi_entropy": _float_metric("q_pi_entropy"),
            "mean_abs_step_efe": _float_metric("mean_abs_step_efe"),
            "planning_cost": _float_metric("planning_cost"),
            "planning_cost_ratio": _float_metric("planning_cost_ratio"),
            "betas": _to_float_list(betas),
            "terminal_signal": _to_float_list(terminal_signal),
            "prediction_errors": _to_float_list(prediction_errors),
            "reward_avgs": _to_float_list(_metric("reward_avgs", default_partner_vector)),
            "G": _to_float_list(_metric("G", [])),
            "q_pi": _to_float_list(_metric("q_pi", [])),
            "best_policy_step_costs": _to_float_list(_metric("best_policy_step_costs", [])),
            "predictive_log_lik": float(agent_metrics.get("predictive_log_lik", float("nan"))),
            "partner_beliefs": partner_beliefs.tolist(),
            "partner_posteriors": partner_posteriors.tolist(),
            "partner_joint_beliefs": partner_joint_beliefs.tolist(),
            "partner_joint_posteriors": partner_joint_posteriors.tolist(),
            "partner_stance_beliefs": partner_stance_beliefs.tolist(),
            "round_log_evidence": float(agent_metrics.get("round_log_evidence", float("nan"))),
            "cumulative_log_evidence": float(agent_metrics.get("cumulative_log_evidence", 0.0)),
        }
        self.records.append(record)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert logged rounds to a DataFrame."""

        return pd.DataFrame(self.records)

    def get_cumulative_payoff(self) -> np.ndarray:
        """Running cumulative payoff over the episode."""

        payoffs = np.asarray([row["payoff"] for row in self.records], dtype=float)
        return payoffs.cumsum()

    def get_type_identification_accuracy(self) -> np.ndarray:
        """Per-round correctness of the inferred partner type."""

        return np.asarray([row["inferred_type_correct"] for row in self.records], dtype=float)
