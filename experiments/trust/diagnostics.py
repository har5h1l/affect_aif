"""Row-level diagnostics derived from trust-runtime decisions."""

from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import NativeTrustRuntime
from tasks.trust.runtime import Decision, PartnerSnapshot, snapshot_partner_bank


def build_decision_diagnostics(
    *,
    config: ExperimentConfig,
    runtime: NativeTrustRuntime,
    decision: Decision,
    snapshot: PartnerSnapshot | None,
    include_diagnostics: bool = False,
) -> dict:
    """Expose native pymdp decisions under experiment column names."""

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
    global_beta = (
        float(betas[0])
        if runtime.affect_mode == "global" and np.asarray(betas, dtype=float).size
        else np.nan
    )
    local_betas = (
        np.full((config.num_partners,), global_beta, dtype=float)
        if runtime.affect_mode == "global"
        else np.asarray(betas, dtype=float)
    )
    prediction_errors = (
        np.asarray(runtime.partner_bank.latest_surprise, dtype=float)
        if runtime.partner_bank.latest_surprise is not None
        else default_vector
    )
    if include_diagnostics and snapshot is None:
        snapshot = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template)
    metrics = {
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
        "betas": local_betas,
        "global_beta": global_beta,
        "local_betas": local_betas,
        "prediction_errors": prediction_errors,
        "latest_surprise_by_partner": prediction_errors,
        "terminal_signal": local_betas,
        "reward_avgs": default_vector,
        "planning_cost": planning_cost,
        "planning_cost_ratio": planning_cost_ratio,
        "round_log_evidence": runtime.partner_bank.round_log_evidence,
        "cumulative_log_evidence": runtime.partner_bank.cumulative_log_evidence,
    }
    if include_diagnostics and snapshot is not None:
        metrics.update(
            {
                "partner_beliefs": snapshot.partner_type_beliefs,
                "partner_posteriors": snapshot.partner_joint_posteriors.sum(axis=2),
                "partner_joint_beliefs": snapshot.partner_joint_beliefs,
                "partner_joint_posteriors": snapshot.partner_joint_posteriors,
                "partner_stance_beliefs": snapshot.partner_stance_beliefs,
            }
        )
    return metrics
