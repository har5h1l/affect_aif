# Supplement: Result Provenance

## Current Evidence Contract

Current evidence must come from completed runs on the supported
factorized-control architecture using official
`inferactively-pymdp==1.0.0`.

Primary interpreted status is maintained in:

- `docs/results/current.md`
- `docs/results/runs/2026-05-18-h0-h5-rerun.md`
- `docs/results/runs/2026-05-21-h1-h3-confirmation.md`
- `docs/results/runs/2026-05-24-h3-precision-sensitivity.md`

## Frozen Repository State

Current documentation cleanup was prepared from local commit:

```text
39faa3f8834fa4805695ca65ef682af45c6942fb
```

The run notes for May 21 and May 24 did not originally record exact experiment
commits. Before submission, tag or commit the final paper packet and cite that
frozen revision in the manuscript or supplement.

## Primary Run Commands

### H0-H5 Current-Architecture Queue

See `docs/results/runs/2026-05-18-h0-h5-rerun.md` for the full run digest.

### H1/H3 Split Confirmation

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml --config configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml --output-dir results --batch-name confirm_h1_h3_split_20260519 --workers 3
python scripts/analysis/analyze.py --results results/confirm_h1_h3_split_20260519/h1/reliability_vs_reward_confirm/results.csv --output-dir results/confirm_h1_h3_split_20260519/h1/reliability_vs_reward_confirm/analysis
python scripts/analysis/analyze.py --results results/confirm_h1_h3_split_20260519/h3/betrayal_reallocation_confirm/results.csv --output-dir results/confirm_h1_h3_split_20260519/h3/betrayal_reallocation_confirm/analysis
```

### H3 Precision Sensitivity

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity.toml --config configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity_gradual.toml --output-dir results --batch-name h3_precision_sensitivity_20260522 --workers 12
python scripts/analysis/analyze.py --results results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/results.csv --output-dir results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/analysis
python scripts/analysis/analyze.py --results results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/results.csv --output-dir results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/analysis
```

## Current Result Read

| Card | Current status | Evidence tier |
|---|---|---|
| H0 | Supported with caveat | Primary queue plus H0/H2 confirmation. |
| H1 | Supported | 30-seed split confirmation. |
| H2 | Supported | Open-regime lesion confirmation. |
| H3 | Boundary condition | 30-seed confirmation plus precision-sensitivity follow-up. |
| H4 | Supported behaviorally | Partner-choice confirmation. |
| H5 | Supported for dynamics | Primary queue and sensitivity outputs; payoff underpowered. |
