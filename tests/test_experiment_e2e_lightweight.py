"""Lightweight end-to-end wiring tests for reusable experiment packages."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
from runtime_helpers import build_runtime

from analysis.hypotheses import run_all_hypothesis_tests
from experiments.multifocal.config import MultiFocalConfig
from experiments.multifocal.runner import MultiFocalRunner
from experiments.trust.config import ExperimentConfig
from experiments.trust.factory import create_agents_from_multi_focal_config, create_env
from experiments.trust.logger import MetricLogger
from experiments.trust.runner import ExperimentRunner
from experiments.trust.spec import RuntimeSpec
from tasks.trust.runtime import (
    select_decision,
    update_beta_after_observation,
    update_partner_after_observation,
)

MANUSCRIPT_DATA_COLLECTION_COLUMNS = {
    "seed",
    "round",
    "partner_idx",
    "active_partner",
    "true_partner_type",
    "true_partner_stance",
    "agent_action",
    "raw_action",
    "partner_action",
    "payoff",
    "partner_payoff",
    "type_switched",
    "stance_switched",
    "switch_kind",
    "active_partner_next",
    "true_types",
    "true_stances",
    "inferred_type",
    "inferred_type_correct",
    "inferred_stance",
    "inferred_stance_correct",
    "inferred_joint_correct",
    "selected_partner",
    "selected_action",
    "best_policy_idx",
    "q_pi_entropy",
    "mean_abs_step_efe",
    "planning_cost",
    "planning_cost_ratio",
    "betas",
    "local_betas",
    "global_beta",
    "terminal_signal",
    "prediction_errors",
    "predictive_log_lik",
    "round_log_evidence",
    "cumulative_log_evidence",
    "hypothesis_id",
    "experiment_id",
    "variant_id",
    "replication",
    "config_name",
}

DEBUG_ONLY_COLUMNS = {
    "G",
    "q_pi",
    "best_policy_step_costs",
    "partner_beliefs",
    "partner_posteriors",
    "partner_joint_beliefs",
    "partner_joint_posteriors",
    "partner_stance_beliefs",
}


def test_tiny_trust_config_constructs_and_runs_one_round():
    config = ExperimentConfig(
        num_partners=2,
        num_rounds=1,
        num_replications=1,
        random_seed=0,
        max_policies=64,
    )
    env = create_env(config, seed=0)
    runtime = build_runtime(config, planning_horizon=1, seed=0)

    context = env.reset()
    decision = select_decision(
        bank=runtime.partner_bank,
        template=runtime.template,
        active_partner=context["active_partner"],
        assignment_mode=config.assignment_mode,
        base_gamma=runtime.base_gamma,
        action_selection=runtime.action_selection,
        rng=runtime.rng,
        affect_mode=runtime.affect_mode,
    )
    result = env.step(decision.raw_action)
    update_beta_after_observation(
        bank=runtime.partner_bank,
        partner_idx=result["partner_idx"],
        predicted_partner_action_probs=decision.predicted_partner_action_probs,
        observed_partner_action=result["partner_action"],
        affect_mode=runtime.affect_mode,
    )
    update_partner_after_observation(
        bank=runtime.partner_bank,
        template=runtime.template,
        partner_idx=result["partner_idx"],
        obs=result["observation"],
        own_action=result["agent_action"],
    )

    assert {"agent_payoff", "partner_idx", "observation"}.issubset(result)


def test_tiny_trust_runner_logs_data_collection_manuscript_contract(tiny_spec):
    results = ExperimentRunner.from_spec(tiny_spec.with_overrides(rounds=1, replications=1)).run_all()

    assert MANUSCRIPT_DATA_COLLECTION_COLUMNS <= set(results.columns)
    assert DEBUG_ONLY_COLUMNS.isdisjoint(results.columns)


def test_tiny_trust_runner_debug_profile_logs_diagnostic_internals(tiny_spec):
    debug_spec = replace(
        tiny_spec.with_overrides(rounds=1, replications=1),
        runtime=RuntimeSpec(profile="debug", debug_mode=True, log_policy_traces=True),
    )

    results = ExperimentRunner.from_spec(debug_spec).run_all()

    assert MANUSCRIPT_DATA_COLLECTION_COLUMNS <= set(results.columns)
    assert DEBUG_ONLY_COLUMNS <= set(results.columns)
    assert any(len(value) > 0 for value in results["q_pi"])
    assert any(len(value) > 0 for value in results["partner_joint_beliefs"])


def test_logger_does_not_fallback_posteriors_to_decision_beliefs():
    logger = MetricLogger(num_rounds=1, num_partners=1, runtime_profile="debug")
    decision_beliefs = np.asarray([[[0.2, 0.8]]], dtype=float)
    logger.log_round(
        round_idx=0,
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
            {"variant_id": "no_affect__planning_horizon_1", "seed": 0, "round": 0, "payoff": 1.0},
            {"variant_id": "affect__planning_horizon_1", "seed": 0, "round": 0, "payoff": 2.0},
        ]
    )

    results = run_all_hypothesis_tests(frame)

    assert "h1" in results
    assert all("available" in payload for payload in results.values())
