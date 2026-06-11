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

### Single-Worker Batch Runner Follow-Up

`BatchExperimentRunner(workers=1)` now runs expanded variant/replication tasks
inline instead of constructing a one-worker `ProcessPoolExecutor`. A follow-up
cleanup also routes inline execution directly through `ExperimentRunner` rather
than the process-safe task wrapper, while sharing the same variant payload
builder used by process workers. Seeds, model dynamics, per-round rows,
checkpoint resume semantics, and output paths are unchanged.

Deterministic old-vs-new CSV comparison on a graded random-assignment probe:
6 rows x 50 columns matched exactly after the worker-path change.

Tiny batch timing probe: 2 variants x 4 replications x 4 rounds = 32 rows.

| Checkout | `workers=1` | `workers=2` | `workers=4` |
|---|---:|---:|---:|
| process-pool `workers=1` baseline | 6.921 s | 4.568 s | 3.745 s |
| inline `workers=1` follow-up | 6.432 s | 4.779 s | 3.810 s |
| direct inline runner follow-up | 6.350 s | 4.692 s | 3.846 s |

The single-worker path is about 7-8% faster on this small probe and simpler to
reason about during local deterministic checks. Multi-worker differences are
within the observed timing band and do not change behavior.

### Runner Provenance And Verbosity Cleanup

Serial, single-worker inline, and multi-worker batch runs now record resolved
absolute config paths in result rows and `batch_metadata.json`. This removes a
public-facing provenance inconsistency where the same config could be recorded
as absolute or CLI-relative depending on the execution path.

The serial and single-worker inline paths also pass
`--verbose --verbosity-mode stage_stream` through to `ExperimentRunner`, so
local stage-stream inspection works consistently on the deterministic local
paths. This cleanup changes runner metadata and console output only; it does
not alter seeds, task dynamics, `pymdp` calls, observations, actions, beta
updates, or manuscript-facing scalar values.

### Persistent JAX Compilation Cache

The runner already supports `--jax-cache-dir`, which enables JAX persistent
compilation caching before importing the experiment stack. This is
exact-preserving: it changes compilation reuse only, not seeds, policies,
observations, actions, or result rows.

CLI timing probe: 2 variants x 2 replications x 4 rounds = 16 rows, separate
Python process per run.

| Mode | Wall time |
|---|---:|
| no cache, first run | 5.375 s |
| no cache, second run | 5.242 s |
| cache directory, cold | 3.618 s |
| cache directory, warm | 2.446 s |

Recommendation: use a persistent cache directory for repeated same-shape local
checks and paper reruns, for example `--jax-cache-dir /tmp/affect_aif_jax_cache`
or `AFFECT_AIF_JAX_CACHE_DIR=/tmp/affect_aif_jax_cache`.

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
- Potential benefit: low to moderate on current tiny probes; possibly higher
  only if many runs share expensive static policy templates.
- Why: each expanded run builds templates and partner agents even when only the
  seed or beta prior differs.
- Measurement: an agent-choice construction probe spent 0.040 s constructing
  environments and 0.654 s constructing native runtime/templates/agents across
  8 replications, versus 11.735 s total replication time. Construction was
  about 5.9% of total replication time.
- Risk: medium. Shared mutable agent state or RNG coupling could silently alter
  trajectories. Exact template caching must include all static config,
  variant, policy, and seed inputs; ignoring seed can change sampled/truncated
  policy sets when `max_policies` is active.
- Validation: strict deterministic row equality for several tiny specs, plus a
  paper-config dry-run/materialization comparison before adoption.
- Recommendation: do not prioritize before policy-inference/JAX work.

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
- Potential benefit: low to moderate, workload dependent. It may help when many
  tiny expanded runs pay more process scheduling overhead than inference work.
- Why: each expanded run is one process-pool task. Larger per-worker chunks
  could reduce serialization and scheduling cost.
- Measurement: a throwaway chunked prototype on 16 expanded runs x 4 rounds
  matched sorted rows exactly. One-task-per-replication took 6.77 s; chunks of
  2 took 6.27 s; chunks of 4 measured about 6.35-6.55 s.
- Risk: medium for the current runner. Result ordering can be normalized, but
  checkpoint cadence and failure recovery become less immediate if several
  replications are bundled into one future.
- Validation: multi-config batch tests, checkpoint resume tests, and final
  row-set equality independent of completion order.
- Recommendation: do not ship yet. The observed gain is too small and uneven to
  justify complicating checkpoint semantics.

### Candidate 5: Runner-Side Pymdp Call/Batching Audit

- Tier: `near-equivalent`
- Potential benefit: possibly high if project-owned orchestration can reduce
  redundant setup or batch independent calls while still using official
  `inferactively-pymdp` APIs.
- Why: the tiny runner checks show official `pymdp` policy inference dominates
  total runtime after logging is trimmed. The target is how often and how
  efficiently our runner calls `pymdp.Agent`, not replacing or editing pymdp's
  policy-inference implementation.
- Risk: high for current manuscript evidence if batching changes dtypes,
  numerical order, sampling order, or pseudorandom streams.
- Validation: explicit user approval, full paper rerun, interpretation-level
  comparison against current manuscript source tables, and documented
  acceptance thresholds for numerical differences.

## Recommendation

Keep the shipped `data_collection` logging contract and the inline
single-worker batch path. Both are exact-preserving and public-facing: fast mode
now records what the manuscript analyzes, debug mode keeps internal arrays
available, and `--workers 1` remains the clean deterministic local execution
path.

The next low-risk operational target is to use the persistent JAX cache for
reruns. The next code target with meaningful upside is runner-side pymdp-call
orchestration, not template construction reuse or a fork of pymdp inference.
Any batching/vectorization experiment should be a separate approved rerun
project.
