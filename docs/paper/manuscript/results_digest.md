# Results Digest For First Draft

## Inclusion Decision

Use the current promoted evidence, not superseded partial outputs.

| Evidence | Include? | Role |
|---|---|---|
| H0 graded choice, H2 lesion open regime, H4 partner choice | Yes | Open-policy and deployment/social-choice evidence; five seeds, so present as supporting evidence. |
| H1 reliability-vs-reward confirmation | Yes | Primary mechanism result; 30 seeds per variant. |
| H3 betrayal reallocation confirmation | Yes | Primary stress boundary result; 30 seeds per variant. |
| H3 precision sensitivity, abrupt and gradual | Yes | Primary follow-up for shock-regime dependence; 30 seeds per variant. |
| H5 clinical dynamics and clinical betrayal | Supplemental | Precision-dynamics phenotype evidence; five seeds and not clinical validation. |
| May 19 H3 reallocation pilot | Mention only if needed | Exploratory context; do not use as main evidence. |
| Partial detached reruns or duplicate outputs | No | Not part of current evidence contract. |

## Audited Run Sizes

| Experiment | Result path | Variants | Seeds | Rounds |
|---|---|---:|---:|---:|
| H0 graded choice | `results/confirm_h0_h1_h2_h4_20260518/h0/graded_choice/results.csv` | 2 | 5 each | 200 |
| H2 lesion open | `results/confirm_h0_h1_h2_h4_20260518/h2/lesion_open_regime/results.csv` | 3 | 5 each | 200 |
| H4 partner choice | `results/confirm_h0_h1_h2_h4_20260518/h4/partner_choice/results.csv` | 2 | 5 each | 200 |
| H1 confirmation | `results/confirm_h1_h3_split_20260519/h1/reliability_vs_reward_confirm/results.csv` | 2 | 30 each | 200 |
| H3 confirmation | `results/confirm_h1_h3_split_20260519/h3/betrayal_reallocation_confirm/results.csv` | 3 | 30 each | 120 |
| H3 abrupt sensitivity | `results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/results.csv` | 12 | 30 each | 120 |
| H3 gradual sensitivity | `results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/results.csv` | 8 | 30 each | 120 |
| H5 clinical dynamics | `results/updated_h0_h5_20260517_w2/h5/clinical_dynamics/results.csv` | 4 | 5 each | 200 |
| H5 clinical betrayal | `results/updated_h0_h5_20260517_w2/h5/clinical_betrayal/results.csv` | 4 | 5 each | 120 |
| H5 affect sensitivity | `results/updated_h0_h5_20260518_remainder/h5/affect_sensitivity/results.csv` | 6 | 5 each | 120 |

## Headline Results

### R1: Policy openness gates affective deployment

H0/H2 open graded regime, five seeds per variant:

- Affect: total payoff `1884.6`, mean policy entropy `7.94`.
- No-affect / lesion: total payoff `1859.4`, mean policy entropy `8.80`.
- Difference: `+25.2` payoff and `-0.86` entropy for affect.
- Interpretation: open graded policy spaces let precision move deployment.
  Because this is five seeds, present as a supporting result, not the strongest
  statistical anchor.

### R2: Precision tracks model fitness more than reward

H1 confirmation, 30 seeds per variant:

- Total payoff: affect `534.6` versus no-affect `542.1`; difference `-7.53`,
  bootstrap CI `[-27.88, 13.82]`.
- Mean entropy: affect `4.48` versus no-affect `4.32`; difference `+0.16`,
  bootstrap CI `[0.06, 0.27]`.
- Partner-level association: `|corr(precision, surprise)| = 0.701` versus
  `|corr(precision, payoff)| = 0.419`.
- Reliability-over-reward effect: `+0.096`, bootstrap CI `[0.027, 0.164]`.
- Interpretation: affective precision is a model-fitness signal, not a cached
  reward signal.

