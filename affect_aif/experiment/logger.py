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
        condition: int,
        seed: int,
        agent_metrics: dict,
        env_result: dict,
    ):
        """Record a single round."""

        def _to_float_list(values):
            return [float(item) for item in np.asarray(values, dtype=float).tolist()]

        record = {
            "condition": int(condition),
            "seed": int(seed),
            "round": int(round_idx),
            "partner_idx": int(env_result["partner_idx"]),
            "true_partner_type": str(env_result["true_partner_type"]),
            "agent_action": int(env_result["agent_action"]),
            "raw_action": int(env_result["raw_action"]),
            "partner_action": int(env_result["partner_action"]),
            "payoff": float(env_result["agent_payoff"]),
            "partner_payoff": float(env_result["partner_payoff"]),
            "type_switched": bool(env_result["type_switched"]),
            "active_partner_next": env_result["active_partner"],
            "true_types": list(env_result["true_types"]),
            "inferred_type": str(agent_metrics["inferred_type"]),
            "inferred_type_correct": bool(agent_metrics["inferred_type_correct"]),
            "q_pi_entropy": float(agent_metrics["q_pi_entropy"]),
            "mean_abs_step_efe": float(agent_metrics["mean_abs_step_efe"]),
            "planning_cost": float(agent_metrics["planning_cost"]),
            "planning_cost_ratio": float(agent_metrics["planning_cost_ratio"]),
            "mu": float(agent_metrics["mu"]),
            "betas": _to_float_list(agent_metrics["betas"]),
            "prediction_errors": _to_float_list(agent_metrics["prediction_errors"]),
            "reward_avgs": _to_float_list(agent_metrics["reward_avgs"]),
            "terminal_values": _to_float_list(agent_metrics["terminal_values"]),
            "G": _to_float_list(agent_metrics["G"]),
            "q_pi": _to_float_list(agent_metrics["q_pi"]),
            "best_policy_step_costs": _to_float_list(agent_metrics["best_policy_step_costs"]),
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
