#!/usr/bin/env python3
"""List available CvC missions from cogames.

Run with Python 3.12:
    python3.12 scripts/cvc_list_missions.py

Tries known mission names against resolve_mission() and reports which ones work.
Also inspects the cogames mission registry if accessible.
"""

from __future__ import annotations

import sys


def main():
    try:
        from cogames.game import get_game
    except ImportError:
        print("ERROR: cogames not available. Needs Python 3.12 + cogames.", file=sys.stderr)
        sys.exit(1)

    game = get_game("cogs_vs_clips")

    # Try to find mission registry
    print("=== Game info ===")
    print(f"  Game: {game}")
    if hasattr(game, "missions"):
        print(f"  Missions attr: {game.missions}")
    if hasattr(game, "list_missions"):
        print(f"  list_missions(): {game.list_missions()}")

    # Inspect game module for mission data
    game_module = type(game).__module__
    print(f"  Module: {game_module}")
    for attr in sorted(dir(game)):
        if "mission" in attr.lower() or "map" in attr.lower() or "level" in attr.lower():
            print(f"  {attr}: {getattr(game, attr, '?')}")

    # Try known and guessed mission names
    from cogames.cli.mission import resolve_mission

    candidates = [
        "machina_1", "machina_2", "machina_3",
        "tutorial", "tutorial_1", "tutorial_2",
        "simple", "basic", "test",
        "open", "arena", "flat",
        "sandbox", "playground",
        "starter", "demo",
    ]

    print("\n=== Mission probe ===")
    for name in candidates:
        try:
            _, env_cfg, _ = resolve_mission(game, name, variants_arg=None, cogs=8)
            map_size = getattr(env_cfg.game, "map_width", "?")
            max_steps = getattr(env_cfg.game, "max_steps", "?")
            print(f"  OK: {name:20s}  map_width={map_size}  max_steps={max_steps}")
        except Exception as e:
            err_msg = str(e)[:80]
            print(f"  FAIL: {name:20s}  {err_msg}")

    # Try to find mission directory in cogames package
    import cogames
    import os
    pkg_dir = os.path.dirname(cogames.__file__)
    for root, dirs, files in os.walk(pkg_dir):
        for f in files:
            if "mission" in f.lower() or f.endswith(".yaml") or f.endswith(".yml"):
                rel = os.path.relpath(os.path.join(root, f), pkg_dir)
                print(f"  File: cogames/{rel}")

    print("\nDone.")


if __name__ == "__main__":
    main()
