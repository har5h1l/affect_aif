from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from experiment_spec_helpers import write_example_toml

from experiments.trust.factory import create_native_runtime_from_run
from experiments.trust.spec import ExpandedRunSpec, ExperimentSpec, load_experiment_specs


@pytest.fixture
def example_spec(tmp_path):
    return ExperimentSpec.from_toml(write_example_toml(tmp_path / "betrayal_choice.toml"))


def test_loads_hierarchical_toml_spec(tmp_path):
    spec = ExperimentSpec.from_toml(write_example_toml(tmp_path / "betrayal_choice.toml"))

    assert spec.hypothesis.id == "h5"
    assert spec.experiment.id == "betrayal_choice"
    assert spec.experiment.family == "trust"
    assert spec.scenario.assignment == "agent_choice"
    assert spec.variants[0].id == "affect"


def test_loads_suite_toml_into_experiment_specs(tmp_path):
    path = tmp_path / "alpha_suite.toml"
    path.write_text(
        """
[suite]
id = "alpha_sweep"
name = "Alpha sweep"

[defaults.hypothesis]
id = "exp_a"
name = "alpha_sweep"

[defaults.experiment]
family = "trust"
rounds = 50
replications = 2
seed = 100

[defaults.scenario]
payoff = "graded"
assignment = "agent_choice"
partners = 4
type_volatility = 0.0
initial_types = ["cooperator", "reciprocator", "exploiter", "random"]
initial_stances = ["trusting", "neutral", "trusting", "neutral"]

[[variants]]
id = "alpha_low"
affect = "precision"
planning_horizon = 4
alpha_charge = 0.5

[[variants]]
id = "alpha_high"
affect = "precision"
planning_horizon = 4
alpha_charge = 8.0

[[experiments]]
id = "open_graded"
seed_offset = 0

[[experiments]]
id = "betrayal"
seed_offset = 10000

[experiments.scenario]
initial_types = ["cooperator", "reciprocator", "cooperator", "random"]

[[experiments.scenario.type_switches]]
round = 21
partner = 0
to = "exploiter"

[[experiments.scenario.stance_switches]]
round = 21
partner = 0
to = "hostile"
""",
        encoding="utf-8",
    )

    specs = load_experiment_specs(path)

    assert [spec.experiment.id for spec in specs] == ["open_graded", "betrayal"]
    assert [spec.experiment.seed for spec in specs] == [100, 10100]
    assert specs[0].hypothesis.id == "exp_a"
    assert [variant.id for variant in specs[0].variants] == ["alpha_low", "alpha_high"]
    assert specs[1].scenario.type_switches[0].round == 21


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
    assert cfg.sigma_0_sq == pytest.approx(0.4804530139182014)
    assert not cfg.log_policy_traces


def test_variant_beta_prior_flows_to_runtime_config(tmp_path):
    path = write_example_toml(tmp_path / "prior.toml")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'planning_horizon = 4\n\n[[variants]]\nid = "no_affect"',
        'planning_horizon = 4\nbeta_prior = [0.4, 0.4, 0.15, 0.04, 0.01]\n\n[[variants]]\nid = "no_affect"',
    )
    path.write_text(text, encoding="utf-8")

    run = ExperimentSpec.from_toml(path).expand_runs()[0]
    cfg = run.to_runtime_config()

    assert cfg.initial_beta_prior == [0.4, 0.4, 0.15, 0.04, 0.01]


def test_scenario_partner_type_params_and_payoffs_flow_to_runtime_config(tmp_path):
    path = write_example_toml(tmp_path / "controlled_h1.toml")
    text = path.read_text(encoding="utf-8")
    params = (
        "{ "
        "reliable_cooperator = { cooperation_probabilities = "
        "{ trusting = 0.9, neutral = 0.9, hostile = 0.9 } }, "
        "reliable_exploiter = { cooperation_probabilities = "
        "{ trusting = 0.1, neutral = 0.1, hostile = 0.1 } }, "
        "random_partner = { cooperation_probabilities = "
        "{ trusting = 0.5, neutral = 0.5, hostile = 0.5 } }, "
        "volatile_partner = { cooperation_probabilities = "
        "{ trusting = 0.8, neutral = 0.5, hostile = 0.2 } } "
        "}"
    )
    text = text.replace(
        "type_volatility = 0.0\n",
        """
type_volatility = 0.0
partner_types = ["reliable_cooperator", "reliable_exploiter", "random_partner", "volatile_partner"]
"""
        + f"partner_type_params = {params}\n"
        + """
mutual_coop = [3.0, 3.0]
sucker = [3.0, 3.0]
temptation = [3.0, 3.0]
mutual_defect = [3.0, 3.0]
""",
    )
    path.write_text(text, encoding="utf-8")

    cfg = ExperimentSpec.from_toml(path).expand_runs()[0].to_runtime_config()

    assert cfg.partner_types == ["reliable_cooperator", "reliable_exploiter", "random_partner", "volatile_partner"]
    assert cfg.partner_type_params["reliable_exploiter"]["cooperation_probabilities"]["neutral"] == 0.1
    assert cfg.mutual_coop == (3.0, 3.0)
    assert cfg.sucker == (3.0, 3.0)
    assert cfg.temptation == (3.0, 3.0)
    assert cfg.mutual_defect == (3.0, 3.0)


def test_scenario_type_switches_flow_to_runtime_config(tmp_path):
    path = write_example_toml(tmp_path / "type_switch.toml")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "type_volatility = 0.0\n",
        'type_volatility = 0.0\ntype_switches = [{ round = 81, partner = 0, to = "exploiter" }]\n',
    )
    path.write_text(text, encoding="utf-8")

    cfg = ExperimentSpec.from_toml(path).expand_runs()[0].to_runtime_config()

    assert cfg.scheduled_type_switches == [{"round": 81, "partner_idx": 0, "to_type": "exploiter"}]


