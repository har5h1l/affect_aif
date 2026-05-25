#!/usr/bin/env python3
"""CLI entry point for running backend-aware benchmarks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmarks.core.benchmark_config import BenchmarkConfig
from benchmarks.core.benchmark_runner import BenchmarkRunner
from benchmarks.core.comparison import format_comparison_report
from experiments.trust.spec import ExperimentSpec


def _coerce_agents(raw_agents: list[str], backends: list[str]):
    if not raw_agents:
        return None

    if len(backends) == 1:
        return [
            {
                "name": agent,
                "backend": backends[0],
                "kind": "registry",
                "implementation": agent,
            }
            for agent in raw_agents
        ]

    raise ValueError("When using multiple backends, provide a config file with explicit agent specs.")


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Run trust-task benchmark comparisons.")
    parser.add_argument("--config", type=str, default=None, help="Path to benchmark-family TOML spec.")
    parser.add_argument(
        "--backend",
        action="append",
        dest="backends",
        default=None,
        help="Benchmark backend to run. The maintained backend is trust.",
    )
    parser.add_argument("--agents", nargs="+", default=None, help="Trust benchmark agent names.")
    parser.add_argument("--scenario", type=str, default="resource_sharing", help="Trust backend scenario label.")
    parser.add_argument("--replications", type=int, default=10, help="Number of replications per agent.")
    parser.add_argument("--rounds", type=int, default=100, help="Number of trust-game rounds.")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    args = parser.parse_args(argv)

    if args.config:
        config_path = Path(args.config)
        if config_path.suffix != ".toml":
            parser.error("--config must point to a benchmark-family TOML spec")
        spec = ExperimentSpec.from_toml(config_path)
        if spec.experiment.family != "benchmark":
            parser.error("--config must point to a benchmark-family TOML spec")
        config = BenchmarkConfig.from_experiment_spec(spec)
        if args.output_dir is not None:
            config.output_dir = args.output_dir
    else:
        backends = args.backends or ["trust"]
        agents = _coerce_agents(args.agents or ["affect", "no_affect", "random", "tit_for_tat"], backends)
        config_payload = {
            "backends": backends,
            "agents": agents,
            "num_replications": args.replications,
            "num_rounds": args.rounds,
            "output_dir": args.output_dir or "results/benchmark",
            "random_seed": args.seed,
            "backend_configs": {"trust": {"scenario": args.scenario}},
        }
        config = BenchmarkConfig.from_dict(config_payload)

    print(f"Backends: {config.backends}")
    print(f"Agents: {[agent.name for agent in config.agents]}")
    print(f"Replications: {config.num_replications}")
    print(f"Trust rounds: {config.num_rounds}")
    print()

    runner = BenchmarkRunner(config)
    results = runner.run_all()
    path = runner.save_results(results)
    report = format_comparison_report(results)

    print(f"Results saved to: {path}")
    print(f"Total records: {len(results)}")
    print()
    print(report)

    report_path = Path(config.output_dir) / "benchmark_report.txt"
    report_path.write_text(report)
    config_path = Path(config.output_dir) / "benchmark_config.resolved.toml"
    config.to_toml(config_path)
    print(f"\nReport saved to: {report_path}")
    print(f"Resolved config saved to: {config_path}")


if __name__ == "__main__":
    main()
