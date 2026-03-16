# AGENTS.md — System Documentation

This document provides comprehensive system documentation for AI agents operating on the affect_aif codebase. It covers architecture, module interfaces, experiment pipeline, and operational procedures.

## Documentation First

- Read `docs/theory.md` before changing computational claims, affect dynamics, terminal values, or the interpretation of results.
- Read `docs/experiment.md` before changing task design, configs, conditions, metrics, or sensitivity sweeps.
- Read `docs/implementation.md` before changing environment semantics, switching logic, or analysis helpers.
- Read `README.md` before changing setup, entry points, or repo layout.

## Required Follow-Through

- If code behavior changes, update the relevant docs in the same change.
- If experiment assumptions change, update both theory-facing and experiment-facing docs.
- If configs or scripts change, update the README or implementation notes so the runnable workflow stays accurate.
- If tests reveal a theory/code mismatch, fix both the implementation and the docs before closing the task.

## Learned

- Use `.venv` in project root; venv should auto-activate when in this folder (direnv with `.envrc`).
- Recommended experiment run: default + betrayal_stress in one batch with `--workers 12`; results go under `results/<batch_name>/<config_slug>/results.csv`; run `run_analysis.py` on those paths after.
- Default config (random partner) does not discriminate conditions; use betrayal_stress (agent-choice, scheduled switch) for hypothesis-relevant results.
- Before updating result-interpretation docs from new experiment outputs, ask the user first.
- State inference (partner-type belief updating) is the analytical solution to VFE minimization (matrix-based Bayes with A and B), not iterative optimization.

---

## Architecture

### Module Dependency Graph

```
affect_aif/
├── core/                  # No internal dependencies
│   ├── control.py         # Policy evaluation, EFE, sophisticated inference
│   ├── learning.py        # Belief update mechanics
│   └── utils.py           # POMDP matrix construction helpers
├── generative_model/      # Depends on: core
│   ├── model.py           # TrustGameModel, GradedTrustGameModel
│   ├── payoffs.py         # Payoff matrix construction
│   └── partner_types.py   # Partner strategy definitions
├── agent/                 # Depends on: core, generative_model
│   ├── base_agent.py      # BaseAgent — plan_and_act / observe_outcome
│   ├── affective_agent.py # AffectiveAgent — per-partner beta tracking
│   ├── lesioned_agent.py  # LesionedAgent — beta tracked but decoupled
│   └── reward_avg_agent.py # RewardAvgAgent — reward-based terminal values
├── environment/           # Depends on: experiment (config only)
│   ├── trust_game.py      # Binary trust game (2 actions × 4 partners)
│   └── graded_trust_game.py # Graded investment (6 levels × 4 partners)
├── experiment/            # Depends on: agent, environment, generative_model
│   ├── config.py          # ExperimentConfig dataclass
│   ├── conditions.py      # Condition ID → name mapping
│   ├── runner.py          # ExperimentRunner (calibration + primary + sensitivity)
│   ├── batch.py           # BatchExperimentRunner (multi-config parallel)
│   ├── logger.py          # MetricLogger (per-round recording)
│   └── progress.py        # ProgressReporter
├── analysis/              # Depends on: nothing (operates on DataFrames)
│   ├── metrics.py         # Summary statistics, betrayal analysis, movement
│   ├── statistics.py      # ANOVA, pairwise tests
│   ├── hypotheses.py      # H1-H5 hypothesis test battery
│   ├── plots.py           # Matplotlib figure generation
│   └── visualization.py   # GIF generation
└── configs/               # JSON experiment configurations
```

### Experiment Conditions

| ID | Name | Agent | Horizon | Affect |
|----|------|-------|---------|--------|
| 1 | deep_no_affect | BaseAgent | deep (8) | No |
| 2 | affective_shallow | AffectiveAgent | shallow (2) | Yes |
| 3 | lesioned | LesionedAgent | shallow (2) | Tracked but decoupled |
| 4 | shallow_no_affect | BaseAgent | shallow (2) | No |
| 5 | reward_avg | RewardAvgAgent | shallow (2) | Reward-based |
| 6 | intermediate_3 | BaseAgent | 3 | No |
| 7 | intermediate_4 | BaseAgent | 4 | No |
| 8 | deep_affective | AffectiveAgent | deep (8) | Yes |
| 9 | alexithymia | AffectiveAgent | shallow (2) | Low responsiveness |
| 10 | borderline | AffectiveAgent | shallow (2) | High volatility |
| 11 | depression | AffectiveAgent | shallow (2) | Low initial beta |

### Experiment Pipeline Flow

```
Config JSON → ExperimentRunner
    │
    ├── calibrate_mu()              # Derive μ from deep-planner EFE mass
    │   └── run_calibration_episode() × N
    │
    ├── run_all()                   # All conditions × all seeds
    │   └── run_replication()       # Single condition × single seed
    │       ├── _create_model()     # TrustGameModel or GradedTrustGameModel
    │       ├── _create_env()       # TrustGameEnv or GradedTrustGameEnv
    │       ├── _create_agent()     # Condition → agent type
    │       └── _run_episode()      # Main loop: plan → step → observe
    │
    └── save_results()              # DataFrame → CSV
         │
         ▼
    run_analysis.py                 # Post-hoc analysis
    ├── final_round_summary()
    ├── cumulative_payoff_anova()
    ├── pairwise_payoff_tests()
    ├── run_all_hypothesis_tests()
    ├── affective_movement_summary()
    └── save_all_figures()
```

### Agent Lifecycle (per round)

```
agent.plan_and_act(active_partner)
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

Configs are JSON files in `affect_aif/configs/`. Key fields of `ExperimentConfig`:

### Game Structure
- `payoff_mode`: "binary" | "graded"
- `num_partners`: default 4
- `num_rounds`: default 200
- `assignment_mode`: "random" | "agent_choice"
- `scheduled_type_switches`: list of `{partner, from_type, to_type, at_round}`

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

`scripts/run_analysis.py --results <csv> --output-dir <dir>` produces:

| File | Contents |
|------|----------|
| `final_round_summary.csv` | Per-seed cumulative payoffs and accuracy |
| `pairwise_payoff_tests.csv` | All condition pairs: t-stat, p-value, Cohen's d |
| `hypothesis_tests.json` | H1-H5 structured test results |
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
3. Compare against known baselines in `docs/results_tracking.md`

### Analysis script errors
- Check CSV has expected columns: `condition`, `seed`, `round`, `payoff`, `run_mode`
- Filter to `run_mode == "primary"` before analysis
