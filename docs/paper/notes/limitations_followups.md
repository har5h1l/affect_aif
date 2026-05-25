# Limitations And Follow-Ups

## Limitations

### Simulation-Only Evidence

The current evidence is computational. It supports a mechanism claim, not a
human behavioral or clinical claim. Human-data fitting would be needed before
claiming psychological validity.

### Scripted Partner Surface

The primary trust task uses environment-owned partner policies. That is
appropriate for isolating focal-agent mechanisms, but it does not yet establish
fully reciprocal multi-agent dynamics.

### No Global-Beta Ablation Yet

Partner-specific beta is an architectural premise. A future global-beta
ablation would directly test whether partner-local precision is better than a
shared affective precision state.

### H3 Is A Boundary Condition

The stress response is not a clean recovery win. Abrupt betrayal reveals
misdeployment risk. This should be a central discussion point, not hidden as a
negative result.

### H5 Payoff Is Underpowered

Clinical-like variants separate in precision dynamics and some behavioral
readouts. Payoff claims need higher replication and possibly better calibrated
tasks.

### Literature Scope

The project is not the first active-inference model of trust or multi-agent
interaction. Its novelty is partner-local affective precision as a
model-fitness and deployment signal.

## Recommended Follow-Ups

### Before Writing

No broad follow-up is required before a manuscript draft. The current evidence
is enough for a mechanistic simulation paper if the claims stay narrow.

### If One More Experiment Is Needed

Run a focused shock-shape experiment:

- vary betrayal abruptness;
- vary observation noise;
- vary number of pre-switch confirmations;
- keep default affect fixed;
- compare against no-affect and tracked-only lesion.

This directly tests whether H3 misdeployment is caused by sudden temporal
credit-assignment mismatch.

### Reviewer-Driven Checks

Potential reviewer asks and the appropriate response:

| Reviewer concern | Best response |
|---|---|
| "Is partner-local beta necessary?" | Add global-beta ablation. |
| "Does this generalize beyond scripted partners?" | Add AIF-vs-AIF descriptive runs or benchmark-facing follow-up. |
| "Are clinical labels justified?" | Soften language to computational perturbations; do not add diagnostic claims. |
| "Is this just reward averaging?" | Lead with H1 model-fitness dissociation. |
| "Why does H3 hurt payoff?" | Present the boundary condition as the point: precision can sharpen wrong deployment under abrupt shocks. |

## Stopping Rule

Do not add more sweeps just because the story has caveats. A mechanistic paper
is stronger when it states its boundary condition clearly than when it hides it
behind broad exploratory reruns.
