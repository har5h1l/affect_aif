# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Overview

JAX-first multi-agent active inference simulations testing whether per-partner metacognitive precision tracking provides orthogonal value beyond explicit planning depth in a volatile trust game. Uses a phased research workflow where theory, code, experiments, and documentation co-evolve.

## Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `python -m pytest tests/ -v` |
| Run single test | `python -m pytest tests/test_core.py::test_name -v` |
| Run experiment | `python scripts/experiment/run.py --config experiments/trust/configs/<name>.json --output-dir results --batch-name <name>` |
| Analyze results | `python scripts/analysis/analyze.py --results <path>/results.csv --output-dir <path>/figures` |
| Preliminary check | `python scripts/experiment/preliminary.py --replications 5 --output results/preliminary.csv` |
| Generate GIFs | `python scripts/analysis/visualize.py --results <path>/results.csv --output-dir <path>/gifs` |
| Batch run (parallel) | `python scripts/experiment/run.py --config <a>.json --config <b>.json --workers 12 --output-dir results --batch-name main_run` |

## Source Layout

| Directory | Purpose |
|-----------|---------|
| `aif/` | Generic active-inference primitives and affect helpers |
| `tasks/trust/` | Trust-task agents, models, environments, rollout, payoffs, and evaluation arena |
| `experiments/trust/` | Trust experiment configs, conditions, logging, batch runner, and runner |
| `experiments/multifocal/` | Multi-focal trust experiment config and runtime |
| `analysis/` | Metrics, statistics, plotting, hypothesis tests |
| `benchmarks/core/` | Shared benchmark runner, config, metrics, and comparison helpers |
| `benchmarks/cvc/` | Experimental CvC backend, policies, packaging, and Observatory client |
| `configs/` | External benchmark and CvC JSON configurations |
| `scripts/` | CLI entry points (thin orchestrators) |
| `tests/` | Unit and integration tests |
| `docs/` | Theory, experiment design, implementation, results tracking, roadmap |
| `results/` | Local run outputs (gitignored except `.gitkeep`) |

## Documentation Map

| Question | Read first |
|----------|-----------|
| Theory or mechanism | `docs/theory/theory.md`, `docs/experiment/design.md` |
| POMDP model specification | `docs/theory/pomdp_spec.md` |
| Environment, implementation | `docs/design/implementation.md` |
| Setup or usage | `README.md` |
| Current results and hypothesis status | `docs/experiment/results.md` |
| Phase roadmap and what's next | `docs/future/roadmap.md` |
| Experimental design and conditions | `docs/experiment/design.md` |
| Partner stance redesign | `docs/design/partner_stance.md` |
| CLI reference | `docs/operations/cli.md` |
| Benchmark integration | `docs/operations/benchmark.md` |

## Working Rules

- Use the docs as the source of truth, but do not assume they are current. Verify against the code, then update both if they diverge.
- Every meaningful code change should leave the docs more accurate than before.
- Every behavior change should ship with tests or updated existing tests.
- Before refreshing result-tracking or interpretation docs from new experiment outputs, ask the user first; do not silently rewrite the current narrative after a run completes.

## Terminology Rules

- "per-partner metacognitive precision tracking" NOT "interoceptive social inference"
- "augmentation" NOT "compensation" or "depth replacement"
- beta update rule is variationally grounded via Hesp et al. — NOT a "heuristic" or "engineering approximation"
- Phase numbers: 3=theory tightening, 4=variational beta, 5=clinical sensitivity, 6=model comparison, 7=richer tasks, 8=human data
- Current phase: MVP complete (Phases 1-7, paper draft). Now in architectural tightening — addressing standard-AIF departures before next paper. See `docs/future/roadmap.md` for open decisions.

---

## Autonomous Research Protocol

When operating autonomously (all permissions granted), follow this protocol. The goal is to safely iterate the research loop: read state, plan, code, test, experiment, analyze, interpret, document, repeat.

### Phase-Aware Startup

Every session begins with orientation:

1. Read `docs/future/roadmap.md` to identify the current phase and its tasks
2. Read `docs/experiment/results.md` to understand where the last session left off
3. Read `docs/experiment/design.md` for experimental design context
4. Check git status for uncommitted work from a prior session
5. Run `python -m pytest tests/ -v` to confirm the codebase is clean

Only then decide what to do next.

### The Research Loop

```
orient -> plan -> code -> test -> experiment -> analyze -> interpret -> document -> commit -> loop
```

**Orient**: Read docs, results, and code to understand current state.

**Plan**: Identify the smallest next step that advances the current phase. Prefer small, testable increments over large changes. If the next step is ambiguous or involves a fundamental mutation (new environment, new model structure, reframing), STOP and ask the user.

**Code**: Make the changes. Keep them minimal and focused.

**Test**: Run `python -m pytest tests/ -v`. All tests must pass before proceeding. If tests fail, fix the code, don't skip the tests.

**Experiment**: Run experiments using the scripts. For exploration, use small replications (5-10 seeds). For confirmation, use full replications (50-100 seeds). Always save results to `results/`.

**Analyze**: Run `scripts/analysis/analyze.py` on the results. Read the output summary, hypothesis tests, and movement tables.

**Interpret**: Compare results against the hypothesis scorecard in `docs/experiment/results.md`. Does this change the story? If yes, flag it clearly.

**Document**: Update docs to reflect new findings. Follow the documentation map above.

**Commit**: Stage and commit at meaningful checkpoints with descriptive messages.

