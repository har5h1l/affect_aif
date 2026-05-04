# AGENTS.md — System Documentation

This document provides comprehensive system documentation for AI agents operating on the affect_aif codebase. It covers architecture, module interfaces, experiment pipeline, and operational procedures.

## Documentation First

- Read `docs/state/README.md` and `docs/state/current/mission.md` before taking over a research or restructure task.
- Read `docs/theory/goals.md`, `docs/theory/hypotheses.md`, and `docs/theory/pomdp_spec.md` before changing computational claims, affect dynamics, terminal values, or the interpretation of results.
- Read `docs/theory/apashea_alignment.md` before changing factorized controls, policy priors, learning hooks, or pymdp/JAX alignment claims.
- Read `docs/experiment/design.md` before changing task design, configs, conditions, metrics, or sensitivity sweeps.
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
- Recommended experiment run: default + betrayal_stress in one batch with `--workers 12`; results go under `results/<batch_name>/<config_slug>/results.csv`; run `scripts/analysis/analyze.py` on those paths after.
- Default config (random partner) does not discriminate conditions; use betrayal_stress (agent-choice, scheduled switch) for hypothesis-relevant results.
- State inference (partner-type belief updating) is the analytical solution to VFE minimization (matrix-based Bayes with A and B), not iterative optimization.
- Benchmark runs use `scripts/benchmark/run_cvc.py` plus `docs/operations/benchmark.md` for backends, configs (for example `configs/benchmark_default.json` and `configs/benchmark_betrayal.json`), and Python 3.12 CvC worker notes.
- Remote VMs, sync, and merge flows for this project use `mango` (CLI at `~/Desktop/mango/`, available globally). See "Mango" section in `CLAUDE.md` for full command reference. Key: `mango run affect_aif --cloud` to launch, `mango stop affect_aif --remote` to stop, `mango cloud sync push/fetch affect_aif` to sync code/results (`sync push` is rsync and does not delete remote-only files under `results/`). Do not add orchestration or deployment scripts to this repo.

---

## Architecture

### Module Dependency Graph

```
affect_aif/
├── aif/                   # Generic active-inference primitives
│   ├── agent.py           # Lightweight Agent dataclass
│   ├── inference.py       # Generic Bayes / policy posterior helpers
│   ├── learning.py        # Dirichlet learning helpers
│   ├── policies.py        # Policy construction and sampling
│   ├── runtime.py         # Observation-sequence enumeration + runtime helpers
│   └── utils.py           # POMDP matrix/object-array helpers
├── tasks/
│   └── trust/             # Trust-task package
│       ├── agents/        # TrustGameAgent, AffectiveAgent, and lesions
│       ├── envs/          # Binary and graded trust-game environments
│       ├── models/        # Canonical TrustGameModel
│       ├── evaluation/    # Trust-task evaluation arena and baselines
│       ├── rollout.py     # Trust-specific planner / rollout helpers
│       ├── payoffs.py     # Trust-game payoff and action encoding helpers
│       ├── stance.py      # Stance dynamics
│       └── types.py       # Partner type metadata
├── experiments/
│   ├── trust/             # Depends on: tasks.trust
│   │   ├── config.py      # ExperimentConfig dataclass
│   │   ├── conditions.py  # Condition ID → name mapping
│   │   ├── runner.py      # ExperimentRunner (calibration + primary + sensitivity)
│   │   ├── batch.py       # BatchExperimentRunner (multi-config parallel)
│   │   ├── logger.py      # MetricLogger (per-round recording)
│   │   ├── progress.py    # ProgressReporter
│   │   └── factory.py     # Agent/model/environment factories
│   └── multifocal/        # M TrustGameAgents, turn-taking rounds (sub-project F)
│       ├── config.py      # Parses heterogeneous `agents: [...]` multi-focal JSON
│       ├── runner.py      # Multi-focal runtime
│       └── joint_resolution.py # Pairwise payoff obs from actions
├── analysis/              # Depends on: nothing (operates on DataFrames)
│   ├── metrics.py         # Summary statistics, betrayal analysis, movement
│   ├── statistics.py      # ANOVA, pairwise tests
│   ├── hypotheses.py      # Current Hesp-extension hypothesis helpers
│   ├── plots.py           # Matplotlib figure generation
│   └── visualization.py   # GIF generation
└── configs/               # External benchmark and CvC JSON configurations
```

### Experiment Conditions

| ID | Name | Agent | Horizon | Affect |
|----|------|-------|---------|--------|
| 1 | tau1_no_affect | TrustGameAgent | 1 | No |
| 2 | tau1_affect | AffectiveAgent | 1 | Yes |
| 3 | tau2_no_affect | TrustGameAgent | 2 | No |
| 4 | tau2_affect | AffectiveAgent | 2 | Yes |
| 5 | tau4_no_affect | TrustGameAgent | 4 | No |
| 6 | tau4_affect | AffectiveAgent | 4 | Yes |
| 7 | tau8_no_affect | TrustGameAgent | 8 | No |
| 8 | tau8_affect | AffectiveAgent | 8 | Yes |
| 9 | tau3_no_affect | TrustGameAgent | 3 | No |
| 10 | tau3_affect | AffectiveAgent | 3 | Yes |

