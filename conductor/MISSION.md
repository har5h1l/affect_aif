# Mission

## Objective
Investigate gaps in current trust-game results and get our affect-augmented AIF model running in the CoGames (CvC) benchmark. The goal is to have everything needed for the full paper: clean trust-game results with the orthogonal augmentation narrative, plus CoGames benchmark results showing how well our AIF affect model scores in a real multi-agent environment.

## Guiding Principles
- Variational principles and docs/theory.md are the north star
- Trust-game results (Phases 1-7) are complete and should not be re-run unless a gap is found
- CoGames/CvC is the active frontier: the benchmark pipeline works but policies score 0 reward
- Ground all work in the active-inference framework; CvC policies should eventually reflect AIF principles, not just rule-based heuristics
- When exploring CvC, iterate quickly: try an approach, measure, adjust

## Completed Work (Phases 1-7)
- Phase 1: Primary results (orthogonal augmentation, H1-H5)
- Phase 2: Exploiter deep-dive (betrayal stress diagnostics)
- Phase 3: Theory tightening (graded game, cross-game synthesis)
- Phase 4: Variational beta (discrete Bayesian formulation validated)
- Phase 5: Clinical sensitivity (graded betrayal: alexithymia protective, borderline deterioration, depression self-corrects)
- Phase 6: Bayesian model comparison (C2 decisive winner under betrayal, log10 BF=3.0)
- Phase 7: Cross-game generalization (PD, Stag Hunt, Chicken — augmentation generalizes under volatility)

## Current Focus

### Track 1: Investigate Trust-Game Gaps
Review existing results for any gaps or weaknesses that would block paper submission:
1. Check that all claimed results reproduce (spot-check key configs)
2. Verify statistical claims match the data in results/
3. Identify any missing comparisons or analyses needed for the paper narrative
4. Check docs consistency: theory.md, results_tracking.md, experiment.md should agree

### Track 2: CoGames/CvC Benchmark — AIF Affect Model
The CvC pipeline is technically complete and runs end-to-end. The core goal is to adapt our affect-augmented active inference model to the CvC domain and benchmark it. Built-in cogames policies (StarterPolicy, role policies) exist only as comparison baselines — the point is testing *our* architecture.

**The central challenge:** Build a CvC policy that uses our AIF generative model + per-partner metacognitive precision tracking. This requires:

1. **A CvC generative model.** Map CvC observations (local grid view, agent states, resource locations) into a generative model the AIF agent can do inference over. Hidden states should include teammate reliability, resource locations, and role assignments.

2. **Affect mechanism integration.** The per-partner precision tracking (beta) should modulate how the agent weighs teammate observations — the same mechanism that works in the trust game, now applied to spatial cooperation. High-beta teammates get trusted for coordination; low-beta teammates get avoided.

3. **Navigation as planning.** The AIF agent should use expected free energy to select among the 5 CvC actions. The generative model needs to predict outcomes of movement actions (will I hit a wall? will I reach a resource?). This implicitly solves the navigation problem through the planning mechanism rather than through heuristic pathfinding.

4. **Practical bootstrapping.** To get non-zero scores while building the full AIF policy:
   - Try simpler/more open mission maps where basic navigation can succeed
   - Add wall-avoidance to existing policies so there's a working baseline to compare against
   - Use built-in cogames policies as comparison baselines only

**What NOT to do:**
- Do not treat rule-based policies as the goal — they are baselines
- Do not fake CvC results or map CvC actions into trust-game semantics
- Do not claim "transfer" based on the toy_gridworld adapter

### Track 3: Paper Preparation
- Ensure all results are saved and reproducible
- Check that benchmark configs match what's described in docs
- Verify test suite passes completely

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any experiment
- Small replications (3-5 seeds) before full runs (10+ seeds)
- Never delete result files
- Max 4 experiment workers
- CvC experiments run in Python 3.12 subprocess — use python3.12 binary
- STOP and describe findings if: results contradict expectations, a proposed direction is a massive shift from the variational-AIF paradigm, or Phase 8 (human data) is being considered

## Notes
Edit this file to change what the conductor does. Set status to PAUSED to stop.

## Status
ACTIVE — Track 2 (CoGames) is the priority. Track 1 (gap investigation) and Track 3 (paper prep) are secondary.
