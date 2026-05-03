"""Tests for the canonical ``trust.model.TrustGameModel``."""

from __future__ import annotations

import pytest


def test_payoff_mode_required():
    from tasks.trust.models import TrustGameModel

    with pytest.raises(ValueError, match="payoff_mode"):
        TrustGameModel({"num_partners": 2})


def test_payoff_mode_binary_constructs():
    from tasks.trust.models import TrustGameModel

    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})

    assert model.payoff_mode == "binary"
    assert model.num_social_actions == 2


def test_payoff_mode_graded_constructs():
    from tasks.trust.models import TrustGameModel

    model = TrustGameModel(
        {
            "payoff_mode": "graded",
            "num_partners": 2,
            "num_investment_levels": 6,
            "endowment": 10.0,
            "multiplier": 3.0,
        }
    )

    assert model.payoff_mode == "graded"
    assert model.num_social_actions == 6


def test_unknown_payoff_mode_raises():
    from tasks.trust.models import TrustGameModel

    with pytest.raises(ValueError, match="unknown payoff_mode"):
        TrustGameModel({"payoff_mode": "rocket-fuel", "num_partners": 2})


def test_variant_key_raises():
    from tasks.trust.models import TrustGameModel

    with pytest.raises(ValueError, match="'variant' was removed"):
        TrustGameModel({"payoff_mode": "binary", "variant": "agent_choice"})


def test_model_class_key_raises():
    from tasks.trust.models import TrustGameModel

    with pytest.raises(ValueError, match="'model_class' was removed"):
        TrustGameModel({"payoff_mode": "binary", "model_class": "TrustGameModel"})


def test_binary_with_graded_keys_raises():
    from tasks.trust.models import TrustGameModel

    with pytest.raises(ValueError, match="graded-only keys"):
        TrustGameModel({"payoff_mode": "binary", "num_investment_levels": 6})


def test_graded_with_binary_keys_raises():
    from tasks.trust.models import TrustGameModel

    with pytest.raises(ValueError, match="binary-only keys"):
        TrustGameModel(
            {
                "payoff_mode": "graded",
                "num_investment_levels": 6,
                "mutual_coop": (3.0, 3.0),
            }
        )


def test_build_a_returns_fresh_copy_each_call():
    from tasks.trust.models import TrustGameModel

    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    first = model.build_A()
    second = model.build_A()

    first[0][0, 0, 0] = 999.0

    assert second[0][0, 0, 0] != 999.0


def test_build_b_returns_fresh_copy_each_call():
    from tasks.trust.models import TrustGameModel

    model = TrustGameModel({"payoff_mode": "binary", "num_partners": 2})
    first = model.build_B()
    second = model.build_B()

    first[0][0, 0, 0] = 999.0

    assert second[0][0, 0, 0] != 999.0
