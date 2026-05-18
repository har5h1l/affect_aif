# Current Results

Current interpreted evidence is promoted from the completed May 2026 H0-H5 run
queue on the supported apashea-aligned, factorized-control architecture.

Primary provenance:

- Server commit: `9f436d6` (`feat(analysis): add behavior-card diagnostics`)
- Primary batch: `results/updated_h0_h5_20260517_w2/`
- Remainder batch: `results/updated_h0_h5_20260518_remainder/`
- Analysis entry point: `scripts/analysis/analyze.py`
- Local evidence copy: compact analysis artifacts, logs, configs, and metadata
  were fetched into `results/`; full row-level `results.csv` files remain on
  `server:~/repos/affect_aif/results/` because the completed raw outputs are
  roughly 27 GB.

See `docs/results/runs/2026-05-18-h0-h5-rerun.md` for the run-level
interpretation.

## Current Read

The central result is conditional, not global: affective precision clearly moves
policy entropy and partner-choice behavior in open regimes, but it is not
monotonically payoff-improving. Precision is useful when it sharpens a good
deployment signal; it can also confidently amplify a bad post-switch model.

## Hypothesis Scorecard

| Card | Current status | Evidence read |
|---|---|---|
| H0 Openness Gate | Supported with caveat | Affect has little room in shallow binary but lowers entropy and can improve payoff in graded choice. Openness is necessary but not sufficient: the graded betrayal run shows lower entropy with worse total payoff. |
| H1 Model Fitness | Supported as pilot | Targeted partner-level analysis shows precision tracks surprise more strongly than realized partner payoff in H1 (`|r| = 0.665` vs `0.414`). This is the right dissociation, but still needs higher-rep confirmation. |
| H2 Deployment | Supported | In the open graded-choice regime, affect and lesioned/no-affect have similar belief accuracy while affect improves payoff by +25.2 and lowers policy entropy. |
| H3 Stress Response | Boundary condition / needs redesign | Post-switch affect shows stronger precision-surprise coupling, but also higher wrong-type and overconfident-wrong-belief rates after betrayal. Current H3 is evidence that affect can misdeploy under volatility, not a clean recovery win. |
| H4 Social Choice | Supported behaviorally | Affect changes partner-selection distribution and policy entropy while payoff is essentially flat. This is the expected signature for partner-choice behavior changing before total reward moves. |
| H5 Perturbation Phenotypes | Supported for dynamics; payoff underpowered | Clinical-like variants separate in beta range, entropy, partner selection, and payoff ordering, but payoff pairwise tests are mostly not significant with five seeds. |

## What This Means

The project is no longer in the "no current evidence" state. The H0-H5 queue
establishes that the precision channel is behaviorally active on the current
runtime. The next scientific decision is whether to treat the current evidence
as a pilot result and run higher-replication confirmation, while revising the
stress-response design so H3 isolates reallocation/recovery from overconfident
wrong-belief deployment.

## Current Architecture Requirement

Current evidence must continue to use the apashea-aligned model surface:

- factorized binary controls
- policy log-priors
- optional Dirichlet learning hooks where configured
- current Hesp-extension H0-H5 behavior cards
- official `inferactively-pymdp==1.0.0`

## Interpretation Guard

Before updating result interpretation from new experiment outputs, ask the user
unless the user has explicitly requested the doc update in the current turn.
