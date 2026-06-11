# Affective Precision

Partner-local beta tracks how predictable each partner's behavior has been for
the focal agent's social model. The signal lives outside the POMDP hidden-state
space: `DiscreteBetaState` in `tasks/trust/affect.py` maintains
`q(beta_k)` per partner, and the runtime maps expected beta into pymdp policy
precision before `infer_policies(...)`.

Beta tracks **model fitness / predictability**, not cached reward or partner
value. Surprise comes from the partner-local prediction of the observed partner
action, not from payoff alone.

In analyses and manuscript prose, report `precision_k = 1 / E[beta_k]` or
beta-derived `gamma_k` when describing reliability — lower beta means higher
precision and higher confidence in the partner-local model.

## Prediction Error

After each round, the runtime takes the predicted partner-action distribution
from the selected branch and the realized partner action:

```text
epsilon_k = -log P(o_action = observed | partner-local beliefs)
```

Low surprisal means the social model predicted the partner well; high surprisal
means it did not. Consistent accurate predictions push expected beta down;
consistent surprises push it up.

## Beta Update

Each partner has a discrete posterior over support points `beta_levels`. The
update is a one-step predict-then-correct filter:

1. **Transition.** Apply a persistent tridiagonal transition matrix controlled
   by `beta_persistence` (default `0.8`).
2. **Charge.** Convert surprisal into signed affective charge:

```text
phi(epsilon) = alpha_charge * (sigma_0_sq - epsilon^2)
```

Small surprise yields positive charge (favor lower beta / higher confidence).
Large surprise yields negative charge (favor higher beta / lower confidence).

3. **Likelihood.** For each support level `l`, likelihood mass scales with
   `exp(phi(epsilon) / beta_l)`.
4. **Posterior.** Multiply likelihood by the transitioned prior and normalize.
   The point estimate is `E[beta_k] = sum_l q(beta_l) * beta_l`.

Default support: `[0.5, 0.67, 1.0, 1.5, 2.0]`. Default
`sigma_0_sq = (log 2)^2`, the squared surprisal of a maximally uninformative
binary prediction.

## Policy Deployment

Before policy inference for partner `k`, the runtime sets:

```text
gamma_k = gamma_base / E[beta_k]
```

Policy scores are precision-scaled around their mean before softmax selection.
Higher `gamma_k` means more decisive policy expression; lower `gamma_k` means
more exploratory action.

Affective precision can change behavior only when the policy posterior has room
to move (`q_pi_entropy`, EFE spread). In saturated binary settings the channel
is often inert; graded games leave more policy openness.

## Parameters

| Field | Default | Role |
|---|---|---|
| `initial_beta` | `1.0` | Starting expected beta (via nearest support point). |
| `alpha_charge` | `3.0` | Surprise-to-charge gain; controls how fast beta moves. |
| `sigma_0_sq` | `(log 2)^2` | Baseline squared surprisal for charge sign flip. |
| `beta_persistence` | `0.8` | Temporal smoothing of the beta posterior. |
| `beta_levels` | five-level grid above | Discrete support for `q(beta_k)`. |
| `gamma` | config base | `gamma_base` before beta modulation. |

Variant sweeps vary `alpha_charge`, `initial_beta`, `beta_persistence`, and
related fields to probe profile-style sensitivity (H6):

| Profile | Typical knob | Expected precision behavior |
|---|---|---|
| Alexithymia-like | low `alpha_charge` | barely moves |
| Borderline-like | high gain / low smoothing | swings too fast |
| Depression-like | high `initial_beta` | starts low-confidence |
| Slow-updating | high `beta_persistence` | lags after shifts |

These are computational profiles, not clinical diagnoses.

## Modes

TOML `affect` values map to runtime behavior as follows.

| TOML | Runtime | Beta tracking | Gamma deployment |
|---|---|---|---|
| `none` | no tracker | off | `gamma_base` only |
| `precision` | partner-local | on | `gamma_base / E[beta_k]` |
| `tracked_only` | partner-local | on | decoupled; stays at `gamma_base` |
| `global_beta` | one shared tracker | on | all partners share one `E[beta]` |

- **`precision`:** full mechanism — beta tracks predictability and modulates
  action confidence.
- **`tracked_only`:** main deployment lesion (H2). Beta still updates from
  social surprise, but `gamma_k` is not modulated, separating confidence
  tracking from action deployment while leaving state inference intact.
- **`global_beta`:** locality control (H3). One shared beta state receives all
  surprise updates; every partner uses the same deployed precision.

## Code

- Beta tracker: `tasks/trust/affect.py`
- Surprise input, gamma mapping, deployment: `tasks/trust/runtime.py`
- Variant wiring: `experiments/trust/factory.py`
- Generative-model boundary and action-perception cycle: `pomdp.md`
