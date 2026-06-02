# Prompt For Full-Draft Writing Model

You are writing the first full manuscript draft from a technical outline and
evidence packet. Do not invent citations, results, methods, or claims.

Read these files first:

1. `docs/paper/manuscript/README.md`
2. `docs/paper/manuscript/main.tex`
3. `docs/paper/manuscript/results_digest.md`
4. `docs/paper/manuscript/figures.md`
5. `docs/paper/manuscript/references.bib`

Use these project docs for context if needed:

- `docs/theory/goals.md`
- `docs/theory/hypotheses.md`
- `docs/theory/pomdp_spec.md`
- `docs/design/implementation.md`
- `docs/results/current.md`

Drafting rules:

- Preserve the central claim as a target claim: partner-specific affective
  precision is designed to track model fitness and gate social policy
  deployment; the current post-fix smoke supports this at diagnostic scale but
  still needs confirmation-scale reruns.
- Make H5 the strongest current behavioral anchor. Treat H1 as a
  corrected-readout confirmation item: active-aligned and partial-correlation
  smoke analyses support surprise-over-reward, but reward/exposure correlations
  remain a design confound to monitor through the active ladder:
  corrected confirmation, normal graded spine, reward-matched graded spine,
  then strict reward-neutral diagnostic if needed.
- Present H0/H2/H4 as smoke-supported deployment/allocation readouts, not as
  confirmed payoff advantages.
- Present H6 and Exp A-D as computational phenotype evidence only after final
  run outputs have been reviewed; do not infer clinical validity.
- Do not write "affect improves payoff" without the boundary conditions.
- Do not write "affect recovers after betrayal"; write that abrupt betrayal
  exposes precision-driven misdeployment risk.
- Use `references.bib` for existing citation keys. Add new citations only after
  checking bibliographic details.
- Every results paragraph must include the relevant seed count and at least one
  concrete number from `results_digest.md`.

Recommended manuscript spine:

1. Active inference and affective precision motivate a model-fitness signal.
2. Social interaction requires partner-specific model-fitness estimates.
3. The implementation keeps state/policy inference in official `pymdp.Agent`
   instances and keeps beta as an external HESP-style tracker.
4. H1 is supported by corrected post-fix smoke readouts but needs
   confirmation-scale replication before carrying the model-fitness claim.
5. H2/H4 show the tracker changes deployment and partner choice in open regimes
   at smoke scale.
6. H3 decomposes partner-local signal quality from global-beta allocation;
   locality is not yet proven behaviorally necessary.
7. H5 shows the corrected selector can improve abrupt-betrayal behavior at
   smoke scale.
8. H6/Exp A-D should be framed as computational phenotype work only after final
   outputs are reviewed; this is not clinical validation.
