#!/usr/bin/env python3
"""List available CvC missions from cogames.

Run with Python 3.12 (or conda env with cogames):
    conda run -n cvc python scripts/cvc/list_missions.py

Probes all available missions and reports their properties.
"""

from __future__ import annotations

import sys


def main():
    try:
        from cogames.game import get_game
    except ImportError:
        print("ERROR: cogames not available. Needs Python 3.12 + cogames.", file=sys.stderr)
        sys.exit(1)

    from cogames.cli.mission import resolve_mission
    from mettagrid import Simulation

    game = get_game("cogs_vs_clips")

    # Get the full list by triggering the error message
    try:
        resolve_mission(game, "INVALID_PROBE_NAME", variants_arg=None, cogs=8)
    except Exception as e:
        msg = str(e)
        if "Available:" in msg:
            names = msg.split("Available:")[1].strip().split(", ")
            print(f"=== Available missions ({len(names)}) ===")
        else:
            print(f"Could not extract mission list: {msg}")
            names = ["machina_1"]

    print()
    print(f"{'Mission':<40s}  {'Map Size':>10s}  {'Max Steps':>10s}  {'Agents':>7s}  Notes")
    print("-" * 90)

    for name in names:
        try:
            _, env_cfg, _ = resolve_mission(game, name, variants_arg=None, cogs=8)
            env_cfg.game.max_steps = 100  # cap for probing

            sim = Simulation(env_cfg)
            w, h = sim.map_width, sim.map_height
            na = sim.num_agents
            ms = env_cfg.game.max_steps

            # Check observation to count walkable cells
            obs = sim.observations()
            ao = obs[0]
            aoe_count = sum(1 for t in ao.tokens if t.feature.name == "aoe_mask")
            tag_types = set()
            for t in ao.tokens:
                if t.feature.name == "tag" and t.value < len(sim.object_type_names):
                    otype = sim.object_type_names[t.value]
                    if otype:
                        tag_types.add(otype)

            notes = f"walkable={aoe_count}, objects={','.join(sorted(tag_types))}"
            print(f"  {name:<38s}  {w}x{h:>5d}  {ms:>10d}  {na:>7d}  {notes}")
            sim.end_episode()
        except Exception as e:
            print(f"  {name:<38s}  ERROR: {str(e)[:60]}")

    print("\nDone.")


if __name__ == "__main__":
    main()
