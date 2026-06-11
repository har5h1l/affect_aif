# Data Collection Runtime Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `profile = "data_collection"` a lean manuscript-facing result contract, keep bulky internals in `debug`, clean the experiment-running mechanism, and produce a measured B/C optimization audit.

**Architecture:** Keep the scientific runtime unchanged. Add an explicit logging-profile boundary at `MetricLogger`, pass the existing runtime profile from `ExperimentRunner`, and centralize row-contract knowledge in tests/docs instead of scattering ad hoc column expectations.

**Tech Stack:** Python, pandas, NumPy/JAX arrays, official `inferactively-pymdp==1.0.0`, pytest, TOML experiment specs.

---

## File Structure

- Modify `experiments/trust/logger.py`: define data-collection vs debug diagnostic columns and keep row construction readable.
- Modify `experiments/trust/runner.py`: pass `RuntimeSpec.profile` into `MetricLogger`; avoid computing debug-only snapshots when the lean contract does not need them.
- Modify `experiments/trust/spec.py` if needed: keep profile parsing strict and ensure `debug` enables diagnostic logging consistently.
- Modify `tests/test_experiment_e2e_lightweight.py`: add focused row-contract tests.
- Modify `tests/test_integration.py` or `tests/test_native_runner_surface.py`: guard deterministic manuscript-facing behavior and debug internals.
- Modify `docs/experiments/running.md`, `docs/experiments/configs.md`, and `scripts/README.md`: document public-facing profile semantics.
- Create `docs/results/runtime_optimization_audit_20260611.md`: measured B/C candidate report with timing, risk tier, expected validation, and recommendation.

## Task 1: Lock the Data-Collection Row Contract

**Files:**
- Modify: `tests/test_experiment_e2e_lightweight.py`
- Modify: `tests/test_integration.py`

- [ ] **Step 1: Write failing tests for lean data_collection rows**
  - Add a test that runs a tiny data-collection spec and asserts manuscript-facing columns exist.
  - Assert debug-only nested fields are absent or empty in `data_collection`: full `q_pi`, `G`, `best_policy_step_costs`, full partner beliefs/posteriors.

- [ ] **Step 2: Write failing tests for debug rows**
  - Add a test that runs the same tiny spec with `runtime.profile = "debug"` and asserts the diagnostic internals are present.

- [ ] **Step 3: Verify RED**
  - Run: `.venv/bin/python -m pytest tests/test_experiment_e2e_lightweight.py tests/test_integration.py -q`
  - Expected: new tests fail because `data_collection` still logs debug-shaped internals and/or `MetricLogger` is not profile-aware.

## Task 2: Implement Profile-Aware Logging

**Files:**
- Modify: `experiments/trust/logger.py`
- Modify: `experiments/trust/runner.py`
- Modify: `experiments/trust/spec.py` only if existing profile/debug wiring is insufficient

- [ ] **Step 1: Pass profile into `MetricLogger`**
  - Extend `MetricLogger.__init__` with `runtime_profile: str = "data_collection"`.
  - Construct it from `config.runtime_profile` or an equivalent value passed through `ExperimentRunner`.

- [ ] **Step 2: Split manuscript fields from debug fields**
  - Keep scalar manuscript fields and required vectors in every row.
  - Gate full `q_pi`, `G`, policy-step arrays, and full nested belief/posterior matrices behind debug.

- [ ] **Step 3: Avoid debug-only snapshot work when possible**
  - Preserve required inferred type/stance correctness and beta/surprise fields.
  - Do not compute or serialize full diagnostic matrices in data collection unless required by manuscript analysis.

- [ ] **Step 4: Verify GREEN**
  - Run the focused tests from Task 1.
  - Expected: row-contract and debug-contract tests pass.

## Task 3: Keep the Experiment Runner Public-Clean

**Files:**
- Modify: `experiments/trust/logger.py`
- Modify: `experiments/trust/runner.py`
- Modify: `scripts/experiment/run.py` only if naming or profile docs need support

