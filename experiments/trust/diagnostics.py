"""Row-level diagnostics derived from trust-runtime decisions."""

from __future__ import annotations

import numpy as np

from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import NativeTrustRuntime
from tasks.trust.runtime import Decision, PartnerSnapshot, snapshot_partner_bank

ENTROPY_TOLERANCE = 1e-10


def summarize_policy_space(
    *,
    q_pi: np.ndarray,
    per_partner_policy_count: int,
    num_partners: int,
    assignment_mode: str,
    expected_per_partner_policy_count: int,
) -> dict:
    """Return diagnostics for the policy candidates actually evaluated."""

    q_pi = np.asarray(q_pi, dtype=float)
    per_partner_policy_count = int(per_partner_policy_count)
    candidate_policy_count = (
        int(num_partners) * per_partner_policy_count
        if assignment_mode == "agent_choice"
        else per_partner_policy_count
    )
    if q_pi.size != candidate_policy_count:
        raise AssertionError(
            "policy posterior length does not match evaluated candidate count: "
            f"len(q_pi)={q_pi.size}, candidate_policy_count={candidate_policy_count}"
        )
    if not np.all(np.isfinite(q_pi)) or np.any(q_pi < -ENTROPY_TOLERANCE):
        raise AssertionError("q_pi must contain finite, non-negative probabilities")
    if not np.isclose(float(q_pi.sum()), 1.0, rtol=0.0, atol=ENTROPY_TOLERANCE):
        raise AssertionError(f"q_pi must sum to one; got {float(q_pi.sum())}")

    positive_mass = q_pi[q_pi > 0.0]
    q_pi_entropy = float(-(positive_mass * np.log(positive_mass)).sum())
    max_q_pi_entropy = float(np.log(candidate_policy_count))
    if q_pi_entropy > max_q_pi_entropy + ENTROPY_TOLERANCE:
        raise AssertionError(
            "policy entropy exceeds its candidate-space maximum: "
            f"q_pi_entropy={q_pi_entropy}, max_q_pi_entropy={max_q_pi_entropy}, "
            f"candidate_policy_count={candidate_policy_count}"
        )

    normalized_q_pi_entropy = (
        float(q_pi_entropy / max_q_pi_entropy) if max_q_pi_entropy > 0.0 else 0.0
    )
    return {
        "q_pi_entropy": q_pi_entropy,
        "per_partner_policy_count": per_partner_policy_count,
        "candidate_policy_count": candidate_policy_count,
        "max_q_pi_entropy": max_q_pi_entropy,
        "normalized_q_pi_entropy": normalized_q_pi_entropy,
        "effective_policy_count": float(np.exp(q_pi_entropy)),
        "policies_fully_enumerated": bool(
            per_partner_policy_count == int(expected_per_partner_policy_count)
        ),
    }


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
    per_partner_policy_count = int(runtime.template.policies.shape[0])
    expected_per_partner_policy_count = int(np.prod(runtime.template.num_controls)) ** int(
        runtime.planning_horizon
    )
    policy_metrics = summarize_policy_space(
        q_pi=q_pi,
        per_partner_policy_count=per_partner_policy_count,
        num_partners=config.num_partners,
        assignment_mode=config.assignment_mode,
        expected_per_partner_policy_count=expected_per_partner_policy_count,
    )
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
        **policy_metrics,
        "betas": local_betas,
        "global_beta": global_beta,
        "local_betas": local_betas,
        "prediction_errors": prediction_errors,
        "latest_surprise_by_partner": prediction_errors,
        "terminal_signal": local_betas,
        "reward_avgs": default_vector,
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
