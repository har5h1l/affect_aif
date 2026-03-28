#!/usr/bin/env python3
"""Diagnostic: run a short CvC episode and dump observation feature names.

Run with Python 3.12 (or conda env with cogames):
    conda run -n cvc python scripts/cvc_obs_diagnostic.py --steps 50

Outputs all unique feature names, their value ranges, and spatial distribution.
Shows how walls/obstacles are encoded in the mettagrid observation.
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
    parser.add_argument("--num-agents", type=int, default=8)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    from cogames.cli.mission import resolve_mission
    from cogames.game import get_game
    from mettagrid import Simulation
    from mettagrid.policy.policy_env_interface import PolicyEnvInterface

    game = get_game("cogs_vs_clips")
    _, env_cfg, _ = resolve_mission(game, args.mission, variants_arg=None, cogs=args.num_agents)
    env_cfg.game.max_steps = args.steps

    pei = PolicyEnvInterface.from_mg_cfg(env_cfg)
    print("=== PolicyEnvInterface ===")
    print(f"  obs_height: {pei.obs_height}")
    print(f"  obs_width: {pei.obs_width}")
    print(f"  num_agents: {pei.num_agents}")
    print(f"  action_names: {pei.action_names}")
    print(f"  num_tags: {len(pei.tags)}")
    print(f"  tags: {pei.tags}")

    sim = Simulation(env_cfg)
    print("\n=== Simulation ===")
    print(f"  map_size: {sim.map_width}x{sim.map_height}")
    print(f"  observation_shape: {sim.observation_shape}")
    print(f"  object_type_names: {[x for x in sim.object_type_names if x]}")
    print(f"  action_names: {sim.action_names}")

    center = (pei.obs_height // 2, pei.obs_width // 2)
    print(f"  center: {center}")

    feature_info = defaultdict(lambda: {"count": 0, "min_val": float("inf"), "max_val": float("-inf"), "unique_locs": 0, "locs": set()})
    tag_value_counts = Counter()
    all_cell_features = Counter()

    for step_i in range(args.steps):
        obs_list = sim.observations()
        for agent_id in range(min(2, pei.num_agents)):
            ao = obs_list[agent_id]
            for token in ao.tokens:
                name = token.feature.name
                val = float(token.value)
                loc = token.location

                info = feature_info[name]
                info["count"] += 1
                info["min_val"] = min(info["min_val"], val)
                info["max_val"] = max(info["max_val"], val)
                if loc is not None:
                    info["locs"].add((loc[0], loc[1]))
                    all_cell_features[(loc[0], loc[1])] += 1

                if name == "tag":
                    tag_value_counts[int(val)] += 1

        # Cycle through move directions
        for i in range(sim.num_agents):
            agent = sim.agent(i)
            direction = ["noop", "move_north", "move_south", "move_west", "move_east"][step_i % 5]
            agent.set_action(direction)
        sim.step()

    print(f"\n=== Feature Summary (from {args.steps} steps, agents 0-1) ===")
    for name, info in sorted(feature_info.items(), key=lambda x: -x[1]["count"]):
        n_locs = len(info["locs"])
        info["unique_locs"] = n_locs
        print(f"  {name:40s}  count={info['count']:6d}  val=[{info['min_val']:.3f}, {info['max_val']:.3f}]  unique_locs={n_locs}")

    print(f"\n=== Tag Value -> Object Type Mapping ===")
    for tag_id, count in sorted(tag_value_counts.items()):
        otype = sim.object_type_names[tag_id] if tag_id < len(sim.object_type_names) else "?"
        pei_tag = pei.tags[tag_id] if tag_id < len(pei.tags) else "?"
        print(f"  tag={tag_id:3d}  count={count:5d}  object_type={otype:25s}  pei_tag={pei_tag}")

    print(f"\n=== Grid Cell Coverage ===")
    total_cells = pei.obs_height * pei.obs_width
    cells_with_features = len(all_cell_features)
    print(f"  Total grid cells: {total_cells}")
    print(f"  Cells with features: {cells_with_features}")
    print(f"  Cells without features (walls/out-of-view): {total_cells - cells_with_features}")

    # Show aoe_mask grid
    print(f"\n=== aoe_mask Grid (last step, agent 0) ===")
    last_obs = sim.observations()
    ao = last_obs[0]
    aoe_cells = set()
    tag_cells = {}
    for token in ao.tokens:
        if token.location is None:
            continue
        r, c = token.location[0], token.location[1]
        if token.feature.name == "aoe_mask":
            aoe_cells.add((r, c))
        elif token.feature.name == "tag":
            otype = sim.object_type_names[token.value] if token.value < len(sim.object_type_names) else "?"
            tag_cells[(r, c)] = otype

    for r in range(pei.obs_height):
        line = ""
        for c in range(pei.obs_width):
            if (r, c) == center:
                line += "@"
            elif (r, c) in tag_cells:
                tc = tag_cells[(r, c)]
                line += tc[0].upper() if tc else "?"
            elif (r, c) in aoe_cells:
                line += "."
            else:
                line += "#"
        print(f"  {line}")
    print("  Legend: @=agent, .=walkable, #=wall/out-of-view, UPPERCASE=object type initial")

    if args.output:
        result = {
            "obs_height": pei.obs_height,
            "obs_width": pei.obs_width,
            "tags": list(pei.tags),
            "object_type_names": [x for x in sim.object_type_names if x],
            "action_names": list(pei.action_names),
            "features": {
                name: {"count": info["count"], "min_val": info["min_val"], "max_val": info["max_val"], "unique_locs": info["unique_locs"]}
                for name, info in feature_info.items()
            },
            "tag_value_counts": dict(tag_value_counts),
            "wall_encoding": "absence_of_aoe_mask",
        }
        Path(args.output).write_text(json.dumps(result, indent=2))
        print(f"\nSaved to {args.output}")

    sim.end_episode()


if __name__ == "__main__":
    main()
