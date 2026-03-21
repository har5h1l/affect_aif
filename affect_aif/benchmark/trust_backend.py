"""Trust-game benchmark backend."""

from __future__ import annotations

import json
import time
from dataclasses import fields
from typing import Any

import numpy as np

from affect_aif.benchmark import baselines
from affect_aif.benchmark.backend import BenchmarkBackend, BenchmarkBackendContext
from affect_aif.benchmark.benchmark_config import AGENT_REGISTRY, SCHEMA_VERSION, AgentSpec, BenchmarkConfig
from affect_aif.benchmark.scenarios import get_scenario
from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.conditions import get_condition_name
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner

EXPERIMENT_CONFIG_FIELDS = {field.name for field in fields(ExperimentConfig)}


def _create_baseline_agent(agent_name: str, num_partners: int, seed: int):
    info = AGENT_REGISTRY[agent_name]
    cls_name = info["class"]
    cls = getattr(baselines, cls_name)
    return cls(num_partners=num_partners, seed=seed)


def _create_aif_agent(condition: int, config: ExperimentConfig, seed: int):
    runner = ExperimentRunner(config)
    model = runner._create_model()
    return runner._create_agent(condition, model, seed), model


class TrustBackend(BenchmarkBackend):
    """Canonical benchmark backend for the trust game."""

    backend_name = "trust"

    def __init__(self, backend_config: dict[str, Any] | None = None):
        super().__init__(backend_config)
        self.scenario_name = str(self.backend_config.get("scenario", "resource_sharing"))
        self.scenario = get_scenario(self.scenario_name)
        self._prepared_config: ExperimentConfig | None = None

    @staticmethod
    def _normalize_partner_type(type_name: str) -> str:
        aliases = {
            "cooperative": "cooperator",
            "cooperator": "cooperator",
            "reciprocal": "reciprocator",
            "reciprocator": "reciprocator",
            "exploitative": "exploiter",
            "exploiter": "exploiter",
            "random": "random",
        }
        return aliases.get(type_name, type_name)

    def _normalize_overrides(self, overrides: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(overrides)
        if "initial_partner_types" in normalized and normalized["initial_partner_types"] is not None:
            normalized["initial_partner_types"] = [
                self._normalize_partner_type(str(name))
                for name in normalized["initial_partner_types"]
            ]
        if "scheduled_type_switches" in normalized:
            normalized["scheduled_type_switches"] = [
                {
                    **event,
                    "to_type": self._normalize_partner_type(str(event["to_type"])),
                }
                for event in normalized["scheduled_type_switches"]
            ]
        return normalized

    def _make_experiment_config(self, config: BenchmarkConfig) -> ExperimentConfig:
        overrides = {
            "num_partners": self.scenario.num_partners,
            "num_rounds": config.num_rounds,
            "num_replications": 1,
            "calibration_episodes": 5,
            "random_seed": config.random_seed,
        }
        direct_overrides = {
            key: value
            for key, value in self.backend_config.items()
            if key in EXPERIMENT_CONFIG_FIELDS
        }
        legacy_overrides = dict(self.backend_config.get("trust_game_overrides", {}))
        overrides.update(self._normalize_overrides({**direct_overrides, **legacy_overrides}))
        return ExperimentConfig(**overrides)

    def prepare(
        self,
        config: BenchmarkConfig,
        agent_specs: list[AgentSpec],
        context: BenchmarkBackendContext,
    ) -> None:
        if "trust_experiment_config" in context.shared:
            self._prepared_config = context.shared["trust_experiment_config"]
            return

        has_aif_agents = any(
            agent.kind == "registry"
            and agent.implementation in AGENT_REGISTRY
            and AGENT_REGISTRY[agent.implementation]["type"] == "aif"
            for agent in agent_specs
        )
        trust_config = self._make_experiment_config(config)
        if has_aif_agents:
            runner = ExperimentRunner(trust_config)
            if runner.needs_mu_calibration():
                runner.calibrate_mu(enforce_minimum=True)
        self._prepared_config = trust_config
        context.shared["trust_experiment_config"] = trust_config

    def run_agent(
        self,
        agent_spec: AgentSpec,
        config: BenchmarkConfig,
        seed: int,
        context: BenchmarkBackendContext,
    ) -> list[dict[str, Any]]:
        if agent_spec.kind != "registry":
            raise ValueError(f"Trust backend only supports registry agents, got '{agent_spec.kind}'.")

        agent_name = agent_spec.implementation or agent_spec.name
        if agent_name not in AGENT_REGISTRY:
            raise ValueError(f"Unknown trust benchmark agent '{agent_name}'.")

        experiment_config = self._prepared_config or context.shared.get("trust_experiment_config")
        if experiment_config is None:
            experiment_config = self._make_experiment_config(config)

        env = TrustGameEnv(experiment_config, seed=seed)
        info = AGENT_REGISTRY[agent_name]
        condition_id = (
            info["condition"]
            if info["type"] == "aif"
            else -(config.agents.index(agent_spec) + 1)
        )

        if info["type"] == "baseline":
            agent = _create_baseline_agent(agent_name, env.num_partners, seed)
        else:
            agent, _ = _create_aif_agent(info["condition"], experiment_config, seed)

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
                    "condition": condition_id,
                    "condition_name": get_condition_name(condition_id) if condition_id > 0 else agent_spec.name,
                    "partner_idx": partner_idx,
                    "true_partner_type": result.get("true_partner_type", "unknown"),
                    "agent_action": result["agent_action"],
                    "raw_action": result.get("raw_action", raw_action),
                    "partner_action": result["partner_action"],
                    "payoff": float(result["agent_payoff"]),
                    "partner_payoff": float(result.get("partner_payoff", np.nan)),
                    "type_switched": bool(result.get("type_switched", False)),
                    "switch_kind": result.get("switch_kind", "none"),
                    "current_partner_switched": bool(result.get("current_partner_switched", False)),
                    "current_partner_scheduled_switch": bool(result.get("current_partner_scheduled_switch", False)),
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
