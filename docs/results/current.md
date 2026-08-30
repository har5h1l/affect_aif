# Current Results

> **Camera-ready canonical evidence.** The values in this file are generated
> from the corrected shared-action policy space with the linear affective-charge
> update. The earlier submitted factorized-action/squared-charge results and the
> intermediate shared-action/squared-charge rebaseline are retained as revision
> provenance on the server but are not current claim-bearing evidence.

Canonical interpreted evidence for the active architecture is stored under
`results/paper/`. Manuscript prose lives in `docs/manuscript/sections/`;
paper-facing compact CSVs live in `docs/manuscript/source_tables/`.

## Inclusion Decision

Use only the corrected-linear tables under `docs/manuscript/source_tables/`
and the matching compact cards under `results/paper/` for camera-ready numbers.
Squared charge is a diagnostic robustness condition. Historical, pre-fix,
incomplete, smoke, and binary-confirmation outputs are not paper evidence.

| Evidence family | Source table | Scale | Status |
|---|---|---:|---|
| Predictability over payoff | `docs/manuscript/source_tables/h1_model_fitness_confirm/model_fitness_correlation_summary.csv` | 30 seed clusters | current |
| Deployment ablation | `docs/manuscript/source_tables/h2_deployment_pathway_summary.csv` | 30 paired seeds | current |
| Partner selection | `docs/manuscript/source_tables/h4_partner_choice_summary.csv` | 30 paired seeds | current, type-allocation headline retired |
| Abrupt betrayal | `docs/manuscript/source_tables/h5_evidence_effect_summary.csv` | 30 paired seeds | current |
| Alpha sweep | `docs/manuscript/source_tables/alpha_sweep/metrics.csv` | 20 seeds per cell | current, condition-specific |
| Prior factorial | `docs/manuscript/source_tables/prior_factorial/metrics.csv` | 20 seeds per cell | current, condition-specific |
| Forgiveness | `docs/manuscript/source_tables/forgiveness/metrics.csv` | 20 seeds per cell | current, condition-specific |

## Provenance

- Canonical suite manifest: `results/paper/manifest.json`
- Figure and source-table map: `docs/results/provenance.md`
- Config-to-result routes: `docs/results/config_map.md`
- Bootstrap contract: 10,000 percentile resamples, bootstrap seed 0
- Treatment-control effects: paired at the simulation-seed level
- Correlations: pooled partial correlations with a seed-cluster bootstrap
- Time courses: seed means bootstrapped within round bins

## Current Evidence Read

### Predictability over realized payoff

For partner-local beta, the partial correlation between precision and
surprisal is `-0.660` with a 95% seed-cluster interval `[-0.766, -0.492]`;
the precision-payoff partial correlation is `0.094` with interval
`[-0.112, 0.291]`. With shared beta, the corresponding values are `-0.454`
`[-0.619, -0.275]` and `0.072` `[-0.163, 0.390]`. These are construct and
locality checks, not independent validation of the update rule.

### Deployment through beta to gamma

Partner-local affect and tracked-only have similar mean within-partner temporal
beta ranges (`0.849` and `0.892`); the paired difference is `-0.043`, 95% CI
`[-0.086, 0.004]`. Deploying beta through gamma lowers mean policy
entropy from `7.657` to `6.887`; the paired difference is `-0.770`, 95% CI
`[-0.966, -0.577]`. Mean cumulative payoff is `2003.3` versus `1966.8`; the
paired difference is `36.5`, but its interval crosses zero
`[-8.6, 84.1]`.

Interpretation: tracked-only confirms that beta can update without the same
deployment effect when the beta-to-gamma pathway is cut. Full partner-local
deployment produces substantially lower policy entropy; payoff remains a
secondary, regime-dependent behavioral outcome rather than the definition of
the mechanism.

### Partner selection

Partner-local affect versus no affect produced mean policy entropy `6.887`
versus `7.657`, paired difference `-0.770`, 95% CI `[-0.966, -0.577]`.
Selected interactions remained broadly distributed: cooperator `29.6%` versus
`30.7%`, exploiter `24.4%` versus `22.6%`, reciprocator `22.0%` versus
`24.0%`, and random `24.0%` versus `22.7%`. All affect-minus-no-affect
type-specific intervals include zero: cooperator `-0.0115`
`[-0.0485, 0.0248]`, exploiter `0.0182` `[-0.0163, 0.0507]`, reciprocator
`-0.0200` `[-0.0468, 0.0038]`, and random `0.0133`
`[-0.0102, 0.0415]`.

Interpretation: partner-local precision sharpens commitment over
partner--investment policies, while selected interactions remain broadly
distributed across partner types. Final-linear type-specific allocation
differences are small and their paired 95% intervals include zero; do not claim
a stable preference for a particular partner type.

### Abrupt betrayal

Relative to no affect, partner-local affect lowers mean policy entropy by
`-2.149`, 95% paired CI `[-2.379, -1.895]`, raises joint type-stance accuracy
by `0.158`, CI `[0.084, 0.226]`, and raises cumulative payoff by `58.2`, CI
`[37.5, 82.3]`, in this one scripted betrayal regime.

Interpretation: accumulated confidence remains behaviorally active after abrupt
change. Lead with the policy-entropy effect; interpret joint type--stance
accuracy as downstream of altered engagement/sampling; treat the payoff
difference as specific to this tested social environment rather than a generic
reward-improvement claim.

### Gain, prior, and repair profiles

In the betrayal alpha sweep, mean beta range rises monotonically from `0.097`
at `alpha=0.05` to `0.675` at `alpha=8.0` (Spearman `rho=1.0`), while payoff
is not monotonic. In the prior-factorial betrayal results,
`naive_high_alpha` / anxious-reactive has the highest mean payoff (`2285.8`),
ahead of the default reference (`2244.2`). The detailed ranking changed under
the corrected model. Forgiveness results continue to separate reengagement,
confidence recovery, and payoff recovery. These labels describe computational
calibration profiles, not validated human or clinical phenotypes.

## Claim Boundary

Use:

- partner-local beta as an auxiliary confidence tracker deployed through gamma;
- corrected shared-action policy accounting;
- linear charge as the canonical model and squared charge as diagnostic;
- seed-level uncertainty and conditional simulation language.

Avoid:

- historical entropy, correlation, allocation, betrayal, or profile values;
- a stable partner-type preference claim;
- a general payoff-improvement claim;
- clinical validation or human-behavior generalization;
- presenting beta as a variational hidden state;
- presenting the construct checks as independent replications.
