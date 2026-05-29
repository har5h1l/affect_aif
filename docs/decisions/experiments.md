# Experiment Decisions

## Hypothesis Spine

The current experiment surface follows the Hesp-extension behavior cards in
`docs/theory/hypotheses.md`.

Canonical labels are:

- H0 Openness Gate
- H1 Model Fitness
- H2 Deployment
- H3 Locality / Global Precision
- H4 Social Allocation
- H5 Timescale / Volatility
- H6 Perturbation Phenotypes
- H7 Signal Source
- H8 Observation Noise / Robustness

Partner-specific beta remains an architectural premise. The global-beta
ablation is now the maintained H3 locality/global-precision comparison.

## Evidence Status

Current evidence requires a completed run on the current factorized-control
architecture, with provenance recorded under `docs/results/`.
Partial outputs are not comparable to completed current-evidence runs.

## Full Runs

Full experiments should wait until the restructure and verification gate pass.
The immediate post-verification queue is recorded in
`docs/active/progress.md`.

## Benchmark Surface

The supported benchmark surface is the trust-task evaluation arena under
`configs/benchmark/`. External benchmark integrations are not part of the
current repository surface.