- [ ] **Step 1: Refactor names and helpers for clarity**
  - Extract small helpers for profile checks or field inclusion.
  - Keep `MetricLogger.log_round()` readable; avoid growing a junk-drawer conditional block.

- [ ] **Step 2: Run focused cleanup verification**
  - Run: `.venv/bin/python -m ruff check experiments/trust/logger.py experiments/trust/runner.py scripts/experiment/run.py tests/test_experiment_e2e_lightweight.py tests/test_integration.py`
  - Expected: no lint errors.

## Task 4: Verify Paper Analysis Completeness

**Files:**
- Modify: tests as needed
- No production changes unless an analysis dependency is genuinely missing

- [ ] **Step 1: Run configured-analysis replay on lean output**
  - Use a tiny temp output from a maintained/demo-style config.
  - Run configured analysis or phenotype artifact code against the lean output.

- [ ] **Step 2: Add or update tests for paper-required columns**
  - Make the required column set explicit in a test helper.
  - Include notebook summary columns: payoff, `q_pi_entropy`, `round_log_evidence`.

- [ ] **Step 3: Run analysis-focused tests**
  - Run: `.venv/bin/python -m pytest tests/test_analysis_semantics.py tests/test_analysis_configured_dispatch.py tests/test_followup_phenotype_scripts.py -q`
  - Expected: pass.

## Task 5: Measure and Report B/C Candidates

**Files:**
- Create: `docs/results/runtime_optimization_audit_20260611.md`
- Optionally create temporary benchmark output under `/tmp`, not in repo

- [ ] **Step 1: Measure current representative runtime**
  - Run small representative commands before/after the exact logging change.
  - Capture wall time, row count, CSV size, and output-column shape.

- [ ] **Step 2: Inspect deeper candidate classes**
  - Evaluate checkpoint I/O, static template caching, snapshot conversion cost, process-pool overhead, and deeper JAX/vectorization possibilities.
  - Classify each as `exact`, `analysis-equivalent`, or `near-equivalent`.

- [ ] **Step 3: Write the audit report**
  - Include measured speedup from shipped exact changes.
  - Include estimated or measured speed potential for B/C candidates.
  - Include validation required before adoption.

## Task 6: Update Public-Facing Docs

**Files:**
- Modify: `docs/experiments/running.md`
- Modify: `docs/experiments/configs.md`
- Modify: `scripts/README.md`

- [ ] **Step 1: Document profile semantics**
  - `data_collection`: manuscript-facing row contract, fast trajectory collection.
  - `debug`: full diagnostic internals and policy/belief arrays.

- [ ] **Step 2: Document the audit**
  - Link `docs/results/runtime_optimization_audit_20260611.md` from the relevant experiment-running docs if appropriate.

- [ ] **Step 3: Run docs checks**
  - Run: `git diff --check`
  - Expected: pass.

## Task 7: Final Verification

**Files:**
- All changed files

- [ ] **Step 1: Run focused tests**
  - `.venv/bin/python -m pytest tests/test_experiment_e2e_lightweight.py tests/test_integration.py tests/test_analysis_semantics.py tests/test_analysis_configured_dispatch.py tests/test_followup_phenotype_scripts.py -q`

- [ ] **Step 2: Run active verification gate if feasible**
  - `.venv/bin/python -m pytest tests/ -q`
  - `.venv/bin/python -m ruff check .`
  - `.venv/bin/python -m mypy`
  - `git diff --check`

- [ ] **Step 3: Refresh Graphify after code structure changes**
  - `$(cat graphify-out/.graphify_python 2>/dev/null || printf python3) -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"`

- [ ] **Step 4: Report evidence**
  - Summarize exact optimizations shipped.
  - Summarize cleanup done for public-facing clarity.
  - Summarize B/C audit candidates, measured/estimated speedup, risk, and validation requirements.
