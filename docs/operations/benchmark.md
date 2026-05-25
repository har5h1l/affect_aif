# Evaluation Arena

The maintained benchmark surface is the trust-task evaluation arena. It is for
comparing the project agents against simple trust-task baselines under common
scenario definitions; it is not a separate paper experiment family.

## Scope

- `trust` is the only supported benchmark backend.
- Benchmark-family TOML specs live under `configs/benchmark/`.
- The canonical runner is `scripts/benchmark/run.py`.
- The canonical analyzer is `scripts/benchmark/analyze.py`.

Historical external benchmark experiments were removed from the supported
surface. They should not be cited as current evidence for this project.

## Config Model

Authored benchmark configs are unified TOML `ExperimentSpec` files with
`experiment.family = "benchmark"`. Trust-specific settings live under
`[benchmark.trust]`; all agents are named registry agents.

Common agents:

- `affect`
- `no_affect`
- `random`
- `tit_for_tat`
- `pavlov`
- `grim_trigger`

Recommended trust benchmark configs:

- `configs/benchmark/e1_arena/default.toml`
- `configs/benchmark/e1_arena/betrayal.toml`
- `configs/benchmark/e1_arena/full.toml`

## Output Schema

All benchmark rows include:

- `schema_version`
- `backend`
- `scenario`
- `agent_name`
- `seed`
- `episode_id`
- `step`
- `reward`

Trust rows may also include task-specific fields such as `payoff`,
`partner_action`, `true_partner_type`, `type_switched`, and
`inferred_type_correct`.

## Commands

```bash
python scripts/benchmark/run.py --config configs/benchmark/e1_arena/default.toml
python scripts/benchmark/run.py --backend trust --agents affect random tit_for_tat --rounds 50 --replications 3
python scripts/benchmark/analyze.py --results results/benchmark/benchmark_results.csv
```

Analysis outputs are written next to the CSV by default:

- `benchmark_shared_summary.csv`
- `benchmark_trust_summary.csv`
- `benchmark_report.txt`

Keep theory-facing hypothesis reads in `configs/trust/hypotheses/` and
`docs/results/`. Use the benchmark arena for baseline sanity checks and
comparative task behavior only.
