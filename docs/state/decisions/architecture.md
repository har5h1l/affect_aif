# Architecture Decisions

## Runtime Ownership

The project no longer owns the active-inference engine. Official `pymdp` is the
runtime dependency; Apashea's notebook/fork is reference material for model
construction and helper ideas.

## Dependency Direction

The target dependency direction is:

```text
scripts -> experiments -> tasks -> inferactively-pymdp
```

Topology changes should preserve behavior first. Scientific changes belong in
explicit follow-up work.

## Task Packages

Trust-game semantics belong in a trust task package: partners, stances, payoffs,
trust environments, trust model construction, pymdp agent wrappers, external
affective precision tracking, and trust-task evaluation.

## Apashea Alignment

The apashea notebook remains a reference for factorized controls, policy priors,
and active-inference matrix conventions. The supported runtime is official
`inferactively-pymdp==1.0.0`; Apashea's fork is reference material, not the
runtime dependency.

## Supported Surface

Do not reintroduce a custom active-inference engine; keep affect and trust logic
in task-local modules around official `pymdp` agents.
