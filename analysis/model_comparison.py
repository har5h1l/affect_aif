"""Predictive log-score comparison for agent variants.

Each agent condition is treated as a predictive model. Per-round predictive
log probabilities of the observed partner action accumulate across an episode
to give the total predictive log score for that model on that seed.

Pairwise comparisons report differences in total predictive log scores.
Random-effects Bayesian model selection (Stephan et al., 2009) is kept intact
for the same seed-by-condition score matrix; the semantics of those inputs are
now described explicitly as predictive log scores rather than exact evidence.
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import digamma, gammaln

from analysis.metrics import final_round_summary


def _condition_sort_key(value) -> tuple[int, str]:
    if isinstance(value, (int, np.integer)):
        return (0, f"{int(value):04d}")
    return (1, str(value))


def _condition_value(value):
    return value.item() if isinstance(value, np.generic) else value


def log_score_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Per-condition summary of total predictive log score across seeds.

    Returns a DataFrame with canonical predictive-log-score columns and legacy
    log-evidence aliases for compatibility.
    """
    summary = final_round_summary(results)
    if "total_log_evidence" not in summary.columns:
        raise ValueError(
            "Results do not contain predictive log-score data. Re-run experiments with the updated agent code."
        )

    records = []
    for (cond, cond_name), grp in summary.groupby(["condition", "condition_name"]):
        scores = grp["total_log_evidence"].to_numpy()
        scores = scores[np.isfinite(scores)]
        mean_score = float(scores.mean()) if len(scores) > 0 else float("nan")
        se_score = float(scores.std(ddof=1) / np.sqrt(len(scores))) if len(scores) > 1 else float("nan")
        median_score = float(np.median(scores)) if len(scores) > 0 else float("nan")
        records.append(
            {
                "condition": _condition_value(cond),
                "condition_name": str(cond_name),
                "n_seeds": len(scores),
                "mean_predictive_log_score": mean_score,
                "se_predictive_log_score": se_score,
                "median_predictive_log_score": median_score,
                "mean_log_evidence": mean_score,
                "se_log_evidence": se_score,
                "median_log_evidence": median_score,
            }
        )
    return pd.DataFrame(records)


def log_evidence_summary(results: pd.DataFrame) -> pd.DataFrame:
    """Compatibility alias for :func:`log_score_summary`."""

    return log_score_summary(results)


def pairwise_predictive_log_scores(results: pd.DataFrame) -> pd.DataFrame:
    """Compute pairwise predictive log-score differences between conditions.

    For each pair (A, B), computes the mean difference in total predictive log
    score mean(score_A) - mean(score_B) across seeds. Also reports the
    proportion of seeds where model A is preferred.

    Interpretation of |log10 score difference|:
        < 0.5: not worth more than a bare mention
        0.5-1: substantial
        1-2:   strong
        > 2:   decisive  (Kass & Raftery, 1995)
    """
    summary = final_round_summary(results)
    if "total_log_evidence" not in summary.columns:
        raise ValueError("Results do not contain predictive log-score data.")

    records = []
    for (cond_a, frame_a), (cond_b, frame_b) in combinations(summary.groupby("condition"), 2):
        le_a = frame_a["total_log_evidence"].to_numpy()
        le_b = frame_b["total_log_evidence"].to_numpy()
        le_a = le_a[np.isfinite(le_a)]
        le_b = le_b[np.isfinite(le_b)]

        if len(le_a) < 2 or len(le_b) < 2:
            records.append(
                {
                    "condition_a": _condition_value(cond_a),
                    "condition_b": _condition_value(cond_b),
                    "mean_predictive_log_score_difference": float("nan"),
                    "log10_predictive_log_score_difference": float("nan"),
                    "se_predictive_log_score_difference": float("nan"),
                    "mean_log_bf": float("nan"),
                    "log10_bf": float("nan"),
                    "se_log_bf": float("nan"),
                    "prop_a_preferred": float("nan"),
                    "t_stat": float("nan"),
                    "p_value": float("nan"),
                }
            )
            continue

        mean_diff = float(le_a.mean() - le_b.mean())
        se_diff = float(np.sqrt(le_a.var(ddof=1) / len(le_a) + le_b.var(ddof=1) / len(le_b)))

        # Welch t-test on log-evidence difference
        t_stat, p_value = stats.ttest_ind(le_a, le_b, equal_var=False)

        # Per-seed comparison (matched by index for equal-length, otherwise just proportions)
        n_min = min(len(le_a), len(le_b))
        prop_a = float((le_a[:n_min] > le_b[:n_min]).mean()) if n_min > 0 else float("nan")

        records.append(
            {
                "condition_a": _condition_value(cond_a),
                "condition_b": _condition_value(cond_b),
                "mean_predictive_log_score_difference": mean_diff,
                "log10_predictive_log_score_difference": float(mean_diff / np.log(10)),
                "se_predictive_log_score_difference": se_diff,
                "mean_log_bf": mean_diff,
                "log10_bf": float(mean_diff / np.log(10)),
                "se_log_bf": se_diff,
                "prop_a_preferred": prop_a,
                "t_stat": float(t_stat),
                "p_value": float(p_value),
            }
        )

    return pd.DataFrame(records)


