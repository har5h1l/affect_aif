# Mission: Post-Restructure Analysis and Reframe

## Objective

Analyze post-restructure experimental results, reframe hypotheses based on new structural findings (G compression, depth redundancy), clean up outdated results, rerun incomplete experiments, and update all documentation.

**Do NOT touch the paper (docs/paper/). Do NOT touch CvC code. Do NOT implement pymdp.**

---

## Critical Context

The codebase was recently restructured to use action-dependent partner stance dynamics (B[1] is action-dependent — cooperating vs defecting produces different stance transition matrices). Core experiments (H1 factorial, H2 lesion, H4 betrayal) were rerun on the new architecture. Analysis of these results reveals:

1. **G compression is structural**: With 256 policies at tau=8, G range grows only sublinearly (2.0 → 9.6 for tau=1 → 8) while policy count grows as 2^tau. Policy entropy explodes: 0.37 (tau=1) → 3.90 (tau=8). Matching tau=1 entropy would require gamma≈41 at tau=8 — exponential scaling. Fixed gamma=1.0 with full policy enumeration IS standard AIF (Parr, Pezzulo & Friston 2022). Do NOT implement gamma scaling.

2. **Depth inversion confirmed**: Myopic planning (tau=1) outperforms deep planning (tau=8) by ~37 points (d=0.82, p<1e-8). This is a structural property of the generative model, not a bug or calibration failure.

3. **Affect signal weakened in pooled analysis**: Pooling all depths gives d=0.15-0.26, not statistically significant. This is expected — affect modulates a softmax channel that is already saturated at deep horizons. The affect effect should be substantial at tau=1,2 where the softmax still discriminates.

4. **Decision 1 (B matrix) is RESOLVED**: Action-dependent stance is implemented and confirmed. Planning depth is structurally redundant — not an artifact requiring a fix.

5. **Lesion dissociation**: d=0.26, p=.07 pooled. Needs targeted re-analysis at tau=1,2.

---

## Phase 1: Cleanup

**1.1 Delete outdated results**

These are pre-restructure and/or architecturally invalid:
- `results/clinical_run/` — pre-restructure clinical data (20 reps, old architecture). Delete entirely.
- `results/h5_selection/h5_partner_selection/results_partial.csv` — incomplete H5 run (32 seeds, condition 5 only). Delete.

**1.2 Update docs/future/roadmap.md**

- Decision 1 (B matrix): Mark **RESOLVED** — action-dependent stance implemented, depth redundancy confirmed structural, paper should document this as a domain finding
- Decision 2 (pymdp): **REMOVED** — not pursuing any pymdp path
- Decision 3 (multiplicative precision): Keep open, does not affect current findings
- Decision 4 (AIF partners): Keep as future direction
- Track 2 (CvC/CoGames): Move to "Future Directions" — not an active track
- Update "Current Direction" section: "Post-restructure reframe — action-dependent stance results in hand, reframing hypotheses and completing remaining experiments"

**1.3 Run all tests**

```bash
python -m pytest tests/ -v
```
All must pass before proceeding.

---

## Phase 2: Hypothesis Reframe in Docs

Update `docs/experiment/design.md` Section 1 (Overview) and hypothesis framing. Update `docs/experiment/results.md` Status Note.

**New hypothesis framing (replace old H1-H5 framing throughout):**

**H1 — G Compression / Depth Redundancy (structural finding):**
In sophisticated active inference with action-dependent stance dynamics, planning depth beyond tau=2 is computationally redundant due to G compression. Policy entropy grows from 0.37 (tau=1) to 3.90 (tau=8) while discriminating signal (G range) grows only sublinearly. With full policy enumeration and standard fixed gamma, deeper planning cannot discriminate among its policies. This is a structural property of binary-action trust games, not a calibration failure.

**H2 — Affect as Orthogonal Augmentation (core claim):**
Per-partner affective precision tracking provides orthogonal augmentation — payoff gains independent of planning depth. Effect is most visible at calibrated horizons (tau=1,2) where the softmax channel is still actively discriminating. Previous finding that affect adds ~+46 points at any depth should be re-examined at calibrated depths specifically.

**H3 — Lesion Dissociation (Damasio pattern):**
Affective decoupling preserves inference accuracy while impairing payoff. The computational Damasio dissociation should be clearest at tau=1,2 where the affect signal operates in a discriminating regime.

**H4 — Betrayal Recovery:**
Affect-augmented agents recover faster after partner stance switches to hostile. Test focused at tau=2 (calibrated depth).

**H5 — Partner Selection:**
Beta-based precision guides adaptive partner selection — agents preferentially interact with high-beta (well-predicted) partners. Test at tau=2.

**Clinical:**
Phenotype-specific precision impairments are visible in volatile, high-miscoordination environments. Alexithymia protective, borderline impaired, depression self-correcting — now tested on new action-dependent architecture.

---

## Phase 3: Targeted Re-Analysis of Existing Data

Do this before running new experiments — may change what experiments are needed.

**3.1 H1 re-analysis: conditions 1-4 only (tau=1,2)**

