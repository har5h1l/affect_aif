# Final Rebaseline Plan

Date: 2026-05-27

## Modeling Decision

The canonical affect update now uses Hesp-style partner-action surprisal:

```text
p = P(observed partner action | current partner-local belief)
epsilon = -log(p)
phi = alpha_charge * (sigma_0_sq - epsilon^2)
q(beta_k) <- normalize(exp(phi / beta_level) * T_beta q(beta_k))
gamma_k = gamma_base / E[beta_k]
```

The neutral baseline is `sigma_0_sq = (-log 0.5)^2`, so a fifty-fifty binary
prediction produces zero affective charge. Low surprisal lowers beta and raises
policy precision; high surprisal raises beta and softens policy precision.

Movement is controlled mainly by:

- `alpha_charge`: gain on affective charge.
- `beta_persistence`: inertia of the categorical beta posterior.
- `beta_levels`: discrete support and range of allowed beta values.
- `gamma`: base policy precision before inverse-beta modulation.

Continuous beta remains future work. It would require a new variational or
numerical posterior over beta rather than the current categorical filter, so it
is not part of this rebaseline.

## Config Surface

The main H0-H4 configs now include `global_beta` variants where relevant:

- `configs/trust/hypotheses/h0_openness/shallow_binary.toml`
- `configs/trust/hypotheses/h0_openness/graded_choice.toml`
- `configs/trust/hypotheses/h0_openness/graded_betrayal.toml`
- `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml`
- `configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml`
- `configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml`
- `configs/trust/hypotheses/h3_stress_response/betrayal_reallocation.toml`
- `configs/trust/hypotheses/h4_social_choice/partner_choice.toml`

The confirmation configs for H1, H2, H3 reallocation, and H4 also include
`global_beta`. H6 remains available for focused locality/interference probes.

## Smoke Queue

Run this first with one worker:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml \
  --config configs/trust/hypotheses/h3_stress_response/betrayal_choice.toml \
  --config configs/trust/hypotheses/h4_social_choice/partner_choice.toml \
  --config configs/trust/hypotheses/h6_locality_interference/global_beta_focal_switch_probe.toml \
  --output-dir results \
  --batch-name log_surprisal_core_smoke_20260527 \
  --workers 1
```

Analyze each completed result with `scripts/analysis/analyze.py`.

Primary smoke readouts:

- H1: precision-surprise association remains stronger than precision-payoff.
- H2: tracked-only preserves beliefs while losing deployment effects.
- H3: abrupt betrayal still tests the timing/misdeployment boundary.
- H4: partner selection entropy and selection rates shift before payoff moves.
- H6: global beta versus local beta separates signal quality and allocation.

## Confirmation Queue

Only run after smoke logs and analysis outputs look sane:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml \
  --config configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml \
  --config configs/trust/hypotheses/h4_social_choice/partner_choice_confirm.toml \
  --output-dir results \
  --batch-name log_surprisal_core_confirm_20260527 \
  --workers 1
```

H0 graded-choice confirmation can be added if the smoke run shows that the
openness effect changes materially under log-surprisal.

## Manuscript Policy

Do not update result numbers from the old bounded-error evidence. Until the
log-surprisal reruns complete, the manuscript should describe the current
mechanism but treat numeric result claims as provisional carryover evidence.

If log-surprisal preserves the qualitative signs, update figures and text with
the new results and retain the same argument. If it inverts H1, H2, or H3, the
paper should be reframed around the difference between model-fitness signal
definitions before submission.
