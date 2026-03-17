# Mission

## Objective
Advance Phase 3 (theory tightening) of the affect_aif project. Test whether
per-partner metacognitive precision tracking provides orthogonal value beyond
explicit planning depth in volatile trust games.

## Current Phase
Phase 3: Theory tightening — clarify the mechanism and boundary conditions.

## Tasks
1. Run pytest to confirm codebase is clean
2. Read docs/long_term_plan.md and docs/results_tracking.md for current state
3. Identify the next incomplete task in Phase 3
4. Execute it: code changes -> tests -> small experiment (5 seeds) -> analysis
5. If small experiment looks good, run confirmation (50 seeds)
6. Update docs/results_tracking.md with findings
7. Commit at each checkpoint

## Resource Allocation
This project is LOWER PRIORITY. Use at most 2-3 workers for experiments.
The VM has 12 cores — the social_learning project gets 8, this project gets the rest.
Avoid running heavy parallel experiments simultaneously.

## Experiment Monitoring
Between experiment launches, CHECK partial results periodically:
- After launching an experiment, wait for a few seeds to complete
- Check if early results look reasonable (no NaN, no degenerate behavior)
- If something looks wrong, STOP the experiment immediately and report
- Update STATE.md with partial findings even before experiment finishes
- This prevents wasting hours on a bad configuration

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any experiment
- Small replications (5 seeds) before full runs (50-100 seeds)
- Never delete result files
- If results contradict the current hypothesis, STOP and describe findings
- Do not advance to Phase 4 without user approval

## Notes
Edit this file to change what the conductor does. Set status to PAUSED to stop.

## Status
ACTIVE
