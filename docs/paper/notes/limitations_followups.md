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

The manuscript treats abrupt betrayal as a structural readout: partner-local
precision can raise total payoff (1322.3 vs 1225.0 in current draft) while
**lowering** joint accuracy (0.319 vs 0.425). The story is portfolio
reallocation when accumulated confidence redirects toward reliable alternatives,
not better inference about the switched partner and not a generic misdeployment
failure. Keep this as a central Discussion point. Final 30-seed numbers may
replace draft values (TODO in `.tex`).

### Phenotypes In Manuscript; Exp C Still Open

Section 3.5–3.6 includes 20-seed phenotype, $\alpha$-sweep, quadrant, and
mixed-volatility results. Exp C forgiveness remains TODO in the `.tex` source.
Do not upgrade computational profiles to clinical categories or human validation.

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
or a model-level failure. H5 confirmation remains the top behavioral run after
Exp A-D complete.

### Reviewer-Driven Checks

Potential reviewer asks and the appropriate response:

| Reviewer concern | Best response |
|---|---|
| "Is partner-local beta necessary?" | Add global-beta ablation. |
| "Does this generalize beyond scripted partners?" | Add AIF-vs-AIF descriptive runs or benchmark-facing follow-up. |
| "Are clinical labels justified?" | Soften language to computational perturbations; do not add diagnostic claims. |
| "Is this just reward averaging?" | Lead with the H1 corrected-readout plus controlled diagnostic ladder. |
| "Why does volatility help or hurt payoff?" | Present the manuscript temporal-dependency framing: payoff can rise via reallocation while accuracy falls; stale confidence is the risk. |
| "Is this ToM?" | No—manuscript positions affect as social metacognition over behavioural model fitness; ToM combination is future work. |

## Stopping Rule

Do not add more sweeps just because the story has caveats. A mechanistic paper
is stronger when it states its boundary condition clearly than when it hides it
behind broad exploratory reruns.
