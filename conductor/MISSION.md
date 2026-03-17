# Mission

## Objective
Continue research through Phases 5–8. Run experiments, update docs, and commit at checkpoints. Stop only when a phase requires a big user decision (new architecture, paper draft, human data, or fundamental reframing).

## Current Phase
Phase 6: Bayesian Model Comparison (Phase 5 is blocked by Phase 7; Phase 7 is a stop point)

## Tasks

### Phase 6 (do now)
1. Run pytest to confirm codebase is clean
2. Read docs/long_term_plan.md and analysis/hypotheses.py for current frequentist pipeline
3. Add likelihood computation for model variants (with/without affect, different depths)
4. Implement BMR or bridge sampling for marginal likelihood / Bayes factors
5. Run model comparison on existing results (default, betrayal_stress)
6. Document findings in docs/results_tracking.md and docs/theory.md
7. Commit at each checkpoint

### Phase 5 (after Phase 7)
- Blocked: current trust game has softmax saturation; clinical sensitivity needs richer tasks first

### Phase 7 (stop point)
- Do not start Phase 7 autonomously. It requires:
  - New environments (public goods, ultimatum) = fundamental architecture
  - Entry condition: single-agent paper in draft or published
- When Phase 6 is complete, STOP and report. User decides whether to proceed to Phase 7.

### Phase 8 (stop point)
- Human data: always requires user. Do not start Phase 8 autonomously.

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any experiment
- Small replications (5 seeds) before full runs (50–100 seeds)
- Never delete result files
- If results contradict expectations, STOP and describe findings
- Max 4 experiment workers (HARD LIMIT)
- STOP when: Phase 6 complete (user decides Phase 7 vs 6 extension), Phase 7 start (user decision), Phase 8 (user decision), or results demand reframing

## Notes
Edit this file to change what the conductor does. Set status to PAUSED to stop.
Phase 4 complete. Phase 6 can proceed autonomously. Phases 7–8 need user decisions.

## Status
RUNNING — Phase 6 in progress. Autonomously continue until Phase 6 complete, then STOP for user decision on Phase 7.
