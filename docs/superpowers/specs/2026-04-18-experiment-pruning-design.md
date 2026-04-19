# sub-project D — experiment configs + research-question cleanup (design)

date: 2026-04-18
status: design — ready for `writing-plans`
parent scoping: `docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md`
upstream specs:
- `docs/superpowers/specs/2026-04-18-aif-extraction-design.md` (B+A — designed, not yet implemented)
- `docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md` (F — completed, configs landed)
upstream completed: sub-project C (agent inventory) and sub-project F (multi-focal runtime), both 2026-04-18

---

## why this doc exists

the scoping audit found that the experiment surface had drifted in three independent ways:

1. **hypothesis labels are inconsistent** between `analysis/hypotheses.py` (code) and `docs/experiment/design.md` (theory). h5 means two completely different claims; h1/h2 are off-by-one slot; one code test (`test_h2_depth_matters`) predicts the *opposite* direction from what the theory doc now claims.
2. **config surface has redundancy and dead references**. 28 total configs (5 cvc out of scope, 23 in scope). benchmark_betrayal trio differ only in rounds/switch timing; benchmark_full and benchmark_comprehensive duplicate each other; design.md references `horizon_sweep.json` and `deep_affect_test.json` that no longer exist.
3. **labels were framed as defended claims** (e.g. "h1 g compression / depth redundancy"), some of which are partially falsified by recent runs. the framing should shift from claims-to-defend to questions-to-answer so we can report descriptively without rhetorical baggage.

D's job is to settle all three at once — derive a canonical research-question set from the codebase as it actually is, prune configs to match, redesign the analysis surface, and write a manifest that prevents the same drift from recurring.

D's job is **not** to rewrite docs (sub-project E) or rerun experiments (separate research sessions gated on D's analysis code being live).

---

## decisions log (cross-reference)

| id | decision | rationale |
|---|---|---|
| D1 | survival criterion is "useful for proving / characterizing a research question grounded in the current codebase + configs"; paper figures are a downstream consumer, not the criterion (paper is stale) | user direction; paper out of scope per scoping doc |
| D2 | derive canonical RQ set from the union of code, configs, and current docs rather than picking either side; do not preserve either old numbering | user direction |
| D3 | reframe from claims to defend (`H1 = depth redundancy`) to questions to answer (`RQ1 = role of planning depth`); descriptive language in docstrings | user direction; matches current epistemic state |
| D4 | rename `H#` → `RQ#` everywhere (configs, tests, docs, manifest); accept the larger churn for unambiguous semantic shift | user direction |
| D5 | keep config inventory: 4 archives, 2 merges, 17 renames; rerun priority `rq2 → rq5 → rq7 → rest` | matches STATE.md blockers and post-restructure invalidation |
| D6 | analysis file rename `analysis/hypotheses.py → analysis/research_questions.py` with deprecation shim for one release; introduce `test_*` (predicate) vs `report_*` (descriptive) split | external script + notebook surface needs a soft migration; signal-vs-claim distinction matters |
| D7 | new `docs/experiment/manifest.md` is a D deliverable (not deferred to E); manifest is the single source of truth for `config ↔ RQ ↔ analysis function` mapping | E needs it on day one; treating it as a D deliverable forces it to land before E starts |
| D8 | new `tests/test_manifest_consistency.py` validator enforces manifest ↔ configs ↔ analysis-functions consistency in `pytest` | prevents the same drift from re-emerging silently |
| D9 | rollout collapses phases 1–4 into a single PR (analysis rename + config rename/merge/archive + new metrics + manifest + validator); phase 5 (shim removal) stays a separate follow-up after one release | smaller review surface than 4 PRs; shim deletion is genuinely independent |

---

## section 1 — canonical research-question set

framing: each entry below is a question to be answered by experiments, not a claim to be defended. analysis functions describe regimes; the user (or paper) decides what counts as supporting / refuting evidence.

### research questions

#### RQ1 — role of planning depth

**question**: how does explicit planning depth affect performance across binary and graded payoff regimes — does deeper help, saturate, or interact with affect?

