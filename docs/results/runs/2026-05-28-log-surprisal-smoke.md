# 2026-05-28 Log-Surprisal Spine Smoke

## Status

Completed reduced H0-H6 smoke under the canonical Hesp-style partner-action
surprisal update. This run is now pre-fix diagnostic evidence because H5
follow-up found an agent-choice candidate aggregation bug in the beta-to-gamma
path.

```text
epsilon = -log P(observed partner action)
sigma_0_sq = (-log 0.5)^2
```

Batch root:

```text
results/log_surprisal_spine_smoke_20260527/
```

This run is diagnostic smoke evidence only: three seeds per variant, one
worker, no promotion to final manuscript statistics. It should be rerun after
the centered-logit agent-choice fix.

## Command

```bash
MPLCONFIGDIR=/private/tmp/affect_aif_matplotlib .venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h0_policy_openness/graded_choice.toml \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml \
  --config configs/trust/hypotheses/h3_locality/global_beta_focal_switch_probe.toml \
  --config configs/trust/hypotheses/h4_social_allocation/partner_choice.toml \
  --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_choice.toml \
  --config configs/trust/hypotheses/h6_perturbation/clinical_dynamics.toml \
  --output-dir results \
  --batch-name log_surprisal_spine_smoke_20260527 \
  --workers 1 \
  --verbose
```

## Integrity

| Card | Experiment | Tasks | Rows | Seeds | Rounds |
|---|---|---:|---:|---|---|
| H0 | `graded_choice` | 9 | 1,800 | 42-44 | 0-199 |
| H1 | `reliability_vs_reward` | 9 | 1,800 | 42-44 | 0-199 |
| H2 | `lesion_open_regime` | 12 | 2,400 | 42-44 | 0-199 |
| H3 | `global_beta_focal_switch_probe` | 12 | 1,200 | 910-912 | 0-99 |
| H4 | `partner_choice` | 9 | 1,800 | 42-44 | 0-199 |
| H5 | `betrayal_choice` | 12 | 1,440 | 42-44 | 0-119 |
| H6 | `clinical_dynamics` | 12 | 2,400 | 42-44 | 0-199 |

All seven `results.csv` files and all analysis outputs exist.

## Interpretation

H1 remains the cleanest positive mechanism read. Local beta tracks predictive
surprise more than reward (`0.646` versus `0.109`), while global beta is weaker
and reward-leaning (`0.194` versus `0.254`).

H0/H2 show that the beta-to-gamma path is behaviorally active, but not that it
improves payoff. Local affect lowers entropy in the open graded regime
(`7.89` versus `8.79` for no-affect) while payoff is slightly worse (`1847.0`
versus `1864.2`). Global beta has the highest mean payoff (`1920.3`) but high
variance.

H3 supports locality as signal quality, not behavioral necessity. Local beta has
the cleanest partner-specific model-fitness signature (`0.943` surprise versus
`0.110` reward), but payoff is not better than no-affect or global beta.

H5 is the main follow-up risk. Local affect underperforms no-affect/lesioned in
betrayal choice (`1127.0` versus `1225.0`) and has much lower joint accuracy
(`0.067` versus `0.425`). The issue is not simple over-return to the switched
partner: local affect has a lower switched-partner reencounter rate (`0.037`)
than no-affect/lesioned (`0.322`). The likely question is why precision-driven
deployment reallocates to poorer post-switch interactions.

H4 and H6 remain supplemental at this scale. H4 payoff is noisy, and H6
separates beta dynamics without supporting clinical validation claims.

## Follow-Up Required

Before confirmation-scale reruns:

1. Complete the post-fix H5 probe at
   `results/log_surprisal_h5_candidate_fix_probe_20260528/`.
2. Rerun the reduced H0-H6 smoke under the centered-logit selector.
3. Inspect H1 payoff-versus-accuracy dissociation under local and global beta.
4. Keep H3 framed as signal quality versus behavior unless a post-fix larger
   run changes the allocation/payoff read.