Preset conditions live in `experiments.trust.conditions.PRESET_CONDITIONS`:
`lesioned`, `no_epistemic`, `alexithymia`, `borderline`, `depression`.

### Experiment Pipeline Flow

```
Config JSON → ExperimentRunner
    │
    ├── calibrate_mu()              # Derive μ from deep-planner EFE mass
    │   └── run_calibration_episode() × N
    │
    ├── run_all()                   # All conditions × all seeds
    │   └── run_replication()       # Single condition × single seed
    │       ├── _create_model()     # Canonical TrustGameModel
    │       ├── _create_env()       # TrustGameEnv or GradedTrustGameEnv
    │       ├── _create_agent()     # Condition → TrustGameAgent / affective variant
    │       └── _run_episode()      # Main loop: plan → step → observe
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

### Agent Lifecycle (per round)

```
agent.plan_and_act(active_partner)  # alias for choose_partner_and_action()
    ├── Enumerate policies (partner × action combinations)
    ├── Evaluate EFE via sophisticated inference (observation-branching)
    ├── [Affective] Weight by per-partner beta signal
    ├── Softmax → action probabilities → select action
    └── Return action

env.step(action)
    ├── Decode action → (partner_idx, agent_action)
    ├── Partner responds according to type strategy
    ├── Compute payoff
    └── Return observation dict

agent.observe_outcome(...)
    ├── Update beliefs about partner type (Bayesian posterior)
    ├── [Affective] Update beta for this partner (EMA of prediction error)
    └── Update internal state for next round
```

## Configuration System

Trust configs live in `experiments/trust/configs/`, multi-focal configs live in
`experiments/multifocal/configs/`, and external benchmark/CvC configs remain in
`configs/`. Key fields of `ExperimentConfig`:

### Game Structure
- `payoff_mode`: "binary" | "graded"
- `num_partners`: default 4
- `num_rounds`: default 200
- `assignment_mode`: "random" | "agent_choice"
- `scheduled_stance_switches`: list of stance-shift events for betrayal-style scenarios

### Agent Parameters
- `deep_horizon` / `shallow_horizon`: planning depth
- `lambda_smooth`: EMA smoothing for beta (0.6)
- `alpha_charge`: prediction error scaling (3.0)
- `sigma_0_sq`: prior variance (0.25)
- `initial_beta`: starting precision (0.5)
- `mu`: terminal value scale (derived from calibration if null)

### Run Parameters
- `conditions`: list of condition IDs
- `num_replications`: seeds per condition
- `calibration_episodes`: episodes for mu derivation
- `random_seed`: base seed

## Analysis Outputs

`scripts/analysis/analyze.py --results <csv> --output-dir <dir>` produces:

| File | Contents |
|------|----------|
| `final_round_summary.csv` | Per-seed cumulative payoffs and accuracy |
| `pairwise_payoff_tests.csv` | All condition pairs: t-stat, p-value, Cohen's d |
| `hypothesis_tests.json` | Structured hypothesis test results |
| `hypothesis_summary.csv` | One-row-per-hypothesis overview |
| `affective_movement_summary.csv` | Beta/terminal-signal range per seed |
| `statistics_summary.txt` | ANOVA + movement + betrayal summaries |
| `betrayal_*.csv` | (if switch events) Post-switch window analysis |
| `*.png` | Figures: payoff distributions, beta trajectories, etc. |

## Key Invariants

1. **Sophisticated inference**: Policy evaluation uses observation-branching, not mean-field rollout
2. **μ calibration**: Affective terminal values are scaled by empirically-derived μ, not hand-tuned
3. **Deterministic seeds**: `random_seed + replication_index` ensures reproducibility
4. **Condition equality**: C1=C3=C4 in same-horizon tasks confirms clean implementation
5. **Binary saturation**: EFE gaps ~10.83 in binary game → softmax is hard argmax → precision modulation inert
6. **Graded activation**: q_pi_entropy ~5.8 in graded game → precision modulation channel active

## Troubleshooting

### Tests fail after code change
```bash
python -m pytest tests/ -v --tb=short
python -m pytest tests/test_core.py -v  # isolate to module
```

### Experiment produces unexpected results
1. Run with `--verbose --verbosity-mode stage_stream` for per-round tracing
2. Check `calibration_summary` in `batch_metadata.json` — is mu reasonable?
3. Check current state in `docs/state/current/blockers.md`
4. Compare against current and historical status in `docs/results/`

### Analysis script errors
- Check CSV has expected columns: `condition`, `seed`, `round`, `payoff`, `run_mode`
- Filter to `run_mode == "primary"` before analysis
