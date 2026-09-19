# Experiment Execution

This layer turns a TOML configuration into reproducible trust-game episodes.
Start from [the CLI](../scripts/experiment/run.py), then follow:

| File | Responsibility |
|---|---|
| [trust/spec.py](trust/spec.py) | Parse configs and expand variants, sweeps, and replications. |
| [trust/config.py](trust/config.py) | Runtime parameter representation. |
| [trust/factory.py](trust/factory.py) | Construct the environment, pymdp agents, and confidence tracker. |
| [trust/batch.py](trust/batch.py) | Coordinate expanded runs and workers. |
| [trust/runner.py](trust/runner.py) | Execute each episode and coordinate observation/update order. |
| [trust/logger.py](trust/logger.py) and [trust/diagnostics.py](trust/diagnostics.py) | Assemble recorded metrics and runtime diagnostics. |
| [trust/output_layout.py](trust/output_layout.py) | Resolve default or custom output paths. |
| [trust/progress.py](trust/progress.py) | Report execution progress. |

The agent and environment mechanics belong to [tasks/](../tasks/README.md);
post-hoc metrics belong to [analysis/](../analysis/README.md).

`multifocal/` is the reciprocal AIF prototype. It is separate from the paper's
focal-agent CLI/config route and is not paper evidence.

See [Running experiments](../docs/guide/running.md) for commands and
[Configs](../docs/guide/configs.md) for the schema and output map.
