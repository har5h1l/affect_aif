# Historical Findings

These findings are preserved as historical context only. They may predate the
apashea-aligned factorized-control model and should not be compared as current
evidence unless explicitly rerun on the current architecture.

May 2026: raw `results/` batches on local disk were deleted; on the Mango
`server` VM, orphan dirs under `~/repos/affect_aif/results/` were removed after
`mango cloud sync push` (rsync does not delete remote-only paths by default).
Partial CSVs mentioned below are no longer available for inspection.

## Salvaged Paper-Era Claims

The deleted `docs/paper/` surface framed affect as per-partner metacognitive
precision tracking in multi-agent active inference. Useful historical claims to
retain as hypotheses or motivation:

- Per-partner affect was argued to track model fitness rather than reward.
- A vmPFC-style lesion was modeled as intact partner inference with impaired
  deployment of affective precision into action selection.
- Precision tracking and reward averaging were described as occupying distinct
  informational niches: prediction reliability under volatility versus cached
  value when reward gradients directly guide action.
- Graded and betrayal regimes were identified as more behaviorally diagnostic
  than saturated binary settings.
- Clinical-like perturbations were treated as changes to affective precision
  dynamics: blunted response, volatile response, and pessimistic initial
  precision.
- CvC transfer was described as an architectural proof of concept, not strong
  evidence of external validity.

These claims should now be tested through the current H0-H5 behavior-card surface in
`docs/theory/hypotheses.md`.

## Salvaged Conductor State

The old conductor state recorded that:

- prior shallow-confirm and factorial numbers are not comparable after
  factorized controls and environment decoding changed;
- detached H5 partner-selection reruns exited without a final `results.csv`;
- detached clinical-betrayal reruns exited without a final `results.csv`;
- clinical phenotypes were absent in the recorded worktree state;
- partial outputs were present but incomplete and should not be analyzed as
  completed batches.

Those notes now inform `docs/state/current/blockers.md` and
`docs/state/current/next_runs.md`.

## Salvaged Archive Themes

The deleted `archive/` surface contained exploratory scripts and configs for
clinical perturbations, cross-game comparisons, Stag Hunt, Chicken, graded
betrayal, precision modulation (`run_precision_modulation.py`), model
comparison, and the legacy standalone discrete-beta prototype. These are not
supported execution surfaces. Their useful concepts are retained only as future
or historical context:

- cross-game volatility can stress-test model-fitness tracking;
- clinical perturbations should be evaluated by task regime, not as global
  traits;
- the legacy discrete-beta prototype is superseded by the supported beta path in
  the active codebase.
