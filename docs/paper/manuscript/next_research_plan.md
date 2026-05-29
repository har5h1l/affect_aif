# Next Research Plan

## Goal

Reveal new structure for the manuscript rather than simply adding more seeds.
Full-seed confirmations should wait until the architecture, logging, and paper
figures are stable. All local runs should use `--workers 1` unless the user
explicitly authorizes otherwise.

## Current Position

The manuscript can already support a constrained claim:

- it changes deployment in open policy regimes;
- it shifts partner choice before payoff clearly separates;
- abrupt betrayal is repaired under the centered selector at smoke scale.

The post-fix H1 smoke does not currently support the stronger claim that
partner-local precision tracks predictive reliability more than reward.

The main unresolved architectural question is whether partner-local beta is
necessary. A reviewer can still ask whether one shared global model-fitness
tracker would explain the same effects.

## Priority 1: Confirm H5 Betrayal

**Status.** The post-fix three-seed smoke completed under
`results/log_surprisal_spine_smoke_postfix_20260528/`. H5 is the strongest
current behavioral anchor: local affect beats no-affect/lesioned after abrupt
betrayal.

**Purpose.** Replace the smoke-scale H5 result with publication-grade evidence
under the corrected centered selector.

**Next run.** This is a more-seeds confirmation, so do not launch it without
explicit approval:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation_confirm.toml \
  --output-dir results \
  --batch-name log_surprisal_h5_confirm_postfix_20260529 \
  --workers 1
```

## Priority 2: Rework H1 Reliability Versus Reward

The post-fix H1 smoke does not preserve the old model-fitness readout:
`|corr(precision, surprise)| = 0.226` versus
`|corr(precision, payoff)| = 0.615` for local affect. Before adding seeds,
inspect whether the current H1 task is measuring reward exposure rather than
predictive reliability under partner-action surprisal.

Run only design-level or diagnostic checks here unless the user explicitly asks
for a higher-seed confirmation.

## Priority 3: Global-Beta Ablation

**Purpose.** Test whether partner-local precision is necessary, or whether a
single global volatility/model-fitness tracker explains the same behavior.

**Condition.** `global_beta` is a fourth affect condition alongside `none`,
`precision`, and `tracked_only`.

- Maintain one categorical beta posterior shared across all partners.
- Update that posterior after every interaction using the existing
  `epsilon -> phi -> q(beta)` rule.
- Set every candidate policy's precision with
  `gamma = gamma_base / E[global_beta]`.
- Keep all partner-local POMDP beliefs unchanged.
- Log global beta, per-partner local beta when available, selected partner,
  partner-indexed surprise, payoff, entropy, and gamma used.

**Next smoke pass.** After reviewing the H3 locality quick smoke, run 3-5 seeds first,
not 30, on the older manuscript regimes:

- H1 reliability-versus-reward;
- H2 open-regime deployment;
- H4 partner choice;
- H5 abrupt betrayal if the first three smoke tests pass.
- H3 locality/interference only after changing the design or diagnostics; the
  first quick smoke has already run.

**Decision rule.**

- If global beta matches partner-local beta on H1/H2/H4/H5, soften manuscript
  language from "partner-specific is necessary" to "partner-specific is an
  interpretable implementation."
- If global beta spreads precision changes to unaffected partners or blurs
  partner-specific reallocation, promote locality as a stronger manuscript
  claim after user review of the new results.

## Priority 2: Locality/Interference Diagnostic

**Working claim.** Partner-local affect should contain volatility to the
partner whose model failed; global affect should contaminate decisions about
partners whose behavior did not change.

**Task design.** Use four partners:

- stable cooperator;
- reliable exploiter;
- random or volatile partner;
- scheduled stance-switch partner.

The first implemented version uses
`configs/trust/hypotheses/h3_locality/global_beta_smoke.toml`:
two seeds, 40 rounds, one scheduled stance switch, and variants `none`,
`precision`, `tracked_only`, and `global_beta`.

**Variants.** Compare:

- `none`;
- `precision`;
- `tracked_only`;
- `global_beta`.

**Primary readouts.**

- beta or precision trajectory per partner;
- selection rate before and after the scheduled switch;
- policy entropy conditional on selected partner;
- payoff conditional on selected partner;
- KL shift in policy posterior for untouched partners after the switched
  partner changes;
- entropy and payoff for unaffected partners after betrayal elsewhere.

Current analysis outputs include `cross_partner_interference_summary.csv` and
`global_vs_local_beta_summary.csv` from `scripts/analysis/analyze.py`.

**Manuscript value.** This is the cleanest test of the title claim. The
important result is not simply payoff. It is whether local beta confines
precision changes while global beta causes cross-partner interference.

## Priority 3: Figure-Quality Script

Before broad reruns, add `scripts/analysis/make_paper_figures.py`.

**Inputs.** Canonical analysis CSVs and source tables already referenced in
`docs/paper/manuscript/results_digest.md`.

**Outputs.**

- model-fitness dissociation;
- deployment payoff/entropy/belief readouts;
- partner-choice selection and entropy;
- betrayal payoff/entropy/reencounters/wrong-type-on-return;
- shock-shape payoff/entropy;
- supplemental beta-range perturbation dynamics.

**Reason.** This makes current and future evidence reviewable. It also prevents
manual plot edits from drifting away from the source CSVs.

## Priority 4: Lesion Family Discovery

Only after global beta and locality diagnostics are smoke-tested, expand the
lesion family.

Candidate variants:

- frozen beta: no beta updates and fixed gamma;
- tracked-only decouple: current lesion, beta updates but gamma is fixed;
- delayed deployment: gamma uses beta from `d` rounds ago;
- noisy beta: beta update receives injected noise;
- asymmetric charge: negative surprises have higher gain than positive
  surprises;
- joint-surprise beta: beta uses action+payoff likelihood rather than partner
  action only;
- global beta: shared beta state.

Report dynamics first: beta range, entropy, choice churn, return latency, and
wrong-type-on-return. Payoff should remain secondary.

## Priority 5: Shock-Timing Gradient

Continue the shock-shape line only if it answers timing.

Hold default affect fixed and vary:

- abrupt switch in one round;
- gradual switch over 3, 5, and 10 rounds;
- pre-switch confirmation length;
- observation noise.

The key metric is lag between beta reaction and stance/type belief
recalibration. This directly tests the proposed misdeployment mechanism.

## Stop Rules

- Do not run full 30-seed sweeps until smoke logs and analysis outputs are
  verified.
- Do not rewrite manuscript claims from new outputs without user review.
- Do not treat H6 labels as clinical validation.
- Do not start a run expected to take more than 30 minutes in an interactive
  session without explicit approval.
- Keep all experiment commands at `--workers 1`.
