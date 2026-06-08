# Trust POMDP

The maintained runtime uses official `inferactively-pymdp==1.0.0` agents. Task
code constructs trust-game matrices, creates one partner-local agent per
partner, and logs beliefs and actions around pymdp state and policy inference.

## State And Observations

The focal agent represents partner type and partner stance as hidden-state
factors. Observations include the partner response and payoff category after
the focal agent chooses a partner/action. Partner policies are environment-side
scripted strategies; the reported experiments do not make partners run pymdp
or affective precision.

## Runtime Loop

1. Select the active partner or evaluate partner-local candidate policies.
2. Set the partner-local policy precision from the current beta state when
   affective precision is enabled.
3. Call pymdp policy inference and choose an action.
4. Step the trust-game environment.
5. Update partner-local state beliefs through pymdp state inference.
6. Update external beta from prediction error and log diagnostics.

Trust-game implementation details live under `tasks/trust/`; experiment
orchestration lives under `experiments/trust/`.
