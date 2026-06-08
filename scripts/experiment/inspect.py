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

from experiments.trust.spec import ExperimentSpec, load_experiment_specs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect an affect_aif experiment config.")
    parser.add_argument("--config", required=True, help="Path to a trust experiment TOML spec.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.config).resolve()
    specs = load_experiment_specs(path)
    print(
        json.dumps(
            {
                "config": str(path),
                "suite": len(specs) > 1,
                "specs": [_spec_summary(spec) for spec in specs],
                "expanded_runs": sum(len(spec.expand_runs()) for spec in specs),
            },
            indent=2,
        )
    )
    return 0


def _spec_summary(spec: ExperimentSpec) -> dict[str, object]:
    return {
        "hypothesis": {"id": spec.hypothesis.id, "name": spec.hypothesis.name},
        "experiment": {
            "id": spec.experiment.id,
            "family": spec.experiment.family,
            "rounds": spec.experiment.rounds,
            "replications": spec.experiment.replications,
            "seed": spec.experiment.seed,
        },
        "scenario": {
            "payoff": spec.scenario.payoff,
            "assignment": spec.scenario.assignment,
            "partners": spec.scenario.partners,
        },
        "variants": [variant.id for variant in spec.variants],
        "sweeps": [sweep.parameter for sweep in spec.sweeps],
        "expanded_runs": len(spec.expand_runs()),
        "analysis": {"auto": spec.analysis.auto, "primary": spec.analysis.primary},
    }


if __name__ == "__main__":
    raise SystemExit(main())
