# Current Results

Current interpreted evidence has two tiers. The primary evidence is promoted
from the completed May 2026 H0-H5 run queue on the supported apashea-aligned,
factorized-control architecture. The May 19 H3 reallocation run is recorded as
a small follow-up pilot, not as equivalent confirmation evidence.

Primary provenance:

- Server commit: `9f436d6` (`feat(analysis): add behavior-card diagnostics`)
- Primary May batch: `results/updated_h0_h5_20260517_w2/`
- May remainder batch: `results/updated_h0_h5_20260518_remainder/`
- Latest local H0/H1/H2/H4 artifacts:
  `results/confirm_h0_h1_h2_h4_20260518/`
- Follow-up pilot: `results/h3_reallocation_followup_20260519/`
- Analysis entry point: `scripts/analysis/analyze.py`
- Server evidence copy: current/provenance-bearing batches are retained under
  `results/`; superseded pilot, incomplete, and duplicate local result
  directories have been removed. Full row-level outputs remain large, so
  non-server checkouts should fetch only the artifacts they need.

See `docs/results/runs/2026-05-18-h0-h5-rerun.md` for the run-level
interpretation.

## Current Read

The central result is conditional, not global: affective precision clearly moves
policy entropy, partner choice, and deployment when the policy space is open,
but it is not monotonically payoff-improving. Precision can guide deployment or
reallocation when it sharpens a good signal; it can also confidently amplify a
bad post-switch model.

## Hypothesis Scorecard

| Card | Current status | Evidence read |
|---|---|---|
| H0 Openness Gate | Supported with caveat | Affect has little room in shallow binary but lowers entropy and can improve payoff in graded choice. Openness is necessary but not sufficient: the graded betrayal run shows lower entropy with worse total payoff. |
| H1 Model Fitness | Supported as pilot | Targeted partner-level analysis shows precision tracks surprise more strongly than realized partner payoff in H1 (`|r| = 0.665` vs `0.414`). This is the right dissociation, but still needs higher-rep confirmation. |
| H2 Deployment | Supported | In the open graded-choice regime, affect and lesioned/no-affect have similar belief accuracy while affect improves payoff by +25.2 and lowers policy entropy. |
| H3 Stress Response | Split pilot / boundary condition | The May 18 H3 run showed lower entropy with higher wrong-type and overconfident-wrong rates after betrayal. The May 19 reallocation pilot adds the other face: affect returns later/less often to the switched partner, with better payoff conditional on return. H3 should read as adaptive reallocation plus misdeployment risk, not an affect payoff win. |
| H4 Social Choice | Supported behaviorally | Affect changes partner-selection distribution and policy entropy while payoff is essentially flat. This is the expected signature for partner-choice behavior changing before total reward moves. |
| H5 Perturbation Phenotypes | Supported for dynamics; payoff underpowered | Clinical-like variants separate in beta range, entropy, partner selection, and payoff ordering, but payoff pairwise tests are mostly not significant with five seeds. |

## What This Means

The project is no longer in the "no current evidence" state. The H0-H5 queue
establishes that the precision channel is behaviorally active on the current
runtime. The project should now be treated as entering write-up stabilization:
consolidate the evidence hierarchy, keep H3 split into reallocation and
misdeployment readouts, and defer more experiments unless higher-replication
confirmation is explicitly needed.

May 19 H3 pilot read: affect has lower whole-run payoff (`1114.3` vs `1138.9`
for no-affect/lesion), but it re-encounters the switched partner less often
(`2.6` vs `3.4` mean re-encounters; `0.029` vs `0.038` selection rate), waits
longer before first return (`30.6` vs `15.25` decisions among returned runs),
and earns better payoff conditional on return (`9.20` vs `8.24`). Read
`betrayal_reallocation_summary.csv` alongside
`betrayal_misdeployment_summary.csv`.

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
