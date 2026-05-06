"""Tests for the native trust POMDP template."""

from __future__ import annotations

import pytest

from tasks.trust.pomdp import build_trust_pomdp_template


def test_payoff_mode_required():
    with pytest.raises(ValueError, match="payoff_mode"):
        build_trust_pomdp_template({"num_partners": 2}, planning_horizon=1)


def test_payoff_mode_binary_constructs():
    template = build_trust_pomdp_template({"payoff_mode": "binary", "num_partners": 2}, planning_horizon=1)

    assert template.payoff_mode == "binary"
    assert template.num_social_actions == 2


def test_payoff_mode_graded_constructs():
    template = build_trust_pomdp_template(
        {
            "payoff_mode": "graded",
            "num_partners": 2,
            "num_investment_levels": 6,
            "endowment": 10.0,
            "multiplier": 3.0,
        },
        planning_horizon=1,
    )

    assert template.payoff_mode == "graded"
    assert template.num_social_actions == 6


def test_unknown_payoff_mode_raises():
    with pytest.raises(ValueError, match="unknown payoff_mode"):
        build_trust_pomdp_template({"payoff_mode": "rocket-fuel", "num_partners": 2}, planning_horizon=1)


def test_variant_key_raises():
    with pytest.raises(ValueError, match="'variant' was removed"):
        build_trust_pomdp_template({"payoff_mode": "binary", "variant": "agent_choice"}, planning_horizon=1)


def test_model_class_key_raises():
    with pytest.raises(ValueError, match="'model_class' was removed"):
        build_trust_pomdp_template({"payoff_mode": "binary", "model_class": "custom"}, planning_horizon=1)


def test_binary_with_graded_keys_raises():
    with pytest.raises(ValueError, match="graded-only keys"):
        build_trust_pomdp_template({"payoff_mode": "binary", "num_investment_levels": 6}, planning_horizon=1)


def test_graded_with_binary_keys_raises():
    with pytest.raises(ValueError, match="binary-only keys"):
        build_trust_pomdp_template(
            {
                "payoff_mode": "graded",
                "num_investment_levels": 6,
                "mutual_coop": (3.0, 3.0),
            },
            planning_horizon=1,
        )