def pairwise_bayes_factors(results: pd.DataFrame) -> pd.DataFrame:
    """Compatibility alias for :func:`pairwise_predictive_log_scores`."""

    return pairwise_predictive_log_scores(results)


def _spm_bms(log_evidence_matrix: np.ndarray, max_iter: int = 100, tol: float = 1e-6) -> dict:
    """Random-effects Bayesian model selection (Stephan et al., 2009).

    Parameters
    ----------
    log_evidence_matrix : ndarray, shape (n_subjects, n_models)
        Per-subject total predictive log score for each model.
    max_iter : int
        Maximum VB iterations.
    tol : float
        Convergence tolerance on alpha.

    Returns
    -------
    dict with keys:
        alpha: posterior Dirichlet parameters
        expected_frequency: E[r_k] = alpha_k / sum(alpha)
        exceedance_probability: P(r_k > r_j for all j != k)
        protected_exceedance_probability: accounts for chance
    """
    n_subjects, n_models = log_evidence_matrix.shape
    alpha0 = np.ones(n_models)
    alpha = alpha0.copy()

    for _ in range(max_iter):
        # E-step: compute responsibilities
        # log u_nk = log_evidence_nk + digamma(alpha_k) - digamma(sum(alpha))
        log_u = log_evidence_matrix + digamma(alpha)[None, :] - digamma(alpha.sum())
        # Normalize to get responsibilities
        log_u_max = log_u.max(axis=1, keepdims=True)
        u = np.exp(log_u - log_u_max)
        responsibilities = u / u.sum(axis=1, keepdims=True)

        # M-step: update Dirichlet parameters
        alpha_new = alpha0 + responsibilities.sum(axis=0)

        if np.max(np.abs(alpha_new - alpha)) < tol:
            alpha = alpha_new
            break
        alpha = alpha_new

    expected_freq = alpha / alpha.sum()

    # Exceedance probability via sampling from the posterior Dirichlet
    n_samples = 100_000
    rng = np.random.default_rng(42)
    samples = rng.dirichlet(alpha, size=n_samples)
    winners = samples.argmax(axis=1)
    exceedance = np.array([float((winners == k).mean()) for k in range(n_models)])

    # Protected exceedance probability (Rigoux et al., 2014)
    # Accounts for the possibility that the data do not discriminate between models
    bor = _bayesian_omnibus_risk(log_evidence_matrix, alpha)
    protected_xp = exceedance * (1.0 - bor) + (1.0 / n_models) * bor

    return {
        "alpha": alpha.tolist(),
        "expected_frequency": expected_freq.tolist(),
        "exceedance_probability": exceedance.tolist(),
        "protected_exceedance_probability": protected_xp.tolist(),
        "bayesian_omnibus_risk": float(bor),
    }


