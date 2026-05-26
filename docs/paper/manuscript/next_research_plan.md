# Next Research Plan

## Goal

Reveal new structure for the manuscript rather than simply adding more seeds.
Full-seed confirmations should wait until the architecture, logging, and paper
figures are stable. All local runs should use `--workers 1` unless the user
explicitly authorizes otherwise.

## Current Position

The manuscript can already support a constrained claim:

- partner-local precision tracks predictive reliability more than reward;
- it changes deployment in open policy regimes;
- it shifts partner choice before payoff clearly separates;
- abrupt betrayal exposes misdeployment rather than recovery.

The main unresolved architectural question is whether partner-local beta is
necessary. A reviewer can still ask whether one shared global model-fitness
tracker would explain the same effects.

## Priority 1: Global-Beta Ablation

**Purpose.** Test whether partner-local precision is necessary, or whether a
single global volatility/model-fitness tracker explains the same behavior.

**Condition.** Add `global_beta` as a fourth affect condition alongside
`none`, `precision`, and `tracked_only`.

- Maintain one categorical beta posterior shared across all partners.
- Update that posterior after every interaction using the existing
  `epsilon -> phi -> q(beta)` rule.
- Set every candidate policy's precision with
  `gamma = gamma_base / E[global_beta]`.
- Keep all partner-local POMDP beliefs unchanged.
- Log global beta, per-partner local beta when available, selected partner,
  partner-indexed surprise, payoff, entropy, and gamma used.

**Smoke pass.** Run 3-5 seeds first, not 30:

- H1 reliability-versus-reward;
- H2 open-regime deployment;
- H4 partner choice;
- H3 abrupt betrayal if the first three smoke tests pass.

**Decision rule.**

- If global beta matches partner-local beta on H1/H2/H4/H3, soften manuscript
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
- Do not treat H5 labels as clinical validation.
- Do not start a run expected to take more than 30 minutes in an interactive
  session without explicit approval.
- Keep all experiment commands at `--workers 1`.

