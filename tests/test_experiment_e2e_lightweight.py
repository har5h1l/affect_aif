"""Lightweight end-to-end wiring tests for reusable experiment packages."""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.hypotheses import run_all_hypothesis_tests
from experiments.multifocal.config import MultiFocalConfig
from experiments.multifocal.runner import MultiFocalRunner
from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_agent, create_agents_from_multi_focal_config, create_env, create_model
from experiments.trust.logger import MetricLogger
from experiments.trust.runner import ExperimentRunner


def test_tiny_trust_config_constructs_and_runs_one_round():
    config = ExperimentConfig(
        num_partners=2,
        num_rounds=1,
        num_replications=1,
        conditions=[1],
        random_seed=0,
        max_policies=64,
        horizon_overrides={1: 1},
    )
    model = create_model(config)
    env = create_env(config, seed=0)
    agent = create_agent(config, 1, model, seed=0)

    context = env.reset()
    action = agent.plan_and_act(active_partner=context["active_partner"])
    result = env.step(action)
    agent.observe_outcome(
        partner_idx=result["partner_idx"],
        observation=result["observation"],
        action_taken=result["agent_action"],
        partner_action=result["partner_action"],
        payoff=result["agent_payoff"],
        true_partner_type=result["true_partner_type"],
        true_partner_stance=result["true_partner_stance"],
    )

    assert {"agent_payoff", "partner_idx", "observation"}.issubset(result)


def test_tiny_trust_runner_logs_pymdp_diagnostics():
    config = ExperimentConfig(
        num_partners=2,
        num_rounds=1,
        num_replications=1,
        conditions=[1],
        random_seed=0,
        max_policies=64,
        horizon_overrides={1: 1},
    )
    results = ExperimentRunner(config).run_all()

    assert "q_pi_entropy" in results.columns
    assert "partner_beliefs" in results.columns
    assert "selected_action" in results.columns
    assert "selected_partner" in results.columns


def test_logger_does_not_fallback_posteriors_to_decision_beliefs():
    logger = MetricLogger(num_rounds=1, num_partners=1)
    decision_beliefs = np.asarray([[[0.2, 0.8]]], dtype=float)
    logger.log_round(
        round_idx=0,
        condition=1,
        seed=0,
        agent_metrics={
            "inferred_type": "cooperator",
            "inferred_type_correct": True,
            "selected_partner": 0,
            "selected_action": 0,
            "best_policy_idx": 0,
            "q_pi_entropy": 0.0,
            "mean_abs_step_efe": np.nan,
            "planning_cost": 1.0,
            "planning_cost_ratio": 1.0,
            "betas": [np.nan],
            "prediction_errors": [np.nan],
            "reward_avgs": [np.nan],
            "G": [],
            "q_pi": [1.0],
            "best_policy_step_costs": [],
            "partner_beliefs": decision_beliefs,
            "partner_joint_beliefs": decision_beliefs,
            "partner_stance_beliefs": [[1.0]],
        },
        env_result={
            "partner_idx": 0,
            "active_partner_start": 0,
            "true_partner_type": "cooperator",
            "true_partner_stance": "friendly",
            "agent_action": 0,
            "raw_action": 0,
            "partner_action": 0,
            "agent_payoff": 1.0,
            "partner_payoff": 1.0,
            "type_switched": False,
            "stance_switched": False,
            "active_partner": 0,
            "true_types": ["cooperator"],
            "true_stances": ["friendly"],
        },
    )

    row = logger.records[0]
    assert row["partner_beliefs"] == decision_beliefs.tolist()
    assert row["partner_posteriors"] == []
    assert row["partner_joint_posteriors"] == []


def test_tiny_multifocal_round_loop_schema():
    config = MultiFocalConfig.from_dict(
        {
            "experiment_name": "tiny_multifocal",
            "num_rounds": 1,
            "random_seed": 0,
            "agents": [
                {"kind": "base", "planning_horizon": 1},
                {"kind": "base", "planning_horizon": 1},
            ],
        }
    )
    agents = create_agents_from_multi_focal_config(config, seed=0)
    runner = MultiFocalRunner(config, agents, rng=np.random.default_rng(0))

    rows = runner.run()

    assert len(rows) == 2
    assert {"round", "agent_global_idx", "focal_idx", "engaged_partner_global_idx"}.issubset(rows[0])
    assert {"selected_action", "planning_cost", "round_log_evidence"}.issubset(rows[0])


def test_analysis_runs_on_tiny_results():
    frame = pd.DataFrame(
        [
            {"condition": 1, "condition_name": "tau1_no_affect", "seed": 0, "round": 0, "payoff": 1.0},
            {"condition": 2, "condition_name": "tau1_affect", "seed": 0, "round": 0, "payoff": 2.0},
        ]
    )

    results = run_all_hypothesis_tests(frame)

    assert "h1" in results
    assert all("available" in payload for payload in results.values())
