# Mission

## Objective
Implement Phase 4 (variational beta extension) of the affect_aif project. Formalize
beta as a discrete hidden state within the generative model, extending the current
continuous EMA update to a full Bayesian inference scheme.

## Current Phase
Phase 4: Variational Beta Extension

## Tasks
1. Run pytest to confirm codebase is clean
2. Read docs/long_term_plan.md and docs/theory.md for the current beta formulation
3. Discretize beta into a set of hidden-state levels with likelihood P(ε|β) and transition dynamics P(β_t|β_{t-1})
4. Implement the discrete beta inference alongside the existing EMA update
5. Show formal correspondence between the continuous EMA update and the discrete hidden-state posterior
6. Run small experiment (5 seeds) comparing continuous vs discrete beta in default condition
7. If results look good, run confirmation (50 seeds) across default and betrayal conditions
8. Quantify behavioral divergence between continuous and discrete formulations
9. Update docs/results_tracking.md and docs/theory.md with findings
10. Commit at each checkpoint

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any experiment
- Small replications (5 seeds) before full runs (50-100 seeds)
- Never delete result files
- If results contradict expectations, STOP and describe findings
- Max 4 experiment workers (HARD LIMIT)

## Notes
Edit this file to change what the conductor does. Set status to PAUSED to stop.
Phase 3 is complete — all theory tightening done. See docs/long_term_plan.md.

## Status
ACTIVE
