# Apashea Alignment

The apashea trust notebook is a reference for active-inference matrix
conventions and selected trust-game design choices. The supported runtime is
official `inferactively-pymdp==1.0.0`; Apashea's notebook and fork remain
reference material for model construction and helper ideas.

## Adopted Alignment

- Binary trust games use factorized controls: partner selection where applicable,
  stance-directed social control, and own action.
- Agent-choice mode encodes environment actions as partner, stance, and own
  action combinations.
- Policy logits include `log_policy_prior`, analogous to a separate policy prior.
- Optional Dirichlet learning hooks exist for A, B, and E where configured.
- Payoff and outcome observation use the executed own action, while planning can
  use the stance-control column for generative stance transitions.
- C[1] remains log-softmaxed rather than represented as a raw softmax.

## Deliberate Deviations

- Official `inferactively-pymdp==1.0.0` is the active runtime dependency.
- Trust-task wrappers own model construction, task semantics, and any adapter
  logic needed around `pymdp.Agent`.
- Pandas and NumPy are acceptable at analysis, logging, and CLI boundaries.
- Current evidence must come from completed runs on this architecture.