def test_rejects_mismatched_variant_beta_prior(tmp_path):
    path = write_example_toml(tmp_path / "bad_prior.toml")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'planning_horizon = 4\n\n[[variants]]',
        'planning_horizon = 4\nbeta_prior = [1.0]\n\n[[variants]]',
    )
    path.write_text(text, encoding="utf-8")

    with pytest.raises(ValueError, match="beta_prior"):
        ExperimentSpec.from_toml(path)


def test_runtime_debug_mode_enables_policy_trace_logging(tmp_path):
    path = write_example_toml(tmp_path / "debug.toml")
    path.write_text(
        path.read_text(encoding="utf-8")
        + """

[runtime]
profile = "debug"
""",
        encoding="utf-8",
    )
    spec = ExperimentSpec.from_toml(path)

    cfg = spec.expand_runs()[0].to_runtime_config()

    assert spec.runtime.profile == "debug"
    assert cfg.debug_mode
    assert cfg.log_policy_traces


def test_runtime_data_collection_profile_keeps_policy_traces_compact(tmp_path):
    path = write_example_toml(tmp_path / "data_collection.toml")
    path.write_text(
        path.read_text(encoding="utf-8")
        + """

[runtime]
profile = "data_collection"
""",
        encoding="utf-8",
    )
    spec = ExperimentSpec.from_toml(path)

    cfg = spec.expand_runs()[0].to_runtime_config()

    assert spec.runtime.profile == "data_collection"
    assert not cfg.debug_mode
    assert not cfg.log_policy_traces


def test_runtime_data_collection_profile_rejects_policy_trace_logging(tmp_path):
    path = write_example_toml(tmp_path / "bad_data_collection.toml")
    path.write_text(
        path.read_text(encoding="utf-8")
        + """

[runtime]
profile = "data_collection"
log_policy_traces = true
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="data_collection"):
        ExperimentSpec.from_toml(path)


def test_maintained_configs_declare_runtime_profile():
    config_root = Path(__file__).resolve().parents[1] / "configs"
    for path in sorted(config_root.glob("*/*.toml")) + sorted(config_root.glob("*/*/*.toml")):
        config_text = path.read_text(encoding="utf-8")
        assert 'profile = "data_collection"' in config_text or 'profile = "debug"' in config_text, path
        for spec in load_experiment_specs(path):
            assert spec.runtime.profile in {"data_collection", "debug"}, path
            if spec.runtime.profile == "data_collection":
                assert not spec.analysis.auto, path


def test_analysis_primary_default_is_slugified(tmp_path):
    path = write_example_toml(tmp_path / "default_primary.toml")
    text = path.read_text(encoding="utf-8")
    text = text.replace('name = "timescale_volatility"', 'name = "Timescale Volatility"')
    text = text.replace('primary = "h5_timescale_volatility"\n', "")
    path.write_text(text, encoding="utf-8")

    spec = ExperimentSpec.from_toml(path)

    assert spec.analysis.primary == "h5_timescale_volatility"


def test_factory_uses_variant_affect_mode(example_spec):
    run = example_spec.expand_runs()[0]

    runtime = create_native_runtime_from_run(run)

    assert runtime.variant_id == "affect"
    assert runtime.agent_kind == "affective"
    assert runtime.affect_mode == "normal"
    assert runtime.planning_horizon == 4
    assert runtime.partner_bank.beta is not None
    assert runtime.partner_bank.beta.sigma_0_sq == pytest.approx(0.4804530139182014)


def test_factory_uses_tracked_only_lesion(example_spec):
    run = example_spec.expand_runs()[0]
    lesioned = replace(run, variant=replace(run.variant, id="lesioned", affect="tracked_only"), variant_id="lesioned")

    runtime = create_native_runtime_from_run(lesioned)

    assert runtime.affect_mode == "decouple"


def test_spec_payload_roundtrip_preserves_expand_runs(example_spec):
    restored = ExperimentSpec.from_payload(example_spec.to_payload())

    original_runs = example_spec.expand_runs()
    restored_runs = restored.expand_runs()

    assert len(restored_runs) == len(original_runs)
    assert [run.variant_id for run in restored_runs] == [run.variant_id for run in original_runs]
    assert restored_runs[0].to_runtime_config().payoff_mode == original_runs[0].to_runtime_config().payoff_mode


def test_expanded_run_payload_normalizes_legacy_debug_runtime(example_spec):
    payload = example_spec.expand_runs()[0].to_payload()
    payload["runtime"] = {"debug_mode": True}

    restored = ExpandedRunSpec.from_payload(payload)

    assert restored.runtime.profile == "debug"
    assert restored.runtime.debug_mode
    assert restored.runtime.log_policy_traces


def test_stance_switch_spec_exports_runtime_dict():
    from experiments.trust.spec import StanceSwitchSpec

    switch = StanceSwitchSpec(round=4, partner=0, to="hostile")

    assert switch.to_runtime_dict() == {"round": 4, "partner_idx": 0, "to_stance": "hostile"}


def test_factory_uses_global_beta_shared_tracker(example_spec):
    run = example_spec.expand_runs()[0]
    global_beta = replace(
        run,
        variant=replace(run.variant, id="global_beta", affect="global_beta"),
        variant_id="global_beta",
    )

    runtime = create_native_runtime_from_run(global_beta)

    assert runtime.variant_id == "global_beta"
    assert runtime.agent_kind == "global_beta"
    assert runtime.affect_mode == "global"
    assert runtime.partner_bank.beta is not None
    assert runtime.partner_bank.beta.num_entities == 1
    assert len(runtime.partner_bank.agents) == global_beta.scenario.partners
