# Claims and Evidence

Synced to the current manuscript framing in `docs/paper/manuscript/sections/`.
The paper organises evidence around five linked claims; H-card IDs remain the
experiment spine.

## Status Summary

| Claim (manuscript framing) | Status | Evidence | How to write it |
|---|---|---|---|
| Partner-local precision tracks predictability, not partner value. | In manuscript with 30-seed confirmation. | §3.1: active-encounter partials local surprise vs payoff (0.882 vs 0.130); shared beta weaker (0.380 vs 0.049). | "Designed for model fitness"; cite action surprisal; note global-beta dilution and no reward-gain claim. |
| Behavioural gains arise through action sharpening, not belief quality. | In manuscript (open graded + tracked-only). | §3.2: entropy 7.94 vs 8.80; tracked-only matches no-affect. | "Metacognitive not epistemic deployment"; use tracked-only as lesion. |
| Partner engagement reorganises around reliability before payoff separates. | In manuscript at current seed scale. | §3.3: entropy 4.66 vs 4.81; selection shifts; flat payoff. | Allocation reorganisation, not payoff headline. |
| Abrupt betrayal exposes temporal dependency. | In manuscript with 30-seed confirmation. | §3.4: payoff 1185.9 vs 1172.1, CI crosses zero; entropy 8.36 vs 8.74; joint accuracy 0.372 vs 0.266. | Action sharpening with modest behavioral benefit; not generic reward improvement. |
| Gain $\alpha$ and prior define computational trust-calibration profiles. | In manuscript at 20-seed phenotype scale; Exp A-D interpreted. | §3.5–3.6: perturbations, $\alpha$ sweep, quadrants, forgiveness, mixed volatility. | "Computational analogues"; not clinical categories. |
| Policy openness gates visible affect effects. | Underpins §3.2; not a separate subsection. | Graded open-regime readouts. | Openness necessary, not sufficient. |
| Partner-local beta is behaviorally necessary. | Not established. | Local cleaner signal; global beta can win on payoff in probes. | Signal-quality decomposition only. |
| Focal AIF vs scripted partners. | Stated in Discussion limitation. | Methods opening + Discussion §Limitations. | Parameterized partner policies; reciprocal AIF is future work. |

## Completeness Read

The manuscript has a complete theory-to-code-to-result chain for a mechanistic
simulation paper at the seed scales stated in Methods:

1. Theory: partner-local model-fitness precision as metacognitive deployment.
2. Implementation: focal `pymdp.Agent` + external beta; scripted partner
   environment (`docs/paper/notes/model_spec.md`).
3. Results: five linked claims from H1–H6 experiment spine.
4. Discussion: metacognition vs ToM, deployment lesion, betrayal temporal
   dependency, three limitations, future directions.

Not ready for: human empirical claims, clinical diagnosis, reciprocal multi-AIF,
or universal payoff improvement.

## Supported Results (manuscript language)

### Predictability not value (H1 / §3.1)

Manuscript uses the 30-seed H1 confirmation. Partner-local precision tracks
action surprisal more strongly than realized payoff after active-encounter
controls; shared beta preserves the ordering with weaker specificity. Payoff
favors no-affect in this probe, so write H1 as model-fitness tracking rather
than reward improvement.

### Metacognitive deployment (H2 / §3.2)

Tracked-only matches no-affect on entropy and payoff while full precision
modulation differs—deployment-channel claim is the manuscript anchor here.

### Social reorganisation (H4 / §3.3)

Partner-choice entropy and engagement shifts; payoff flat at stated scale.

### Temporal dependency under betrayal (H5 / §3.4)

The 30-seed confirmation replaces the earlier smoke-scale payoff--accuracy
story. Partner-local affect lowers policy entropy and raises joint accuracy,
while the payoff advantage is small and uncertain. Write this as
precision-weighted commitment under abrupt change, not as a broad reward gain or
as evidence that affect simply improves partner-type inference.

### Phenotype programme (H6 / Exp A–D / §3.5–3.6)

20-seed descriptive profiles in manuscript. Exp C forgiveness is now
interpreted as a dissociation between reengagement and restored confidence:
no-affect and cautious-low-$\alpha$ profiles reengage most, while payoff
recovery remains near baseline across profiles. Do not infer clinical validity.

## Unsupported Or Overstrong Claims

Do not claim:

- affective precision monotonically improves payoff;
- betrayal success means better partner-type inference;
- the model validates clinical diagnoses or attachment/anxiety phenotypes as
  categories;
- partner-local beta is behaviorally necessary under current task design;
- reciprocal multi-agent active inference (partners as full AIF agents);
- the project is the first active-inference model of trust;
- human empirical support.
