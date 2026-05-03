"""Tests for ``aif.affect.beta.DiscreteBetaState``."""

from __future__ import annotations

import numpy as np

from aif.affect.beta import DiscreteBetaState

_RECORDED_SEQUENCE_BETAS = np.asarray(
    [
        [1.011254406317, 1.0, 1.0],
        [1.011254406317, 1.040168737557, 1.0],
        [0.977095838456, 1.040168737557, 1.0],
        [0.977095838456, 1.040168737557, 1.052939097553],
        [0.977095838456, 1.064711923651, 1.052939097553],
        [0.977095838456, 1.009445092173, 1.052939097553],
        [0.977095838456, 1.009445092173, 1.146040657021],
        [0.977095838456, 1.140682556281, 1.146040657021],
        [0.919456745673, 1.140682556281, 1.146040657021],
        [0.919456745673, 1.140682556281, 1.194890300481],
    ],
    dtype=float,
)


def test_entity_renamed_construction():
    state = DiscreteBetaState(
        num_entities=3,
        num_levels=5,
        persistence=0.8,
        alpha_charge=3.0,
        sigma_0_sq=0.25,
        initial_beta=1.0,
    )

    assert state.num_entities == 3
    assert state.get_all_betas().shape == (3,)


def test_update_uses_entity_idx_kwarg():
    state = DiscreteBetaState(
        num_entities=2,
        num_levels=5,
        persistence=0.8,
        alpha_charge=3.0,
        sigma_0_sq=0.25,
        initial_beta=1.0,
    )

    state.update(entity_idx=0, predicted_action_probs=np.asarray([0.7, 0.3]), observed_action=1)

    betas = state.get_all_betas()
    assert betas[0] != 1.0
    assert np.isclose(betas[1], 1.0)
    assert np.isclose(state.get_prediction_error(entity_idx=0), 0.7)


def test_aif_beta_matches_recorded_partner_api_baseline_sequence():
    rng = np.random.default_rng(42)
    state = DiscreteBetaState(
        num_entities=3,
        num_levels=5,
        persistence=0.8,
        alpha_charge=3.0,
        sigma_0_sq=0.25,
        initial_beta=1.0,
    )

    observed_rows = []
    for _ in range(10):
        entity_idx = int(rng.integers(0, 3))
        probs = np.asarray([rng.random(), 0.0], dtype=float)
        probs[1] = 1.0 - probs[0]
        observed_action = int(rng.integers(0, 2))
        state.update(entity_idx=entity_idx, predicted_action_probs=probs, observed_action=observed_action)
        observed_rows.append(state.get_all_betas())

    np.testing.assert_allclose(np.asarray(observed_rows, dtype=float), _RECORDED_SEQUENCE_BETAS, atol=1e-12)
