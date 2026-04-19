# Sub-project D — Experiment Configs + Research-Question Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the experiment surface — rename `analysis/hypotheses.py` to `analysis/research_questions.py` with a deprecation shim, rename/merge/archive 23 in-scope configs to `rq#_*` / `e#_*` / `smoke_*` naming, add 5 new RQ/E analysis functions backed by 6 new metric helpers, and write `docs/experiment/manifest.md` plus a CI validator that prevents the same drift from recurring.

**Architecture:** Single PR collapses phases 1–4 (analysis rename, config inventory cleanup, new metrics + functions, manifest + validator). Phase 5 (shim removal) is a separate follow-up PR after one release cycle. Backward compat preserved during the shim period via `analysis/hypotheses.py` re-export shim and a `hypothesis_tests.json` alias artifact written alongside `research_questions.json`. All renames use `git mv` to preserve history.

**Tech Stack:** Python 3.12, numpy, pandas, pytest. No new third-party deps. Markdown parser for the manifest validator is hand-written using stdlib only (no external markdown lib).

**Spec reference:** `docs/superpowers/specs/2026-04-18-experiment-pruning-design.md`. Decision numbers (D1–D9) in this plan refer to that spec's decisions log.

**Skills referenced:**
- @superpowers:test-driven-development for new analysis/metric functions (write failing tests first)
- @superpowers:verification-before-completion before claiming acceptance criteria met
- @superpowers:systematic-debugging if any test fails after a rename

---

## File Structure

### Files modified

| path | role | change |
|---|---|---|
| `analysis/__init__.py` | package surface | re-export new function names |
| `analysis/hypotheses.py` | now: full implementation; after: deprecation shim | becomes shim re-exporting from `research_questions` |
| `analysis/metrics.py` | metric helpers | add 6 new metric functions |
| `scripts/run_analysis.py` | CLI entry point | switch import; rewrite `_hypothesis_summary_frame`; dual-write JSON |
| `scripts/run_preliminary.py` | CLI entry point | switch import |
| `tests/test_analysis_semantics.py` | analysis-fn tests | rename references; add fixtures for new fns |
| `experiment/logger.py` | round-level logger | add `mu_realized` column if missing (gate on phase 1 audit) |
| `cli/common.py` | shared CLI helpers | audit only — likely no change |
| `experiment/factory.py` | config-to-experiment construction | audit only — likely no change |
| `conductor/STATE.md` | operational tracker | update `pending_work` + `next_session_focus` per spec section 4 |

### Files created

| path | role |
|---|---|
| `analysis/research_questions.py` | new module — 7 RQ functions + 2 E functions + orchestrator |
| `analysis/_manifest.py` | minimal markdown parser for the manifest validator (stdlib only) |
| `tests/test_manifest_consistency.py` | pytest validator: configs ↔ manifest ↔ analysis fns |
| `docs/experiment/manifest.md` | NEW — single source of truth for config ↔ RQ ↔ analysis mapping |
| `configs/archive/README.md` | documents read-only policy for archived configs |
| `configs/archive/` (directory) | preserves merged/archived configs |

### Files renamed (`git mv` to preserve history)

17 config renames + 4 archive moves + 1 module rename, listed in Phase 2 below.

### Files deleted (Phase 5, deferred)

- `analysis/hypotheses.py` (after shim period)
- `hypothesis_tests.json` alias write in `scripts/run_analysis.py` (after shim period)

---

## Phase 0 — Pre-flight audit

These tasks gather information needed by later phases. Each is a read-only audit and produces a short note in the PR description.

### Task 0.1: Audit logger.py for mu column

**Files:**
- Inspect: `experiment/logger.py`

- [ ] **Step 1: Read the logger source**

```bash
grep -n "mu\|realized" experiment/logger.py
```

Expected: `q_pi_entropy` and `q_pi` are present (verified during plan-write). `mu_realized` may or may not be — discover.

- [ ] **Step 2: If `mu_realized` not present, add it before Phase 3**

