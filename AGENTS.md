# AGENTS.md — System Documentation

This document provides comprehensive system documentation for AI agents operating on the affect_aif codebase. It covers architecture, module interfaces, experiment pipeline, and operational procedures.

## Documentation First

- Read `docs/state/README.md` and `docs/state/current/mission.md` before taking over a research or restructure task.
- Read `docs/theory/goals.md`, `docs/theory/hypotheses.md`, and `docs/theory/pomdp_spec.md` before changing computational claims, affect dynamics, terminal values, or the interpretation of results.
- Read `docs/theory/apashea_alignment.md` before changing factorized controls, policy priors, learning hooks, or pymdp/JAX alignment claims.
- Read `docs/experiment/design.md` before changing task design, configs, variants, metrics, or sensitivity sweeps.
- Read `docs/design/implementation.md` before changing environment semantics, switching logic, or analysis helpers.
- Read `README.md` before changing setup, entry points, or repo layout.

## Required Follow-Through

- If code behavior changes, update the relevant docs in the same change.
- If experiment assumptions change, update both theory-facing and experiment-facing docs.
- If configs or scripts change, update the README or implementation notes so the runnable workflow stays accurate.
- If tests reveal a theory/code mismatch, fix both the implementation and the docs before closing the task.

## Learned User Preferences

- Before updating result-interpretation docs from new experiment outputs, ask the user first.
- When the user asks about branch state, merge readiness, or pruning stale remote branches, run git (fetch or prune as needed) and summarise concrete outputs instead of only listing commands.
- For docs/state-driven research, treat `docs/state/current/mission.md` as the source of truth for phase autonomy; do not default to “blocked” framing when the mission tells the agent to proceed or to choose the next phase.

## Learned Workspace Facts

- Use `.venv` in project root; venv should auto-activate when in this folder (direnv with `.envrc`).
- Recommended experiment run: queue the relevant TOML specs under `experiments/trust/hypotheses/` in one batch with `--workers 12`; results go under `results/<batch_name>/<hypothesis_id>/<experiment_id>/results.csv`; run `scripts/analysis/analyze.py` on those paths after.
- Random-assignment specs are weak discriminators for the current hypothesis spine; use agent-choice scheduled-stance-switch specs for stress-response results.
- Official `inferactively-pymdp==1.0.0` is the supported runtime. Do not reintroduce a custom active-inference engine; keep affect and trust logic in task modules.
- State inference (partner-type belief updating) is handled by official
  `pymdp.Agent` instances created from `tasks.trust.pomdp` templates and logged
  as matrix-based belief updates.
- Benchmark runs use `scripts/benchmark/run_cvc.py` plus `docs/operations/benchmark.md` for backends, TOML configs (for example `configs/benchmark_default.toml` and `configs/benchmark_betrayal.toml`), and Python 3.12 CvC worker notes.
- Remote VMs, sync, and merge flows for this project use `mango` (CLI at `~/Desktop/mango/`, available globally). See "Mango" section in `CLAUDE.md` for full command reference. Key: `mango run affect_aif --cloud` to launch, `mango stop affect_aif --remote` to stop, `mango cloud sync push/fetch affect_aif` to sync code/results (`sync push` is rsync and does not delete remote-only files under `results/`). Do not add orchestration or deployment scripts to this repo.

---

## Architecture

### Module Dependency Graph

```
affect_aif/
├── inferactively-pymdp==1.0.0  # Supported active-inference runtime dependency
├── tasks/
│   └── trust/             # Trust-task package
│       ├── envs/          # Binary and graded trust-game environments
│       ├── pomdp.py       # Native trust POMDP template and pymdp.Agent construction
│       ├── runtime.py     # PartnerBank and procedural plan/update helpers
│       ├── affect.py      # External HESP beta tracking
│       ├── evaluation/    # Trust-task evaluation arena and baselines
│       ├── payoffs.py     # Trust-game payoff and action encoding helpers
│       ├── stance.py      # Stance dynamics
│       └── types.py       # Partner type metadata
├── experiments/
│   ├── trust/             # Depends on: tasks.trust
│   │   ├── config.py      # ExperimentConfig runtime dataclass
│   │   ├── spec.py        # TOML ExperimentSpec and variant expansion
│   │   ├── runner.py      # ExperimentRunner for expanded variant runs
│   │   ├── batch.py       # BatchExperimentRunner (multi-config parallel)
│   │   ├── logger.py      # MetricLogger (per-round recording)
│   │   ├── progress.py    # ProgressReporter
│   │   └── factory.py     # Agent/model/environment factories
│   └── multifocal/        # M native trust runtimes, turn-taking rounds (sub-project F)
│       ├── config.py      # Parses heterogeneous `agents: [...]` multi-focal JSON
│       ├── runner.py      # Multi-focal runtime
│       └── joint_resolution.py # Pairwise payoff obs from actions
├── analysis/              # Depends on: nothing (operates on DataFrames)
│   ├── metrics.py         # Summary statistics, betrayal analysis, movement
│   ├── statistics.py      # ANOVA, pairwise tests
│   ├── hypotheses.py      # Current Hesp-extension hypothesis helpers
│   ├── plots.py           # Matplotlib figure generation
│   └── visualization.py   # GIF generation
└── configs/               # External benchmark and CvC TOML configurations
```

### Experiment Variants

Trust experiments are declared as TOML specs under
`experiments/trust/hypotheses/`. Each spec expands explicit `[[variants]]`
instead of numeric condition IDs or presets.

