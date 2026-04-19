"""Regression tests for the payoff-modality likelihood fix."""

from __future__ import annotations

import numpy as np
import pytest


def test_payoff_modality_contributes_to_posterior():
    from trust.model import TrustGameModel

    model = TrustGameModel(
        {
            "payoff_mode": "binary",
            "observation_noise": 0.5,
            "mutual_coop": (10.0, 10.0),
            "sucker": (-10.0, 10.0),
            "temptation": (10.0, -10.0),
            "mutual_defect": (-10.0, -10.0),
        }
    )
    prior = np.full((model.num_types, model.num_stances), 1.0 / (model.num_types * model.num_stances))

    posterior = model.infer_joint_posterior(prior, observation=[0, 1], own_action=0)

    assert not np.allclose(posterior, prior, atol=0.05)


def test_observation_likelihood_requires_own_action():
    from trust.model import TrustGameModel

    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})

    with pytest.raises(ValueError, match="own_action"):
        model.observation_likelihood([0, 1], own_action=None)


def test_observation_likelihood_requires_both_modalities():
    from trust.model import TrustGameModel

    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})

    with pytest.raises(ValueError, match="both modalities"):
        model.observation_likelihood([0], own_action=0)


def test_joint_observation_likelihood_multiplies_both_modalities():
    from trust.model import TrustGameModel

    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})

    likelihood = model.joint_observation_likelihood(partner_action=0, payoff_obs=0, own_action=0)
    expected = np.asarray(model.A[0][0], dtype=float) * np.asarray(model.A[1][0, 0], dtype=float)

    np.testing.assert_allclose(likelihood, expected, atol=1e-12)
