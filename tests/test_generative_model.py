import numpy as np

from affect_aif.experiment.config import ExperimentConfig
from affect_aif.generative_model.model import GradedTrustGameModel, TrustGameModel
from affect_aif.generative_model.partner_types import PartnerType
from affect_aif.generative_model.payoffs import build_graded_payoff_matrix, decode_action, encode_action


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


def test_graded_payoff_matrix_shape():
    matrix = build_graded_payoff_matrix(num_levels=6, endowment=10.0, multiplier=3.0)
    assert matrix.shape == (6, 2, 2)
    # Level 0: no investment — agent keeps endowment regardless
    assert matrix[0, 0, 0] == 10.0  # cooperate
    assert matrix[0, 1, 0] == 10.0  # defect
    # Level 5: full investment
    assert matrix[5, 0, 0] == 10.0 - 5 + 3.0 * 5 / 2  # = 12.5
    assert matrix[5, 1, 0] == 10.0 - 5  # = 5.0
    # Payoffs monotonically decrease with investment when partner defects
    for i in range(5):
        assert matrix[i, 1, 0] >= matrix[i + 1, 1, 0]


def test_graded_encode_decode_roundtrip():
    for partner in range(4):
        for action in range(6):
            encoded = encode_action(partner, action, num_partners=4, assignment_mode="agent_choice", num_social_actions=6)
            p, a = decode_action(encoded, num_partners=4, assignment_mode="agent_choice", num_social_actions=6)
            assert p == partner
            assert a == action


def test_graded_model_construction():
    cfg = ExperimentConfig(payoff_mode="graded", num_investment_levels=6, assignment_mode="agent_choice")
    model = GradedTrustGameModel(cfg)
    assert model.num_social_actions == 6
    assert model.payoff_matrix.shape == (6, 2, 2)
    assert model.num_controls == [24]  # 6 levels × 4 partners
    assert model.payoff_index_table.shape == (6, 2)
    # A, B, C, D should all be constructable
    A, B, C, D = model.get_matrices()
    assert A[0].shape[0] == 2  # partner action obs is binary
    assert B[0].shape[2] == 24  # transitions for each action
    assert D[0].shape[0] == model.num_types
    assert D[1].shape[0] == model.num_partners


def test_graded_a_matrix_column_normalized():
    cfg = ExperimentConfig(payoff_mode="graded", num_investment_levels=6, assignment_mode="agent_choice")
    model = GradedTrustGameModel(cfg)
    # Partner action A matrix
    assert np.allclose(model.A[0].sum(axis=0), 1.0)
    # Payoff A matrix — each column should sum to 1
    assert np.allclose(model.A[1].sum(axis=0), 1.0)
