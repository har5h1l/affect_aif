# Result Summaries

This directory is the public result scaffold. Git tracks compact summaries,
manifests, and README files. Full per-round trajectories named `results.csv`
are intentionally ignored and live in the Drive packet or can be regenerated.

## Paper Results

- `paper/01_predictability_value/`
- `paper/02_deployment_ablation/`
- `paper/03_partner_selection/`
- `paper/04_betrayal_adaptation/`
- `paper/05a_alpha_sweep/`
- `paper/05b_prior_factorial/`
- `paper/05c_forgiveness/`

The full suite map is `paper/manifest.json`.

## Diagnostics

`diagnostics/` contains complete informative non-paper runs that remain
runnable from public configs.

- `diagnostics/model_fitness/` — binary H1 confirmation retained as supplementary provenance only.
- `diagnostics/social_allocation/` — binary H4 partner-choice confirmation
  retained as boundary provenance only; paper partner selection remains graded.

## Future Extensions

`future/` contains compact summaries for implemented follow-up surfaces that
are not paper evidence.

- `future/mixed_volatility/` — heterogeneous-volatility extension retained for
  future change-detection work.
