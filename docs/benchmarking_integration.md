# Benchmarking Integration: Trust Backend + Real CvC

## Status

The benchmark layer is now organized around explicit backends rather than a
trust-game runner with a fake `gridworld` toggle.

- `trust` is the canonical production backend for the current affect_aif agents.
- `cvc_local` is the real CoGames/CvC backend. It runs through a Python 3.12
  worker and uses the same policy class path / policy spec shape that can later
  be packaged for submission.
- `toy_gridworld` remains only as a backward-compatible scripted adapter around
  the old trust-like fallback. It is not a real CoGames integration and should
  not be used for transfer claims.

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

`affect_aif/benchmark/benchmark_config.py` now uses:

- `backends: list[str]`
- `agents: list[AgentSpec]`
- `backend_configs: dict[str, dict]`
- `observatory: dict | None`

`AgentSpec` is backend-specific:

- trust and toy-gridworld use registry-backed agents such as
  `affective_shallow`, `random`, `pavlov`, `grim_trigger`
- CvC uses explicit policy specs such as
  `class=affect_aif.benchmark.cvc_policy.TeammateReliabilityPolicy`

Legacy config booleans (`run_trust_game`, `run_gridworld`) are still parsed for
compatibility, but they are converted immediately into backend selections.

### Backends

- `affect_aif/benchmark/trust_backend.py`
  Canonical trust benchmark backend. Reuses the current `ExperimentRunner`,
  `TrustGameEnv`, and benchmark baseline agents.
- `affect_aif/benchmark/cvc_local_backend.py`
  Real local CvC backend. Launches `python3.12 -m affect_aif.benchmark.cvc_local_worker`.
- `affect_aif/benchmark/toy_gridworld_backend.py`
  Deprecated scripted adapter for old experiments only.

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

## Trust Backend

The trust backend is the main benchmark for the existing active-inference
theory. It now includes:

- Pavlov baseline
- Grim Trigger baseline
- benchmark JSON configs under `affect_aif/configs/`
- scheduled-switch propagation through benchmark results
- hard failure for the old `AIFPolicy` stubs instead of silently wrong behavior

Recommended trust configs:

- `affect_aif/configs/benchmark_default.json`
- `affect_aif/configs/benchmark_betrayal.json`
- `affect_aif/configs/benchmark_full.json`

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

- `affect_aif.benchmark.cvc_policy.TeammateReliabilityPolicy`

This is deliberately not called an active-inference policy. It is a rule-based
team policy with shared per-teammate reliability tracking and role allocation.

### Submission-compatible packaging

`affect_aif/benchmark/cvc_packaging.py` writes `policy_spec.json` bundles using
the same class-path format the local backend already consumes. The goal is to
avoid maintaining a separate “submission version” of the policy.

## Observatory Integration

`affect_aif/benchmark/observatory.py` is a read-only client for:

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
python scripts/run_benchmark.py --backend trust --config affect_aif/configs/benchmark_default.json
python scripts/run_benchmark.py --backend trust --agents affective_shallow random tit_for_tat --rounds 50 --replications 3
python scripts/run_benchmark.py --backend cvc_local --agents teammate_reliability starter --mission machina_1 --max-steps 250 --python-bin python3.12
```

### Analyze benchmark results

```bash
python scripts/analyze_benchmark.py --results results/benchmark/benchmark_results.csv
```

Outputs are written next to the CSV by default:

- `benchmark_shared_summary.csv`
- `benchmark_trust_summary.csv`
- `benchmark_cvc_summary.csv`
- `benchmark_report.txt`

## Notes

- Do not claim cross-environment “transfer” based on `toy_gridworld`.
- Do not reinterpret the CvC policy as an AIF agent unless a real generative
  model and inference loop are added later.
- Keep trust-specific hypothesis reads in trust analyses and use reward /
  coordination summaries for cross-backend comparisons.