### R3: Affect changes deployment with similar beliefs

H2 open-regime lesion, five seeds per variant:

- Affect: payoff `1884.6`, joint accuracy `0.336`, stance accuracy `0.816`,
  entropy `7.94`.
- Lesion: payoff `1859.4`, joint accuracy `0.339`, stance accuracy `0.855`,
  entropy `8.80`.
- Interpretation: the lesion preserves similar or slightly higher belief
  readouts but loses the affective policy-precision pathway. This supports a
  knowing-versus-using dissociation, bounded by the five-seed sample.

### R4: Partner choice moves before payoff

H4 partner choice, five seeds per variant:

- Payoff is flat: affect `393.6` versus no-affect `393.2`.
- Entropy changes: affect `3.99` versus no-affect `4.83`.
- Mean selection rates by partner: affect `[0.366, 0.316, 0.138, 0.180]`;
  no-affect `[0.348, 0.318, 0.162, 0.172]`.
- Interpretation: partner-local precision changes choice distribution and
  policy entropy before total payoff becomes informative.

### R5: Abrupt betrayal exposes precision-driven misdeployment

H3 confirmation, 30 seeds per variant:

- Total payoff: affect `1136.1` versus no-affect/lesion `1172.1`; difference
  `-36.08`, bootstrap CI `[-63.65, -10.93]`, pairwise `p = 0.0169`.
- Mean entropy: affect `8.38` versus no-affect `8.74`; difference `-0.36`,
  bootstrap CI `[-0.45, -0.26]`.
- Reencounters with switched partner: affect `4.4` versus no-affect `6.1`.
- Reencounter selection rate: affect `0.049` versus no-affect `0.067`.
- Payoff on reencounter: affect `8.76` versus no-affect `8.91`.
- Wrong-type rate on reencounter: affect `0.237` versus no-affect `0.165`.
- Interpretation: affect reallocates somewhat and lowers entropy, but does not
  improve return safety or whole-run payoff. Write H3 as a stress boundary
  condition, not an affective recovery win.

### R6: Shock shape matters more than generic caution

H3 precision sensitivity, 30 seeds per variant:

- Abrupt baseline: no-affect/lesion payoff `1153.6`, entropy `8.80`.
- Abrupt default affect: payoff `1140.4`, entropy `8.35`, pairwise `p = 0.370`
  against no-affect.
- Abrupt combined caution: payoff `1115.0`, entropy `9.27`, `p = 0.003`
  against no-affect.
- Gradual baseline: no-affect/lesion payoff `1148.9`, entropy `8.76`.
- Gradual default affect: payoff `1147.6`, entropy `8.38`, `p = 0.906`
  against no-affect.
- Gradual combined caution: payoff `1118.3`, entropy `9.25`, `p = 0.005`
  against no-affect.
- Interpretation: default affect is harmful mainly under abrupt shock; generic
  caution raises entropy but does not rescue behavior.

### R7: H5 separates precision dynamics, not clinical validity

H5, five seeds per variant:

- Dynamics run payoff: affect `1884.6`, borderline `1871.1`, alexithymia
  `1840.7`, depression `1834.1`.
- Dynamics beta range: borderline `1.318`, depression `1.435`, affect `0.950`,
  alexithymia `0.149`.
- Betrayal payoff: alexithymia `1216.3`, borderline `1196.9`, affect `1168.3`,
  depression `1150.1`.
- Interpretation: perturbations separate beta range, entropy, and selection
  dynamics. Keep these as supplemental simulations and explicitly avoid
  clinical validation claims.

## Claims To Avoid

- Do not claim affect globally improves payoff.
- Do not claim affect wins after betrayal.
- Do not claim H5 variants validate clinical phenotypes.
- Do not claim partner-specific beta is proven better than a global beta; that
  ablation is future work.
- Do not treat no-affect and lesion as conceptually identical outside configs
  where they are numerically identical.
