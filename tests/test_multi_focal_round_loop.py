"""End-to-end: multi-focal rounds with AffectiveAgents and base agents."""

from __future__ import annotations

import numpy as np

from experiment.factory import create_agents_from_multi_focal_config
from experiment.multi_focal_config import MultiFocalConfig
from experiment.multi_focal_runner import MultiFocalRunner


def _make_runner(M=2, assignment_mode="random", num_rounds=1, seed=0):
    cfg = MultiFocalConfig.from_dict(
        {
            "experiment_name": "round_loop",
            "assignment_mode": assignment_mode,
            "num_rounds": num_rounds,
            "random_seed": seed,
            "agents": [{"kind": "affective", "planning_horizon": 2}] * M,
        }
    )
    agents = create_agents_from_multi_focal_config(cfg, seed=seed)
    return MultiFocalRunner(cfg, agents, rng=np.random.default_rng(seed))


def test_one_round_random_M2_produces_two_rows():
    runner = _make_runner(M=2, assignment_mode="random", num_rounds=1)
    rows = runner.run()
    assert len(rows) == 2
    assert rows[0]["round"] == 0
    assert rows[1]["round"] == 0
    assert rows[0]["focal_idx"] == rows[1]["focal_idx"]
    assert rows[0]["engaged_partner_global_idx"] == rows[1]["engaged_partner_global_idx"]
    assert {rows[0]["agent_global_idx"], rows[1]["agent_global_idx"]} == {0, 1}
    assert {rows[0]["is_focal_this_round"], rows[1]["is_focal_this_round"]} == {True, False}


def test_three_rounds_M4_round_robin_focal_cycles():
    cfg = MultiFocalConfig.from_dict(
        {
            "experiment_name": "x",
            "assignment_mode": "random",
            "num_rounds": 4,
            "focal_selection": "round_robin",
            "agents": [{"kind": "base", "planning_horizon": 2}] * 4,
        }
    )
    agents = create_agents_from_multi_focal_config(cfg, seed=1)
    runner = MultiFocalRunner(cfg, agents, rng=np.random.default_rng(1))
    rows = runner.run()
    assert len(rows) == 8
    focal_per_round = {}
    for r in rows:
        focal_per_round.setdefault(r["round"], r["focal_idx"])
    assert focal_per_round == {0: 0, 1: 1, 2: 2, 3: 3}


def test_agent_choice_mode_runs_without_error():
    runner = _make_runner(M=3, assignment_mode="agent_choice", num_rounds=2, seed=7)
    rows = runner.run()
    assert len(rows) == 4
    for r in rows:
        assert r["engaged_partner_global_idx"] != r["focal_idx"]


def test_metrics_columns_propagate():
    runner = _make_runner(M=2, num_rounds=1, seed=2)
    rows = runner.run()
    expected_keys = {
        "round",
        "focal_idx",
        "engaged_partner_global_idx",
        "agent_global_idx",
        "agent_kind",
        "is_focal_this_round",
        "best_policy_idx",
        "selected_partner",
        "selected_action",
        "raw_action",
        "q_pi_entropy",
        "planning_cost",
        "planning_cost_ratio",
        "round_log_evidence",
        "cumulative_log_evidence",
        "mean_abs_step_efe",
    }
    assert expected_keys.issubset(rows[0].keys())
