import numpy as np

from experiment.config import ExperimentConfig


def _build_model(config):
    from trust.model import TrustGameModel

    return TrustGameModel(config)


def test_model_exposes_two_modalities_and_three_factors():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))

    assert len(model.A) == 2
    assert model.A[0].shape == (2, 4, 3)
    assert model.A[1].shape == (4, 2, 4, 3)

    assert len(model.B) == 3
    n_ctrl = int(np.prod(model.num_controls))
    assert model.B[0].shape == (4, 4, n_ctrl)
    assert model.B[1].shape == (3, 3, n_ctrl)
    assert model.B[2].shape == (2, 2, n_ctrl)

    assert len(model.C) == 2
    assert model.C[0].shape == (2,)
    assert model.C[1].shape == (4,)

    assert len(model.D) == 3
    assert model.D[2].shape == (2,)


def test_payoff_modality_marginalizes_partner_action_from_type_and_stance():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))

    trusting_cooperator_prob = model.A[0][0, 0, 0]
    payoff_levels = list(model.payoff_levels)
    idx_payoff_5 = payoff_levels.index(5.0)
    idx_payoff_1 = payoff_levels.index(1.0)

    assert np.isclose(model.A[1][idx_payoff_5, 1, 0, 0], trusting_cooperator_prob)
    assert np.isclose(model.A[1][idx_payoff_1, 1, 0, 0], 1.0 - trusting_cooperator_prob)


def test_own_action_transition_is_deterministic():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))

    cooperate = model.B[2][:, :, 0]
    defect = model.B[2][:, :, 1]

    np.testing.assert_allclose(cooperate, np.asarray([[1.0, 1.0], [0.0, 0.0]]))
    np.testing.assert_allclose(defect, np.asarray([[0.0, 0.0], [1.0, 1.0]]))


def test_social_posterior_multiplies_action_and_payoff_modalities():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))
    prior = np.full((model.num_types, model.num_stances), 1.0 / (model.num_types * model.num_stances))

    expected_likelihood = np.asarray(model.A[0][0], dtype=float) * np.asarray(model.A[1][2, 0], dtype=float)
    expected_posterior = expected_likelihood * prior
    expected_posterior /= expected_posterior.sum()

    posterior = model.infer_joint_posterior(prior, observation=[0, 2], own_action=0)

    np.testing.assert_allclose(posterior, expected_posterior)
