# Runtime Optimization Audit - 2026-06-11

This audit records optimization work around the trust experiment runner. It is
not an interpreted result update and does not change manuscript claims.

## Shipped Exact-Preserving Change

`profile = "data_collection"` now logs the manuscript-facing result contract
only. It keeps payoff, choice, entropy, beta/precision, surprise/log-evidence,
inference-correctness, switch, seed, variant, config, and batch metadata needed
by the paper analysis path. It no longer serializes diagnostic-only policy and
belief internals:

- full `q_pi` vectors
- full policy-score vectors `G`
- `best_policy_step_costs`
- partner belief and posterior matrices
- joint belief and posterior tensors
- stance belief matrices

`profile = "debug"` still logs those internals.

This change does not alter trust-task dynamics, random seeds, `pymdp` calls,
action sampling, environment transitions, beta updates, or manuscript-facing
scalar readouts. A focused equivalence test compares data-collection and debug
outputs on deterministic manuscript-facing columns.

## Measurements

Measurements used the parent virtualenv and pinned `PYTHONPATH` to the checkout
being measured.

### Tiny End-To-End Runner Check

Synthetic graded agent-choice spec: 2 variants x 1 replication x 8 rounds = 16
rows.

| Checkout | Columns | Diagnostic columns in `data_collection` | CSV bytes | Warm run |
|---|---:|---|---:|---:|
| pre-change default logger | 58 | present | 59,540 | 3.50 s |
| optimized `data_collection` | 50 | absent | 10,428 | 3.51 s |

The wall time is effectively unchanged at this tiny scale because official
`pymdp` inference dominates. The raw row payload is much smaller: about 82.5%
less CSV output for this check.

### Logger/CSV Microbenchmark

Synthetic logger rows with representative policy vectors and belief tensors:
10,000 rows.

| Mode | Columns | CSV bytes | Log time | CSV time | Total |
|---|---:|---:|---:|---:|---:|
| pre-change data collection | 51 | 30,319,762 | 0.297 s | 0.680 s | 1.010 s |
| optimized `data_collection` | 43 | 3,849,627 | 0.088 s | 0.096 s | 0.212 s |
| optimized `debug` | 51 | 49,569,762 | 0.369 s | 1.087 s | 1.486 s |

The targeted logging/CSV path is about 4.8x faster in the microbenchmark, with
about 87.3% less CSV output. Full experiment wall-clock speedup will be smaller
when `pymdp` inference dominates, but checkpoint and final-result writes should
be materially lighter on long paper runs.

## B/C Candidate Audit

### Candidate 1: Checkpoint Write Cadence And Format

- Tier: `exact`
- Potential benefit: moderate for long runs with frequent checkpoints.
- Why: current checkpointing can rewrite all accumulated rows at each
  checkpoint. Lean rows reduce this cost; increasing checkpoint interval or
  writing append-style chunks would reduce it further.
- Risk: low if resume logic is updated and tested carefully.
- Validation: interrupted-run resume tests, structural completion checks, and
  equality of final manuscript-facing rows against the current checkpoint path.

### Candidate 2: Static Template/Agent Construction Reuse

- Tier: `analysis-equivalent`
- Potential benefit: moderate to high if repeated runs share the same static
  POMDP template shape.
- Why: each expanded run builds templates and partner agents even when only the
  seed or beta prior differs.
- Risk: medium. Shared mutable agent state or RNG coupling could silently alter
  trajectories.
- Validation: strict deterministic row equality for several tiny specs, plus a
  paper-config dry-run/materialization comparison before adoption.

### Candidate 3: Snapshot Conversion Caching

- Tier: `exact` if limited to debug-only snapshots; `analysis-equivalent` if it
  changes any timing of posterior extraction.
- Potential benefit: low to moderate. The data-collection path now avoids
  planning-time diagnostic snapshots, but post-observation inferred
  type/stance still requires one snapshot per round.
- Risk: low for debug-only caching, medium if shared with manuscript inference
  readouts.
- Validation: data_collection/debug equivalence on manuscript columns and debug
  posterior-shape tests.

### Candidate 4: Process-Pool Scheduling Granularity

- Tier: `exact`
- Potential benefit: workload dependent. It may help when many tiny expanded
  runs pay more process scheduling overhead than inference work.
- Why: each expanded run is one process-pool task. Larger per-worker chunks
  could reduce serialization and scheduling cost.
- Risk: low to medium. Result ordering and checkpoint resume semantics must
  remain stable.
- Validation: multi-config batch tests, checkpoint resume tests, and final
  row-set equality independent of completion order.

### Candidate 5: Deeper JAX/Vectorized Runtime Rewrite

- Tier: `near-equivalent`
- Potential benefit: possibly high, especially if policy inference or
  partner-choice scoring can be vectorized across partners/runs.
- Why: the actual tiny runner check shows `pymdp` inference dominates total
  runtime after logging is trimmed.
- Risk: high for current manuscript evidence. Vectorization can change dtypes,
  numerical order, sampling order, or pseudorandom streams.
- Validation: explicit user approval, full paper rerun, interpretation-level
  comparison against current manuscript source tables, and documented
  acceptance thresholds for numerical differences.

## Recommendation

Keep the shipped `data_collection` logging contract. It is exact-preserving and
public-facing: fast mode now records what the manuscript analyzes, while debug
mode keeps internal arrays available.

The next low-risk target is checkpoint cadence/format. The next high-upside
target is template/agent construction reuse, but it should be treated as
analysis-equivalent until deterministic equality checks prove otherwise. A
deeper JAX/vectorization rewrite should be a separate approved rerun project.
