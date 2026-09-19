# Result Summaries

Experiment results, grouped below. Download the [paper data](../paper_results.zip)
and [checksum](../paper_results.zip.sha256); see the
[reproduction guide](../docs/guide/reproduce.md#use-the-published-results-without-rerunning)
for extraction instructions.

## Paper Results

- `paper/01_predictability_value/`
- `paper/02_deployment_ablation/`
- `paper/03_partner_selection/`
- `paper/04_betrayal_adaptation/`
- `paper/05a_alpha_sweep/`
- `paper/05b_prior_factorial/`
- `paper/05c_forgiveness/`

The full suite map is `paper/manifest.json`. Every config-to-result route is
documented in `docs/guide/configs.md`.

## Diagnostics

`diagnostics/` contains additional experiments not used as the main paper results.

- `diagnostics/model_fitness/` — binary H1 confirmation retained as an additional comparison.
- `diagnostics/social_allocation/` — binary H4 partner-choice confirmation
  retained as an additional comparison; paper partner selection remains graded.

## Future Extensions

`future/` contains compact summaries for exploratory experiments that
are not paper evidence.

- `future/mixed_volatility/` — heterogeneous-volatility extension retained for
  future change-detection work.
