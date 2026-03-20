"""Orchestrates benchmark runs across trust game and gridworld environments."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from affect_aif.benchmark import baselines
from affect_aif.benchmark.benchmark_config import AGENT_REGISTRY, BenchmarkConfig
from affect_aif.benchmark.cogames_adapter import CoGamesTrustAdapter
from affect_aif.benchmark.scenarios import get_scenario
from affect_aif.environment.trust_game import TrustGameEnv
from affect_aif.experiment.config import ExperimentConfig
from affect_aif.experiment.runner import ExperimentRunner
from affect_aif.generative_model.model import TrustGameModel


def _create_baseline_agent(agent_name: str, num_partners: int, seed: int):
    """Create a baseline agent by name."""
    info = AGENT_REGISTRY[agent_name]
    cls_name = info["class"]
    cls = getattr(baselines, cls_name)
    return cls(num_partners=num_partners, seed=seed)


def _create_aif_agent(condition: int, config: ExperimentConfig, seed: int):
    """Create an AIF agent using the experiment runner's factory."""
    runner = ExperimentRunner(config)
    model = runner._create_model()
    return runner._create_agent(condition, model, seed), model


def _run_episode(agent, env, num_rounds: int, agent_name: str, environment_name: str, seed: int) -> list[dict]:
    """Run a single episode and return per-round records."""
    context = env.reset()
    agent.reset()
    records = []

    for round_idx in range(num_rounds):
        active_partner = context.get("active_partner")
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

        # Determine inferred type if the agent supports it
        inferred_type = "unknown"
        inferred_correct = False
        if hasattr(agent, "get_partner_type_belief"):
            belief = agent.get_partner_type_belief(partner_idx)
            if hasattr(agent, "model") and hasattr(agent.model, "partner_type_names"):
                inferred_idx = int(np.argmax(belief))
                inferred_type = agent.model.partner_type_names[inferred_idx]
                true_type = result.get("true_partner_type", "")
                inferred_correct = inferred_type == true_type

        record = {
            "environment": environment_name,
            "agent_name": agent_name,
            "seed": seed,
            "round": round_idx,
            "condition": agent_name,
            "partner_idx": partner_idx,
            "true_partner_type": result.get("true_partner_type", "unknown"),
            "agent_action": result["agent_action"],
            "raw_action": result.get("raw_action", raw_action),
            "partner_action": result["partner_action"],
            "payoff": result["agent_payoff"],
            "partner_payoff": result.get("partner_payoff", np.nan),
            "type_switched": result.get("type_switched", False),
            "switch_kind": result.get("switch_kind", "none"),
            "inferred_type": inferred_type,
            "inferred_type_correct": inferred_correct,
        }
        records.append(record)

        context = result

    return records


class BenchmarkRunner:
    """Run benchmark comparisons across environments and agent types."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.scenario = get_scenario(config.scenario)

    def _make_trust_game_config(self) -> ExperimentConfig:
        """Create a trust game config matching the benchmark scenario."""
        overrides = {
            "num_partners": self.scenario.num_partners,
            "num_rounds": self.config.num_rounds,
            "num_replications": 1,
            "calibration_episodes": 5,
            "random_seed": self.config.random_seed,
        }
        overrides.update(self.config.trust_game_overrides)
        return ExperimentConfig(**overrides)

    def run_all(self) -> pd.DataFrame:
        """Run all agents in all environments and return combined results."""
        all_records = []

        for agent_name in self.config.agents:
            if agent_name not in AGENT_REGISTRY:
                raise ValueError(f"Unknown agent '{agent_name}'. Available: {sorted(AGENT_REGISTRY.keys())}")

            for seed_offset in range(self.config.num_replications):
                seed = self.config.random_seed + seed_offset

                info = AGENT_REGISTRY[agent_name]

                if self.config.run_trust_game:
                    trust_config = self._make_trust_game_config()
                    trust_env = TrustGameEnv(trust_config, seed=seed)

                    if info["type"] == "baseline":
                        agent = _create_baseline_agent(
                            agent_name, self.scenario.num_partners, seed
                        )
                    else:
                        agent, _ = _create_aif_agent(
                            info["condition"], trust_config, seed
                        )

                    records = _run_episode(
                        agent, trust_env, self.config.num_rounds,
                        agent_name, "trust_game", seed
                    )
                    all_records.extend(records)

                if self.config.run_gridworld:
                    grid_env = CoGamesTrustAdapter(
                        scenario=self.scenario,
                        seed=seed,
                    )

                    if info["type"] == "baseline":
                        agent = _create_baseline_agent(
                            agent_name, self.scenario.num_partners, seed
                        )
                    else:
                        grid_trust_config = self._make_trust_game_config()
                        agent, _ = _create_aif_agent(
                            info["condition"], grid_trust_config, seed
                        )

                    records = _run_episode(
                        agent, grid_env, self.config.num_rounds,
                        agent_name, "gridworld", seed
                    )
                    all_records.extend(records)

        return pd.DataFrame(all_records)

    def save_results(self, results: pd.DataFrame, path: str | None = None):
        """Save results to CSV."""
        if path is None:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            path = str(output_dir / "benchmark_results.csv")
        results.to_csv(path, index=False)
        return path
