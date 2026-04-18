import numpy as np

from experiment.config import ExperimentConfig
from agent.model.trust_game import TrustGameModel


def test_model_exposes_two_modalities_and_three_factors():
    model = TrustGameModel(ExperimentConfig())

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
    model = TrustGameModel(ExperimentConfig())

    trusting_cooperator_prob = model.A[0][0, 0, 0]
    payoff_levels = list(model.payoff_levels)
    idx_payoff_5 = payoff_levels.index(5.0)
    idx_payoff_1 = payoff_levels.index(1.0)

    assert np.isclose(model.A[1][idx_payoff_5, 1, 0, 0], trusting_cooperator_prob)
    assert np.isclose(model.A[1][idx_payoff_1, 1, 0, 0], 1.0 - trusting_cooperator_prob)


def test_own_action_transition_is_deterministic():
    model = TrustGameModel(ExperimentConfig())

    cooperate = model.B[2][:, :, 0]
    defect = model.B[2][:, :, 1]

    np.testing.assert_allclose(cooperate, np.asarray([[1.0, 1.0], [0.0, 0.0]]))
    np.testing.assert_allclose(defect, np.asarray([[0.0, 0.0], [1.0, 1.0]]))


def test_social_posterior_does_not_double_count_deterministic_payoff():
    model = TrustGameModel(ExperimentConfig())
    prior = np.full((model.num_types, model.num_stances), 1.0 / (model.num_types * model.num_stances))

    posterior_with_payoff = model.infer_joint_posterior(prior, observation=[0, 2], own_action=0)
    posterior_without_payoff = model.joint_observation_likelihood(0)
    posterior_without_payoff = posterior_without_payoff * prior
    posterior_without_payoff /= posterior_without_payoff.sum()

    np.testing.assert_allclose(posterior_with_payoff, posterior_without_payoff)


