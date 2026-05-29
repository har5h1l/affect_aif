# Project Roadmap

This roadmap tracks the public research direction for `affect_aif`. The current
project is no longer organized around the older C1-C5 phase scorecard. Current
claims use the H0-H8 behavior-card spine in `docs/theory/hypotheses.md` and the
completed current-architecture evidence in `docs/results/current.md`.

## Current Status

The supported trust-task architecture is in place:

- official `inferactively-pymdp==1.0.0` is the active inference runtime
- project code owns trust-task matrices, environments, beta tracking, logging,
  experiment runners, and analysis
- binary trust games use factorized controls
- affective precision is partner-local and deployed as
  `gamma_k = gamma_base / E[beta_k]`
- current historical evidence comes from the May 2026 H0-H5 queue, the 30-seed
  H1/timescale confirmation batch, and the precision-sensitivity follow-up

The immediate research phase is **write-up stabilization**. There is no
required experiment queue before a public narrative draft.

The paper-facing packet is maintained under `docs/paper/`.

## Current Scientific Read

The central result is conditional:

```text
partner prediction reliability
  -> partner-specific precision
  -> policy-posterior shift
  -> action or partner-choice behavior
  -> payoff, reallocation, or misdeployment
```

Affective precision is behaviorally active, but it is not a monotonic reward
booster. It helps when the policy space is open and the partner model remains
useful. Under stress, it can also sharpen a wrong post-switch model and reduce
payoff.

Current evidence summary:

| Card | Status | Public-facing read |
|---|---|---|
| H0 Policy Openness | Supported with caveat | Affect has little room in saturated regimes, but moves policy entropy and behavior in open regimes. Openness is necessary, not sufficient. |
| H1 Model Fitness | Supported | Precision tracks predictive reliability more than realized reward; this is the cleanest current mechanism result. |
| H2 Deployment | Supported | Lesion/no-affect can preserve partner inference while changing policy deployment. |
| H3 Locality / Global Precision | Discovery only | Local beta preserves a cleaner model-fitness signal than global beta in small probes, but has not shown better aggregate payoff. |
| H4 Social Allocation | Supported behaviorally | Partner selection and policy entropy move even when total payoff is flat. |
| H5 Timescale / Volatility | Boundary condition confirmed | Abrupt stress exposes precision-driven misdeployment risk more than a clean affective recovery advantage. |
| H6 Perturbation Phenotypes | Supported for dynamics | Clinical-like variants separate in beta dynamics and behavior; payoff tests remain underpowered. |

## Near-Term Work

### 1. Write-Up Stabilization

Consolidate the public narrative around:

- affect as partner-specific model-fitness precision, not cached reward
- openness as the gate for observable policy effects
- deployment dissociation as the strongest behavioral evidence
- H5 as a timescale boundary condition, not an affect-wins-after-betrayal claim
- clinical-like variants as perturbation dynamics, not diagnoses

### 2. Documentation Hygiene

Keep public docs aligned with the current architecture:

- `docs/results/current.md` is the active evidence scorecard
- `docs/results/historical_findings.md` is the archive for pre-current claims
- old C1-C5, reward-average, Stag Hunt, Chicken, and pre-cutover claims should
  be marked historical unless rerun on the supported architecture

### 3. Optional Reviewer-Driven Experiments

Do not run more experiments by default. If a manuscript or reviewer needs a
specific check, use the verification gate in `docs/active/progress.md`
before launching a new full run.

Likely optional checks:

- H0/H2 open-regime confirmation
- H4 higher-replication partner-choice confirmation
- a specific H3 robustness variant if the stress-boundary-condition claim needs
  sharpening
- future global-beta ablation for partner-local factorization

## Future Directions

These are future research tracks, not current blockers.

1. **Human data fitting**: estimate `alpha_charge`, `beta_persistence`,
   `initial_beta`, and policy-precision coupling from behavioral data.
2. **AIF partners**: replace scripted partners with active-inference agents for
   genuine multi-agent inference.
3. **Structure learning**: test whether persistent low precision can signal
   model inadequacy and trigger model-structure search.
4. **Richer task regimes**: noisy observations, larger action spaces, delayed
   reward, coalition structure, and richer partner dynamics.
5. **Benchmarks**: keep the supported benchmark surface limited to trust-task
   baseline comparisons unless a new benchmark integration is explicitly scoped.

## Archive Note

Older phase narratives, C-condition scorecards, cross-game claims, and
reward-average comparisons are historical context. They helped motivate the
current H0-H5 spine but are not current evidence unless explicitly rerun on the
supported `inferactively-pymdp==1.0.0` architecture.
