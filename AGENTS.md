# Repository Instructions

## Documentation First

- Read [docs/theory.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/docs/theory.md) before changing computational claims, affect dynamics, terminal values, or the interpretation of results.
- Read [docs/experiment.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/docs/experiment.md) before changing task design, configs, conditions, metrics, or sensitivity sweeps.
- Read [docs/implementation.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/docs/implementation.md) before changing environment semantics, switching logic, or analysis helpers.
- Read [README.md](/Users/harshilshah/Desktop/Active%20Inference/affect_aif/README.md) before changing setup, entry points, or repo layout.

## Required Follow-Through

- If code behavior changes, update the relevant docs in the same change.
- If experiment assumptions change, update both theory-facing and experiment-facing docs.
- If configs or scripts change, update the README or implementation notes so the runnable workflow stays accurate.
- If tests reveal a theory/code mismatch, fix both the implementation and the docs before closing the task.

## Learned

- Use `.venv` in project root; venv should auto-activate when in this folder (Cursor terminal setting and/or direnv with `.envrc`).
- Recommended experiment run: default + betrayal_stress in one batch with `--workers 12`; results go under `results/<batch_name>/<config_slug>/results.csv`; run `run_analysis.py` on those paths after.
- Default config (random partner) does not discriminate conditions; use betrayal_stress (agent-choice, scheduled switch) for hypothesis-relevant results.
- Before updating result-interpretation docs (`docs/results_tracking.md`, theory/experiment summaries, README conclusions) from new experiment outputs, ask the user first so the repo does not silently overwrite the active narrative.
- State inference (partner-type belief updating) is the analytical solution to VFE minimization (matrix-based Bayes with A and B), not iterative optimization; describe it that way in theory and implementation docs.
