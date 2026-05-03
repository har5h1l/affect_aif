"""Unit tests for joint action resolution (multi-focal F)."""

from __future__ import annotations

import pytest

from experiments.multifocal.joint_resolution import joint_resolve
from tasks.trust.models import TrustGameModel


@pytest.fixture
def binary_model():
    return TrustGameModel(
        {
            "payoff_mode": "binary",
            "num_partners": 1,
            "mutual_coop": (3.0, 3.0),
            "sucker": (-1.0, 5.0),
            "temptation": (5.0, -1.0),
            "mutual_defect": (1.0, 1.0),
        }
    )


@pytest.fixture
def graded_model():
    return TrustGameModel(
        {
            "payoff_mode": "graded",
            "num_partners": 1,
            "num_investment_levels": 6,
            "endowment": 10.0,
            "multiplier": 3.0,
        }
    )


def test_binary_mutual_cooperate_returns_3(binary_model):
    obs_idx, payoff = joint_resolve(my_action=0, partner_action=0, model=binary_model)
    assert payoff == pytest.approx(3.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(3.0)


def test_binary_sucker_returns_minus_1(binary_model):
    obs_idx, payoff = joint_resolve(my_action=0, partner_action=1, model=binary_model)
    assert payoff == pytest.approx(-1.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(-1.0)


def test_binary_temptation_returns_5(binary_model):
    obs_idx, payoff = joint_resolve(my_action=1, partner_action=0, model=binary_model)
    assert payoff == pytest.approx(5.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(5.0)


def test_binary_mutual_defect_returns_1(binary_model):
    obs_idx, payoff = joint_resolve(my_action=1, partner_action=1, model=binary_model)
    assert payoff == pytest.approx(1.0)
    assert binary_model.payoff_levels[obs_idx] == pytest.approx(1.0)


def test_graded_symmetric_max_invest(graded_model):
    """Graded tensor is (investment_level, partner_coop_defect, player); partner axis is binary."""
    max_level = graded_model.num_social_actions - 1
    obs_idx, payoff = joint_resolve(my_action=max_level, partner_action=0, model=graded_model)
    assert obs_idx >= 0
    levels = list(graded_model.payoff_levels)
    assert any(abs(level - payoff) < 1e-9 for level in levels)


def test_graded_zero_zero(graded_model):
    """Both invest 0 → both get endowment."""
    obs_idx, payoff = joint_resolve(my_action=0, partner_action=0, model=graded_model)
    assert payoff == pytest.approx(10.0)


def test_round_trip_swap_for_partner(binary_model):
    """Swap (my, partner) to compute the partner's payoff."""
    obs_my, p_my = joint_resolve(my_action=0, partner_action=1, model=binary_model)
    obs_par, p_par = joint_resolve(my_action=1, partner_action=0, model=binary_model)
    assert p_my == pytest.approx(-1.0)  # I cooperated, partner defected → sucker
    assert p_par == pytest.approx(5.0)  # partner defected, I cooperated → temptation
