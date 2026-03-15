# Implementation Notes

## Code/Doc Alignment

- `docs/theory.md` is the mechanism-level description.
- `docs/experiment.md` is the task and hypothesis-level description.
- This file records implementation-specific choices that are easy to misread from the theory alone.
- When code changes any of these behaviors, update the docs in the same patch.

## Switching Semantics

- `p_switch` in the environment is the stochastic probability that a partner changes **latent type** after an interaction.
- `switch_round` in the generative model is not that process. It is the exploiter-type partner's internal phase boundary: after enough interactions, an exploiter switches from `p_coop_early` to `p_coop_late`.
- These are intentionally separate:
  - stochastic type switching controls volatility across partner identities
  - exploiter phase switching controls a specific within-type betrayal profile

## Precision Modulation

- `affect_modulates_precision=False` by default.
- When enabled, the current implementation multiplies policy precision by `1 + precision_signal`.
- That means the optional precision path only boosts decisiveness above the base `gamma`; it does not suppress precision below baseline.

## Terminal Values

- Affective and reward-average agents now both emit terminal signals on a comparable `[0, 1]` scale.
- Affective agents use raw `beta_k`.
- Reward-average agents use `0.5 * (1 + tanh(reward_avg / max_abs_payoff))`, which is centered at `0.5` when reward history is neutral.
- The terminal value actually used in planning is context-sensitive:

```text
V = -mu * signal_k * normalized_continuation_payoff
```

## Affective Update Signal

- The current code tracks unsigned surprise, not signed residual error.
- Concretely, it uses `1 - P(observed action)` under the current predictive distribution for that partner.
- The existing `prediction_errors` logging field is kept for backward compatibility, but its semantics are surprise magnitude.

## Betrayal Stress Experiment

- The environment supports `initial_partner_types` to seed a specific partner roster.
- It also supports `scheduled_type_switches`, a list of `{round, partner_idx, to_type}` events.
- Scheduled switches are applied at the start of the specified 1-based round, before the selected partner acts, so the agent experiences the switch as an unexpected behavioral change.
- See `affect_aif/configs/betrayal_stress.json` for the reference setup.
