# Sub-project E — Documentation Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land a coherent doc rewrite that addresses the scoping audit's five findings (stale content, broken cross-links, content duplications, missing content, hypothesis-label drift) and locks in CI gates so future drift is caught at merge time. End state: 14 in-scope docs in a properly reorganized tree (docs/design/ name preserved), CLAUDE.md collapsed to a pointer, docs/README.md as the audience-contract index, three pytest validators in CI.

**Architecture:** Single PR with 15 ordered commits. Each commit is a bounded, reviewable unit (mostly one or two files). The 3 new validators land in commit 15 and run against the just-rewritten doc surface. Content rewrites happen in dependency order — new files first (so others can link to them), then rewrites of existing files, then top-level (README/AGENTS/CLAUDE) which depend on everything below.

**Tech Stack:** Markdown (CommonMark + GitHub-flavored). Python 3.12 + pytest for validators. Stdlib only — no markdown-parsing third-party dep.

**Spec reference:** `docs/superpowers/specs/2026-04-18-doc-rewrite-design.md`. Decision numbers (E1–E10) refer to that spec's decisions log.

**Upstream dependency:** D's `docs/experiment/manifest.md` MUST exist before E starts. E reads from it and links to it. Verify with `ls docs/experiment/manifest.md` before running Task 0.1.

**Skills referenced:**
- @superpowers:test-driven-development for the 3 new validators (write failing test first)
- @superpowers:verification-before-completion before claiming acceptance criteria met
- @superpowers:systematic-debugging if any cross-link or rewrite regresses

---

## File Structure

### Files modified (REWRITE — start fresh, may reuse sections)

| path | target lines | scope |
|---|---|---|
| `README.md` | ~80 | external visitors / quickstart |
| `AGENTS.md` | ~250 | canonical agent / coding-rules doc |
| `docs/theory/theory.md` | ~450 | RQ-shaped theory narrative |
| `docs/experiment/design.md` | ~500 | RQ1–7 + E1–2 protocols |
| `docs/experiment/results.md` | ~300 | per-RQ rolling results |
| `docs/research/roadmap.md` | ~250 | post-restructure roadmap (was docs/future/roadmap.md) |

### Files modified (REWRITE+MERGE)

| path | target lines | scope |
|---|---|---|
| `docs/design/trust.md` | ~500 | merges old design/implementation.md + design/partner_stance.md |

### Files modified (EDIT — surgical: stale-content + label sweep)