**Loop**: Go back to orient. If the phase is complete, update `docs/future/roadmap.md` and ask the user before advancing to the next phase.

### Subagent Strategy

Use subagents for parallelizable work:

- **Experiment runner** (background): Launch experiment runs as background tasks while doing other work
- **Analysis** (background): Analyze results from completed experiments in parallel
- **Code exploration** (Explore agent): When investigating unfamiliar parts of the codebase
- **Theory research** (general agent): When needing to reason about theoretical implications

When running multiple independent experiments, launch them as parallel background subagents.

### Safety Invariants

These are absolute rules that never bend:

1. **Tests before experiments**: Never run an experiment on code that doesn't pass all tests
2. **Small before large**: Always run small replications (5 seeds) before committing to full runs (100 seeds)
3. **Never delete results**: Results files are append-only history. Create new result files, don't overwrite old ones
4. **Never force-push**: All git operations are local-only unless the user explicitly asks to push
5. **Never silently rewrite narrative**: If experiment results change the interpretation, flag it to the user before updating docs
6. **Commit at checkpoints**: After any working code change + passing tests, commit. After any completed experiment + analysis, commit
7. **Preserve the hypothesis scorecard**: The scorecard in `docs/experiment/results.md` is the ground truth. Update it with evidence, not speculation
8. **Save results incrementally**: When running experiments, use partial saves (e.g., `_partial.csv`) during long runs so that a crash or OOM doesn't lose all progress. Scripts like `run_clinical_incremental.py` and `run_comparison.py` already do this — follow the same pattern for any new experiment scripts
9. **No orchestration infrastructure in this repo.** Syncing, deployment, conductor scripts, and cloud operations belong in the mango repo only. This repo contains only project code, configs, tests, and results.

### When to Stop and Ask

STOP and ask the user when:

- The next step requires a fundamental architecture change (new environment, new model, new agent type)
- Experiment results contradict the current phase's hypothesis in a way that might require reframing
- A phase appears complete and you'd need to advance to the next one
- Tests fail in a way that suggests a design problem, not a bug
- You're unsure which of several approaches to take
- The work would take more than ~30 minutes of experiment runtime

### Experiment Sizing Guide

| Purpose | Replications | Rounds | Use when |
|---------|-------------|--------|----------|
| Smoke test | 3-5 | 50 | Checking code works at all |
| Exploration | 10 | 100 | Testing a hypothesis direction |
| Confirmation | 50-100 | 200 | Producing publication-quality results |
| Clinical sensitivity | 100 | 200 | Parameter sweep across conditions |

### Configuration Templates

Trust experiments are configured via JSON in `experiments/trust/configs/`;
multi-focal experiments live in `experiments/multifocal/configs/`; external
benchmark and CvC configs remain under `configs/` until the benchmark package
split lands. Key parameters:

- `conditions`: list of condition IDs to run (see `docs/experiment/design.md` Section 3)
- `num_replications`: seeds per condition
- `num_rounds`: rounds per episode
- `payoff_mode`: "binary" or "graded"
- `assignment_mode`: "random" or "agent_choice"
- `scheduled_stance_switches`: supported betrayal/stance-shift scenarios

---

## Project State

`docs/state/` is the steering surface for humans and agents:

- `docs/state/current/mission.md` — active mission, scope, constraints, and stop conditions
- `docs/state/current/next_runs.md` — exact experiment queue and run commands
- `docs/state/current/blockers.md` — unresolved blockers and human decisions
- `docs/state/decisions/` — settled architecture and experiment decisions
- `docs/state/handoffs/` — dated handoff snapshots

Historical conductor state has been salvaged into `docs/state/` and
`docs/results/historical_findings.md`; it is not a live repo surface.

## Mango (Session & Cloud Management)

`mango` is the CLI for managing autonomous research sessions, both locally and on cloud VMs. It lives at `~/Desktop/mango/` and is available globally.

### Common Commands

```bash
# Session lifecycle
mango run affect_aif --cloud              # Launch autonomous session on server
mango run affect_aif --cloud --mode hybrid # Hybrid: compute on server, monitor locally
mango status --remote                      # Check running sessions on server
mango logs affect_aif --remote --lines 50  # Tail remote session logs
mango stop affect_aif --remote             # Stop remote session
mango attach affect_aif                    # SSH+tmux attach to cloud session

# Branch management
mango review affect_aif                    # Review latest session branch
mango merge affect_aif                     # Merge session branch to main

# Cloud operations
mango cloud sync push affect_aif           # Push code to server (rsync; does not delete remote-only paths under results/)
mango cloud sync fetch affect_aif          # Fetch results from server
mango cloud ssh                            # SSH into server
mango cloud push-infra                     # Sync mango itself to server

# Steering a running session
mango task affect_aif "try X" --now        # Send instruction to running session via INBOX.md
mango agent mission affect_aif             # View current mission
mango agent state affect_aif               # View current state
```

### Key Behaviors

- `mango run --cloud` creates a git worktree on the server, checks out the current branch, and launches a remote agent session
- Sessions continue on the **same branch** they were launched on — push your branch to origin before launching
- When a session stops (even via SIGKILL), mango **automatically removes the worktree**
- Server's local master is NOT auto-updated by `mango run --cloud`. To sync: `mango cloud sync push affect_aif` or manually pull on server
- Session logs are managed by Mango on the server
- Results from experiments land in `results/` within the worktree — use `mango cloud sync fetch` to pull them back
