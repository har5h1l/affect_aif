import numpy as np

from experiments.trust.config import ExperimentConfig


def _build_model(config):
    from tasks.trust.models import TrustGameModel

    return TrustGameModel(config)


def test_trust_model_exposes_stance_factor_and_joint_likelihood():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))

    assert model.num_stances == 3
    assert model.A[0].shape == (2, model.num_types, model.num_stances)
    n_ctrl = int(np.prod(model.num_controls))
    assert model.B[0].shape == (model.num_types, model.num_types, n_ctrl)
    assert model.B[1].shape == (model.num_stances, model.num_stances, n_ctrl)
    np.testing.assert_allclose(model.D[1], np.asarray([0.2, 0.6, 0.2], dtype=float))


def test_graded_model_uses_action_strength_for_stance_transitions():
    model = _build_model(
        ExperimentConfig(
            payoff_mode="graded",
            num_investment_levels=6,
            assignment_mode="agent_choice",
        )
    )

    low = model.stance_transition_for_action(0)
    high = model.stance_transition_for_action(5)
    mid = model.stance_transition_for_action(3)

    trusting = model.stance_names.index("trusting")
    hostile = model.stance_names.index("hostile")

    assert high[trusting, trusting] > low[trusting, trusting]
    assert high[hostile, hostile] < low[hostile, hostile]
    np.testing.assert_allclose(mid.sum(axis=0), 1.0, atol=1e-8)


def test_trust_model_predicts_partner_actions_from_type_and_stance_beliefs():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))
    belief = np.zeros((model.num_types, model.num_stances), dtype=float)
    cooperator = model.partner_type_names.index("cooperator")
    trusting = model.stance_names.index("trusting")
    belief[cooperator, trusting] = 1.0

    prediction = model.partner_action_distribution(belief)
    np.testing.assert_allclose(prediction, np.asarray([0.95, 0.05], dtype=float), atol=1e-8)
