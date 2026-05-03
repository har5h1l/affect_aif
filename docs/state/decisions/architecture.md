# Architecture Decisions

## Reusable Core

`aif/` is the reusable active-inference core. It should remain free of trust,
experiment, analysis, benchmark, and runtime-orchestration imports.

## Dependency Direction

The target dependency direction is:

```text
scripts -> experiments -> tasks -> aif
```

Topology changes should preserve behavior first. Scientific changes belong in
explicit follow-up work.

## Task Packages

Trust-game semantics belong in a trust task package: partners, stances, payoffs,
trust environments, trust rollout, trust agents, and trust-task evaluation.

## Apashea Alignment

The apashea notebook remains a reference for factorized controls, policy priors,
and active-inference matrix conventions. This project keeps a JAX-based core and
does not embed pymdp as a runtime dependency.

## Legacy Surfaces

`conductor/`, `archive/`, and `docs/paper/` are not current operating surfaces.
Useful context is salvaged into `docs/state/` and `docs/results/`, then stale
sources are removed.
