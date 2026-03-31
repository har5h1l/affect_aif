# Affect State Helpers

## Responsibility

This subpackage contains the affect-state implementations used by `AffectiveAgent` and related compatibility paths.

## Public Surface

There is no package-level re-export from `affect_aif.agent.affect`; import the state helpers directly from their modules when needed.

## Key Modules

- `state.py`: continuous EMA-based affective state
- `variational_state.py`: supported variational beta-state implementation for `Condition 12`
- `discrete_state.py`: legacy discrete-beta state used by the compatibility agent

## Internal / Compatibility Notes

- The supported path uses `state.py` for the continuous beta update and `variational_state.py` for the condition-12 variational path.
- `discrete_state.py` is retained for compatibility and test coverage only.
- The earlier standalone discrete-beta prototype is preserved in `archive/legacy_discrete_beta/`.
