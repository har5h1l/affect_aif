import numpy as np

from benchmark.benchmark_config import AGENT_REGISTRY
from experiment.conditions import CONDITIONS, PRESET_CONDITIONS, get_condition_name
from experiment.config import ExperimentConfig
from experiment.factory import create_agent
from trust import AffectiveAgent, LesionedAgent, TrustGameAgent


def _build_model(config):
    from trust.model import TrustGameModel

    return TrustGameModel(config)


def _make_model_and_agent(agent_cls=TrustGameAgent, **kwargs):
    cfg = ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0)
    model = _build_model(cfg)
    agent = agent_cls(model=model, planning_horizon=2, gamma=1.0, seed=0, reference_horizon=8, max_policies=64, **kwargs)
    return model, agent


def test_base_agent_tracks_joint_type_and_stance_beliefs():
    model, agent = _make_model_and_agent()

    assert agent.partner_joint_beliefs.shape == (agent.num_partners, model.num_types, model.num_stances)
    assert agent.partner_joint_posteriors.shape == (agent.num_partners, model.num_types, model.num_stances)
    np.testing.assert_allclose(agent.partner_beliefs[0], model.D[0])
    np.testing.assert_allclose(agent.partner_stance_beliefs[0], model.D[1])


def test_observe_outcome_updates_stance_belief_after_surprising_defection():
    model, agent = _make_model_and_agent()
    cooperator = model.partner_type_names.index("cooperator")
    trusting = model.stance_names.index("trusting")
    hostile = model.stance_names.index("hostile")

    focused = np.zeros((model.num_types, model.num_stances), dtype=float)
    focused[cooperator] = np.asarray([0.7, 0.2, 0.1], dtype=float)
    agent.partner_joint_beliefs[0] = focused
    agent.partner_beliefs[0] = focused.sum(axis=1)
    agent.partner_stance_beliefs[0] = focused.sum(axis=0)
    agent.pending_prediction_partner = 0
    agent.pending_prediction_probs = np.asarray([0.95, 0.05], dtype=float)

    sucker_idx = model.payoff_levels.index(-1.0)
    agent.observe_outcome(partner_idx=0, observation=[1, sucker_idx], action_taken=0, partner_action=1, payoff=-1.0)

    stance_posterior = agent.partner_joint_posteriors[0].sum(axis=0)
    assert stance_posterior[hostile] > stance_posterior[trusting]


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


def test_factory_builds_agents_from_core_conditions_and_presets():
    config = ExperimentConfig(payoff_mode="binary", num_rounds=2, num_replications=1, random_seed=0)
    model = _build_model(config)

    tau4_affect = create_agent(config, 6, model, seed=0)
    lesioned = create_agent(config, "lesioned", model, seed=0)

    assert isinstance(tau4_affect, AffectiveAgent)
    assert isinstance(lesioned, LesionedAgent)
    assert tau4_affect.planning_horizon == 4
    assert get_condition_name(6) == "tau4_affect"


def test_benchmark_registry_reuses_condition_and_preset_names():
    assert AGENT_REGISTRY["tau4_affect"]["condition"] == 6
    assert AGENT_REGISTRY["lesioned"]["preset"] == "lesioned"
