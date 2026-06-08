# Claims and Evidence

Synced to the current manuscript framing in `docs/manuscript/sections/`.
The paper organises evidence around five linked claims; H-card IDs remain the
experiment spine.

## Status Summary

| Claim (manuscript framing) | Status | Evidence | How to write it |
|---|---|---|---|
| Partner-local precision tracks predictability, not partner value. | In manuscript with 30-seed confirmation. | §3.1: active-encounter partials local surprise vs payoff (0.882 vs 0.130); shared beta weaker (0.380 vs 0.049). | "Designed for model fitness"; cite action surprisal; note global-beta dilution and no reward-gain claim. |
| Behavioural gains arise through action sharpening, not belief quality. | In manuscript (open graded + tracked-only). | §3.3: entropy `8.59` vs `8.79`; tracked-only matches no-affect on entropy and payoff. | "Metacognitive not epistemic deployment"; use tracked-only as lesion. |
| Partner engagement reorganises around reliability before payoff separates. | In manuscript at current seed scale. | §3.4: entropy 3.99 vs 4.83; cooperator up (36.6% vs 34.8%), exploiter down (13.8% vs 16.2%); flat payoff (393.6 vs 393.2). | Allocation reorganisation, not payoff headline. |
| Abrupt betrayal exposes temporal dependency. | In manuscript with 30-seed confirmation. | §3.5: round-31 switch; entropy 8.36 vs 8.74 (CI −0.62 to −0.14); joint accuracy 0.372 vs 0.266 (CI 0.034 to 0.185); payoff 1185.9 vs 1172.1 (CI crosses zero). | Lead with entropy; uncertain payoff is correct for a calibration mechanism; hand off to §3.6 revision-speed profiles. |
| Gain $\alpha$ and prior define computational trust-calibration profiles. | In manuscript at 20-seed phenotype scale; Exp A-D interpreted. | §3.6: orienting four-experiment frame, $\alpha$ sweep (non-monotonic payoff), four gain-prior profiles, forgiveness decoupling, mixed-volatility tension/synthesis. | "Computational analogues"; disclaimer in Discussion §4; not clinical categories. |
| Policy openness gates visible affect effects. | Underpins §3.3; not a separate subsection. | Graded open-regime readouts. | Openness necessary, not sufficient. |
| Partner-local beta is behaviorally necessary. | Not established. | Local cleaner signal; global beta can win on payoff in probes. | Signal-quality decomposition only. |
| Focal AIF vs scripted partners. | Stated in Discussion limitation. | Methods opening + Discussion §Limitations. | Parameterized partner policies; reciprocal AIF is future work. |

## Completeness Read

The manuscript has a complete theory-to-code-to-result chain for a mechanistic
simulation paper at the seed scales stated in Methods:

1. Theory: partner-local model-fitness precision as metacognitive deployment.
2. Implementation: focal `pymdp.Agent` + external beta; scripted partner
   environment (`docs/manuscript/notes/model_spec.md`).
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

### Social reorganisation (H4 / §3.4)

Partner-choice entropy drops under precision modulation (3.99 vs 4.83); engagement shifts toward cooperator and away from exploiter; payoff flat at stated scale (393.6 vs 393.2).

### Temporal dependency under betrayal (H5 / §3.5)

The 30-seed confirmation replaces the earlier smoke-scale payoff--accuracy
story. Open with accumulated confidence as a liability when a partner changes
(round-31 P0 switch). Lead with entropy (`8.36` vs `8.74`; CI does not cross
zero), then joint accuracy (`0.372` vs `0.266`), then uncertain payoff
(`1185.9` vs `1172.1`; CI crosses zero) as the correct readout for a
calibration mechanism rather than a power failure. Reallocation diagnostics
(higher post-switch P0 reencounters under affect) support active portfolio
management but do not establish a payoff headline. Hand off to §3.6 for revision
speed via precision gain and prior model fitness.

### Phenotype programme (H6 / Exp A–D / §3.6)

20-seed descriptive profiles in manuscript. §3.6 opens with a four-experiment
orienting frame, leads the $\alpha$ sweep with non-monotonic payoff, gives
equal weight to four gain-prior profiles, and closes with trade-off synthesis.
Exp C forgiveness is interpreted as a dissociation between reengagement and
restored confidence (no-affect 0.593 / cautious-low 0.630; payoff recovery
0.996--1.033). Mixed-volatility payoff--discrimination dissociation at high
gain; softened inertia claim (cautious-low muted $\beta_k$ only). Human-data
disclaimer in Discussion §4. Do not infer clinical validity.

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
