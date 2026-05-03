# Apashea Alignment

The apashea trust notebook is a reference for active-inference matrix
conventions and selected trust-game design choices. It is not a runtime
dependency, and this project remains committed to a reusable JAX-based `aif/`
core.

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

- The project does not embed pymdp.
- The active core is JAX-oriented and should pass randomness through explicit
  keys where random policy sampling is part of a public core API.
- Pandas and NumPy are acceptable at analysis, logging, CLI, and compatibility
  boundaries.
- Historical paper and archive claims are not promoted as current evidence until
  rerun on this architecture.
