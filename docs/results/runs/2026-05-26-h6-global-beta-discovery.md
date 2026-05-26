# 2026-05-26 H6 Global-Beta Discovery

## Status

This is a discovery-scale result note for the H6 locality/interference follow-up.
It should guide the next experiment design and manuscript limitations. It should
not be used as confirmation evidence that partner-local beta is necessary.

## Provenance

- Batch: `results/h6_global_beta_discovery_20260525/`
- Runtime: official `inferactively-pymdp==1.0.0`
- Experiment family: H6 locality/interference
- Size: five seeds for the global-beta regime probes; three seeds for the larger
  lesion-family probe
- Worker count: `--workers 1`
- Status: completed, analyzed, discovery-scale only

Run command:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_model_fitness_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_deployment_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_partner_choice_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_betrayal_probe.toml \
  --config configs/trust/hypotheses/h6_locality_interference/lesion_family_probe.toml \
  --output-dir results \
  --batch-name h6_global_beta_discovery_20260525 \
  --workers 1
```

Analysis command template:

```bash
.venv/bin/python scripts/analysis/analyze.py \
  --results results/h6_global_beta_discovery_20260525/h6/<experiment_id>/results.csv \
  --output-dir results/h6_global_beta_discovery_20260525/h6/<experiment_id>/analysis
```

Completed experiment outputs:

| Experiment | Rows | Main comparison |
|---|---:|---|
| `global_beta_model_fitness_probe` | `3,000` | local beta, global beta, no affect |
| `global_beta_deployment_probe` | `4,000` | local beta, global beta, tracked-only, no epistemic value |
| `global_beta_partner_choice_probe` | `3,000` | local beta, global beta, no affect |
| `global_beta_betrayal_probe` | `2,400` | local beta, global beta, tracked-only, no affect |
| `lesion_family_probe` | `3,600` | beta parameter variants plus global beta |

## Question

The H0-H5 experiments show that partner-local precision is behaviorally active.
They do not yet show whether the precision signal must be partner-local. H6 asks
whether a single shared beta posterior can reproduce the same effects, or
whether a global tracker mixes evidence from different partners.

## Main Discovery Read

Global beta did not simply duplicate local beta in these smoke-scale probes.
Local beta preserved a stronger precision-surprise signature, while global beta
was weaker or more payoff-like in the settings where partner context mattered.

In the model-fitness probe, both local and global beta tracked predictive
surprise more than reward, but the association was much weaker for global beta:

| Variant | `|corr(precision, surprise)|` | `|corr(precision, reward)|` |
|---|---:|---:|
| local beta | `0.904` | `0.761` |
| global beta | `0.452` | `0.153` |

In the deployment probe, local beta remained strongly surprise-linked
(`0.937` versus `0.425` for reward), whereas global beta was weakly associated
with both surprise and reward (`0.196` versus `0.172`). In the lesion-family
betrayal probe, the global-beta signal shifted toward reward:
`|corr(precision, surprise)| = 0.213` and
`|corr(precision, reward)| = 0.704`.

The beta trajectories also differed. In betrayal-style probes, global beta moved
more broadly as a shared state than the average partner-local beta:

| Probe | Global beta range | Local mean beta range |
|---|---:|---:|
| global-beta betrayal | `0.855` | `0.520` |
| lesion family | `0.846` | `0.466` |

The cautious interpretation is that a shared beta tracker may blend
partner-specific model fitness with aggregate episode quality. This is a reason
to run a dedicated locality/interference experiment, not a basis for claiming
necessity.

## Locality / Interference Read

The current cross-partner summaries are suggestive but not decisive. In the
betrayal probe, local beta had slightly more untouched-partner selection in the
10-round post-switch window (`0.80`) than global beta (`0.74`). In the
lesion-family probe, local and global beta had the same average
untouched-partner selection rate (`0.767`), while global beta showed lower
untouched-partner entropy and larger payoff spread.

These results point to possible shared-state interference, but the task was not
designed tightly enough to isolate it. The next experiment should hold three
partners stable, shock one partner, and measure whether global beta changes
entropy, selection, and payoff for untouched partners.

## Manuscript Boundary

Use this result cautiously:

- It can motivate a limitation or follow-up paragraph about global versus
  partner-local precision.
- It can justify the new locality/interference diagnostic as the next
  manuscript-relevant experiment.
- It should not be promoted into the main evidence hierarchy yet.
- It should not support the claim that partner-local beta is necessary.

A manuscript-level necessity claim requires a higher-replication locality design
showing that global beta spreads uncertainty or maladaptive precision to
untouched partners while local beta contains the effect.

## Follow-Up Design Implication

The next run should prioritize the locality/interference diagnostic:

1. Use four partners: stable cooperator, reliable exploiter, random/volatile
   partner, and one scheduled stance-switch partner.
2. Compare `no_affect`, `tracked_only`, `local_beta`, and `global_beta`.
3. Report partner-indexed dynamics before aggregate payoff: beta/gamma,
   selection rate, policy entropy, payoff, return latency, wrong-type-on-return,
   and untouched-partner shifts after the switch.
4. Add focused lesion variants only after the locality logs are verified.
5. Build figure-quality outputs from canonical analysis CSVs so the result can
   be reviewed without reading raw logs.