From `results/h1_factorial/h1_depth_affect_factorial/results.csv`:
- Filter to condition_name in ["tau1_no_affect", "tau1_affect", "tau2_no_affect", "tau2_affect"] (conditions 1-4)
- Compute: affect vs no-affect effect size (Cohen's d) at each of tau=1 and tau=2
- Key question: is d(affect) substantially larger than pooled d=0.15? Expect d>0.4 at tau=1.

**3.2 H2 re-analysis: lesion dissociation at available conditions**

From `results/h2_lesion/h2_lesion_dissociation/results.csv`:
- Conditions available: [5,6] + "lesioned" + "no_epistemic" presets (all at tau=4)
- Check: inference accuracy (inferred_joint_correct) for lesioned vs condition 5 (no_affect baseline)
- Check: payoff for lesioned vs condition 6 (affect)
- Note: this is at tau=4 which is already partially saturated. Flag whether effect is present but weaker than expected.

**3.3 H4 re-analysis: betrayal window**

From `results/h4_betrayal/h4_betrayal_recovery/results.csv`:
- Conditions available: [5,6] + presets, agent_choice assignment
- Analyze: payoff in rounds 30-60 (post-betrayal window) for affect vs no-affect
- Compute effect size in recovery window specifically

Save re-analysis outputs to:
- `results/reanalysis/h1_shallow_reanalysis.txt`
- `results/reanalysis/h2_lesion_reanalysis.txt`
- `results/reanalysis/h4_betrayal_window_reanalysis.txt`

---

## Phase 4: New Experiment Runs

Run in this order (each requires smoke test first):

**4.1 Shallow Depth Confirmation** (new config — create first)

Create `configs/shallow_affect_confirm.json`:
```json
{
  "experiment_name": "shallow_affect_confirm",
  "num_partners": 4,
  "num_rounds": 200,
  "p_switch": 0.05,
  "assignment_mode": "random",
  "gamma": 1.0,
  "lr": 0.1,
  "action_sampling": "marginal",
  "deep_horizon": 8,
  "shallow_horizon": 2,
  "max_policies": 4096,
  "alpha_charge": 3.0,
  "sigma_0_sq": 0.25,
  "initial_beta": 1.0,
  "beta_persistence": 0.8,
  "beta_num_levels": 5,
  "lesion_mode": "decouple",
  "num_replications": 100,
  "random_seed": 42,
  "conditions": [1, 2, 3, 4],
  "presets": ["lesioned"],
  "partner_types": ["cooperator", "reciprocator", "exploiter", "random"],
  "run_sensitivity": false
}
```
Purpose: Confirm affect effect size at tau=1,2 where softmax discriminates. Also include lesioned preset to get lesion dissociation at shallow depth.

Run:
```bash
python -m pytest tests/ -v  # must pass
# Smoke test (5 seeds):
python scripts/run_experiment.py --config configs/shallow_affect_confirm.json --output-dir results --batch-name shallow_confirm_smoke --override num_replications=5
# Full run:
python scripts/run_experiment.py --config configs/shallow_affect_confirm.json --output-dir results --batch-name shallow_confirm
```

**4.2 H5 Partner Selection (fresh run)**

Config: `configs/h5_partner_selection.json` already exists.
Run:
```bash
python scripts/run_experiment.py --config configs/h5_partner_selection.json --output-dir results --batch-name h5_selection
```

**4.3 Clinical Betrayal (new architecture)**

Config: `configs/clinical_betrayal.json` already exists.
Run:
```bash
python scripts/run_experiment.py --config configs/clinical_betrayal.json --output-dir results --batch-name clinical_betrayal
```

**4.4 Clinical Phenotypes (new architecture)**

Config: `configs/clinical_phenotypes.json` already exists.
Run:
```bash
python scripts/run_experiment.py --config configs/clinical_phenotypes.json --output-dir results --batch-name clinical_phenotypes
```

Run 4.3 and 4.4 in parallel if system resources allow.

---

## Phase 5: Analysis and Documentation

After each experiment completes, run analysis immediately:

```bash
python scripts/run_analysis.py --results results/<batch_name>/<experiment_name>/results.csv --output-dir results/<batch_name>/<experiment_name>/figures
```

Update `docs/experiment/results.md` hypothesis scorecard after each analysis:
- Report: effect size (Cohen's d), p-value, direction
- Flag any finding that contradicts the reframed hypothesis before updating narrative
- Mark each hypothesis as: SUPPORTED / WEAKLY SUPPORTED / NOT SUPPORTED / NEEDS MORE DATA

---

## Commit Checkpoints

Commit after:
1. Cleanup complete (Phase 1) + tests pass
2. Docs reframe complete (Phase 2)
3. Each re-analysis output saved (Phase 3)
4. Each new experiment + analysis complete (Phase 4-5)

Use descriptive commit messages, e.g.:
- "Cleanup: delete pre-restructure clinical results, update roadmap"
- "Reframe: update hypothesis framing in design.md and results.md for action-dependent stance"
- "Analysis: shallow-depth reanalysis shows d=X for affect at tau=1,2"
- "Experiment: shallow_affect_confirm complete, d=X affect signal confirmed at tau=1,2"

---

## When to Stop and Ask

STOP and flag in STATE.md if:
- Shallow-depth re-analysis shows affect effect is STILL weak (d<0.3) at tau=1 — this would require fundamental reframing of the paper story
- Clinical rerun on new architecture shows qualitatively different phenotype ordering than old results
- Any experiment produces results that contradict H2 (affect provides zero benefit at any depth)
- Tests fail in a way that suggests a design problem, not a fixable bug

---

## Constraints

- All safety invariants from CLAUDE.md apply
- Tests before every experiment
- Never overwrite existing result files
- Do not work on docs/paper/
- Do not touch benchmark/ or CvC code
- Do not implement pymdp
- Do not implement gamma scaling (not standard AIF)
- Do not push to remote unless user explicitly requests
