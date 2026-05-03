# Next Runs

Do not launch full statistical experiments until the reusable-core/task-package
restructure and docs-state verification are green.

## Verification Gate

Run these before scheduling current-evidence experiments:

```bash
python -m pytest tests/ -q
python -m ruff check .
python -m mypy
git diff --check
```

## Post-Verification Queue

1. Smoke `shallow_affect_confirm` on the current architecture.
2. Full `shallow_affect_confirm` with conditions `[1, 2, 3, 4, 9, 10]` and the
   `lesioned` preset.
3. Relaunch or intentionally abandon the incomplete H5 partner-selection run.
4. Relaunch or intentionally abandon the incomplete clinical betrayal run.
5. Run clinical phenotypes only after the clinical-betrayal decision is clear.

## Historical Partial Runs

The detached H5 and clinical-betrayal reruns recorded in the old conductor state
stopped with `results_partial.csv` files and no final `results.csv`. They are
salvage context only until the user decides whether to rerun or explicitly
analyze them as partial historical artifacts.