**configs**: `rq1_depth_factorial.json`, `rq6_graded_factorial.json` (cross-referenced for graded curve)

**analysis**: `analysis.research_questions.report_rq1_depth_curve` → `rq1_depth_curve.json`

descriptive: payoff(tau) curve per `condition_name × payoff_mode × scenario` with bootstrap CI; reports curve-shape statistics (slope at low tau, plateau detection, monotonicity). does not assert "depth helps" or "depth saturates".

#### RQ2 — regime where affect adds value

**question**: is there a `(tau × payoff_mode × scenario)` regime where affect-augmented agents systematically outperform matched-depth no-affect controls, and how large is the effect?

**configs**: `rq2_shallow_affect.json` (focused tau∈{1,2,3}), `rq1_depth_factorial.json` (paired contrast at every tau), `rq6_graded_factorial.json` (graded contrast)

**analysis**: `analysis.research_questions.report_rq2_affect_value` → `rq2_affect_value.json`

descriptive: returns d, p, mean affect gain across regimes. does not return support/reject.

#### RQ3 — lesion dissociation (Damasio analog)

**question**: does decoupling affect from policy selection preserve type inference accuracy while degrading payoff, and at which horizons?

**configs**: `rq3_lesion_dissociation.json`

**analysis**: `analysis.research_questions.test_rq3_lesion_dissociation` → `rq3_lesion_dissociation.json`

predicate: `type_accuracy_preserved`, `payoff_lower_than_intact`, `stance_recovery_worse_than_intact` (booleans + supporting metrics). this question has a genuinely binary answer, so keep `test_*` shape.

#### RQ4 — betrayal recovery

**question**: does affect help recover faster after a stance switch in the post-switch window?

**configs**: `rq4_betrayal_recovery.json`, `rq7_clinical_betrayal.json` (clinical presets layered on the same betrayal scenario)

**analysis**: `analysis.research_questions.test_rq4_betrayal_recovery` → `rq4_betrayal_recovery.json`

predicate: post-switch payoff difference, detection latency, recovery latency. absorbs the post-switch metric from the removed `test_h5_affect_vs_no_affect_post_switch` (which was an unintentional duplicate of this question).

#### RQ5 — partner selection

**question**: in `agent_choice` settings, do affect-guided agents preferentially select well-modeled partners?

**configs**: `rq5_partner_selection.json`

**analysis**: `analysis.research_questions.test_rq5_partner_selection` → `rq5_partner_selection.json` (**NEW** — replaces the mislabeled current `test_h5_affect_vs_no_affect_post_switch`)

predicate: correlation between per-partner beta and partner-choice frequency, partner-choice entropy, and payoff conditioned on selected partner.

#### RQ6 — graded payoff unlocks the precision channel

**question**: by enlarging the action space (binary → 6-level graded), does `q_pi` entropy rise enough that mu becomes load-bearing for the affect-vs-no-affect contrast?

**configs**: `rq6_graded_factorial.json`, `rq6_graded_betrayal.json`

**analysis**: `analysis.research_questions.report_rq6_graded_channel` → `rq6_graded_channel.json` (**NEW**)

descriptive: per-condition `q_pi` entropy summary, realized mu summary, affect-vs-no-affect deltas in graded mode (cross-referenced with binary deltas from RQ2 for context).

#### RQ7 — clinical task-specificity

**question**: where (which task family / EFE landscape) do clinical preset parameter regimes (alexithymia, borderline, depression) produce measurable behavioral differences vs healthy baseline?

**configs**: `rq7_clinical_betrayal.json`, `rq7_clinical_phenotypes.json`, `rq7_sensitivity_sweep.json`; cross-references `rq6_graded_betrayal.json` for the graded clinical comparison

**analysis**: `analysis.research_questions.report_rq7_clinical_resolution` → `rq7_clinical_resolution.json` (**NEW**)