Core maintained variant knobs:

| Field | Examples | Meaning |
|----|------|-------|
| `affect` | `none`, `precision`, `tracked_only` | Runtime affect mode |
| `planning_horizon` | `1`, `2`, `4`, `8` | Native pymdp policy horizon |
| `epistemic_value` | `true`, `false` | Whether policy inference uses information gain |
| `alpha_charge`, `initial_beta`, `beta_persistence`, `beta_levels` | numeric / arrays | Affective precision dynamics |

### Experiment Pipeline Flow

```
TOML ExperimentSpec → expanded variant runs → ExperimentRunner
    │
    ├── run_all()                   # All expanded variant runs
    │   └── run_replication()       # Single variant × single seed
    │       ├── create_native_runtime_from_run() # Trust POMDP template + PartnerBank
    │       ├── _create_env()       # TrustGameEnv or GradedTrustGameEnv
    │       └── _run_episode()      # Main loop: infer policies → step → update
    │
    └── save_results()              # DataFrame → CSV
         │
         ▼
    scripts/analysis/analyze.py     # Post-hoc analysis
    ├── final_round_summary()
    ├── cumulative_payoff_anova()
    ├── pairwise_payoff_tests()
    ├── run_all_hypothesis_tests()
    ├── affective_movement_summary()
    └── save_all_figures()
```

### Native Runtime Lifecycle (per round)

```
select_decision(...)
    ├── Pick the active partner or evaluate each partner-local pymdp.Agent
    ├── Set partner-specific gamma from external beta when enabled
    ├── Call official pymdp.Agent.infer_policies(...)
    ├── Select a policy/action
    └── Return a Decision with raw env action and diagnostics

env.step(action)
    ├── Decode action → (partner_idx, agent_action)
    ├── Partner responds according to type strategy
    ├── Compute payoff
    └── Return observation dict

update_partner_after_observation(...)
    ├── Call official pymdp.Agent.infer_states(...)
    ├── Store partner-local posterior and next prior snapshots
    ├── [Affective] update external beta from prediction error
    └── Log snapshot fields for analysis
```

## Configuration System

Trust specs live in `experiments/trust/hypotheses/`, multi-focal configs live in
`experiments/multifocal/configs/`, and external benchmark/CvC configs live in
`configs/`. `ExperimentConfig` is now an internal runtime adapter derived from
expanded TOML runs. Key runtime fields:

### Game Structure
- `payoff_mode`: "binary" | "graded"
- `num_partners`: default 4
- `num_rounds`: default 200
- `assignment_mode`: "random" | "agent_choice"
- `scheduled_stance_switches`: list of stance-shift events for betrayal-style scenarios

### Agent Parameters
- `planning_horizon`: planning depth, supplied by each variant before runtime construction
- `alpha_charge`: prediction error scaling (3.0)
- `sigma_0_sq`: prior variance (0.25)
- `initial_beta`: starting precision prior (1.0)
- `beta_num_levels`: number of discrete beta support points (default 5)
- `beta_persistence`: transition persistence for the beta posterior (0.8)
- `gamma`: base policy precision before partner-local beta modulation

### Run Parameters
- `replications`: seeds per variant in TOML experiment metadata
- `random_seed`: base seed
- `[[sweeps]]`: optional explicit variant-parameter expansion

## Analysis Outputs

`scripts/analysis/analyze.py --results <csv> --output-dir <dir>` produces:

| File | Contents |
|------|----------|
| `final_round_summary.csv` | Per-seed cumulative payoffs and accuracy |
| `pairwise_payoff_tests.csv` | All variant pairs: t-stat, p-value, Cohen's d |
| `hypothesis_tests.json` | Structured hypothesis test results |
| `hypothesis_summary.csv` | One-row-per-hypothesis overview |
| `affective_movement_summary.csv` | Beta / precision-signal range per seed |
| `statistics_summary.txt` | ANOVA + movement + betrayal summaries |
| `betrayal_*.csv` | (if switch events) Post-switch window analysis |
| `*.png` | Figures: payoff distributions, beta trajectories, etc. |

## Key Invariants

1. **Sophisticated inference**: Policy evaluation uses observation-branching, not mean-field rollout
2. **Native pymdp boundary**: policy/state inference stays inside official `pymdp.Agent`; task code only constructs matrices and manages partner-local beta/gamma
3. **Deterministic seeds**: `random_seed + replication_index` ensures reproducibility
4. **Variant equality**: same-horizon no-affect and tracked-only variants should match when precision is decoupled
5. **Binary saturation**: EFE gaps ~10.83 in binary game → softmax is hard argmax → precision modulation inert
6. **Graded activation**: q_pi_entropy ~5.8 in graded game → precision modulation channel active

## Troubleshooting

### Tests fail after code change
```bash
python -m pytest tests/ -v --tb=short
.venv/bin/python -m pytest tests/test_package_surface.py tests/test_supported_surface.py -q  # supported package surface
```

### Experiment produces unexpected results
1. Run with `--verbose --verbosity-mode stage_stream` for per-round tracing
2. Check beta/gamma traces and `q_pi_entropy` in the per-round results
3. Check current state in `docs/state/current/blockers.md`
4. Compare against current and historical status in `docs/results/`

### Analysis script errors
- Check CSV has expected columns: `variant_id`, `seed`, `round`, and `payoff`
- Filter or group by `variant_id` for hypothesis comparisons
