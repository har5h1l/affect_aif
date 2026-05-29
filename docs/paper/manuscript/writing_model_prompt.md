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
  deployment; the current post-fix smoke only supports the deployment/H5 side.
- Make H5 the strongest current empirical anchor. Treat H1 as a
  confirmation/rework item because the post-fix smoke does not preserve the old
  surprise-over-reward diagnostic.
- Present H0/H2/H4 as supporting five-seed evidence.
- Present H6 as supplemental precision-dynamics evidence only.
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
4. H1 is currently unresolved under post-fix smoke and needs confirmation or
   redesign before carrying the model-fitness claim.
5. H2/H4 show the tracker changes deployment and partner choice in open regimes.
6. H5 shows the corrected selector can improve abrupt-betrayal behavior at
   smoke scale.
7. H6 suggests clinical-like perturbations separate precision dynamics, but this
   is not clinical validation.
