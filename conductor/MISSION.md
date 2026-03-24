# Mission

## Objective
Prepare the affect-augmented AIF paper for submission by closing theory gaps, getting non-zero CvC benchmark scores, and ensuring all claims are backed by reproducible results. Four tracks: (1) paper theory gaps, (2) CvC benchmark with actual Observatory submission, (3) paper preparation, (4) research-brain improvements (document only).

## Guiding Principles
- Variational principles and docs/theory.md are the north star
- Trust-game results (Phases 1-7) are complete and should not be re-run unless a gap is found
- Navigation is engineering, not theory — solve it pragmatically so the AIF mechanism can be evaluated
- Ground all work in the active-inference framework; CvC policies should eventually reflect AIF principles, not just rule-based heuristics
- When exploring CvC, iterate quickly: try an approach, measure, adjust
- The CvC work targets ACTUAL benchmark submission (Observatory beta-cvc season, compat 0.19), not just a local demo

## Completed Work (Phases 1-7)
- Phase 1: Primary results (orthogonal augmentation, H1-H5)
- Phase 2: Exploiter deep-dive (betrayal stress diagnostics)
- Phase 3: Theory tightening (graded game, cross-game synthesis)
- Phase 4: Variational beta (discrete Bayesian formulation validated)
- Phase 5: Clinical sensitivity (graded betrayal: alexithymia protective, borderline deterioration, depression self-corrects)
- Phase 6: Bayesian model comparison (C2 decisive winner under betrayal, log10 BF=3.0)
- Phase 7: Cross-game generalization (PD, Stag Hunt, Chicken — augmentation generalizes under volatility)

## Current Focus

### Track 1: Paper Theory Gaps (Priority: HIGH)

Specific gaps in theory, related work, and empirical story that must be addressed before submission.

