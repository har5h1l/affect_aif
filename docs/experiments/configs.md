# Configs

Experiment configs are TOML files under `configs/`.

## Families

- `configs/paper/`: paper evidence reproduction.
- `configs/demo/`: fast demos.
- `configs/diagnostics/`: smoke checks, reviewer controls, and informative
  non-paper probes.

## Core Tables

Each trust config contains:

- `[hypothesis]`: hypothesis id/name.
- `[experiment]`: id, family, rounds, replications, seed.
- `[scenario]`: payoff mode, assignment mode, partners, switches, and payoff
  parameters.
- `[[variants]]`: explicit affect/planning/precision variants.
- optional `[[sweeps]]`: parameter expansion over selected variants.
- optional `[analysis]`: configured analysis contract.

Legacy condition ids and presets are intentionally unsupported. Public configs
should be readable as explicit variants.
