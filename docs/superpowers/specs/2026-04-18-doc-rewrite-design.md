# sub-project E — documentation rewrite (design)

date: 2026-04-18
status: design — ready for `writing-plans`
parent scoping: `docs/superpowers/specs/2026-04-18-codebase-restructure-scoping.md`
upstream specs:
- `docs/superpowers/specs/2026-04-18-aif-extraction-design.md` (B+A — designed, not yet implemented)
- `docs/superpowers/specs/2026-04-18-multi-focal-runtime-design.md` (F — completed, configs landed)
- `docs/superpowers/specs/2026-04-18-experiment-pruning-design.md` (D — designed, ready for plan)
upstream required-before-merge: D's `docs/experiment/manifest.md` must exist (E references it as canonical config↔RQ↔analysis map and does not write to it)

---

## why this doc exists

the scoping audit (section "docs (clean rewrite)") found the documentation surface had drifted in five ways:

1. **stale content**: jax-first language (project is numpy-first; jax is optional), `o_intero` interoceptive observation channel (removed in pomdp v4), beta-as-pomdp-factor framing (also removed in v4), dead config refs (`horizon_sweep.json`, `deep_affect_test.json`), and outdated source-tree drawings in `AGENTS.md`.
2. **broken cross-links**: 8 internal markdown links resolve to nonexistent files (e.g. `AGENTS.md` references `docs/theory.md`, `docs/experiment.md`, `docs/implementation.md` — none exist; the actual paths are `docs/theory/theory.md`, `docs/experiment/design.md`, `docs/design/implementation.md`).
3. **content duplications**: stance design appears in 5 files, cli docs in 3, empirical narrative in 4. no single source of truth.
4. **missing content**: factorized controls, `log_policy_prior`, dirichlet learning flags, conditions 9–10 (tau3 pair), the `aif/` package decision (B+A outcome), the multi-focal runtime (F outcome), and the `payoff_mode='graded'` extension are all undocumented.
5. **hypothesis-label drift**: ~58 in-scope mentions of `H[1-9]` will conflict with D's RQ#/E# rename. E ports the new vocabulary into the doc surface.

E's job is to land a coherent doc rewrite that addresses all five at once and locks in CI gates so future drift is caught at merge time.

