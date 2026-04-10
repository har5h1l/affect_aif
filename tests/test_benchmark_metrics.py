"""Tests for benchmark common metrics on synthetic data."""

import numpy as np
import pandas as pd
import pytest

from benchmark.common_metrics import (
    adaptation_speed,
    cooperation_rate,
    cumulative_payoff,
    mean_payoff,
    partner_discrimination,
    social_welfare,
    type_identification_accuracy,
)


@pytest.fixture
def synthetic_results():
    """Create synthetic results resembling a trust game episode."""
    rng = np.random.default_rng(42)
    n = 100
    return pd.DataFrame({
        "condition": [1] * n,
        "seed": [0] * n,
        "round": list(range(n)),
        "partner_idx": rng.integers(0, 4, n).tolist(),
        "true_partner_type": rng.choice(
            ["cooperator", "reciprocator", "exploiter", "random"], n
        ).tolist(),
        "agent_action": rng.integers(0, 2, n).tolist(),
        "partner_action": rng.integers(0, 2, n).tolist(),
        "payoff": rng.choice([-1.0, 1.0, 3.0, 5.0], n).tolist(),
        "partner_payoff": rng.choice([-1.0, 1.0, 3.0, 5.0], n).tolist(),
        "inferred_type_correct": rng.choice([True, False], n).tolist(),
    })


@pytest.fixture
def cooperative_results():
    """Results where agent always cooperates."""
    n = 50
    return pd.DataFrame({
        "condition": [1] * n,
        "seed": [0] * n,
        "round": list(range(n)),
        "partner_idx": [0] * n,
        "true_partner_type": ["cooperator"] * n,
        "agent_action": [0] * n,
        "partner_action": [0] * n,
        "payoff": [3.0] * n,
        "partner_payoff": [3.0] * n,
        "inferred_type_correct": [True] * n,
    })


def test_cooperation_rate_all_cooperate(cooperative_results):
    assert cooperation_rate(cooperative_results) == 1.0


def test_cooperation_rate_all_defect():
    df = pd.DataFrame({"agent_action": [1, 1, 1, 1]})
    assert cooperation_rate(df) == 0.0


def test_cooperation_rate_mixed(synthetic_results):
    rate = cooperation_rate(synthetic_results)
    assert 0.0 <= rate <= 1.0


def test_cooperation_rate_grouped(synthetic_results):
    result = cooperation_rate(synthetic_results, group_by="true_partner_type")
    assert isinstance(result, pd.DataFrame)
    assert "cooperation_rate" in result.columns
    assert len(result) > 0


def test_cumulative_payoff(cooperative_results):
    assert cumulative_payoff(cooperative_results) == 150.0  # 50 * 3.0


def test_cumulative_payoff_grouped(synthetic_results):
    result = cumulative_payoff(synthetic_results, group_by="condition")
    assert isinstance(result, pd.DataFrame)
    assert "cumulative_payoff" in result.columns


def test_mean_payoff(cooperative_results):
    assert mean_payoff(cooperative_results) == 3.0


def test_type_identification_accuracy(cooperative_results):
    assert type_identification_accuracy(cooperative_results) == 1.0


def test_type_identification_accuracy_missing_column():
    df = pd.DataFrame({"agent_action": [0, 1]})
    assert np.isnan(type_identification_accuracy(df))


def test_social_welfare(cooperative_results):
    assert social_welfare(cooperative_results) == 300.0  # 50 * (3 + 3)


def test_partner_discrimination():
    df = pd.DataFrame({
        "true_partner_type": ["cooperator"] * 10 + ["exploiter"] * 10,
        "agent_action": [0] * 10 + [1] * 10,  # cooperate with coop, defect with exploit
    })
    disc = partner_discrimination(df)
    assert disc == 1.0  # maximal discrimination


def test_partner_discrimination_no_exploiters():
    df = pd.DataFrame({
        "true_partner_type": ["cooperator"] * 10,
        "agent_action": [0] * 10,
    })
    assert np.isnan(partner_discrimination(df))


def test_adaptation_speed():
    n = 50
    df = pd.DataFrame({
        "round": list(range(n)),
        "inferred_type_correct": [False] * 20 + [True] * 30,
    })
    speed = adaptation_speed(df, switch_round=15, accuracy_threshold=0.8, window=5)
    assert isinstance(speed, float)
    assert speed >= 0


def test_adaptation_speed_never_recovers():
    n = 50
    df = pd.DataFrame({
        "round": list(range(n)),
        "inferred_type_correct": [False] * n,
    })
    speed = adaptation_speed(df, switch_round=10, accuracy_threshold=0.8, window=5)
    assert np.isnan(speed)