| path | scope |
|---|---|
| `docs/theory/pomdp_spec.md` | add appendices: graded payoff extension, factorized controls, divergences from apashea v4 |
| `docs/operations/cli.md` | sweep config name updates (rq#_*, e#_*) |
| `docs/operations/benchmark.md` | sweep config name updates |

### Files modified (COLLAPSE)

| path | scope |
|---|---|
| `CLAUDE.md` | from 222 lines → 5–15 line pointer to AGENTS.md |

### Files created (NEW)

| path | target lines | role |
|---|---|---|
| `docs/README.md` | ~60 | top-level doc index + audience contract + future-expansion door |
| `docs/design/aif.md` | ~250 | generic active-inference package overview (B+A outcome) |
| `docs/design/multi_focal.md` | ~200 | multi-focal-agent runtime overview (F outcome) |
| `tests/test_doc_links.py` | ~100 | broken-link sweep validator |
| `tests/test_rq_labels.py` | ~80 | no-stale-H# validator |
| `tests/test_doc_inventory.py` | ~100 | doc tree shape validator |

### Files renamed (`git mv`)

| from | to |
|---|---|
| `docs/future/roadmap.md` | `docs/research/roadmap.md` |
| `docs/design/implementation.md` | (deleted; content merged into `docs/design/trust.md`) |
| `docs/design/partner_stance.md` | (deleted; content merged into `docs/design/trust.md`) |

### Files deleted

- `docs/design/implementation.md` (after merge into trust.md)
- `docs/design/partner_stance.md` (after merge into trust.md)
- empty `docs/future/` directory (after rename)

---

## Phase 0 — Pre-flight

### Task 0.1: Verify D has merged and manifest exists

- [ ] **Step 1: Confirm manifest.md exists**

```bash
ls docs/experiment/manifest.md
```

If missing, STOP. D must be merged before E can start (E reads from manifest and links to it).

- [ ] **Step 2: Read manifest to absorb the canonical RQ→config→analysis mapping**

```bash
cat docs/experiment/manifest.md
```

This mapping is referenced in multiple E rewrites. Have it open while writing.

### Task 0.2: Re-inventory broken links (final state may differ from spec audit)

- [ ] **Step 1: Run a fresh broken-link scan**

```bash
rg "\]\(([^)]*\.md[^)]*)\)" -n --type-add 'doc:*.{md}' --type doc
```

Cross-reference against the spec's broken-link table (section 3.4). Note any new broken links that have appeared since the audit.

- [ ] **Step 2: Tabulate non-spec broken links in the PR description**

If any new ones appear, add them to commit 14's final cross-link sweep.

### Task 0.3: Verify B+A status (informs aif.md content)

- [ ] **Step 1: Check whether B+A has been implemented**

```bash
ls aif/ 2>/dev/null
```

- If `aif/` exists with the modules from spec section 3 (backend, maths, utils, efe, policies, learning, runtime, affect/): write `docs/design/aif.md` against the as-built code.
- If `aif/` does not exist yet: write `docs/design/aif.md` against B+A's spec (`docs/superpowers/specs/2026-04-18-aif-extraction-design.md`); add a header note "this doc precedes B+A implementation; update during B+A landing".

Note the chosen path in the PR description.

---

## Phase 1 — Structural moves (commit 1)

### Task 1.1: Rename docs/future → docs/research

**Files:**
- Rename: `docs/future/roadmap.md` → `docs/research/roadmap.md`

- [ ] **Step 1: git mv**

```bash
mkdir -p docs/research
git mv docs/future/roadmap.md docs/research/roadmap.md
rmdir docs/future
```

- [ ] **Step 2: Verify history preserved**

```bash
git log --follow docs/research/roadmap.md | head -n 5
```

### Task 1.2: Remove placeholder design files (content will be merged in commit 6)

**Files:**
- Delete: `docs/design/implementation.md`, `docs/design/partner_stance.md`

- [ ] **Step 1: Save a backup of contents to a scratch file (not committed)**

```bash
cp docs/design/implementation.md /tmp/e_implementation_backup.md
cp docs/design/partner_stance.md /tmp/e_partner_stance_backup.md
```

These are inputs for commit 6 (REWRITE+MERGE into `docs/design/trust.md`). Do NOT commit the backups.

- [ ] **Step 2: git rm**

```bash
git rm docs/design/implementation.md docs/design/partner_stance.md
```

- [ ] **Step 3: Commit (1 of 15)**

```bash
git commit -m "docs: structural moves — rename docs/future → docs/research; placeholder rm of design/implementation+partner_stance (E commit 1)"
```

This commit deliberately leaves the tree temporarily incomplete (trust.md doesn't exist yet). Commit 6 lands trust.md with the merged content.

---

## Phase 2 — Pre-rewrite link fixes (commit 2)

### Task 2.1: Fix broken links in non-rewritten files that are still in scope

This applies surgical fixes to files that ARE NOT being rewritten (otherwise the rewrite would handle the link). After commit 1, the rewriting starts; commit 2 fixes any link in a file not slated for full rewrite.

**Files:**
- Modify: `docs/theory/pomdp_spec.md` (EDIT-target; small, will be touched again in commit 8 but pre-fix any links here is safe)
- Modify: `docs/operations/cli.md` (EDIT-target; pre-fix links)
- Modify: `docs/operations/benchmark.md` (EDIT-target; pre-fix links)

- [ ] **Step 1: Scan for broken links in EDIT-targets**

```bash
rg "\]\(" docs/theory/pomdp_spec.md docs/operations/
```

Identify any link that points to a nonexistent file or to a file that will move (e.g. `docs/future/` → `docs/research/`).

- [ ] **Step 2: Fix in place**

Common patterns:
- `docs/future/roadmap.md` → `docs/research/roadmap.md`
- `docs/design/implementation.md` → `docs/design/trust.md`
- `docs/design/partner_stance.md` → `docs/design/trust.md`

Use `StrReplace` per file, one fix per file pass.

- [ ] **Step 3: Commit (2 of 15)**

```bash
git commit -am "docs: pre-rewrite link fixes in EDIT-target files (E commit 2)"
```

---

## Phase 3 — New file: docs/README.md (commit 3)

### Task 3.1: Write docs/README.md

**Files:**
- Create: `docs/README.md`

- [ ] **Step 1: Write the index**

Sections (target ~60 lines total):

1. **Heading**: `# Documentation index`
2. **One-paragraph preamble**: "This index points to every authoritative doc in the project. The top-level `README.md` is the project intro; this file is the docs index for researchers and maintainers."
3. **Audience contract table** (per spec section 1):

```markdown
## Who reads what

| audience | reads |
|---|---|
| external visitor / first time | `../README.md` |
| AI coding agent (Cursor, Claude Code) | `../AGENTS.md` (and `../CLAUDE.md` pointer) |
| researcher / theorist | `theory/`, `experiment/`, `research/` |
| maintainer / engineer | `design/`, `operations/` |
| reviewer of past decisions | `superpowers/specs/`, `superpowers/plans/` |
| paper consumer | `paper/main.pdf` (out of E scope) |
```

4. **Per-directory ToC**:

```markdown
## What's where

### theory/
- `theory.md` — research-question-shaped narrative (motivation + RQ1–7)
- `pomdp_spec.md` — formal generative model spec (canonical, apashea v4-aligned)

### design/
- `aif.md` — generic active-inference package (modules, public API, extension points)
- `trust.md` — trust-game project module (TrustGameModel, TrustGameAgent, partner stance)
- `multi_focal.md` — multi-focal-agent runtime

### experiment/
- `design.md` — RQ1–7 + E1–2 protocols, conditions, task setup
- `results.md` — rolling per-RQ results narrative
- `manifest.md` — config ↔ RQ ↔ analysis function map (single source of truth)

### operations/
- `cli.md` — command-line reference
- `benchmark.md` — benchmark runner ops

### research/
- `roadmap.md` — completed sub-projects, near/mid/long-term research
```

5. **Future-expansion door** (per spec section 1):

```markdown
## Future expansion

The doc tree is designed to grow without re-collapsing. New docs land here:

| if/when… | new doc lands here |
|---|---|
| CvC track unfreezes | `design/cogames.md` + `experiment/cvc.md` |
| Human data lands (Phase 8) | `experiment/human_fits.md` |
| New sub-project on top of B+A | `superpowers/specs/<date>-<name>-design.md` (existing pattern) |
| New analysis methodology | `operations/analysis.md` |
| Per-RQ deep dive needed | `research/rq#_<name>_deepdive.md` |
```

- [ ] **Step 2: Commit (3 of 15)**

```bash
git add docs/README.md
git commit -m "docs: add top-level index with audience contract (E commit 3)"
```

---

## Phase 4 — New file: docs/design/aif.md (commit 4)

### Task 4.1: Write docs/design/aif.md

**Files:**
- Create: `docs/design/aif.md`

Decision: write against as-built `aif/` if it exists (Task 0.3), else against the B+A spec.

- [ ] **Step 1: Read the B+A spec**

```bash
cat docs/superpowers/specs/2026-04-18-aif-extraction-design.md | head -n 200
```

- [ ] **Step 2: If aif/ exists, list module structure**

```bash
ls aif/ 2>/dev/null
ls aif/affect/ 2>/dev/null
```

- [ ] **Step 3: Write the doc**

Structure (target ~250 lines):

1. **Heading**: `# AIF package`
2. **One-paragraph rationale**: "Generic active-inference machinery, extracted from the trust-game project per sub-project B+A. The `aif/` package is task-agnostic and reusable; trust-game–specific code lives in `trust/` (see `design/trust.md`)."
3. **Module-by-module overview** (a section per module):
   - `aif.backend` — numpy-first; jax optional
   - `aif.maths` — softmax, log-softmax, KL, entropy, log_policy_prior helpers
   - `aif.utils` — array helpers, config validation
   - `aif.efe` — expected free energy components (epistemic + pragmatic + risk)
   - `aif.policies` — policy enumeration, sampling, evaluation
   - `aif.learning` — optional dirichlet learning of A and B priors
   - `aif.runtime` — `aif.Agent` shell + `decision_step` orchestrator
   - `aif.affect.beta` — discrete-beta precision tracker
   - `aif.affect.interoception` — interoceptive update rule
4. **Public surface**: list of `__all__` from `aif/__init__.py`
5. **What's NOT in `aif/`**: anything trust-specific (TrustGameModel, TrustGameAgent, partner stance) — those live in `trust/`
6. **How to extend**:
   - new affect module → `aif/affect/<name>.py` with the standard interface
   - new example task → `examples/<task>/` not `aif/`
7. **Reference**: B+A spec at `../superpowers/specs/2026-04-18-aif-extraction-design.md` for design rationale

- [ ] **Step 4: Commit (4 of 15)**

```bash
git add docs/design/aif.md
git commit -m "docs: add design/aif.md — generic active-inference package overview (E commit 4)"
```

---

## Phase 5 — New file: docs/design/multi_focal.md (commit 5)

### Task 5.1: Write docs/design/multi_focal.md

**Files:**
- Create: `docs/design/multi_focal.md`

- [ ] **Step 1: Read F's spec**

```bash
cat docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md | head -n 200
```

- [ ] **Step 2: Inspect the as-built runner**

```bash
ls experiment/multi_focal_runner.py 2>/dev/null
grep -n "^def \|^class " experiment/multi_focal_runner.py
```

- [ ] **Step 3: Write the doc**

Structure (target ~200 lines):

1. **Heading**: `# Multi-focal runtime`
2. **Motivation**: M focal AIF agents vs 1 focal + scripted partners. Why this matters: enables emergent dynamics, mixed clinical populations, assortative pairing.
3. **Entry point**: `experiment/multi_focal_runner.py` — class structure, top-level `run` function
4. **Pairing rules**:
   - round-robin
   - all-pairs (per round each agent plays one match against another)
   - random
   - mutual-selection (agent_choice mode)
5. **Joint game resolution**: simultaneous-moves convention (decision F4 from F's spec). What "simultaneous" means for inference order: each agent plans against its own beliefs; both submit; both observe; both update.
6. **Heterogeneous populations**: config schema example showing how to mix affective + lesioned + clinical-preset agents in one population.
7. **Emergent dynamics tests**: gated `slow` tests in `tests/test_multi_focal_emergent.py` describe what's checked.
8. **Reference**: F's spec at `../superpowers/specs/2026-04-18-multi-focal-runtime-design.md`.

- [ ] **Step 4: Commit (5 of 15)**

```bash
git add docs/design/multi_focal.md
git commit -m "docs: add design/multi_focal.md — multi-focal-agent runtime overview (E commit 5)"
```

---

## Phase 6 — REWRITE+MERGE: docs/design/trust.md (commit 6)

### Task 6.1: Write docs/design/trust.md by merging implementation.md + partner_stance.md

**Files:**
- Create: `docs/design/trust.md`
- Reference (from `/tmp/e_implementation_backup.md` and `/tmp/e_partner_stance_backup.md`)

- [ ] **Step 1: Re-read the backups**

```bash
cat /tmp/e_implementation_backup.md
cat /tmp/e_partner_stance_backup.md
```

- [ ] **Step 2: Write the merged doc**

Structure (target ~500 lines):

1. **Heading**: `# Trust-game project module`
2. **Overview** (~30 lines): trust-game–specific code, distinct from generic `aif/` package; relies on aif/ for inference machinery
3. **TrustGameModel** (~100 lines): canonical generative model post-B+A; `payoff_mode={binary, graded}`; A/B/C/D matrices; cross-reference `../theory/pomdp_spec.md` for math, this section explains the code-level realization
4. **TrustGameAgent** (~80 lines): multi-partner joint beliefs, per-partner beta tracker, decision flow
5. **Partner stance dynamics** (~120 lines, was `partner_stance.md`): refreshed for B+A; remove jax-first language; describe action-dependent stance transitions, latent stance categories, how stance interacts with type
6. **Factorized environment wiring** (~50 lines): `[1,2,2]` and `[N,2,2]` control modes; how the env factorizes observations per partner
7. **decision_step_trust_game** (~60 lines): the trust-game-specific decision orchestrator; what it does on top of `aif.Agent.decision_step`
8. **Rollout** (~30 lines): a turn in detail (predict → step → observe → update)
9. **Cross-references**: `../theory/pomdp_spec.md`, `aif.md`, `multi_focal.md`, `../experiment/manifest.md`

Apply sweep specs from spec section 3 throughout: kill jax-first language, kill `o_intero` references (but the level-3 transition narrative gets the v4 update — external beta tracker, not interoceptive observation channel).

- [ ] **Step 3: Commit (6 of 15)**

```bash
git add docs/design/trust.md
git commit -m "docs: add design/trust.md merging implementation+partner_stance (E commit 6)"
```

---

## Phase 7 — REWRITE: docs/theory/theory.md (commit 7)

### Task 7.1: Rewrite theory.md as RQ-shaped narrative

**Files:**
- Modify: `docs/theory/theory.md`

- [ ] **Step 1: Read current theory.md to extract still-good content**

```bash
cat docs/theory/theory.md
```

Note which sections are reusable (the formal POMDP framing language, motivational arc) and which to drop (jax-first, `o_intero`, dead config refs, H6/H7 narrative).

- [ ] **Step 2: Read manifest.md and experiment/design.md (current) to align RQ vocabulary**

```bash
cat docs/experiment/manifest.md
```

- [ ] **Step 3: Write the rewrite**

Structure (target ~450 lines, down from 615):

1. **Motivation** (~40 lines): what we're studying — affect-modulated active inference in iterated trust games; biological grounding (Damasio); why active inference rather than RL
2. **POMDP framing** (~30 lines): high-level picture; link to `pomdp_spec.md` for the formal spec; do NOT duplicate that content
3. **Per-RQ sections** (~50 lines each):
   - **RQ1 — role of planning depth**: open question; what we're measuring; what answers might look like
   - **RQ2 — regime where affect adds value**: same shape
   - **RQ3 — lesion dissociation (Damasio analog)**: same shape
   - **RQ4 — betrayal recovery**: same shape
   - **RQ5 — partner selection**: same shape
   - **RQ6 — graded payoff unlocks the precision channel**: same shape
   - **RQ7 — clinical task-specificity**: same shape
4. **Engineering objectives** (~30 lines): brief mention of E1, E2; pointer to manifest.md for details
5. **Theoretical extensions in current code** (~50 lines):
   - factorized controls (`[1,2,2]` / `[N,2,2]`)
   - `log_policy_prior` (log-softmax C[1] vs raw apashea)
   - dirichlet learning flags (optional A/B priors)
   - external beta tracker (post-v4)
6. **Conditions reference** (~30 lines): brief overview of conditions 1–8 + 9–10 (tau3 pair); link to `../experiment/design.md` for full schedule

Apply sweep specs: kill jax-first, `o_intero`, dead config refs (`horizon_sweep.json`, `deep_affect_test.json`, `variational_beta`, `AIFPolicy`), beta-as-pomdp-factor framing. Move H6 (predictive comparison) reference into `../research/roadmap.md` (this commit prepares the move; the actual addition lands in commit 12).

Kill broken link to `docs/action-dependent-partner-design.md` (file never existed).

H#→RQ# rename (~2 mentions in old theory.md): apply during rewrite.

- [ ] **Step 4: Commit (7 of 15)**

```bash
git add docs/theory/theory.md
git commit -m "docs: REWRITE theory.md as RQ-shaped narrative (E commit 7)"
```

---

## Phase 8 — EDIT: docs/theory/pomdp_spec.md (commit 8)

### Task 8.1: Add appendices to pomdp_spec.md

**Files:**
- Modify: `docs/theory/pomdp_spec.md`

- [ ] **Step 1: Read current pomdp_spec.md**

```bash
cat docs/theory/pomdp_spec.md | head -n 50
```

Confirm: v4 framing is correct (beta external, no `o_intero`). The audit confirmed no kills needed in this file.

- [ ] **Step 2: Append three new appendix sections at the end**

**Appendix A — Extension: Graded payoff (`payoff_mode='graded'`)** (~30 lines):
- 6-level graded action space
- A/C matrix shape changes
- Why this matters for RQ6 (precision channel becomes load-bearing)

**Appendix B — Extension: Factorized controls (`[1,2,2]` / `[N,2,2]`)** (~30 lines):
- N partners → action space `[N, 2, 2]` (partner choice × cooperate/defect × extra)
- How env factorizes observations per partner
- When to use `[1,2,2]` (single-partner mode) vs `[N,2,2]` (multi-partner)

**Appendix C — Documented divergences from apashea v4** (~30 lines):
- log-softmax C[1] (vs raw apashea) → name: `log_policy_prior`; rationale: numerical stability
- optional dirichlet learning of A and B priors → name: `aif.learning`
- per-partner beta tracker (apashea has single beta) → rationale: each partner has its own history
- any other divergences discovered during B+A implementation

- [ ] **Step 3: Commit (8 of 15)**

```bash
git add docs/theory/pomdp_spec.md
git commit -m "docs: EDIT pomdp_spec — add graded/factorized/divergences appendices (E commit 8)"
```

---

## Phase 9 — REWRITE: docs/experiment/design.md (commit 9)

### Task 9.1: Rewrite experiment/design.md as RQ1–7 + E1–2 protocols

**Files:**
- Modify: `docs/experiment/design.md`

- [ ] **Step 1: Read current design.md**

```bash
cat docs/experiment/design.md
```

Identify reusable sections (POMDP description if accurate, conditions list if updatable, analytical conventions) and what to kill (H1–H9 framing, `o_intero` line 92, dead config refs, broken links to `docs/action-dependent-partner-design.md` and `docs/results_tracking.md`).

- [ ] **Step 2: Read manifest.md as the canonical RQ→config map**

```bash
cat docs/experiment/manifest.md
```

- [ ] **Step 3: Write the rewrite**

Structure (target ~500 lines, down from 585):

1. **Motivation** (~30 lines)
2. **Task setup** (~50 lines): trust-game environment, partner types and stances, payoff modes (binary + graded)
3. **POMDP framing** (~40 lines): updated to v4 (no `o_intero`, external beta); link `../theory/pomdp_spec.md`
4. **Experimental conditions** (~80 lines):
   - conditions 1–8 (existing)
   - conditions 9–10 (tau3 pair) — newly documented per spec section 3.3
   - per-condition table: name, agent type, parameters, scenario
5. **Per-RQ protocols** (~40 lines each):
   - RQ1 — protocol for `rq1_depth_factorial.json`: what's varied, what's measured, link to `manifest.md` for analysis fn
   - RQ2 — protocol for `rq2_shallow_affect.json` and the contrast against `rq1_depth_factorial.json`
   - RQ3 — `rq3_lesion_dissociation.json`
   - RQ4 — `rq4_betrayal_recovery.json` (and link `rq7_clinical_betrayal.json` for clinical layer)
   - RQ5 — `rq5_partner_selection.json`
   - RQ6 — `rq6_graded_factorial.json`, `rq6_graded_betrayal.json`
   - RQ7 — `rq7_clinical_betrayal.json`, `rq7_clinical_phenotypes.json`, `rq7_sensitivity_sweep.json`
6. **Engineering objectives** (~30 lines): E1 (baseline arena), E2 (multi-focal dynamics); pointer to manifest
7. **Naming history** (~30 lines, with `<!-- rq-labels:allow -->` ... `<!-- rq-labels:end -->` HTML comments): documents the H#→RQ# transition for future readers / paper drafts. Per spec validator allow-list.
8. **Analysis pointers** (~10 lines): pointer to `manifest.md` for canonical config↔RQ↔analysis triple; pointer to `results.md` for rolling status

Apply sweep: kill jax-first language (~1-2 mentions), kill `o_intero` line 92 (rewrite level-3 transition), kill dead config refs, kill broken links.

H#→RQ# rename: apply for ~17 in-scope mentions (most absorbed by the per-RQ section rewrite).

- [ ] **Step 4: Commit (9 of 15)**

```bash
git add docs/experiment/design.md
git commit -m "docs: REWRITE experiment/design — RQ1–7 + E1–2 protocols (E commit 9)"
```

---

## Phase 10 — REWRITE: docs/experiment/results.md (commit 10)

### Task 10.1: Rewrite results.md with per-RQ status blocks

**Files:**
- Modify: `docs/experiment/results.md`

- [ ] **Step 1: Read current results.md**

Most pre-restructure tables are no longer comparable. Identify any results that survive the model surface change (rare).

- [ ] **Step 2: Write the rewrite**

Structure (target ~300 lines, down from 600):

1. **Heading + preamble** (~20 lines): "rolling per-RQ results narrative; canonical status field per RQ; cross-references manifest.md"
2. **Status legend**: explain `complete | needs_rerun | pending | future` (machine-parseable per spec section 3.5)
3. **Per-RQ block** (~30 lines each):

```markdown
### RQ1 — role of planning depth

**Status**: needs_rerun

**Question**: how does explicit planning depth affect performance across binary
and graded payoff regimes — does deeper help, saturate, or interact with affect?

**Configs**: `rq1_depth_factorial.json`, `rq6_graded_factorial.json`

**Analysis**: `analysis.research_questions.report_rq1_depth_curve`

**Current evidence**: post-restructure rerun pending. Pre-restructure results
are no longer comparable due to canonical model surface change in B+A.

**Interpretation**: pending.

**Result artifacts**: pending; will land at `results/<batch>/rq1_depth_factorial/`.
```

Repeat for RQ2–RQ7 + E1, E2.

4. **Naming history note** (allow-listed via HTML comment): brief mention that pre-restructure runs used H1–H9 labels; see `design.md` naming-history section for full mapping.

- [ ] **Step 3: Commit (10 of 15)**

```bash
git add docs/experiment/results.md
git commit -m "docs: REWRITE results.md as per-RQ status blocks (E commit 10)"
```

---

## Phase 11 — EDIT: operations/cli.md + benchmark.md (commit 11)

### Task 11.1: Sweep cli.md for old config names + analysis output names

**Files:**
- Modify: `docs/operations/cli.md`

- [ ] **Step 1: Read current cli.md**

```bash
cat docs/operations/cli.md
```

- [ ] **Step 2: Apply renames**

| old | new |
|---|---|
| `shallow_affect_confirm.json` | `rq2_shallow_affect.json` |
| `clinical_betrayal.json` | `rq7_clinical_betrayal.json` |
| `h1_*.json`, `h2_*.json`, `h4_*.json`, `h5_*.json` | `rq#_*.json` per manifest |
| `multifocal_*.json` | `e2_multifocal_*.json` or `smoke_multifocal.json` |
| `benchmark_*.json` | `e1_benchmark_*.json` (or `configs/archive/*` if archived) |
| `hypothesis_tests.json` | `research_questions.json` |
| any `H[1-9]` mention (1 in current file) | rename per manifest |

- [ ] **Step 3: Verify no jax-first language remains** (`rg jax docs/operations/cli.md`)

### Task 11.2: Sweep benchmark.md

**Files:**
- Modify: `docs/operations/benchmark.md`

- [ ] **Step 1: Apply renames per manifest**

Same patterns as cli.md but focused on benchmark configs. Notable updates:
- `benchmark_full.json` → `e1_benchmark_arena.json` (merged)
- `benchmark_betrayal_comprehensive.json` → `e1_benchmark_betrayal_kitchen_sink.json`
- `benchmark_betrayal_fair.json` → `e1_benchmark_betrayal_fair.json`
- `benchmark_noisy.json` → `e1_benchmark_noisy.json`
- archived configs (`benchmark_default`, `benchmark_resource_sharing`, `benchmark_comprehensive`, `benchmark_betrayal`) → either drop the example or update to canonical replacements; reference `configs/archive/README.md` for "why this isn't here"

- [ ] **Step 2: Verify variational_beta and AIFPolicy not mentioned (already removed in C)**

```bash
rg "variational_beta|AIFPolicy" docs/operations/benchmark.md
```

Expected: no matches.

### Task 11.3: Commit (11 of 15)

```bash
git add docs/operations/cli.md docs/operations/benchmark.md
git commit -m "docs: EDIT operations/{cli,benchmark} — config name + artifact sweeps (E commit 11)"
```

---

## Phase 12 — REWRITE: docs/research/roadmap.md (commit 12)

### Task 12.1: Rewrite roadmap with completed sub-projects + new horizons

**Files:**
- Modify: `docs/research/roadmap.md`

- [ ] **Step 1: Read current roadmap (was docs/future/roadmap.md, moved in commit 1)**

```bash
cat docs/research/roadmap.md
```

- [ ] **Step 2: Read STATE.md for current operational state**

```bash
cat conductor/STATE.md
```

- [ ] **Step 3: Write rewrite**

Structure (target ~250 lines, up from 202):

1. **Heading + preamble** (~20 lines): "research roadmap — completed work, current focus, near/mid/long-term horizons"
2. **Completed sub-projects** (~30 lines): 
   - C — agent inventory consolidation (2026-04-18)
   - F — multi-focal runtime (2026-04-18)
   - B+A — aif/ extraction (status per Task 0.3)
   - D — experiment configs + research-question cleanup (with PR ref)
   - E — documentation rewrite (this PR)
3. **Pending sub-projects** (~30 lines): post-D reruns sequenced per STATE.md (rq2 → rq5 → rq7 → rest)
4. **Near-term research** (~50 lines): RQ-aligned next sessions
   - shallow rerun (RQ2)
   - partner selection (RQ5)
   - clinical (RQ7)
   - graded channel deeper exploration (RQ6)
5. **Mid-term** (~50 lines):
   - multi-focal emergent dynamics deep dive (E2)
   - cross-RQ synthesis (paper draft refresh)
6. **Long-term / future research** (~50 lines):
   - H6 predictive model comparison (moved from theory.md per spec section 3.1) — describe what it would entail; not currently scheduled
   - human data fits (Phase 8) — what's needed (data acquisition, fit infrastructure)
   - BMR / structure learning (Phase 7+) — open problem
7. **Open methodological questions** (~20 lines): ongoing items that don't fit a sub-project (e.g. "should `mu` calibration target a fixed value or be free?")

H#→RQ# rename: apply (~2 mentions in current file).

- [ ] **Step 4: Commit (12 of 15)**

```bash
git add docs/research/roadmap.md
git commit -m "docs: REWRITE research/roadmap — post-restructure horizons (E commit 12)"
```

---

## Phase 13 — REWRITE top-level + COLLAPSE CLAUDE.md (commit 13)

### Task 13.1: Rewrite README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current README.md**

```bash
cat README.md
```

- [ ] **Step 2: Write rewrite (target ~80 lines)**

Sections:
1. **Heading + one-paragraph project intro**: what this project is (active-inference trust-game research), what it produces (RQ-shaped evidence + paper)
2. **Quickstart** (~30 lines):

```markdown
## Quickstart

```bash
git clone <repo>
cd affect_aif
pip install -e .
pytest --ignore=tests/test_cvc_*.py  # default suite
python scripts/run_experiment.py --config configs/smoke_focal.json --out /tmp/smoke
```
```

3. **RQ summary table** (~20 lines):

```markdown
## Research questions at a glance

| RQ | question | doc |
|---|---|---|
| RQ1 | role of planning depth | [docs/experiment/design.md#rq1](docs/experiment/design.md#rq1) |
| RQ2 | regime where affect adds value | [...] |
| ... | ... | ... |
```

(Per spec section 3.1; absorbed from manifest.)

4. **Audience pointer** (~5 lines): "for full doc index see [docs/README.md](docs/README.md); for AI-coding-agent conventions see [AGENTS.md](AGENTS.md)"
5. **License + citation** (~5 lines)

Fix broken link `docs/cli.md` → `docs/operations/cli.md` (or just point to docs/README.md as the index).

### Task 13.2: Rewrite AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Read current AGENTS.md**

```bash
cat AGENTS.md
```

- [ ] **Step 2: Read CLAUDE.md to identify content that should move into AGENTS.md before COLLAPSE**

```bash
cat CLAUDE.md
```

Identify any rules / workflow guidance in CLAUDE.md that doesn't already exist in AGENTS.md.

- [ ] **Step 3: Write rewrite (target ~250 lines)**

Sections:
1. **Heading + preamble**: "canonical agent / coding-rules doc; CLAUDE.md is a pointer to this file"
2. **Required reading before changes**: per-area pointers (theory → `docs/theory/`, experiments → `docs/experiment/`, etc.) — fix the 5 broken links from spec section 3.4
3. **Workflow rules**: pre-commit gates, test-before-merge, verification skill reference
4. **Skills available**: brief table of skills (test-driven-development, verification-before-completion, etc.) with @paths
5. **Source layout**: refresh per current `affect_aif/` layout post-B+A and post-C (new `aif/` package, `trust/` package, `experiment/multi_focal_runner.py`)
6. **Coding conventions**: 4-space indents, lowercase concise comments (per user rules), no inline imports
7. **Experiment conditions** (table): conditions 1–8 + 9–10 (tau3 pair) — newly added per spec section 3.3; pull from `docs/experiment/design.md#conditions`
8. **RQ → config map** (one-line per RQ): pointer to `docs/experiment/manifest.md` for the full canonical mapping
9. **Analysis output filenames**: `research_questions.json` (canonical), `engineering_objectives.json`, `hypothesis_tests.json` (deprecated alias during D shim period)
10. **Pre-commit hooks**: list what's enforced; reference `.pre-commit-config.yaml`
11. **Known gotchas**: brief list (e.g. "default config (random partner) does not discriminate conditions; use scheduled-switch configs for RQ-relevant results")

H#→RQ# rename: apply for the ~4 in-scope mentions (likely "H1-H5" in analysis section).

Fix all 5 broken links per spec section 3.4.

### Task 13.3: COLLAPSE CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Replace contents with pointer**

```markdown
# Claude Code

This project's agent-facing conventions live in [AGENTS.md](AGENTS.md).

For a per-audience doc index, see [docs/README.md](docs/README.md).
```

(~5 lines. Sentinel: must be ≤15 lines per validator 3.)

If any Claude-Code-specific directive doesn't fit AGENTS.md (e.g. specific to Claude Code's hook system), preserve it under a `## Claude-only` subsection here. Keep total ≤15 lines.

- [ ] **Step 2: Verify line count**

```bash
wc -l CLAUDE.md
```

Expected: ≤15.

### Task 13.4: Commit (13 of 15)

```bash
git add README.md AGENTS.md CLAUDE.md
git commit -m "docs: REWRITE README+AGENTS, COLLAPSE CLAUDE (E commit 13)"
```

---

## Phase 14 — STATE.md update + final cross-link sweep (commit 14)

### Task 14.1: Update conductor/STATE.md

**Files:**
- Modify: `conductor/STATE.md`

- [ ] **Step 1: Read current STATE.md**

```bash
cat conductor/STATE.md
```

After D's PR, STATE.md should already reflect post-D state. E updates:
- Add E to completed sub-projects
- Clear "sub-project E" from `next_priority` if listed
- `next_session_focus`: advance to "post-E reruns sequenced per manifest.md (rq2 → rq5 → rq7)"
- Clear any pending docs items now resolved by E

- [ ] **Step 2: Apply edit**

### Task 14.2: Final cross-link sweep

- [ ] **Step 1: Run a fresh broken-link scan**

```bash
rg "\]\(([^)]*\.md[^)]*)\)" -n --type-add 'doc:*.{md}' --type doc --glob '!docs/superpowers/**' --glob '!docs/paper/**'
```

- [ ] **Step 2: Verify each link resolves**

For each match, check `Path(link_target).exists()`. If any broken, fix in place.

- [ ] **Step 3: Verify no stale H# references in in-scope files**

```bash
rg '\bH[1-9]\b' README.md AGENTS.md CLAUDE.md docs/theory/ docs/experiment/ docs/design/ docs/operations/ docs/research/
```

Expected: only matches inside `<!-- rq-labels:allow -->` ... `<!-- rq-labels:end -->` blocks (in `docs/experiment/design.md` naming-history section).

If anything else matches: fix per the H#→RQ# table in spec section 3.1.

### Task 14.3: Commit (14 of 15)

```bash
git add conductor/STATE.md
# include any final link fixes
git commit -m "docs: STATE.md update + final cross-link sweep (E commit 14)"
```

---

## Phase 15 — Validators (commit 15)

### Task 15.1: Implement tests/test_doc_links.py

**Files:**
- Create: `tests/test_doc_links.py`

- [ ] **Step 1: Write failing test (TDD: assert that the validator finds zero broken links)**

```python
"""Verify every internal markdown link in in-scope docs points to an existing file."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
IN_SCOPE_FILES = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    *ROOT.glob("docs/**/*.md"),
]
EXCLUDED_DIRS = {ROOT / "docs" / "paper", ROOT / "docs" / "superpowers"}


def _is_in_scope(path: Path) -> bool:
    return not any(excluded in path.parents for excluded in EXCLUDED_DIRS)


_LINK_RE = re.compile(r"\]\(([^)]+\.md(?:#[^)]*)?)\)")


def _collect_links() -> list[tuple[Path, int, str]]:
    """Yield (file, line_number, link_target) for every internal .md link."""
    out = []
    for path in IN_SCOPE_FILES:
        if not _is_in_scope(path):
            continue
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for match in _LINK_RE.finditer(line):
                target = match.group(1)
                if target.startswith(("http://", "https://")):
                    continue
                out.append((path, lineno, target))
    return out


@pytest.mark.parametrize("file,lineno,link", _collect_links())
def test_internal_link_resolves(file: Path, lineno: int, link: str):
    target = link.split("#", 1)[0]  # strip anchor
    if target.startswith("/"):
        resolved = ROOT / target.lstrip("/")
    else:
        resolved = (file.parent / target).resolve()
    assert resolved.exists(), f"{file.relative_to(ROOT)}:{lineno} → {link!r} does not resolve to {resolved}"
```

- [ ] **Step 2: Run, expect PASS (because we already fixed all broken links in commits 1–14)**

```bash
pytest tests/test_doc_links.py -v
```

Expected: ALL PASS.

If any FAIL: fix in commit 14 retroactively, then re-run.

### Task 15.2: Implement tests/test_rq_labels.py

**Files:**
- Create: `tests/test_rq_labels.py`

- [ ] **Step 1: Write the validator**

```python
"""Verify in-scope docs have migrated H# → RQ#/E# labels."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
IN_SCOPE_FILES = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    *ROOT.glob("docs/theory/*.md"),
    *ROOT.glob("docs/experiment/*.md"),
    *ROOT.glob("docs/design/*.md"),
    *ROOT.glob("docs/operations/*.md"),
    *ROOT.glob("docs/research/*.md"),
]
# CLAUDE.md excluded — collapsed to pointer; docs/superpowers and docs/paper out of scope.

_H_RE = re.compile(r"\bH[1-9]\b")
_ALLOW_OPEN = "<!-- rq-labels:allow -->"
_ALLOW_CLOSE = "<!-- rq-labels:end -->"


def _strip_allow_listed_blocks(text: str) -> str:
    """Remove content between <!-- rq-labels:allow --> and <!-- rq-labels:end -->."""
    out = []
    i = 0
    while i < len(text):
        open_idx = text.find(_ALLOW_OPEN, i)
        if open_idx == -1:
            out.append(text[i:])
            break
        out.append(text[i:open_idx])
        close_idx = text.find(_ALLOW_CLOSE, open_idx + len(_ALLOW_OPEN))
        if close_idx == -1:
            break  # unterminated allow block; treat rest as allow-listed
        i = close_idx + len(_ALLOW_CLOSE)
    return "".join(out)


def _collect_h_mentions() -> list[tuple[Path, int, str]]:
    out = []
    for path in IN_SCOPE_FILES:
        if not path.exists():
            continue
        text = _strip_allow_listed_blocks(path.read_text(encoding="utf-8"))
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in _H_RE.finditer(line):
                out.append((path, lineno, match.group(0)))
    return out


@pytest.mark.parametrize("file,lineno,label", _collect_h_mentions())
def test_no_stale_h_label(file: Path, lineno: int, label: str):
    pytest.fail(f"{file.relative_to(ROOT)}:{lineno} contains stale label {label!r}; rename to RQ#/E# per docs/experiment/manifest.md")
```

- [ ] **Step 2: Run**

```bash
pytest tests/test_rq_labels.py -v
```

Expected: ALL PASS (or 0 collected if no H# mentions remain — also a pass).

If any FAIL: fix the offending file, OR wrap with `<!-- rq-labels:allow -->` ... `<!-- rq-labels:end -->` if the mention is legitimate (naming history).

### Task 15.3: Implement tests/test_doc_inventory.py

**Files:**
- Create: `tests/test_doc_inventory.py`

- [ ] **Step 1: Write the validator**

```python
"""Verify in-scope doc tree matches the spec."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "theory" / "theory.md",
    ROOT / "docs" / "theory" / "pomdp_spec.md",
    ROOT / "docs" / "design" / "aif.md",
    ROOT / "docs" / "design" / "trust.md",
    ROOT / "docs" / "design" / "multi_focal.md",
    ROOT / "docs" / "experiment" / "design.md",
    ROOT / "docs" / "experiment" / "results.md",
    ROOT / "docs" / "experiment" / "manifest.md",
    ROOT / "docs" / "operations" / "cli.md",
    ROOT / "docs" / "operations" / "benchmark.md",
    ROOT / "docs" / "research" / "roadmap.md",
}
EXCLUDED_DIRS = {ROOT / "docs" / "paper", ROOT / "docs" / "superpowers"}


def _scanned_in_scope_files() -> set[Path]:
    """Find all *.md files under top-level + docs/ excluding paper/superpowers."""
    candidates = set(ROOT.glob("*.md")) | set(ROOT.glob("docs/**/*.md"))
    return {p for p in candidates if not any(excluded in p.parents for excluded in EXCLUDED_DIRS)}


def test_all_expected_docs_exist():
    missing = {p for p in EXPECTED if not p.exists()}
    assert not missing, f"missing expected docs: {sorted(p.relative_to(ROOT) for p in missing)}"


def test_no_unexpected_docs():
    actual = _scanned_in_scope_files()
    unexpected = actual - EXPECTED
    assert not unexpected, (
        f"unexpected docs found (add to EXPECTED in this test or docs/README.md): "
        f"{sorted(p.relative_to(ROOT) for p in unexpected)}"
    )


def test_paper_and_superpowers_excluded():
    actual = _scanned_in_scope_files()
    for p in actual:
        for excluded in EXCLUDED_DIRS:
            assert excluded not in p.parents, f"{p} should be excluded but appears in scan"


def test_claude_md_is_pointer():
    claude = ROOT / "CLAUDE.md"
    assert claude.exists()
    line_count = sum(1 for _ in claude.read_text(encoding="utf-8").splitlines())
    assert line_count <= 15, f"CLAUDE.md is {line_count} lines; should be ≤15 (collapsed to pointer)"
```

- [ ] **Step 2: Run**

```bash
pytest tests/test_doc_inventory.py -v
```

Expected: ALL PASS.

If `test_no_unexpected_docs` fails, either the file is legitimately new (update EXPECTED + docs/README.md) or it's a stray (delete it).

### Task 15.4: Run all 3 validators together

```bash
pytest tests/test_doc_links.py tests/test_rq_labels.py tests/test_doc_inventory.py -v
```

Expected: ALL PASS.

### Task 15.5: Commit (15 of 15)

```bash
git add tests/test_doc_links.py tests/test_rq_labels.py tests/test_doc_inventory.py
git commit -m "tests: add 3 doc validators (links, RQ labels, inventory) (E commit 15)"
```

---

## Phase 16 — Final verification (per @superpowers:verification-before-completion)

### Task 16.1: Run full pytest

```bash
pytest --ignore=tests/test_cvc_*.py
```

Expected: GREEN (including the 3 new doc validators + D's manifest validator).

### Task 16.2: Run pre-commit hooks (if configured)

```bash
cat .pre-commit-config.yaml  # confirm what's configured
pre-commit run --all-files   # if pre-commit is installed
```

Expected: GREEN (markdown formatters / linters clean).

### Task 16.3: Manual review checklist

Tick before opening PR:

- [ ] `docs/README.md` audience-contract table is accurate
- [ ] All 8 missing-content topics from spec section 3.3 have a section in their target doc with >1 paragraph:
  - [ ] factorized controls (in `docs/theory/theory.md` and `docs/theory/pomdp_spec.md`)
  - [ ] `log_policy_prior` (in `docs/theory/pomdp_spec.md` and `docs/design/aif.md`)
  - [ ] dirichlet learning flags (in `docs/theory/theory.md` and `docs/design/aif.md`)
  - [ ] conditions 9–10 (in `docs/experiment/design.md` and `AGENTS.md`)
  - [ ] aif/ module decision (in `docs/design/aif.md`)
  - [ ] multi-focal runtime (in `docs/design/multi_focal.md`)
  - [ ] `payoff_mode='graded'` (in `docs/theory/pomdp_spec.md` and `docs/design/trust.md`)
  - [ ] simultaneous-moves convention (in `docs/design/multi_focal.md`)
- [ ] No code changes (E is documentation-only)
- [ ] `docs/experiment/manifest.md` is unchanged (D's deliverable, E only references it)
- [ ] `docs/superpowers/` and `docs/paper/` are unchanged

### Task 16.4: Stat the diff

```bash
git diff --stat main...HEAD
```

Expected: ~14 markdown files modified, 3 new test files, 2 directory changes (rename + delete). Net ~3000 lines (after pruning ~1000 lines from the previous 3650-line surface).

### Task 16.5: Open PR with paste of verification output

PR description includes:
- output of `pytest --ignore=tests/test_cvc_*.py` (green)
- output of `git diff --stat main...HEAD`
- the manual review checklist (all ticked)
- the rq-labels allow-list rationale (link to `docs/experiment/design.md` naming-history section)

---

## Acceptance criteria checklist

(Mirrors spec section 4.2; tick on PR description before merging.)

- [ ] **Tree shape**: 14 in-scope docs exist per Section 1; `docs/design/`, `docs/research/`, `docs/operations/`, `docs/theory/`, `docs/experiment/` populated; `docs/future/` removed; `docs/design/implementation.md` and `docs/design/partner_stance.md` removed (content merged into `trust.md`).
- [ ] **Labels**: `tests/test_rq_labels.py` passes — zero `H[1-9]` mentions in in-scope docs (excluding allow-listed naming-history subsection in `docs/experiment/design.md`).
- [ ] **Links**: `tests/test_doc_links.py` passes — every internal `.md` link resolves.
- [ ] **Inventory**: `tests/test_doc_inventory.py` passes — exactly the expected file set, CLAUDE.md ≤ 15 lines, paper/superpowers excluded.
- [ ] **Stale content**: REWRITE files contain zero references to `o_intero` as observation channel, `horizon_sweep.json`, `deep_affect_test.json`, `variational_beta`, `AIFPolicy` (manual review).
- [ ] **New content present**: each of the 8 missing-content topics has a section in its target doc with substantive content (>1 paragraph).
- [ ] **Audience contract live**: `docs/README.md` exists with audience-contract table; top-level `README.md` links to it.
- [ ] **Manifest unchanged**: `docs/experiment/manifest.md` is referenced from design.md, results.md, AGENTS.md, but the file itself is untouched by E.
- [ ] **Pre-existing test suite passes**: `pytest --ignore=tests/test_cvc_*.py` green.
- [ ] **Pre-commit hooks pass**.
- [ ] **STATE.md updated**: `next_priority` cleared of "sub-project E"; `next_session_focus` advances to post-E reruns; pending docs items cleared.

---

## Out of scope (do NOT do in this PR)

- Updating `docs/paper/main.tex` — paper is out of scope per scoping doc.
- Updating `docs/superpowers/specs/*` and `docs/superpowers/plans/*` — historical records.
- Code changes — E is documentation-only. Any code/docstring drift surfaced during writing gets logged in STATE.md as a follow-up item, not fixed in this PR.
- Adding new figures / diagrams — text-only rewrite.
