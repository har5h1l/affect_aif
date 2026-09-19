# Agent And Trust-Game Code

The focal agent lives in `trust/`; there is no separate `agents/` package.
Project code builds and coordinates official `pymdp.Agent` objects. Social
partners in the paper are scripted environment policies, not additional
active-inference agents.

## Reading Order

1. [runtime.py](trust/runtime.py): `PartnerBank` stores partner-local agents and
   confidence state; `select_decision` selects a partner/action;
   `update_partner_after_observation` and `update_beta_after_observation` apply
   the state and confidence updates.
2. [pomdp.py](trust/pomdp.py) and [pomdp_matrices.py](trust/pomdp_matrices.py):
   construct the generative model and the shared social-action policy space.
3. [affect.py](trust/affect.py): the confidence tracker and its update rules. Gamma is mapped from expected beta in
   `runtime.py`.
4. [envs/graded.py](trust/envs/graded.py) and [envs/partners.py](trust/envs/partners.py):
   graded interactions and scripted partner responses. [stance.py](trust/stance.py)
   and [payoffs.py](trust/payoffs.py) define transition and payoff mechanics.
5. [rollout.py](trust/rollout.py) and [types.py](trust/types.py): supporting
   action-decoding, rollout, and shared-type utilities.

For the actual order of calls within an episode, read
[the experiment runner](../experiments/trust/runner.py). For the mathematical
model, read the Methods and appendices in [the manuscript](../docs/manuscript/main.tex).
Configurable controls are described in [the config guide](../docs/guide/configs.md).
