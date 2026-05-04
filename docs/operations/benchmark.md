# Evaluation Integration: Trust-Task Arena + Experimental CvC

## Status

The evaluation layer separates the trust-task arena from external benchmark
backends rather than treating the trust game as a benchmark peer of CvC.

- `trust` routes to the canonical, supported trust-task evaluation arena for
  the current affect_aif agents and theory-facing evaluation.
- `cvc_local` is a real CoGames/CvC backend, but it is still proof-of-concept
  / WIP. It runs through a Python 3.12 worker and uses the same policy class
  path / policy spec shape that can later be packaged for submission.

## Why the Split Exists

The trust game and CvC are not the same task with a different state list.

- Trust game: repeated single-focal-agent social dilemma with explicit partner
  identity and hidden partner type.
- CvC: partially observed, tick-level, multi-agent territory control with role
  specialization, shared reward, and token observations.

Because of that mismatch:

- shared analysis only compares reward-centric summaries across backends
- trust-specific and CvC-specific metrics are reported separately
- we do not map CvC actions into fake `cooperate/defect` labels

## Current Architecture

### Config model

`benchmarks/core/benchmark_config.py` uses:

- `backends: list[str]`
- `agents: list[AgentSpec]`
- `backend_configs: dict[str, dict]`
- `observatory: dict | None`

`AgentSpec` is backend-specific:

- trust uses registry-backed agents such as `tau4_affect`, `random`,
  `pavlov`, `grim_trigger`
- CvC uses explicit policy specs such as
  `class=benchmarks.cvc.policy.TeammateReliabilityPolicy`

### Evaluation Surfaces

- `tasks/trust/evaluation/arena.py`
  Canonical trust-task evaluation arena. Reuses the current
  `ExperimentRunner`, `TrustGameEnv`, and trust-task baseline agents.
- `benchmarks/cvc/local_backend.py`
  Real local CvC backend. Launches `python3.12 -m benchmarks.cvc.local_worker`.

### Shared record schema

All backends emit records with the shared fields:

- `schema_version`
- `backend`
- `scenario`
- `agent_name`
- `seed`
- `episode_id`
- `step`
- `reward`

Backends may add extra columns:

- trust: `payoff`, `partner_action`, `true_partner_type`, `type_switched`, etc.
- CvC: `team_reward_mean`, `aligned_junctions`, `hearts_gained`,
  role-specific gains, and other episode summaries

## Trust-Task Evaluation Arena

The trust-task evaluation arena is the main comparison surface for the existing
active-inference theory. It now includes:

- Pavlov baseline
- Grim Trigger baseline
- benchmark JSON configs under `configs/`
- scheduled-switch propagation through benchmark results
- unfinished CoGames policy adapters are not shipped in `benchmarks/core/`
  (add one under `benchmarks/cvc/` when CvC integration is active)

Recommended trust configs:

- `configs/benchmark_default.json`
- `configs/benchmark_betrayal.json`
- `configs/benchmark_full.json`

Scenario defaults now matter for the trust-task evaluation arena rather than
serving as labels only. In particular, `betrayal_arena` now carries its own
trust-game setup: `assignment_mode="agent_choice"`, `p_switch=0`, an initial
roster of `["cooperator", "random"]`, and a scheduled `partner 0 -> exploiter`
switch at round 50 unless a benchmark config overrides those values.

## Real CvC Backend

### Runtime split

The main repo stays on Python 3.10. Real CoGames execution happens in Python
3.12 because `cogames` requires `>=3.12,<3.13`.

The intended workflow is:

1. keep normal trust-game work in the project venv
2. create a separate Python 3.12 environment for CoGames
3. run the canonical benchmark CLI from the repo root
4. let the `cvc_local` backend dispatch the worker process

### Policy shape

The first real local CvC policy is:

- `benchmarks.cvc.policy.TeammateReliabilityPolicy`

This is deliberately not called an active-inference policy. It is a rule-based
team policy with shared per-teammate reliability tracking and role allocation.

### Submission-compatible packaging

`benchmarks/cvc/packaging.py` writes `policy_spec.json` bundles using
the same class-path format the local backend already consumes. The goal is to
avoid maintaining a separate “submission version” of the policy.

## Observatory Integration

`benchmarks/cvc/observatory.py` is a read-only client for:

- season discovery
- season detail
- leaderboard fetches
- pool config fetches
- compat-version validation

This is intended for metadata, local validation, and future packaging checks.
It does not log in, upload, or submit policies.

## CLI

### Run benchmarks

```bash
python scripts/benchmark/run_cvc.py --backend trust --config configs/benchmark_default.json
python scripts/benchmark/run_cvc.py --backend trust --agents tau4_affect random tit_for_tat --rounds 50 --replications 3
# Experimental / WIP: requires Python 3.12 and uses the real CvC local worker.
python scripts/benchmark/run_cvc.py --backend cvc_local --agents teammate_reliability starter --mission machina_1 --max-steps 250 --python-bin python3.12
```

For day-to-day evaluation work, prefer the trust-task arena. The `cvc_local`
example is included to document the current experimental surface, not to imply
parity with the supported trust-task evaluation arena.

### Analyze benchmark results

```bash
python scripts/benchmark/analyze.py --results results/benchmark/benchmark_results.csv
```

Outputs are written next to the CSV by default:

- `benchmark_shared_summary.csv`
- `benchmark_trust_summary.csv`
- `benchmark_cvc_summary.csv`
- `benchmark_report.txt`

## CvC Integration Status (2026-03-21)

This section tracks the experimental local CvC backend. It is useful for
validation and packaging work, but it should be treated as WIP rather than the
primary benchmark surface.

### What works end-to-end

The full CvC pipeline runs cleanly:

1. **Python 3.10 orchestrator** (`scripts/benchmark/run_cvc.py`) loads config and dispatches
2. **CvC local backend** spawns `python3.12 -m benchmarks.cvc.local_worker` subprocess
3. **Worker** imports cogames/mettagrid, resolves mission, runs episode, extracts metrics
4. **Results** flow back as JSON → DataFrame → CSV → comparison report
5. **Analysis** pipeline (`scripts/benchmark/analyze.py`) computes CvC-specific summaries

Verified with: `benchmark_cvc_full.json` (6 policies × 10 seeds × 10,000 steps = 60 episodes).

Available CvC policies tested:

| Policy | Source | Role gains | Hearts |
|--------|--------|-----------|--------|
| `TeammateReliabilityPolicy` | custom | mixed | 6.7 |
| `StarterPolicy` | cogames built-in | mixed | 7.0 |
| `MinerRolePolicy` | cogames built-in | miner-heavy | 6.9 |
| `AlignerRolePolicy` | cogames built-in | aligner-heavy | 7.1 |
| `ScramblerRolePolicy` | cogames built-in | scrambler-heavy | 7.1 |
| `ScoutRolePolicy` | cogames built-in | scout-heavy | 6.9 |

### Known limitations

1. **All policies score 0 reward and 0 aligned junctions.** The CvC game loop
   (get gear → mine → deposit → get hearts → align junction) requires effective
   navigation, but both built-in and custom rule-based policies have ~80% failed
   moves (walking into walls). No rule-based policy in cogames 0.19.2 completes
   the full scoring loop.

2. **CvC has only 5 actions** (`noop`, `move_north/south/east/west`). All object
   interaction is proximity-based. Scoring requires effective pathfinding which
   the simple “move toward nearest tag” heuristic cannot provide.

3. **No direct Python 3.10 tests for `policy.py`** since it requires
   mettagrid (Python 3.12 only). The CvC worker subprocess is tested via mock.

### What's needed to get meaningful CvC results

- **Better navigation**: A* pathfinding or wall-avoidance to replace the simple
  directional move heuristic. Currently ~80% of move actions fail.
- **Or trained policies**: The cogames `PufferlibCogsPolicy` supports RL-trained
  agents. A trained policy would likely score non-zero.
- **Or a simpler mission**: The `machina_1` mission has a complex map with walls.
  A more open map might let rule-based policies succeed.

### Dependencies

- `cogames>=0.19.2` — installed via `python3.12 -m pip install cogames`
- `mettagrid>=0.19.3` — pulled in as cogames dependency
- Both require Python `>=3.12,<3.13`

## Notes

- Do not reinterpret the CvC policy as an AIF agent unless a real generative
  model and inference loop are added later.
- Keep trust-specific hypothesis reads in trust analyses and use reward /
  coordination summaries for cross-backend comparisons.