E's job is **not** to:
- modify code (documentation-only; if rewrites surface code/docstring drift, log to STATE.md as follow-up)
- update `docs/paper/main.tex` (paper rewrite is a separate effort)
- update `docs/superpowers/*` (historical records, not the in-scope doc surface)
- run experiments (reruns happen after E.1's `results.md` placeholder structure lands)

---

## decisions log

| id | decision | reasoning |
|---|---|---|
| E1 | Target shape: moderate (~14 in-scope docs) with `docs/<area>/` subdir structure that supports future expansion. Reorganize content properly (not surgical-edits-only). | per user: "moderate but reorganize properly & leave door open for future expansion" |
| E2 | Keep `docs/design/` directory name (do not rename to `docs/engineering/`). Inside: `aif.md`, `trust.md`, `multi_focal.md`. | per user: less disruption to existing cross-links and naming continuity |
| E3 | Merge `docs/design/partner_stance.md` into `docs/design/trust.md` as a "stance" section (3 design docs, not 4). | stance is part of the trust model, not a separable concept; cleaner top-level surface |
| E4 | Collapse `CLAUDE.md` to a 5–15 line pointer to `AGENTS.md`. AGENTS.md becomes canonical for all agent-facing conventions. | eliminates duplication; Claude Code reads CLAUDE.md by default so file remains, but content lives in one place |
| E5 | Add `docs/README.md` as a top-level doc index with audience-contract table. | navigation aid; tells readers "what's where, who reads what" without bloating the project README |
| E6 | Rename `docs/future/` → `docs/research/`. | "future" implied "not now"; "research" reflects the actual content (open questions + roadmap) |
| E7 | New files: `docs/design/aif.md` (B+A outcome), `docs/design/multi_focal.md` (F outcome), `docs/README.md` (index). | the missing-content audit + audience contract requires three new files |
| E8 | REWRITE files (6): `README.md`, `AGENTS.md`, `docs/theory/theory.md`, `docs/experiment/design.md`, `docs/experiment/results.md`, `docs/research/roadmap.md`. EDIT files (3): `docs/theory/pomdp_spec.md`, `docs/operations/cli.md`, `docs/operations/benchmark.md`. REWRITE+MERGE (1): `docs/design/trust.md`. NEW (3): `docs/README.md`, `docs/design/aif.md`, `docs/design/multi_focal.md`. COLLAPSE (1): `CLAUDE.md`. | per-doc plan in section 2 |
| E9 | Three new pytest validators: `tests/test_doc_links.py` (broken links), `tests/test_rq_labels.py` (no stale H#), `tests/test_doc_inventory.py` (file structure matches target). | locks in the rewrite so future PRs can't drift; runs in CI |
| E10 | Single PR rollout (Option A). All content + validators land in one diff. Commit-by-commit ordering keeps the PR reviewable as 15 small commits. | per user: "validators land with the content they validate; reviewer sees the whole picture in one diff" |

---

## section 1 — target doc tree

net change: 12 in-scope docs today + 1 from D (`manifest.md`) → **14 in-scope docs after E** (3 added: `aif.md`, `multi_focal.md`, `docs/README.md`; 2 removed: `implementation.md` and `partner_stance.md` merged into `trust.md`; CLAUDE.md collapses but file remains). The structure changes; the count is roughly stable.

```
README.md                             # external visitors / quickstart (REWRITE, ~80 lines)
AGENTS.md                             # canonical agent/coding-rules doc (REWRITE)
CLAUDE.md                             # 5–15 line pointer to AGENTS.md (COLLAPSE from 222 lines)

docs/
├── README.md                         # NEW — top-level index + audience-contract table
│
├── theory/
│   ├── pomdp_spec.md                 # KEPT — formal generative model spec, surgical edits
│   └── theory.md                     # REWRITTEN — RQ-shaped narrative; pomdp_spec linked
│
├── design/
│   ├── aif.md                        # NEW — generic active-inference package (from B+A)
│   ├── trust.md                      # REWRITE+MERGE: was design/implementation.md +
│   │                                 #                design/partner_stance.md
│   └── multi_focal.md                # NEW — multi-focal-agent runtime (from F)
│
├── experiment/
│   ├── design.md                     # REWRITTEN — RQ1–7 + E1–2 protocols (replaces H1–H7)
│   ├── results.md                    # REWRITTEN — rolling per-RQ results narrative
│   └── manifest.md                   # FROM D — config ↔ RQ ↔ analysis map (untouched by E)
│
├── operations/
│   ├── cli.md                        # KEPT, stale-content sweep
│   └── benchmark.md                  # KEPT, stale-content sweep
│
├── research/                         # RENAMED from docs/future/
│   └── roadmap.md                    # REWRITTEN — refresh against post-restructure state
│
├── superpowers/                      # EXISTING — specs/, plans/ (out of scope)
└── paper/                            # EXISTING — out of scope
```

### audience contract (lives at the top of `docs/README.md`)

| audience | reads |
|---|---|
| external visitor / first time | `README.md` |
| AI coding agent (Cursor, Claude Code) | `AGENTS.md` (and `CLAUDE.md` pointer) |
| researcher / theorist | `docs/theory/*`, `docs/experiment/*`, `docs/research/*` |
| maintainer / engineer | `docs/design/*`, `docs/operations/*` |
| reviewer of past decisions | `docs/superpowers/specs/`, `docs/superpowers/plans/` |
| paper consumer | `docs/paper/main.pdf` (out of E scope) |

### future-expansion door (called out in `docs/README.md` so it doesn't get re-collapsed)

| if/when… | new doc lands here |
|---|---|
| CvC track unfreezes | `docs/design/cogames.md` + `docs/experiment/cvc.md` |
| Human data lands (Phase 8) | `docs/experiment/human_fits.md` |
| New sub-project on top of B+A | `docs/superpowers/specs/<date>-<name>-design.md` (existing pattern) |
| New analysis methodology | `docs/operations/analysis.md` |
| Per-RQ deep dive needed | `docs/research/rq#_<name>_deepdive.md` |

### file moves / renames summary

| from | to | action |
|---|---|---|
| `docs/design/implementation.md` | `docs/design/trust.md` | rename + section-merge with partner_stance + refresh |
| `docs/design/partner_stance.md` | folded into `docs/design/trust.md` ("stance" section) | section-merge |
| `docs/future/roadmap.md` | `docs/research/roadmap.md` | dir rename + rewrite |
| `docs/design/` (dir) | kept (not renamed to engineering) | per E2 |
| `docs/future/` (dir) | removed (empty after move) | cleanup |
| `CLAUDE.md` (~222 lines) | content → `AGENTS.md`; `CLAUDE.md` becomes pointer | content moves |

---

## section 2 — per-doc rewrite/edit plan

action codes: **REWRITE** (start fresh, may reuse sections), **EDIT** (surgical: fix stale, update labels), **NEW** (didn't exist), **COLLAPSE** (most content moves elsewhere; file becomes a stub), **KEEP** (no E action; touched only by sweep).

### top-level (3 files)

| file | action | target lines | scope |
|---|---|---|---|
| `README.md` | REWRITE | ~80 | project intro paragraph, quickstart (install + `smoke_focal.json`), RQ summary table linking to `docs/experiment/design.md`, audience-contract pointer to `docs/README.md`, license/citation. Kill: old hypothesis names, `o_intero`, jax-first language. Fix broken link to `docs/cli.md` → `docs/operations/cli.md`. |
| `AGENTS.md` | REWRITE | ~250 | absorb relevant `CLAUDE.md` content; canonical agent rules + workflow + skills; condition table 1–8 + 9–10 (currently inconsistent per audit); RQ#→config map (1-line per RQ pointing to `manifest.md`); coding conventions; pre-commit gates. Fix all 5 broken links (theory.md, experiment.md, implementation.md, benchmarking_integration.md, results_tracking.md). |
| `CLAUDE.md` | COLLAPSE | ~10 | `# Claude Code` heading, one paragraph: "this project's agent-facing conventions live in `AGENTS.md`", pointer link, plus any Claude-Code-only directives that don't fit AGENTS.md (e.g. specific to Claude Code's hook system if any). Sentinel: <= 15 lines. |

### `docs/` (1 new index)

| file | action | target lines | scope |
|---|---|---|---|
| `docs/README.md` | NEW | ~60 | top-level doc index: ToC per directory + audience contract + future-expansion door. No content beyond navigation. |

### `docs/theory/` (2 files)

| file | action | target lines | scope |
|---|---|---|---|
| `docs/theory/theory.md` | REWRITE | ~450 (from 615) | RQ-shaped narrative. Reorganize: motivation → POMDP framing (link `pomdp_spec.md`, no duplication) → RQ1 (depth) → RQ2 (affect value) → RQ3 (lesion) → RQ4 (betrayal) → RQ5 (partner selection) → RQ6 (graded channel) → RQ7 (clinical). Drop H6/H7 narrative entirely (move to `docs/research/roadmap.md`). Kill: jax-first, `o_intero`, beta-as-pomdp-factor. Add: factorized controls, `log_policy_prior`, dirichlet learning flags, conditions 9–10. Kill broken link to `docs/action-dependent-partner-design.md`. |
| `docs/theory/pomdp_spec.md` | EDIT | ~340 (kept) | confirm alignment with B+A canonical `TrustGameModel`. Add appendices: "extension: graded payoff (`payoff_mode='graded'`)", "extension: factorized controls `[1,2,2]` / `[N,2,2]`", "documented divergences from apashea v4" (log-softmax C[1], optional dirichlet, etc.). Beta references already correct (v4 externalized) — no kill. |

### `docs/design/` (3 files)

| file | action | target lines | scope |
|---|---|---|---|
| `docs/design/aif.md` | NEW | ~250 | generic active-inference package (per B+A spec). Module-by-module overview: `aif.backend`, `aif.maths`, `aif.utils`, `aif.efe`, `aif.policies`, `aif.learning`, `aif.runtime`, `aif.affect.beta`, `aif.affect.interoception`. The `aif.Agent` shell. Public surface, what's *not* in here (anything trust-specific). How to extend: new affect modules, new examples. Reference: B+A spec for design rationale. |
| `docs/design/trust.md` | REWRITE+MERGE | ~500 (from 158 + 320 input) | merges old `design/implementation.md` + `design/partner_stance.md`. Sections: trust-game project module overview → `TrustGameModel` (canonical, `payoff_mode={binary, graded}`) → `TrustGameAgent` (multi-partner joint beliefs) → partner stance dynamics (was partner_stance.md, refreshed) → factorized env wiring → `decision_step_trust_game` → rollout. Refresh per B+A: aif/ extraction completed, generative model unified, `infer_joint_posterior` status documented per B+A decision. |
| `docs/design/multi_focal.md` | NEW | ~200 | F runtime overview. Sections: motivation (M focal AIF agents vs 1 focal + scripted) → `experiment/multi_focal_runner.py` → pairing rules (round-robin, all-pairs, random, mutual-selection) → joint game resolution → heterogeneous populations (config schema example) → simultaneous-moves convention (decision F4) → emergent dynamics tests (gated `slow`). Reference F's spec for design rationale. |

### `docs/experiment/` (3 files)

| file | action | target lines | scope |
|---|---|---|---|
| `docs/experiment/design.md` | REWRITE | ~500 (from 585) | RQ1–7 + E1–2 protocol descriptions per D's spec section 1. Replaces H1–H7 framing entirely. Updates: POMDP section to v4 (no `o_intero`, external beta), Conditions section (1–8 + 9–10), Variants section (binary + graded), removed-experiment-surface section pruned (variational_beta, AIFPolicy already removed in C). Section ordering: motivation → task setup → conditions → RQs → engineering objectives → analysis pointers (→ `manifest.md`). Kill: jax-first, old hypothesis names, dead config refs. H6 (predictive comparison) moves to `docs/research/roadmap.md`. Fix broken links to `docs/action-dependent-partner-design.md` and `docs/results_tracking.md`. |
| `docs/experiment/results.md` | REWRITE | ~300 (from 600) | rolling per-RQ results narrative. Placeholder `status: needs_rerun \| pending \| complete \| future` blocks for each RQ until reruns land. Each RQ block: question recap, current evidence (or "post-restructure rerun pending"), interpretation, links to result CSVs and figures. Cross-references `manifest.md`. Kill: pre-restructure result tables that no longer compare. |
| `docs/experiment/manifest.md` | FROM D | (D's deliverable) | E does NOT touch this file. E only links to it. |

### `docs/operations/` (2 files)

| file | action | target lines | scope |
|---|---|---|---|
| `docs/operations/cli.md` | EDIT | ~94 (kept) | stale-content sweep: update CLI examples to new config names (`rq2_shallow_affect.json` not `shallow_affect_confirm.json`). Confirm `scripts/run_experiment.py` and `scripts/run_analysis.py` examples accurate post-D (analysis output is `research_questions.json` not `hypothesis_tests.json`). |
| `docs/operations/benchmark.md` | EDIT | ~247 (kept) | sweep for old config names; update for `e1_benchmark_arena.json` (merged), `e1_benchmark_betrayal_*.json` (renamed), `e2_multifocal_*.json` (renamed). Update for any C/F changes (variational_beta removed, AIFPolicy removed). |

### `docs/research/` (1 file, was `docs/future/`)

| file | action | target lines | scope |
|---|---|---|---|
| `docs/research/roadmap.md` | REWRITE | ~250 (from 202) | refresh against post-restructure state. Sections: completed sub-projects (B+A, C, F, D, E) → pending sub-projects (post-D reruns sequenced per STATE.md) → near-term research (RQ-aligned: shallow rerun, partner selection, clinical) → mid-term (graded channel deeper, multi-focal emergent dynamics deep dive) → long-term (H6 predictive model comparison, human data fits Phase 8, BMR / structure learning Phase 7+). |

### total writing work (rough)

- 6 REWRITE files: README, AGENTS, theory, experiment/design, results, roadmap (~1660 lines net new content after pruning)
- 1 REWRITE+MERGE: design/trust (~500 lines, from 478 input)
- 3 NEW files: docs/README, design/aif, design/multi_focal (~510 lines)
- 1 COLLAPSE: CLAUDE (~10 lines from 222)
- 3 EDIT (surgical): pomdp_spec, cli, benchmark (~680 lines kept, light touch)

---

## section 3 — cross-cutting sweep specifications

### 3.1 H# → RQ#/E# label sweep (mechanical, deterministic)

per D's spec section 1, the canonical mapping:

| old | new | semantic |
|---|---|---|
| H1 | RQ1 | depth understanding (was "depth redundancy") |
| H2 | RQ2 | affect value (was "affect orthogonal augmentation") |
| H3 | RQ3 | lesion dissociation |
| H4 | RQ4 | betrayal recovery |
| H5 (analysis-code: post-switch) | merged into RQ4 (duplicate per D's audit) |
| H5 (config: partner selection) | RQ5 | partner selection |
| H6 (graded) | RQ6 | graded channel |
| H7 (clinical) | RQ7 | clinical phenotypes |
| H8 (benchmark) | E1 | benchmark / arena (engineering objective) |
| H9 (multi-focal) | E2 | multi-focal runtime (engineering objective) |
| H6 (predictive comparison) — never implemented | → moved to `docs/research/roadmap.md` as future work |

**footprint (in-scope)**: ~58 mentions across 7 files (theory.md:2, experiment/design.md:17, experiment/results.md:34, future/roadmap.md:2, operations/cli.md:1, AGENTS.md:4). Five files are full REWRITEs in E (renames happen as part of rewrite); EDIT files (cli.md) get sweep-only pass.

**also rename associated artifact references**:
- `hypothesis_tests.json` → `research_questions.json` (matches D's analysis output rename)
- "hypothesis scorecard" → "research-question scorecard"
- "test H#" / "validates H#" prose → "characterizes RQ#" / "answers RQ#"

### 3.2 stale-content kills (per-file)

| stale item | files affected | action |
|---|---|---|
| jax-first language ("jax pmap", "vmap-friendly", "jax-native") | `docs/design/partner_stance.md`, `docs/experiment/design.md` | killed during REWRITE/MERGE; project is numpy-first, jax is optional |
| `o_intero` interoceptive observation channel | `docs/experiment/design.md:92` (genuinely stale; line 533 is about behavioral measure for human fits — KEEP) | killed during REWRITE; level-3 transition description rewritten to v4 (external beta tracker, no intero observation) |
| beta-as-pomdp-factor | `docs/theory/pomdp_spec.md` (CORRECT — v4 externalized; no kill needed) | NO ACTION |
| dead config refs (`horizon_sweep.json`, `deep_affect_test.json`, `variational_beta`, `AIFPolicy`) | theory.md, experiment/design.md, experiment/results.md, future/roadmap.md | killed during REWRITE (all four are REWRITE targets) |
| outdated post-restructure source-tree drawings | `AGENTS.md` (lines 60–65) | refresh during REWRITE per current `affect_aif/` layout post-B+A and post-C |
| stance-design duplication (currently in 5 files) | resolved by REWRITE+MERGE: stance design lives in `docs/design/trust.md` only; other docs link to it |
| cli-docs duplication (currently in 3 files) | resolved: `cli.md` canonical; `benchmark.md` only documents benchmark-specific extensions; `AGENTS.md` links to `cli.md` |
| empirical-narrative duplication (currently in 4 files) | resolved: `docs/experiment/results.md` canonical; other docs link to it |

### 3.3 missing-content additions (where each lands)

| topic | lands in | section |
|---|---|---|
| factorized controls (`[1,2,2]` / `[N,2,2]`) | theory.md (rewrite) and pomdp_spec.md (edit, appendix) | "factorized control space" |
| `log_policy_prior` (log-softmax C[1] vs raw apashea v4) | pomdp_spec.md (edit, divergences appendix) and design/aif.md (NEW, where it lives in code) | "documented divergences from apashea v4" |
| dirichlet learning flags (optional A/B priors) | theory.md (rewrite, learning section) and design/aif.md (NEW, `aif.learning` overview) | "online learning of A/B" |
| conditions 9–10 (tau3 pair) | experiment/design.md (rewrite, conditions section) and AGENTS.md (rewrite, condition table) | "experimental conditions" |
| aif/ module decision (B+A outcome) | design/aif.md (NEW file) | entire file |
| multi-focal runtime (F outcome) | design/multi_focal.md (NEW file) | entire file |
| `payoff_mode='graded'` (C track) | pomdp_spec.md (edit, extension appendix) and design/trust.md (rewrite+merge, model section) | "extension: graded payoff" |
| simultaneous-moves convention (decision F4) | design/multi_focal.md (NEW) and brief mention in experiment/design.md | "joint resolution" |

### 3.4 broken-link inventory (must-fix in E)

| file:line | broken link | fix |
|---|---|---|
| `README.md:18` | `docs/cli.md` | `docs/operations/cli.md` (also rewritten in E to use new index) |
| `AGENTS.md:7` | `docs/theory.md` | `docs/theory/theory.md` |
| `AGENTS.md:8` | `docs/experiment.md` | `docs/experiment/design.md` |
| `AGENTS.md:9` | `docs/implementation.md` | post-E: `docs/design/trust.md` |
| `AGENTS.md:31` | `docs/benchmarking_integration.md` | `docs/operations/benchmark.md` |
| `AGENTS.md:208` | `docs/results_tracking.md` | `docs/experiment/results.md` |
| `docs/theory/theory.md:7` | `docs/action-dependent-partner-design.md` | killed; never existed |
| `docs/experiment/design.md:7` | `docs/action-dependent-partner-design.md` | killed; never existed |
| `docs/experiment/design.md:493` | `docs/results_tracking.md` (absolute path) | `docs/experiment/results.md` (relative path) |
| `docs/design/implementation.md:58` | `docs/theory.md` (absolute path) | `docs/theory/theory.md` (relative); file merged into `docs/design/trust.md` so link gets updated as part of merge |
| `CLAUDE.md` (multiple) | various stale paths | moot — file collapses to pointer |

E adds an automated check (section 4) so future broken links don't accumulate.

### 3.5 style and convention conventions (uniform across all rewrites)

- **headings**: title case for H1, sentence case for H2+, no terminal punctuation
- **code refs**: backticks for file paths, function names, config names; relative-path links for internal docs
- **RQ language**: "RQ#: <descriptive question>" not "H#: <claim to prove>"; "characterize / measure / answer" verbs not "prove / show / demonstrate"
- **status markers in `results.md`**: `status: complete | needs_rerun | pending | future` (machine-parseable for the section-4 validator)
- **cross-references to manifest**: any doc that mentions a config-RQ-analysis triple links to `docs/experiment/manifest.md` rather than restating the mapping (single source of truth per D)
- **removed items**: when killing a config or function, leave a one-line "removed in <date>: see manifest.md" footnote rather than silent deletion (helps git blame / archaeology)

---

## section 4 — validators + acceptance criteria

### 4.1 validators (new CI checks)

three new pytest validators, runnable locally and in CI:

#### validator 1: `tests/test_doc_links.py` — broken-link sweep

```python
"""verify every internal markdown link in in-scope docs points to an existing file."""

# scans: README.md, AGENTS.md, CLAUDE.md, docs/**/*.md
# excludes: docs/paper/, docs/superpowers/
# for each [text](path.md[#anchor]) link, asserts path resolves
# fails on first broken link with file:line and the bad path
```

#### validator 2: `tests/test_rq_labels.py` — no stale H# labels

```python
"""verify in-scope docs have migrated H# → RQ#/E# labels."""

# scans: README.md, AGENTS.md, docs/theory/, docs/experiment/, docs/design/,
#        docs/operations/, docs/research/
# excludes: docs/superpowers/, docs/paper/
# regex: r'\bH[1-9]\b'
# fails with file:line of any match
# allow-list: a single 'naming history' subsection in docs/experiment/design.md
#             may reference H1-H9 for historical continuity (marked by HTML comment
#             <!-- rq-labels:allow --> ... <!-- rq-labels:end -->)
```

#### validator 3: `tests/test_doc_inventory.py` — file structure matches target tree

```python
"""verify in-scope doc tree matches the spec."""

# expected_paths = [<the 14 files from section 1>]
# unexpected_paths = scan docs/** + top-level for *.md, subtract expected,
#                    subtract paper/superpowers/
# asserts no unexpected paths (catches new docs added without updating docs/README.md)
# asserts all expected paths exist
# asserts CLAUDE.md is <= 15 lines (sentinel for "still a pointer")
```

#### existing validators (unchanged but exercised)

- D's `tests/test_manifest_consistency.py` already covers config↔RQ↔analysis. E does not extend it.

### 4.2 acceptance criteria for E

E is "done" when:

1. **tree shape**: 14 in-scope docs exist per section 1; `docs/design/`, `docs/research/`, `docs/operations/`, `docs/theory/`, `docs/experiment/` populated as specified; `docs/future/` removed; `docs/design/implementation.md` and `docs/design/partner_stance.md` removed (content merged into `trust.md`).
2. **labels**: `tests/test_rq_labels.py` passes — zero `H[1-9]` mentions in in-scope docs (excluding allow-listed naming-history subsection).
3. **links**: `tests/test_doc_links.py` passes — every internal `.md` link resolves.
4. **inventory**: `tests/test_doc_inventory.py` passes — exactly the expected file set, CLAUDE.md ≤ 15 lines.
5. **stale content**: REWRITE files contain zero references to `o_intero` as observation channel, `horizon_sweep.json`, `deep_affect_test.json`, `variational_beta`, `AIFPolicy` (manual-review checklist; not automated).
6. **new content present**: each of the 8 missing-content topics in section 3.3 has a section in its target doc with substantive content (>1 paragraph). Manual review checklist in PR description.
7. **audience contract live**: `docs/README.md` exists with audience-contract table; top-level `README.md` links to it.
8. **manifest unchanged**: `docs/experiment/manifest.md` (D's deliverable) is referenced from design.md, results.md, AGENTS.md, but the file itself is untouched by E.
9. **pre-existing test suite passes**: `pytest` green (no behavior change in E expected; new doc validators are new gates).
10. **pre-commit hooks pass**: any markdown-lint or formatter (per `.pre-commit-config.yaml`) clean.
11. **STATE.md updated**: `next_priority` cleared of "sub-project E"; `next_session_focus` advances to post-E reruns (per D's spec section 4); pending docs items cleared.

### 4.3 out of scope for E

- updating `docs/paper/main.tex` — paper is out of scope per scoping doc; separate effort.
- updating `docs/superpowers/specs/*` and `docs/superpowers/plans/*` — historical records, not the in-scope doc surface.
- code changes — E is documentation-only. Any code change exposed by writing docs (e.g. docstring inconsistency) gets logged in STATE.md and handled separately.
- adding new figures / diagrams — text-only rewrite. If figures become necessary, tracked as follow-ups.

---

## section 5 — rollout strategy

### 5.1 PR shape

**single PR (Option A)**: all content + validators in one diff (~14 file rewrites + 3 new validators + 2 directory moves + 2 file deletions). Validators land with the content they validate; reviewer sees the whole picture in one diff.

per E10: validators codify expectations that should be applied in the same PR that creates the docs they validate. otherwise a two-PR split risks the content PR landing without lock-in, and the validator PR potentially failing on subtle drift.

### 5.2 within the single PR, work order (commit-by-commit)

to keep the PR reviewable as small commits:

| commit | scope | reviewability |
|---|---|---|
| 1 | structural moves: `mv docs/future docs/research`, `git rm docs/design/implementation.md docs/design/partner_stance.md` (placeholders, content not yet merged in this commit) | small, mechanical |
| 2 | broken-link fixes in non-rewritten files (README, pre-rewrite AGENTS) | small, mechanical |
| 3 | NEW: `docs/README.md` (audience-contract index) | small, new content |
| 4 | NEW: `docs/design/aif.md` | medium, new content |
| 5 | NEW: `docs/design/multi_focal.md` | medium, new content |
| 6 | REWRITE+MERGE: `docs/design/trust.md` (consumes implementation.md + partner_stance.md content; deletions from commit 1 now have a destination) | large diff but self-contained |
| 7 | REWRITE: `docs/theory/theory.md` | large |
| 8 | EDIT: `docs/theory/pomdp_spec.md` (appendix additions) | small |
| 9 | REWRITE: `docs/experiment/design.md` | large |
| 10 | REWRITE: `docs/experiment/results.md` | medium |
| 11 | EDIT: `docs/operations/cli.md`, `docs/operations/benchmark.md` (sweep) | small |
| 12 | REWRITE: `docs/research/roadmap.md` | medium |
| 13 | REWRITE: top-level `AGENTS.md`, `README.md`; COLLAPSE: `CLAUDE.md` | medium |
| 14 | STATE.md update + final cross-link sweep (every doc's links to renamed/moved targets) | small, mechanical |
| 15 | NEW: validators (`tests/test_doc_links.py`, `tests/test_rq_labels.py`, `tests/test_doc_inventory.py`) | small, contained |

### 5.3 risk + mitigation

| risk | likelihood | mitigation |
|---|---|---|
| H# slips through in a quoted code block / config name | medium | validator 2 fails CI; allow-listed via HTML comment for legitimate cases |
| Internal links break mid-PR (e.g. AGENTS.md links to `docs/design/trust.md` but commit 13 lands before commit 6) | medium | order commits so dependencies land first; validator 1 runs against final tree only |
| Doc inventory drift if reviewer requests a new doc mid-review | low | validator 3 fails CI; updating expected list is a one-line change |
| Content regression (rewriter loses important detail from old doc) | medium | manual review + `git diff --stat` shows total line count; rewrites should preserve ≥80% of substantive content (paraphrased, not just deleted) |
| CLAUDE.md collapse loses Claude-Code-specific directives that don't fit AGENTS.md | low | review CLAUDE.md content carefully before collapsing; preserve Claude-only items inline in pointer file with a "Claude-only" subsection if any |
| Manifest references go stale if D's manifest.md changes between D-merge and E-merge | low | E pulls manifest.md from main at start of work; if D's manifest evolves during E, rebase |

### 5.4 sequencing relative to D and other sub-projects

```
D merged → D's manifest.md exists → E starts → E merged
                                                   │
                                          CI lock now in place;
                                          future PRs can't drift.
                                                   │
                                  reruns of pending experiments
                                  (rq2_shallow_affect, rq5_partner_selection,
                                   rq7_clinical_betrayal, rq7_clinical_phenotypes)
                                  can land — E's results.md has placeholder slots ready.
```

E does not block reruns; reruns can begin after E lands (results.md has the structure waiting).

### 5.5 estimated effort (rough)

- content (commits 1–14): ~2 days of writing/editing (14 docs, ~3000 lines net new content after pruning, much paraphrased from existing material)
- validators (commit 15): ~0.5 day (3 validators, each ~50 lines of pytest)

---

## handoff

next steps:
1. commit this design doc to `main` (or to E's worktree branch)
2. invoke `writing-plans` skill against this spec to produce `docs/superpowers/plans/2026-04-18-doc-rewrite-plan.md`
3. execute the plan as a single PR per section 5
4. after E merges: STATE.md update unblocks the post-D reruns

dependencies:
- D must merge first (E references D's `manifest.md` and uses D's RQ#/E# labels, `research_questions.json` filename)
- B+A must be implemented before E (E's `docs/design/aif.md` documents the as-built `aif/` package; if B+A is still in design phase when E starts, `aif.md` documents the design and gets updated during B+A implementation)
- F is already complete (E's `docs/design/multi_focal.md` documents the as-built F runtime)
