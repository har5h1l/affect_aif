# 2026-05-29 Log-Surprisal Post-Fix Smoke

## Provenance

- Result root: `results/log_surprisal_spine_smoke_postfix_20260528/`
- Runtime: official `inferactively-pymdp==1.0.0` with project trust-task
  wrappers.
- Affect update: partner-action surprisal,
  `epsilon = -log P(observed partner action)`.
- Selector: centered precision logits for cross-partner agent-choice candidate
  comparison.
- Scale: three seeds per variant; smoke evidence only.
- Execution: detached tmux on `server`, registered through Mango as
  `affect_aif_postfix_spine_smoke_20260528`; the tmux session exited and the
  stale Mango monitor was removed after completion.

## Completed Outputs

Analysis outputs exist for all queued experiments:

- `h0/graded_choice/analysis`
- `h1/reliability_vs_reward/analysis`
- `h2/lesion_open_regime/analysis`
- `h3/global_beta_focal_switch_probe/analysis`
- `h4/partner_choice/analysis`
- `h5/betrayal_choice/analysis`
- `h6/clinical_dynamics/analysis`

## Smoke Read

| Card | Mean payoff read | Interpretation |
|---|---:|---|
| H0 graded choice | affect `1851.3`, global beta `1851.3`, no-affect `1864.2` | No local-affect payoff win; entropy channel remains active. |
| H1 model fitness | affect `492.7`, global beta `512.7`, no-affect `552.0` | Corrected active-aligned and partial-correlation readouts support surprise-over-reward at smoke scale; requires confirmation and exposure-confound monitoring. |
| H2 deployment | affect `1851.3`, global beta `1851.3`, lesioned `1864.2`, no-epistemic `1863.3` | Deployment path exists, but payoff is flat-to-negative. |
| H3 locality | global beta `976.2`, local beta `946.8`, no-affect/tracked-only `950.7` | Locality remains a decomposition/signal-quality question, not a behavioral necessity claim. |
| H4 social allocation | affect `377.3`, global beta `388.7`, no-affect `385.3` | Underpowered and noisy; keep supplemental until confirmation. |
| H5 betrayal choice | affect `1322.3`, global beta `1216.2`, no-affect/lesioned `1225.0` | Repaired positive behavioral anchor after the centered-selector fix. |
| H6 perturbation | affect `1851.3`, alexithymia `1840.5`, borderline `1859.0`, depression `1877.7` | Dynamics/perturbation support only; no clinical validation claim. |

## Publication Implication

This run clears the immediate H5 smoke blocker but does not make the manuscript
publication-ready. The next confirmation lane should prioritize H5 as the
repaired behavioral anchor. H1 should be treated as a corrected-readout
model-fitness confirmation item: active-aligned and partial-correlation smoke
analyses support the surprise-over-reward diagnostic, while reward/exposure
correlations remain a design confound to monitor. H0, H2, and H4 should either
be confirmed at higher seed count or written as deployment/entropy support
rather than payoff claims.
