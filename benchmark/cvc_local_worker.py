"""Python 3.12 worker used by the CvC local benchmark backend."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one local CoGames/CvC episode and emit benchmark records.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--policy-spec", required=True)
    parser.add_argument("--mission", default="machina_1")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-agents", type=int, default=8)
    parser.add_argument("--max-steps", type=int, default=1000)
    parser.add_argument("--max-action-time-ms", type=int, default=10000)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--season-name", default=None)
    return parser


def _sum_agent_stat(agent_stats: list[dict], key: str) -> float:
    return float(sum(float(agent.get(key, 0.0)) for agent in agent_stats))


def main():
    args = _build_parser().parse_args()

    from cogames.cli.mission import resolve_mission
    from cogames.cli.policy import parse_policy_spec
    from cogames.game import get_game
    from mettagrid.runner.rollout import run_episode_local

    game = get_game("cogs_vs_clips")
    _, env_cfg, _ = resolve_mission(game, args.mission, variants_arg=None, cogs=args.num_agents)
    env_cfg.game.max_steps = int(args.max_steps)

    policy_spec = parse_policy_spec(args.policy_spec, device=args.device).to_policy_spec()
    results, _ = run_episode_local(
        policy_specs=[policy_spec],
        assignments=[0] * env_cfg.game.num_agents,
        env=env_cfg,
        seed=int(args.seed),
        max_action_time_ms=int(args.max_action_time_ms),
        device=args.device,
        render_mode="none",
        autostart=False,
    )

    agent_stats = results.stats.get("agent", [])
    rewards = np.asarray(results.rewards, dtype=float)
    record = {
        "schema_version": 2,
        "backend": "cvc_local",
        "scenario": args.mission,
        "record_type": "episode",
        "agent_name": args.agent_name,
        "seed": int(args.seed),
        "episode_id": f"cvc_local:{args.agent_name}:{args.seed}",
        "step": int(results.steps),
        "reward": float(rewards.mean()) if rewards.size else 0.0,
        "team_reward_mean": float(rewards.mean()) if rewards.size else 0.0,
        "team_reward_sum": float(rewards.sum()) if rewards.size else 0.0,
        "team_reward_var": float(rewards.var()) if rewards.size else 0.0,
        "num_agents": int(len(results.rewards)),
        "max_steps": int(env_cfg.game.max_steps),
        "policy_spec": args.policy_spec,
        "season_name": args.season_name,
        "aligned_junctions": _sum_agent_stat(agent_stats, "junction.aligned_by_agent"),
        "scrambled_junctions": _sum_agent_stat(agent_stats, "junction.scrambled_by_agent"),
        "hearts_gained": _sum_agent_stat(agent_stats, "heart.gained"),
        "miner_role_gains": _sum_agent_stat(agent_stats, "miner.gained"),
        "aligner_role_gains": _sum_agent_stat(agent_stats, "aligner.gained"),
        "scrambler_role_gains": _sum_agent_stat(agent_stats, "scrambler.gained"),
        "scout_role_gains": _sum_agent_stat(agent_stats, "scout.gained"),
        "cells_visited": _sum_agent_stat(agent_stats, "cell.visited"),
        "max_steps_without_motion": _sum_agent_stat(agent_stats, "status.max_steps_without_motion"),
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps([record], indent=2))


if __name__ == "__main__":
    main()
