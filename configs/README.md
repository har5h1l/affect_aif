# Configs

TOML configs are the public experiment surface. All maintained configs use the
same `ExperimentSpec` envelope and expand explicit `[[variants]]` into
seeded runs.

## Choose A Config

- `paper/`: paper evidence reproduction, numbered in manuscript-results order.
- `demo/`: fast notebook-sized configs for checking the workflow.
- `diagnostics/`: smoke checks, reviewer controls, and informative non-paper
  probes.
- `future/`: implemented exploratory extensions that are not paper evidence.

## Quick Checks

```bash
python scripts/experiment/run.py \
  --config configs/diagnostics/smoke/trust_smoke.toml \
  --batch-name smoke \
  --workers 1 \
  --dry-run
```

The demo folder mirrors the numbered paper suite at reduced scale:
`01_predictability_value.toml` through `05c_forgiveness.toml`. The notebook
runs the main spine by default and marks the profile-factorial and forgiveness
demos as optional.

```bash
python scripts/experiment/run.py \
  --config configs/paper/05a_alpha_sweep.toml \
  --batch-name alpha_dry \
  --workers 1 \
  --dry-run
```

## Paper Suite

```bash
python scripts/experiment/run.py \
  --config configs/paper/01_predictability_value.toml \
  --config configs/paper/02_deployment_ablation.toml \
  --config configs/paper/03_partner_selection.toml \
  --config configs/paper/04_betrayal_adaptation.toml \
  --config configs/paper/05a_alpha_sweep.toml \
  --config configs/paper/05b_prior_factorial.toml \
  --config configs/paper/05c_forgiveness.toml \
  --batch-name paper \
  --workers 1 \
  --dry-run
```

## Future Extensions

`configs/future/mixed_volatility.toml` implements a heterogeneous-volatility
partner-choice environment. It is a future-facing extension, not part of the
paper reproduction suite.

## Diagnostic Boundaries

Binary confirmation configs such as
`configs/diagnostics/h1_model_fitness/reliability_vs_reward_confirm.toml` and
`configs/diagnostics/h4_social_allocation/partner_choice_confirm.toml` are
diagnostic provenance only. They do not replace the graded paper configs.
