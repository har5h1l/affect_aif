# 2026-05-26 H6 Locality / Interference Probe

## Status

This note records two five-seed H6 locality/interference smoke results. They
are useful for deciding what to run next, but they should not be promoted into
the main manuscript evidence hierarchy or used to claim that partner-local beta
is necessary.

## Provenance

- Batch: `results/h6_global_beta_locality_probe_20260526/`
- Config:
  `configs/trust/hypotheses/h6_locality_interference/global_beta_locality_probe.toml`
- Runtime: official `inferactively-pymdp==1.0.0`
- Size: 4 variants x 5 seeds x 80 rounds = `1,600` rows
- Worker count: `--workers 1`
- Status: completed and analyzed
- Analysis:
  `results/h6_global_beta_locality_probe_20260526/h6/global_beta_locality_probe/analysis/`

Second focal-switch probe:

- Batch: `results/h6_global_beta_focal_switch_probe_20260526/`
- Config:
  `configs/trust/hypotheses/h6_locality_interference/global_beta_focal_switch_probe.toml`
- Size: 4 variants x 5 seeds x 100 rounds = `2,000` rows
- Worker count: `--workers 1`
- Status: completed and analyzed
- Analysis:
  `results/h6_global_beta_focal_switch_probe_20260526/h6/global_beta_focal_switch_probe/analysis/`

Run command:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_locality_probe.toml \
  --output-dir results \
  --batch-name h6_global_beta_locality_probe_20260526 \
  --workers 1
```

Analysis command:

```bash
.venv/bin/python scripts/analysis/analyze.py \
  --results results/h6_global_beta_locality_probe_20260526/h6/global_beta_locality_probe/results.csv \
  --output-dir results/h6_global_beta_locality_probe_20260526/h6/global_beta_locality_probe/analysis
```

Focal-switch run command:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_focal_switch_probe.toml \
  --output-dir results \
  --batch-name h6_global_beta_focal_switch_probe_20260526 \
  --workers 1
```

Focal-switch analysis command:

```bash
.venv/bin/python scripts/analysis/analyze.py \
  --results results/h6_global_beta_focal_switch_probe_20260526/h6/global_beta_focal_switch_probe/results.csv \
  --output-dir results/h6_global_beta_focal_switch_probe_20260526/h6/global_beta_focal_switch_probe/analysis
```

## Design

The probe uses four partners:

- partner `0`: stable cooperator;
- partner `1`: reliable exploiter;
- partner `2`: random partner;
- partner `3`: reciprocator with a scheduled stance switch to hostile.

The comparison includes `no_affect`, `tracked_only`, `local_beta`, and
`global_beta`, with partner-local POMDP beliefs preserved in every condition.
Only the precision source differs.

## Aggregate Read

Aggregate payoff does not support a simple locality-win story:

| Variant | Mean total payoff | Mean policy entropy | Mean joint accuracy |
|---|---:|---:|---:|
| `global_beta` | `822.9` | `7.62` | `0.443` |
| `no_affect` | `796.6` | `8.05` | `0.310` |
| `tracked_only` | `796.6` | `8.05` | `0.310` |
| `local_beta` | `768.2` | `7.78` | `0.170` |

The tracked-only and no-affect variants are identical, as expected when beta is
decoupled from policy precision. Global beta has the best aggregate payoff in
this small run, while local beta has the lowest aggregate payoff. This means the
paper should not claim that local beta is necessary based on current H6
evidence.

## Model-Fitness Read

The precision-surprise diagnostic still separates local and global beta:

| Variant | `|corr(precision, surprise)|` | `|corr(precision, reward)|` | Surprise dominates reward |
|---|---:|---:|---|
| `local_beta` | `0.872` | `0.601` | yes |
| `tracked_only` | `0.811` | `0.608` | yes |
| `global_beta` | `0.070` | `0.236` | no |

Local beta retains the model-fitness signature in this design; global beta does
not. However, that cleaner signal did not translate into better payoff in the
five-seed smoke.

