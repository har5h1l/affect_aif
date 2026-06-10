# 2026-05-26 H4 Social-Choice Pair Check

## Status

This is a completed five-seed rerun of the maintained H4 partner-choice config.
It is not a 30-seed confirmation, but it provides a clean affect-vs-no-affect
pair check after the H6 follow-up work.

Current note: the completed June 2026 30-seed binary H4 confirmation is
retained under `results/diagnostics/social_allocation/` as diagnostic
provenance only. It does not replace the graded paper Section 3.3
partner-selection readout.

## Provenance

- Batch: `results/h4_social_choice_paircheck_20260526/`
- Config: `configs/trust/hypotheses/h4_social_choice/partner_choice.toml`
- Runtime: official `inferactively-pymdp==1.0.0`
- Size: 2 variants x 5 seeds x 200 rounds = `2,000` rows
- Worker count: `--workers 1`
- Status: completed and analyzed
- Analysis:
  `results/h4_social_choice_paircheck_20260526/h4/partner_choice/analysis/`

Run command:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h4_social_choice/partner_choice.toml \
  --output-dir results \
  --batch-name h4_social_choice_paircheck_20260526 \
  --workers 1
```

Analysis command:

```bash
.venv/bin/python scripts/analysis/analyze.py \
  --results results/h4_social_choice_paircheck_20260526/h4/partner_choice/results.csv \
  --output-dir results/h4_social_choice_paircheck_20260526/h4/partner_choice/analysis
```

## Readout

The pair check reproduces the existing H4 pattern: partner-local precision
changes deployment and selection sharpness, but not total payoff.

| Readout | Affect | No affect | Difference |
|---|---:|---:|---:|
| Total payoff | `393.6` | `393.2` | `+0.4` |
| Mean policy entropy | `3.989` | `4.833` | `-0.844` |
| Mean joint accuracy | `0.416` | `0.408` | `+0.008` |
| Mean stance accuracy | `0.944` | `0.945` | `-0.001` |

Pairwise payoff is flat (`p = 0.992`). The entropy effect is large relative to
seed variance (`d = -4.07`, bootstrap CI `[-1.051, -0.601]`). The
model-fitness readout remains positive: `|corr(precision, surprise)| -
|corr(precision, reward)| = 0.191`, bootstrap CI `[0.070, 0.352]`.

## Interpretation

This supports writing H4 as a behavioral deployment effect, not a payoff effect.
The partner-choice regime exposes approach/avoidance and policy concentration:
affect changes the distribution over choices even when aggregate return is
nearly identical. The result should not be over-sold as a reward advantage.

## Follow-Up

The 30-seed H4 confirmation config was started separately under
`results/h4_social_choice_confirm_20260526/` and stopped after 5 no-affect seeds
because the one-worker run was too slow for the interactive loop. That partial
batch is marked `ABORTED_DO_NOT_USE.md` and should not be interpreted unless it
is intentionally resumed to completion.
