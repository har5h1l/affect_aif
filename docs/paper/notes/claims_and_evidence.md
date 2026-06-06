# Claims and Evidence

Synced to the current manuscript framing in `docs/paper/manuscript/sections/`.
The paper organises evidence around five linked claims; H-card IDs remain the
experiment spine.

## Status Summary

| Claim (manuscript framing) | Status | Evidence | How to write it |
|---|---|---|---|
| Partner-local precision tracks predictability, not partner value. | In manuscript at locality-probe scale; 30-seed confirm TODO. | §3.1: surprise vs payoff correlations (0.943 vs 0.110 local). | "Designed for model fitness"; cite action surprisal; note global-beta dilution. |
| Behavioural gains arise through action sharpening, not belief quality. | In manuscript (open graded + tracked-only). | §3.2: entropy 7.94 vs 8.80; tracked-only matches no-affect. | "Metacognitive not epistemic deployment"; use tracked-only as lesion. |
| Partner engagement reorganises around reliability before payoff separates. | In manuscript at current seed scale. | §3.3: entropy 4.66 vs 4.81; selection shifts; flat payoff. | Allocation reorganisation, not payoff headline. |
| Abrupt betrayal exposes temporal dependency (payoff gain, accuracy cost). | In manuscript; 30-seed confirm TODO. | §3.4: payoff 1322.3 vs 1225.0; accuracy 0.319 vs 0.425. | Portfolio reallocation story, not "better inference" or pure misdeployment failure. |
| Gain $\alpha$ and prior define computational trust-calibration profiles. | In manuscript at 20-seed phenotype scale; Exp C TODO. | §3.5–3.6: perturbations, $\alpha$ sweep, quadrants, mixed volatility. | "Computational analogues"; not clinical categories. |
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

Manuscript uses locality-probe correlations and global-beta dilution. Treat
30-seed confirmation as open if numbers change.

### Metacognitive deployment (H2 / §3.2)

Tracked-only matches no-affect on entropy and payoff while full precision
modulation differs—deployment-channel claim is the manuscript anchor here.

### Social reorganisation (H4 / §3.3)

Partner-choice entropy and engagement shifts; payoff flat at stated scale.

### Temporal dependency under betrayal (H5 / §3.4)

Manuscript's central stress readout: higher payoff with lower joint accuracy.
Write as adaptive reallocation when alternatives exist, not as recovery or as
pure failure.

### Phenotype programme (H6 / Exp A–D / §3.5–3.6)

20-seed descriptive profiles in manuscript. Exp C forgiveness subsection still
TODO in `.tex`. Do not infer clinical validity.

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
