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
