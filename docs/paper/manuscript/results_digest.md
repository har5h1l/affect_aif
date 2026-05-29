# Results Digest For Current Draft

## Inclusion Decision

Use the post-fix reduced log-surprisal smoke as current smoke evidence only. It
was run after fixing the agent-choice candidate aggregation bug in the
beta-to-gamma deployment path. The old bounded-error / bounded-surprise numbers
and the first log-surprisal smoke are historical diagnostic evidence and should
not be promoted as current evidence.

Current canonical batch:

```text
results/log_surprisal_spine_smoke_postfix_20260528/
```

Run scale: three seeds per variant. Treat all payoff and pairwise-test readouts
as smoke-scale and underpowered.

## Current Smoke Run Sizes

| Experiment | Path | Variants | Seeds | Rounds |
|---|---|---:|---:|---:|
| H0 graded choice | `results/log_surprisal_spine_smoke_postfix_20260528/h0/graded_choice/results.csv` | 3 | 3 each | 200 |
| H1 reliability versus reward | `results/log_surprisal_spine_smoke_postfix_20260528/h1/reliability_vs_reward/results.csv` | 3 | 3 each | 200 |
| H2 lesion open regime | `results/log_surprisal_spine_smoke_postfix_20260528/h2/lesion_open_regime/results.csv` | 4 | 3 each | 200 |
| H3 focal-switch locality | `results/log_surprisal_spine_smoke_postfix_20260528/h3/global_beta_focal_switch_probe/results.csv` | 4 | 3 each | 100 |
| H4 partner choice | `results/log_surprisal_spine_smoke_postfix_20260528/h4/partner_choice/results.csv` | 3 | 3 each | 200 |
| H5 betrayal choice | `results/log_surprisal_spine_smoke_postfix_20260528/h5/betrayal_choice/results.csv` | 4 | 3 each | 120 |
| H6 clinical dynamics | `results/log_surprisal_spine_smoke_postfix_20260528/h6/clinical_dynamics/results.csv` | 4 | 3 each | 200 |

## Headline Post-Fix Smoke Read

### R1: H1 is not yet rescued under post-fix smoke

H1 reliability-versus-reward smoke:

- Local affect: `|corr(precision, surprise)| = 0.226`,
  `|corr(precision, payoff)| = 0.615`.
- Global beta: `0.115` versus `0.103`, a weak and nearly flat readout.
- Total payoff: affect `492.7`, no-affect `552.0`, global beta `512.7`.
- Interpretation: the post-fix H1 smoke does not support the old
  surprise-over-reward model-fitness claim. Treat H1 as a required
  confirmation/rework item, not as a current manuscript anchor.
- Follow-up exposure diagnostic: grouped by selected partner/seed, beta is
  strongly associated with both mean surprisal and mean payoff, suggesting the
  current task may not cleanly separate reliability from reward exposure at
  smoke scale.

### R2: Open-regime deployment changes without stable payoff gain

H0/H2 graded open regime:

- H0 payoff: affect `1851.3`, no-affect `1864.2`, global beta `1851.3`.
- H0 entropy: affect `8.59`, no-affect `8.79`, global beta `8.64`.
- H2 repeats the same open-regime setup with lesion/no-epistemic controls;
  no-affect and tracked-only/lesioned match in the shared comparisons.
- Interpretation: the beta-to-gamma path changes policy entropy, but the older
  local-affect payoff benefit does not survive this three-seed log-surprisal
  smoke.

### R3: Locality is signal quality, not behavioral necessity

H3 focal-switch locality smoke:

- Local beta: `|corr(precision, surprise)| = 0.943`, reward `0.110`.
- Global beta: surprise `0.149`, reward `0.043`.
- Payoff: global beta `976.2`, local beta `946.8`, no-affect/tracked-only
  `950.7`.
- Interpretation: local beta is the cleaner partner-specific readout in this
  focal-switch task, but the current task does not show a locality payoff
  advantage.

### R4: Betrayal is repaired but needs confirmation

H5 betrayal-choice smoke:

- Total payoff: affect `1322.3`, global beta `1216.2`, no-affect/lesioned
  `1225.0`.
- Entropy: affect `7.47`, no-affect/lesioned `8.68`.
- Joint accuracy: affect `0.319`, no-affect/lesioned `0.425`.
- Interpretation: the centered selector fixes the pre-fix H5 warning at smoke
  scale. This is now the strongest candidate positive behavioral anchor, but it
  needs confirmation-scale reruns before publication.

### R5: H4 and H6 are supplemental at smoke scale

- H4 payoff is noisy: affect `377.3`, global beta `388.7`, no-affect `385.3`;
  local affect slightly lowers entropy (`4.66` versus `4.81` for no-affect).
- H6 beta dynamics separate as intended: alexithymia-like range `0.180`,
  affect `1.126`, borderline-like `1.412`, depression-like `1.464`.
- Interpretation: H4 needs confirmation before manuscript claims; H6 can
  support a supplemental precision-dynamics table but not clinical validation.

## Follow-Up Fix

The H5 follow-up traced a runtime issue in `agent_choice` candidate comparison.
The previous selector scaled negative policy scores directly by partner gamma;
for low-precision partners this could shrink all scores toward zero and make a
bad uncertain branch more selectable. The runtime now compares partner-local
branches with centered precision logits,
`center(G_k) + gamma_k * (G_k - center(G_k))`, which preserves within-partner
sharpening while avoiding this cross-partner sign artifact.

A one-seed post-fix H5 trace changed affect seed 42 from `1134.5` payoff with
near-locking onto partner 3 to `1260.0` payoff with branch mass concentrated on
partner 2. The post-fix H5 probe and full reduced H0-H6 smoke completed under
`results/log_surprisal_h5_candidate_fix_probe_20260528/` and
`results/log_surprisal_spine_smoke_postfix_20260528/`.

## Claims To Use Now

- The canonical affect update is partner-action surprisal,
  `epsilon = -log P(observed partner action)`.
- The pre-fix smoke should not be used for final evidence.
- Post-fix smoke restores H5 as a candidate positive behavioral anchor.
- H1 needs confirmation or a revised reliability-vs-reward design before it can
  carry the model-fitness claim.
- The corrected agent-choice path uses centered precision logits.

## Claims To Avoid

- Do not claim affect globally improves payoff.
- Do not claim local affect wins in the open graded regime under log-surprisal.
- Do not claim partner-local beta is behaviorally necessary.
- Do not claim H5 is publication-ready from three seeds.
- Do not claim H6 variants validate clinical phenotypes.
- Do not reuse old bounded-error numbers as current manuscript evidence.
- Do not promote pre-fix smoke numbers as current manuscript evidence.
