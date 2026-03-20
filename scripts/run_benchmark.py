#!/usr/bin/env python3
"""CLI entry point for running benchmark comparisons.

Usage:
    python scripts/run_benchmark.py --scenario resource_sharing \
        --agents affective_shallow random tit_for_tat \
        --replications 10 --rounds 100 \
        --output-dir results/benchmark

    python scripts/run_benchmark.py --config benchmark_config.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from affect_aif.benchmark.benchmark_config import AGENT_REGISTRY, BenchmarkConfig
from affect_aif.benchmark.benchmark_runner import BenchmarkRunner
from affect_aif.benchmark.comparison import format_comparison_report
from affect_aif.benchmark.scenarios import list_scenarios


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark comparison across trust game and gridworld environments."
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to benchmark config JSON file.",
    )
    parser.add_argument(
        "--scenario", type=str, default="resource_sharing",
        help=f"Scenario name. Available: {', '.join(list_scenarios())}",
    )
    parser.add_argument(
        "--agents", nargs="+", default=None,
        help=f"Agent types to benchmark. Available: {', '.join(sorted(AGENT_REGISTRY.keys()))}",
    )
    parser.add_argument(
        "--replications", type=int, default=10,
        help="Number of replications per agent per environment.",
    )
    parser.add_argument(
        "--rounds", type=int, default=100,
        help="Number of rounds per episode.",
    )
    parser.add_argument(
        "--output-dir", type=str, default="results/benchmark",
        help="Output directory for results.",
    )
    parser.add_argument(
        "--trust-game-only", action="store_true",
        help="Only run trust game (skip gridworld).",
    )
    parser.add_argument(
        "--gridworld-only", action="store_true",
        help="Only run gridworld (skip trust game).",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed.",
    )

    args = parser.parse_args()

    if args.config:
        config = BenchmarkConfig.from_json(args.config)
    else:
        config = BenchmarkConfig(
            scenario=args.scenario,
            agents=args.agents or ["affective_shallow", "shallow_no_affect", "random", "tit_for_tat"],
            num_replications=args.replications,
            num_rounds=args.rounds,
            output_dir=args.output_dir,
            random_seed=args.seed,
            run_trust_game=not args.gridworld_only,
            run_gridworld=not args.trust_game_only,
        )

    print(f"Benchmark: {config.scenario}")
    print(f"Agents: {config.agents}")
    print(f"Replications: {config.num_replications}")
    print(f"Rounds: {config.num_rounds}")
    print(f"Environments: ", end="")
    envs = []
    if config.run_trust_game:
        envs.append("trust_game")
    if config.run_gridworld:
        envs.append("gridworld")
    print(", ".join(envs))
    print()

    runner = BenchmarkRunner(config)
    results = runner.run_all()

    path = runner.save_results(results)
    print(f"Results saved to: {path}")
    print(f"Total records: {len(results)}")
    print()

    report = format_comparison_report(results)
    print(report)

    # Save report
    report_path = Path(config.output_dir) / "benchmark_report.txt"
    report_path.write_text(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
