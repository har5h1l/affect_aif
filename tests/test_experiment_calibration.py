from affect_aif.experiment.calibration import (
    build_sensitivity_specs,
    build_zero_calibration_summary,
    resolve_calibration_episodes,
)
from affect_aif.experiment.config import ExperimentConfig


def test_resolve_calibration_episodes_enforces_minimum_when_requested():
    cfg = ExperimentConfig(calibration_episodes=2, deep_horizon=4, shallow_horizon=2)

    assert resolve_calibration_episodes(cfg, enforce_minimum=False) == 2
    assert resolve_calibration_episodes(cfg, enforce_minimum=True) == 10


def test_build_zero_calibration_summary_matches_expected_shape():
    cfg = ExperimentConfig(calibration_episodes=7)

    summary = build_zero_calibration_summary(cfg)

    assert summary == {
        "requested_calibration_episodes": 7,
        "calibration_episodes": 0,
        "mean_abs_efe_per_step": 0.0,
        "derived_mu": 0.0,
    }


def test_build_sensitivity_specs_preserves_existing_parameter_order():
    cfg = ExperimentConfig(
        sensitivity_factors={
            "mu": [0.5, 1.0],
            "lambda_smooth": [0.4],
            "alpha_charge": [2.0],
            "sigma_0_sq": [0.1, 0.25],
        }
    )

    assert build_sensitivity_specs(cfg) == [
        ("mu", 0.5),
        ("mu", 1.0),
        ("lambda_smooth", 0.4),
        ("alpha_charge", 2.0),
        ("sigma_0_sq", 0.1),
        ("sigma_0_sq", 0.25),
    ]
