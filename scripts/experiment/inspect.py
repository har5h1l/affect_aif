"""Inspect experiment configs without running them."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if sys.path and str(Path(sys.path[0]).resolve()) == SCRIPT_DIR:
    sys.path.pop(0)

import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.trust.config import ExperimentConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect an affect_aif experiment config.")
    parser.add_argument("--config", required=True, help="Path to a trust experiment config JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.config).resolve()
    config = ExperimentConfig.from_json(str(path))
    print(
        json.dumps(
            {
                "config": str(path),
                "conditions": list(config.conditions),
                "num_rounds": config.num_rounds,
                "num_replications": config.num_replications,
                "run_sensitivity": config.run_sensitivity,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
