from __future__ import annotations

from dataclasses import replace

import pytest
from experiment_spec_helpers import write_benchmark_toml, write_example_toml

from experiments.trust.factory import create_native_runtime_from_run
from experiments.trust.spec import ExperimentSpec


@pytest.fixture
def example_spec(tmp_path):
    return ExperimentSpec.from_toml(write_example_toml(tmp_path / "betrayal_choice.toml"))


def test_loads_hierarchical_toml_spec(tmp_path):
    spec = ExperimentSpec.from_toml(write_example_toml(tmp_path / "betrayal_choice.toml"))

    assert spec.hypothesis.id == "h3"
    assert spec.experiment.id == "betrayal_choice"
    assert spec.experiment.family == "trust"
    assert spec.scenario.assignment == "agent_choice"
    assert spec.variants[0].id == "affect"


def test_loads_benchmark_family_add_on(tmp_path):
    spec = ExperimentSpec.from_toml(write_benchmark_toml(tmp_path / "benchmark_smoke.toml"))

    assert spec.experiment.family == "benchmark"
    assert spec.benchmark is not None
    assert spec.benchmark.backends == ("trust",)
    assert spec.benchmark.agents == ("affect", "random")
    assert spec.benchmark.trust["scenario"] == "resource_sharing"


def test_benchmark_family_requires_benchmark_section(tmp_path):
    path = write_benchmark_toml(tmp_path / "missing.toml", include_benchmark=False)

    with pytest.raises(ValueError, match="benchmark"):
        ExperimentSpec.from_toml(path)


def test_trust_family_rejects_benchmark_section(tmp_path):
    path = write_example_toml(tmp_path / "trust.toml")
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text
        + """

[benchmark]
backends = ["trust"]
agents = ["affect"]
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="benchmark"):
        ExperimentSpec.from_toml(path)


def test_rejects_legacy_condition_keys(tmp_path):
    path = tmp_path / "legacy.toml"
    path.write_text(
        """
[hypothesis]
id = "h0"
name = "openness"

[experiment]
id = "legacy"
rounds = 10
replications = 1
seed = 1

[scenario]
payoff = "binary"
assignment = "random"
partners = 4

conditions = [1, 2]
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="conditions"):
        ExperimentSpec.from_toml(path)


def test_expands_variants_to_runs(example_spec):
    spec = replace(example_spec, variants=(example_spec.variants[0],))

    runs = spec.expand_runs()

    assert [run.variant_id for run in runs] == ["affect", "affect", "affect"]
    assert [run.seed for run in runs] == [42, 43, 44]


def test_expands_planning_horizon_sweep(tmp_path):
    spec = ExperimentSpec.from_toml(write_example_toml(tmp_path / "h0_sweep.toml", sweeps=True))

    ids = {run.variant_id for run in spec.expand_runs()}

    assert "affect__planning_horizon_1" in ids
    assert "affect__planning_horizon_4" in ids
    assert "no_affect__planning_horizon_1" in ids


def test_expanded_run_builds_runtime_config(example_spec):
    run = example_spec.expand_runs()[0]

    cfg = run.to_runtime_config()

    assert cfg.payoff_mode == "binary"
    assert cfg.assignment_mode == "agent_choice"
    assert cfg.num_rounds == 120
    assert cfg.p_switch == 0.0
    assert cfg.gamma == 1.0
    assert cfg.alpha_charge == 3.0
    assert not cfg.log_policy_traces


def test_runtime_debug_mode_enables_policy_trace_logging(tmp_path):
    path = write_example_toml(tmp_path / "debug.toml")
    path.write_text(
        path.read_text(encoding="utf-8")
        + """

[runtime]
debug_mode = true
""",
        encoding="utf-8",
    )
    spec = ExperimentSpec.from_toml(path)

    cfg = spec.expand_runs()[0].to_runtime_config()

    assert cfg.debug_mode
    assert cfg.log_policy_traces


def test_analysis_primary_default_is_slugified(tmp_path):
    path = write_example_toml(tmp_path / "default_primary.toml")
    text = path.read_text(encoding="utf-8")
    text = text.replace('name = "stress_response"', 'name = "Stress Response"')
    text = text.replace('primary = "h3_stress_response"\n', "")
    path.write_text(text, encoding="utf-8")

    spec = ExperimentSpec.from_toml(path)

    assert spec.analysis.primary == "h3_stress_response"


def test_factory_uses_variant_affect_mode(example_spec):
    run = example_spec.expand_runs()[0]

    runtime = create_native_runtime_from_run(run)

    assert runtime.variant_id == "affect"
    assert runtime.agent_kind == "affective"
    assert runtime.affect_mode == "normal"
    assert runtime.planning_horizon == 4


def test_factory_uses_tracked_only_lesion(example_spec):
    run = example_spec.expand_runs()[0]
    lesioned = replace(run, variant=replace(run.variant, id="lesioned", affect="tracked_only"), variant_id="lesioned")

    runtime = create_native_runtime_from_run(lesioned)

    assert runtime.affect_mode == "decouple"