If absent, plan a single commit early in Phase 3 that:
- adds `"mu_realized": float(agent_metrics["mu_realized"])` to the record dict in `MetricLogger.log_round`
- ensures `agent_metrics` carries `mu_realized` (likely via the agent's `update_step` or `decision_step` return value)
- adds a unit test in `tests/test_payoff_modality_in_likelihood.py` or a new `tests/test_logger_schema.py` that asserts `mu_realized` is in the resulting CSV

**Note in PR**: "Logger schema: q_pi_entropy ✓, q_pi ✓, mu_realized {present|added in commit X}"

### Task 0.2: Inventory current callsites of hypotheses.py

- [ ] **Step 1: Find every import of `analysis.hypotheses`**

```bash
rg "from analysis.hypotheses import|import analysis.hypotheses" -n
rg "hypothesis_tests\.json" -n
rg "test_h[0-9]_" -n
```

Expected callsites (from spec section 3): `scripts/run_analysis.py`, `scripts/run_preliminary.py`, `tests/test_analysis_semantics.py`, possibly `analysis/__init__.py`.

- [ ] **Step 2: Note any unexpected callsites in PR description**

If anything outside the spec's expected list shows up (e.g. a notebook, a CI script), add it to the Phase 1 task list.

### Task 0.3: Inventory current callsites of config filenames being renamed

- [ ] **Step 1: For each old config name, find references**

```bash
for cfg in shallow_affect_confirm h1_depth_affect_factorial h2_lesion_dissociation \
           h4_betrayal_recovery h5_partner_selection graded_trust_factorial \
           graded_betrayal clinical_betrayal clinical_phenotypes \
           sensitivity_affect_params benchmark_full benchmark_comprehensive \
           benchmark_betrayal benchmark_betrayal_fair benchmark_betrayal_comprehensive \
           benchmark_noisy benchmark_default benchmark_resource_sharing \
           multifocal_homogeneous_affective multifocal_clinical_mix \
           multifocal_assortative_choice smoke_test multifocal_smoke; do
    echo "=== $cfg ==="
    rg "$cfg" -n --type-add 'cfg:*.{json,py,md,sh,yml,yaml,toml}' --type cfg
done
```

Expected non-config callsites: `conductor/STATE.md`, possibly `docs/experiment/design.md` (E will fix), `scripts/*` examples, `tests/test_*.py` fixtures.

- [ ] **Step 2: Build a `sed` script for non-source-file renames**

Tracked changes go into Phase 2 commits. Doc-file references that fall in sub-project E's surface are NOT updated by D (E owns those edits).

---

## Phase 1 — Analysis code rename + tests

### Task 1.1: Create the new module skeleton

**Files:**
- Create: `analysis/research_questions.py`

- [ ] **Step 1: Write empty module with docstring**

```python
"""Per-research-question analysis functions.

Conventions:
- ``test_rq*`` / ``test_e*``: predicate-style — return ``{available, supported, evidence}``.
  use only when the question has a genuinely binary answer.
- ``report_rq*`` / ``report_e*``: descriptive — return ``{available, summary, breakdowns}``.
  no support/reject; describes regimes for the human to interpret.

See ``docs/experiment/manifest.md`` for the canonical config ↔ RQ ↔ analysis-fn map.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
```

- [ ] **Step 2: Commit**

```bash
git add analysis/research_questions.py
git commit -m "analysis: scaffold research_questions module (D phase 1)"
```

### Task 1.2: Move existing helpers from hypotheses.py to research_questions.py

The private helpers (`_clean`, `_mean`, `_std`, `_welch_ttest`, `_cohen_d`, `_summary_by_condition`, `_condition_values`, `_paired_seed_differences`, `_depth_gain_payload`, `_switch_window_metric`, `_latency_metric`) are reused by the new functions. Move them, don't rewrite.

**Files:**
- Modify: `analysis/research_questions.py`
- Modify: `analysis/hypotheses.py`

- [ ] **Step 1: Read the existing helpers**

```bash
sed -n '27,131p' analysis/hypotheses.py
```

- [ ] **Step 2: Copy all private helpers (lines 27–131) into `analysis/research_questions.py`**

Preserve docstrings. Do not rewrite the helpers' bodies.

- [ ] **Step 3: Verify imports are sufficient**

The helpers use `np` and `pd`; no other imports needed.

- [ ] **Step 4: Commit**

```bash
git add analysis/research_questions.py
git commit -m "analysis: move private helpers to research_questions.py (D phase 1)"
```

### Task 1.3: Port RQ3 (lesion dissociation) — pure rename of `test_h3_lesion_dissociation`

**Files:**
- Modify: `analysis/research_questions.py`

- [ ] **Step 1: Read the current `test_h3_lesion_dissociation` (lines 213–260)**

- [ ] **Step 2: Add identical function under new name `test_rq3_lesion_dissociation` to `research_questions.py`**

Update only:
- Function name: `test_h3_lesion_dissociation` → `test_rq3_lesion_dissociation`
- Docstring header: "RQ3 — does decoupling affect from policy selection preserve type inference accuracy while degrading payoff?"
- Internal label keys in returned dict: `"hypothesis": "h3"` → `"research_question": "rq3"`
- Return key `"supported"` stays (predicate-style retained per spec section 3)

- [ ] **Step 3: Add unit test for RQ3 in test_analysis_semantics.py (will be moved during Task 1.10)**

For now, add a minimal smoke test:

```python
def test_rq3_lesion_dissociation_runs_on_synthetic_data():
    from analysis.research_questions import test_rq3_lesion_dissociation
    df = _build_lesion_dissociation_fixture()  # existing helper, rename if needed
    result = test_rq3_lesion_dissociation(df)
    assert result["available"] is True
    assert "supported" in result
```

- [ ] **Step 4: Run pytest on the new test**

```bash
pytest tests/test_analysis_semantics.py::test_rq3_lesion_dissociation_runs_on_synthetic_data -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add analysis/research_questions.py tests/test_analysis_semantics.py
git commit -m "analysis: port test_rq3_lesion_dissociation (D phase 1)"
```

### Task 1.4: Port RQ4 (betrayal recovery) — rename + absorb removed h5 post-switch metric

**Files:**
- Modify: `analysis/research_questions.py`
- Modify: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Read `test_h4_betrayal_recovery` (lines 262–306) and `test_h5_affect_vs_no_affect_post_switch` (lines 308–356)**

- [ ] **Step 2: Identify the post-switch payoff metric in `test_h5_*` that's distinct from h4**

The h5 function returns a `post_switch_payoff_diff` style metric. Audit and confirm it's not already computed in `test_h4_*`.

- [ ] **Step 3: Implement `test_rq4_betrayal_recovery` in research_questions.py**

Body = `test_h4_betrayal_recovery` body + the post-switch payoff metric absorbed from h5. Return dict additions:

```python
return {
    # ... existing h4 fields ...
    "post_switch_payoff_difference": post_switch_diff,  # absorbed from h5
    "research_question": "rq4",
}
```

- [ ] **Step 4: Write a unit test that asserts both the original h4 logic AND the absorbed metric work**

```python
def test_rq4_betrayal_recovery_includes_post_switch_metric():
    from analysis.research_questions import test_rq4_betrayal_recovery
    df = _build_betrayal_fixture()
    result = test_rq4_betrayal_recovery(df)
    assert result["available"] is True
    assert "post_switch_payoff_difference" in result
```

- [ ] **Step 5: Run the test**

```bash
pytest tests/test_analysis_semantics.py::test_rq4_betrayal_recovery_includes_post_switch_metric -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add analysis/research_questions.py tests/test_analysis_semantics.py
git commit -m "analysis: port test_rq4_betrayal_recovery, absorb h5 post-switch metric (D phase 1)"
```

### Task 1.5: Port RQ1 (depth curve) — `test_h2_depth_matters` → `report_rq1_depth_curve` (descriptive reframe)

**Files:**
- Modify: `analysis/research_questions.py`
- Modify: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Read `test_h2_depth_matters` (lines 180–211)**

The current function returns `supported: bool` based on monotonicity / direction of payoff vs tau. The new function reports the curve shape descriptively without a verdict.

- [ ] **Step 2: Implement `report_rq1_depth_curve`**

```python
def report_rq1_depth_curve(results: pd.DataFrame) -> dict:
    """RQ1 — describe payoff(tau) curve per condition × payoff_mode × scenario.

    Descriptive: returns slope at low tau, plateau detection, monotonicity.
    Does NOT assert "depth helps" or "depth saturates".
    """
    summary = _summary_by_condition(results)
    if summary.empty:
        return {"available": False, "research_question": "rq1"}

    breakdowns = {}
    for condition_name in summary["condition_name"].unique():
        condition_summary = summary[summary["condition_name"] == condition_name]
        depths = sorted(condition_summary["tau"].unique())
        payoff_curve = {
            int(tau): float(_mean(_condition_values(
                summary, f"{condition_name}_tau{tau}", "mean_payoff"
            )))
            for tau in depths
        }
        breakdowns[condition_name] = {
            "payoff_curve": payoff_curve,
            "slope_low_tau": _slope_low_tau(payoff_curve, depths),
            "monotonic": _is_monotonic(payoff_curve, depths),
            "plateau_detected": _plateau_detected(payoff_curve, depths, threshold=0.05),
        }

    return {
        "available": True,
        "research_question": "rq1",
        "summary": {"num_conditions": len(breakdowns)},
        "breakdowns": breakdowns,
    }
```

Add helper functions `_slope_low_tau`, `_is_monotonic`, `_plateau_detected` to research_questions.py (private). These are simple math helpers (5–10 lines each).

- [ ] **Step 3: Write a unit test**

```python
def test_report_rq1_depth_curve_reports_per_condition_breakdowns():
    from analysis.research_questions import report_rq1_depth_curve
    df = _build_depth_factorial_fixture()  # multi-tau, multi-condition synthetic data
    result = report_rq1_depth_curve(df)
    assert result["available"] is True
    assert "breakdowns" in result
    cond_breakdown = next(iter(result["breakdowns"].values()))
    assert "payoff_curve" in cond_breakdown
    assert "slope_low_tau" in cond_breakdown
    assert "monotonic" in cond_breakdown
    assert "plateau_detected" in cond_breakdown
    assert "supported" not in result  # descriptive, not predicate
```

- [ ] **Step 4: Run the test**

```bash
pytest tests/test_analysis_semantics.py::test_report_rq1_depth_curve_reports_per_condition_breakdowns -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add analysis/research_questions.py tests/test_analysis_semantics.py
git commit -m "analysis: port report_rq1_depth_curve as descriptive (D phase 1)"
```

### Task 1.6: Port RQ2 (affect value) — `test_h1_orthogonal_augmentation` → `report_rq2_affect_value` (descriptive reframe)

**Files:**
- Modify: `analysis/research_questions.py`
- Modify: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Read `test_h1_orthogonal_augmentation` (lines 133–178)**

- [ ] **Step 2: Implement `report_rq2_affect_value`**

Body: same statistical machinery (Welch's t-test, Cohen's d), but return shape changes:

```python
def report_rq2_affect_value(results: pd.DataFrame) -> dict:
    """RQ2 — describe the regime where affect adds value.

    Descriptive: returns d, p, mean affect gain across regimes.
    Does NOT return a support/reject verdict — the human (or paper) decides.
    """
    summary = _summary_by_condition(results)
    if summary.empty:
        return {"available": False, "research_question": "rq2"}

    affect_payoffs = _condition_values(summary, "affect", "mean_payoff")
    no_affect_payoffs = _condition_values(summary, "no_affect", "mean_payoff")
    if len(affect_payoffs) == 0 or len(no_affect_payoffs) == 0:
        return {"available": False, "research_question": "rq2"}

    welch = _welch_ttest(affect_payoffs, no_affect_payoffs)
    cohen_d = _cohen_d(affect_payoffs, no_affect_payoffs)
    mean_gain = _mean(affect_payoffs) - _mean(no_affect_payoffs)

    return {
        "available": True,
        "research_question": "rq2",
        "summary": {
            "mean_affect_gain": mean_gain,
            "cohen_d": cohen_d,
            "welch_t": welch["t"],
            "welch_p": welch["p"],
        },
        "breakdowns": {
            "affect_n": int(len(affect_payoffs)),
            "no_affect_n": int(len(no_affect_payoffs)),
        },
    }
```

- [ ] **Step 3: Unit test**

```python
def test_report_rq2_affect_value_returns_descriptive_summary():
    from analysis.research_questions import report_rq2_affect_value
    df = _build_affect_contrast_fixture()
    result = report_rq2_affect_value(df)
    assert result["available"] is True
    assert "supported" not in result  # descriptive
    assert result["summary"]["mean_affect_gain"] is not None
    assert "cohen_d" in result["summary"]
    assert "welch_p" in result["summary"]
```

- [ ] **Step 4: Run, commit**

```bash
pytest tests/test_analysis_semantics.py::test_report_rq2_affect_value_returns_descriptive_summary -v
git add analysis/research_questions.py tests/test_analysis_semantics.py
git commit -m "analysis: port report_rq2_affect_value as descriptive (D phase 1)"
```

### Task 1.7: Stub the 5 NEW functions (RQ5, RQ6, RQ7, E1, E2) — bodies land in Phase 3

**Files:**
- Modify: `analysis/research_questions.py`

- [ ] **Step 1: Add stubs returning `{"available": False, ...}`**

```python
def test_rq5_partner_selection(results: pd.DataFrame) -> dict:
    """RQ5 — do affect-guided agents preferentially select well-modeled partners?

    Predicate: correlation between per-partner beta and partner-choice frequency,
    partner-choice entropy, payoff conditioned on selected partner.
    """
    return {"available": False, "research_question": "rq5", "reason": "stub: implemented in D phase 3"}


def report_rq6_graded_channel(results: pd.DataFrame) -> dict:
    """RQ6 — does graded payoff unlock the precision channel?

    Descriptive: q_pi entropy summary, realized mu summary, affect-vs-no-affect
    deltas in graded mode (cross-referenced with binary deltas from RQ2).
    """
    return {"available": False, "research_question": "rq6", "reason": "stub: implemented in D phase 3"}


def report_rq7_clinical_resolution(results: pd.DataFrame) -> dict:
    """RQ7 — where do clinical preset parameter regimes produce measurable
    behavioral differences vs healthy baseline?

    Descriptive: pairwise Cohen's d for clinical-vs-baseline and between-clinical,
    broken out by payoff_mode × scenario.
    """
    return {"available": False, "research_question": "rq7", "reason": "stub: implemented in D phase 3"}


def report_e1_baseline_competitiveness(results: pd.DataFrame) -> dict:
    """E1 — AIF agents vs scripted baselines, head-to-head.

    Descriptive: per-scenario ranking of all agents by mean payoff with bootstrap CI;
    pairwise win-rate matrix.
    """
    return {"available": False, "engineering_objective": "e1", "reason": "stub: implemented in D phase 3"}


def report_e2_multi_focal_dynamics(results: pd.DataFrame) -> dict:
    """E2 — emergent dynamics when M focal AIF agents play each other.

    Descriptive: per-round per-agent cooperation rate, type-distribution drift,
    pairing transition matrix, cooperation-cascade detection.
    """
    return {"available": False, "engineering_objective": "e2", "reason": "stub: implemented in D phase 3"}
```

- [ ] **Step 2: Commit**

```bash
git add analysis/research_questions.py
git commit -m "analysis: stub new RQ5/RQ6/RQ7/E1/E2 functions (D phase 1)"
```

### Task 1.8: Implement the orchestrator `run_all_research_questions`

**Files:**
- Modify: `analysis/research_questions.py`

- [ ] **Step 1: Implement orchestrator**

```python
def run_all_research_questions(results: pd.DataFrame) -> dict:
    """Run all RQ + E analysis functions over a results DataFrame.

    Returns:
        {
            "questions": {"rq1": ..., "rq2": ..., ..., "rq7": ...},
            "engineering": {"e1": ..., "e2": ...},
        }
    """
    return {
        "questions": {
            "rq1": report_rq1_depth_curve(results),
            "rq2": report_rq2_affect_value(results),
            "rq3": test_rq3_lesion_dissociation(results),
            "rq4": test_rq4_betrayal_recovery(results),
            "rq5": test_rq5_partner_selection(results),
            "rq6": report_rq6_graded_channel(results),
            "rq7": report_rq7_clinical_resolution(results),
        },
        "engineering": {
            "e1": report_e1_baseline_competitiveness(results),
            "e2": report_e2_multi_focal_dynamics(results),
        },
    }
```

- [ ] **Step 2: Unit test**

```python
def test_run_all_research_questions_returns_questions_and_engineering_blocks():
    from analysis.research_questions import run_all_research_questions
    df = _build_minimal_fixture()
    result = run_all_research_questions(df)
    assert "questions" in result
    assert "engineering" in result
    assert set(result["questions"].keys()) == {"rq1", "rq2", "rq3", "rq4", "rq5", "rq6", "rq7"}
    assert set(result["engineering"].keys()) == {"e1", "e2"}
```

- [ ] **Step 3: Run, commit**

```bash
pytest tests/test_analysis_semantics.py::test_run_all_research_questions_returns_questions_and_engineering_blocks -v
git add analysis/research_questions.py tests/test_analysis_semantics.py
git commit -m "analysis: add run_all_research_questions orchestrator (D phase 1)"
```

### Task 1.9: Convert `analysis/hypotheses.py` to a deprecation shim

**Files:**
- Modify: `analysis/hypotheses.py`

- [ ] **Step 1: Replace contents of `analysis/hypotheses.py` with the shim**

```python
"""DEPRECATED — use ``analysis.research_questions`` instead.

This shim re-exports the legacy ``test_h*`` and ``run_all_hypothesis_tests`` names
for one release cycle. The shim will be removed in sub-project D phase 5.

Migration guide:
    test_h1_orthogonal_augmentation → report_rq2_affect_value
    test_h2_depth_matters           → report_rq1_depth_curve
    test_h3_lesion_dissociation     → test_rq3_lesion_dissociation
    test_h4_betrayal_recovery       → test_rq4_betrayal_recovery
    test_h5_affect_vs_no_affect_post_switch → REMOVED (was duplicate of h4)
    run_all_hypothesis_tests        → run_all_research_questions
"""

from __future__ import annotations

import warnings

from analysis.research_questions import (
    report_rq1_depth_curve as _report_rq1_depth_curve,
    report_rq2_affect_value as _report_rq2_affect_value,
    run_all_research_questions as _run_all_research_questions,
    test_rq3_lesion_dissociation as _test_rq3_lesion_dissociation,
    test_rq4_betrayal_recovery as _test_rq4_betrayal_recovery,
)


def _warn(old: str, new: str) -> None:
    warnings.warn(
        f"analysis.hypotheses.{old} is deprecated; use analysis.research_questions.{new}",
        DeprecationWarning,
        stacklevel=3,
    )


def test_h1_orthogonal_augmentation(results):
    _warn("test_h1_orthogonal_augmentation", "report_rq2_affect_value")
    return _report_rq2_affect_value(results)


def test_h2_depth_matters(results):
    _warn("test_h2_depth_matters", "report_rq1_depth_curve")
    return _report_rq1_depth_curve(results)


def test_h3_lesion_dissociation(results, accuracy_margin: float = 0.05):
    _warn("test_h3_lesion_dissociation", "test_rq3_lesion_dissociation")
    return _test_rq3_lesion_dissociation(results, accuracy_margin=accuracy_margin)


def test_h4_betrayal_recovery(results):
    _warn("test_h4_betrayal_recovery", "test_rq4_betrayal_recovery")
    return _test_rq4_betrayal_recovery(results)


def test_h5_affect_vs_no_affect_post_switch(results):
    _warn(
        "test_h5_affect_vs_no_affect_post_switch",
        "test_rq4_betrayal_recovery (post_switch_payoff_difference field)",
    )
    return _test_rq4_betrayal_recovery(results)


def run_all_hypothesis_tests(results):
    _warn("run_all_hypothesis_tests", "run_all_research_questions")
    return _run_all_research_questions(results)


__all__ = [
    "test_h1_orthogonal_augmentation",
    "test_h2_depth_matters",
    "test_h3_lesion_dissociation",
    "test_h4_betrayal_recovery",
    "test_h5_affect_vs_no_affect_post_switch",
    "run_all_hypothesis_tests",
]
```

Note: `test_h1_depth_compensation` (legacy alias per spec) is NOT re-exported — it was a dead alias.

- [ ] **Step 2: Add a shim test**

```python
def test_hypotheses_shim_emits_deprecation_warning():
    import warnings
    df = _build_minimal_fixture()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        from analysis.hypotheses import test_h3_lesion_dissociation
        test_h3_lesion_dissociation(df)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
```

- [ ] **Step 3: Run all analysis tests to confirm nothing broke**

```bash
pytest tests/test_analysis_semantics.py -v
```

Expected: PASS (some new tests, all old tests via shim).

- [ ] **Step 4: Commit**

```bash
git add analysis/hypotheses.py tests/test_analysis_semantics.py
git commit -m "analysis: convert hypotheses.py to deprecation shim (D phase 1)"
```

### Task 1.10: Update `analysis/__init__.py` to re-export new names

**Files:**
- Modify: `analysis/__init__.py`

- [ ] **Step 1: Read current `__init__.py`**

```bash
cat analysis/__init__.py
```

Currently exports `build_run_gifs` and `load_results`.

- [ ] **Step 2: Add new RQ/E re-exports**

```python
"""Analysis helpers for experiment outputs."""

from analysis.research_questions import (
    report_e1_baseline_competitiveness,
    report_e2_multi_focal_dynamics,
    report_rq1_depth_curve,
    report_rq2_affect_value,
    report_rq6_graded_channel,
    report_rq7_clinical_resolution,
    run_all_research_questions,
    test_rq3_lesion_dissociation,
    test_rq4_betrayal_recovery,
    test_rq5_partner_selection,
)
from analysis.visualization import build_run_gifs, load_results

__all__ = [
    "build_run_gifs",
    "load_results",
    "run_all_research_questions",
    "report_e1_baseline_competitiveness",
    "report_e2_multi_focal_dynamics",
    "report_rq1_depth_curve",
    "report_rq2_affect_value",
    "report_rq6_graded_channel",
    "report_rq7_clinical_resolution",
    "test_rq3_lesion_dissociation",
    "test_rq4_betrayal_recovery",
    "test_rq5_partner_selection",
]
```

- [ ] **Step 3: Commit**

```bash
git add analysis/__init__.py
git commit -m "analysis: re-export research_questions API from package (D phase 1)"
```

### Task 1.11: Update `scripts/run_analysis.py`

**Files:**
- Modify: `scripts/run_analysis.py`

- [ ] **Step 1: Read current run_analysis.py imports + main**

```bash
sed -n '1,50p' scripts/run_analysis.py
grep -n "hypothesis\|hypothes" scripts/run_analysis.py
```

- [ ] **Step 2: Switch import from `analysis.hypotheses` to `analysis.research_questions`**

Replace:
```python
from analysis.hypotheses import run_all_hypothesis_tests
```

With:
```python
from analysis.research_questions import run_all_research_questions
```

- [ ] **Step 3: Rewrite `_hypothesis_summary_frame` to handle the `{questions, engineering}` shape**

The existing function returns a DataFrame keyed by hypothesis. The new shape has two top-level blocks. Either:
- (a) keep `_hypothesis_summary_frame` for compat, internally routing both blocks; rename to `_research_question_summary_frame`
- (b) introduce a new `_research_question_summary_frame` and have `_hypothesis_summary_frame` call it (compat alias for one release)

Pick (b) for cleaner migration. Implementation:

```python
def _research_question_summary_frame(results: dict) -> pd.DataFrame:
    """Flatten {questions: {...}, engineering: {...}} into a single frame."""
    rows = []
    for rq_id, payload in results.get("questions", {}).items():
        rows.append({"id": rq_id, "kind": "question", **_flatten(payload)})
    for e_id, payload in results.get("engineering", {}).items():
        rows.append({"id": e_id, "kind": "engineering", **_flatten(payload)})
    return pd.DataFrame(rows)
```

`_flatten` is a small helper that pulls scalar fields from the nested return dict.

- [ ] **Step 4: Dual-write JSON artifacts during shim period**

```python
results = run_all_research_questions(df)

# new canonical artifacts
out_dir / "research_questions.json".write_text(json.dumps(results["questions"], indent=2))
(out_dir / "engineering_objectives.json").write_text(json.dumps(results["engineering"], indent=2))

# legacy alias (removed in D phase 5)
legacy_payload = {
    **{f"h{i}": v for i, v in zip([1, 2, 3, 4], [
        results["questions"]["rq2"],
        results["questions"]["rq1"],
        results["questions"]["rq3"],
        results["questions"]["rq4"],
    ])},
    "h5": results["questions"]["rq4"],  # h5 was duplicate of h4
}
(out_dir / "hypothesis_tests.json").write_text(json.dumps(legacy_payload, indent=2))
```

- [ ] **Step 5: Run the script end-to-end on a small results CSV**

```bash
# locate or create a tiny sample CSV with required columns
python scripts/run_analysis.py --results <path> --out /tmp/d_phase1_check
ls /tmp/d_phase1_check/
# Expected: research_questions.json, engineering_objectives.json, hypothesis_tests.json
```

- [ ] **Step 6: Commit**

```bash
git add scripts/run_analysis.py
git commit -m "scripts: switch run_analysis to research_questions API; dual-write artifacts (D phase 1)"
```

### Task 1.12: Update `scripts/run_preliminary.py`

**Files:**
- Modify: `scripts/run_preliminary.py`

- [ ] **Step 1: Find and replace import**

```bash
grep -n "hypothesis\|hypothes" scripts/run_preliminary.py
```

Switch any `from analysis.hypotheses import ...` to the matching `analysis.research_questions` import. If `run_all_hypothesis_tests` is called, switch to `run_all_research_questions` and adapt the result-shape unpacking.

- [ ] **Step 2: Run the script smoke test if there's one, otherwise manual exec**

```bash
python scripts/run_preliminary.py --help
```

- [ ] **Step 3: Commit**

```bash
git add scripts/run_preliminary.py
git commit -m "scripts: switch run_preliminary to research_questions API (D phase 1)"
```

### Task 1.13: Audit `cli/common.py` and `experiment/factory.py`

**Files:**
- Inspect: `cli/common.py`, `experiment/factory.py`

- [ ] **Step 1: Search for any references to old config names or hypothesis names**

```bash
grep -n "h1_\|h2_\|h3_\|h4_\|h5_\|hypothesis\|hypothes" cli/common.py experiment/factory.py
```

- [ ] **Step 2: If anything turns up, fix in place; otherwise note "audit clean" in PR description**

- [ ] **Step 3: Commit any changes (or skip)**

### Task 1.14: Phase 1 gate — full pytest run

- [ ] **Step 1: Run the full default pytest suite**

```bash
pytest -x --ignore=tests/test_cvc_*.py
```

Expected: GREEN. The shim should produce `DeprecationWarning`s but no failures. If any failures appear, debug per @superpowers:systematic-debugging.

- [ ] **Step 2: If pytest is green, tag the local commit message with "phase 1 complete"**

```bash
git commit --allow-empty -m "checkpoint: D phase 1 complete (analysis rename + shim + scripts updated)"
```

---

## Phase 2 — Config renames + archive

### Task 2.1: Create `configs/archive/` directory + README

**Files:**
- Create: `configs/archive/README.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p configs/archive
```

- [ ] **Step 2: Write README**

```markdown
# Archived configurations

Read-only directory. Configs here have been superseded by canonical entries in
`configs/` proper. Do not edit files in place; if you need a variant, copy it
back out under a new name and re-add it to `docs/experiment/manifest.md`.

## Why archived

| file | reason |
|---|---|
| `benchmark_default.json` | strict subset of `e1_benchmark_arena.json` (10 reps × 100 rounds) |
| `benchmark_resource_sharing.json` | strict subset of `e1_benchmark_arena.json` (50 reps × 100 rounds) |
| `benchmark_comprehensive.json` | merged into `e1_benchmark_arena.json` (100 reps was canonical) |
| `benchmark_betrayal.json` | merged into `e1_benchmark_betrayal_kitchen_sink.json` (200 rounds, p_switch=0, switch r100 — kitchen-sink covers it) |

History preserved via `git mv` — see `git log --follow configs/archive/<file>` for full evolution.
```

- [ ] **Step 3: Commit**

```bash
git add configs/archive/README.md
git commit -m "configs: create archive directory with read-only policy (D phase 2)"
```

### Task 2.2: Move 4 archived configs

**Files:**
- Rename: 4 configs to `configs/archive/`

- [ ] **Step 1: git mv each**

```bash
git mv configs/benchmark_default.json configs/archive/benchmark_default.json
git mv configs/benchmark_resource_sharing.json configs/archive/benchmark_resource_sharing.json
git mv configs/benchmark_comprehensive.json configs/archive/benchmark_comprehensive.json
git mv configs/benchmark_betrayal.json configs/archive/benchmark_betrayal.json
```

- [ ] **Step 2: Verify history preserved**

```bash
git log --follow configs/archive/benchmark_default.json | head -n 5
```

Expected: shows commits from before the move.

- [ ] **Step 3: Commit**

```bash
git commit -m "configs: archive 4 superseded configs (D phase 2)"
```

### Task 2.3: Rename 17 configs to RQ/E/smoke naming

**Files:**
- Rename: 17 configs

- [ ] **Step 1: git mv each (paste as a block)**

```bash
git mv configs/smoke_test.json configs/smoke_focal.json
git mv configs/multifocal_smoke.json configs/smoke_multifocal.json
git mv configs/h1_depth_affect_factorial.json configs/rq1_depth_factorial.json
git mv configs/shallow_affect_confirm.json configs/rq2_shallow_affect.json
git mv configs/h2_lesion_dissociation.json configs/rq3_lesion_dissociation.json
git mv configs/h4_betrayal_recovery.json configs/rq4_betrayal_recovery.json
git mv configs/h5_partner_selection.json configs/rq5_partner_selection.json
git mv configs/graded_trust_factorial.json configs/rq6_graded_factorial.json
git mv configs/graded_betrayal.json configs/rq6_graded_betrayal.json
git mv configs/clinical_betrayal.json configs/rq7_clinical_betrayal.json
git mv configs/clinical_phenotypes.json configs/rq7_clinical_phenotypes.json
git mv configs/sensitivity_affect_params.json configs/rq7_sensitivity_sweep.json
git mv configs/benchmark_betrayal_fair.json configs/e1_benchmark_betrayal_fair.json
git mv configs/benchmark_betrayal_comprehensive.json configs/e1_benchmark_betrayal_kitchen_sink.json
git mv configs/benchmark_noisy.json configs/e1_benchmark_noisy.json
git mv configs/multifocal_homogeneous_affective.json configs/e2_multifocal_homogeneous.json
git mv configs/multifocal_clinical_mix.json configs/e2_multifocal_clinical_mix.json
git mv configs/multifocal_assortative_choice.json configs/e2_multifocal_assortative.json
```

- [ ] **Step 2: Verify all 17 moves succeeded**

```bash
git status | grep renamed | wc -l
# Expected: 17
ls configs/*.json | sort
# Expected: 18 files (17 renamed + 1 still-to-do merge target)
```

- [ ] **Step 3: Commit**

```bash
git commit -m "configs: rename 17 configs to rq#/e#/smoke naming (D phase 2)"
```

### Task 2.4: Merge `benchmark_full` + `benchmark_comprehensive` → `e1_benchmark_arena`

**Files:**
- Modify/Rename: `benchmark_full.json` → `e1_benchmark_arena.json`

- [ ] **Step 1: Verify the diff between benchmark_full and benchmark_comprehensive (already archived)**

```bash
diff configs/benchmark_full.json configs/archive/benchmark_comprehensive.json
```

Expected: identical except `num_replications` (100 vs 50). Per spec, take `benchmark_full`'s 100 reps as canonical.

- [ ] **Step 2: git mv benchmark_full to e1_benchmark_arena**

```bash
git mv configs/benchmark_full.json configs/e1_benchmark_arena.json
```

- [ ] **Step 3: Commit**

```bash
git commit -m "configs: merge benchmark_full+benchmark_comprehensive into e1_benchmark_arena (D phase 2)"
```

### Task 2.5: Run smoke configs end-to-end

**Files:**
- Read: `configs/smoke_focal.json`, `configs/smoke_multifocal.json`

- [ ] **Step 1: Run smoke_focal**

```bash
python scripts/run_experiment.py --config configs/smoke_focal.json --out /tmp/d_phase2_smoke_focal
ls /tmp/d_phase2_smoke_focal/
```

Expected: results.csv produced.

- [ ] **Step 2: Run smoke_multifocal**

```bash
python scripts/run_experiment.py --config configs/smoke_multifocal.json --out /tmp/d_phase2_smoke_multifocal
ls /tmp/d_phase2_smoke_multifocal/
```

Expected: results.csv produced.

- [ ] **Step 3: If both green, commit empty marker; if either fails, debug**

```bash
git commit --allow-empty -m "checkpoint: D phase 2 complete (smoke configs green, 17 renamed, 4 archived, 1 merged)"
```

---

## Phase 3 — New metrics + new RQ/E function bodies

### Task 3.0: (Conditional) Extend logger.py for `mu_realized`

**Files:**
- Modify (if needed): `experiment/logger.py`

Per Task 0.1 audit. Skip this task if `mu_realized` is already in the logger.

- [ ] **Step 1: Add `mu_realized` to the record dict**

```python
"mu_realized": float(agent_metrics.get("mu_realized", 0.0)),
```

- [ ] **Step 2: Ensure agents emit `mu_realized` in their `agent_metrics` dict**

Check `experiment/runner.py` or wherever agent_metrics is assembled. Add `mu_realized` from the agent's affect module state.

- [ ] **Step 3: Add a logger schema test**

```python
def test_logger_includes_mu_realized():
    from experiment.logger import MetricLogger
    logger = MetricLogger(num_rounds=1, num_partners=2)
    logger.log_round(
        round_idx=0, condition="test", seed=0,
        agent_metrics={"q_pi_entropy": 0.5, "q_pi": [0.5, 0.5], "mu_realized": 0.3, ...},
        env_result={...},
    )
    df = logger.to_dataframe()
    assert "mu_realized" in df.columns
```

- [ ] **Step 4: Run, commit**

```bash
pytest tests/test_logger_schema.py -v
git add experiment/logger.py experiment/runner.py tests/test_logger_schema.py
git commit -m "logger: add mu_realized column for RQ6 metric (D phase 3)"
```

### Task 3.1: Add `partner_selection_summary` metric

**Files:**
- Modify: `analysis/metrics.py`
- Modify: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Write failing test first (TDD)**

```python
def test_partner_selection_summary_returns_per_seed_stats():
    from analysis.metrics import partner_selection_summary
    df = pd.DataFrame({
        "seed": [0]*10 + [1]*10,
        "partner_idx": [0,0,0,1,1,1,2,2,2,0]*2,
        "agent_action": [1]*20,
        "beta_estimate": [0.5,0.5,0.5,1.0,1.0,1.0,1.5,1.5,1.5,0.5]*2,
    })
    result = partner_selection_summary(df)
    assert "per_seed_choice_counts" in result
    assert "beta_choice_correlation" in result
    assert "choice_entropy" in result
```

- [ ] **Step 2: Run test, see it fail**

```bash
pytest tests/test_analysis_semantics.py::test_partner_selection_summary_returns_per_seed_stats -v
```

Expected: FAIL (`partner_selection_summary` not defined).

- [ ] **Step 3: Implement metric in `analysis/metrics.py`**

```python
def partner_selection_summary(results: pd.DataFrame) -> dict:
    """Per-seed partner-choice statistics for RQ5.

    Args:
        results: must contain columns ``seed``, ``partner_idx``, ``beta_estimate`` (optional).

    Returns:
        {
            "per_seed_choice_counts": dict[seed -> dict[partner_idx -> count]],
            "beta_choice_correlation": float (Spearman rho across all seeds, NaN if no beta col),
            "choice_entropy": dict[seed -> float (Shannon entropy bits)],
        }
    """
    per_seed_counts = (
        results.groupby(["seed", "partner_idx"])
        .size()
        .unstack(fill_value=0)
        .to_dict(orient="index")
    )

    choice_entropy = {}
    for seed, counts in per_seed_counts.items():
        total = sum(counts.values())
        if total == 0:
            choice_entropy[seed] = 0.0
            continue
        probs = np.array([c / total for c in counts.values()])
        probs = probs[probs > 0]
        choice_entropy[seed] = float(-np.sum(probs * np.log2(probs)))

    if "beta_estimate" in results.columns:
        # beta-choice correlation: per-partner mean beta vs choice frequency
        per_partner = results.groupby("partner_idx").agg(
            mean_beta=("beta_estimate", "mean"),
            choice_count=("seed", "size"),
        )
        from scipy.stats import spearmanr
        rho, _ = spearmanr(per_partner["mean_beta"], per_partner["choice_count"])
        beta_choice_corr = float(rho) if not np.isnan(rho) else None
    else:
        beta_choice_corr = None

    return {
        "per_seed_choice_counts": per_seed_counts,
        "beta_choice_correlation": beta_choice_corr,
        "choice_entropy": choice_entropy,
    }
```

- [ ] **Step 4: Re-run test**

```bash
pytest tests/test_analysis_semantics.py::test_partner_selection_summary_returns_per_seed_stats -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add analysis/metrics.py tests/test_analysis_semantics.py
git commit -m "metrics: add partner_selection_summary for RQ5 (D phase 3)"
```

### Task 3.2: Add `q_pi_entropy_summary` metric

**Files:**
- Modify: `analysis/metrics.py`
- Modify: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Write failing test (TDD)**

```python
def test_q_pi_entropy_summary_returns_per_condition_distribution():
    from analysis.metrics import q_pi_entropy_summary
    df = pd.DataFrame({
        "condition": ["affect"]*10 + ["no_affect"]*10,
        "q_pi_entropy": [0.5]*5 + [0.7]*5 + [0.3]*5 + [0.4]*5,
    })
    result = q_pi_entropy_summary(df)
    assert "affect" in result
    assert "mean" in result["affect"]
    assert "p25" in result["affect"]
    assert "p75" in result["affect"]
```

- [ ] **Step 2: Implement**

```python
def q_pi_entropy_summary(results: pd.DataFrame) -> dict:
    """Per-condition q_pi entropy distribution for RQ6.

    Args:
        results: must contain ``condition`` and ``q_pi_entropy`` columns.

    Returns:
        {condition -> {"mean": float, "p25": float, "p75": float, "n": int}}
    """
    if "q_pi_entropy" not in results.columns:
        return {}
    grouped = results.groupby("condition")["q_pi_entropy"]
    return {
        str(name): {
            "mean": float(group.mean()),
            "p25": float(group.quantile(0.25)),
            "p75": float(group.quantile(0.75)),
            "n": int(group.size),
        }
        for name, group in grouped
    }
```

- [ ] **Step 3: Run, commit**

```bash
pytest tests/test_analysis_semantics.py::test_q_pi_entropy_summary_returns_per_condition_distribution -v
git add analysis/metrics.py tests/test_analysis_semantics.py
git commit -m "metrics: add q_pi_entropy_summary for RQ6 (D phase 3)"
```

### Task 3.3: Add `mu_realized_summary` metric

Same TDD shape as 3.2. Inputs: `condition`, `mu_realized` columns. Outputs: per-condition mean realized mu + calibration delta vs configured.

- [ ] **Step 1: Test, implement, commit per the established pattern**

```bash
git commit -m "metrics: add mu_realized_summary for RQ6 (D phase 3)"
```

### Task 3.4: Add `clinical_vs_baseline_pairwise` metric

Inputs: `condition` (preset names like `alexithymia`, `borderline`, `depression`, `healthy`), `payoff_mode`, `scenario`, `payoff`. Outputs: structured pairwise contrast with Cohen's d for clinical-vs-healthy and between-clinical, broken out by `payoff_mode × scenario`.

- [ ] **Step 1: Test, implement, commit**

```bash
git commit -m "metrics: add clinical_vs_baseline_pairwise for RQ7 (D phase 3)"
```

### Task 3.5: Add `baseline_rank_summary` metric

Inputs: results df from benchmark configs. Outputs: per-scenario agent ranking by mean payoff with bootstrap CI (95%, 1000 resamples); pairwise win-rate matrix (NxN, where N = number of agents in scenario).

- [ ] **Step 1: Test, implement, commit**

```bash
git commit -m "metrics: add baseline_rank_summary for E1 (D phase 3)"
```

### Task 3.6: Add `multi_focal_emergence_metrics` metric

Inputs: per-agent per-round multifocal results. Outputs: per-round per-agent cooperation rate, type-distribution drift, pairing transition matrix (when agent_choice mode), cooperation-cascade detection (heuristic: count of round windows where all-pairs cooperation rate ≥ threshold).

- [ ] **Step 1: Test, implement, commit**

```bash
git commit -m "metrics: add multi_focal_emergence_metrics for E2 (D phase 3)"
```

### Task 3.7: Implement `test_rq5_partner_selection` (replace stub)

**Files:**
- Modify: `analysis/research_questions.py`
- Modify: `tests/test_analysis_semantics.py`

- [ ] **Step 1: Replace stub with full implementation using `partner_selection_summary`**

```python
def test_rq5_partner_selection(results: pd.DataFrame) -> dict:
    """RQ5 — do affect-guided agents preferentially select well-modeled partners?"""
    from analysis.metrics import partner_selection_summary

    # filter to agent_choice runs only
    if "partner_idx" not in results.columns:
        return {"available": False, "research_question": "rq5", "reason": "no partner_idx column"}

    affect_df = results[results["condition"].str.contains("affect", na=False, regex=False)]
    no_affect_df = results[results["condition"].str.contains("no_affect", na=False, regex=False)]

    affect_summary = partner_selection_summary(affect_df)
    no_affect_summary = partner_selection_summary(no_affect_df)

    # predicate: affect should show non-uniform partner choice (lower entropy than no_affect)
    affect_mean_entropy = float(np.mean(list(affect_summary.get("choice_entropy", {}).values()) or [0]))
    no_affect_mean_entropy = float(np.mean(list(no_affect_summary.get("choice_entropy", {}).values()) or [0]))
    supported = affect_mean_entropy < no_affect_mean_entropy

    return {
        "available": True,
        "research_question": "rq5",
        "supported": supported,
        "evidence": {
            "affect_mean_entropy": affect_mean_entropy,
            "no_affect_mean_entropy": no_affect_mean_entropy,
            "affect_beta_choice_corr": affect_summary.get("beta_choice_correlation"),
        },
    }
```

- [ ] **Step 2: Update unit test**

Replace the `assert result["available"] is False` style test with:

```python
def test_test_rq5_partner_selection_returns_supported_field():
    from analysis.research_questions import test_rq5_partner_selection
    df = _build_partner_selection_fixture()  # need to add this fixture
    result = test_rq5_partner_selection(df)
    assert result["available"] is True
    assert "supported" in result
    assert "evidence" in result
```

- [ ] **Step 3: Run, commit**

```bash
pytest tests/test_analysis_semantics.py::test_test_rq5_partner_selection_returns_supported_field -v
git add analysis/research_questions.py tests/test_analysis_semantics.py
git commit -m "analysis: implement test_rq5_partner_selection (D phase 3)"
```

### Task 3.8: Implement `report_rq6_graded_channel`

Use `q_pi_entropy_summary` and `mu_realized_summary` plus an affect-vs-no-affect delta computation against RQ2's framework.

- [ ] **Step 1: Test, implement, commit**

```bash
git commit -m "analysis: implement report_rq6_graded_channel (D phase 3)"
```

### Task 3.9: Implement `report_rq7_clinical_resolution`

Use `clinical_vs_baseline_pairwise`. Output structure follows the descriptive `report_*` convention.

- [ ] **Step 1: Test, implement, commit**

```bash
git commit -m "analysis: implement report_rq7_clinical_resolution (D phase 3)"
```

### Task 3.10: Implement `report_e1_baseline_competitiveness`

Use `baseline_rank_summary`.

- [ ] **Step 1: Test, implement, commit**

```bash
git commit -m "analysis: implement report_e1_baseline_competitiveness (D phase 3)"
```

### Task 3.11: Implement `report_e2_multi_focal_dynamics`

Use `multi_focal_emergence_metrics`.

- [ ] **Step 1: Test, implement, commit**

```bash
git commit -m "analysis: implement report_e2_multi_focal_dynamics (D phase 3)"
```

### Task 3.12: Phase 3 gate — full pytest

- [ ] **Step 1: Run full pytest**

```bash
pytest -x --ignore=tests/test_cvc_*.py
```

Expected: GREEN.

- [ ] **Step 2: Tag checkpoint**

```bash
git commit --allow-empty -m "checkpoint: D phase 3 complete (6 metrics + 5 RQ/E functions live)"
```

---

## Phase 4 — Manifest + validator

### Task 4.1: Write `docs/experiment/manifest.md`

**Files:**
- Create: `docs/experiment/manifest.md`

- [ ] **Step 1: Write the manifest with all 7 RQs + 2 Es per spec section 4 schema**

Each entry follows the schema:

```markdown
### RQ1 — role of planning depth

**Question**: how does explicit planning depth affect performance across binary and graded payoff regimes — does deeper help, saturate, or interact with affect?

**Configs**:
- `configs/rq1_depth_factorial.json` — multi-tau factorial across affect / no_affect / lesioned — status: needs_rerun

**Analysis**: `analysis.research_questions.report_rq1_depth_curve` → `rq1_depth_curve.json`

**Last run**: never (post-restructure)

**Open blockers**: none
```

Write all 7 RQs and 2 Es. All status fields start as `needs_rerun`.

- [ ] **Step 2: Add a "How to use this document" preamble**

```markdown
# Experiment manifest

This document is the **single source of truth** for the mapping between configs,
research questions / engineering objectives, and analysis functions. Every active
config (excluding `configs/archive/` and `configs/benchmark_cvc_*.json`) appears
in exactly one entry. Every RQ/E has at least one config and exactly one analysis
function.

**Drift prevention**: `tests/test_manifest_consistency.py` runs in CI and asserts:
1. every active config is referenced from at least one entry
2. every entry's config references resolve on disk
3. every analysis function in `analysis.research_questions.run_all_research_questions` is referenced
4. every entry's analysis reference is callable

If you add or rename a config, update this manifest in the same commit.
```

- [ ] **Step 3: Commit**

```bash
git add docs/experiment/manifest.md
git commit -m "docs: add experiment manifest as single source of truth (D phase 4)"
```

### Task 4.2: Implement `analysis/_manifest.py` parser

**Files:**
- Create: `analysis/_manifest.py`

- [ ] **Step 1: Implement minimal markdown parser**

```python
"""Minimal markdown parser for docs/experiment/manifest.md.

Parses the per-entry structure documented in
``docs/superpowers/specs/2026-04-18-experiment-pruning-design.md`` section 4.

Exposes a single function ``parse_manifest(path)`` returning a list of entries:
    [{"id": "rq1", "configs": [...], "analysis": "module.fn", "status": "needs_rerun"}, ...]

stdlib only — no external markdown dep.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict


class ManifestEntry(TypedDict):
    id: str
    kind: str  # "question" | "engineering"
    configs: list[str]
    analysis: str
    last_run: str
    blockers: list[str]


_HEADING_RE = re.compile(r"^### (RQ\d+|E\d+)\b", re.MULTILINE)
_CONFIG_RE = re.compile(r"^- `(configs/[^`]+\.json)`", re.MULTILINE)
_ANALYSIS_RE = re.compile(r"\*\*Analysis\*\*: `([^`]+)`")
_LAST_RUN_RE = re.compile(r"\*\*Last run\*\*: ([^\n]+)")


def parse_manifest(path: Path) -> list[ManifestEntry]:
    text = Path(path).read_text(encoding="utf-8")
    headings = list(_HEADING_RE.finditer(text))
    entries = []
    for i, match in enumerate(headings):
        section_id = match.group(1).lower()
        section_start = match.end()
        section_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        section = text[section_start:section_end]

        configs = _CONFIG_RE.findall(section)
        analysis_match = _ANALYSIS_RE.search(section)
        last_run_match = _LAST_RUN_RE.search(section)

        entries.append(ManifestEntry(
            id=section_id,
            kind="engineering" if section_id.startswith("e") else "question",
            configs=configs,
            analysis=analysis_match.group(1) if analysis_match else "",
            last_run=last_run_match.group(1).strip() if last_run_match else "",
            blockers=[],
        ))
    return entries
```

- [ ] **Step 2: Unit test for the parser**

```python
def test_parse_manifest_round_trips_known_entries():
    from analysis._manifest import parse_manifest
    entries = parse_manifest("docs/experiment/manifest.md")
    ids = {e["id"] for e in entries}
    assert ids >= {"rq1", "rq2", "rq3", "rq4", "rq5", "rq6", "rq7", "e1", "e2"}
    rq1 = next(e for e in entries if e["id"] == "rq1")
    assert any("rq1_depth_factorial.json" in c for c in rq1["configs"])
    assert "report_rq1_depth_curve" in rq1["analysis"]
```

- [ ] **Step 3: Run, commit**

```bash
pytest tests/test_manifest_consistency.py::test_parse_manifest_round_trips_known_entries -v
git add analysis/_manifest.py tests/test_manifest_consistency.py
git commit -m "analysis: add _manifest.py parser (D phase 4)"
```

### Task 4.3: Implement `tests/test_manifest_consistency.py` validator

**Files:**
- Create: `tests/test_manifest_consistency.py`

- [ ] **Step 1: Write the four assertions from spec section 4**

```python
"""Manifest consistency validator.

Asserts:
1. every active config appears in some manifest entry
2. every manifest config-reference resolves on disk
3. every RQ/E function in run_all_research_questions is referenced
4. every manifest analysis-reference is callable
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from analysis._manifest import parse_manifest

MANIFEST_PATH = Path("docs/experiment/manifest.md")
CONFIGS_DIR = Path("configs")


def _active_configs() -> set[str]:
    """All configs/*.json excluding archive/ and benchmark_cvc_*."""
    return {
        f"configs/{p.name}"
        for p in CONFIGS_DIR.glob("*.json")
        if not p.name.startswith("benchmark_cvc_")
    }


def _resolve_callable(dotted: str):
    module_path, _, name = dotted.rpartition(".")
    module = importlib.import_module(module_path)
    return getattr(module, name)


@pytest.fixture(scope="module")
def entries():
    return parse_manifest(MANIFEST_PATH)


def test_every_active_config_referenced(entries):
    referenced = set()
    for e in entries:
        referenced.update(e["configs"])
    active = _active_configs()
    missing = active - referenced
    assert not missing, f"configs not referenced by any manifest entry: {sorted(missing)}"


def test_every_manifest_config_reference_resolves(entries):
    for e in entries:
        for cfg in e["configs"]:
            assert Path(cfg).exists(), f"manifest entry {e['id']} references missing config {cfg}"


def test_every_orchestrator_function_referenced(entries):
    from analysis.research_questions import (
        report_e1_baseline_competitiveness,
        report_e2_multi_focal_dynamics,
        report_rq1_depth_curve,
        report_rq2_affect_value,
        report_rq6_graded_channel,
        report_rq7_clinical_resolution,
        test_rq3_lesion_dissociation,
        test_rq4_betrayal_recovery,
        test_rq5_partner_selection,
    )
    expected_functions = {
        f"analysis.research_questions.{fn.__name__}"
        for fn in [
            report_rq1_depth_curve, report_rq2_affect_value,
            test_rq3_lesion_dissociation, test_rq4_betrayal_recovery,
            test_rq5_partner_selection, report_rq6_graded_channel,
            report_rq7_clinical_resolution, report_e1_baseline_competitiveness,
            report_e2_multi_focal_dynamics,
        ]
    }
    referenced = {e["analysis"] for e in entries}
    missing = expected_functions - referenced
    assert not missing, f"functions not referenced by manifest: {sorted(missing)}"


def test_every_manifest_analysis_reference_callable(entries):
    for e in entries:
        if not e["analysis"]:
            continue
        try:
            fn = _resolve_callable(e["analysis"])
        except (ImportError, AttributeError) as exc:
            pytest.fail(f"manifest entry {e['id']} references uncallable {e['analysis']}: {exc}")
        assert callable(fn)
```

- [ ] **Step 2: Run all four asserts**

```bash
pytest tests/test_manifest_consistency.py -v
```

Expected: ALL PASS. If any fail, fix the manifest or the analysis module to align.

- [ ] **Step 3: Commit**

```bash
git add tests/test_manifest_consistency.py
git commit -m "tests: add manifest consistency validator (D phase 4)"
```

### Task 4.4: Update `conductor/STATE.md`

**Files:**
- Modify: `conductor/STATE.md`

- [ ] **Step 1: Read current STATE.md**

```bash
cat conductor/STATE.md
```

- [ ] **Step 2: Update `pending_work` and `next_session_focus` per spec section 4**

Apply the diff from spec section 4:

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

Note: `next_priority`, `model_hint`, `mode_hint` unchanged.

- [ ] **Step 3: Commit**

```bash
git add conductor/STATE.md
git commit -m "conductor: update STATE for post-D rerun sequencing (D phase 4)"
```

### Task 4.5: Phase 4 final pytest gate

- [ ] **Step 1: Run full pytest**

```bash
pytest --ignore=tests/test_cvc_*.py
```

Expected: GREEN. Includes the new manifest validator.

- [ ] **Step 2: Run smoke configs one more time**

```bash
python scripts/run_experiment.py --config configs/smoke_focal.json --out /tmp/d_final_smoke
python scripts/run_experiment.py --config configs/smoke_multifocal.json --out /tmp/d_final_smoke_mf
```

Expected: Both produce `results.csv`.

- [ ] **Step 3: Tag final commit**

```bash
git commit --allow-empty -m "checkpoint: D phases 1-4 complete; ready for PR"
```

---

## Phase 5 — Shim removal (DEFERRED, separate PR after one release cycle)

**Do NOT include in the same PR as phases 1–4.** Open a follow-up issue / branch when one release has elapsed.

### Task 5.1: Delete `analysis/hypotheses.py`

```bash
git rm analysis/hypotheses.py
```

### Task 5.2: Remove `hypothesis_tests.json` alias write from `scripts/run_analysis.py`

Drop the legacy alias block.

### Task 5.3: Remove deprecated re-exports from `analysis/__init__.py`

If any old `test_h*` names linger, drop them.

### Task 5.4: Run full pytest, ensure no breakage

```bash
pytest --ignore=tests/test_cvc_*.py
```

### Task 5.5: Commit

```bash
git commit -m "analysis: remove hypotheses.py shim (D phase 5)"
```

---

## Acceptance criteria checklist

Tick on the final PR description before merging:

- [ ] all 17 config renames + 2 merges + 4 archives applied with `git mv` history preserved
- [ ] `configs/archive/README.md` exists with read-only policy
- [ ] `analysis/research_questions.py` exists with 7 RQ functions + 2 E functions
- [ ] each new function has at least one unit test in `tests/test_analysis_semantics.py`
- [ ] `analysis/hypotheses.py` is a deprecation shim re-exporting old names with `DeprecationWarning`
- [ ] `scripts/run_analysis.py` produces `research_questions.json` + `engineering_objectives.json` and (during shim period) `hypothesis_tests.json` alias
- [ ] `analysis/metrics.py` contains all 6 new metric functions, each with a unit test
- [ ] `experiment/logger.py` schema includes `q_pi_entropy` (already), `q_pi` (already), and `mu_realized` (added if needed)
- [ ] `docs/experiment/manifest.md` exists; every active config (excluding cvc) and every RQ/E function is referenced
- [ ] `tests/test_manifest_consistency.py` passes (4 asserts)
- [ ] full default `pytest` green; no `slow`-marked test added by D
- [ ] `conductor/STATE.md` updated with new pending_work block
- [ ] `smoke_focal.json` and `smoke_multifocal.json` run end-to-end on the final commit

---

## Verification before completion (per @superpowers:verification-before-completion)

Run these locally before opening the PR:

```bash
# tests
pytest --ignore=tests/test_cvc_*.py

# manifest validator (specifically)
pytest tests/test_manifest_consistency.py -v

# smoke configs
python scripts/run_experiment.py --config configs/smoke_focal.json --out /tmp/d_final_focal
python scripts/run_experiment.py --config configs/smoke_multifocal.json --out /tmp/d_final_mf

# analysis pipeline end-to-end
python scripts/run_analysis.py --results /tmp/d_final_focal/results.csv --out /tmp/d_final_analysis
ls /tmp/d_final_analysis/
# Expected files: research_questions.json, engineering_objectives.json, hypothesis_tests.json
```

All four checks must pass. Paste output into the PR description.
