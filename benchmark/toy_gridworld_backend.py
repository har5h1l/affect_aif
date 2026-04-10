"""Legacy toy backend backed by the scripted trust adapter.

This backend exists only for backward compatibility with old benchmark configs.
It is not treated as a real CoGames/CvC integration.
"""

from __future__ import annotations

import json
import time
from typing import Any

import numpy as np

from benchmark import baselines
from benchmark.backend import BenchmarkBackend, BenchmarkBackendContext
from benchmark.benchmark_config import AGENT_REGISTRY, SCHEMA_VERSION, AgentSpec, BenchmarkConfig
from benchmark.cogames_adapter import CoGamesTrustAdapter
from benchmark.scenarios import get_scenario
from experiment.conditions import resolve_condition_spec
from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner


def _create_baseline_agent(agent_name: str, num_partners: int, seed: int):
    info = AGENT_REGISTRY[agent_name]
    cls_name = info["class"]
    cls = getattr(baselines, cls_name)
    return cls(num_partners=num_partners, seed=seed)


def _create_aif_agent(condition: int | str, config: ExperimentConfig, seed: int):
    runner = ExperimentRunner(config)
    model = runner._create_model()
    return runner._create_agent(condition, model, seed), model


class ToyGridworldBackend(BenchmarkBackend):
    """Deprecated scripted backend kept for compatibility only."""

    backend_name = "toy_gridworld"

    def __init__(self, backend_config: dict[str, Any] | None = None):
        super().__init__(backend_config)
        self.scenario_name = str(self.backend_config.get("scenario", "resource_sharing"))
        self.scenario = get_scenario(self.scenario_name)
        self._shared_trust_config: ExperimentConfig | None = None

    def prepare(
        self,
        config: BenchmarkConfig,
        agent_specs: list[AgentSpec],
        context: BenchmarkBackendContext,
    ) -> None:
        self._shared_trust_config = context.shared.get("trust_experiment_config")
        if self._shared_trust_config is None:
            overrides = {
                "num_rounds": config.num_rounds,
                "num_replications": 1,
                "calibration_episodes": 5,
                "random_seed": config.random_seed,
            }
            overrides.update(self.scenario.trust_game_defaults())
            overrides.update(dict(self.backend_config.get("trust_game_overrides", {})))
            self._shared_trust_config = ExperimentConfig(**overrides)
            context.shared["trust_experiment_config"] = self._shared_trust_config

    def run_agent(
        self,
        agent_spec: AgentSpec,
        config: BenchmarkConfig,
        seed: int,
        context: BenchmarkBackendContext,
    ) -> list[dict[str, Any]]:
        if agent_spec.kind != "registry":
            raise ValueError(f"Toy gridworld backend only supports registry agents, got '{agent_spec.kind}'.")

        agent_name = agent_spec.implementation or agent_spec.name
        if agent_name not in AGENT_REGISTRY:
            raise ValueError(f"Unknown toy-gridworld agent '{agent_name}'.")

        trust_config = self._shared_trust_config or context.shared["trust_experiment_config"]
        env = CoGamesTrustAdapter(
            scenario=self.scenario,
            seed=seed,
            ticks_per_round=int(self.backend_config.get("ticks_per_round", self.scenario.ticks_per_round)),
        )
        info = AGENT_REGISTRY[agent_name]
        condition_key = info.get("condition", info.get("preset")) if info["type"] == "aif" else -(config.agents.index(agent_spec) + 1)

        if info["type"] == "baseline":
            agent = _create_baseline_agent(agent_name, self.scenario.num_partners, seed)
        else:
            agent, _ = _create_aif_agent(condition_key, trust_config, seed)

        context_payload = env.reset()
        agent.reset()
        records: list[dict[str, Any]] = []
        episode_id = f"{self.backend_name}:{agent_spec.name}:{seed}"
        started = time.perf_counter()

        for round_idx in range(config.num_rounds):
            active_partner = context_payload.get("active_partner")
            raw_action = agent.plan_and_act(active_partner)
            result = env.step(raw_action)

            partner_idx = result["partner_idx"]
            agent.observe_outcome(
                partner_idx=partner_idx,
                observation=result["observation"],
                action_taken=result["agent_action"],
                partner_action=result["partner_action"],
                payoff=result["agent_payoff"],
                true_partner_type=result.get("true_partner_type"),
            )

            inferred_type = "unknown"
            inferred_correct = np.nan
            if hasattr(agent, "get_partner_type_belief"):
                belief = agent.get_partner_type_belief(partner_idx)
                if hasattr(agent, "model") and hasattr(agent.model, "partner_type_names"):
                    inferred_idx = int(np.argmax(belief))
                    inferred_type = agent.model.partner_type_names[inferred_idx]
                    inferred_correct = inferred_type == result.get("true_partner_type", "")

            records.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "backend": self.backend_name,
                    "scenario": self.scenario_name,
                    "record_type": "round",
                    "agent_name": agent_spec.name,
                    "seed": seed,
                    "episode_id": episode_id,
                    "step": round_idx,
                    "reward": float(result["agent_payoff"]),
                    "condition": condition_key,
                    "condition_name": resolve_condition_spec(condition_key).name if info["type"] == "aif" else agent_spec.name,
                    "partner_idx": partner_idx,
                    "true_partner_type": result.get("true_partner_type", "unknown"),
                    "agent_action": result["agent_action"],
                    "raw_action": result.get("raw_action", raw_action),
                    "partner_action": result["partner_action"],
                    "payoff": float(result["agent_payoff"]),
                    "partner_payoff": float(result.get("partner_payoff", np.nan)),
                    "type_switched": bool(result.get("type_switched", False)),
                    "switch_kind": result.get("switch_kind", "none"),
                    "scheduled_switch_partner_ids": ",".join(
                        str(value) for value in result.get("scheduled_switch_partner_ids", [])
                    ),
                    "true_types": json.dumps(result.get("true_types", [])),
                    "inferred_type": inferred_type,
                    "inferred_type_correct": inferred_correct,
                }
            )
            context_payload = result

        elapsed = time.perf_counter() - started
        for record in records:
            record["episode_runtime_s"] = elapsed
        return records
