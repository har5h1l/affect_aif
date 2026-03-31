# Environment Layer

## Responsibility

This layer owns the executable trust-game environments and the scripted partner abstraction used by those environments.

## Public Surface

The package-level import surface is `affect_aif.environment`. It re-exports:

- `TrustGameEnv`
- `GradedTrustGameEnv`

## Key Modules

- `trust_game.py`: binary trust-game environment
- `graded_trust_game.py`: graded investment variant
- `partner.py`: scripted partner behavior with the same minimal lifecycle seam as agents

## Internal / Compatibility Notes

- The environment layer depends on experiment config data but does not own orchestration.
- The graded environment is a first-class shipped variant, not an archive artifact.
