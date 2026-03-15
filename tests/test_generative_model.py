import numpy as np

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.generative_model.model import TrustGameModel
from affect_aif.generative_model.partner_types import PartnerType


def test_a_matrix_column_normalized():
    model = TrustGameModel(ExperimentConfig())
    partner_a = model.A[0]
    assert np.allclose(partner_a.sum(axis=0), 1.0)
    payoff_a = model.A[1]
    assert np.allclose(payoff_a.sum(axis=0), 1.0)


def test_b_matrix_column_normalized():
    model = TrustGameModel(ExperimentConfig())
    assert np.allclose(model.B[0].sum(axis=0), 1.0)
    assert np.allclose(model.B[1].sum(axis=0), 1.0)


def test_c_and_d_shapes():
    model = TrustGameModel(ExperimentConfig())
    assert model.C[0].shape == (2,)
    assert model.C[1].shape == (4,)
    assert np.isclose(model.D[0].sum(), 1.0)
    assert np.isclose(model.D[1].sum(), 1.0)


def test_partner_type_probabilities():
    cooperator = PartnerType("cooperator", {"p_coop": 0.9})
    reciprocator = PartnerType("reciprocator", {"p_mirror": 0.85})
    exploiter = PartnerType("exploiter", {"p_coop_early": 0.85, "p_coop_late": 0.15, "switch_round": 4})
    assert np.isclose(cooperator.get_action_probability(0, 0), 0.9)
    assert reciprocator.get_action_probability(0, 0) > reciprocator.get_action_probability(1, 0)
    assert exploiter.get_action_probability(0, 0) > exploiter.get_action_probability(0, 8)
