# Agent Layer

Supported agent implementations used by the current condition set:

- `base_agent.py`: non-affective baseline planner
- `affective_agent.py`: affective agent with continuous or variational beta state
- `lesioned_agent.py`: affective state present but decoupled from control
- `reward_avg_agent.py`: reward-average control agent

Historical prototypes that are no longer first-class are preserved under `archive/`.