def _bayesian_omnibus_risk(log_evidence_matrix: np.ndarray, alpha: np.ndarray) -> float:
    """Bayesian omnibus risk: probability that model frequencies are equal.

    Compares the fitted Dirichlet against a flat Dirichlet(1,...,1).
    BOR = p(H0) / (p(H0) + p(H1)) where H0 is the null (all models equal).
    The comparison operates on predictive log scores rather than exact model
    evidence.
    """
    n_subjects, n_models = log_evidence_matrix.shape

    # Log evidence under the null (flat Dirichlet)
    log_ev_null = _dirichlet_log_evidence(log_evidence_matrix, np.ones(n_models))
    # Log evidence under the fitted model
    log_ev_fitted = _dirichlet_log_evidence(log_evidence_matrix, alpha)

    # BOR with equal prior on H0 and H1
    log_bf = log_ev_null - log_ev_fitted
    bor = 1.0 / (1.0 + np.exp(-log_bf))
    return float(bor)


def _dirichlet_log_evidence(log_evidence_matrix: np.ndarray, alpha0: np.ndarray) -> float:
    """Approximate score for a Dirichlet-multinomial model of assignments."""
    n_subjects, n_models = log_evidence_matrix.shape

    # Compute responsibilities under this prior
    log_u = log_evidence_matrix + digamma(alpha0)[None, :] - digamma(alpha0.sum())
    log_u_max = log_u.max(axis=1, keepdims=True)
    u = np.exp(log_u - log_u_max)
    resp = u / u.sum(axis=1, keepdims=True)

    # Approximate log-evidence: sum of log-normalizers
    alpha_post = alpha0 + resp.sum(axis=0)
    log_ev = (
        gammaln(alpha0.sum())
        - gammaln(alpha_post.sum())
        + gammaln(alpha_post).sum()
        - gammaln(alpha0).sum()
        + np.sum(log_u_max)
        + np.sum(np.log(u.sum(axis=1, keepdims=True)))
    )
    return float(log_ev)


def random_effects_bms(results: pd.DataFrame) -> dict:
    """Run random-effects Bayesian model selection on experiment results.

    Each seed is treated as a 'subject'. Returns posterior model frequencies
    and protected exceedance probabilities from the predictive log-score matrix.
    """
    summary = final_round_summary(results)
    if "total_log_evidence" not in summary.columns:
        raise ValueError("Results do not contain predictive log-score data.")

    conditions = sorted(summary["condition"].unique(), key=_condition_sort_key)
    seeds = sorted(summary["seed"].unique())

    # Build the predictive log-score matrix (n_seeds x n_conditions)
    le_matrix = np.full((len(seeds), len(conditions)), np.nan)
    for j, cond in enumerate(conditions):
        cond_data = summary[summary["condition"] == cond]
        for i, seed in enumerate(seeds):
            seed_data = cond_data[cond_data["seed"] == seed]
            if len(seed_data) == 1:
                le_matrix[i, j] = float(seed_data["total_log_evidence"].iloc[0])

    # Drop rows with any NaN (seeds not present in all conditions)
    valid_mask = np.all(np.isfinite(le_matrix), axis=1)
    le_matrix = le_matrix[valid_mask]

    if le_matrix.shape[0] < 3:
        return {
            "error": "Too few complete seeds for random-effects BMS",
            "n_valid_seeds": int(le_matrix.shape[0]),
        }

    bms_result = _spm_bms(le_matrix)
    bms_result["conditions"] = [c.item() if isinstance(c, np.generic) else c for c in conditions]
    bms_result["n_valid_seeds"] = int(le_matrix.shape[0])
    return bms_result


def model_comparison_report(results: pd.DataFrame) -> dict:
    """Full predictive log-score comparison report.

    Returns a dict with:
        - predictive_log_score_summary: per-condition summary
        - pairwise_predictive_log_scores: all pairwise score differences
        - random_effects_bms: RFX-BMS results (if enough data)
        - legacy log_evidence_summary / pairwise_bayes_factors aliases
    """
    le_summary = log_score_summary(results)
    bf_table = pairwise_predictive_log_scores(results)
    bms = random_effects_bms(results)

    return {
        "predictive_log_score_summary": le_summary.to_dict(orient="records"),
        "log_evidence_summary": le_summary.to_dict(orient="records"),
        "pairwise_predictive_log_scores": bf_table.to_dict(orient="records"),
        "pairwise_bayes_factors": bf_table.to_dict(orient="records"),
        "random_effects_bms": bms,
    }
