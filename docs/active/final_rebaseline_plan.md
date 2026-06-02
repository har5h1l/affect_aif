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

Continuous beta remains future work. It would require a new variational or
numerical posterior over beta rather than the current categorical filter.

## Final Hypothesis Spine

The maintained spine is now H0-H8. The manuscript does not have to use every
lane, but configs and docs should use this single numbering.

| Card | Role | Active config status |
|---|---|---|
| H0 Policy Openness | Gate: can precision move policy here? | active |
| H1 Model Fitness | Precision tracks predictive reliability, not reward. | active |
| H2 Deployment | Beta-to-gamma changes deployment with beliefs preserved. | active |
| H3 Locality / Global Precision | Local beta versus shared global beta. | active |
| H4 Social Allocation | Partner choice, avoidance, probing, and return. | active |
| H5 Timescale / Volatility | Abrupt versus gradual social change. | active |
| H6 Perturbation Phenotypes | Parameter perturbations of precision dynamics. | active, supplemental |
| H7 Signal Source | Partner-action versus joint surprise. | future/exploratory |
| H8 Observation Noise / Robustness | Noisy social observations. | future/exploratory |

## Config Surface

Active TOML specs now live under directories that match the final spine:

- `configs/trust/hypotheses/h0_policy_openness/`
- `configs/trust/hypotheses/h1_model_fitness/`
- `configs/trust/hypotheses/h2_deployment/`
- `configs/trust/hypotheses/h3_locality/`
- `configs/trust/hypotheses/h4_social_allocation/`
- `configs/trust/hypotheses/h5_timescale_volatility/`
- `configs/trust/hypotheses/h6_perturbation/`

H7 and H8 are documented exploratory lanes. Do not add active TOML for them
until the intended implementation and readouts are explicit.

## First Smoke Queue

Run this first with one worker. It is deliberately smoke-scale, not a final
statistical confirmation.

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h0_policy_openness/graded_choice.toml \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime.toml \
  --config configs/trust/hypotheses/h3_locality/global_beta_focal_switch_probe.toml \
  --config configs/trust/hypotheses/h4_social_allocation/partner_choice.toml \
  --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_choice.toml \
  --config configs/trust/hypotheses/h6_perturbation/clinical_dynamics.toml \
  --output-dir results \
  --batch-name log_surprisal_spine_smoke_20260527 \
  --workers 1
```

Analyze each completed result with `scripts/analysis/analyze.py`.

Primary smoke readouts:

- H0: policy entropy and payoff/action effects move together only when the
  policy posterior is open.
- H1: test whether the precision-surprise association remains stronger than
  precision-payoff after the selector fix.
- H2: tracked-only preserves beliefs while losing deployment effects.
- H3: local beta versus global beta separates signal quality, allocation, or
  cross-partner interference.
- H4: partner-selection entropy and selection rates shift before payoff moves.
- H5: abrupt switch exposes timing/misdeployment boundary conditions.
- H6: perturbation variants separate first in beta/precision dynamics.

## Smoke Outcome

The reduced H0-H6 post-fix smoke completed at
`results/log_surprisal_spine_smoke_postfix_20260528/`. It is current smoke
evidence, not confirmation-scale evidence. The earlier
`results/log_surprisal_spine_smoke_20260527/` run is pre-fix diagnostic
provenance only.

Current read:

- H1 preserves the surprise-over-reward model-fitness readout after correcting
  active-encounter alignment, including a partial readout controlling payoff and
  encounter count; treat it as smoke evidence that still needs confirmation.
- H0/H2 show an active deployment channel through entropy changes, but the old
  local-affect payoff benefit does not replicate at three seeds.
- H3 supports locality as cleaner signal quality, not behavioral necessity;
  global beta has the best smoke payoff.
- H5 betrayal choice is repaired under the centered selector: local affect beats
  no-affect/lesioned at three seeds and should be the first confirmation target.
- H4 and H6 should remain supplemental until larger runs justify stronger
  claims.

## Confirmation Queue

Do not launch this queue until the verification gate in
`docs/active/progress.md` passes. Prioritize H5. Keep H1 as a corrected-readout
confirmation target, and keep H0/H2/H4 only if the manuscript needs
confirmation of deployment/entropy support:

```bash
.venv/bin/python scripts/experiment/run.py \
  --config configs/trust/hypotheses/h0_policy_openness/graded_choice_confirm.toml \
  --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml \
  --config configs/trust/hypotheses/h2_deployment/lesion_open_regime_confirm.toml \
  --config configs/trust/hypotheses/h3_locality/global_beta_locality_probe.toml \
  --config configs/trust/hypotheses/h4_social_allocation/partner_choice_confirm.toml \
  --config configs/trust/hypotheses/h5_timescale_volatility/betrayal_reallocation_confirm.toml \
  --output-dir results \
  --batch-name log_surprisal_spine_confirm_20260527 \
  --workers 1
```

H6 confirmation is optional and should stay supplemental unless the manuscript
needs a stronger precision-dynamics phenotype table.

H1 has a bounded diagnostic ladder rather than a single all-or-nothing
confirmation. Run `reliability_vs_reward_confirm.toml` first to confirm the
corrected active-encounter readout. If reward/exposure coupling remains heavy,
run `reliability_spine_graded_diagnostic.toml` to use balanced exposure on a
graded reliability spine. If the normal graded spine still couples reliability
to reward, run `reliability_spine_graded_reward_matched_diagnostic.toml`; this
keeps the graded investment task while setting the multiplier to zero so own
payoff is independent of partner action at each investment level. If that still
cannot separate predictive reliability from reward or exposure, run
`reliability_reward_neutral_diagnostic.toml`. Only a failure of the strict
reward-neutral diagnostic should be treated as evidence against the model-level
H1 mechanism.

## Manuscript Policy

Do not reuse result numbers from the old bounded-error evidence as current
evidence. The reduced log-surprisal smoke has replaced them as the current
diagnostic read, but it is not final publication evidence.

The manuscript should now be framed around deployment changes through
beta-to-gamma coupling and H5 as the repaired behavioral anchor. It should not
claim a general affect payoff advantage, a proven behavioral necessity for
partner-local beta, or a settled model-fitness dissociation until
confirmation-scale runs support those claims.
