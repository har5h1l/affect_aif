"""Shared stance dynamics for trust-game partners and agents."""

from __future__ import annotations

import numpy as np

STANCE_ORDER = ("trusting", "neutral", "hostile")
AGENT_CHARACTER_ORDER = ("cooperative", "exploitative", "unreliable")

_COOPERATE_LIKELIHOOD = np.asarray([0.85, 0.15, 0.50], dtype=float)
_DEFECT_LIKELIHOOD = 1.0 - _COOPERATE_LIKELIHOOD

_TYPE_STANCE_COOP_TABLE = {
    "cooperator": {"trusting": 0.95, "neutral": 0.80, "hostile": 0.55},
    "reciprocator": {"trusting": 0.90, "neutral": 0.70, "hostile": 0.30},
    "exploiter": {"trusting": 0.70, "neutral": 0.35, "hostile": 0.10},
    "random": {"trusting": 0.60, "neutral": 0.50, "hostile": 0.35},
}

_COOPERATE_STANCE_TRANSITION = np.asarray(
    [
        [0.90, 0.30, 0.05],
        [0.10, 0.60, 0.35],
        [0.00, 0.10, 0.60],
    ],
    dtype=float,
)
_DEFECT_STANCE_TRANSITION = np.asarray(
    [
        [0.10, 0.05, 0.02],
        [0.50, 0.35, 0.18],
        [0.40, 0.60, 0.80],
    ],
    dtype=float,
)


def normalize_distribution(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    total = float(array.sum())
    if total <= 0.0:
        raise ValueError("Distribution must have positive mass.")
    return array / total


def cooperation_evidence_strength(action: int, num_social_actions: int) -> float:
    """Map a binary or graded action to cooperative evidence in [0, 1]."""

    if num_social_actions <= 2:
        return 1.0 if int(action) == 0 else 0.0
    if num_social_actions <= 1:
        return 0.0
    clipped = min(max(int(action), 0), int(num_social_actions) - 1)
    return float(clipped / float(num_social_actions - 1))


def update_agent_character_posterior(prior: np.ndarray, cooperation_evidence_strength: float) -> np.ndarray:
    """Bayesian update over the partner's belief about the agent's character."""

    evidence = float(np.clip(cooperation_evidence_strength, 0.0, 1.0))
    prior_arr = normalize_distribution(prior)
    likelihood = evidence * _COOPERATE_LIKELIHOOD + (1.0 - evidence) * _DEFECT_LIKELIHOOD
    posterior = prior_arr * likelihood
    return normalize_distribution(posterior)


def posterior_to_stance(agent_character_posterior: np.ndarray) -> str:
    """Map posterior belief about the agent to a discrete stance label."""

    posterior = normalize_distribution(agent_character_posterior)
    p_cooperative = float(posterior[AGENT_CHARACTER_ORDER.index("cooperative")])
    if p_cooperative > 0.6:
        return "trusting"
    if p_cooperative < 0.3:
        return "hostile"
    return "neutral"


def interpolate_stance_transition(cooperation_evidence_strength: float) -> np.ndarray:
    """Blend stance transitions between cooperative and defect evidence."""

    evidence = float(np.clip(cooperation_evidence_strength, 0.0, 1.0))
    transition = evidence * _COOPERATE_STANCE_TRANSITION + (1.0 - evidence) * _DEFECT_STANCE_TRANSITION
    return transition / transition.sum(axis=0, keepdims=True)


def get_type_stance_cooperation_probability(type_name: str, stance_name: str) -> float:
    """Return the stance-conditioned probability that a partner cooperates."""

    try:
        return float(_TYPE_STANCE_COOP_TABLE[str(type_name)][str(stance_name)])
    except KeyError as exc:
        raise ValueError(f"Unknown type/stance combination: {type_name}/{stance_name}") from exc


def get_type_stance_cooperation_table(type_names: tuple[str, ...] | list[str]) -> np.ndarray:
    """Build a dense cooperation-probability table indexed by type then stance."""

    table = np.zeros((len(type_names), len(STANCE_ORDER)), dtype=float)
    for type_idx, type_name in enumerate(type_names):
        for stance_idx, stance_name in enumerate(STANCE_ORDER):
            table[type_idx, stance_idx] = get_type_stance_cooperation_probability(type_name, stance_name)
    return table
