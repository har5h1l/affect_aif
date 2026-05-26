# Global Beta Locality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a global-beta affect ablation and a locality/interference diagnostic for the trust-task manuscript.

**Architecture:** Reuse the existing `DiscreteBetaState` update law, but allow one shared beta entity to drive all partner policies. Keep partner-local POMDP beliefs unchanged. Add analysis that compares changed-partner and untouched-partner behavior before and after scheduled stance switches.

**Tech Stack:** Python, TOML experiment specs, official `inferactively-pymdp==1.0.0`, pandas analysis scripts, pytest.

---

### Files

- Modify: `experiments/trust/spec.py`
  Add `global_beta` to the valid affect values.
- Modify: `experiments/trust/factory.py`
  Instantiate a shared one-entity beta tracker for `global_beta`.
- Modify: `tasks/trust/runtime.py`
  Route gamma lookup and beta update through entity `0` for `global_beta`.
- Modify: `experiments/trust/runner.py`
  Log `global_beta`, `local_betas`, and `gamma_used`.
- Modify: `experiments/trust/logger.py`
  Persist the new scalar/vector fields in CSV-safe form.
- Create: `configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml`
  Small seed smoke config for no affect, local precision, tracked-only, and global beta.
- Create: `analysis/interference.py`
  Cross-partner interference summaries.
- Modify: `scripts/analysis/analyze.py`
  Write interference outputs when scheduled stance switches are present.
- Create: `scripts/analysis/make_paper_figures.py`
  Regenerate manuscript figures from canonical CSV/source tables.
- Test: add or extend tests under `tests/` for spec parsing, runtime gamma routing, logging, and analysis outputs.
- Docs: update `docs/design/implementation.md`, `docs/experiment/design.md`, and `docs/paper/manuscript/next_research_plan.md`.

### Task 1: Spec Surface

- [ ] **Step 1: Add failing spec parser test**

Create or update a test that parses a variant with:

```toml
[[variants]]
id = "global_beta"
affect = "global_beta"
planning_horizon = 2
epistemic_value = true
```

Expected: `ExperimentSpec.from_file(...)` accepts the variant and expanded runs preserve `variant.affect == "global_beta"`.

- [ ] **Step 2: Run the targeted test**

Run:

```bash
.venv/bin/python -m pytest tests -k "spec and global_beta" -q
```

Expected: fail because `global_beta` is not a valid affect value.

- [ ] **Step 3: Update `experiments/trust/spec.py`**

Add `global_beta` to `AFFECT_VALUES`.

- [ ] **Step 4: Re-run the targeted test**

Run the same pytest command.

Expected: pass.

### Task 2: Runtime Semantics

- [ ] **Step 1: Add gamma routing tests**

Test `gamma_for_partner(...)` for:

- local precision: partner-specific beta is used;
- tracked-only/none: base gamma is used;
- global beta: entity `0` beta is used for every partner.

- [ ] **Step 2: Add beta update routing tests**

Test that `update_beta_after_observation(...)` updates:

- the selected partner for local precision;
- no beta for `none` and `fixed`;
- entity `0` for `global_beta`;
- beta but not gamma for tracked-only decouple.

- [ ] **Step 3: Implement runtime routing**

Modify `tasks/trust/runtime.py` so `affect_mode == "global"`:

- reads expected beta from index `0`;
- updates beta index `0`;
- still logs the selected partner separately.

- [ ] **Step 4: Run runtime tests**

Run:

```bash
.venv/bin/python -m pytest tests -k "gamma_for_partner or update_beta" -q
```

Expected: pass.

### Task 3: Factory And Logging

- [ ] **Step 1: Add factory test**

Build a runtime from a `global_beta` variant. Assert:

- `runtime.affect_mode == "global"`;
- `runtime.partner_bank.beta.num_entities == 1`;
- partner-local agent count is unchanged.

- [ ] **Step 2: Implement factory support**

In `experiments/trust/factory.py`, map `variant.affect == "global_beta"` to:

- `agent_kind = "affective"`;
- `affect_mode = "global"`;
- `DiscreteBetaState(num_entities=1, ...)`.

- [ ] **Step 3: Add logger test**

Assert result rows include:

- `global_beta`;
- `betas` or `local_betas`;
- `gamma_used`;
- `selected_partner`;
- `prediction_errors`.

- [ ] **Step 4: Implement logging fields**

Keep existing fields backward compatible. For non-global variants, write
`global_beta` as missing/NaN. For global variants, write scalar beta in
`global_beta` and use an empty or repeated vector only if needed for plotting.

### Task 4: Smoke Configs

- [ ] **Step 1: Create locality smoke TOML**

Create `configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml` with:

- 3-5 replications;
- four partners: stable cooperator, reliable exploiter, random/volatile, scheduled stance-switch;
- variants: `none`, `precision`, `tracked_only`, `global_beta`;
- metrics including payoff, precision, partner choice, stance accuracy, deployment, and interference.

- [ ] **Step 2: Run smoke with one worker**

Run:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_smoke.toml \
  --output-dir results \
  --batch-name global_beta_locality_smoke_20260525 \
  --workers 1
```

Expected: completes or stops with a concrete runtime error to fix before any larger run.

### Task 5: Interference Analysis

- [ ] **Step 1: Add analysis unit tests**

Use a synthetic DataFrame with one switched partner and one untouched partner.
Assert the summary separates:

- switched partner post-switch entropy/payoff;
- untouched partner post-switch entropy/payoff;
- before/after selection rates;
- KL policy-posterior shift when policy vectors are available.

- [ ] **Step 2: Implement `analysis/interference.py`**

Provide a function such as:

```python
def cross_partner_interference_summary(df: pd.DataFrame) -> pd.DataFrame:
    ...
```

- [ ] **Step 3: Wire into `scripts/analysis/analyze.py`**

When scheduled switch metadata is present, write:

- `cross_partner_interference_summary.csv`;
- `untouched_partner_entropy_shift.csv`;
- `global_vs_local_beta_summary.csv` when global-beta rows exist.

### Task 6: Paper Figure Script

- [ ] **Step 1: Add script skeleton**

Create `scripts/analysis/make_paper_figures.py` with CLI args:

- `--source-root`;
- `--output-dir`;
- optional `--format png|pdf|both`.

- [ ] **Step 2: Implement current canonical figures**

Regenerate:

- H1 model-fitness dissociation;
- H2 deployment readouts;
- H4 partner choice;
- H3 betrayal boundary;
- shock-shape sensitivity;
- H5 supplemental beta dynamics.

- [ ] **Step 3: Run script on manuscript source tables**

Run:

```bash
.venv/bin/python scripts/analysis/make_paper_figures.py \
  --source-root docs/paper/manuscript/source_tables \
  --output-dir docs/paper/manuscript/figures \
  --format png
```

Expected: figures regenerate without manual plotting.

### Task 7: Verification And Handoff

- [ ] **Step 1: Run quality gate**

Run:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
git diff --check
```

- [ ] **Step 2: Document results**

Update docs only with implementation facts and smoke-run provenance. Do not
rewrite manuscript interpretation until the user reviews the new results.

- [ ] **Step 3: Commit**

Commit after passing tests and smoke analysis:

```bash
git add .
git commit -m "feat(trust): add global beta locality smoke"
```

