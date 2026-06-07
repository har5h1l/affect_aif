# Limitations And Follow-Ups

## Limitations

### Simulation-Only Evidence

The current evidence is computational. It supports a mechanism claim, not a
human behavioral or clinical claim. Human-data fitting would be needed before
claiming psychological validity.

### Scripted Partner Surface

The primary trust task uses environment-owned **parameterized partner policies**,
not reciprocal active-inference agents. Each partner samples from
type-by-stance cooperation tables and updates stance reactively from the focal
agent's actions; only the focal agent runs full `pymdp.Agent` inference plus
partner-local affective precision. That isolates the focal mechanism, but it
does not yet establish fully reciprocal multi-agent dynamics in which both sides
update beliefs, confidence, and policies simultaneously. See
`docs/theory/pomdp_spec.md` §12–§13.

### Global-Beta Evidence Is Discovery-Scale

Partner-specific beta is an architectural premise. Current global-beta probes
support a signal-quality decomposition but do not yet establish that
partner-local precision is behaviorally necessary. Exp D and a higher-seed H3
locality probe are the planned tests of cross-partner interference.

### H5 Is A Temporal Dependency, Not A Simple Win Or Loss

The manuscript treats abrupt betrayal as a structural readout. In the 30-seed
confirmation, partner-local precision lowers policy entropy (8.36 vs 8.74) and
raises joint accuracy (0.372 vs 0.266), while the payoff advantage is small and
uncertain (1185.9 vs 1172.1; paired bootstrap interval crosses zero). The story
is precision-weighted commitment under temporal change, not better reward
maximization and not a generic misdeployment failure.

### Phenotypes In Manuscript; Exp C Reviewed

Section 3.5–3.6 includes 20-seed phenotype, $\alpha$-sweep, quadrant, and
mixed-volatility results. Exp C forgiveness is interpreted as a dissociation:
reengagement after repair and restoration of model-fitness confidence need not
move together, and payoff recovery remains near baseline across profiles. Do
not upgrade computational profiles to clinical categories or human validation.

### Literature Scope

The project is not the first active-inference model of trust or multi-agent
interaction. Its novelty is partner-local affective precision as a
model-fitness and deployment signal.

## Recommended Follow-Ups

### Before Writing

No broad follow-up is required before a manuscript draft. The current evidence
is enough for a mechanistic simulation paper if the claims stay narrow.

### If One More Experiment Is Needed

Run the H1 controlled diagnostic ladder if confirmation remains confounded:

- corrected active-encounter confirmation;
- normal graded reliability spine;
- reward-matched graded reliability spine;
- strict reward-neutral diagnostic.

This directly tests whether any H1 failure is an analysis/task-design confound
or a model-level failure. H5 confirmation has already replaced the smoke-scale
betrayal read in the manuscript.

### Reviewer-Driven Checks

Potential reviewer asks and the appropriate response:

| Reviewer concern | Best response |
|---|---|
| "Is partner-local beta necessary?" | Add global-beta ablation. |
| "Does this generalize beyond scripted partners?" | Add AIF-vs-AIF descriptive runs or benchmark-facing follow-up. |
| "Are clinical labels justified?" | Soften language to computational perturbations; do not add diagnostic claims. |
| "Is this just reward averaging?" | Lead with the H1 corrected-readout plus controlled diagnostic ladder. |
| "Why does volatility help or hurt payoff?" | Present the manuscript temporal-dependency framing: precision sharpens action under change, but payoff effects depend on portfolio structure and need not be monotonic. |
| "Is this ToM?" | No—manuscript positions affect as social metacognition over behavioural model fitness; ToM combination is future work. |

## Stopping Rule

Do not add more sweeps just because the story has caveats. A mechanistic paper
is stronger when it states its boundary condition clearly than when it hides it
behind broad exploratory reruns.
