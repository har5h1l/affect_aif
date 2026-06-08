import numpy as np
from runtime_helpers import build_runtime

from experiments.trust.config import ExperimentConfig
from tasks.trust.runtime import snapshot_partner_bank, update_partner_after_observation


def test_partner_bank_tracks_joint_type_and_stance_beliefs():
    runtime = build_runtime(ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0))
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
    runtime = build_runtime(ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0))
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


def test_factory_builds_native_runtimes_from_explicit_variants():
    config = ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0)

    affect = build_runtime(config, variant_id="affect", affect="precision", planning_horizon=4)
    lesioned = build_runtime(config, variant_id="lesioned", affect="tracked_only", planning_horizon=4)
    no_epistemic = build_runtime(config, variant_id="no_epistemic", affect="none", epistemic_value=False)

    assert affect.affect_mode == "normal"
    assert lesioned.affect_mode == "decouple"
    assert affect.planning_horizon == 4
    assert no_epistemic.partner_bank.beta is None
    assert all(agent.use_states_info_gain is False for agent in no_epistemic.partner_bank.agents)
