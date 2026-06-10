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
`docs/overview/pomdp.md`.

### Shared-Beta Evidence Is Signal-Level

Partner-specific beta is an architectural premise. Current global-beta probes
support a signal-quality decomposition: pooling precision evidence weakens the
partner-local predictability signal. They do not establish that partner-local
precision is behaviorally necessary in every task context; that would require a
dedicated behavioral cross-partner-interference comparison.

### Abrupt Betrayal Is A Temporal Dependency, Not A Simple Win Or Loss

The manuscript treats abrupt betrayal as a structural readout. In the 30-seed
confirmation, partner-local precision lowers policy entropy (8.36 vs 8.74) and
raises joint accuracy (0.372 vs 0.266), while the payoff advantage is small and
uncertain (1185.9 vs 1172.1; paired bootstrap interval crosses zero). The story
is precision-weighted commitment under temporal change, not better reward
maximization and not a generic misdeployment failure.

### Profiles In Manuscript; Forgiveness Reviewed

Section 3.5 includes 20-seed phenotype, $\alpha$-sweep, quadrant, and
forgiveness results. The forgiveness profile is interpreted as a separation:
reengagement after repair and restoration of model-fitness confidence need not
move together, and payoff recovery remains near baseline across profiles. Do
not upgrade computational profiles to clinical categories or human validation.

### Literature Scope

The project is not the first active-inference model of trust or multi-agent
interaction. Its novelty is partner-local affective precision as a
model-fitness and deployment signal.

## Current Evidence Status

The manuscript has two interpreted evidence layers:

1. **Core mechanism:** partner-local affective precision as social metacognitive
   calibration and deployment (predictability-over-value, open deployment,
   partner-choice, and abrupt-betrayal readouts at confirmation scale where
   stated).
2. **Individual-differences extension:** gain and prior define computational
   trust-calibration profiles (profile analyses at 20 seeds).

The abrupt-betrayal and profile analyses have reached structural finality for
the current draft.
There is no remaining experiment gate before submission. Headline numbers and
include/exclude rules live in `docs/results/current.md`.

## Reviewer-Driven Follow-Ups

Run only if needed for reviewer response:

| Reviewer concern | Best response |
|---|---|
| "Is partner-local beta necessary?" | Shared-beta/locality confirmation as signal-level evidence; behavioral necessity remains a future cross-partner-interference test. |
| "Does this generalize beyond scripted partners?" | Reciprocal AIF descriptive runs or future external evaluation. |
| "Are clinical labels justified?" | Soften language to computational perturbations; do not add diagnostic claims. |
| "Is this just reward averaging?" | Corrected model-fitness readout plus controlled diagnostic ladder. |
| "How should volatility be handled?" | Treat heterogeneous-volatility environments as future tests of change detection, not current manuscript evidence. |
| "Is this ToM?" | No—social metacognition over behavioural model fitness; ToM combination is future work. |

### Model-Fitness Diagnostic Escalation

If reviewers ask for a stronger reward-control decomposition, use the bounded
diagnostic ladder:

1. corrected active-encounter confirmation;
2. balanced-exposure graded reliability spine;
3. reward-matched graded reliability spine;
4. strict reward-neutral diagnostic.

Pause before changing manuscript claims if the reward-neutral diagnostic also
fails or if a follow-up would revive broad payoff-improvement framing.

### Shared-Beta / Locality Ablation

Question: is partner-specific affective precision behaviorally necessary, or
does a shared beta tracker explain the same behavior?

Current stance: local beta gives the cleaner partner-specific reliability
signal in the model-fitness confirmation, but universal behavioral necessity is not
established. A dedicated behavioral shared-beta confirmation is optional and
should be motivated by reviewer pressure.

## Longer-Term Extensions

- **Reciprocal social active inference:** replace scripted partners with full
  active-inference agents that update their own beliefs, confidence, and policies.
- **Human behavioral validation:** fit $\alpha$, prior, and coupling parameters
  to iterated trust-game behavior with individual-difference measures.
- **Model extensions:** variational beta as a proper auxiliary hidden state;
  explicit theory-of-mind factors combined with metacognitive precision; noisy
  observations and richer social ecologies; correlated partner histories and
  group-level reliability.
- **Clinical modeling** only after stronger empirical validation.

## Not Current Priorities

- Broad hyperparameter sweeps.
- Reviving historical stress-shape figures from bounded-error outputs.
- Treating payoff as the primary success metric for every hypothesis.

## Stopping Rule

Do not add more sweeps just because the story has caveats. A mechanistic paper
is stronger when it states its boundary condition clearly than when it hides it
behind broad exploratory reruns. No broad follow-up is required before a
manuscript draft if claims stay narrow.
