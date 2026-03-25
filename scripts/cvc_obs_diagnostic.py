#!/usr/bin/env python3
"""Diagnostic: run a short CvC episode and dump observation feature names.

Run with Python 3.12:
    python3.12 scripts/cvc_obs_diagnostic.py --steps 50

Outputs all unique feature names, their value ranges, and spatial distribution.
This tells us how walls/obstacles are encoded in the mettagrid observation.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission", default="machina_1")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-agents", type=int, default=8)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    from cogames.cli.mission import resolve_mission
    from cogames.game import get_game
    from mettagrid.mettagrid_env import MettaGridEnv
    from mettagrid.policy.policy_env_interface import PolicyEnvInterface

    game = get_game("cogs_vs_clips")
    _, env_cfg, _ = resolve_mission(game, args.mission, variants_arg=None, cogs=args.num_agents)
    env_cfg.game.max_steps = args.steps

    env = MettaGridEnv(env_cfg, render_mode="none")
    obs_list, _ = env.reset(seed=args.seed)

    pei = PolicyEnvInterface(env)
    print(f"=== PolicyEnvInterface ===")
    print(f"  obs_height: {pei.obs_height}")
    print(f"  obs_width: {pei.obs_width}")
    print(f"  num_agents: {pei.num_agents}")
    print(f"  action_names: {pei.action_names}")
    print(f"  num_tags: {len(pei.tags)}")
    print(f"  tags: {pei.tags}")

    feature_info = defaultdict(lambda: {"count": 0, "min_val": float("inf"), "max_val": float("-inf"), "locations": set()})
    tag_value_names = {}
    all_cell_features = Counter()

    center = (pei.obs_height // 2, pei.obs_width // 2)
    print(f"  center: {center}")

    for step_i in range(args.steps):
        for agent_id in range(min(2, pei.num_agents)):
            obs = obs_list[agent_id] if isinstance(obs_list, list) else obs_list
            agent_obs = pei.get_observation(obs, agent_id) if hasattr(pei, "get_observation") else obs

            for token in agent_obs.tokens:
                name = token.feature.name
                val = float(token.value)
                loc = token.location

                info = feature_info[name]
                info["count"] += 1
                info["min_val"] = min(info["min_val"], val)
                info["max_val"] = max(info["max_val"], val)
                if loc is not None:
                    info["locations"].add(loc)

                if name == "tag" and loc is not None:
                    tag_id = int(token.value)
                    if tag_id < len(pei.tags):
                        tag_value_names[tag_id] = pei.tags[tag_id]

                if loc is not None:
                    all_cell_features[(loc[0], loc[1])] += 1

        actions = [0] * pei.num_agents  # noop
        if step_i % 5 < 4:
            actions = [(step_i % 4) + 1] * pei.num_agents  # cycle through move directions
        obs_list, rewards, terminated, truncated, infos = env.step(actions)

    print(f"\n=== Feature Summary (from {args.steps} steps, agents 0-1) ===")
    for name, info in sorted(feature_info.items(), key=lambda x: -x[1]["count"]):
        n_locs = len(info["locations"])
        print(f"  {name:40s}  count={info['count']:6d}  val=[{info['min_val']:.3f}, {info['max_val']:.3f}]  unique_locs={n_locs}")

    print(f"\n=== Tag ID -> Name Mapping ===")
    for tag_id, tag_name in sorted(tag_value_names.items()):
        print(f"  {tag_id:3d} -> {tag_name}")

    print(f"\n=== Grid Cell Coverage ===")
    total_cells = pei.obs_height * pei.obs_width
    cells_with_features = len(all_cell_features)
    print(f"  Total grid cells: {total_cells}")
    print(f"  Cells with features: {cells_with_features}")
    print(f"  Cells without features: {total_cells - cells_with_features}")

    # Check specific potential wall indicators
    wall_candidates = [n for n in feature_info if any(w in n.lower() for w in ("wall", "obstacle", "block", "impass", "terrain", "floor", "empty"))]
    print(f"\n=== Potential Wall/Terrain Features ===")
    if wall_candidates:
        for name in wall_candidates:
            print(f"  FOUND: {name}")
    else:
        print("  None found by name heuristic. Walls may be encoded as absence of features,")
        print("  or via a numeric feature channel not matching common names.")

    # Dump sample observation grid for step 0
    print(f"\n=== Sample Grid (last step, agent 0) ===")
    agent_obs = pei.get_observation(obs_list, 0) if hasattr(pei, "get_observation") else obs_list
    grid_features = defaultdict(list)
    for token in agent_obs.tokens:
        loc = token.location
        if loc is not None:
            grid_features[loc].append(f"{token.feature.name}={token.value:.2f}")

    for r in range(pei.obs_height):
        for c in range(pei.obs_width):
            feats = grid_features.get((r, c), [])
            marker = "." if not feats else ("@" if (r, c) == center else "#")
            print(marker, end="")
        print()

    if args.output:
        result = {
            "obs_height": pei.obs_height,
            "obs_width": pei.obs_width,
            "tags": list(pei.tags),
            "action_names": list(pei.action_names),
            "features": {
                name: {"count": info["count"], "min_val": info["min_val"], "max_val": info["max_val"], "unique_locs": len(info["locations"])}
                for name, info in feature_info.items()
            },
            "tag_mapping": {str(k): v for k, v in tag_value_names.items()},
        }
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"\nSaved to {args.output}")

    env.close()


if __name__ == "__main__":
    main()
