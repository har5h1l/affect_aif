import numpy as np

from tasks.trust.stance import (
    AGENT_CHARACTER_ORDER,
    STANCE_ORDER,
    cooperation_evidence_strength,
    get_type_stance_cooperation_probability,
    interpolate_stance_transition,
    posterior_to_stance,
    update_agent_character_posterior,
)


def test_posterior_to_stance_uses_trusting_and_hostile_thresholds():
    assert posterior_to_stance(np.asarray([0.61, 0.19, 0.20], dtype=float)) == "trusting"
    assert posterior_to_stance(np.asarray([0.30, 0.35, 0.35], dtype=float)) == "neutral"
    assert posterior_to_stance(np.asarray([0.29, 0.36, 0.35], dtype=float)) == "hostile"


def test_agent_character_update_moves_toward_cooperative_or_exploitative():
    prior = np.full(len(AGENT_CHARACTER_ORDER), 1.0 / len(AGENT_CHARACTER_ORDER), dtype=float)

    coop_posterior = update_agent_character_posterior(prior, cooperation_evidence_strength=1.0)
    defect_posterior = update_agent_character_posterior(prior, cooperation_evidence_strength=0.0)

    np.testing.assert_allclose(
        coop_posterior,
        np.asarray([0.56666667, 0.1, 0.33333333], dtype=float),
        atol=1e-6,
    )
    np.testing.assert_allclose(
        defect_posterior,
        np.asarray([0.1, 0.56666667, 0.33333333], dtype=float),
        atol=1e-6,
    )

    assert posterior_to_stance(coop_posterior) == "neutral"
    assert posterior_to_stance(defect_posterior) == "hostile"


def test_graded_cooperation_evidence_strength_is_normalized():
    assert cooperation_evidence_strength(action=0, num_social_actions=6) == 0.0
    assert cooperation_evidence_strength(action=5, num_social_actions=6) == 1.0
    assert cooperation_evidence_strength(action=3, num_social_actions=6) == 0.6


def test_type_cooperation_probabilities_are_stance_conditioned():
    assert get_type_stance_cooperation_probability("cooperator", "trusting") == 0.95
    assert get_type_stance_cooperation_probability("reciprocator", "neutral") == 0.70
    assert get_type_stance_cooperation_probability("exploiter", "hostile") == 0.10
    assert get_type_stance_cooperation_probability("random", "hostile") == 0.35


def test_interpolated_stance_transitions_preserve_asymmetry():
    cooperate = interpolate_stance_transition(cooperation_evidence_strength=1.0)
    defect = interpolate_stance_transition(cooperation_evidence_strength=0.0)
    mixed = interpolate_stance_transition(cooperation_evidence_strength=0.5)

    trusting = STANCE_ORDER.index("trusting")
    neutral = STANCE_ORDER.index("neutral")
    hostile = STANCE_ORDER.index("hostile")

    assert cooperate[trusting, neutral] > defect[trusting, neutral]
    assert defect[hostile, neutral] > cooperate[hostile, neutral]

    np.testing.assert_allclose(mixed.sum(axis=0), 1.0, atol=1e-8)
    assert cooperate[hostile, trusting] < mixed[hostile, trusting] < defect[hostile, trusting]
