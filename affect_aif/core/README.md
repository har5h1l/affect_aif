# Core Layer

This layer contains generic active-inference helpers that are not specific to a single experiment runner.

Main modules:

- `maths.py`: numerical primitives
- `learning.py`: likelihood/Dirichlet learning updates
- `policies.py`: policy enumeration and posterior/action utilities
- `efe.py`: non-JAX expected-free-energy helpers
- `rollout.py`: JAX trust-game rollout and decision step
- `control.py`: compatibility facade re-exporting the supported control surface
