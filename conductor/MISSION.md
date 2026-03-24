# Mission

## Objective
Continue research through Phases 5–8. Run experiments, update docs, and commit at checkpoints. Make decisions autonomously. Ground all work in variational principles (VFE minimization, generative models, belief updating, precision dynamics) and the project's theoretical framework (per-partner metacognitive precision, orthogonal augmentation, Hesp et al. grounding). New environments or tasks that fit this scope—stretching or pivoting within the framework—are fine to pursue. Stop only for a massive shift: human data collection, or a direction that fundamentally departs from the current variational active-inference paradigm.

## Guiding Principles
- Variational principles and docs/theory.md are the north star
- Stretch scope (richer games, new partner types, new inference schemes) as long as it stays within the variational-AIF framework
- Pivot within the paradigm when results suggest it; do not stop for normal extensions

## Current Phase
Phase 6: Bayesian Model Comparison (Phase 5 clinical sensitivity can proceed autonomously; Phase 7 can proceed if environments fit principles)

## Tasks

### Phase 6 (do now)
1. Run pytest to confirm codebase is clean
2. Read docs/long_term_plan.md and analysis/hypotheses.py for current frequentist pipeline
3. Add likelihood computation for model variants (with/without affect, different depths)
4. Implement BMR or bridge sampling for marginal likelihood / Bayes factors
5. Run model comparison on existing results (default, betrayal_stress)
6. Document findings in docs/results_tracking.md and docs/theory.md
7. Commit at each checkpoint

### Phase 5 (clinical sensitivity)
- proceed autonomously with clinical-sensitivity sweeps on the graded/SH variants (or any richer environment that fits variational-aif principles); adapt away from binary softmax saturation if it makes bayes-factor discrimination uninformative

### Phase 7 (richer environments)
- Proceed autonomously if new environments (public goods, ultimatum, etc.) fit variational principles and extend the current generative-model framework. No stop unless the change is a massive architectural shift.

### Phase 8 (stop point)
- Human data collection always requires user. Do not start Phase 8 autonomously. STOP.

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any experiment
- Small replications (5 seeds) before full runs (50–100 seeds)
- Never delete result files
- If results contradict expectations, STOP and describe findings
- Max 4 experiment workers (HARD LIMIT)
- STOP only when: human data collection (Phase 8), or a proposed direction is a massive shift away from the variational-AIF paradigm

## Notes
Edit this file to change what the conductor does. Set status to PAUSED to stop.
Phase 4 complete. Agent proceeds through Phase 5–7 autonomously as long as work stays within scope. Only Phase 8 and massive shifts require user decision.

## Status
PAUSED — Phases 5–7 complete. Awaiting user decision on Phase 8 (human data collection).
