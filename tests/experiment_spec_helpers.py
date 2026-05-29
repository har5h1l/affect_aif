from __future__ import annotations

from pathlib import Path


def write_example_toml(path: Path, *, sweeps: bool = False, rounds: int = 120, replications: int = 3) -> Path:
    sweep_block = """

[[sweeps]]
parameter = "planning_horizon"
values = [1, 4]
applies_to = ["affect", "no_affect"]
""" if sweeps else ""
    path.write_text(
        f"""
[hypothesis]
id = "h5"
name = "timescale_volatility"

[experiment]
id = "betrayal_choice"
family = "trust"
rounds = {rounds}
replications = {replications}
seed = 42

[scenario]
payoff = "binary"
assignment = "agent_choice"
partners = 4
type_volatility = 0.0

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 4

[[variants]]
id = "no_affect"
affect = "none"
planning_horizon = 4

[analysis]
auto = true
primary = "h5_timescale_volatility"
compare = ["affect", "no_affect"]
{sweep_block}
""",
        encoding="utf-8",
    )
    return path


def write_benchmark_toml(path: Path, *, include_benchmark: bool = True) -> Path:
    benchmark_block = """

[benchmark]
backends = ["trust"]
agents = ["affect", "random"]

[benchmark.trust]
scenario = "resource_sharing"
""" if include_benchmark else ""
    path.write_text(
        f"""
[hypothesis]
id = "e1"
name = "benchmark_arena"

[experiment]
id = "benchmark_smoke"
family = "benchmark"
rounds = 2
replications = 1
seed = 7

[scenario]
payoff = "binary"
assignment = "random"
partners = 2

[[variants]]
id = "affect"
affect = "precision"
planning_horizon = 1
{benchmark_block}
""",
        encoding="utf-8",
    )
    return path
