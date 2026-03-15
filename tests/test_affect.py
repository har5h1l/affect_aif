import numpy as np

from affect_aif.agent.affect.state import AffectiveState


def test_beta_starts_at_initial_value():
    affect = AffectiveState(num_partners=4, initial_beta=0.3)
    assert np.allclose(affect.get_all_betas(), 0.3)


def test_beta_increases_on_accurate_prediction():
    affect = AffectiveState(num_partners=1, initial_beta=0.5)
    beta, epsilon = affect.update(0, np.array([0.95, 0.05]), 0)
    assert beta > 0.5
    assert epsilon < 0.1


def test_beta_decreases_on_surprise_and_returns_raw_error():
    affect = AffectiveState(num_partners=1, initial_beta=0.5)
    beta, epsilon = affect.update(0, np.array([0.95, 0.05]), 1)
    assert beta < 0.5
    assert np.isclose(epsilon, 0.95)


def test_beta_bounded_0_to_1():
    affect = AffectiveState(num_partners=1, initial_beta=0.5)
    for _ in range(100):
        affect.update(0, np.array([0.01, 0.99]), 1)
    assert 0.0 <= affect.get_beta(0) <= 1.0
