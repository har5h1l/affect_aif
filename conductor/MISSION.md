# Mission

## Objective
Polish the affect-augmented AIF paper for submission. All research tracks (theory, CvC benchmark, experiments) are complete. The remaining work is paper-level fixes identified by systematic review.

## Guiding Principles
- Variational principles and docs/theory.md are the north star
- Trust-game results (Phases 1-7) and CvC benchmark are complete — do not re-run experiments
- The paper compiles clean (zero LaTeX warnings). Keep it that way.
- Prioritize issues that a reviewer would flag over cosmetic improvements

## Completed Work
- Phases 1-7: All research phases complete with publication-quality results
- Track 1: All 5 paper theory gaps addressed (inside-out framing, precision modulation tested, vmPFC grounding, BMR framing, clinical differentiation)
- Track 2: CvC benchmark complete (ScoringLoopPolicy 0.072, AffectCvCPolicy 0.071, StarterPolicy 0.000)
- Track 3: Paper updated with all results, CvC section, precision modulation section
- All 197 tests pass, paper compiles clean

## Current Focus: Paper Polish

Issues found by systematic review (3 parallel reviewer agents + independent checks):

### CRITICAL (must fix)

#### P1. Clinical d sign convention inconsistency
Tables 6 (graded betrayal, ~line 384) and 7 (Stag Hunt, ~line 413) use opposite sign conventions for Cohen's d:
- Table 6: d = (phenotype - healthy), so alexithymia d=+0.80 means *outperforms*
- Table 7: d = (healthy - phenotype), so borderline d=+0.72 means *impaired*

Pick one convention and apply consistently. Natural choice: d = (phenotype - reference), positive = better. Add a footnote or column annotation.

#### P2. Missing somatosensory citation (~line 532)
Future Work BMR paragraph cites specific timing claims (70ms, 140ms) with no citation. The "Neural surprise somatosensory paper" referenced in MISSION Track 1.4 was never actually added to the bibliography. Either find and add the citation, or remove the specific timing claims.

### IMPORTANT (should fix)

#### P3. No figures in the paper
The paper has 10 tables but zero figures. Unused packages: `graphicx`, `subcaption`. At minimum add:
1. Beta trajectory plot showing betrayal response (the key mechanism visualization)
2. Clinical phenotype comparison (borderline progressive deterioration vs depression self-correction)
3. Optionally: architecture schematic

#### P4. Tables and equations never cross-referenced in prose
`eq:precision_weight` (the core equation) and most result tables are defined with `\label{}` but never referenced via `\ref{}`. Add "as shown in Table X" style references throughout.

#### P5. Empty author affiliation (~line 35)
`\affil[1]{}` is blank — visible placeholder.

#### P6. Approximate C8 values
C8 results reported as "≈576" with no p-value in Tables 3 and 4. Every other condition has exact values. Report exact C8 mean or explain why only approximate value is available.

#### P7. Abstract d=1.72 comparison may be misleading (~line 45)
The abstract says "reward averaging dominating in continuous-investment settings (d=1.72)". This d=1.72 is C5 vs C4 (reward-avg vs no-affect baseline), NOT C5 vs C2 head-to-head. The "dominating" framing implies C5 vs C2, which is d=0.43/0.89. Clarify or use the head-to-head effect size.

#### P8. Bibliography not alphabetically sorted
Behrens, Mishchanchuk, Yoshida appended at end out of order (lines 654-668). Re-sort.

### SUGGESTIONS

#### P9. "Phase 4" terminology leak (line 137)
Internal project terminology. Replace with content description.

#### P10. Sparse Implementation section (lines 549-553)
No repo URL, no JAX version, no hardware info, no runtime. Either expand or convert to a "Code Availability" paragraph.

#### P11. Missing Sennesh/Ramstead reference
MISSION Track 3.4 requested it but it was never added. Check if the paper needs it or if it's no longer relevant.

### CODE CLEANUP (low priority)

#### C1. Dead `stuck_steps` state in CvC policies
`stuck_steps` and `stuck_counter` in cvc_affect_policy.py and cvc_navigation.py are tracked but never read. Remove or use.

#### C2. Docstring mismatch in cvc_navigation.py (line 18)
Example shows `update_position(nav_state, moved, last_action)` but actual API is `update_position(state, moved)`.

#### C3. Hardcoded server path in benchmark_cvc_comparison.json (line 32)
`python_bin` is `/Users/server/miniforge3/envs/cvc/bin/python`. Should be `python3.12` for portability.

#### C4. No navigation unit tests
NavigationHelper received significant changes (wall expiry, aoe_mask) but has no dedicated tests.

### DOCS CLEANUP

#### D1. C9-C11 missing from experiment.md
Clinical conditions are defined in theory.md and the paper but not in the canonical experiment design document.

#### D2. Track 1.2 result CSVs not on local machine
The precision modulation experiment ran on the server; raw CSVs were not fetched. Consider re-running locally (50 seeds × 120 rounds, ~10 min) for reproducibility.

## Constraints
- Follow all safety invariants from CLAUDE.md
- Tests must pass before any changes
- Paper must compile clean (zero warnings) after every change
- Do NOT re-run experiments unless specifically needed for D2
- Do NOT change condition numbering, effect sizes, or hypothesis status
- STOP and ask if any change would alter the scientific narrative

## Status
ACTIVE — Paper polish phase. Focus on P1-P2 (critical), then P3-P8 (important), then the rest.
