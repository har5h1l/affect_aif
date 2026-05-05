from __future__ import annotations

import numpy as np
import pytest

from tasks.trust.affect import DiscreteBetaState
from tasks.trust.rollout import gamma_per_policy


def test_discrete_beta_state_starts_at_requested_level() -> None:
    state = DiscreteBetaState(num_entities=3, initial_beta=1.0)

    np.testing.assert_allclose(state.expected_beta(), np.array([1.0, 1.0, 1.0]))


def test_low_surprise_decreases_beta_rate() -> None:
    state = DiscreteBetaState(num_entities=1, initial_beta=1.0)

    before = state.expected_beta()[0]
    state.update(entity=0, surprise=0.0)
    after = state.expected_beta()[0]

    assert after < before


def test_high_surprise_increases_beta_rate() -> None:
    state = DiscreteBetaState(num_entities=1, initial_beta=1.0)

    before = state.expected_beta()[0]
    state.update(entity=0, surprise=1.0)
    after = state.expected_beta()[0]

    assert after > before


def test_discrete_beta_state_rejects_invalid_initialization() -> None:
    invalid_kwargs = [
        {"num_entities": 0},
        {"num_entities": 1, "beta_levels": []},
        {"num_entities": 1, "beta_levels": [0.5, np.inf]},
        {"num_entities": 1, "beta_levels": [0.0, 1.0]},
        {"num_entities": 1, "initial_beta": np.nan},
        {"num_entities": 1, "initial_beta": 0.0},
        {"num_entities": 1, "alpha_charge": np.inf},
        {"num_entities": 1, "alpha_charge": 0.0},
        {"num_entities": 1, "alpha_charge": -1.0},
        {"num_entities": 1, "sigma_0_sq": np.nan},
        {"num_entities": 1, "sigma_0_sq": 0.0},
        {"num_entities": 1, "persistence": 1.1},
    ]

    for kwargs in invalid_kwargs:
        with pytest.raises(ValueError):
            DiscreteBetaState(**kwargs)


def test_discrete_beta_state_rejects_nonfinite_surprise_without_state_change() -> None:
    state = DiscreteBetaState(num_entities=1, initial_beta=1.0)
    before_betas = state.expected_beta()
    before_history_len = len(state.beta_history)

    with pytest.raises(ValueError):
        state.update(entity=0, surprise=np.inf)

    np.testing.assert_allclose(state.expected_beta(), before_betas)
    assert len(state.beta_history) == before_history_len


def test_gamma_per_policy_uses_inverse_beta_expectation() -> None:
    first_partners = np.asarray([0, 1, 0, 1], dtype=int)
    precision_signal = np.asarray([0.5, 2.0], dtype=float)

    gamma_values = gamma_per_policy(
        gamma_base=1.0,
        first_partners=first_partners,
        precision_signal=precision_signal,
    )

    np.testing.assert_allclose(gamma_values, np.asarray([2.0, 0.5, 2.0, 0.5]))
