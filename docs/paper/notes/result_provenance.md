# Supplement: Result Provenance

## Current Evidence Contract

Current evidence must come from completed runs on the supported
factorized-control architecture using official
`inferactively-pymdp==1.0.0`.

Primary interpreted status is maintained in:

- `docs/results/current.md`
- `docs/paper/manuscript/results_digest.md`
- `docs/active/progress.md`

## Frozen Repository State

Current planning/provenance cleanup began from pushed `master` commit:

```text
f86ede4
```

The run notes for May 21 and May 24 did not originally record exact experiment
commits. Before submission, tag or commit the final paper packet and cite that
frozen revision in the manuscript or supplement.

## Primary Run Commands

### Post-Fix Log-Surprisal H0-H6 Smoke

Current smoke batch:

```text
results/log_surprisal_spine_smoke_postfix_20260528/
```

Run command:

```bash
MPLCONFIGDIR=/private/tmp/affect_aif_matplotlib .venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h0_policy_openness/graded_choice.toml \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml \
  --config configs/trust/hypotheses/h3_locality/global_beta_focal_switch_probe.toml \
  --config configs/trust/hypotheses/h4_social_allocation/partner_choice.toml \
  --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_choice.toml \
  --config configs/trust/hypotheses/h6_perturbation/perturbation_dynamics.toml \
  --output-dir results \
  --batch-name log_surprisal_spine_smoke_postfix_20260528 \
  --workers 1 \
  --verbose
```

Analysis outputs were generated under each experiment's `analysis/` directory.
This is three-seed smoke evidence, not final manuscript confirmation.

The earlier `results/log_surprisal_spine_smoke_20260527/` batch is retained as
pre-fix diagnostic evidence only because it exposed the agent-choice
candidate-aggregation bug in the beta-to-gamma path.

### Historical H0-H5 Current-Architecture Queue

See `docs/results/runs/2026-05-18-h0-h5-rerun.md` for the historical bounded-
error run digest. Do not reuse those numbers as current evidence after the
log-surprisal cutover.

### Historical H1/H5 Split Confirmation

This run predates the current log-surprisal spine and the corrected
active-encounter H1 readout. Keep it as provenance only; do not use it as
current manuscript evidence.

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation_confirm.toml --output-dir results --batch-name confirm_h1_h3_split_20260519 --workers 1
python scripts/analysis/analyze.py --results results/confirm_h1_h3_split_20260519/h1/reliability_vs_reward_confirm/results.csv --output-dir results/confirm_h1_h3_split_20260519/h1/reliability_vs_reward_confirm/analysis
python scripts/analysis/analyze.py --results results/confirm_h1_h3_split_20260519/h3/betrayal_reallocation_confirm/results.csv --output-dir results/confirm_h1_h3_split_20260519/h3/betrayal_reallocation_confirm/analysis
```

H1 reached structural finality on June 6 (30-seed confirmation). The diagnostic
ladder in `docs/paper/notes/limitations_and_followups.md` is for reviewer-driven
escalation only, not a current manuscript gate.

### Historical H5 Precision Sensitivity

This run also predates the current log-surprisal spine. Treat it as historical
stress-boundary provenance until rerun under current H5 configs and analysis.

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_precision_sensitivity.toml --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_precision_sensitivity_gradual.toml --output-dir results --batch-name h3_precision_sensitivity_20260522 --workers 1
python scripts/analysis/analyze.py --results results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/results.csv --output-dir results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/analysis
python scripts/analysis/analyze.py --results results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/results.csv --output-dir results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/analysis
```

## Current Result Read

| Card | Current status | Evidence tier |
|---|---|---|
| H0 | Mixed | Post-fix three-seed smoke; active entropy channel, no local-affect payoff win. |
| H1 | Confirmed | June 6 30-seed confirmation preserves the surprise-over-reward model-fitness diagnostic after active-encounter controls; payoff favors no-affect, so do not frame as reward gain. |
| H2 | Deployment active | Post-fix three-seed smoke; lesion/no-affect match, local affect changes entropy but not payoff. |
| H3 | Decomposition only | Post-fix three-seed smoke; global beta has higher aggregate payoff, local beta remains cleaner as a partner-specific signal. |
| H4 | Underpowered | Post-fix three-seed smoke; keep supplemental until confirmation. |
| H5 | Confirmed | 30-seed confirmation (`results/log_surprisal_h5_confirm_postfix_20260604/`); use `manuscript/source_tables/h5_evidence_effect_summary.csv`. |
| H6 | Dynamics only | Post-fix three-seed smoke; beta ranges separate, no clinical validation. |
