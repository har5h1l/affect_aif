# Claims and Evidence

## Status Summary

| Claim | Status | Evidence | How to write it |
|---|---|---|---|
| Affective precision can move policy only when the policy space is open. | Post-fix smoke-supported; needs confirmation if payoff language stays. | H0/H2 smoke shows entropy/deployment movement while payoff remains flat. | "Policy openness gates visible affect effects"; do not claim a general payoff advantage. |
| Partner-local precision tracks model fitness more than reward. | Post-fix smoke-supported; needs confirmation or controlled diagnostics. | Corrected post-fix H1 smoke restores the readout (`0.976` surprise vs `0.721` payoff; partial `0.951` vs `0.172` controlling payoff and encounter count). | Treat as a target claim requiring the H1 ladder before manuscript use. |
| Affect changes deployment more than belief inference. | Smoke-supported as a deployment-channel claim. | H2 open-regime lesion/no-affect readouts leave payoff flat but show policy-entropy movement. | "The lesion tests knowing-without-using"; keep payoff language conditional on confirmation. |
| Partner-local beta is behaviorally necessary. | Not established. | H3 smoke shows local beta has the cleaner model-fitness signal, while global beta has higher aggregate payoff. | Write H3 as a decomposition of signal quality versus allocation, not as necessity. |
| Partner-specific precision guides social choice. | Underpowered; keep as allocation-reorganisation claim. | H4 partner-choice smoke is noisy and payoff-flat. | "Partner choice is the planned readout; payoff is secondary here." |
| Stress amplifies the mechanism. | Best current positive behavioral anchor, but smoke only. | H5 betrayal smoke shows local affect beating no-affect after the selector fix (`1322.3` vs `1225.0`). | Use as the priority confirmation target, not final publication evidence. |
| Clinical-like variants map to validated clinical phenotypes. | Not supported. | Current variants are parameter perturbations only; Exp A-D are computational phenotype runs. | "Clinical-like" or "computational phenotype", not diagnosis. |
| Clinical-like variants separate in precision dynamics. | Pending final Exp A-D review. | Exp A-D are running; outputs are not final evidence until complete and approved for interpretation. | Keep Section 3.6 placeholders until final valid outputs are reviewed. |

## Completeness Read

The core computational story is complete enough for a paper draft because it has
a theory-to-code-to-result chain:

1. Theory defines affect as partner-local model-fitness precision.
2. Implementation uses official `inferactively-pymdp==1.0.0`, partner-local
   `type x stance` POMDPs, and external beta-to-gamma modulation.
3. Experiments test openness, model fitness, deployment, stress, social choice,
   and perturbation dynamics.
4. Current post-fix smoke shows deployment effects and a repaired H5 behavioral
   anchor, while H1 remains smoke-supported but not confirmation-scale.

The evidence is not complete enough for a broad empirical psychology claim, a
clinical claim, or a universal performance claim. Those would require human
data, stronger phenotype validation, and broader benchmark comparison.
It is also not yet complete enough to use H1 as a publication-grade
model-fitness anchor; the corrected H1 readout still needs confirmation or the
controlled diagnostic ladder described in `docs/active/progress.md`.

## Supported Results

### H0: Openness Gate

Supported with caveat. Affect has little room in constrained/saturated policy
regimes but can move entropy, action, partner choice, and sometimes payoff in
graded or choice regimes. Openness is necessary but not sufficient: H3 shows
that open regimes can also expose maladaptive precision.

### H1: Model Fitness

Corrected post-fix smoke-supported, but not yet confirmation-scale. The
active-encounter and partial-correlation readouts show precision tracking
surprise/predictability more strongly than payoff, but H1 should not be used as
a manuscript anchor until the corrected readout is confirmed at higher seed
count.

### H2: Deployment

Smoke-supported as a deployment-channel result. The beta-to-policy-precision
lesion/no-affect comparisons preserve the knowing-versus-using framing, but
payoff is flat at smoke scale and should stay conditional on confirmation.

### H3: Locality / Global Precision

Supported only as a decomposition. Partner-local beta preserves the cleaner
partner-level model-fitness signal, while global beta currently has higher
smoke payoff. Do not claim that partner-local beta is behaviorally necessary
until Exp D or a dedicated higher-seed H3 run shows cross-partner interference
or allocation benefit.

### H4: Social Choice

Underpowered. Partner selection is still the right readout because H4 predicts
approach/avoidance/probing shifts rather than immediate payoff gain, but the
post-fix smoke is too noisy for a strong manuscript claim.

### H5: Timescale / Volatility

Smoke-supported as the strongest current behavioral anchor. The corrected
selector repairs the betrayal result at three seeds; run confirmation before
using it as a publication-grade claim.

### H6: Perturbation Phenotypes

Pending Exp A-D. Keep phenotype claims as computational precision-dynamics
claims and do not fill Section 3.6 interpretation text until the running
outputs are complete and approved for interpretation.

## Unsupported Or Overstrong Claims

Do not claim:

- affective precision monotonically improves payoff;
- affect always helps recovery after betrayal;
- the model validates clinical diagnoses;
- partner-local beta is behaviorally necessary under the current task design;
- H1 is currently confirmed under the post-fix selector;
- the project is the first active-inference model of trust.