## Locality / Interference Read

The central interference prediction was that global beta would spread the
effect of one partner's switch to untouched partners more than local beta. This
smoke does not cleanly support that prediction.

Post-minus-pre deltas averaged across the three untouched partners:

| Variant | Selection-rate delta | Payoff delta | Entropy delta |
|---|---:|---:|---:|
| `global_beta` | `+0.012` | `-0.248` | `-0.283` |
| `local_beta` | `+0.057` | `-0.146` | `-0.458` |
| `no_affect` | `+0.007` | `-0.301` | `-0.143` |
| `tracked_only` | `+0.007` | `-0.301` | `-0.143` |

Switch-partner post-minus-pre deltas:

| Variant | Selection-rate delta | Payoff delta | Entropy delta |
|---|---:|---:|---:|
| `global_beta` | `-0.035` | `+0.269` | `-0.401` |
| `local_beta` | `-0.170` | `+0.668` | `-0.337` |
| `no_affect` | `-0.020` | `-0.217` | `-0.137` |
| `tracked_only` | `-0.020` | `-0.217` | `-0.137` |

Partner-selection entropy fell most under local beta (`-0.620`) and less under
global beta (`-0.190`), with no-affect/tracked-only at `-0.122`. Local beta
therefore produced the strongest post-switch concentration in this probe,
especially by shifting selection toward the random partner (`+0.400`) and away
from the switched partner (`-0.170`). Global beta produced a smaller and more
diffuse selection change.

## Interpretation

This run is useful precisely because it complicates the simple story. The local
tracker keeps a cleaner model-fitness signal, but the global tracker performs
better by aggregate payoff in this small mixed-partner setting. The locality
claim should therefore be softened.

The next design should separate two questions that are confounded here:

1. Does beta locality preserve a cleaner reliability signal?
2. Does that cleaner signal improve social allocation after a shock?

The current answer is: probably yes to the first, not yet to the second.

## Focal-Switch Follow-Up

The first probe switched partner `3`, which was not reliably selected after the
switch. A second five-seed smoke switched partner `0`, the stable cooperator
that tends to draw engagement. This made the post-switch comparison cleaner.

Aggregate payoff still does not support a local-beta advantage:

| Variant | Mean total payoff | Mean policy entropy | Mean joint accuracy |
|---|---:|---:|---:|
| `global_beta` | `991.7` | `7.92` | `0.292` |
| `no_affect` | `964.3` | `8.11` | `0.300` |
| `tracked_only` | `964.3` | `8.11` | `0.300` |
| `local_beta` | `953.7` | `7.80` | `0.214` |

The model-fitness diagnostic again separates local and global beta:

| Variant | `|corr(precision, surprise)|` | `|corr(precision, reward)|` | Surprise dominates reward |
|---|---:|---:|---|
| `local_beta` | `0.832` | `0.287` | yes |
| `tracked_only` | `0.874` | `0.030` | yes |
| `global_beta` | `0.133` | `0.164` | no |

The focal-switch partner-delta readout is also mixed. In the 10-round pre/post
window, local beta slightly increased selection of the switched partner
(`+0.060`) and reduced untouched-partner selection (`-0.020` on average).
Global beta increased selection of the switched partner more strongly
(`+0.220`) and reduced untouched-partner selection more broadly (`-0.073` on
average), but this did not hurt aggregate payoff. Global beta also moved more
widely as a shared state (`mean beta range = 0.777`) than the mean local beta
range (`0.361`).

## Next Step

Do not scale H6 directly to a 30-seed necessity test. The current H6 conclusion
is already useful: partner-local beta is a cleaner model-fitness readout, but a
global tracker can still perform as well or better behaviorally in these small
mixed-partner probes. The next manuscript-useful work is to treat H6 as an open
decomposition and shift effort back to confirmation of the main H0-H5 result
spine unless a reviewer specifically asks for locality necessity.
