"""Regression tests for the payoff-modality likelihood fix."""

from __future__ import annotations

import numpy as np
import pytest

from tasks.trust.pomdp import (
    build_trust_pomdp_template,
    infer_joint_posterior,
    joint_observation_likelihood,
    observation_likelihood,
)


def test_payoff_modality_contributes_to_posterior():
    template = build_trust_pomdp_template(
        {
            "payoff_mode": "binary",
            "observation_noise": 0.5,
            "mutual_coop": (10.0, 10.0),
            "sucker": (-10.0, 10.0),
            "temptation": (10.0, -10.0),
            "mutual_defect": (-10.0, -10.0),
        },
        planning_horizon=1,
    )
    prior = np.full((template.num_types, template.num_stances), 1.0 / (template.num_types * template.num_stances))

    posterior = infer_joint_posterior(template, prior, observation=[0, 1], own_action=0)

    assert not np.allclose(posterior, prior, atol=0.05)


def test_observation_likelihood_requires_own_action():
    template = build_trust_pomdp_template({"payoff_mode": "binary", "num_partners": 2}, planning_horizon=1)

    with pytest.raises(ValueError, match="own_action"):
        observation_likelihood(template, [0, 1], own_action=None)


def test_observation_likelihood_requires_both_modalities():
    template = build_trust_pomdp_template({"payoff_mode": "binary", "num_partners": 2}, planning_horizon=1)

    with pytest.raises(ValueError, match="both modalities"):
        observation_likelihood(template, [0], own_action=0)


def test_joint_observation_likelihood_multiplies_both_modalities():
    template = build_trust_pomdp_template({"payoff_mode": "binary", "num_partners": 2}, planning_horizon=1)

    likelihood = joint_observation_likelihood(template, partner_action=0, payoff_obs=0, own_action=0)
    expected = np.asarray(template.A[0][0, :, :, 0], dtype=float) * np.asarray(template.A[1][0, :, :, 0], dtype=float)

    np.testing.assert_allclose(likelihood, expected, atol=1e-12)