#### 1.1 Inside-Out Framing: Position in Literature
Add a related-work paragraph triangulating three approaches:
- **Yoshida (2024)** — empathic coupling = outside-in (model partner's internal states)
- **Pitliya et al. (2025)** — ToM = cognitive model of other's inference
- **This work** — inside-out metacognitive monitoring of one's own social inference channel

This triple dissociation (outside-in empathy / cognitive ToM / inside-out precision monitoring) is the cleanest way to position the contribution. Action: add/update a Discussion subsection in `docs/paper/main.tex` and update `docs/theory.md` Section 4 accordingly.

#### 1.2 Precision Modulation Pathway: Test or Cut
The paper mentions per-partner policy precision modulation (gamma_k = f(beta_k)) as an alternative to terminal-value weighting — but it's implemented and never tested in production experiments. Described-but-untested mechanisms weaken the contribution.

**STOP and present options to the user:**
- **Option A: Run it.** The graded game (q_pi entropy ~5.8) is exactly where precision modulation should matter because softmax isn't saturated. Run C2 with gamma-modulation in the graded betrayal environment (50-100 seeds). If it works, add to results. If not, report as a clean negative result.
- **Option B: Cut it.** Remove all mention from the paper. Keep the code, don't claim it. Move to future_work.md explicitly.

Do NOT run experiments or cut content without user approval.

#### 1.3 Neuro-Architectural Argument for vmPFC as Beta
The vmPFC lesion analogy (C3 = C4 reproducing Damasio's somatic marker deficit) is in the paper but lacks neural grounding. Two papers provide the missing argument:
- **Bancee et al. (2026)** — vmPFC encodes emotion concepts in geometric form (valence/arousal maps)
- **Baram et al. (2026)** — OFC/vmPFC maintains persistent schema representations as semi-separable manifolds

Together with Damasio: vmPFC is where precision over social models (schemas) intersects with affective state (valence geometry). This makes vmPFC the natural biological locus of beta. Action: add a Discussion paragraph in `docs/paper/main.tex` connecting Bancee + Baram + Damasio to the beta construct.

#### 1.4 BMR Trigger Framing (Theory Only — No Implementation)
Strengthen the Future Work paragraph on BMR with neuroscience grounding:
- **Behrens (2025)** — hippocampal ripples mediate structural (not parametric) belief updates
- **Mishchanchuk (2024)** — causal dissociation of hidden-state inference from parameter updating
- **Neural surprise somatosensory paper** — early ~70ms signal = model inadequacy, late ~140ms = parameter update

These support the argument: persistent low beta is computationally analogous to the "model inadequacy" signal — evidence that the structure is wrong, not just the parameters. Do NOT implement BMR. Preserve the conflation warning in `docs/experiment.md` Section 8.2.

#### 1.5 Between-Clinical Differentiation Framing
Phase 5 showed d > 2.1 effects vs C4 but between-profile payoff differences are small (10.324-10.353 range). The paper needs to lead with the qualitative story: (a) alexithymia protective / borderline deteriorating / depression self-correcting as qualitatively distinct computational impairments; (b) the structural distinction (beta_0 is correctable by inference, alpha and lambda create persistent perturbations); (c) acknowledge between-profile quantitative differentiation as a limitation/future-work item.

### Track 2: CoGames/CvC Benchmark (Priority: HIGH)

**Goal:** Get a submission-ready policy onto the actual CvC benchmark (beta-cvc Observatory season, compat_version 0.19). The policy needs to score non-zero reward and be packaged for submission via `cvc_packaging.py`.

**The navigation problem is the fundamental blocker.** All policies (including cogames built-in) score 0 because ~80% of moves hit walls.

#### 2.1 Solve Navigation First
Implement an A* pathfinding layer. The CvC action space is only 5 actions (noop + 4 cardinal). The observation includes a local grid view.

1. Parse the local grid observation to build a walkability map
2. Use A* (or BFS — the grid is small) to find a path to the target
3. Return the next cardinal action along the path
4. Fall back to random valid moves if no path exists

Implementation: `PathfindingMixin` or utility in `affect_aif/benchmark/cvc_navigation.py`. Wire into `TeammateReliabilityPolicy` first. Smoke-test: 3 seeds, 1000 steps — target: >0 aligned junctions.

Start by examining CvC observation format in `affect_aif/benchmark/cvc_policy.py` and cogames docs.

#### 2.2 Build a Working Baseline Policy
Once navigation works, build `ScoringLoopPolicy` — a simple state-machine that completes the CvC scoring loop:
1. Get gear (navigate to gear location)
2. Mine ore (navigate to ore, proximity-interact)
3. Deposit at base (navigate to base)
4. Collect hearts (proximity pickup)
5. Align junction (navigate to junction)

Test with 10 seeds, confirm non-zero reward.

#### 2.3 Add Affect Mechanism to CvC Policy
Once baseline scores non-zero, layer in per-partner precision tracking as `AffectCvCPolicy`:
1. **Teammate observation model:** For each teammate k, predict position/behavior based on role and recent trajectory
2. **Beta_k update:** Compare predicted vs actual teammate behavior, update via EMA rule (or discrete Bayesian)
3. **Policy modulation:** High-beta_k teammates -> prioritize coordination. Low-beta_k -> work independently

Uses same `PathfindingMixin` as baseline. Test each layer incrementally: (a) teammate tracking alone, (b) beta updates, (c) policy modulation. Compare against `ScoringLoopPolicy`.

#### 2.4 Benchmark and Package for Submission
1. Full benchmark: `AffectCvCPolicy` vs `ScoringLoopPolicy` vs built-in cogames policies, 10,000 steps, machina_1
2. Analyze with `scripts/analyze_benchmark.py`
3. Package via `affect_aif/benchmark/cvc_packaging.py` for Observatory submission
4. Validate compat_version matches season (0.19)

The paper claim is "the architecture transfers to a spatial multi-agent domain" — even modest performance gains from the affect mechanism over the baseline are meaningful.

#### 2.5 Try Simpler Missions (Parallel Track)
In parallel with 2.1-2.4, check if simpler/more-open CvC missions exist where navigation is easier. Provides a stepping stone if machina_1 proves too hard for rule-based pathfinding.

### Track 3: Paper Preparation (Priority: MEDIUM — depends on Tracks 1-2)

#### 3.1 Docs Consistency Check
Verify that `docs/theory.md`, `docs/results_tracking.md`, `docs/experiment.md`, and `docs/paper/main.tex` all agree on: condition numbering/descriptions, key numbers (effect sizes, p-values, BFs), hypothesis status, phase descriptions and completion status. Flag any inconsistencies.

#### 3.2 Results Reproducibility Spot-Check
Spot-check 2-3 key configs (5 seeds each):
- `default.json` -> C2 = 575.06
- `betrayal_stress.json` -> C2 = 481.88
- `horizon_sweep.json` -> flat non-affect depth curve

Confirm numbers are in the right ballpark (patterns should hold, exact values may differ with different seeds).

#### 3.3 Add CvC Results to Paper
Once Track 2 produces results, add a section to `docs/paper/main.tex`:
- Describe CvC environment and why it tests generality
- Report benchmark results (reward, aligned junctions, hearts)
- Show beta dynamics over teammates (if affect mechanism is wired)
- Frame as "architectural generality" demonstration

#### 3.4 Final LaTeX Polish
- Ensure all references are in the bibliography
- Check figure/table numbering and equation references
- Add Yoshida, Sennesh/Ramstead, Bancee, Baram to bibliography
- Check for TODO/FIXME markers in the LaTeX

### Track 4: Research-Brain Improvements (Priority: LOW — background)

Do NOT implement these. Document identified issues in STATE.md only. The user will handle research-brain changes separately.

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any experiment
- Small replications (3-5 seeds) before full runs (10+ seeds)
- Never delete result files
- Max 4 experiment workers
- CvC experiments run in Python 3.12 subprocess — use python3.12 binary
- STOP and present options for section 1.2 (precision modulation: test or cut) before proceeding
- STOP and describe findings if: results contradict expectations, a proposed direction is a massive shift from the variational-AIF paradigm, or Phase 8 (human data) is being considered

## Notes
Edit this file to change what the conductor does. Set status to PAUSED to stop.

## Status
ACTIVE — Track 1 (paper theory gaps) and Track 2 (CvC benchmark) are co-priority. Track 3 depends on Tracks 1-2. Track 4 is document-only.
