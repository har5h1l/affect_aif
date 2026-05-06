#!/usr/bin/env python3
"""CLI entry point for running backend-aware benchmarks."""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmarks.core.benchmark_config import BenchmarkConfig
from benchmarks.core.benchmark_runner import BenchmarkRunner
from benchmarks.core.comparison import format_comparison_report
from experiments.trust.spec import ExperimentSpec

CVC_POLICY_ALIASES = {
    "teammate_reliability": "class=benchmarks.cvc.policy.TeammateReliabilityPolicy",
    "scoring_loop": "class=benchmarks.cvc.scoring_policy.ScoringLoopPolicy",
    "scoring": "class=benchmarks.cvc.scoring_policy.ScoringLoopPolicy",
    "affect_cvc": "class=benchmarks.cvc.affect_policy.AffectCvCPolicy",
    "affect": "class=benchmarks.cvc.affect_policy.AffectCvCPolicy",
    "starter": "class=cogames.policy.starter_agent.StarterPolicy",
    "miner": "class=cogames.policy.role_policies.MinerRolePolicy",
    "aligner": "class=cogames.policy.role_policies.AlignerRolePolicy",
    "scrambler": "class=cogames.policy.role_policies.ScramblerRolePolicy",
    "scout": "class=cogames.policy.role_policies.ScoutRolePolicy",
}


def _coerce_agents(raw_agents: list[str], backends: list[str]):
    if not raw_agents:
        return None

    if backends == ["cvc_local"]:
        agents = []
        for agent in raw_agents:
            policy_spec = CVC_POLICY_ALIASES.get(agent, agent)
            agents.append(
                {
                    "name": agent,
                    "backend": "cvc_local",
                    "kind": "policy_spec",
                    "policy_spec": policy_spec,
                }
            )
        return agents

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
    parser = argparse.ArgumentParser(description="Run benchmark comparisons across benchmark backends.")
    parser.add_argument("--config", type=str, default=None, help="Path to benchmark-family TOML spec.")
    parser.add_argument(
        "--backend",
        action="append",
        dest="backends",
        default=None,
        help="Benchmark backend to run. Repeatable. Examples: trust, cvc_local.",
    )
    parser.add_argument("--agents", nargs="+", default=None, help="Agent names or policy specs.")
    parser.add_argument("--scenario", type=str, default="resource_sharing", help="Trust backend scenario label.")
    parser.add_argument("--mission", type=str, default="machina_1", help="CvC mission name for cvc_local.")
    parser.add_argument("--replications", type=int, default=10, help="Number of replications per agent.")
    parser.add_argument("--rounds", type=int, default=100, help="Number of trust-game rounds.")
    parser.add_argument("--max-steps", type=int, default=1000, help="Maximum CvC steps for cvc_local.")
    parser.add_argument("--num-agents", type=int, default=8, help="Number of CvC agents.")
    parser.add_argument("--python-bin", type=str, default="python3.12", help="Python binary for cvc_local worker.")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory.")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed.")
    parser.add_argument(
        "--observatory-season", type=str, default=None, help="Optional Observatory season name or 'default'."
    )
    parser.add_argument(
        "--observatory-pool", type=str, default=None, help="Optional Observatory pool for config fetch."
    )
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
            "backend_configs": {
                "trust": {"scenario": args.scenario},
                "cvc_local": {
                    "mission": args.mission,
                    "num_agents": args.num_agents,
                    "max_steps": args.max_steps,
                    "python_bin": args.python_bin,
                },
            },
        }
        if args.observatory_season or args.observatory_pool:
            config_payload["observatory"] = {
                "season": args.observatory_season,
                "pool": args.observatory_pool,
            }
        config = BenchmarkConfig.from_dict(config_payload)

    experimental_backends = [backend for backend in config.backends if backend == "cvc_local"]
    if experimental_backends:
        warnings.warn(
            "Experimental benchmark backend(s) selected: "
            f"{', '.join(experimental_backends)}. "
            "Trust is the canonical supported backend; CvC is a WIP external integration.",
            RuntimeWarning,
            stacklevel=2,
        )

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
