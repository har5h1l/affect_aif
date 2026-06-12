# Claims and Evidence

Headline numbers and include/exclude rules: `docs/results/current.md`.

Synced to the current manuscript framing in `docs/manuscript/sections/`.
The paper organises evidence around linked reader-facing experiment families;
internal H-card IDs remain provenance only.

## Status Summary

| Claim (manuscript framing) | Status | Evidence | How to write it |
|---|---|---|---|
| Partner-local precision tracks predictability rather than realized value. | In manuscript as restored locality probe. | Section 3.1: raw correlations `-0.945` vs `0.367`; active-encounter partial correlations `-0.940` vs `0.023`; shared-$\beta$ partial readout `-0.496` vs `0.535`; analysis-run payoff local `1977.2`, shared `1973.4`, no-affect `1905.9`. | Mechanism calibration, not reward optimization; specify that similar local/shared payoff does not preserve the partner-local surprisal signal. |
| Behavioural gains arise through policy sharpening, not belief quality. | In manuscript (open graded + tracked-only). | Deployment subsection: beta range local `1.34` vs tracked-only `1.34`; entropy delta vs tracked-only `-0.238`; payoff delta vs tracked-only `+2.1`. | "Metacognitive not epistemic deployment"; use tracked-only as lesion and avoid reward-improvement language. |
| Partner engagement reorganises before payoff separates. | In manuscript at 30-seed graded-paper scale. | Partner-choice subsection: entropy `8.60` vs `8.83`; selected-type allocation affect vs no-affect: cooperator `25.3%` vs `29.2%`, exploiter `25.5%` vs `21.3%`, reciprocator `23.7%` vs `22.5%`, random `25.5%` vs `27.1%`; payoff nearly matched (`1868.3` vs `1866.2`). | Small allocation reorganisation consistent with sharper policy commitment, not a one-type preference or payoff headline. |
| Abrupt betrayal exposes temporal dependency. | In manuscript with 30-seed confirmation. | Betrayal subsection: round-31 switch; entropy 8.36 vs 8.74 (CI -0.63 to -0.16); joint accuracy 0.372 vs 0.266 (CI 0.024 to 0.188); payoff 1185.9 vs 1172.1 (CI crosses zero). | Lead with entropy; uncertain payoff is correct for a calibration mechanism; hand off to profile revision-speed analyses. |
| Gain $\alpha$ and prior define computational trust-calibration profiles. | In manuscript at 20-seed profile scale. | Profile subsection: orienting three-experiment frame, $\alpha$ sweep (non-monotonic payoff), four gain-prior profiles, and forgiveness decoupling. | "Computational analogues"; disclaimer in Discussion; not clinical categories. |
| Policy openness gates visible affect effects. | Underpins §3.2; not a separate subsection. | Graded open-regime readouts. | Openness necessary, not sufficient. |
| Partner-local beta is behaviorally necessary. | Not established. | Local cleaner signal; global beta can win on payoff in probes. | Signal-quality decomposition only. |
| Focal AIF vs scripted partners. | Stated in Discussion limitation. | Methods opening + Discussion §Limitations. | Parameterized partner policies; reciprocal AIF is future work. |

## Completeness Read

The manuscript has a complete theory-to-code-to-result chain for a mechanistic
simulation paper at the seed scales stated in Methods:

1. Theory: partner-local model-fitness precision as metacognitive deployment.
2. Implementation: focal `pymdp.Agent` + external beta; scripted partner
   environment (`docs/manuscript/notes/model_spec.md`).
3. Results: predictability-over-value, graded deployment, partner-choice,
   betrayal, and profile claims.
4. Discussion: metacognition vs ToM, deployment lesion, betrayal temporal
   dependency, three limitations, future directions.

Not ready for: human empirical claims, clinical diagnosis, reciprocal multi-AIF,
or universal payoff improvement.

## Supported Results (manuscript language)

### Predictability over value (§3.1)

Partner-local precision tracks partner-response likelihood surprisal more
strongly than realized payoff; shared-$\beta$ attenuates this relationship-local
signal. The payoff panel is the active-encounter locality-probe analysis window,
not full-episode cumulative payoff.

### Metacognitive deployment (§3.2)

Tracked-only updates beta without deploying it through gamma, while full
precision modulation lowers entropy relative to tracked-only. The
deployment-channel claim is the manuscript anchor here.

### Social reorganisation (§3.3)

Partner-choice entropy drops under precision modulation (8.60 vs 8.83);
selected-type allocation is reorganised without a simple cooperator-seeking
direction; payoff remains nearly matched at stated scale (1868.3 vs 1866.2).
These are the 30-seed graded paper readout numbers. Reviewer-control provenance
remains outside the manuscript source-table set.

### Temporal dependency under betrayal (§3.4)

The 30-seed confirmation replaces the earlier smoke-scale payoff--accuracy
story. Open with accumulated confidence as a liability when a partner changes
(round-31 P0 switch). Lead with entropy (`8.36` vs `8.74`; CI does not cross
zero, `-0.63` to `-0.16`), then joint accuracy (`0.372` vs `0.266`; CI
`0.024` to `0.188`), then uncertain payoff
(`1185.9` vs `1172.1`; CI crosses zero) as the correct readout for a
calibration mechanism rather than a power failure. The figure now shows the
time course of betrayed-partner engagement, P0 beta, and entropy around the
switch; it should be read as temporal persistence of deployment rather than a
simple reallocation-away result. Hand off to §3.5 for revision speed via
precision gain and prior model fitness.

### Profile programme (§3.5)

20-seed descriptive profiles in manuscript. §3.5 opens with a three-experiment
orienting frame, leads the $\alpha$ sweep with non-monotonic payoff, gives
equal weight to four gain-prior profiles, and closes with trade-off synthesis.
The forgiveness profile is interpreted as a separation between reengagement and
restored confidence (no-affect 0.593 / cautious-low 0.630; payoff recovery
0.996--1.033). Mixed-volatility analyses are future-facing and are not
reported as manuscript evidence. Human-data disclaimer in Discussion §4. Do not
infer clinical validity.

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
