import numpy as np

from experiments.trust.config import ExperimentConfig
from tasks.trust.payoffs import build_graded_payoff_matrix, decode_action, encode_action
from tasks.trust.types import PartnerType


def _build_model(config):
    from tasks.trust.models import TrustGameModel

    return TrustGameModel(config)


def test_a_matrix_column_normalized():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))
    partner_a = model.A[0]
    assert np.allclose(partner_a.sum(axis=0), 1.0)
    payoff_a = model.A[1]
    assert np.allclose(payoff_a.sum(axis=0), 1.0)


def test_b_matrix_column_normalized():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))
    assert np.allclose(model.B[0].sum(axis=0), 1.0)
    assert np.allclose(model.B[1].sum(axis=0), 1.0)


def test_c_and_d_shapes():
    model = _build_model(ExperimentConfig(payoff_mode="binary"))
    assert model.C[0].shape == (2,)
    assert model.C[1].shape == (4,)
    assert np.isclose(model.D[0].sum(), 1.0)
    assert np.isclose(model.D[1].sum(), 1.0)
    assert np.isclose(model.D[2].sum(), 1.0)


def test_partner_type_probabilities():
    cooperator = PartnerType(
        "cooperator", {"cooperation_probabilities": {"trusting": 0.95, "neutral": 0.8, "hostile": 0.55}}
    )
    reciprocator = PartnerType(
        "reciprocator",
        {"cooperation_probabilities": {"trusting": 0.9, "neutral": 0.7, "hostile": 0.3}},
    )
    exploiter = PartnerType(
        "exploiter", {"cooperation_probabilities": {"trusting": 0.7, "neutral": 0.35, "hostile": 0.1}}
    )
    assert np.isclose(cooperator.get_action_probability("neutral"), 0.8)
    assert reciprocator.get_action_probability("trusting") > reciprocator.get_action_probability("hostile")
    assert exploiter.get_action_probability("trusting") > exploiter.get_action_probability("hostile")


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
            encoded = encode_action(
                partner, action, num_partners=4, assignment_mode="agent_choice", num_social_actions=6
            )
            p, a = decode_action(encoded, num_partners=4, assignment_mode="agent_choice", num_social_actions=6)
            assert p == partner
            assert a == action


def test_graded_model_construction():
    cfg = ExperimentConfig(payoff_mode="graded", num_investment_levels=6, assignment_mode="agent_choice")
    model = _build_model(cfg)
    assert model.num_social_actions == 6
    assert model.payoff_matrix.shape == (6, 2, 2)
    assert model.num_controls == [24]  # 6 levels × 4 partners
    assert model.payoff_index_table.shape == (6, 2)
    # A, B, C, D should all be constructable
    A, B, C, D = model.get_matrices()
    assert A[0].shape[0] == 2  # partner action obs is binary
    assert B[0].shape[2] == 24  # transitions for each action
    assert D[0].shape[0] == model.num_types
    assert D[1].shape[0] == model.num_stances
    assert D[2].shape[0] == model.num_social_actions


def test_graded_a_matrix_column_normalized():
    cfg = ExperimentConfig(payoff_mode="graded", num_investment_levels=6, assignment_mode="agent_choice")
    model = _build_model(cfg)
    # Partner action A matrix
    assert np.allclose(model.A[0].sum(axis=0), 1.0)
    # Payoff A matrix — each column should sum to 1
    assert np.allclose(model.A[1].sum(axis=0), 1.0)
