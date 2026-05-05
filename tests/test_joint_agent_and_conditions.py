import numpy as np

from benchmarks.core.benchmark_config import AGENT_REGISTRY
from experiments.trust.conditions import CONDITIONS, PRESET_CONDITIONS, get_condition_name
from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_native_runtime
from tasks.trust.runtime import snapshot_partner_bank, update_partner_after_observation


def test_partner_bank_tracks_joint_type_and_stance_beliefs():
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0),
        condition=1,
        seed=0,
    )
    snapshot = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template)

    assert snapshot.partner_joint_beliefs.shape == (
        runtime.template.num_partners,
        runtime.template.num_types,
        runtime.template.num_stances,
    )
    assert snapshot.partner_joint_posteriors.shape == snapshot.partner_joint_beliefs.shape
    np.testing.assert_allclose(snapshot.partner_type_beliefs[0], np.asarray(runtime.template.D[0], dtype=float))
    np.testing.assert_allclose(snapshot.partner_stance_beliefs[0], np.asarray(runtime.template.D[1], dtype=float))


def test_observation_update_changes_active_partner_stance_belief():
    runtime = create_native_runtime(
        ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0),
        condition=1,
        seed=0,
    )
    before = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template).partner_stance_beliefs[0]
    sucker_idx = runtime.template.payoff_levels.index(-1.0)

    update_partner_after_observation(
        bank=runtime.partner_bank,
        template=runtime.template,
        partner_idx=0,
        obs=[1, sucker_idx],
        own_action=0,
    )
    after = snapshot_partner_bank(bank=runtime.partner_bank, template=runtime.template).partner_stance_beliefs[0]

    assert not np.allclose(after, before)


def test_core_conditions_are_the_depth_affect_matrix():
    expected = {
        1: "tau1_no_affect",
        2: "tau1_affect",
        3: "tau2_no_affect",
        4: "tau2_affect",
        5: "tau4_no_affect",
        6: "tau4_affect",
        7: "tau8_no_affect",
        8: "tau8_affect",
    }
    assert {condition_id: CONDITIONS[condition_id].name for condition_id in expected} == expected


def test_named_presets_cover_lesion_control_and_clinical_variants():
    assert {"lesioned", "no_epistemic", "alexithymia", "borderline", "depression"} <= set(PRESET_CONDITIONS)


def test_factory_builds_native_runtimes_from_core_conditions_and_presets():
    config = ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0)

    tau4_affect = create_native_runtime(config, 6, seed=0)
    lesioned = create_native_runtime(config, "lesioned", seed=0)

    assert tau4_affect.affect_mode == "normal"
    assert lesioned.affect_mode == "decouple"
    assert tau4_affect.planning_horizon == 4
    assert get_condition_name(6) == "tau4_affect"


def test_benchmark_registry_reuses_condition_and_preset_names():
    assert AGENT_REGISTRY["tau4_affect"]["condition"] == 6
    assert AGENT_REGISTRY["lesioned"]["preset"] == "lesioned"
