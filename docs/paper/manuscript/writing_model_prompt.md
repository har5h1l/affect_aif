# Prompt For Full-Draft Writing Model

You are writing the first full manuscript draft from a technical outline and
evidence packet. Do not invent citations, results, methods, or claims.

Read these files first:

1. `docs/paper/manuscript/README.md`
2. `docs/paper/manuscript/outline.tex`
3. `docs/paper/manuscript/results_digest.md`
4. `docs/paper/manuscript/figures.md`
5. `docs/paper/manuscript/references_todo.md`

Use these project docs for context if needed:

- `docs/theory/goals.md`
- `docs/theory/hypotheses.md`
- `docs/theory/pomdp_spec.md`
- `docs/design/implementation.md`
- `docs/results/current.md`

Drafting rules:

- Preserve the central claim: partner-specific affective precision tracks model
  fitness and gates social policy deployment; it is not a generic reward
  booster.
- Make H1 and H3 the strongest empirical anchors because they use 30 seeds per
  variant.
- Present H0/H2/H4 as supporting five-seed evidence.
- Present H5 as supplemental precision-dynamics evidence only.
- Do not write "affect improves payoff" without the boundary conditions.
- Do not write "affect recovers after betrayal"; write that abrupt betrayal
  exposes precision-driven misdeployment risk.
- Keep citations as TODO placeholders unless exact bibliographic details are
  verified.
- Every results paragraph must include the relevant seed count and at least one
  concrete number from `results_digest.md`.

Recommended manuscript spine:

1. Active inference and affective precision motivate a model-fitness signal.
2. Social interaction requires partner-specific model-fitness estimates.
3. The implementation keeps state/policy inference in official `pymdp.Agent`
   instances and keeps beta as an external HESP-style tracker.
4. H1 shows the tracker follows prediction reliability more than reward.
5. H2/H4 show the tracker changes deployment and partner choice in open regimes.
6. H3 shows abrupt volatility can make the same precision channel harmful.
7. H5 suggests clinical-like perturbations separate precision dynamics, but this
   is not clinical validation.
