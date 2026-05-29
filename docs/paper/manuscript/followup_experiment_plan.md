# Follow-Up Experiment Design Plan

## Purpose

The next experiment phase should strengthen the manuscript-facing result spine
while keeping H3 locality in the right evidential position. The current post-fix
H0-H6 smoke supports partner-local precision as an active deployment signal and
repairs H5 betrayal-choice behavior at smoke scale. It does not yet support the
old H1 surprise-over-reward model-fitness readout, so H1 must be confirmed or
redesigned before carrying a central manuscript claim. H3 should remain a
mechanism decomposition, not a necessity claim.

The plan has four lanes, ordered by manuscript value:

1. Confirm H5 as the repaired behavioral anchor.
2. Rework or confirm H1 before using the model-fitness claim.
3. Confirm H0/H2/H4 manuscript support only if payoff/deployment language
   remains in the draft.
4. Keep H3 as a locality/global-beta decomposition.

All runs should use `--workers 1` unless the user explicitly authorizes a
different worker count.

## Lane 1: H5 Betrayal Confirmation

### Question

Does the post-fix H5 betrayal-choice advantage survive a confirmation-scale run?

### Run

This is a more-seeds confirmation, so do not launch it without explicit user
approval.

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation_confirm.toml \
  --output-dir results \
  --batch-name log_surprisal_h5_confirm_postfix_YYYYMMDD \
  --workers 1
```

### Primary Readouts

- total payoff by variant;
- post-switch reallocation and reencounter rate;
- policy entropy and joint accuracy;
- payoff conditional on returned/switched partner.

## Lane 2: H1 Reliability-Versus-Reward Rework

### Question

Why does the post-fix smoke show local precision more payoff-correlated than
surprise-correlated?

### Next Step

Do not add seeds first. Inspect whether the current H1 task creates exposure
confounds where reward and partner-action predictability are not cleanly
separated. A useful follow-up would be a design-level diagnostic with the same
seed count, not a broad confirmation sweep.

### Primary Readouts

- partner-level action surprisal versus payoff exposure;
- whether active partner sampling changes the correlation denominator;
- whether a reliability manipulation with matched reward removes the reversal.

## Lane 3: Manuscript Support Confirmation

### Question

Do H0/H2/H4 support results hold at higher replication if the draft keeps those
claims?

### Run

This is also a more-seeds confirmation and should wait for approval.

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h0_policy_openness/graded_choice_confirm.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml \
  --config configs/trust/hypotheses/h4_social_allocation/partner_choice_confirm.toml \
  --output-dir results \
  --batch-name manuscript_open_social_confirm_YYYYMMDD \
  --workers 1
```

Promote only the readouts that replicate. Do not rewrite H3 locality into a
necessity claim from these runs.

## Lane 4: Locality / Interference Diagnostic

### Question

When one partner changes, does affective precision stay attached to the partner
whose model failed, or does it contaminate policy deployment for untouched
partners?

### Task Design

Use four partners in a single mixed regime:

- one stable cooperator;
- one reliable exploiter;
- one random or volatile partner;
- one partner with a scheduled stance switch mid-run.

The key comparison is not overall payoff first. The first readout is whether the
shock to the switching partner changes selection, entropy, or payoff for the
three partners whose behavior did not change.

### Conditions

Run the same task under:

- `local_beta`: partner-local beta updates and beta-to-policy deployment;
- `global_beta`: one shared beta posterior updated by all interactions;
- `tracked_only`: beta updates but does not set policy precision;
- `no_affect`: no beta tracker.

Keep partner-local POMDP beliefs unchanged in every condition. Only the source
of policy precision should differ.

### Primary Readouts

For each partner separately, compute pre-switch and post-switch summaries:

- selection rate;
- policy entropy conditional on selecting that partner;
- payoff conditional on selecting that partner;
- beta or gamma trajectory;
- KL shift in policy posterior for untouched partners after the switch;
- return latency to the switched partner;
- wrong-type-on-return after reencounter.

The strongest locality result would be a selective change for the switched
partner under `local_beta`, but broader entropy/payoff disruption for untouched
partners under `global_beta`.

### Smoke Run

Run 3-5 seeds first and inspect logs before any confirmation sweep:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h3_locality/global_beta_locality_probe.toml \
  --output-dir results \
  --batch-name h3_global_beta_locality_probe_YYYYMMDD \
  --workers 1
```

Analyze the smoke output before increasing replication:

```bash
.venv/bin/python scripts/analysis/analyze.py \
  --results results/h3_global_beta_locality_probe_YYYYMMDD/h3/global_beta_locality_probe/results.csv \
  --output-dir results/h3_global_beta_locality_probe_YYYYMMDD/h3/global_beta_locality_probe/analysis
