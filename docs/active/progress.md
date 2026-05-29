# Next Runs

Re-run the verification gate below immediately before launching full
statistical experiments so queued runs carry fresh local provenance.

## Verification Gate

Run these before scheduling current-evidence experiments:

```bash
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy
git diff --check
```

## Current Queue Status

As of May 27, 2026, the canonical affect update uses Hesp-style surprisal,
`-log P(observed partner action)`, with neutral baseline
`sigma_0_sq = (-log 0.5)^2`. Earlier bounded-error results are historical. The
first reduced log-surprisal smoke queue has completed at:

```text
results/log_surprisal_spine_smoke_20260527/
```

The completed smoke is now treated as pre-fix diagnostic evidence because H5
follow-up found an agent-choice candidate aggregation bug in the beta-to-gamma
path. The bug let low-precision branches with negative policy scores become
more selectable by shrinking scores toward zero. The runtime now uses centered
precision logits for agent-choice candidate comparison.

The pre-fix run command was:

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

Analysis outputs have been generated for all seven queued configs:

- `h0/graded_choice/analysis`
- `h1/reliability_vs_reward/analysis`
- `h2/lesion_open_regime/analysis`
- `h3/global_beta_focal_switch_probe/analysis`
- `h4/partner_choice/analysis`
- `h5/betrayal_choice/analysis`
- `h6/clinical_dynamics/analysis`

Do not run the confirmation queue from the pre-fix smoke.

The post-fix smoke rerun has completed under the corrected selector:

```text
results/log_surprisal_spine_smoke_postfix_20260528/
```

Analysis outputs exist for all seven queued configs:

- `h0/graded_choice/analysis`
- `h1/reliability_vs_reward/analysis`
- `h2/lesion_open_regime/analysis`
- `h3/global_beta_focal_switch_probe/analysis`
- `h4/partner_choice/analysis`
- `h5/betrayal_choice/analysis`
- `h6/clinical_dynamics/analysis`

The stale Mango monitor `affect_aif_postfix_spine_smoke_20260528` has been
removed after tmux exited and no matching experiment or analysis process was
running.

## Pre-Fix Smoke Read

```text
H0: affect lowers entropy but does not improve payoff over no-affect.
H1: local beta tracks surprise more cleanly than reward.
H2: deployment path is active, but no payoff win for local affect.
H3: local beta has cleaner signal quality; no locality payoff advantage.
H4: underpowered partner-choice readout.
H5: main follow-up risk; local affect underperforms no-affect/lesioned.
H6: beta dynamics separate; clinical claims remain supplemental only.
```

## Post-Fix Smoke Read

```text
H0: no stable payoff advantage; affect/global beta/no-affect are close.
H1: post-fix smoke does not preserve the old surprise-over-reward readout.
H2: deployment path is active; payoff remains flat-to-negative for affect.
H3: global beta has the best smoke payoff; local beta remains a cleaner signal.
H4: partner-choice payoff is noisy and flat at three seeds.
H5: repaired under the centered selector; affect beats no-affect/lesioned.
H6: perturbation dynamics separate; clinical claims remain supplemental only.
```

## Follow-Up Before Confirmation

1. Refresh the verification gate immediately before any confirmation-scale run.
2. Queue a confirmation-scale H5 betrayal-choice run first, because it is the
   repaired positive behavioral anchor after the selector fix.
3. Queue H1 only if the next step is a confirmation/rework of the
   reliability-versus-reward design; current smoke should not carry the
   model-fitness claim.
4. Treat H0/H2/H4 as manuscript-support checks: either confirm at higher seeds
   or soften them to deployment/entropy diagnostics rather than payoff claims.
5. Keep H3 local/global as a decomposition result unless a revised task makes
   locality behaviorally necessary.

## Superseded Partial Smoke Provenance

The first reduced smoke queue was initially stopped after a clean H0 checkpoint:

```text
results/log_surprisal_spine_smoke_20260527/h0/graded_choice/checkpoint_manifest.json
results/log_surprisal_spine_smoke_20260527/h0/graded_choice/results_partial.csv
```

That partial state is superseded by the completed batch at the same root.

## Result Interpretation Rules

- Do not treat partial detached rerun outputs as current evidence.
- Do not promote new outputs into manuscript-level claims until the user reviews
  the result read.
- Treat pre-log-surprisal batches as historical/provisional, even if they remain
  useful for design provenance.
- Keep H7 signal-source and H8 observation-noise lanes exploratory unless the
  user explicitly promotes them.

## Historical Provenance

Historical bounded-error and earlier log-surprisal discovery outputs remain
documented in `docs/results/`. They should not be used as current manuscript
evidence after the H0-H8 rebaseline begins.
