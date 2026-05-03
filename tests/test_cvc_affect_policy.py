"""Tests for the CvC affect policy beta-update logic.

These test the pure-Python beta tracking without requiring mettagrid.
"""

from benchmarks.cvc.beta import (
    ALPHA_CHARGE,
    COOPERATE_THRESHOLD,
    INDEPENDENT_THRESHOLD,
    INITIAL_BETA,
    LAMBDA_SMOOTH,
    SIGMA_0_SQ,
    sigmoid,
    update_beta,
)


class TestSigmoid:
    def test_zero(self):
        assert sigmoid(0.0) == 0.5

    def test_large_positive(self):
        assert sigmoid(100.0) > 0.99

    def test_large_negative(self):
        assert sigmoid(-100.0) < 0.01

    def test_symmetry(self):
        assert abs(sigmoid(2.0) + sigmoid(-2.0) - 1.0) < 1e-10


class TestUpdateBeta:
    def test_perfect_prediction_increases_beta(self):
        """When prediction matches exactly, surprise=0, beta should increase."""
        new_beta = update_beta((5, 5), (5, 5), 0.5, max_distance=20.0)
        assert new_beta > 0.5

    def test_large_error_decreases_beta(self):
        """When prediction is far off, surprise is high, beta should decrease."""
        new_beta = update_beta((0, 0), (10, 10), 0.5, max_distance=20.0)
        assert new_beta < 0.5

    def test_moderate_error_near_sigma0(self):
        """When surprise^2 ~ sigma_0_sq, charge ~ 0, beta stays near 0.5."""
        # surprise = sqrt(0.25) = 0.5, distance/max_distance = 0.5
        # With max_distance=20, distance = 10
        new_beta = update_beta((0, 0), (5, 5), 0.5, max_distance=20.0)
        assert abs(new_beta - 0.5) < 0.1

    def test_ema_smoothing(self):
        """Beta update respects lambda smoothing — doesn't jump instantly."""
        new_beta = update_beta((0, 0), (0, 0), 0.2, max_distance=20.0)
        squashed = sigmoid(ALPHA_CHARGE * SIGMA_0_SQ)
        expected = LAMBDA_SMOOTH * 0.2 + (1.0 - LAMBDA_SMOOTH) * squashed
        assert abs(new_beta - expected) < 1e-10

    def test_max_distance_zero_safe(self):
        """Handles max_distance=0 without division by zero."""
        new_beta = update_beta((0, 0), (1, 1), 0.5, max_distance=0.0)
        assert 0.0 < new_beta < 1.0

    def test_repeated_perfect_prediction_converges_high(self):
        """Repeatedly perfect predictions push beta toward 1."""
        beta = 0.5
        for _ in range(50):
            beta = update_beta((3, 3), (3, 3), beta, max_distance=20.0)
        assert beta > 0.65

    def test_repeated_bad_prediction_converges_low(self):
        """Repeatedly wrong predictions push beta toward 0."""
        beta = 0.5
        for _ in range(50):
            beta = update_beta((0, 0), (15, 15), beta, max_distance=30.0)
        assert beta < 0.15


class TestConstants:
    def test_thresholds_ordered(self):
        assert INDEPENDENT_THRESHOLD < COOPERATE_THRESHOLD

    def test_initial_beta_in_range(self):
        assert 0.0 < INITIAL_BETA < 1.0

    def test_lambda_in_range(self):
        assert 0.0 < LAMBDA_SMOOTH < 1.0
