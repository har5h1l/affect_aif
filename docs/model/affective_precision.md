# Affective Precision

Affective precision is implemented outside pymdp as a partner-local confidence
signal. For partner `k`, prediction error updates a beta posterior `q(beta_k)`.
The beta-derived signal then modulates policy precision `gamma_k` before policy
inference for that partner.

Higher inferred reliability corresponds to lower beta and higher policy
precision. In manuscript prose, describe reliability through `q(beta_k)`,
beta-derived `gamma_k`, or the confidence signal, not as raw beta increasing
with reliability.

## Modes

- `none`: no affective beta state.
- `precision`: beta is tracked and deployed into policy precision.
- `tracked_only`: beta is tracked but decoupled from policy precision.
- `global_beta`: a shared beta control used for locality diagnostics.

The tracked-only mode is the main deployment dissociation: belief updating can
remain intact while the confidence-to-action channel is disabled.
