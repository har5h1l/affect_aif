"""Tests for AffectiveState and VariationalAffectiveState.

These classes (continuous EMA beta and variational beta) have been removed.
All tests that depended on them are skipped.
"""
import pytest

# All tests in this file depended on deleted classes:
# - AffectiveState (affect_aif/agent/affect/state.py - continuous EMA beta, superseded by discrete)
# - VariationalAffectiveState (affect_aif/agent/affect/variational_state.py - superseded by discrete)
# They are skipped rather than deleted so the test history is preserved.


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_starts_at_initial_value():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_increases_on_accurate_prediction():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_decreases_on_surprise_and_returns_raw_error():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_bounded_0_to_1():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_converges_to_default_high_fixed_point_under_consistent_correct_predictions():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_converges_toward_one_under_consistent_correct_predictions_with_high_charge():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_converges_to_default_low_fixed_point_under_consistent_surprise():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_beta_converges_toward_zero_under_consistent_surprise_with_high_charge():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_clinical_parameter_regimes_produce_distinct_beta_trajectories():
    pass


@pytest.mark.skip(reason="AffectiveState removed — superseded by DiscreteBetaState")
def test_extreme_surprise_values_do_not_cause_numerical_instability():
    pass


@pytest.mark.skip(reason="VariationalAffectiveState removed — superseded by DiscreteBetaState")
def test_variational_beta_starts_at_initial_value():
    pass


@pytest.mark.skip(reason="VariationalAffectiveState removed — superseded by DiscreteBetaState")
def test_variational_beta_increases_on_accurate_prediction():
    pass


@pytest.mark.skip(reason="VariationalAffectiveState removed — superseded by DiscreteBetaState")
def test_variational_beta_decreases_on_surprise():
    pass


@pytest.mark.skip(reason="VariationalAffectiveState removed — superseded by DiscreteBetaState")
def test_variational_beta_bounded():
    pass


@pytest.mark.skip(reason="VariationalAffectiveState removed — superseded by DiscreteBetaState")
def test_variational_posterior_is_valid_distribution():
    pass


@pytest.mark.skip(reason="VariationalAffectiveState removed — superseded by DiscreteBetaState")
def test_variational_history_tracks_updates():
    pass


@pytest.mark.skip(reason="VariationalAffectiveState removed — superseded by DiscreteBetaState")
def test_affective_agent_variational_mode():
    pass
