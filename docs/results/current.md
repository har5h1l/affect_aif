# Current Results

Current interpreted evidence has two tiers. The primary evidence is promoted
from the completed May 2026 H0-H5 run queue on the supported factorized-control
architecture. The May 2026 H1/H3 confirmation batch is a
targeted follow-up confirmation for the two formerly weakest split readouts,
and the H3 precision-sensitivity batch is a stress-regime robustness check for
that boundary condition. The earlier May 19 H3 reallocation run remains a small
pilot because its conditional-return advantage did not survive the
higher-replication check.

Primary provenance:

- Server commit: `9f436d6` (`feat(analysis): add behavior-card diagnostics`)
- Primary May batch: `results/updated_h0_h5_20260517_w2/`
- May remainder batch: `results/updated_h0_h5_20260518_remainder/`
- Latest local H0/H1/H2/H4 artifacts:
  `results/confirm_h0_h1_h2_h4_20260518/`
- Follow-up pilot: `results/h3_reallocation_followup_20260519/`
- H1/H3 confirmation: `results/confirm_h1_h3_split_20260519/`
- H3 precision sensitivity:
  `results/h3_precision_sensitivity_20260522/`
- Analysis entry point: `scripts/analysis/analyze.py`
- Server evidence copy: current/provenance-bearing batches are retained under
  `results/`; superseded incomplete and duplicate local result directories
  should be pruned when they are not needed. The H3 reallocation pilot is
  intentionally retained as exploratory context. Full row-level outputs remain
  large, so non-server checkouts should fetch only the artifacts they need.

See `docs/results/runs/2026-05-18-h0-h5-rerun.md` for the run-level
interpretation and `docs/results/runs/2026-05-21-h1-h3-confirmation.md` for the
targeted confirmation. See
`docs/results/runs/2026-05-24-h3-precision-sensitivity.md` for the H3
precision-sensitivity follow-up. See `docs/paper/` for the current
submission-readiness and literature-positioning read.

## Current Read

The central result is conditional, not global: affective precision clearly moves
policy entropy, partner choice, and deployment when the policy space is open,
but it is not monotonically payoff-improving. Precision can guide deployment
when it sharpens a good signal; under stress it can also confidently amplify a
bad post-switch model.

## Hypothesis Scorecard

| Card | Current status | Evidence read |
|---|---|---|
| H0 Openness Gate | Supported with caveat | Affect has little room in shallow binary but lowers entropy and can improve payoff in graded choice. Openness is necessary but not sufficient: the graded betrayal run shows lower entropy with worse total payoff. |
| H1 Model Fitness | Supported | The 30-seed confirmation strengthens the reliability-over-reward readout: precision tracks surprise more strongly than realized payoff (`|r| = 0.701` vs `0.419`), while total payoff remains flat-to-worse for affect. |
| H2 Deployment | Supported | In the open graded-choice regime, affect and lesioned/no-affect have similar belief accuracy while affect improves payoff by +25.2 and lowers policy entropy. |
| H3 Stress Response | Boundary condition sharpened | The 30-seed reallocation confirmation shows lower entropy and fewer returns to the switched partner, but worse whole-run payoff and no conditional-return payoff advantage. The precision-sensitivity follow-up shows that simple caution knobs do not rescue the abrupt betrayal regime; gradual betrayal makes default affect nearly payoff-neutral relative to baseline. H3 should read as stress exposing precision-driven misdeployment risk, especially under abrupt shocks. |
| H4 Social Choice | Supported behaviorally | Affect changes partner-selection distribution and policy entropy while payoff is essentially flat. This is the expected signature for partner-choice behavior changing before total reward moves. |
| H5 Perturbation Phenotypes | Supported for dynamics; payoff underpowered | Clinical-like variants separate in beta range, entropy, partner selection, and payoff ordering, but payoff pairwise tests are mostly not significant with five seeds. |

## What This Means

The project is no longer in the "no current evidence" state. The H0-H5 queue
establishes that the precision channel is behaviorally active on the current
runtime, and the H1/H3 confirmation removes the main uncertainty about whether
the weakest readouts were only five-seed artifacts.

H1 confirmation read: affect does not improve total payoff (`534.6` vs
`542.1`; bootstrap CI for the difference crosses zero), but the precision
signal tracks surprise more strongly than payoff (`|r| = 0.701` vs `0.419`).
This supports H1 as a model-fitness claim rather than a reward claim.

H3 confirmation read: affect has lower whole-run payoff (`1136.1` vs `1172.1`
for no-affect/lesion; pairwise `p = 0.0169`) while lowering entropy (`8.38` vs
`8.74`). It re-encounters the switched partner less often (`4.4` vs `6.1`
mean re-encounters; `0.049` vs `0.067` selection rate), but it does not wait
longer before first return (`15.6` vs `17.6` decisions among returned runs) and
does not earn better payoff conditional on return (`8.76` vs `8.91`). Read
`evidence_effect_summary.csv`, `betrayal_reallocation_summary.csv`, and
`betrayal_misdeployment_summary.csv` together.

H3 precision-sensitivity read: the abrupt betrayal sweep does not support a
simple "make affect more cautious" repair. In the abrupt run, no-affect and
lesioned remain best by total payoff (`1153.6`), while default affect is lower
but not significantly different by pairwise payoff test (`1140.4`, `p =
0.370`). The most cautious variants raise policy entropy but do worse:
combined caution reaches the highest entropy (`9.27`) and lower payoff
(`1115.0`, `p = 0.003` vs no-affect), and low gamma is similarly worse
(`1120.8`, `p = 0.016`). Caution reduces some overconfident wrong-type rates,
but it also increases returns to the switched partner and lowers payoff on
re-encounter. In the gradual betrayal run, default affect nearly matches the
baseline (`1147.6` vs `1148.9`, `p = 0.906`) while the cautious variants still
lag. This points to shock-regime dependence: the default precision channel is
most harmful when betrayal is abrupt, not because its beta dynamics are
globally too aggressive.

The project should now be treated as in write-up stabilization: consolidate the
evidence hierarchy, keep H3 split into reallocation and misdeployment readouts,
and avoid broad new experiment sweeps unless they directly test the abrupt
shock mechanism or a reviewer asks for a specific stress-regime variant.

## Current Architecture Requirement

Current evidence must continue to use the supported factorized-control model surface:

- factorized binary controls
- policy log-priors
- optional Dirichlet learning hooks where configured
- current Hesp-extension H0-H5 behavior cards
- official `inferactively-pymdp==1.0.0`

## Interpretation Guard

Before updating result interpretation from new experiment outputs, ask the user
unless the user has explicitly requested the doc update in the current turn.
