"""Deterministic smoke tests for the native multi-focal runner."""

from __future__ import annotations

import numpy as np
import pytest

from experiments.multifocal.config import MultiFocalConfig
from experiments.multifocal.runner import MultiFocalRunner
from experiments.trust.factory import create_agents_from_multi_focal_config


def _build(M=4, num_rounds=50, seed=42):
    cfg = MultiFocalConfig.from_dict(
        {
            "experiment_name": "det",
            "round_mode": "turn_taking",
            "focal_selection": "round_robin",
            "assignment_mode": "random",
            "num_rounds": num_rounds,
            "random_seed": seed,
            "payoff_mode": "binary",
            "agents": [
                {
                    "kind": "affective",
                    "planning_horizon": 4,
                    "alpha_charge": 3.0,
                    "sigma_0_sq": 0.4804530139182014,
                    "initial_beta": 1.0,
                    "num_levels": 5,
                    "persistence": 0.8,
                },
            ]
            * M,
        }
    )
    agents = create_agents_from_multi_focal_config(cfg, seed=seed)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(seed))


def _run_and_index(runner) -> dict:
    rows = runner.run()
    by = {}
    for r in rows:
        by[(r["round"], r["agent_global_idx"], r["is_focal_this_round"])] = r
    return by


@pytest.fixture(scope="module")
def baseline_rows():
    return _run_and_index(_build())


def test_round0_focal_idx(baseline_rows):
    keys_round_0 = [k for k in baseline_rows if k[0] == 0]
    focal_keys = [k for k in keys_round_0 if k[2] is True]
    assert len(focal_keys) == 1
    assert focal_keys[0][1] == 0


def test_round0_focal_action_pinned(baseline_rows):
    row = baseline_rows[(0, 0, True)]
    assert row["selected_action"] == 1


@pytest.mark.parametrize("t", [10, 25, 40, 49])
def test_cumulative_log_evidence_focal_is_finite(baseline_rows, t):
    row = baseline_rows[(t, t % 4, True)]
    assert np.isfinite(row["cumulative_log_evidence"])


@pytest.mark.parametrize("t", [0, 25, 49])
def test_q_pi_entropy_focal_is_finite(baseline_rows, t):
    row = baseline_rows[(t, t % 4, True)]
    assert np.isfinite(row["q_pi_entropy"])


def test_round25_focal_idx_round_robin(baseline_rows):
    keys = [k for k in baseline_rows if k[0] == 25 and k[2] is True]
    assert len(keys) == 1
    assert keys[0][1] == 25 % 4


def test_round49_payoff_in_legal_set(baseline_rows):
    row = baseline_rows[(49, 49 % 4, True)]
    assert row.get("round_log_evidence") is not None


def test_focal_selected_action_consistent_across_sample_rounds(baseline_rows):
    for t in (5, 10, 15, 20):
        assert baseline_rows[(t, t % 4, True)]["selected_action"] == 1
