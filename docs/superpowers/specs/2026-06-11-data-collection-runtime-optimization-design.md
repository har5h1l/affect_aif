# Data Collection Runtime Optimization Design

## Goal

Reduce experiment runtime overhead without changing trust-task dynamics,
random seeds, active-inference inference calls, action sampling, environment
transitions, or manuscript interpretations.

The first implementation packet should wire the existing
`profile = "data_collection"` mode into a strict manuscript-facing result
contract. It should log everything needed to regenerate the current paper
analyses, source tables, figures, and public notebook summaries, while moving
bulky diagnostic-only internals into `profile = "debug"`.

## Non-Goals

- Do not add a new execution mode.
- Do not change `inferactively-pymdp==1.0.0` usage.
- Do not change model matrices, beta updates, partner dynamics, action
  selection, random seeding, or environment behavior.
- Do not reinterpret results or update manuscript claims from new outputs.
- Do not ship JAX/vectorization changes that alter numerical trajectories in
  this packet.

## Current Context

The repository already has a maintained `data_collection` runtime profile. It
is the default profile for paper, demo, diagnostic, and future configs. Current
docs define it as the fast path for essential per-round result rows, with
debug policy traces and automatic analysis kept outside the statistical data
collection path.

Recent runtime optimizations already improved equivalent execution paths by
reducing import overhead, adding a single-worker fast path, improving
checkpoint resume filtering, and documenting optional JAX persistent
compilation caching. The next likely exact-preserving opportunity is narrower:
reduce per-round logging and serialization overhead in `data_collection`.

## Design

### Data Collection Contract

`profile = "data_collection"` should mean: record the manuscript-facing
trajectory fields required for paper analysis, and omit diagnostic-only arrays
that are not consumed by the paper source-table or figure builders.

The data-collection row contract must include fields needed for:

- payoff and total-payoff summaries
- selected partner, active partner, raw action, selected action, and partner
  action readouts
- `q_pi_entropy` and other scalar policy-openness readouts used in the paper
- local/global beta traces used by Exp A-C and locality analysis
- prediction errors, predictive log likelihood, round log evidence, and
  cumulative log evidence for model-fitness and surprise-over-reward analyses
- inferred type, inferred stance, and joint correctness readouts
- switch markers, scheduled switch partner ids, true partner types, and true
  stances needed by betrayal, forgiveness, and reencounter windows
- seed, replication, variant, config, batch, hypothesis, and experiment
  metadata

The contract should exclude from `data_collection` unless a current
manuscript-facing analyzer requires them:

- full `q_pi` vectors
- full policy score vectors `G`
- `best_policy_step_costs`
- full nested partner belief matrices
- full nested partner posterior matrices
- full joint belief/posterior tensors
- full stance belief matrices

Those diagnostic arrays should remain available in `profile = "debug"`.

### Runtime Boundaries

The runner should continue to follow the current data flow:

```text
TOML spec
-> ExpandedRunSpec
-> ExperimentRunner
-> NativeTrustRuntime / official pymdp + TrustGameEnv
-> per-round result row
-> results.csv
-> analysis scripts
-> manuscript source tables and figures
```

The optimization boundary is only the per-round result row construction and
serialization. The scientific core must remain unchanged.

`MetricLogger` is the natural implementation boundary. It can become
profile-aware, or receive an explicit logging contract derived from
`RuntimeSpec.profile`. `ExperimentRunner` should pass the existing runtime
profile through when constructing the logger. `debug` should preserve the
current full diagnostic surface.

### Audit Lane

In parallel with the exact data-collection change, produce a measured audit of
additional candidates. The audit should classify candidates into three risk
tiers:

- `exact`: preserves model behavior, random streams, and manuscript-facing
  values; acceptable for the first implementation packet.
- `analysis-equivalent`: may alter raw schema, internal representation, or
  low-level ordering, but should preserve manuscript readouts after analysis.
- `near-equivalent`: may alter pseudorandomness or numerical details, such as
  deeper JAX/vectorized rewrites; requires explicit user approval and a full
  rerun before adoption.

The first implementation packet should ship only `exact` changes. The audit
may recommend B/C candidates, but should not implement them.

## Verification

Use focused checks before any broad rerun:

1. Column-contract test: a tiny maintained config run under
   `profile = "data_collection"` emits every column required by paper analysis
   and notebook summaries.
2. Debug-surface test: the same tiny run under `profile = "debug"` still emits
   the heavier diagnostic arrays.
3. Exactness test: on a deterministic smoke config, paper-facing scalar values
   and trajectory choices match the current behavior before and after the
   logging change.
4. Analysis replay test: configured analysis and phenotype artifact builders
   run successfully from lean `data_collection` outputs.
5. Docs check: update `docs/experiments/running.md`,
   `docs/experiments/configs.md`, and script docs if the row contract or
   profile semantics change.

Before scheduling any full evidence rerun, run the active verification gate:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
git diff --check
```

Full paper reruns, if needed, should happen on `server` through detached
tmux/Mango process registration, not as a Codex app-server child.

## Acceptance Criteria

- `profile = "data_collection"` contains everything needed for current
  manuscript/paper analysis.
- `profile = "debug"` keeps diagnostic internals available.
- Paper-facing analysis scripts and public notebook summaries can consume lean
  data-collection outputs.
- Focused deterministic checks show no change to model behavior, action
  trajectories, or manuscript-facing scalar readouts.
- The measured audit reports B/C optimization candidates with risk tier,
  expected benefit, and required validation before any deeper change is made.
