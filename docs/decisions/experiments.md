# Experiment Decisions

## Hypothesis Spine

The current experiment surface follows the Hesp-extension behavior cards in
`docs/theory/hypotheses.md`.

Canonical labels are:

- H0 Openness Gate
- H1 Model Fitness
- H2 Deployment
- H3 Stress Response
- H4 Social Choice
- H5 Perturbation Phenotypes

Partner-specific beta remains an architectural premise. A global-beta ablation
can be added later as optional model comparison, but it is not part of the
current core hypothesis spine.

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