```

### Current Smoke Read

The completed 2026-05-26 smoke is documented in
`docs/results/runs/2026-05-26-h6-locality-probe.md`. It should not be scaled
directly to 30 seeds yet.

The smoke verified that partner-indexed logs and analysis outputs exist, but it
did not confirm the simple prediction that global beta contaminates untouched
partners more than local beta. Local beta preserved the stronger
precision-surprise association, while global beta had better aggregate payoff.
The next design should separate those two questions explicitly.

### Promotion Rule

Promote this to a larger confirmation run only if the smoke pass shows usable
partner-indexed logs for:

- selected partner;
- payoff;
- surprise or prediction error;
- `q_pi_entropy`;
- `gamma_used` or enough beta/precision state to reconstruct the deployed
  precision;
- global beta, when present;
- local beta, when present.

Do not promote based on aggregate payoff alone. Also do not promote the exact
2026-05-26 design unless the stance-switch timing and post-switch comparison
window are revised so the same shock is cleanly represented across seeds.

## Lane 3: Global-Beta Interpretation

### Question

Does one shared beta tracker preserve the same model-fitness signal as
partner-local beta, or does it mix partner-specific reliability with overall
episode quality?

### Current Discovery Read

The global-beta discovery batch suggests that global beta is not an equivalent
replacement for partner-local beta. In the discovery probes, local beta showed a
stronger precision-surprise association, while global beta weakened or changed
that association in deployment and lesion-family settings.

This remains discovery evidence only. It should shape the next experiment and
the manuscript limitations, not support a manuscript-level necessity claim.

### Decision Criteria

After the locality smoke and any confirmation run, interpret global beta with
four questions:

- Does global beta spread precision changes to untouched partners after a shock?
- Does global beta reduce partner-selection entropy in a way that local beta
  does not?
- Does global beta track reward/payoff more than predictive surprise in
  multi-partner settings?
- If local beta preserves a cleaner reliability signal, does that signal improve
  allocation or merely concentrate choices?

If yes, the manuscript can say partner-local precision appears important for
containing volatility to the partner whose model failed. If no, soften the claim
to: partner-local precision is an interpretable implementation of a more general
volatility/fitness signal.

## Lane 4: Focused Lesion-Family Follow-Up

### Question

Which failure mode best explains maladaptive deployment: fixed precision, stale
precision, noisy precision, asymmetric updating, or global sharing?

### Run After Lane 2

Do not start with a broad lesion sweep. Add lesions only after the locality logs
are verified, because the lesion results are most useful when they can be read
against partner-specific interference metrics.

Priority lesions:

- `frozen_beta`: beta posterior never updates and precision stays fixed;
- `tracked_only_decouple`: beta updates but policy precision uses the base
  gamma;
- `delayed_deployment`: beta updates immediately but precision uses beta from
  `d` rounds earlier;
- `noisy_beta`: beta update receives controlled noise;
- `asymmetric_charge`: negative surprises receive higher gain than positive
  surprises;
- `joint_surprise_beta`: epsilon comes from joint action-plus-payoff likelihood
  rather than partner action alone.

### Readout Map

For each lesion, report dynamics before payoff:

- beta range;
- entropy change;
- choice churn;
- return latency;
- wrong-type-on-return;
- payoff conditional on selected partner;
- untouched-partner entropy and payoff after a betrayal elsewhere.

The useful product is a phenotyping table: lesion type -> expected beta
dynamics -> deployment signature -> behavioral consequence.

## Lane 5: Figure-Quality Outputs

Create one figure-generation path that reads canonical analysis CSVs and emits
reviewable PDF/PNG panels. This should happen before more exploratory sweeps,
because it turns existing evidence into inspectable manuscript material.

Required panels:

- model-fitness dissociation: precision-surprise versus precision-payoff;
- deployment dissociation: payoff, entropy, and belief readouts;
- partner choice: selection rates and partner-selection entropy;
- betrayal: payoff, entropy, reencounters, and wrong-type-on-return;
- shock shape: abrupt versus gradual payoff and entropy;
- H6 supplement: local versus global beta ranges and perturbation dynamics;
- lesion supplement: beta range, entropy, choice churn, and return latency by
  lesion type.

Recommended output location:

```text
docs/paper/manuscript/figures/generated/
```

Recommended script name:

```text
scripts/analysis/make_paper_figures.py
```

The script should not rewrite manuscript claims. It should produce figures and
summary CSVs that make the evidence easier to review.

## Stop Conditions

Pause before changing manuscript claims if:

- global beta matches local beta on the locality/interference readouts;
- the locality smoke lacks partner-indexed logs needed for interpretation;
- lesion variants change belief updating instead of only beta/precision
  deployment;
- aggregate payoff improves while untouched-partner interference worsens.

In those cases, update the research plan first and decide whether the manuscript
should make a weaker interpretive claim.
