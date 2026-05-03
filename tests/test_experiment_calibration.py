from experiments.trust.calibration import build_sensitivity_specs
from experiments.trust.config import ExperimentConfig


def test_build_sensitivity_specs_returns_all_four_parameters():
    cfg = ExperimentConfig(
        sensitivity_factors={
            "alpha_charge": [1.0, 2.0],
            "sigma_0_sq": [0.1],
            "beta_persistence": [0.8],
            "initial_beta": [0.5, 1.0],
        }
    )

    specs = build_sensitivity_specs(cfg)

    assert ("alpha_charge", 1.0) in specs
    assert ("alpha_charge", 2.0) in specs
    assert ("sigma_0_sq", 0.1) in specs
    assert ("beta_persistence", 0.8) in specs
    assert ("initial_beta", 0.5) in specs
    assert ("initial_beta", 1.0) in specs


def test_build_sensitivity_specs_ordering():
    cfg = ExperimentConfig(
        sensitivity_factors={
            "alpha_charge": [2.0],
            "sigma_0_sq": [0.1],
            "beta_persistence": [0.8],
            "initial_beta": [1.0],
        }
    )

    specs = build_sensitivity_specs(cfg)

    parameter_names = [name for name, _ in specs]
    assert parameter_names == ["alpha_charge", "sigma_0_sq", "beta_persistence", "initial_beta"]


def test_build_sensitivity_specs_empty_when_no_factors():
    cfg = ExperimentConfig(
        sensitivity_factors={
            "alpha_charge": [],
            "sigma_0_sq": [],
            "beta_persistence": [],
            "initial_beta": [],
        }
    )

    specs = build_sensitivity_specs(cfg)

    assert specs == []


def test_build_sensitivity_specs_uses_defaults_when_not_overridden():
    cfg = ExperimentConfig()

    specs = build_sensitivity_specs(cfg)

    parameter_names = [name for name, _ in specs]
    assert "alpha_charge" in parameter_names
    assert "sigma_0_sq" in parameter_names
    assert "beta_persistence" in parameter_names
    assert "initial_beta" in parameter_names
