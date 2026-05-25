# 2026-05-24 H3 Precision Sensitivity

## Provenance

- Batch: `results/h3_precision_sensitivity_20260522/`
- Branch/commit: current server checkout on `master`; exact commit not
  recorded in this note.
- Abrupt betrayal config:
  `configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity.toml`
- Gradual betrayal config:
  `configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity_gradual.toml`
- Runtime: official `inferactively-pymdp==1.0.0`
- Size: 30 seeds per variant; 12 variants in the abrupt run and 8 variants in
  the gradual run.
- Outputs:
  - Abrupt: `h3/betrayal_precision_sensitivity/results.csv` (`43,200` rows)
  - Gradual: `h3/betrayal_precision_sensitivity_gradual/results.csv`
    (`28,800` rows)
- Analysis: `scripts/analysis/analyze.py`

Run command:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity.toml --config configs/trust/hypotheses/h3_stress_response/betrayal_precision_sensitivity_gradual.toml --output-dir results --batch-name h3_precision_sensitivity_20260522 --workers 12
```

Analysis commands:

```bash
python scripts/analysis/analyze.py --results results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/results.csv --output-dir results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity/analysis
python scripts/analysis/analyze.py --results results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/results.csv --output-dir results/h3_precision_sensitivity_20260522/h3/betrayal_precision_sensitivity_gradual/analysis
```

## Question

The H3 confirmation showed that affective precision lowers policy entropy after
betrayal but can reduce whole-run payoff. This follow-up asked whether that
misdeployment is a tunable hyperparameter failure or a stronger stress-regime
boundary condition.

The sweep tested lower affect gain, slower or faster beta persistence, cautious
initial beta, softer precision support, lower base gamma, no epistemic value,
and combined caution. A second config made betrayal gradual with two scheduled
stance switches instead of one abrupt shock.

## Abrupt Betrayal

No-affect and lesioned baselines remain best by total payoff:

| Variant | Mean total payoff | Mean accuracy | Mean entropy |
|---|---:|---:|---:|
| no-affect / lesioned | `1153.6` | `0.346` | `8.80` |
| affect default | `1140.4` | `0.253` | `8.35` |
| affect low alpha | `1138.7` | `0.236` | `8.64` |
| affect slow beta | `1132.7` | `0.281` | `8.46` |
| affect cautious prior | `1124.7` | `0.297` | `9.03` |
| affect low gamma | `1120.8` | `0.298` | `9.02` |
| affect combined caution | `1115.0` | `0.309` | `9.27` |

Pairwise payoff tests against no-affect:

- Default affect: `p = 0.370`
- Low alpha: `p = 0.235`
- Cautious prior: `p = 0.024`
- Low gamma: `p = 0.016`
- Combined caution: `p = 0.003`

The caution variants did what they were designed to do in policy-space terms:
they raised entropy and often reduced overconfident wrong-type rates. But this
did not translate into better stress behavior. Combined caution and cautious
prior increased returns to the switched partner, while low gamma and combined
caution produced lower payoff on re-encounter than the baselines.

## Gradual Betrayal

The gradual switch changes the result. Default affect nearly matches baseline:

| Variant | Mean total payoff | Mean accuracy | Mean entropy |
|---|---:|---:|---:|
| no-affect / lesioned | `1148.9` | `0.426` | `8.76` |
| affect default | `1147.6` | `0.273` | `8.38` |
| affect low alpha | `1138.4` | `0.312` | `8.65` |
| affect slow beta | `1135.8` | `0.294` | `8.49` |
| affect soft precision | `1132.1` | `0.298` | `8.44` |
| affect combined caution | `1118.3` | `0.334` | `9.25` |
| affect low gamma | `1115.6` | `0.331` | `9.01` |

Pairwise payoff tests against no-affect:

- Default affect: `p = 0.906`
- Low alpha: `p = 0.335`
- Slow beta: `p = 0.216`
- Soft precision: `p = 0.119`
- Combined caution: `p = 0.005`
- Low gamma: `p = 0.002`

The default affective channel therefore looks much less harmful when betrayal
unfolds gradually. The cautious variants still do not rescue payoff, which
argues against the narrow story that current H3 failure is just excessive
precision gain or an overly sharp beta support.

## Interpretation

This run sharpens H3 rather than overturning it.

The precision channel is behaviorally active: it changes entropy, return rates,
and post-switch deployment. But the failure mode is not fixed by generic
caution. Raising entropy can prevent some overconfident wrong beliefs while
also making the agent re-engage the wrong partner more often or with less
profitable actions.

The stronger read is shock-regime dependence. Abrupt betrayal makes the
precision signal dangerous because policy sharpening and partner-belief
recalibration are temporarily misaligned. Gradual betrayal gives the default
agent more opportunity to absorb evidence, and default affect becomes nearly
payoff-neutral against the no-affect/lesioned baselines.

H3 should be written as a volatility boundary condition, not as an affective
recovery win and not as a globally bad precision channel.

## Next Research Implication

Do not run another broad hyperparameter sweep. The next useful experiment, if
needed, is a focused shock-shape test: vary betrayal abruptness, observation
noise, or the number of pre-switch confirmations while holding the default
affect channel fixed. That would directly test whether the problem is temporal
credit assignment during sudden model mismatch.
