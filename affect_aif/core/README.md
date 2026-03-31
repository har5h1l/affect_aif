# Core Layer

## Responsibility

This layer contains generic active-inference helpers that are not specific to a single experiment runner.

## Public Surface

The package-level import surface is `affect_aif.core`. It re-exports:

- `DEFAULT_BACKEND`
- `HAS_JAX`

The remaining modules are internal helpers consumed by the agent, generative-model, and experiment layers.

## Key Modules

- `maths.py`: numerical primitives
- `learning.py`: likelihood and Dirichlet-learning updates
- `policies.py`: policy enumeration and posterior/action utilities
- `efe.py`: expected-free-energy helpers
- `rollout.py`: JAX trust-game rollout and decision step
- `control.py`: compatibility facade for the supported control surface

## Internal / Compatibility Notes

- `control.py` exists as the stable compatibility facade for callers that still import the control layer by module path.
- Backend detection is centralized in `backend.py` so the rest of the package can branch on JAX availability consistently.
