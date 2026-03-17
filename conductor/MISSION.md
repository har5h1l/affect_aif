# Mission

## Objective
Begin Phase 4 (Variational Beta Extension). Formalize beta as a discrete hidden
state within the generative model, extending the current continuous EMA update.

## Current Phase
Phase 4: Variational Beta Extension

## Tasks
1. Run pytest to confirm codebase is clean
2. Read docs/long_term_plan.md and docs/results_tracking.md for current state
3. Read docs/theory.md for the current beta formulation
4. Design the discrete beta hidden state: define state levels, likelihood P(e|beta), transition dynamics P(beta_t|beta_{t-1})
5. Show formal correspondence between current EMA update and discrete hidden-state posterior
6. Implement the discrete beta formulation alongside the existing continuous one
7. Run small experiments (5 seeds) comparing continuous vs discrete beta
8. If results look good, run confirmation (50 seeds)
9. Update docs with findings
10. Commit at each checkpoint

## Resource Allocation
This project uses 1 worker for experiments. Be conservative with compute.

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any experiment
- Small replications (5 seeds) before full runs (50-100 seeds)
- Never delete result files
- Save results incrementally (partial CSVs during long runs)

## Notes
Edit this file to change what the conductor does. Set status to PAUSED to stop.

## Status
ACTIVE
