# 2026-05-21 H1/H3 Split Confirmation

## Provenance

- Batch: `results/confirm_h1_h3_split_20260519/`
- Branch/commit: current server checkout on `master`; exact commit not
  recorded in this note.
- H1 config:
  `configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml`
- H3 config:
  `configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml`
- Size: H1 has 30 seeds each for affect and no-affect; H3 has 30 seeds each
  for affect, no-affect, and lesioned.
- Active reruns should use `--workers 1` unless explicitly authorized
  otherwise. This historical batch was completed before the current one-worker
  operating rule.
- Analysis: `scripts/analysis/analyze.py`

Run command:

```bash
python scripts/experiment/run.py --config configs/trust/hypotheses/h1_model_fitness/reliability_vs_reward_confirm.toml --config configs/trust/hypotheses/h3_stress_response/betrayal_reallocation_confirm.toml --output-dir results --batch-name confirm_h1_h3_split_20260519 --workers 1
```

Analysis commands:

```bash
python scripts/analysis/analyze.py --results results/confirm_h1_h3_split_20260519/h1/reliability_vs_reward_confirm/results.csv --output-dir results/confirm_h1_h3_split_20260519/h1/reliability_vs_reward_confirm/analysis
python scripts/analysis/analyze.py --results results/confirm_h1_h3_split_20260519/h3/betrayal_reallocation_confirm/results.csv --output-dir results/confirm_h1_h3_split_20260519/h3/betrayal_reallocation_confirm/analysis
```

## H1 Model Fitness

The confirmation supports H1 as a model-fitness signal, not as a payoff signal.

Key read:

- Total payoff: affect `534.6` vs no-affect `542.1`; difference `-7.53`,
  bootstrap CI `[-27.88, 13.82]`.
- Mean policy entropy: affect `4.48` vs no-affect `4.32`; difference `+0.16`,
  bootstrap CI `[0.06, 0.27]`.
- Partner-level precision correlation: `|corr(precision, surprise)| = 0.701`
  vs `|corr(precision, payoff)| = 0.419`.
- The reliability-over-reward effect summary is positive: `+0.096`, bootstrap
  CI `[0.027, 0.164]`.

Interpretation: affective precision is tracking predictive reliability more
than realized reward, and H1 no longer needs to be labeled only as five-seed
pilot evidence. It still should not be described as a reward advantage.

## H3 Stress Response

The confirmation does not support the earlier pilot impression that affect
returns later and more safely after betrayal. It supports H3 as a stress
boundary condition where affective precision sharpens deployment in a way that
can hurt payoff.

Key read:

- Total payoff: affect `1136.1` vs no-affect/lesioned `1172.1`; difference
  `-36.08`, bootstrap CI `[-63.65, -10.93]`.
- Pairwise payoff tests: affect vs no-affect `p = 0.0169`; affect vs lesioned
  `p = 0.0169`; no-affect and lesioned are identical in this config.
- Mean policy entropy: affect `8.38` vs no-affect `8.74`; difference `-0.36`,
  bootstrap CI `[-0.45, -0.26]`.
- Reencounters with the switched partner: affect `4.4` vs no-affect `6.1`;
  bootstrap CI for the difference crosses zero.
- Decisions to first reencounter among runs that return: affect `15.6` vs
  no-affect `17.6`; bootstrap CI crosses zero.
- Payoff conditional on reencounter: affect `8.76` vs no-affect `8.91`;
  bootstrap CI crosses zero.
- Wrong-type rate on reencounter: affect `0.237` vs no-affect `0.165`;
  bootstrap CI crosses zero.

Interpretation: H3 should not be written as "affect wins after betrayal."
The stable result is that stress exposes a risk mode: affect lowers policy
entropy and changes return behavior, but the sharpened deployment is not safer
or more profitable in this confirmation.

## Evidence Hierarchy Update

- Promote H1 from pilot-supported to supported as a model-fitness readout.
- Keep H3 as a confirmed boundary-condition result.
- Treat the May 19 five-seed H3 reallocation pilot as exploratory context only.
- Do not run more experiments before write-up unless the manuscript needs a
  very specific stress-regime robustness check.
