import numpy as np

from affect_aif.agent.affect.state import AffectiveState


def _run_affective_sequence(state: AffectiveState, updates: list[tuple[np.ndarray, int]]) -> np.ndarray:
    history = [state.get_beta(0)]
    for predicted_action_probs, observed_action in updates:
        state.update(0, predicted_action_probs, observed_action)
        history.append(state.get_beta(0))
    return np.asarray(history, dtype=float)


def _continuous_fixed_point(alpha_charge: float, surprise: float, sigma_0_sq: float = 0.25) -> float:
    charge = alpha_charge * (sigma_0_sq - surprise**2)
    return float(1.0 / (1.0 + np.exp(-charge)))


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


def test_beta_converges_to_default_high_fixed_point_under_consistent_correct_predictions():
    affect = AffectiveState(num_partners=1, initial_beta=0.5)
    history = _run_affective_sequence(
        affect,
        [(np.array([0.95, 0.05]), 0) for _ in range(30)],
    )
    expected = _continuous_fixed_point(alpha_charge=3.0, surprise=0.05)
    assert history[-1] > history[0]
    np.testing.assert_allclose(history[-1], expected, atol=1e-5)
    assert np.all(np.diff(history) >= -1e-7)


def test_beta_converges_toward_one_under_consistent_correct_predictions_with_high_charge():
    affect = AffectiveState(num_partners=1, alpha_charge=100.0, initial_beta=0.5)
    history = _run_affective_sequence(
        affect,
        [(np.array([0.95, 0.05]), 0) for _ in range(30)],
    )
    assert history[-1] > 0.99
    assert np.all(np.diff(history) >= -1e-7)


def test_beta_converges_to_default_low_fixed_point_under_consistent_surprise():
    affect = AffectiveState(num_partners=1, initial_beta=0.5)
    history = _run_affective_sequence(
        affect,
        [(np.array([0.95, 0.05]), 1) for _ in range(30)],
    )
    expected = _continuous_fixed_point(alpha_charge=3.0, surprise=0.95)
    assert history[-1] < history[0]
    np.testing.assert_allclose(history[-1], expected, atol=1e-5)
    assert np.all(np.diff(history) <= 1e-7)


def test_beta_converges_toward_zero_under_consistent_surprise_with_high_charge():
    affect = AffectiveState(num_partners=1, alpha_charge=100.0, initial_beta=0.5)
    history = _run_affective_sequence(
        affect,
        [(np.array([0.95, 0.05]), 1) for _ in range(30)],
    )
    assert history[-1] < 1e-5
    assert np.all(np.diff(history) <= 1e-7)


def test_clinical_parameter_regimes_produce_distinct_beta_trajectories():
    updates = (
        [(np.array([0.95, 0.05]), 0) for _ in range(5)]
        + [(np.array([0.95, 0.05]), 1) for _ in range(5)]
        + [(np.array([0.95, 0.05]), 0) for _ in range(5)]
    )

    alexithymia = _run_affective_sequence(
        AffectiveState(num_partners=1, alpha_charge=0.1, lambda_smooth=0.6, initial_beta=0.5),
        updates,
    )
    borderline = _run_affective_sequence(
        AffectiveState(num_partners=1, alpha_charge=12.0, lambda_smooth=0.5, initial_beta=0.5),
        updates,
    )
    depression = _run_affective_sequence(
        AffectiveState(num_partners=1, alpha_charge=3.0, lambda_smooth=0.6, initial_beta=0.2),
        updates,
    )

    alex_range = np.ptp(alexithymia)
    borderline_range = np.ptp(borderline)
    depression_range = np.ptp(depression)

    assert alex_range < depression_range < borderline_range
    assert alexithymia[-1] > 0.5
    assert borderline.min() < 0.1 and borderline.max() > 0.9
    assert depression[0] < 0.3 and depression[-1] > 0.6
    assert not np.allclose(alexithymia, borderline)
    assert not np.allclose(borderline, depression)


def test_extreme_surprise_values_do_not_cause_numerical_instability():
    affect = AffectiveState(num_partners=1, alpha_charge=1000.0, initial_beta=0.5)
    updates = [
        (np.array([1.0, 0.0]), 0),
        (np.array([1.0, 0.0]), 1),
        (np.array([0.0, 1.0]), 0),
        (np.array([0.0, 1.0]), 1),
    ] * 10

    for predicted_action_probs, observed_action in updates:
        beta, epsilon = affect.update(0, predicted_action_probs, observed_action)
        assert np.isfinite(beta)
        assert np.isfinite(epsilon)

    assert np.isfinite(affect.get_all_betas()).all()
    assert np.isfinite(affect.get_prediction_errors()).all()
    assert 0.0 <= affect.get_beta(0) <= 1.0


from affect_aif.agent.affect.variational_state import VariationalAffectiveState
from affect_aif.agent.affective_agent import AffectiveAgent
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.generative_model.model import TrustGameModel


def test_variational_beta_starts_at_initial_value():
    affect = VariationalAffectiveState(num_partners=4, initial_beta=0.5)
    np.testing.assert_allclose(affect.get_beta(0), 0.5)
    np.testing.assert_allclose(affect.get_all_betas(), np.full(4, 0.5))


def test_variational_beta_increases_on_accurate_prediction():
    affect = VariationalAffectiveState(num_partners=1, initial_beta=0.5)
    affect.update(0, np.array([0.9, 0.1]), 0)
    assert affect.get_beta(0) > 0.5


def test_variational_beta_decreases_on_surprise():
    affect = VariationalAffectiveState(num_partners=1, initial_beta=0.5)
    affect.update(0, np.array([0.9, 0.1]), 1)
    assert affect.get_beta(0) < 0.5


def test_variational_beta_bounded():
    affect = VariationalAffectiveState(num_partners=1, initial_beta=0.5)
    for _ in range(50):
        affect.update(0, np.array([0.99, 0.01]), 0)
    assert affect.get_beta(0) <= 0.95

    for _ in range(50):
        affect.update(0, np.array([0.99, 0.01]), 1)
    assert 0.05 <= affect.get_beta(0) <= 0.95


def test_variational_posterior_is_valid_distribution():
    affect = VariationalAffectiveState(num_partners=1, initial_beta=0.5)
    affect.update(0, np.array([0.9, 0.1]), 0)
    posterior = affect.get_posterior(0)
    np.testing.assert_allclose(posterior.sum(), 1.0)
    assert np.all(posterior >= 0.0)


def test_variational_history_tracks_updates():
    affect = VariationalAffectiveState(num_partners=1, initial_beta=0.5)
    affect.update(0, np.array([0.9, 0.1]), 0)
    affect.update(0, np.array([0.8, 0.2]), 0)
    affect.update(0, np.array([0.7, 0.3]), 1)
    assert affect.get_history(0).shape == (4,)


def _make_variational_affective_agent(**kwargs):
    cfg = ExperimentConfig(num_rounds=2, calibration_episodes=1, num_replications=1, random_seed=0)
    model = TrustGameModel(cfg)
    A, B, C, D = model.get_matrices()
    return AffectiveAgent(
        A=A,
        B=B,
        C=C,
        D=D,
        model=model,
        planning_horizon=2,
        gamma=1.0,
        seed=0,
        reference_horizon=cfg.deep_horizon,
        max_policies=64,
        **kwargs,
    )


def test_affective_agent_variational_mode():
    agent = _make_variational_affective_agent(
        num_partners=4,
        mu=1.0,
        initial_beta=0.5,
        beta_mode="variational",
    )
    assert agent.beta_mode == "variational"
    assert agent.get_betas().shape == (4,)
