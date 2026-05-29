# Post-Fix Smoke Source Tables

These compact tables were copied from the server-only result root:

```text
results/log_surprisal_spine_smoke_postfix_20260528/
```

They are small analysis artifacts for manuscript review. Row-level experiment
outputs remain on `server` under `results/`.

Use these tables as current smoke evidence only. The key correction from the
analysis is that H1 does not preserve the old surprise-over-reward
model-fitness readout after the centered-selector fix:

- local affect: `|corr(precision, surprise)| = 0.226`
- local affect: `|corr(precision, payoff)| = 0.615`

H5 remains the strongest post-fix behavioral anchor at smoke scale:

- local affect mean payoff: `1322.3`
- no-affect / tracked-only mean payoff: `1225.0`

The follow-up H1 exposure diagnostic (`h1_exposure_diagnostic.csv`) suggests
the reliability-vs-reward task is confounded at smoke scale: partner beta is
strongly associated with both mean surprisal and mean payoff when grouped by
selected partner/seed. Use this as a reason to inspect or redesign H1 before
adding seeds.