descriptive: pairwise effect sizes (cohen's d) for `clinical-vs-baseline` and `between-clinical`, broken out by `payoff_mode × scenario`. reports the regime in which each clinical preset becomes behaviorally distinguishable.

### engineering objectives (not research questions)

these are not testable hypotheses; they are deliverables whose outputs feed the paper as supporting evidence.

#### E1 — baseline competitiveness

**deliverable**: AIF agents (affective + matched no-affect + lesioned) compared head-to-head against scripted baselines (TFT / WSLS / Pavlov / GRIM / Q-learning / Random) under matched conditions across multiple scenarios.

**configs**: `e1_benchmark_arena.json` (merged from `benchmark_full` + `benchmark_comprehensive`), `e1_benchmark_betrayal_fair.json` (matched-horizon, the cleanest contrast), `e1_benchmark_betrayal_kitchen_sink.json` (longer rounds + lesioned variant), `e1_benchmark_noisy.json`

**analysis**: `analysis.research_questions.report_e1_baseline_competitiveness` → `e1_baseline_ranking.json` (**NEW**)

descriptive: per-scenario ranking of all agents by mean payoff with bootstrap CI; pairwise win-rate matrix.

#### E2 — multi-focal emergent dynamics

**deliverable**: descriptive characterization of emergent dynamics when M focal AIF agents play each other (cooperation buildup with homogeneous affective populations; asymmetric clinical signatures in mixed populations; assortative pairing in agent_choice).

**configs**: `e2_multifocal_homogeneous.json`, `e2_multifocal_clinical_mix.json`, `e2_multifocal_assortative.json`

**analysis**: `analysis.research_questions.report_e2_multi_focal_dynamics` → `e2_multi_focal_dynamics.json` (**NEW**)

descriptive: per-round per-agent cooperation rate, type-distribution drift over time, pairing transition matrix (when agent_choice), cooperation-cascade detection.

### what changes from today's state

| was | becomes | reason |
|---|---|---|
| `test_h1_orthogonal_augmentation` | `report_rq2_affect_value` | label moves down a slot; reframed descriptive |
| `test_h2_depth_matters` (predicts tau8 > tau1) | `report_rq1_depth_curve` (no directional prediction) | direction is empirically open; descriptive curve |
| `test_h3_lesion_dissociation` | `test_rq3_lesion_dissociation` | rename only |
| `test_h4_betrayal_recovery` | `test_rq4_betrayal_recovery` | rename only; absorbs h5 post-switch metric |
| `test_h5_affect_vs_no_affect_post_switch` | **REMOVED** | unintentional duplicate of h4 |
| (none) | `test_rq5_partner_selection` | NEW — replaces the mislabeled current h5 |
| (none) | `report_rq6_graded_channel` | NEW |
| (none) | `report_rq7_clinical_resolution` | NEW |
| (none) | `report_e1_baseline_competitiveness` | NEW |
| (none) | `report_e2_multi_focal_dynamics` | NEW |
| `test_h1_depth_compensation` (legacy alias) | **REMOVED** | dead alias |

### what's dropped from the surface entirely

- design.md "H6 = predictive model comparison (FUTURE)" → moved to `docs/future/` notes by sub-project E (no implementation, conceptually clean but not active)
- design.md "H7 = clinical sensitivity (PRELIMINARY, failure mode realized)" → that *finding* is the answer to RQ7, not a separate hypothesis

---

## section 2 — config inventory

### survivors (19, after 2 merges = 17 active files)

| # | current path | action | new path | feeds |
|---|---|---|---|---|
| 1 | `configs/smoke_test.json` | rename | `configs/smoke_focal.json` | smoke |
| 2 | `configs/multifocal_smoke.json` | rename | `configs/smoke_multifocal.json` | smoke |
| 3 | `configs/h1_depth_affect_factorial.json` | rename | `configs/rq1_depth_factorial.json` | RQ1 |
| 4 | `configs/shallow_affect_confirm.json` | rename | `configs/rq2_shallow_affect.json` | RQ2 |
| 5 | `configs/h2_lesion_dissociation.json` | rename | `configs/rq3_lesion_dissociation.json` | RQ3 |
| 6 | `configs/h4_betrayal_recovery.json` | rename | `configs/rq4_betrayal_recovery.json` | RQ4 |
| 7 | `configs/h5_partner_selection.json` | rename | `configs/rq5_partner_selection.json` | RQ5 |
| 8 | `configs/graded_trust_factorial.json` | rename | `configs/rq6_graded_factorial.json` | RQ6 |
| 9 | `configs/graded_betrayal.json` | rename | `configs/rq6_graded_betrayal.json` | RQ6 |
| 10 | `configs/clinical_betrayal.json` | rename | `configs/rq7_clinical_betrayal.json` | RQ4 + RQ7 |
| 11 | `configs/clinical_phenotypes.json` | rename | `configs/rq7_clinical_phenotypes.json` | RQ7 |
| 12 | `configs/sensitivity_affect_params.json` | rename | `configs/rq7_sensitivity_sweep.json` | RQ7 |
| 13 | `configs/benchmark_full.json` + `configs/benchmark_comprehensive.json` | **merge** | `configs/e1_benchmark_arena.json` | E1 |
| 14 | `configs/benchmark_betrayal_fair.json` | rename | `configs/e1_benchmark_betrayal_fair.json` | E1 |
| 15 | `configs/benchmark_betrayal_comprehensive.json` | rename | `configs/e1_benchmark_betrayal_kitchen_sink.json` | E1 |
| 16 | `configs/benchmark_noisy.json` | rename | `configs/e1_benchmark_noisy.json` | E1 |
| 17 | `configs/multifocal_homogeneous_affective.json` | rename | `configs/e2_multifocal_homogeneous.json` | E2 |
| 18 | `configs/multifocal_clinical_mix.json` | rename | `configs/e2_multifocal_clinical_mix.json` | E2 |
| 19 | `configs/multifocal_assortative_choice.json` | rename | `configs/e2_multifocal_assortative.json` | E2 |

### archived (move to `configs/archive/`, do not delete) — 4

| current path | reason archived |
|---|---|
| `configs/benchmark_default.json` | 10 reps × 100 rounds — strict subset of merged `e1_benchmark_arena`; smoke role already covered by `smoke_focal` |
| `configs/benchmark_resource_sharing.json` | 50 reps × 100 rounds — strict subset of `e1_benchmark_arena` |
| `configs/benchmark_comprehensive.json` | merged into `e1_benchmark_arena.json` |
| `configs/benchmark_betrayal.json` | merged into `e1_benchmark_betrayal_kitchen_sink.json` (200 rounds, p_switch=0, switch r100 — kitchen-sink covers it) |

### untouched (cvc, out of scope per MISSION) — 5

`configs/benchmark_cvc_affect_smoke.json`, `configs/benchmark_cvc_comparison.json`, `configs/benchmark_cvc_full.json`, `configs/benchmark_cvc_local_smoke.json`, `configs/benchmark_cvc_scoring_smoke.json`

### merge specifications

#### `e1_benchmark_arena.json` (canonicalization of `benchmark_full` + `benchmark_comprehensive`)

base: `benchmark_full.json` (it has `num_replications: 100`, `num_rounds: 200`, all tau* + lesioned + 5 baselines, scenario `resource_sharing`).

`benchmark_comprehensive.json` is identical except `num_replications: 50`. take `benchmark_full`'s settings as canonical; archive `benchmark_comprehensive.json`.

no schema change; pure consolidation.

#### `e1_benchmark_betrayal_kitchen_sink.json` (rename of `benchmark_betrayal_comprehensive`)

`benchmark_betrayal.json` (200 rounds, tau4 only, 4 baselines) is a strict subset; archive it.

`benchmark_betrayal_comprehensive.json` (200 rounds, tau4 + tau8 + lesioned + 6 baselines) becomes the canonical kitchen-sink betrayal config under the new name.

`benchmark_betrayal_fair.json` (100 rounds, matched horizons) is the cleaner contrast — kept under `e1_benchmark_betrayal_fair.json`.

### naming convention

- `smoke_*` for smoke configs (run on every restructure / B+A landing as gate)
- `rq#_<short_name>.json` for research-question configs
- `e#_<short_name>.json` for engineering-objective configs
- `configs/archive/<original_name>.json` for archived configs

every active config file (excluding cvc) must follow one of these patterns; `tests/test_manifest_consistency.py` enforces this.

### rerun priority

post-restructure, all prior result CSVs should be considered invalidated until rerun on the post-B+A model surface. priority follows STATE.md's live blockers + the user's decision to lead with RQ2 (the headline contrast).

| priority | config | reason |
|---|---|---|
| P0 | `rq2_shallow_affect.json` | STATE.md flags as needing rerun on post-restructure model; RQ2 headline evidence |
| P0 | `rq5_partner_selection.json` | partial run abandoned; metric is new (test_rq5_*) so rerun rather than salvage partials |
| P0 | `rq7_clinical_betrayal.json` | partial run abandoned (26 seeds); rerun |
| P0 | `rq7_clinical_phenotypes.json` | never produced csv; full run |
| P1 | `rq1_depth_factorial.json`, `rq3_lesion_dissociation.json`, `rq4_betrayal_recovery.json` | rerun on post-restructure model |
| P1 | `rq6_graded_factorial.json`, `rq6_graded_betrayal.json` | needs `report_rq6_*` analysis to land first |
| P2 | `e1_benchmark_arena.json`, `e1_benchmark_betrayal_*.json`, `e1_benchmark_noisy.json` | needs `report_e1_*` analysis; lower-priority methodological output |
| P2 | `e2_multifocal_*.json` | needs `report_e2_*` analysis; F's tests already gate behavior, this is descriptive |
| ongoing | `smoke_focal.json`, `smoke_multifocal.json` | run on every restructure / B+A landing |

reruns themselves are out of scope for D — D only delivers the new naming, the new analysis surface, and the manifest. reruns are scheduled by the research loop.

---

## section 3 — analysis code restructure

### file rename

`analysis/hypotheses.py` → `analysis/research_questions.py`

`analysis/hypotheses.py` becomes a deprecation-warning re-export shim (one release; phase 5 deletes it).

### function rename + redesign

| current | new | type | semantics |
|---|---|---|---|
| `test_h1_orthogonal_augmentation` | `report_rq2_affect_value` | report | descriptive: returns d, p, mean affect gain across regimes; does not return support/reject |
| `test_h2_depth_matters` | `report_rq1_depth_curve` | report | descriptive: payoff(tau) per condition × payoff_mode × scenario; reports curve shape statistics |
| `test_h3_lesion_dissociation` | `test_rq3_lesion_dissociation` | test | keep predicate-style return (existing logic) |
| `test_h4_betrayal_recovery` | `test_rq4_betrayal_recovery` | test | keep test-style; absorb post-switch payoff metric from removed h5 |
| `test_h5_affect_vs_no_affect_post_switch` | **REMOVED** | — | duplicate of rq4 |
| `test_h1_depth_compensation` (alias) | **REMOVED** | — | dead alias |
| (NEW) | `test_rq5_partner_selection` | test | needs new metric `partner_selection_summary` |
| (NEW) | `report_rq6_graded_channel` | report | needs `q_pi_entropy_summary`, `mu_realized_summary` |
| (NEW) | `report_rq7_clinical_resolution` | report | needs `clinical_vs_baseline_pairwise` |
| (NEW) | `report_e1_baseline_competitiveness` | report | needs `baseline_rank_summary` |
| (NEW) | `report_e2_multi_focal_dynamics` | report | needs `multi_focal_emergence_metrics` |
| `run_all_hypothesis_tests` | `run_all_research_questions` | orchestrator | returns `{questions: {rq1..rq7}, engineering: {e1, e2}}` |

### convention

- **`test_*`** = adversarial predicate; returns `{available: bool, supported: bool, evidence: dict}`. use only when the question has a genuinely binary answer. RQ3, RQ4, RQ5 are tests.
- **`report_*`** = descriptive; returns `{available: bool, summary: dict, breakdowns: dict}`. no support/reject. RQ1, RQ2, RQ6, RQ7, E1, E2 are reports.

### new metrics (added to `analysis/metrics.py`)

| metric function | needed for | input | output |
|---|---|---|---|
| `partner_selection_summary` | RQ5 | results df with `chosen_partner` column | per-seed: counts of partner choices, beta-vs-choice correlation, choice entropy |
| `q_pi_entropy_summary` | RQ6 | results df with `q_pi` per step (logger may need extension) | per-condition mean & p25/p75 of `q_pi` entropy |
| `mu_realized_summary` | RQ6 | results df with `mu` per run | per-condition mean realized mu, calibration delta vs configured |
| `clinical_vs_baseline_pairwise` | RQ7 | results df with clinical preset names | structured pairwise contrast over `payoff_mode × scenario × preset` |
| `baseline_rank_summary` | E1 | results df from benchmark configs | per-scenario agent ranking by mean payoff with bootstrap CI; pairwise win-rate matrix |
| `multi_focal_emergence_metrics` | E2 | results df from multifocal configs (per-agent, per-round) | per-round per-agent cooperation rate; type-distribution drift; pairing transition matrix; cascade detection |

logger extension scope: `q_pi_entropy_summary` and `mu_realized_summary` may require adding new columns to `experiment/logger.py` results.csv schema. if the columns aren't already there, **scope expands** to add them; check during implementation phase 1 and either confirm presence or add a small logger PR before phase 3.

### callsite updates (in scope for D)

| file | what changes |
|---|---|
| `analysis/__init__.py` | re-export new function names (and old names from shim) |
| `scripts/run_analysis.py` | switch import from `analysis.hypotheses` to `analysis.research_questions`; rewrite `_hypothesis_summary_frame` to handle `{questions, engineering}` structure; emit `research_questions.json` + `engineering_objectives.json`; during shim period also emit `hypothesis_tests.json` alias |
| `scripts/run_preliminary.py` | switch import |
| `tests/test_analysis_semantics.py` | update fixtures + assertions; cover the NEW report functions with synthetic-data fixtures |
| `cli/common.py` | audit `filter_primary_runs` for hardcoded condition names — likely no change needed, but verify |
| `experiment/factory.py` | audit for hardcoded config-path references — likely no change |

### backward compat

- `analysis/hypotheses.py` shim module re-exports every old function name with a `DeprecationWarning`. removed in phase 5 (separate follow-up after one release cycle).
- `scripts/run_analysis.py` writes `hypothesis_tests.json` next to the new `research_questions.json` for one release.
- old config filenames are **not** re-exported. paths are stable references; the rename is a clean break with `git mv` history preserved.

---

## section 4 — manifest doc + cross-cutting touchpoints

### new deliverable: `docs/experiment/manifest.md`

single source of truth for the `config ↔ RQ ↔ analysis function` mapping. every active config must appear here; every RQ/E must list its configs and analysis function.

schema per entry:

```markdown
### RQ#  <name>

**Question**: <one sentence>

**Configs**:
- `configs/rq#_<name>.json` — <one-line description> — status: {green | needs_rerun | partial | not_run}

**Analysis**: `analysis.research_questions.<test|report>_rq#_<name>` → `<artifact_name>.json`

**Last run**: <date or "never"> on commit <sha-short> with model_hint <opus|sonnet|n/a>

**Open blockers**: <bullets or "none">
```

E1/E2 use the same shape with `**Deliverable**:` instead of `**Question**:`.

initial population: every entry starts with `status: needs_rerun` (since post-restructure invalidates all prior result CSVs) and `Last run: never (post-restructure)`.

### validator: `tests/test_manifest_consistency.py`

a `pytest` module that asserts:

1. every `configs/*.json` (excluding `configs/archive/` and `configs/benchmark_cvc_*.json`) appears in at least one manifest entry as `Configs:` reference
2. every manifest `Configs:` reference points to a file that exists on disk
3. every `test_rq*` / `report_rq*` / `report_e*` function in `analysis.research_questions.run_all_research_questions` is mentioned in some manifest entry as an `Analysis:` reference
4. every manifest `Analysis:` reference is callable on `analysis.research_questions`

implementation: minimal markdown parser in `analysis/_manifest.py` (read fenced sections; pure stdlib, no extra deps). validator runs in default `pytest`.

failure mode: clear error messages like `"configs/rq2_shallow_affect.json is not referenced by any manifest entry"` or `"manifest references analysis.research_questions.report_rq8_xyz which does not exist"`.

### cross-cutting touchpoints (in scope for D)

| file | what changes | reason |
|---|---|---|
| `analysis/hypotheses.py` → `analysis/research_questions.py` | rename + redesign per section 3 | core change |
| `analysis/__init__.py` | re-export new names | |
| `analysis/metrics.py` | add 6 new metric functions per section 3 | enables new RQ/E reports |
| `analysis/_manifest.py` | NEW — markdown parser for validator | supports validator |
| `scripts/run_analysis.py` | switch import + rewrite `_hypothesis_summary_frame` + dual-write json artifacts during shim period | callsite |
| `scripts/run_preliminary.py` | switch import | callsite |
| `tests/test_analysis_semantics.py` | update fixtures + assertions; add fixtures for new report functions | tests must pass |
| `tests/test_manifest_consistency.py` | NEW — manifest validator | enforces drift prevention |
| `configs/*.json` | rename per section 2 (17 renames, 2 merges, 4 archives) | inventory cleanup |
| `configs/archive/*.json` | new directory; preserves merged/archived configs | history preserved |
| `configs/archive/README.md` | NEW — documents read-only policy: archive contents may be restored or rewritten in future work, never edited in place | discourages drift back into archive |
| `experiment/logger.py` | audit during phase 1; if `q_pi_entropy` and `mu` are not in results.csv schema, extend logger before phase 3 | RQ6 metric prerequisites |
| `cli/common.py` | audit `filter_primary_runs` for hardcoded condition names | callsite verification |
| `experiment/factory.py` | audit for hardcoded config-path references | callsite verification |
| `conductor/STATE.md` | rewrite `pending_work` and `next_session_focus` against new config names | operational tracker |
| `docs/experiment/manifest.md` | **NEW** — core experiment manifest | new deliverable |

### out of scope for D, deferred to E

| file | why deferred |
|---|---|
| `docs/experiment/design.md` | full rewrite — E's job |
| `docs/experiment/results.md` | rewrite once new runs land — E's job |
| `docs/theory/theory.md` | hypothesis labels referenced — E's job |
| `AGENTS.md`, `CLAUDE.md`, `README.md` | restructure — E's job; E will pull `manifest.md` as the canonical RQ→config map |
| `docs/design/*.md` | restructure — E's job |
| `docs/paper/main.tex` | explicitly out of scope per scoping doc |

### STATE.md rerun policy update (concrete diff to apply)

```yaml
pending_work:
  - "P0 rerun rq2_shallow_affect (was shallow_affect_confirm) on the post-restructure model — primary RQ2 evidence"
  - "P0 implement test_rq5_partner_selection metric, then run rq5_partner_selection (was h5_partner_selection)"
  - "P0 rerun rq7_clinical_betrayal (was clinical_betrayal); previous detached rerun stopped at 26 seeds"
  - "P0 run rq7_clinical_phenotypes (was clinical_phenotypes); never produced csv"
  - "P1 implement report_rq6_graded_channel + report_rq7_clinical_resolution; rerun rq6_graded_factorial and rq6_graded_betrayal"
  - "P1 implement report_e1_baseline_competitiveness; rerun e1_benchmark_arena (merged) + e1_benchmark_betrayal_fair"
  - "P1 implement report_e2_multi_focal_dynamics; rerun e2_multifocal_*"
next_session_focus: "land D's plan, then sequence rq2 → rq5 → rq7 reruns"
```

`next_priority`, `model_hint`, `mode_hint` unchanged in this design (no D opinion).

---

## section 5 — rollout strategy + acceptance criteria

### rollout (phases 1–4 collapsed into one PR per D9; phase 5 separate)

**single PR (phases 1–4 combined)**

- phase 1: analysis code rename + tests
  - `analysis/hypotheses.py` → `analysis/research_questions.py` with deprecation shim
  - function renames per section 3
  - `tests/test_analysis_semantics.py` updated for renames
  - `scripts/run_analysis.py` and `scripts/run_preliminary.py` switched
  - existing tests green at this commit point inside the PR

- phase 2: config renames + archive
  - 17 renames via `git mv` (preserves history)
  - 4 moves to `configs/archive/` via `git mv`
  - 2 merges (canonicalize `e1_benchmark_arena.json`, drop redundant betrayal)
  - `configs/archive/README.md` documents read-only policy
  - smoke configs (`smoke_focal.json`, `smoke_multifocal.json`) run end-to-end

- phase 3: new metrics + new test/report functions
  - 6 new metric functions in `analysis/metrics.py`
  - 5 new RQ/E report+test functions in `analysis/research_questions.py`
  - if `q_pi_entropy` / `mu` not in results.csv schema, extend `experiment/logger.py` first
  - each new function gets a unit test with a synthetic results DataFrame

- phase 4: manifest + validator
  - write `docs/experiment/manifest.md` (every active config + RQ/E referenced; initial status `needs_rerun`)
  - write `analysis/_manifest.py` (markdown parser)
  - write `tests/test_manifest_consistency.py` (validator)
  - update `conductor/STATE.md` with new naming + rerun priority
  - final pytest run: green

**phase 5 (separate follow-up PR, after one release cycle)**

- delete `analysis/hypotheses.py` shim
- delete `hypothesis_tests.json` alias write in `scripts/run_analysis.py`
- update `analysis/__init__.py` to drop deprecated re-exports

### acceptance criteria for D

D is "done" when all of these are true on a single green commit:

- [ ] all 17 config renames + 2 merges + 4 archives applied with `git mv` history preserved
- [ ] `configs/archive/README.md` exists with read-only policy
- [ ] `analysis/research_questions.py` exists with 7 RQ functions + 2 E functions, each with at least one unit test in `tests/test_analysis_semantics.py`
- [ ] `analysis/hypotheses.py` is a deprecation shim re-exporting old names
- [ ] `scripts/run_analysis.py` produces `research_questions.json` + `engineering_objectives.json` and (during shim period) `hypothesis_tests.json` alias
- [ ] `analysis/metrics.py` contains all 6 new metric functions, each with a unit test
- [ ] `experiment/logger.py` schema confirmed (or extended) to include `q_pi` entropy and realized `mu`
- [ ] `docs/experiment/manifest.md` exists; every active config (excluding cvc) and every RQ/E function is referenced
- [ ] `tests/test_manifest_consistency.py` passes (validator) in default `pytest`
- [ ] full default `pytest` green; no `slow`-marked test added by D
- [ ] `conductor/STATE.md` updated with new pending_work block per section 4
- [ ] `smoke_focal.json` and `smoke_multifocal.json` run end-to-end on the final commit

### what's still NOT done after D

- doc rewrites (sub-project E)
- actual rerun of pending experiments (separate research sessions, gated on D's analysis code being live)
- paper update (out of scope per scoping doc)
- shim removal (phase 5, separate follow-up PR)

---

## what is explicitly out of scope for D

- cvc / cogames stack — `configs/benchmark_cvc_*.json`, `benchmark/cvc_*.py`, `tests/test_cvc_*.py`. per `conductor/MISSION.md`, do not touch.
- rewriting any documentation file except `docs/experiment/manifest.md` (NEW) and `conductor/STATE.md` (operational tracker). everything else is sub-project E.
- running any experiment. D delivers the surface; reruns are scheduled by the research loop after D lands.
- changing agent classes or generative model code. those landed in C / B+A.
- changing the multi-focal runtime. that landed in F.
- new science. RQ8+ or new engineering objectives are out of scope; they go through their own brainstorming.

---

## handoff

after this design is approved by the user, this session:

1. (this file) commit the design spec to `docs/superpowers/specs/`
2. invoke `writing-plans` skill to produce an implementation plan
3. commit the implementation plan to `docs/superpowers/plans/2026-04-18-experiment-pruning-plan.md`
4. NOT start implementation in the same session

a separate executing-plans session implements the plan as a single PR (phases 1–4) with phase 5 as a deferred follow-up.

after D lands, sub-project E (doc rewrite) brainstorming starts in a fresh session with this spec as a primary input.
