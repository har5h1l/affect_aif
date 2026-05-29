# Claims and Evidence

## Status Summary

| Claim | Status | Evidence | How to write it |
|---|---|---|---|
| Affective precision can move policy only when the policy space is open. | Supported with caveat | H0 graded-choice and graded/stress runs show entropy and behavior shifts; saturated binary regimes are weaker. | "Policy openness gates visible affect effects." |
| Partner-local precision tracks model fitness more than reward. | Post-fix unresolved | Older H1 confirmation supported this, but the post-fix smoke reverses the readout (`0.226` surprise vs `0.615` payoff). | Treat as a target claim requiring confirmation or design revision. |
| Affect changes deployment more than belief inference. | Supported | H2 open-regime lesion: belief accuracy remains similar while policy entropy and payoff move. | "The lesion resembles knowing-without-using rather than ignorance." |
| Stress amplifies the mechanism. | Supported as boundary condition | H3 betrayal runs show lower entropy, altered return/reallocation, and worse payoff under abrupt shocks. | "Stress reveals the precision channel and its failure mode." |
| Affect improves recovery after betrayal. | Not supported | The 30-seed H3 confirmation does not show a robust conditional-return payoff advantage. | Do not claim this. |
| Generic caution fixes H3 misdeployment. | Not supported | H3 precision sensitivity: cautious variants often raise entropy but do not rescue payoff. | "The failure is shock-regime dependent, not just excessive gain." |
| Partner-specific precision guides social choice. | Supported behaviorally | H4 partner-choice distribution and entropy move while payoff is flat. | "Partner choice is the readout; payoff is secondary here." |
| Clinical-like variants map to validated clinical phenotypes. | Not supported | Current variants are parameter perturbations only. | "Clinical-like" or "computational phenotype", not diagnosis. |
| Clinical-like variants separate in precision dynamics. | Supported | H5 beta ranges, entropy, and selection dynamics differ by perturbation. | "Perturbations separate first in dynamics; payoff remains underpowered." |

## Completeness Read

The core computational story is complete enough for a paper draft because it has
a theory-to-code-to-result chain:

1. Theory defines affect as partner-local model-fitness precision.
2. Implementation uses official `inferactively-pymdp==1.0.0`, partner-local
   `type x stance` POMDPs, and external beta-to-gamma modulation.
3. Experiments test openness, model fitness, deployment, stress, social choice,
   and perturbation dynamics.
4. Current post-fix smoke shows deployment effects and a repaired H5 behavioral
   anchor, while H1 remains unresolved.

The evidence is not complete enough for a broad empirical psychology claim, a
clinical claim, or a universal performance claim. Those would require human
data, stronger phenotype validation, and broader benchmark comparison.

## Supported Results

### H0: Openness Gate

Supported with caveat. Affect has little room in constrained/saturated policy
regimes but can move entropy, action, partner choice, and sometimes payoff in
graded or choice regimes. Openness is necessary but not sufficient: H3 shows
that open regimes can also expose maladaptive precision.

### H1: Model Fitness

Post-fix unresolved. The older 30-seed bounded-proxy confirmation showed
precision tracking surprise/predictability more strongly than payoff, but the
post-fix log-surprisal smoke does not preserve that result. Do not use H1 as a
current manuscript anchor until it is confirmed or redesigned.

### H2: Deployment

Supported. The beta-to-policy-precision lesion preserves much of the
partner-belief readout while changing policy entropy and payoff in the open
graded-choice regime. This is the strongest "knowing versus using" result.

### H3: Stress Response

Supported only as a boundary condition. Stress makes the precision mechanism
visible, but abrupt betrayal causes lower entropy with worse payoff and no
confirmed conditional-return benefit. The precision-sensitivity follow-up rules
out a simple generic-caution repair and points to shock-shape dependence.

### H4: Social Choice

Supported behaviorally. Partner selection changes before reward clearly moves.
This is useful evidence because H4 predicts approach/avoidance/probing shifts,
not necessarily immediate payoff gain.

### H5: Perturbation Phenotypes

Partly supported. The precision dynamics separate as intended, but payoff
comparisons are underpowered and task-dependent. Keep H5 as supporting
computational phenotype plausibility, not as a central empirical result.

## Unsupported Or Overstrong Claims

Do not claim:

- affective precision monotonically improves payoff;
- affect always helps recovery after betrayal;
- the model validates clinical diagnoses;
- partner-local beta has been directly compared against global beta;
- H1 is currently confirmed under the post-fix selector;
- the project is the first active-inference model of trust.
