# Agent Layer

## Responsibility

This layer contains the agent implementations used by the supported condition set.

## Public Surface

There is no package-level re-export from `affect_aif.agent`; import concrete agent classes from their defining modules.

## Key Modules

- `base_agent.py`: non-affective baseline planner
- `affective_agent.py`: affective agent with continuous or variational beta state
- `lesioned_agent.py`: affective state present but decoupled from control
- `reward_avg_agent.py`: reward-average control agent
- `discrete_affective_agent.py`: discrete-beta compatibility implementation retained for legacy coverage
- `affect/`: affect-state helpers for the continuous, variational, and legacy discrete paths

## Internal / Compatibility Notes

- The supported affective path is the current `AffectiveAgent` plus `affect/variational_state.py`.
- The discrete-beta implementation remains available for compatibility and tests, but it is not the current first-class path.
- Historical prototypes that are no longer first-class are preserved under `archive/`.
