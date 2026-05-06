from experiment_spec_helpers import write_example_toml

from experiments.trust.spec import ExperimentSpec


def test_sweeps_replace_legacy_sensitivity_helpers(tmp_path):
    spec = ExperimentSpec.from_toml(write_example_toml(tmp_path / "sweep.toml", sweeps=True))

    runs = spec.expand_runs()

    assert {run.variant_id for run in runs} >= {
        "affect__planning_horizon_1",
        "affect__planning_horizon_4",
        "no_affect__planning_horizon_1",
        "no_affect__planning_horizon_4",
    }
